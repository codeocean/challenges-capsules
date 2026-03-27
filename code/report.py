#!/usr/bin/env python3
"""report.py — Publication-quality figures, FASTA output, and statistics
for the Enhancer Designer challenge.

Generates a four-panel figure (score distributions, GA trajectory,
score-vs-GC scatter, pairwise diversity heatmap) plus annotated FASTA
and comprehensive stats JSON.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from scipy.stats import mannwhitneyu

from score import K562_MOTIFS, gc_content, scan_motif, one_hot, GOOD_HIT_THRESH

# ── Colour palette (colour-blind safe) ────────────────────────────────────

C_EVOLVED = "#2ca02c"
C_SEED    = "#1f77b4"
C_SHUFFLED = "#ff7f0e"
C_RANDOM  = "#7f7f7f"


# ── FASTA output ──────────────────────────────────────────────────────────

def write_fasta(
    seqs: list[str],
    scores: np.ndarray,
    path: Path,
) -> None:
    """Write annotated FASTA with per-sequence GC, motif hits, and mfg status."""
    from generate import check_manufacturability

    with open(path, "w") as f:
        for i, (seq, sc) in enumerate(zip(seqs, scores)):
            gc = gc_content(seq)
            oh = one_hot(seq)
            motif_parts = []
            for name in K562_MOTIFS:
                q, _, ng = scan_motif(oh, name)
                if q >= GOOD_HIT_THRESH:
                    motif_parts.append(f"{name}({ng})")
            motifs_str = ",".join(motif_parts) if motif_parts else "none"
            mfg_ok, issues = check_manufacturability(seq)
            mfg_str = "PASS" if mfg_ok else "FAIL:" + ";".join(issues)
            hdr = (
                f">evolved_{i+1:03d} "
                f"score={sc:.4f} GC={gc:.3f} len={len(seq)} "
                f"motifs=[{motifs_str}] mfg={mfg_str}"
            )
            f.write(f"{hdr}\n{seq}\n")
    print(f"  → {path.name}: {len(seqs)} sequences")


# ── Statistics ────────────────────────────────────────────────────────────

def compute_stats(
    evolved: np.ndarray,
    seed_sc: np.ndarray,
    random_sc: np.ndarray,
    shuffled_sc: np.ndarray,
    trajectory: list[dict],
    n_filtered: int,
    n_total: int,
) -> dict:
    """Compute Mann-Whitney tests, effect sizes, and summary metrics."""
    def _mw(a, b):
        u, p = mannwhitneyu(a, b, alternative="greater")
        return float(u), float(p)

    def _cohend(a, b):
        ps = np.sqrt((np.var(a) + np.var(b)) / 2)
        return float((np.mean(a) - np.mean(b)) / ps) if ps > 0 else 0.0

    u_r, p_r = _mw(evolved, random_sc)
    u_s, p_s = _mw(evolved, shuffled_sc)
    u_seed, p_seed = _mw(evolved, seed_sc)

    return {
        "mann_whitney_p_vs_random":   p_r,
        "mann_whitney_p_vs_shuffled": p_s,
        "mann_whitney_p_vs_seeds":    p_seed,
        "mann_whitney_U_vs_random":   u_r,
        "effect_size_vs_random":   round(_cohend(evolved, random_sc), 4),
        "effect_size_vs_shuffled": round(_cohend(evolved, shuffled_sc), 4),
        "effect_size_vs_seeds":    round(_cohend(evolved, seed_sc), 4),
        "mean_evolved":  round(float(evolved.mean()), 4),
        "std_evolved":   round(float(evolved.std()), 4),
        "mean_seeds":    round(float(seed_sc.mean()), 4),
        "mean_random":   round(float(random_sc.mean()), 4),
        "mean_shuffled": round(float(shuffled_sc.mean()), 4),
        "n_evolved": len(evolved),
        "n_seeds":   len(seed_sc),
        "n_random":  len(random_sc),
        "n_shuffled": len(shuffled_sc),
        "n_filtered_out": n_filtered,
        "n_population": n_total,
        "generations": trajectory[-1]["gen"] if trajectory else 0,
        "best_score_gen1":  trajectory[0]["best"]  if trajectory else 0,
        "best_score_final": trajectory[-1]["best"] if trajectory else 0,
        "scoring_method": "PWM log-quality + cooperativity + GC + complexity (proxy)",
        "target_cell_type": "K562",
        "pass_criterion": "Mann-Whitney p < 0.05 (one-sided greater)",
    }


def write_stats(stats: dict, path: Path) -> None:
    with open(path, "w") as f:
        json.dump(stats, f, indent=2)

    p_r = stats["mann_whitney_p_vs_random"]
    p_s = stats["mann_whitney_p_vs_shuffled"]
    p_sd = stats["mann_whitney_p_vs_seeds"]
    tag = lambda p: "PASS ✓" if p < 0.05 else "FAIL ✗"

    print(f"\n{'═' * 62}")
    print(f"  EVALUATION SUMMARY")
    print(f"{'═' * 62}")
    print(f"  Evolved vs Random:   p = {p_r:.2e}  [{tag(p_r)}]")
    print(f"  Evolved vs Shuffled: p = {p_s:.2e}  [{tag(p_s)}]")
    print(f"  Evolved vs Seeds:    p = {p_sd:.2e}  [{tag(p_sd)}]")
    print(f"  Effect size d (vs random):   {stats['effect_size_vs_random']}")
    print(f"  Effect size d (vs shuffled): {stats['effect_size_vs_shuffled']}")
    print(f"  Mean evolved={stats['mean_evolved']:.4f}  "
          f"seeds={stats['mean_seeds']:.4f}  "
          f"random={stats['mean_random']:.4f}  "
          f"shuffled={stats['mean_shuffled']:.4f}")
    print(f"  Filtered out: {stats['n_filtered_out']}/{stats['n_population']}")
    print(f"{'═' * 62}")
    print(f"  → {path.name}")


# ── Multi-panel figure ────────────────────────────────────────────────────

def _pairwise_hamming(seqs: list[str]) -> np.ndarray:
    """Pairwise Hamming distance matrix (normalised to [0, 1])."""
    n = len(seqs)
    mat = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = sum(a != b for a, b in zip(seqs[i], seqs[j])) / len(seqs[i])
            mat[i, j] = mat[j, i] = d
    return mat


def generate_figure(
    evolved_seqs: list[str],
    evolved_scores: np.ndarray,
    seed_scores: np.ndarray,
    random_scores: np.ndarray,
    shuffled_scores: np.ndarray,
    trajectory: list[dict],
    path: Path,
) -> None:
    """Create a 2×2 publication-quality panel."""
    fig = plt.figure(figsize=(14, 11))
    gs = gridspec.GridSpec(2, 2, hspace=0.32, wspace=0.30)

    # ── Panel A: Score distributions (box + strip) ────────────────────────
    ax_a = fig.add_subplot(gs[0, 0])
    groups = [evolved_scores, seed_scores, shuffled_scores, random_scores]
    labels = ["Evolved", "Seeds", "Shuffled", "Random"]
    colours = [C_EVOLVED, C_SEED, C_SHUFFLED, C_RANDOM]

    bp = ax_a.boxplot(
        groups, labels=labels, patch_artist=True, widths=0.5,
        medianprops=dict(color="black", linewidth=1.5),
        flierprops=dict(marker=".", markersize=3),
    )
    for patch, c in zip(bp["boxes"], colours):
        patch.set_facecolor(c)
        patch.set_alpha(0.55)

    # Overlay individual points (jittered)
    rng = np.random.RandomState(0)
    for i, (grp, c) in enumerate(zip(groups, colours)):
        jitter = rng.normal(0, 0.06, size=len(grp))
        ax_a.scatter(
            np.full(len(grp), i + 1) + jitter, grp,
            c=c, alpha=0.6, s=12, edgecolors="none", zorder=3,
        )

    ax_a.set_ylabel("Enhancer Activity Score")
    ax_a.set_title("A. Score Distributions", fontweight="bold", loc="left")
    ax_a.grid(axis="y", alpha=0.2)

    # ── Panel B: GA evolution trajectory ──────────────────────────────────
    ax_b = fig.add_subplot(gs[0, 1])
    gens = [t["gen"] for t in trajectory]
    bests = [t["best"] for t in trajectory]
    means = [t["mean"] for t in trajectory]
    stds = [t["std"] for t in trajectory]
    mins  = [t["min"] for t in trajectory]

    ax_b.fill_between(
        gens,
        [m - s for m, s in zip(means, stds)],
        [m + s for m, s in zip(means, stds)],
        alpha=0.18, color=C_EVOLVED,
    )
    ax_b.plot(gens, bests, "-", color=C_EVOLVED, lw=2, label="Best")
    ax_b.plot(gens, means, "--", color=C_EVOLVED, lw=1.5, label="Mean")
    ax_b.plot(gens, mins, ":", color=C_RANDOM, lw=1, label="Min")
    ax_b.set_xlabel("Generation")
    ax_b.set_ylabel("Score")
    ax_b.set_title("B. GA Optimisation Trajectory", fontweight="bold", loc="left")
    ax_b.legend(fontsize=9, framealpha=0.8)
    ax_b.grid(alpha=0.2)

    # ── Panel C: Score vs GC content ──────────────────────────────────────
    ax_c = fig.add_subplot(gs[1, 0])
    ev_gc = [gc_content(s) for s in evolved_seqs]
    ax_c.scatter(ev_gc, evolved_scores, c=C_EVOLVED, s=40, alpha=0.8,
                 edgecolors="white", linewidths=0.5, label="Evolved", zorder=3)
    # Add reference bands
    ax_c.axvspan(0.30, 0.70, alpha=0.06, color="green",
                 label="Mfg. GC range")
    ax_c.axvline(0.52, ls="--", color="grey", lw=0.8, alpha=0.5)
    ax_c.set_xlabel("GC Content")
    ax_c.set_ylabel("Score")
    ax_c.set_title("C. Score vs GC Content", fontweight="bold", loc="left")
    ax_c.legend(fontsize=9, framealpha=0.8)
    ax_c.grid(alpha=0.2)

    # ── Panel D: Pairwise diversity heatmap ───────────────────────────────
    ax_d = fig.add_subplot(gs[1, 1])
    dist_mat = _pairwise_hamming(evolved_seqs)
    im = ax_d.imshow(dist_mat, cmap="YlOrRd", vmin=0, aspect="auto")
    ax_d.set_xlabel("Sequence Index")
    ax_d.set_ylabel("Sequence Index")
    ax_d.set_title("D. Pairwise Hamming Distance", fontweight="bold", loc="left")
    cbar = fig.colorbar(im, ax=ax_d, fraction=0.046, pad=0.04)
    cbar.set_label("Normalised Distance")

    # Diversity metric annotation
    triu = dist_mat[np.triu_indices(len(dist_mat), k=1)]
    mean_dist = triu.mean()
    min_dist = triu.min()
    ax_d.text(
        0.02, 0.98,
        f"mean dist = {mean_dist:.3f}\nmin dist = {min_dist:.3f}",
        transform=ax_d.transAxes, va="top", fontsize=8,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8),
    )

    fig.suptitle(
        "Enhancer Designer — K562 Synthetic Enhancer Optimisation",
        fontsize=14, fontweight="bold", y=0.98,
    )
    fig.savefig(str(path), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  → {path.name}")
