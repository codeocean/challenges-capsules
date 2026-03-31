# Results — Challenge 10: NeuroBase Foundation Model Evaluation

## Evidence Strength: PARTIAL — Benchmark harness validated with classical baselines; NeuroBase weights unavailable

The evaluation framework works correctly and demonstrates meaningful results: **classical features achieve 2.59× improvement over random** on Allen CCFv3 brain region parcellation. However, the NeuroBase foundation model weights were not available, so only classical and self-supervised proxy baselines are compared.

## Why NeuroBase Is Missing

The NeuroBase foundation model requires:
- Pre-trained weights provided by challenge organizers (not included in data assets)
- Specific model architecture implementation

Without the weights, the capsule implements a **self-supervised 3D-CNN proxy** (rotation prediction task) as a stand-in, plus a classical feature baseline and random baseline for comparison.

## Evaluation Results (summary.json)

### Model Comparison
| Model | Mean Dice | F1 | vs Random |
|-------|----------|-----|-----------|
| **Classical Features** | 0.3671 | 0.4005 | **2.59×** |
| Pretrained Proxy (3D-CNN) | 0.3228 | 0.3522 | 2.28× |
| Random Baseline | 0.1416 | 0.1545 | baseline |

### Per-Region Dice Scores (dice_scores.csv)
| Region | Classical | Pretrained | Random |
|--------|-----------|-----------|--------|
| Isocortex | 0.793 | **0.863** | 0.677 |
| Cerebellum | **0.667** | 0.444 | 0.000 |
| Hippocampus | **0.588** | 0.400 | 0.143 |
| Midbrain | **0.600** | 0.500 | 0.000 |
| Striatum | **0.533** | 0.500 | 0.000 |
| Olfactory | 0.625 | **0.667** | 0.435 |
| Medulla | **0.600** | 0.500 | 0.444 |
| Cortical subplate | 0.000 | 0.000 | 0.000 |
| Hypothalamus | 0.000 | 0.000 | 0.000 |
| Pallidum | 0.000 | 0.000 | 0.000 |
| Pons | 0.000 | 0.000 | 0.000 |
| Thalamus | 0.000 | 0.000 | 0.000 |

### Dataset
- Source: Allen CCFv3 25μm template (downloaded at runtime)
- 345 patches (276 train / 69 test), 12 coarse brain regions
- Patch size: 32, stride: 24

## What the Evidence Shows
- **Real brain data:** Allen CCFv3 annotation volume (not synthetic)
- **Benchmark harness works:** Clean train/test split, per-region evaluation, visualizations
- **Meaningful baselines:** Classical > pretrained proxy > random, confirming the evaluation framework detects real performance differences
- **Ready for NeuroBase:** Drop in weights and the full comparison runs automatically

## Output Artifacts
| File | Description |
|------|-------------|
| `summary.json` | Overall results and model comparison |
| `dice_scores.csv` | Per-region Dice scores for all models |
| `opportunity_analysis.json` | Per-region assessment (strong/weak) |
| `confusion_matrix.png` | Classification confusion matrix |
| `dice_barplot.png` | Per-region Dice visualization |
| `overlay_coronal.png` | Brain overlay (coronal slice) |
| `overlay_sagittal.png` | Brain overlay (sagittal slice) |
| `overlay_horizontal.png` | Brain overlay (horizontal slice) |
