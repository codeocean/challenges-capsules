# Challenge 10: NeuroBase Foundation Model Evaluation

## What This Capsule Does
Takes one pre-registered mouse brain volume, runs it through the NeuroBase encoder
to get patch embeddings, trains a logistic regression to predict 12 coarse brain
regions, and outputs Dice score table + overlay visualizations — pretrained vs random.

## Evaluation
Per-region Dice scores showing pretrained encoder meaningfully outperforms random baseline.

## Required Data Assets
| File | Description |
|------|-------------|
| `brain_volume.nrrd` | 25μm STPT mouse brain volume |
| `annotation.nrrd` | CCFv3 annotation volume at matching resolution |
| `neurobase_weights/` | NeuroBase encoder checkpoint |
| `region_mapping.json` | CCFv3 label IDs → 12 coarse region names |

## Expected Outputs
| File | Description |
|------|-------------|
| `dice_scores.csv` | `region`, `dice_pretrained`, `dice_random` |
| `overlay_coronal.png`, `overlay_sagittal.png`, `overlay_horizontal.png` | Slice overlays |
| `summary.json` | Mean Dice, improvement factor |

## Environment
- GPU required (encoder inference), `torch`, `monai`, `pynrrd`, `scikit-learn`, `matplotlib`, `numpy`, `pandas`
