#!/usr/bin/env python3
"""Challenge 03 · Enhancer Designer — Main orchestrator.

Pipeline:
  1. Load or generate K562 enhancer seed sequences
  2. Load DeepSTARR model or fall back to PWM proxy scorer
  3. Run genetic algorithm (tournament selection, crossover, elitism)
  4. Score control sequences (random + dinucleotide-shuffled)
  5. Apply manufacturability filters
  6. Select diverse top-20 via k-mer farthest-point sampling
  7. Generate multi-panel figure, annotated FASTA, and stats JSON

Evaluation: Mann-Whitney U showing evolved > controls (p < 0.05).
"""
from __future__ import annotations

import random
from pathlib import Path

import numpy as np

from score import load_deepstarr, score_batch
from generate import (
    generate_seeds,
    generate_controls,
    load_seeds_fasta,
    run_ga,
    filter_population,
    select_diverse,
)
from report import (
    compute_stats,
    generate_figure,
    write_fasta,
    write_stats,
)

# ── Configuration ─────────────────────────────────────────────────────────

DATA_DIR      = Path("/data")
RESULTS_DIR   = Path("/results")
SEED_FASTA    = DATA_DIR / "k562_peaks.fasta"
WEIGHTS_DIR   = DATA_DIR / "model_weights"

N_GEN         = 50
POP_SIZE      = 200
TOP_K         = 20
MUT_RATE      = 0.04
CROSSOVER_P   = 0.6
ELITE_FRAC    = 0.05
TOURNAMENT    = 3
SEQ_LEN       = 200
N_CONTROLS    = 100
SEED          = 42


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)

    # ── 1. Seed sequences ─────────────────────────────────────────────────
    print("=" * 62)
    print("  ENHANCER DESIGNER — K562")
    print("=" * 62)

    if SEED_FASTA.exists():
        seeds = load_seeds_fasta(SEED_FASTA)
    else:
        print(f"Seed FASTA not found at {SEED_FASTA}")
        seeds = generate_seeds(n=100, seq_len=SEQ_LEN, rng=rng)

    # ── 2. Scorer ─────────────────────────────────────────────────────────
    model = load_deepstarr(WEIGHTS_DIR) if WEIGHTS_DIR.exists() else None
    if model is None:
        print("Using PWM-based proxy scorer (motif + cooperativity + GC + complexity)")

    def score_fn(seqs: list[str]) -> np.ndarray:
        return score_batch(seqs, model)

    # ── 3. Genetic algorithm ──────────────────────────────────────────────
    print(f"\nRunning GA: {N_GEN} generations, pop={POP_SIZE}, "
          f"mut={MUT_RATE}, xover={CROSSOVER_P}")
    pop, pop_scores, trajectory = run_ga(
        seeds, score_fn,
        n_gen=N_GEN, pop_size=POP_SIZE, mut_rate=MUT_RATE,
        crossover_prob=CROSSOVER_P, elite_frac=ELITE_FRAC,
        tournament_size=TOURNAMENT, seed=SEED,
    )

    # ── 4. Score controls ─────────────────────────────────────────────────
    print("\nScoring controls ...")
    rand_seqs, shuf_seqs = generate_controls(seeds, n=N_CONTROLS, rng=rng)
    rand_scores  = score_fn(rand_seqs)
    shuf_scores  = score_fn(shuf_seqs)
    seed_scores  = score_fn(seeds)

    # ── 5. Manufacturability filter ───────────────────────────────────────
    print("\nFiltering for manufacturability ...")
    filt_seqs, filt_scores, n_removed = filter_population(pop, pop_scores)
    print(f"  Removed {n_removed}/{len(pop)} non-manufacturable sequences")

    if len(filt_seqs) < TOP_K:
        print(f"  Warning: only {len(filt_seqs)} pass filters; "
              f"relaxing to unfiltered top-{TOP_K}")
        ranked = np.argsort(pop_scores)[::-1]
        filt_seqs = [pop[i] for i in ranked[:TOP_K * 3]]
        filt_scores = pop_scores[ranked[:TOP_K * 3]]
        n_removed = 0

    # ── 6. Diverse top-K selection ────────────────────────────────────────
    print(f"\nSelecting diverse top-{TOP_K} (k-mer farthest-point) ...")
    top_seqs, top_scores, sel_idx = select_diverse(
        filt_seqs, filt_scores, top_k=TOP_K,
    )
    print(f"  Selected {len(top_seqs)} sequences: "
          f"score range [{top_scores.min():.4f}, {top_scores.max():.4f}]")

    # ── 7. Write outputs ──────────────────────────────────────────────────
    print("\nWriting outputs ...")
    write_fasta(top_seqs, top_scores, RESULTS_DIR / "top20.fasta")

    generate_figure(
        top_seqs, top_scores,
        seed_scores, rand_scores, shuf_scores,
        trajectory,
        RESULTS_DIR / "boxplot.png",
    )

    stats = compute_stats(
        top_scores, seed_scores, rand_scores, shuf_scores,
        trajectory, n_removed, len(pop),
    )
    write_stats(stats, RESULTS_DIR / "stats.json")

    print("\nDone. All outputs in /results/")


if __name__ == "__main__":
    main()
