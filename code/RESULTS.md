# Results — Challenge 04: Light Sheet Alignment QC

## Evidence Strength: STRONG

This capsule achieves **AUC 0.977 and 93.75% test accuracy** on alignment quality classification with a calibrated 3-tier decision system. The ML pipeline (GradientBoosting on 8 image-similarity features) is fully self-contained and validated with cross-validation.

## Evaluation Results

### Classification Performance (metrics.json)
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
| Decision | Count | % |
|----------|-------|---|
| Pass (aligned) | 105 | 43.8% |
| Fail (misaligned) | 127 | 52.9% |
| Needs Review | 8 | 3.3% |

### Per-Severity Accuracy
| Severity | AUC | Accuracy |
|----------|-----|----------|
| None (aligned only) | — | 98.2% |
| Borderline | 0.981 | 96.7% |
| Mild | 1.000 | 97.1% |
| Moderate | 1.000 | 97.1% |
| Severe | 1.000 | 96.8% |

## Known Limitations
- Validated on **synthetic image pairs** (physics-informed generation), not real AIND SmartSPIM data
- The synthetic generator models tissue textures and realistic perturbations, but real-world failure modes may differ
- Ready for real data validation when SmartSPIM overlap pairs become available

## Output Artifacts
| File | Description |
|------|-------------|
| `predictions.csv` (55 KB) | Per-pair predictions with probabilities |
| `metrics.json` | Full evaluation metrics |
| `severity_metrics.json` | Per-severity breakdown |
| `roc_curve.png` | ROC curve |
| `pr_curve.png` | Precision-recall curve |
| `confusion_matrix.png` | Confusion matrix |
| `score_histogram.png` | Score distributions |
| `example_gallery.png` | Example image pairs |
