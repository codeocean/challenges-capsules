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

    # 2. Scorer — always attempt CNN training if no pre-trained weights
    model = load_deepstarr(WEIGHTS_DIR)
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

    # --- Cross-oracle validation (CNN vs PWM) ---
    if model is not None:
        from score import score_batch_pwm
        pwm_scores = score_batch_pwm(top_seqs)
        cross_corr = float(np.corrcoef(top_sc, pwm_scores)[0, 1])
        stats["cross_oracle"] = {
            "primary": "Trained CNN" if hasattr(model, 'conv1') else "DeepSTARR",
            "secondary": "PWM (quality^4 + cooperativity + GC + entropy)",
            "pearson_correlation": round(cross_corr, 4),
            "note": "Cross-oracle correlation between CNN and PWM scorers on top-K sequences"
        }
        stats["method"] = "Trained CNN oracle (K562 sequence features)" if hasattr(model, 'conv1') else "DeepSTARR neural network"
        print(f"\n  Cross-oracle correlation (CNN vs PWM): r={cross_corr:.3f}")

    write_stats(stats, RESULTS_DIR / "stats.json")
    write_manifest(RESULTS_DIR / "run_manifest.yaml", config, stats)

    # 9. Mandatory protocol artifacts
    _write_protocol_artifacts(RESULTS_DIR, config, stats, diversity_info,
                              model is not None, SEED_FASTA.exists())
    print("\n✓ Done — all outputs in /results/")


def _write_protocol_artifacts(results_dir: Path, config: dict, stats: dict,
                               diversity_info: dict, has_model: bool,
                               has_real_seeds: bool) -> None:
    """Write manifest.json, IMPLEMENTATION_SUMMARY.md, VALIDATION_NOTES.md."""
    import json, time
    ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    scorer = "Trained CNN oracle" if has_model else "PWM proxy (quality^4 + cooperativity + GC + entropy)"
    seeds = "Real K562 ENCODE ATAC-seq peaks" if has_real_seeds else "Synthetic seeds (GC-balanced, 200bp)"

    manifest = {
        "capsule_number": 3,
        "capsule_objective": "Design synthetic enhancer sequences for K562 using genetic algorithm with in silico scoring",
        "round_mission": "Protocol-compliant run with mandatory artifacts",
        "timestamp": ts,
        "created_files": ["top20.fasta", "enhancer_report.png", "stats.json",
                          "run_manifest.yaml", "manifest.json",
                          "IMPLEMENTATION_SUMMARY.md", "VALIDATION_NOTES.md"],
        "main_entrypoints": ["run.py"],
        "commands_run": ["python /code/run.py"],
        "outputs_produced": ["top20.fasta", "enhancer_report.png", "stats.json"],
        "dependencies_or_configs": {"scorer": scorer, "seed_source": seeds},
        "known_limitations": [
            "Uses PWM proxy scorer when DeepSTARR weights unavailable",
            "Uses synthetic seed sequences when real K562 peaks not in /data/",
            "Output named top20.fasta but contains top_k sequences (configurable)",
        ],
        "unresolved_issues": [
            "DeepSTARR model checkpoint not available as data asset",
            "Real K562 ATAC-seq peak sequences not available as data asset",
        ],
        "cli_entrypoint": True,
        "llm_or_agent_used": False,
        "bedrock_used": False,
        "bedrock_note": "Not applicable — no LLM needed in this capsule",
        "ga_config": config,
        "evaluation_summary": stats.get("evaluation", {}),
        "diversity": diversity_info,
    }
    with open(results_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    summary = f"""# Implementation Summary — Capsule 03: Enhancer Designer

## What Was Implemented
Genetic algorithm (GA) for designing synthetic enhancer-like DNA sequences
optimised for K562 cell-type activity, scored by an in silico oracle.

## Files
| File | Purpose |
|------|---------|
| `run.py` | CLI orchestrator — parses args, runs GA, writes outputs |
| `generate.py` | GA engine — seed generation, mutation, crossover, selection, filtering, diversity |
| `score.py` | PWM-based proxy scorer (or DeepSTARR wrapper if weights available) |
| `report.py` | Statistics, 6-panel publication figure, FASTA writer, YAML manifest |

## Architecture
- **CLI with argparse**: `--generations`, `--population_size`, `--mutation_rate`, `--crossover_prob`, `--top_k`, `--seed`
- **App Panel compatible** via named parameters
- **Deterministic**: random seed controls all stochastic steps

## How to Run
```bash
python /code/run.py --generations 75 --population_size 300 --top_k 25 --seed 7
```

## Scoring Method
- **Current**: PWM quality^4 + Gaussian cooperativity + GC content + trinucleotide entropy
- **Motifs**: GATA1, TAL1, SP1, NFE2, KLF1, MYC (K562-relevant transcription factors)
- **Upgrade path**: Drop DeepSTARR weights into /data/model_weights/ for neural scoring

## Evaluation
- Mann-Whitney U test: evolved vs random, evolved vs shuffled
- Cohen's d effect size
- Near-duplicate fraction check (< 50% threshold)
- Filtering: manufacturability (homopolymers, dinuc repeats, restriction sites) + motif explosion

## No LLM or Agent Needed
This capsule is purely computational — no LLM, no Bedrock, no API calls.
"""
    (results_dir / "IMPLEMENTATION_SUMMARY.md").write_text(summary)

    validation = f"""# Validation Notes — Capsule 03: Enhancer Designer

## Complete
- Genetic algorithm with configurable parameters
- PWM-based proxy scoring for K562 enhancer motifs
- Statistical evaluation (Mann-Whitney U, Cohen's d)
- Diversity analysis and near-duplicate filtering
- Manufacturability filtering (restriction sites, homopolymers, dinuc repeats)
- 6-panel publication-quality figure
- Annotated FASTA output with per-sequence metadata
- CLI with App Panel parameter support

## Partial
- **Scoring**: Using PWM proxy instead of DeepSTARR neural network
  - PWM captures motif composition but not sequence context/grammar
  - DeepSTARR would provide more biologically realistic predictions
  - Upgrade is drop-in: place weights in /data/model_weights/

## Assumptions
1. PWM motif quality scores correlate with enhancer activity (supported by literature)
2. K562-relevant motifs: GATA1, TAL1, SP1, NFE2, KLF1, MYC
3. Synthetic seeds with realistic GC content are adequate starting points
4. Diversity threshold of 10% edit distance is sufficient

## Limitations
- No real DeepSTARR model weights available as data asset
- No real ENCODE K562 ATAC-seq peak sequences available
- PWM scores are a proxy — may not perfectly predict experimental activity
- Single-objective optimization (no multi-oracle Pareto front)

## Blockers
- DeepSTARR checkpoint: requires GPU + specific model download
- K562 peak FASTA: requires ENCODE data download and processing

## Aqua Control Loop
- Aqua can trigger runs via CLI with different parameters
- Aqua can inspect stats.json for quantitative evaluation
- Aqua can compare top20.fasta across runs with different seeds
- Fully deterministic with seed control
"""
    (results_dir / "VALIDATION_NOTES.md").write_text(validation)


if __name__ == "__main__":
    main()
