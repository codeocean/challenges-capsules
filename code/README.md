# Challenge 10: NeuroBase Foundation Model Evaluation


## Results Summary
| Model | Mean Dice | vs Random |
|-------|----------|-----------|
| **Classical Features** | 0.3671 | 2.59× |
| Pretrained Proxy | 0.3228 | 2.28× |
| Random | 0.1416 | baseline |

> See [RESULTS.md](RESULTS.md) for full evaluation, per-region analysis, and visualizations.

## Overview

Benchmarks 3-D neuroanatomical encoders on **Allen CCFv3 brain region parcellation**,
comparing a self-supervised pretrained proxy against classical features and a
random-weights baseline. Designed as a ready-to-go harness — when real NeuroBase
weights are provided they plug in automatically.

## What the Pipeline Does

1. **Downloads real Allen CCFv3 data** at runtime
   - Annotation volume (25 µm, ~4 MB compressed)
   - Average template intensity volume (25 µm, ~33 MB compressed)
   - Structure ontology JSON from the Allen Brain Atlas API (1,327 structures)
2. **Builds anatomically-correct region mapping** by traversing the Allen
   structure ontology tree and collapsing 581 annotation IDs to 12 major
   brain regions (Isocortex, Hippocampal formation, Cerebellum, etc.);
   89 IDs (fibre tracts, ventricles) remain unmapped as background
3. **Extracts 345 3-D patches** (32³, stride 24) with a stratified 80/20
   train/test split (276 train / 69 test) ensuring every region with ≥2
   patches is represented in the test set
4. **Encodes patches** with three methods:

   | Encoder | Features | Dim |
   |---------|----------|-----|
   | Classical Features | 16-bin histogram + gradient magnitude stats + Laplacian stats + spatial centroid | 28 |
   | Pretrained Proxy | Deeper 3-D CNN self-supervised via rotation prediction (55% accuracy, 4 classes) | 64 |
   | Random Baseline | Shallow 3-D CNN with untrained random weights | 64 |

5. **Trains LogisticRegression** classifiers on each embedding set
6. **Evaluates** per-region Dice scores and macro F1
7. **Generates** visualisations, reports, and reusable embedding artifacts

## Verified Results

| Encoder | Mean Dice | Macro F1 | vs Random |
|---------|-----------|----------|-----------|
| **Classical Features** | **0.3671** | **0.4005** | **2.59×** |
| Pretrained Proxy | 0.3228 | 0.3522 | 2.28× |
| Random Baseline | 0.1416 | 0.1545 | 1.00× |

Strongest regions: Isocortex (0.79), Cerebellum (0.67), Olfactory areas (0.63),
Hippocampal formation (0.59), Medulla/Midbrain (0.60), Striatum (0.53).

## Output Artifacts (17 files)

| File | Description |
|------|-------------|
| `summary.json` | Status, all metrics, resource profiling, conclusion |
| `dice_scores.csv` | Per-region Dice for all 3 encoders |
| `opportunity_analysis.json` | Per-region best encoder + assessment |
| `evaluation_report.md` | Full narrative evaluation report |
| `scope.md` | Problem scope declaration |
| `failures.md` | Known limitations and blockers |
| `overlay_coronal.png` | Brain slice annotation overlay — coronal |
| `overlay_sagittal.png` | Brain slice annotation overlay — sagittal |
| `overlay_horizontal.png` | Brain slice annotation overlay — horizontal |
| `dice_barplot.png` | Per-region Dice comparison bar chart (3 encoders) |
| `confusion_matrix.png` | Confusion matrix for the best encoder |
| `embeddings/*.npy` | Saved embeddings, labels, and split indices for reuse |

## Using Real NeuroBase Weights

When organiser-provided NeuroBase weights become available:

1. Create a data asset containing the checkpoint (`.pt` or `.pth`)
2. Mount it at `/data/neurobase_weights/`
3. Re-run — the capsule auto-detects real weights and skips the proxy

## Environment

- **Base image**: PyTorch 2.4.0, CUDA 12.4, Python 3.12
- **Packages**: numpy 2.4, pandas 3.0, scikit-learn 1.8, matplotlib 3.10,
  pynrrd 1.1, requests 2.33, torch 2.11
- **Compute**: X-Small flex tier (CPU sufficient at this scale)
- **Runtime**: ~960 seconds including data download; ~120 s with cached data
- **Peak memory**: ~5.1 GB

## Reproducibility

- Seed: 42 (numpy + torch), deterministic throughout
- Stratified train/test split preserves region representation
- All intermediate data cached to `/scratch/allen/` across runs
- Two consecutive bare runs produce **identical** results (exit 0, same Dice/F1)

---

## Changelog

### v2 — Complete Benchmark Overhaul (current)

Eight fixes addressing all issues from the verification report:

1. **Ontology-based region mapping** — Downloads Allen structure ontology
   (1,327 structures) and walks each annotation ID up the parent tree to
   find which of 12 major brain regions it belongs to. Previously used
   meaningless round-robin assignment (`aid % 12`).

2. **Real Allen CCFv3 average template** — Downloads the actual 25 µm
   average template volume (33 MB) as the intensity signal. Previously
   fabricated intensity from annotation IDs, creating a circular dependency
   (classifier could read labels through the "intensity" values).

3. **Stratified train/test split with denser patches** — Stride reduced
   from 32→24 (148→345 patches); uses `StratifiedShuffleSplit` so every
   region with ≥2 patches gets test coverage. Previously 10/12 regions had
   zero test patches.

4. **Classical feature baseline (3rd encoder)** — Hand-crafted 28-dim
   features: 16-bin intensity histogram, gradient magnitude (mean/std/p95),
   Laplacian (mean/std), basic stats (mean/std/Q1/Q3), and normalised
   spatial centroid. Provides a non-neural reference the challenge requires.

5. **Self-supervised pretrained proxy** — The deeper CNN is now actually
   pretrained via 3-D rotation prediction (0°/90°/180°/270° around one
   axis, 40 epochs). Achieves 55% accuracy (vs 25% chance), proving it
   learns real spatial features. Previously both "pretrained" and "random"
   were untrained random CNNs.

6. **Resource profiling** — Timing for each pipeline stage and peak RSS
   memory are captured and reported in `summary.json`.

7. **Full deliverable artifacts** — Added `scope.md`, `failures.md`,
   `evaluation_report.md`, `opportunity_analysis.json`, and
   `embeddings/*.npy`. Meets the challenge's required demo packet.

8. **Improved visualisations** — Added per-region Dice comparison bar
   chart, confusion matrix heatmap for the best encoder, and masked
   annotation overlays (background correctly transparent).

### v1 — Initial Working Version

- Downloaded Allen CCFv3 annotation at runtime
- Round-robin region mapping (not anatomically correct)
- Synthetic intensity volume from annotation IDs
- Two random CNNs compared (no actual pretraining)
- 148 patches, 29 test, 10/12 regions empty in test set
- Mean Dice: 0.04 pretrained / 0.05 random (both near zero)
