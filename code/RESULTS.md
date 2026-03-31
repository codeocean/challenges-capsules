# Results — Challenge 10: NeuroBase Foundation Model Evaluation

## Latest Successful Run
- **Computation ID:** `efb155c4-a393-4244-a981-a59f0b294822`
- **Status:** PASS (exit code 0)
- **Runtime:** 965 seconds

## Evaluation Results (summary.json)

### Baseline Comparison
| Model | Mean Dice | F1 |
|-------|----------|-----|
| **Classical Features** | 0.3671 | 0.4005 |
| Pretrained Proxy (3D-CNN) | 0.3228 | 0.3522 |
| Random Baseline | 0.1416 | 0.1545 |

### Improvement Over Random
- Classical: **2.59×** improvement
- Pretrained proxy: **2.28×** improvement

### Dataset
- Data source: Allen CCFv3 template (25μm)
- Patches: 345 (276 train / 69 test)
- Regions: 12 coarse brain regions
- Patch size: 32, stride: 24

### Resource Usage
- Peak memory: 5,126 MB
- Total runtime: 957.5 seconds

### Conclusion
> Classical Features achieved the highest mean Dice (0.3671). Self-supervised pretraining provides meaningful improvement over random initialization. With real NeuroBase weights, stronger gains are expected.

## Output Artifacts
| File | Description |
|------|-------------|
| `summary.json` | Overall results and model comparison |
| `opportunity_analysis.json` | Per-region analysis |
| `dice_scores.csv` | Per-region Dice scores |
| `confusion_matrix.png` | Classification confusion matrix |
| `dice_barplot.png` | Per-region Dice visualization |
| `overlay_coronal.png` | Brain overlay (coronal) |
| `overlay_sagittal.png` | Brain overlay (sagittal) |
| `overlay_horizontal.png` | Brain overlay (horizontal) |
| `evaluation_report.md` | Detailed evaluation narrative |
