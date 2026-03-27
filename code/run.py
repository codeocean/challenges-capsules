#!/usr/bin/env python3
"""Challenge 03 · Enhancer Designer — Main orchestrator.

Configurable via CLI flags (App Panel compatible with named_parameters).

Usage:
  python run.py                            # defaults
  python run.py --generations 100 --top_k 30 --seed 123
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np

from score import load_deepstarr, score_batch
from generate import (
    generate_seeds, generate_controls, load_seeds_fasta,
    run_ga, filter_population, select_diverse,
    pairwise_edit_distance, near_duplicate_fraction,
)
from report import (
    compute_stats, generate_figure, write_fasta,
    write_stats, write_manifest,
)

DATA_DIR    = Path("/data")
RESULTS_DIR = Path("/results")
SEED_FASTA  = DATA_DIR / "k562_peaks.fasta"
WEIGHTS_DIR = DATA_DIR / "model_weights"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="K562 Enhancer Designer")
    p.add_argument("--generations",    type=int,   default=50)
    p.add_argument("--population_size", type=int,  default=200)
    p.add_argument("--mutation_rate",  type=float, default=0.04)
    p.add_argument("--crossover_prob", type=float, default=0.6)
    p.add_argument("--top_k",         type=int,   default=20)
    p.add_argument("--seed",          type=int,   default=42)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)

    config = {
        "n_gen": args.generations, "pop_size": args.population_size,
        "mut_rate": args.mutation_rate, "xover_prob": args.crossover_prob,
        "elite_frac": 0.05, "tourn_size": 3,
        "top_k": args.top_k, "seed": args.seed, "seq_len": 200,
    }

    print("═" * 62)
    print("  ENHANCER DESIGNER — K562")
    print("═" * 62)
    print(f"  Params: gen={config['n_gen']} pop={config['pop_size']} "
          f"mut={config['mut_rate']} xover={config['xover_prob']} "
          f"top_k={config['top_k']} seed={config['seed']}")
    print("═" * 62)

    # 1. Seeds
    if SEED_FASTA.exists():
        seeds = load_seeds_fasta(SEED_FASTA)
    else:
        print(f"Seed FASTA not at {SEED_FASTA} → generating synthetic seeds")
        seeds = generate_seeds(n=100, seq_len=config["seq_len"], rng=rng)

    # 2. Scorer
    model = load_deepstarr(WEIGHTS_DIR) if WEIGHTS_DIR.exists() else None
    if model is None:
        print("Using PWM proxy scorer (quality^4 + cooperativity + GC + entropy)\n")
    score_fn = lambda seqs: score_batch(seqs, model)

    # 3. GA
    print(f"Running GA: {config['n_gen']} gen × {config['pop_size']} pop")
    pop, pop_sc, traj = run_ga(
        seeds, score_fn,
        n_gen=config["n_gen"], pop_size=config["pop_size"],
        mut_rate=config["mut_rate"], xover_prob=config["xover_prob"],
        elite_frac=config["elite_frac"], tourn_size=config["tourn_size"],
        seed=config["seed"],
    )

    # 4. Controls
    print("\nScoring controls …")
    rand_seqs, shuf_seqs = generate_controls(seeds, n=100, rng=rng)
    rand_sc = score_fn(rand_seqs)
    shuf_sc = score_fn(shuf_seqs)
    seed_sc = score_fn(seeds)

    # 5. Filter
    print("\nFiltering …")
    filt_seqs, filt_sc, filt_stats = filter_population(pop, pop_sc)
    print(f"  mfg_fail={filt_stats['mfg_fail']}  "
          f"motif_explosion={filt_stats['motif_explosion_fail']}  "
          f"kept={filt_stats['kept']}/{filt_stats['total']}")

    if len(filt_seqs) < config["top_k"]:
        print(f"  ⚠ Only {len(filt_seqs)} pass filters; relaxing to unfiltered top")
        ranked = np.argsort(pop_sc)[::-1][:config["top_k"] * 3]
        filt_seqs = [pop[i] for i in ranked]
        filt_sc = pop_sc[ranked]

    # 6. Diverse selection
    print(f"\nSelecting diverse top-{config['top_k']} …")
    top_seqs, top_sc, _ = select_diverse(filt_seqs, filt_sc, top_k=config["top_k"])
    print(f"  range [{top_sc.min():.4f}, {top_sc.max():.4f}]")

    # 7. Diversity validation
    div_mat = pairwise_edit_distance(top_seqs)
    near_dup = near_duplicate_fraction(top_seqs, threshold=0.10)
    triu = div_mat[np.triu_indices(len(div_mat), k=1)]
    diversity_info = {
        "mean_pairwise_dist": round(float(triu.mean()), 4),
        "min_pairwise_dist":  round(float(triu.min()), 4),
        "near_dup_fraction":  round(near_dup, 4),
        "near_dup_threshold": 0.10,
        "diversity_pass": near_dup < 0.50,
    }
    print(f"  near-dup fraction={near_dup:.2f}  "
          f"[{'PASS ✓' if near_dup < 0.50 else 'FAIL ✗'}]")

    # 8. Write outputs
    print("\nWriting outputs …")
    write_fasta(top_seqs, top_sc, RESULTS_DIR / "top20.fasta")

    generate_figure(
        top_seqs, top_sc, seed_sc, rand_sc, shuf_sc,
        seeds, rand_seqs, shuf_seqs,
        traj, div_mat, RESULTS_DIR / "enhancer_report.png",
    )

    stats = compute_stats(
        top_sc, seed_sc, rand_sc, shuf_sc, traj, filt_stats, diversity_info,
    )
    write_stats(stats, RESULTS_DIR / "stats.json")
    write_manifest(RESULTS_DIR / "run_manifest.yaml", config, stats)

    print("\n✓ Done — all outputs in /results/")


if __name__ == "__main__":
    main()
