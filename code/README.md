# Challenge 15: Allen Single Cell Model Pantry


## Results Summary
| Model | Macro F1 | Status |
|-------|----------|--------|
| PCA Baseline | 0.072 | ✅ Working |
| scVI | — | ❌ Import error |
| Geneformer | — | ❌ Weights path error |

> See [RESULTS.md](RESULTS.md) for full leaderboard and error details.

## What This Capsule Does
Head-to-head benchmark of scVI vs. Geneformer on Allen Human MTG cell-type
annotation. Loads frozen pre-split h5ad, runs both through shared KNN classifier,
outputs leaderboard CSV plus confusion matrices.

## Evaluation
Cell-type classification macro F1 on a donor-held-out test split.

## Required Data Assets
| File | Description |
|------|-------------|
| `mtg_dataset.h5ad` | Frozen pre-split Allen Human MTG dataset with `split` column |
| `gene_mapping.csv` | HGNC symbol → Ensembl ID mapping |
| `geneformer_weights/` | Pre-downloaded Geneformer HuggingFace checkpoint |

## Expected Outputs
| File | Description |
|------|-------------|
| `leaderboard.csv` | model, accuracy, macro_f1, runtime_seconds |
| `confusion_scvi.png` | scVI confusion matrix |
| `confusion_geneformer.png` | Geneformer confusion matrix |
| `summary.json` | Winner, test cells, per-model F1 |

## Environment
- GPU required. `scanpy`, `anndata`, `scvi-tools`, `torch`, `transformers`, `scikit-learn`, `matplotlib`, `pandas`
