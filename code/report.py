#!/usr/bin/env python3
"""report.py — Publication-quality 6-panel figure, annotated FASTA, stats
JSON, and YAML run manifest for the K562 Enhancer Designer.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from scipy.stats import mannwhitneyu

from score import K562_MOTIFS, GOOD_HIT_THRESH, gc_content, one_hot, scan_motif

# ── Colour palette (colour-blind safe) ────────────────────────────────────
C = {"evolved": "#2ca02c", "seed": "#1f77b4",
     "shuffled": "#ff7f0e", "random": "#7f7f7f"}


# ── FASTA output with rich annotations ────────────────────────────────────

def write_fasta(seqs: list[str], scores: np.ndarray, path: Path) -> None:
    from generate import check_manufacturability, check_motif_explosion
    with open(path, "w") as f:
        for i, (seq, sc) in enumerate(zip(seqs, scores)):
            gc = gc_content(seq)
            oh = one_hot(seq)
            parts = []
            for nm in K562_MOTIFS:
                r = scan_motif(oh, nm)
                if r["n_good"] > 0:
                    parts.append(f"{nm}({r['n_good']})")
            mfg_ok, mfg_iss = check_manufacturability(seq)
            exp_ok, exp_iss = check_motif_explosion(seq)
            flags = []
            if not mfg_ok:
                flags.append("MFG:" + ";".join(mfg_iss))
            if not exp_ok:
                flags.append("EXP:" + exp_iss)
            status = "PASS" if (mfg_ok and exp_ok) else "|".join(flags)
            hdr = (f">evolved_{i+1:03d} score={sc:.4f} GC={gc:.3f} "
                   f"len={len(seq)} motifs=[{','.join(parts) or 'none'}] "
                   f"filter={status}")
            f.write(f"{hdr}\n{seq}\n")
    print(f"  → {path.name}: {len(seqs)} sequences")


# ── Motif landscape helpers ───────────────────────────────────────────────

def _motif_matrix(seqs: list[str]) -> np.ndarray:
    """(n_seqs × n_motifs) matrix of best-hit quality for each motif."""
    names = list(K562_MOTIFS.keys())
    mat = np.zeros((len(seqs), len(names)))
    for i, seq in enumerate(seqs):
        oh = one_hot(seq)
        for j, nm in enumerate(names):
            mat[i, j] = scan_motif(oh, nm)["quality"]
    return mat


def _mean_good_hits(seqs: list[str]) -> np.ndarray:
    """Mean number of good hits per motif across a set of sequences."""
    names = list(K562_MOTIFS.keys())
    counts = np.zeros(len(names))
    for seq in seqs:
        oh = one_hot(seq)
        for j, nm in enumerate(names):
            counts[j] += scan_motif(oh, nm)["n_good"]
    return counts / max(len(seqs), 1)


# ── Statistics ────────────────────────────────────────────────────────────

def compute_stats(
    evolved: np.ndarray, seed_sc: np.ndarray,
    random_sc: np.ndarray, shuffled_sc: np.ndarray,
    traj: list[dict], filt_stats: dict, diversity_info: dict,
) -> dict:
    def _mw(a, b):
        u, p = mannwhitneyu(a, b, alternative="greater")
        return float(u), float(p)
    def _d(a, b):
        ps = np.sqrt((np.var(a) + np.var(b)) / 2)
        return round(float((np.mean(a) - np.mean(b)) / ps), 4) if ps > 0 else 0.0

    ur, pr = _mw(evolved, random_sc)
    us, ps = _mw(evolved, shuffled_sc)
    usd, psd = _mw(evolved, seed_sc)

    return {
        "evaluation": {
            "p_vs_random": pr, "p_vs_shuffled": ps, "p_vs_seeds": psd,
            "U_vs_random": ur,
            "d_vs_random": _d(evolved, random_sc),
            "d_vs_shuffled": _d(evolved, shuffled_sc),
            "d_vs_seeds": _d(evolved, seed_sc),
            "pass_vs_random": pr < 0.05, "pass_vs_shuffled": ps < 0.05,
        },
        "scores": {
            "mean_evolved": round(float(evolved.mean()), 4),
            "std_evolved":  round(float(evolved.std()), 4),
            "mean_seeds":   round(float(seed_sc.mean()), 4),
            "mean_random":  round(float(random_sc.mean()), 4),
            "mean_shuffled": round(float(shuffled_sc.mean()), 4),
        },
        "counts": {
            "n_evolved": len(evolved), "n_seeds": len(seed_sc),
            "n_random": len(random_sc), "n_shuffled": len(shuffled_sc),
        },
        "filtering": filt_stats,
        "diversity": diversity_info,
        "trajectory": {
            "generations": traj[-1]["gen"] if traj else 0,
            "score_gen1": round(traj[0]["best"], 4) if traj else 0,
            "score_final": round(traj[-1]["best"], 4) if traj else 0,
            "improvement": round(traj[-1]["best"] - traj[0]["best"], 4) if traj else 0,
        },
        "method": {
            "scoring": "PWM quality^4 + Gaussian cooperativity + GC + trinuc entropy",
            "target": "K562",
            "criterion": "Mann-Whitney p < 0.05 (one-sided greater)",
        },
    }


def write_stats(stats: dict, path: Path) -> None:
    with open(path, "w") as f:
        json.dump(stats, f, indent=2)
    e = stats["evaluation"]
    s = stats["scores"]
    tag = lambda p: "PASS ✓" if p else "FAIL ✗"
    print(f"\n{'═'*62}")
    print(f"  EVALUATION RESULTS")
    print(f"{'═'*62}")
    print(f"  vs Random:   p={e['p_vs_random']:.2e}  d={e['d_vs_random']}  [{tag(e['pass_vs_random'])}]")
    print(f"  vs Shuffled: p={e['p_vs_shuffled']:.2e}  d={e['d_vs_shuffled']}  [{tag(e['pass_vs_shuffled'])}]")
    print(f"  vs Seeds:    p={e['p_vs_seeds']:.2e}  d={e['d_vs_seeds']}")
    print(f"  Means: evolved={s['mean_evolved']}  seed={s['mean_seeds']}  "
          f"rand={s['mean_random']}  shuf={s['mean_shuffled']}")
    di = stats["diversity"]
    print(f"  Diversity: mean_dist={di['mean_pairwise_dist']:.3f}  "
          f"near_dup_frac={di['near_dup_fraction']:.2f}  "
          f"[{'PASS ✓' if di['diversity_pass'] else 'FAIL ✗'}]")
    print(f"  Filtering: {stats['filtering']}")
    print(f"{'═'*62}\n  → {path.name}")


# ── Run manifest ──────────────────────────────────────────────────────────

def write_manifest(path: Path, config: dict, stats: dict) -> None:
    lines = [
        "# Enhancer Designer — Run Manifest",
        f"timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
        f"target_cell_type: K562",
        f"sequence_length: {config.get('seq_len', 200)}",
        "",
        "# GA parameters",
        f"generations: {config['n_gen']}",
        f"population_size: {config['pop_size']}",
        f"mutation_rate: {config['mut_rate']}",
        f"crossover_prob: {config['xover_prob']}",
        f"elite_fraction: {config['elite_frac']}",
        f"tournament_size: {config['tourn_size']}",
        f"top_k: {config['top_k']}",
        f"random_seed: {config['seed']}",
        "",
        "# Scoring",
        "scoring_method: PWM quality^4 + Gaussian cooperativity + GC + trinuc entropy",
        f"motifs: [{', '.join(K562_MOTIFS.keys())}]",
        "",
        "# Filters",
        "gc_range: [0.30, 0.70]",
        "max_homopolymer: 6",
        "max_dinuc_repeat: 4",
        "restriction_sites: [EcoRI, BamHI, HindIII, NotI]",
        "max_single_motif_coverage: 0.30",
        "",
        "# Results",
        f"best_score: {stats['trajectory']['score_final']}",
        f"improvement: {stats['trajectory']['improvement']}",
        f"p_vs_random: {stats['evaluation']['p_vs_random']:.2e}",
        f"p_vs_shuffled: {stats['evaluation']['p_vs_shuffled']:.2e}",
        f"diversity_pass: {stats['diversity']['diversity_pass']}",
    ]
    path.write_text("\n".join(lines) + "\n")
    print(f"  → {path.name}")


# ── 6-panel figure ────────────────────────────────────────────────────────

def generate_figure(
    ev_seqs: list[str], ev_scores: np.ndarray,
    seed_scores: np.ndarray, rand_scores: np.ndarray, shuf_scores: np.ndarray,
    seed_seqs: list[str], rand_seqs: list[str], shuf_seqs: list[str],
    traj: list[dict], diversity_mat: np.ndarray,
    path: Path,
) -> None:
    """2×3 publication-quality panel."""
    fig = plt.figure(figsize=(18, 11))
    gs = gridspec.GridSpec(2, 3, hspace=0.34, wspace=0.30,
                           left=0.05, right=0.97, top=0.92, bottom=0.06)

    rng = np.random.RandomState(0)
    groups = [ev_scores, seed_scores, shuf_scores, rand_scores]
    labels = ["Evolved", "Seeds", "Shuffled", "Random"]
    cols = [C["evolved"], C["seed"], C["shuffled"], C["random"]]

    # ── A: Score distributions ────────────────────────────────────────────
    ax = fig.add_subplot(gs[0, 0])
    bp = ax.boxplot(groups, labels=labels, patch_artist=True, widths=0.5,
                    medianprops=dict(color="k", lw=1.5),
                    flierprops=dict(marker=".", ms=3))
    for p, c in zip(bp["boxes"], cols):
        p.set_facecolor(c); p.set_alpha(0.5)
    for i, (g, c) in enumerate(zip(groups, cols)):
        ax.scatter(np.full(len(g), i+1) + rng.normal(0, 0.06, len(g)), g,
                   c=c, alpha=0.55, s=10, edgecolors="none", zorder=3)
    ax.set_ylabel("Enhancer Score"); ax.grid(axis="y", alpha=0.15)
    ax.set_title("A. Score Distributions", fontweight="bold", loc="left")

    # ── B: GA trajectory ──────────────────────────────────────────────────
    ax = fig.add_subplot(gs[0, 1])
    gens = [t["gen"] for t in traj]
    ax.fill_between(gens, [t["mean"]-t["std"] for t in traj],
                    [t["mean"]+t["std"] for t in traj],
                    alpha=0.15, color=C["evolved"])
    ax.plot(gens, [t["best"] for t in traj], "-", color=C["evolved"], lw=2, label="Best")
    ax.plot(gens, [t["mean"] for t in traj], "--", color=C["evolved"], lw=1.5, label="Mean")
    ax.plot(gens, [t["min"] for t in traj], ":", color=C["random"], lw=1, label="Min")
    ax.set_xlabel("Generation"); ax.set_ylabel("Score")
    ax.legend(fontsize=8, framealpha=0.8); ax.grid(alpha=0.15)
    ax.set_title("B. Optimisation Trajectory", fontweight="bold", loc="left")

    # ── C: Motif quality heatmap ──────────────────────────────────────────
    ax = fig.add_subplot(gs[0, 2])
    mat = _motif_matrix(ev_seqs)
    im = ax.imshow(mat, cmap="YlGn", vmin=0.5, vmax=1.0, aspect="auto")
    ax.set_xticks(range(len(K562_MOTIFS)))
    ax.set_xticklabels(K562_MOTIFS.keys(), rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Sequence")
    ax.set_title("C. Motif Match Quality", fontweight="bold", loc="left")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Quality")

    # ── D: Score vs GC (all groups) ───────────────────────────────────────
    ax = fig.add_subplot(gs[1, 0])
    for seqs, scores, lab, c in [
        (ev_seqs, ev_scores, "Evolved", C["evolved"]),
        (seed_seqs, seed_scores, "Seeds", C["seed"]),
        (shuf_seqs, shuf_scores, "Shuffled", C["shuffled"]),
        (rand_seqs, rand_scores, "Random", C["random"]),
    ]:
        gcs = [gc_content(s) for s in seqs]
        ax.scatter(gcs, scores, c=c, s=14, alpha=0.5, label=lab, edgecolors="none")
    ax.axvspan(0.30, 0.70, alpha=0.04, color="green")
    ax.axvline(0.52, ls="--", color="grey", lw=0.6, alpha=0.5)
    ax.set_xlabel("GC Content"); ax.set_ylabel("Score")
    ax.legend(fontsize=7, markerscale=1.5, framealpha=0.8); ax.grid(alpha=0.15)
    ax.set_title("D. Score vs GC Content", fontweight="bold", loc="left")

    # ── E: Diversity heatmap ──────────────────────────────────────────────
    ax = fig.add_subplot(gs[1, 1])
    im = ax.imshow(diversity_mat, cmap="YlOrRd", vmin=0, aspect="auto")
    ax.set_xlabel("Sequence"); ax.set_ylabel("Sequence")
    ax.set_title("E. Pairwise Hamming Distance", fontweight="bold", loc="left")
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("Norm. Distance")
    triu = diversity_mat[np.triu_indices(len(diversity_mat), k=1)]
    ax.text(0.02, 0.97, f"mean={triu.mean():.3f}\nmin={triu.min():.3f}",
            transform=ax.transAxes, va="top", fontsize=7,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.85))

    # ── F: Motif enrichment (evolved vs controls) ─────────────────────────
    ax = fig.add_subplot(gs[1, 2])
    names = list(K562_MOTIFS.keys())
    x = np.arange(len(names))
    w = 0.20
    for offset, (seqs, lab, c) in enumerate([
        (ev_seqs, "Evolved", C["evolved"]),
        (seed_seqs, "Seeds", C["seed"]),
        (shuf_seqs, "Shuffled", C["shuffled"]),
        (rand_seqs, "Random", C["random"]),
    ]):
        vals = _mean_good_hits(seqs)
        ax.bar(x + (offset - 1.5) * w, vals, w, label=lab, color=c, alpha=0.75)
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Mean Good Hits / Seq"); ax.legend(fontsize=7, framealpha=0.8)
    ax.grid(axis="y", alpha=0.15)
    ax.set_title("F. Motif Enrichment", fontweight="bold", loc="left")

    fig.suptitle("Enhancer Designer — K562 Synthetic Enhancer Optimisation",
                 fontsize=15, fontweight="bold")
    fig.savefig(str(path), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  → {path.name}")
