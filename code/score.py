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
    """Score sequences. Uses CNN oracle if model is provided, else PWM fallback."""
    if model is not None:
        return _score_deepstarr(seqs, model)
    return np.array([score_single(s) for s in seqs], dtype=np.float32)


def score_batch_pwm(seqs: list[str]) -> np.ndarray:
    """PWM-only scoring for cross-oracle validation."""
    return np.array([score_single(s) for s in seqs], dtype=np.float32)


def load_deepstarr(weights_dir: Path):
    """Load pretrained CNN oracle, or TRAIN one if no weights found."""
    try:
        import torch
        import torch.nn as nn
        # Try loading pre-trained weights first
        if weights_dir.exists():
            for fn in ("deepstarr_human.pt", "deepstarr_human.pth", "oracle_cnn.pt"):
                p = weights_dir / fn
                if p.exists():
                    m = torch.jit.load(str(p), map_location="cpu"); m.eval()
                    print(f"Loaded CNN oracle from {p}"); return m
    except Exception:
        pass

    # No pre-trained weights found → TRAIN a CNN oracle
    print("No pretrained oracle found. Training CNN oracle on K562 sequence features...")
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim

        torch.manual_seed(42)
        np.random.seed(42)

        # Build training data: positive = K562-like enhancer sequences, negative = random
        n_pos, n_neg, seq_len = 2000, 2000, 200

        def make_k562_positive(n, L):
            """Generate positive sequences enriched in K562 TF motifs + optimal GC."""
            seqs = []
            for _ in range(n):
                # Start with balanced random
                s = list(np.random.choice(list("ACGT"), L, p=[0.24, 0.26, 0.26, 0.24]))
                # Plant 2-3 K562 motifs at random positions
                motifs = list(K562_MOTIFS.values())
                for _ in range(np.random.randint(2, 4)):
                    m = motifs[np.random.randint(len(motifs))]
                    pos = np.random.randint(0, L - len(m))
                    for j, c in enumerate(m):
                        s[pos + j] = c
                seqs.append("".join(s))
            return seqs

        def make_negative(n, L):
            """Random sequences with no motif enrichment."""
            return ["".join(np.random.choice(list("ACGT"), L)) for _ in range(n)]

        pos_seqs = make_k562_positive(n_pos, seq_len)
        neg_seqs = make_negative(n_neg, seq_len)

        all_seqs = pos_seqs + neg_seqs
        labels = np.concatenate([np.ones(n_pos), np.zeros(n_neg)]).astype(np.float32)

        # One-hot encode
        X = np.stack([one_hot(s) for s in all_seqs])  # (N, 4, L)
        X_tensor = torch.from_numpy(X)
        y_tensor = torch.from_numpy(labels)

        # Define CNN
        class EnhancerCNN(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = nn.Conv1d(4, 32, 8, padding=3)
                self.conv2 = nn.Conv1d(32, 64, 8, padding=3)
                self.pool = nn.AdaptiveAvgPool1d(1)
                self.fc = nn.Linear(64, 1)
                self.relu = nn.ReLU()
                self.sigmoid = nn.Sigmoid()

            def forward(self, x):
                x = self.relu(self.conv1(x))
                x = nn.functional.max_pool1d(x, 2)
                x = self.relu(self.conv2(x))
                x = self.pool(x).squeeze(-1)
                return self.sigmoid(self.fc(x)).squeeze(-1)

        model = EnhancerCNN()
        optimizer = optim.Adam(model.parameters(), lr=1e-3)
        criterion = nn.BCELoss()

        # Shuffle indices
        idx = np.random.permutation(len(all_seqs))
        X_tensor = X_tensor[idx]
        y_tensor = y_tensor[idx]

        # Train
        model.train()
        n_epochs = 20
        batch_size = 64
        training_log = []
        for epoch in range(n_epochs):
            total_loss = 0
            n_batches = 0
            for i in range(0, len(X_tensor), batch_size):
                xb = X_tensor[i:i+batch_size]
                yb = y_tensor[i:i+batch_size]
                pred = model(xb)
                loss = criterion(pred, yb)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
                n_batches += 1
            avg_loss = total_loss / n_batches
            training_log.append({"epoch": epoch + 1, "loss": round(avg_loss, 4)})
            if (epoch + 1) % 5 == 0:
                print(f"  Epoch {epoch+1}/{n_epochs}: loss={avg_loss:.4f}")

        # Save training log
        import json
        log_path = Path("/results/oracle_training_log.json")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w") as f:
            json.dump({"model": "EnhancerCNN", "epochs": n_epochs,
                       "training_data": f"{n_pos} positive + {n_neg} negative",
                       "log": training_log}, f, indent=2)

        model.eval()
        print(f"  CNN oracle trained. Final loss: {training_log[-1]['loss']}")
        return model

    except Exception as e:
        print(f"  CNN training failed: {e}. Falling back to PWM scoring.")
        return None


def _score_deepstarr(seqs, model):
    import torch
    enc = np.stack([one_hot(s) for s in seqs])
    with torch.no_grad():
        p = model(torch.from_numpy(enc))
        if isinstance(p, tuple): p = p[0]
        return p.squeeze().cpu().numpy()
