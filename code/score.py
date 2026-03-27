#!/usr/bin/env python3
"""score.py — PWM-based enhancer activity scoring for K562 sequences.

Uses vectorised Position Weight Matrix scanning, inter-motif cooperativity,
GC optimality, and sequence complexity to produce continuous, non-saturating
scores that mirror real enhancer biology.

Falls back to a pretrained DeepSTARR model when weights are available.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

import numpy as np

# ── Constants ─────────────────────────────────────────────────────────────
BASES = "ACGT"
BASE_IDX = {b: i for i, b in enumerate(BASES)}

# K562-enriched TF motifs (JASPAR consensus, N-free)
K562_MOTIFS: dict[str, str] = {
    "GATA1": "AGATAAGG",
    "TAL1":  "CAGATG",
    "SP1":   "GGGCGG",
    "NFE2":  "TGCTGAGTCA",
    "KLF1":  "CCACACCCT",
    "MYC":   "CACGTG",
}

# Cooperative TF pairs and required spacing
COOPERATIVE_PAIRS = [("GATA1", "TAL1"), ("GATA1", "KLF1"), ("SP1", "MYC")]
COOP_MIN, COOP_MAX = 10, 50

# Scoring hyper-parameters
QUALITY_POWER = 4          # Sharpens differentiation between partial and full matches
GOOD_HIT_THRESH = 0.80     # Minimum quality to count as a "good" hit
GC_OPTIMAL = 0.52          # K562 open-chromatin GC centre
WEIGHTS = (0.30, 0.20, 0.15, 0.20, 0.15)  # richness, hits, coop, gc, complexity


# ── Encoding helpers ──────────────────────────────────────────────────────

def one_hot(seq: str) -> np.ndarray:
    """Encode DNA as (4, L) float32 array; ambiguous bases → 0."""
    arr = np.zeros((4, len(seq)), dtype=np.float32)
    for i, c in enumerate(seq.upper()):
        idx = BASE_IDX.get(c)
        if idx is not None:
            arr[idx, i] = 1.0
    return arr


def reverse_complement(seq: str) -> str:
    return seq.upper().translate(str.maketrans("ACGT", "TGCA"))[::-1]


def gc_content(seq: str) -> float:
    s = seq.upper()
    return (s.count("G") + s.count("C")) / len(s) if s else 0.0


# ── Pre-compute motif one-hot matrices (module-level cache) ───────────────

def _build_motif_cache() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for name, consensus in K562_MOTIFS.items():
        fwd = one_hot(consensus)
        rc = one_hot(reverse_complement(consensus))
        cache[name] = (fwd, rc)
    return cache

_MOTIF_CACHE = _build_motif_cache()


# ── Vectorised motif scanning ─────────────────────────────────────────────

def _scan_one_strand(seq_oh: np.ndarray, motif_oh: np.ndarray) -> np.ndarray:
    """Cross-correlate seq with motif on one strand → quality per position."""
    n_pos = seq_oh.shape[1] - motif_oh.shape[1] + 1
    if n_pos <= 0:
        return np.zeros(1)
    scores = np.zeros(n_pos, dtype=np.float32)
    for row in range(4):
        scores += np.correlate(seq_oh[row], motif_oh[row], mode="valid")
    return scores / motif_oh.shape[1]          # normalise to [0, 1]


def scan_motif(seq_oh: np.ndarray, name: str) -> tuple[float, int, int]:
    """Scan both strands. Returns (best_quality, best_position, n_good_hits)."""
    fwd_oh, rc_oh = _MOTIF_CACHE[name]
    fwd_q = _scan_one_strand(seq_oh, fwd_oh)
    rc_q = _scan_one_strand(seq_oh, rc_oh)
    combined = np.maximum(fwd_q, rc_q)
    best_pos = int(np.argmax(combined))
    return float(combined[best_pos]), best_pos, int(np.sum(combined >= GOOD_HIT_THRESH))


# ── Single-sequence scorer ────────────────────────────────────────────────

def _trinuc_entropy(seq: str) -> float:
    """Shannon entropy of trinucleotide distribution, normalised to [0, 1]."""
    trimers = [seq[i:i + 3] for i in range(len(seq) - 2)]
    counts = Counter(trimers)
    total = sum(counts.values())
    if total == 0:
        return 0.0
    probs = np.array([c / total for c in counts.values()], dtype=np.float64)
    entropy = -np.sum(probs * np.log2(probs + 1e-12))
    max_ent = np.log2(min(64, total))
    return float(entropy / max_ent) if max_ent > 0 else 0.0


def score_single(seq: str) -> float:
    """Score one sequence. Returns a continuous value in ~[0.15, 0.90]."""
    s = seq.upper()
    seq_oh = one_hot(s)

    # 1. Motif scanning
    results: dict[str, tuple[float, int, int]] = {}
    for name in K562_MOTIFS:
        results[name] = scan_motif(seq_oh, name)

    # 2. Motif richness — power-transformed quality, averaged
    qualities = np.array([r[0] ** QUALITY_POWER for r in results.values()])
    motif_richness = float(qualities.mean())

    # 3. Good-hit count with diminishing returns
    total_good = sum(r[2] for r in results.values())
    hit_score = min(float(np.log1p(total_good) / np.log1p(15)), 1.0)

    # 4. Cooperativity — TF pairs at correct spacing
    coop = 0
    for tf1, tf2 in COOPERATIVE_PAIRS:
        _, p1, _ = results[tf1]
        _, p2, _ = results[tf2]
        d = abs(p1 - p2)
        if COOP_MIN <= d <= COOP_MAX:
            coop += 1
    cooperativity = coop / len(COOPERATIVE_PAIRS)

    # 5. GC penalty
    gc = gc_content(s)
    gc_score = max(0.0, 1.0 - abs(gc - GC_OPTIMAL) / 0.25)

    # 6. Sequence complexity
    complexity = _trinuc_entropy(s)

    w = WEIGHTS
    return (
        w[0] * motif_richness
        + w[1] * hit_score
        + w[2] * cooperativity
        + w[3] * gc_score
        + w[4] * complexity
    )


# ── Batch scorer (proxy or neural) ───────────────────────────────────────

def score_batch(seqs: list[str], model=None) -> np.ndarray:
    """Score a list of sequences. Uses DeepSTARR if model is provided."""
    if model is not None:
        return _score_deepstarr(seqs, model)
    return np.array([score_single(s) for s in seqs], dtype=np.float32)


def load_deepstarr(weights_dir: Path):
    """Try to load DeepSTARR TorchScript model; return None on failure."""
    try:
        import torch
        for ext in ("deepstarr_human.pt", "deepstarr_human.pth"):
            p = weights_dir / ext
            if p.exists():
                m = torch.jit.load(str(p), map_location="cpu")
                m.eval()
                print(f"Loaded DeepSTARR model from {p}")
                return m
    except Exception:
        pass
    return None


def _score_deepstarr(seqs: list[str], model) -> np.ndarray:
    import torch
    encoded = np.stack([one_hot(s) for s in seqs])
    with torch.no_grad():
        preds = model(torch.from_numpy(encoded))
        if isinstance(preds, tuple):
            preds = preds[0]
        return preds.squeeze().cpu().numpy()
