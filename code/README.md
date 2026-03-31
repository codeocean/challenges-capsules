# 🧬 Challenge 03: Enhancer Designer

## What This Capsule Does


## Results Summary

| Metric | Value |
|--------|-------|
| **Evolved vs Random p-value** | 9.73e-13 |
| **Evolved vs Shuffled p-value** | 9.73e-13 |
| **Cohen's d (vs Random)** | 6.20 |
| **Mean Evolved Score** | 1.000 |
| **Mean Random Score** | 0.196 |
| **Diversity Pass** | ✅ |
| **Oracle** | Trained CNN (K562 features) |

> See [RESULTS.md](RESULTS.md) for full statistical tests, diversity metrics, and oracle details.

Designs synthetic K562 enhancer DNA sequences via a genetic algorithm with
biologically-informed PWM scoring, manufacturability filtering, and
diversity-aware selection.  Fully configurable via the **App Panel**.

### Pipeline

| Stage | Description |
|-------|-------------|
| **1. Seeds** | 100 K562-like sequences with embedded TF motifs (GATA1, TAL1, SP1, NF-E2, KLF1, MYC) in GC-matched backgrounds.  Uses real FASTA if attached. |
| **2. Scoring** | PWM log-quality⁴ with Gaussian inter-motif cooperativity, GC optimality, trinucleotide complexity, and motif-explosion penalty. |
| **3. GA** | Tournament selection (k=3), two-point crossover, point mutation, 5 % elitism.  Configurable generations, population, rates. |
| **4. Filters** | GC 30–70 %, homopolymer ≤6, dinucleotide repeat ≤4, no EcoRI/BamHI/HindIII/NotI sites, no single motif >30 % coverage. |
| **5. Diversity** | 4-mer farthest-point sampling; near-duplicate fraction validated (<50 % threshold, edit distance <10 %). |
| **6. Evaluation** | Mann-Whitney U tests (evolved vs random, dinucleotide-shuffled, and seed controls) with Cohen's d effect sizes. |

### Controls

- **Random**: uniform-base sequences (matched length)
- **Dinucleotide-shuffled**: Euler-path shuffle preserving exact dinucleotide
  frequencies (Altschul & Erickson 1985)
- **Seeds**: original K562 motif-embedded sequences (positive reference)

## App Panel Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Generations | 50 | 10–500 | Number of GA generations |
| Population Size | 200 | 50–1000 | GA population per generation |
| Mutation Rate | 0.04 | 0.001–0.2 | Per-base mutation probability |
| Crossover Probability | 0.6 | 0–1 | Probability of two-point crossover |
| Top-K Finalists | 20 | 5–100 | Number of diverse finalists to return |
| Random Seed | 42 | 0–999999 | For reproducibility |

## Outputs

| File | Description |
|------|-------------|
| `enhancer_report.png` | 6-panel figure: score distributions, GA trajectory, motif heatmap, GC scatter, diversity matrix, motif enrichment |
| `stats.json` | Structured evaluation: Mann-Whitney tests, effect sizes, diversity metrics, filter stats, trajectory |
| `top20.fasta` | Annotated FASTA: score, GC, motif hits per TF, filter status |
| `run_manifest.yaml` | Complete reproducibility record: all parameters, scoring method, filter config, results |

## Evaluation Criteria

| Criterion | Target | How Verified |
|-----------|--------|--------------|
| ≥20 filtered candidates | 20 | `top20.fasta` count |
| Evolved > controls (p < 0.05) | Mann-Whitney | `stats.json` evaluation block |
| Diverse panel | <50 % near-duplicates | `stats.json` diversity block |
| Motif annotations | Per-sequence | FASTA headers |
| Reproducibility | Same seed → same output | `run_manifest.yaml` |

## Data Assets (optional — capsule is self-contained)

| Mount path | Description |
|---|---|
| `/data/k562_peaks.fasta` | Real K562 ATAC-seq peak sequences (200 bp) |
| `/data/model_weights/deepstarr_human.pt` | Human DeepSTARR TorchScript checkpoint |

## Code Structure

| File | Lines | Role |
|------|-------|------|
| `run` | 3 | Bash entrypoint, passes CLI args |
| `run.py` | ~100 | Orchestrator with argparse (App Panel compatible) |
| `score.py` | ~160 | PWM scanning, cooperativity, scoring engine |
| `generate.py` | ~220 | Seeds, GA, Euler shuffle, filters, diversity |
| `report.py` | ~250 | 6-panel figure, stats, FASTA, manifest |

## Environment

- Python 3.10, numpy, scipy, matplotlib, biopython
- CPU sufficient (vectorised numpy PWM scanning)
