# Results — Challenge 15: Allen Single-Cell Model Pantry

## Latest Successful Run
- **Computation ID:** `a8d55b72-d78b-4ee9-b739-e92c952cf622`
- **Status:** Succeeded (exit code 0)
- **Runtime:** 16 seconds

## Evaluation Results (leaderboard.csv)

### Model Leaderboard
| Model | Accuracy | Macro F1 | Runtime | Notes |
|-------|----------|----------|---------|-------|
| PCA Baseline | 0.078 | 0.072 | 2.1s | ✅ Working |
| scVI | 0.0 | 0.0 | — | ❌ torchvision circular import |
| Geneformer | 0.0 | 0.0 | — | ❌ Model weights path error |

### Notes
- PCA baseline successfully runs and produces classifications
- scVI fails due to torchvision circular import in this environment
- Geneformer fails due to model weights path issue
- Dataset: 80 MB synthetic MTG-like H5AD (10K cells, 2000 genes, 10 cell types)

## Output Artifacts
| File | Description |
|------|-------------|
| `leaderboard.csv` | Model comparison table |
| `confusion_pca.png` (169 KB) | PCA baseline confusion matrix |
| `mtg_dataset.h5ad` (80 MB) | Synthetic MTG dataset |
| `summary.json` | Run summary |
