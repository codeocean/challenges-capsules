#!/usr/bin/env python3
"""score.py — PWM-based enhancer activity scoring for K562 sequences.

Uses vectorised Position Weight Matrix scanning with Gaussian-weighted
inter-motif cooperativity, GC optimality, and trinucleotide complexity
to produce continuous, non-saturating scores grounded in enhancer biology.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Optional

import numpy as np

# ── Constants ─────────────────────────────────────────────────────────────
BASES = "ACGT"
_BASE_IDX = {b: i for i, b in enumerate(BASES)}

# K562-enriched TF binding motifs (JASPAR consensus, N-free)
K562_MOTIFS: dict[str, str] = {
    "GATA1": "AGATAAGG",
    "TAL1":  "CAGATG",
    "SP1":   "GGGCGG",
    "NFE2":  "TGCTGAGTCA",
    "KLF1":  "CCACACCCT",
    "MYC":   "CACGTG",
}

# Cooperative TF pairs in K562 erythroid program
COOPERATIVE_PAIRS = [("GATA1", "TAL1"), ("GATA1", "KLF1"), ("SP1", "MYC")]
COOP_OPTIMAL_DIST = 30          # bp — optimal inter-motif spacing
COOP_SIGMA = 15                 # Gaussian width for spacing quality

# Scoring hyper-parameters
QUALITY_POWER = 4
GOOD_HIT_THRESH = 0.80
GC_OPTIMAL = 0.52
MAX_MOTIF_COVERAGE = 0.30       # motif explosion threshold
WEIGHTS = (0.28, 0.18, 0.17, 0.20, 0.17)  # richness, hits, coop, gc, complexity


# ── Encoding helpers ──────────────────────────────────────────────────────

def one_hot(seq: str) -> np.ndarray:
    """(4, L) one-hot encoding."""
    arr = np.zeros((4, len(seq)), dtype=np.float32)
    for i, c in enumerate(seq.upper()):
        idx = _BASE_IDX.get(c)
        if idx is not None:
            arr[idx, i] = 1.0
    return arr


def reverse_complement(seq: str) -> str:
    return seq.upper().translate(str.maketrans("ACGT", "TGCA"))[::-1]


def gc_content(seq: str) -> float:
    s = seq.upper()
    return (s.count("G") + s.count("C")) / len(s) if s else 0.0


# ── Pre-computed motif one-hot cache ──────────────────────────────────────

def _build_motif_cache() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    c: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for name, consensus in K562_MOTIFS.items():
        c[name] = (one_hot(consensus), one_hot(reverse_complement(consensus)))
    return c

_MOTIF_CACHE = _build_motif_cache()


# ── Vectorised motif scanning ─────────────────────────────────────────────

def _scan_strand(seq_oh: np.ndarray, motif_oh: np.ndarray) -> np.ndarray:
    n = seq_oh.shape[1] - motif_oh.shape[1] + 1
    if n <= 0:
        return np.zeros(1, dtype=np.float32)
    scores = np.zeros(n, dtype=np.float32)
    for row in range(4):
        scores += np.correlate(seq_oh[row], motif_oh[row], mode="valid")
    return scores / motif_oh.shape[1]


def scan_motif(seq_oh: np.ndarray, name: str) -> dict:
    """Scan both strands. Returns dict with quality, positions, and counts."""
    fwd_oh, rc_oh = _MOTIF_CACHE[name]
    fwd_q = _scan_strand(seq_oh, fwd_oh)
    rc_q = _scan_strand(seq_oh, rc_oh)
    combined = np.maximum(fwd_q, rc_q)
    best_idx = int(np.argmax(combined))
    good_mask = combined >= GOOD_HIT_THRESH
    return {
        "quality": float(combined[best_idx]),
        "best_pos": best_idx,
        "good_positions": np.where(good_mask)[0].tolist(),
        "n_good": int(good_mask.sum()),
    }


def motif_coverage_fraction(seq_oh: np.ndarray, name: str) -> float:
    """Fraction of sequence bases covered by good motif hits."""
    r = scan_motif(seq_oh, name)
    motif_len = len(K562_MOTIFS[name])
    covered = set()
    for pos in r["good_positions"]:
        covered.update(range(pos, min(pos + motif_len, seq_oh.shape[1])))
    return len(covered) / seq_oh.shape[1]


# ── Scoring ───────────────────────────────────────────────────────────────

def _spacing_quality(dist: int) -> float:
    """Gaussian reward for inter-motif spacing centred at optimal distance."""
    return float(np.exp(-0.5 * ((dist - COOP_OPTIMAL_DIST) / COOP_SIGMA) ** 2))


def _trinuc_entropy(seq: str) -> float:
    trimers = [seq[i:i + 3] for i in range(len(seq) - 2)]
    counts = Counter(trimers)
    total = sum(counts.values())
    if total == 0:
        return 0.0
    probs = np.array([c / total for c in counts.values()], dtype=np.float64)
    ent = float(-np.sum(probs * np.log2(probs + 1e-12)))
    mx = np.log2(min(64, total))
    return ent / mx if mx > 0 else 0.0


def score_single(seq: str) -> float:
    """Score one sequence → continuous value in ~[0.15, 0.90]."""
    s = seq.upper()
    oh = one_hot(s)

    # 1. Scan all motifs
    results: dict[str, dict] = {}
    for name in K562_MOTIFS:
        results[name] = scan_motif(oh, name)

    # 2. Motif richness (power-transformed quality, averaged)
    qualities = np.array([r["quality"] ** QUALITY_POWER for r in results.values()])
    motif_richness = float(qualities.mean())

    # 3. Good-hit count (diminishing returns)
    total_good = sum(r["n_good"] for r in results.values())
    hit_score = min(float(np.log1p(total_good) / np.log1p(18)), 1.0)

    # 4. Cooperativity — Gaussian-weighted spacing between ALL good-hit pairs
    coop_raw = 0.0
    for tf1, tf2 in COOPERATIVE_PAIRS:
        p1 = results[tf1]["good_positions"]
        p2 = results[tf2]["good_positions"]
        if p1 and p2:
            best_sq = max(_spacing_quality(abs(a - b)) for a in p1 for b in p2)
            coop_raw += best_sq
    cooperativity = coop_raw / len(COOPERATIVE_PAIRS)

    # 5. GC penalty
    gc = gc_content(s)
    gc_score = max(0.0, 1.0 - abs(gc - GC_OPTIMAL) / 0.25)

    # 6. Complexity
    complexity = _trinuc_entropy(s)

    # 7. Motif explosion penalty (any TF covering >30 % → penalise)
    max_cov = max(motif_coverage_fraction(oh, n) for n in K562_MOTIFS)
    explosion_penalty = max(0.0, max_cov - MAX_MOTIF_COVERAGE) * 2.0

    w = WEIGHTS
    raw = (w[0] * motif_richness + w[1] * hit_score + w[2] * cooperativity
           + w[3] * gc_score + w[4] * complexity)
    return max(0.0, raw - explosion_penalty)


# ── Batch scorer ──────────────────────────────────────────────────────────

def score_batch(seqs: list[str], model=None) -> np.ndarray:
    if model is not None:
        return _score_deepstarr(seqs, model)
    return np.array([score_single(s) for s in seqs], dtype=np.float32)


def load_deepstarr(weights_dir: Path):
    try:
        import torch
        for fn in ("deepstarr_human.pt", "deepstarr_human.pth"):
            p = weights_dir / fn
            if p.exists():
                m = torch.jit.load(str(p), map_location="cpu"); m.eval()
                print(f"Loaded DeepSTARR from {p}"); return m
    except Exception:
        pass
    return None


def _score_deepstarr(seqs, model):
    import torch
    enc = np.stack([one_hot(s) for s in seqs])
    with torch.no_grad():
        p = model(torch.from_numpy(enc))
        if isinstance(p, tuple): p = p[0]
        return p.squeeze().cpu().numpy()
