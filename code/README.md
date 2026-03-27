# Challenge 03: Enhancer Designer 🧬

## What This Capsule Does

Designs synthetic K562 enhancer DNA sequences via a genetic algorithm
with biologically-informed scoring, manufacturability filtering, and
diversity-aware selection.

### Pipeline

1. **Seed generation** — 100 K562-like sequences with embedded TF motifs
   (GATA1, TAL1, SP1, NF-E2, KLF1, MYC) in GC-matched backgrounds.
   Uses real FASTA if attached at `/data/k562_peaks.fasta`.
2. **Scoring oracle** — Position Weight Matrix log-quality scoring with
   inter-motif cooperativity, GC optimality, and sequence complexity.
   Falls back to a pretrained DeepSTARR model when weights are at
   `/data/model_weights/deepstarr_human.pt`.
3. **Genetic algorithm** — 50 generations, population 200, tournament
   selection (k=3), single-point crossover (p=0.6), point mutation
   (rate=0.04), and 5 % elitism.
4. **Manufacturability filter** — GC 30–70 %, no homopolymer >6 bp,
   no dinucleotide repeats >4 units, no EcoRI/BamHI/HindIII/NotI sites.
5. **Diversity selection** — 4-mer farthest-point sampling (score-weighted)
   to choose 20 diverse high-scoring finalists.
6. **Evaluation** — Mann-Whitney U tests (evolved vs random, shuffled,
   and seed controls) with Cohen's d effect sizes.

## Evaluation Criteria

Mann-Whitney U test showing evolved sequences score significantly higher
than both random and shuffled controls (p < 0.05).

## Required Data Assets (optional — capsule is self-contained)

| Mount path | Description |
|---|---|
| `/data/k562_peaks.fasta` | Real K562 ATAC-seq peak sequences (200 bp) |
| `/data/model_weights/deepstarr_human.pt` | Human DeepSTARR TorchScript checkpoint |

If not attached, the capsule generates biologically realistic seed
sequences and uses the PWM proxy scorer.

## Outputs

| File | Description |
|---|---|
| `top20.fasta` | 20 optimised sequences with score, GC, motif, and mfg annotations |
| `boxplot.png` | 4-panel figure: distributions, GA trajectory, GC scatter, diversity heatmap |
| `stats.json` | Mann-Whitney p-values, effect sizes, run parameters |

## Environment

- Python 3.10 + numpy, scipy, matplotlib, biopython
- CPU sufficient (PWM scorer is vectorised numpy)

## Code Structure

| File | Role |
|---|---|
| `run` | Bash entrypoint |
| `run.py` | Orchestrator — config, pipeline stages, output writing |
| `score.py` | PWM-based scorer: vectorised motif scanning, cooperativity, GC, complexity |
| `generate.py` | Seed generation, GA engine, controls, filters, diversity selection |
| `report.py` | Multi-panel figure, annotated FASTA, statistics |
