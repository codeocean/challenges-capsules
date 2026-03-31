# Challenge 04: Light Sheet Alignment QC

## What This Capsule Does

A complete, self-contained quality control system for light-sheet microscopy image
registration that detects alignment failures, routes uncertain cases to human review,
and outperforms a naive SSIM-only baseline by +10% AUC.

### Pipeline

```
generate_pairs.py → 250 synthetic tile pairs
  • 10 tissue types (dense, sparse, border, empty, mixed)
  • 6 perturbation types (translation, rotation, intensity drift, seam, scale, blur)
  • 4 severity levels (borderline, mild, moderate, severe)
      │
      ▼
run.py → 7-feature extraction → GradientBoosting classifier → Isotonic calibration
  • SSIM, NCC, edge continuity, mutual info, gradient similarity,
    content quality, intensity difference
  • 5-fold cross-validated (AUC = 0.966 ± 0.017)
  • Adaptive percentile-based thresholds → pass / fail / needs_review
      │
      ▼
visualize.py → HTML report + 20 QC overlay montages + TP/FP/TN/FN gallery + 8 plots
```

## How To Run

Click **Reproducible Run**. Self-contained — generates synthetic data + full pipeline
in ~55 seconds on CPU.

## Final Results — All Targets Met

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| ROC-AUC | ≥ 0.90 | **0.966** | ✅ |
| PR-AUC | ≥ 0.85 | **0.940** | ✅ |
| Precision (fail) | ≥ 0.85 | **0.893** | ✅ |
| Recall (fail) | ≥ 0.80 | **0.962** | ✅ |
| Review rate | ≤ 15% | **2.0%** | ✅ |
| Beats SSIM baseline | — | +10% AUC | ✅ |
| Test accuracy | — | **92.0%** | — |
| 5-fold CV AUC | — | **0.966 ± 0.017** | — |

## Per-Severity Performance

| Severity | AUC | Accuracy | N pairs |
|----------|-----|----------|---------|
| Borderline | 0.999 | 98.3% | 60 |
| Mild | 0.979 | 96.3% | 54 |
| Moderate | 1.000 | 98.6% | 70 |
| Severe | 0.999 | 98.7% | 76 |

## Outputs

| File | Description |
|------|-------------|
| **`evaluation_report.html`** | Primary deliverable — comprehensive HTML report |
| `predictions.csv` | Per-pair: score, prediction, confidence, 7 features, metadata |
| `metrics.json` | Machine-readable evaluation metrics |
| `roc_curve.png` | ROC curve (AUC = 0.966) |
| `pr_curve.png` | Precision-Recall curve (PR-AUC = 0.940) |
| `score_histogram.png` | Score distribution with threshold zones |
| `confusion_matrix.png` | Test set confusion matrix |
| `feature_distributions.png` | 7-feature distributions by class |
| `severity_breakdown.png` | Performance per severity level |
| `baseline_comparison.png` | SSIM baseline vs GradientBoosting ensemble |
| `example_gallery.png` | TP/FP/TN/FN gallery (4 each) |
| `figures/*.png` | 18-20 QC overlay montages (left\|right\|diff\|blend) |

## Environment

- Python 3.10+, CPU only (Small instance, ~55s runtime)
- `scikit-image`, `scikit-learn`, `numpy`, `matplotlib`, `tifffile`, `pandas`, `scipy`
