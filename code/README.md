# Challenge 10: NeuroBase Foundation Model Evaluation

## Overview

Benchmarks 3-D neuroanatomical encoders on **Allen CCFv3 brain region parcellation**,
comparing a self-supervised pretrained proxy against classical features and a
random-weights baseline. Designed as a ready-to-go harness — when real NeuroBase
weights are provided they plug in automatically.

## What the Pipeline Does

1. **Downloads real Allen CCFv3 data** at runtime
   - Annotation volume (25 µm, ~4 MB compressed)
   - Average template intensity volume (25 µm, ~50 MB compressed)
   - Structure ontology JSON from the Allen Brain Atlas API
2. **Builds anatomically-correct region mapping** by traversing the Allen
   structure ontology tree and collapsing ~670 annotation IDs to 12 major
   brain regions (Isocortex, Hippocampal formation, Cerebellum, etc.)
3. **Extracts 3-D patches** (32³, stride 24) with a stratified 80/20
   train/test split ensuring every region is represented in the test set
4. **Encodes patches** with three methods:
   | Encoder | Description |
   |---------|-------------|
   | Classical Features | 16-bin intensity histogram + gradient magnitude + Laplacian + spatial centroid |
   | Pretrained Proxy | Deeper 3-D CNN pretrained via rotation prediction (self-supervised) |
   | Random Baseline | Shallow 3-D CNN with random weights (lower bound) |
5. **Trains LogisticRegression** classifiers on each embedding set
6. **Evaluates** per-region Dice scores and macro F1
7. **Generates** visualisations, reports, and reusable embedding artifacts

## Output Artifacts

| File | Description |
|------|-------------|
| `summary.json` | Status, all metrics, resource profiling, conclusion |
| `dice_scores.csv` | Per-region Dice for all 3 encoders |
| `opportunity_analysis.json` | Per-region best encoder + assessment |
| `evaluation_report.md` | Full narrative report |
| `scope.md` | Problem scope declaration |
| `failures.md` | Known limitations |
| `overlay_coronal.png` | Brain slice overlay — coronal |
| `overlay_sagittal.png` | Brain slice overlay — sagittal |
| `overlay_horizontal.png` | Brain slice overlay — horizontal |
| `dice_barplot.png` | Per-region Dice comparison bar chart |
| `confusion_matrix.png` | Confusion matrix for the best encoder |
| `embeddings/*.npy` | Saved embeddings, labels, and split indices |

## Using Real NeuroBase Weights

When organiser-provided NeuroBase weights become available:

1. Create a data asset containing the checkpoint (`.pt` or `.pth`)
2. Mount it at `/data/neurobase_weights/`
3. Re-run — the capsule auto-detects real weights and skips the proxy

## Environment

- **Base image**: PyTorch 2.4.0, CUDA 12.4, Python 3.12
- **Packages**: numpy, pandas, scikit-learn, matplotlib, pynrrd, requests, torch
- **Compute**: X-Small flex tier (CPU sufficient at this scale; ~2 min runtime)

## Reproducibility

- Seed: 42 (numpy + torch)
- Deterministic patch extraction, stratified split, and classifier training
- All intermediate data cached to `/scratch/allen/` across runs
- Two consecutive bare runs produce identical results (exit 0)
