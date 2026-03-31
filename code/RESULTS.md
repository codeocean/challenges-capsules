# Results — Challenge 04: Light Sheet Alignment QC

## Latest Successful Run
- **Computation ID:** `0760b737-13b9-4f54-b7d1-25462153f08f`
- **Status:** Succeeded (exit code 0)
- **Runtime:** 505 seconds

## Evaluation Results (metrics.json)

### Classification Performance
| Metric | Value |
|--------|-------|
| **AUC** | 0.9773 |
| **PR-AUC** | 0.9694 |
| **Test Accuracy** | 93.75% |
| **CV AUC (mean ± std)** | 0.9616 ± 0.0166 |

### Per-Class Metrics
| Class | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| Aligned | 0.9524 | 0.9091 | 0.9302 |
| Misaligned | 0.9259 | 0.9615 | 0.9434 |

### 3-Tier Decision Output
| Decision | Count |
|----------|-------|
| Pass (aligned) | 105 |
| Fail (misaligned) | 127 |
| Needs Review | 8 (3.3%) |

### Dataset
- Total pairs: 240 (192 train / 48 test)
- Classifier: GradientBoosting (n=150, depth=4, lr=0.1)
- Features: SSIM, NCC, edge continuity, mutual info, gradient similarity, phase correlation, content quality, intensity difference

### Feature Importance
| Feature | Importance |
|---------|-----------|
| NCC | 0.669 |
| Gradient similarity | 0.085 |
| Edge continuity | 0.070 |
| Content quality | 0.045 |

## Output Artifacts
| File | Description |
|------|-------------|
| `predictions.csv` (55 KB) | Per-pair predictions with probabilities |
| `metrics.json` | Full evaluation metrics |
| `roc_curve.png` | ROC curve visualization |
| `pr_curve.png` | Precision-recall curve |
| `score_histogram.png` | Score distribution |
| `confusion_matrix.png` | Confusion matrix |
| `example_gallery.png` | Example aligned/misaligned pairs |
| `severity_metrics.json` | Per-severity breakdown |
| `evaluation_report.html` | Interactive HTML report |
