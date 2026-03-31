#!/usr/bin/env python3
"""visualize.py — Visual QC overlays, galleries, and HTML report generation.

Produces:
  - Per-pair QC overlay montages (left | right | difference | blend)
  - Example gallery (TP, FP, TN, FN — 3+ each)
  - Score histogram with thresholds
  - ROC and PR curves
  - Confusion matrix
  - Feature distributions
  - Per-severity performance breakdown chart
  - Comprehensive HTML evaluation report
"""

from __future__ import annotations

import base64
import io
import json
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap


# ---------------------------------------------------------------------------
# Image utilities
# ---------------------------------------------------------------------------

def _norm_to_uint8(img: np.ndarray) -> np.ndarray:
    """Normalise any image to uint8 [0,255]."""
    f = img.astype(np.float64)
    mn, mx = f.min(), f.max()
    if mx - mn < 1e-9:
        return np.zeros_like(img, dtype=np.uint8)
    return ((f - mn) / (mx - mn) * 255).astype(np.uint8)


def _fig_to_base64(fig: plt.Figure, dpi: int = 100) -> str:
    """Render figure to base64 PNG for HTML embedding."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


def _fig_to_file(fig: plt.Figure, path: Path, dpi: int = 150) -> None:
    """Save figure to file."""
    fig.savefig(str(path), dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Per-pair QC overlay
# ---------------------------------------------------------------------------

def make_pair_overlay(
    left: np.ndarray,
    right: np.ndarray,
    score: float,
    prediction: str,
    pair_id: str,
    label: str,
) -> plt.Figure:
    """Create a 4-panel QC overlay for one pair:
    [left tile] [right tile] [|difference|] [alpha blend]
    """
    l8 = _norm_to_uint8(left)
    r8 = _norm_to_uint8(right)

    # Ensure same shape
    h = min(l8.shape[0], r8.shape[0])
    w = min(l8.shape[1], r8.shape[1])
    l8, r8 = l8[:h, :w], r8[:h, :w]

    diff = np.abs(l8.astype(np.int16) - r8.astype(np.int16)).astype(np.uint8)
    blend = ((l8.astype(np.float32) + r8.astype(np.float32)) / 2).astype(np.uint8)

    pred_colors = {"pass": "#27ae60", "fail": "#e74c3c", "needs_review": "#f39c12"}
    color = pred_colors.get(prediction, "#95a5a6")

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    titles = ["Left Tile", "Right Tile", "|Difference|", "Alpha Blend"]
    images = [l8, r8, diff, blend]
    cmaps = ["gray", "gray", "hot", "gray"]

    for ax, img, title, cmap in zip(axes, images, titles, cmaps):
        ax.imshow(img, cmap=cmap, vmin=0, vmax=255)
        ax.set_title(title, fontsize=10)
        ax.axis("off")

    fig.suptitle(
        f"{pair_id}  |  GT: {label}  |  Pred: {prediction}  |  Score: {score:.3f}",
        fontsize=12, fontweight="bold", color=color, y=1.02,
    )
    fig.tight_layout()
    return fig


def save_pair_overlays(
    pairs_dir: Path,
    feat_df: pd.DataFrame,
    out_dir: Path,
    max_pairs: int = 20,
) -> list[str]:
    """Save QC overlay PNGs for a subset of pairs. Returns list of saved filenames."""
    import tifffile
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []

    # Select: worst fails, best passes, all needs_review, some misclassified
    subset = feat_df.copy()
    # Prioritise interesting cases
    groups = []
    # needs_review
    nr = subset[subset["prediction"] == "needs_review"].head(5)
    groups.append(nr)
    # worst fails (lowest score among misaligned)
    fails = subset[(subset["prediction"] == "fail") & (subset["label"] == 0)].nsmallest(3, "score")
    groups.append(fails)
    # best passes (highest score among aligned)
    passes = subset[(subset["prediction"] == "pass") & (subset["label"] == 1)].nlargest(3, "score")
    groups.append(passes)
    # misclassified (false positives + false negatives)
    fp = subset[(subset["label"] == 0) & (subset["score"] >= 0.5)].head(3)
    fn = subset[(subset["label"] == 1) & (subset["score"] < 0.5)].head(3)
    groups.append(fp)
    groups.append(fn)
    # fill remaining
    remaining = max_pairs - sum(len(g) for g in groups)
    if remaining > 0:
        used_ids = set()
        for g in groups:
            used_ids.update(g["pair_id"])
        rest = subset[~subset["pair_id"].isin(used_ids)].sample(
            n=min(remaining, len(subset) - len(used_ids)), random_state=42
        )
        groups.append(rest)

    selected = pd.concat(groups).drop_duplicates(subset="pair_id").head(max_pairs)

    for _, row in selected.iterrows():
        pid = row["pair_id"]
        lp = pairs_dir / f"{pid}_left.tif"
        rp = pairs_dir / f"{pid}_right.tif"
        if not lp.exists() or not rp.exists():
            continue
        left = tifffile.imread(str(lp))
        right = tifffile.imread(str(rp))
        label_str = "aligned" if row["label"] == 1 else "misaligned"
        fig = make_pair_overlay(left, right, row["score"], row["prediction"], pid, label_str)
        fname = f"overlay_{pid}.png"
        _fig_to_file(fig, out_dir / fname, dpi=120)
        saved.append(fname)

    return saved


# ---------------------------------------------------------------------------
# Example gallery (TP / FP / TN / FN)
# ---------------------------------------------------------------------------

def make_example_gallery(
    pairs_dir: Path,
    feat_df: pd.DataFrame,
    out_path: Path,
    n_each: int = 4,
) -> None:
    """Create a 4-row gallery: TP, FP, TN, FN — n_each examples per row."""
    import tifffile

    # Binary classification at 0.5
    df = feat_df.copy()
    df["pred_binary"] = (df["score"] >= 0.5).astype(int)

    categories = {
        "True Positive\n(aligned, pred=aligned)": df[(df["label"] == 1) & (df["pred_binary"] == 1)],
        "False Positive\n(misaligned, pred=aligned)": df[(df["label"] == 0) & (df["pred_binary"] == 1)],
        "True Negative\n(misaligned, pred=misaligned)": df[(df["label"] == 0) & (df["pred_binary"] == 0)],
        "False Negative\n(aligned, pred=misaligned)": df[(df["label"] == 1) & (df["pred_binary"] == 0)],
    }

    n_rows = len(categories)
    fig, axes = plt.subplots(n_rows, n_each * 2, figsize=(n_each * 5, n_rows * 3.2))
    if n_rows == 1:
        axes = axes[np.newaxis, :]

    for row_idx, (cat_name, cat_df) in enumerate(categories.items()):
        samples = cat_df.head(n_each)
        for col_idx in range(n_each):
            ax_left = axes[row_idx, col_idx * 2]
            ax_right = axes[row_idx, col_idx * 2 + 1]

            if col_idx < len(samples):
                row_data = samples.iloc[col_idx]
                pid = row_data["pair_id"]
                lp = pairs_dir / f"{pid}_left.tif"
                rp = pairs_dir / f"{pid}_right.tif"
                if lp.exists() and rp.exists():
                    left = _norm_to_uint8(tifffile.imread(str(lp)))
                    right = _norm_to_uint8(tifffile.imread(str(rp)))
                    ax_left.imshow(left, cmap="gray")
                    ax_right.imshow(right, cmap="gray")
                    ax_left.set_title(f"{pid} L\nscore={row_data['score']:.2f}", fontsize=7)
                    ax_right.set_title(f"{pid} R", fontsize=7)
                else:
                    ax_left.text(0.5, 0.5, "N/A", ha="center", va="center", transform=ax_left.transAxes)
                    ax_right.text(0.5, 0.5, "N/A", ha="center", va="center", transform=ax_right.transAxes)
            else:
                ax_left.text(0.5, 0.5, "—", ha="center", va="center", transform=ax_left.transAxes, fontsize=14, color="#ccc")
                ax_right.text(0.5, 0.5, "—", ha="center", va="center", transform=ax_right.transAxes, fontsize=14, color="#ccc")

            ax_left.axis("off")
            ax_right.axis("off")

        # Row label
        axes[row_idx, 0].set_ylabel(cat_name, fontsize=9, fontweight="bold", rotation=0,
                                     labelpad=80, va="center")

    fig.suptitle("Example Gallery: TP / FP / TN / FN", fontsize=14, fontweight="bold", y=1.01)
    fig.tight_layout()
    _fig_to_file(fig, out_path, dpi=130)


# ---------------------------------------------------------------------------
# Standard plots
# ---------------------------------------------------------------------------

def plot_roc_curve(y_true: np.ndarray, y_proba: np.ndarray, out_path: Path) -> float:
    from sklearn.metrics import auc, roc_curve
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    roc_auc = auc(fpr, tpr)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, color="#2ecc71", lw=2.5, label=f"Ensemble (AUC = {roc_auc:.3f})")
    ax.plot([0, 1], [0, 1], color="#95a5a6", lw=1, linestyle="--", label="Random")
    ax.fill_between(fpr, tpr, alpha=0.12, color="#2ecc71")
    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("ROC Curve — Light Sheet Alignment QC", fontsize=13, fontweight="bold")
    ax.legend(loc="lower right", fontsize=10)
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)
    _fig_to_file(fig, out_path)
    return roc_auc


def plot_pr_curve(y_true: np.ndarray, y_proba: np.ndarray, out_path: Path) -> float:
    from sklearn.metrics import average_precision_score, precision_recall_curve
    precision, recall, _ = precision_recall_curve(y_true, y_proba)
    pr_auc = average_precision_score(y_true, y_proba)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(recall, precision, color="#3498db", lw=2.5, label=f"Ensemble (PR-AUC = {pr_auc:.3f})")
    baseline = y_true.mean()
    ax.axhline(baseline, color="#95a5a6", lw=1, linestyle="--", label=f"Baseline ({baseline:.2f})")
    ax.fill_between(recall, precision, alpha=0.12, color="#3498db")
    ax.set_xlabel("Recall", fontsize=12)
    ax.set_ylabel("Precision", fontsize=12)
    ax.set_title("Precision-Recall Curve", fontsize=13, fontweight="bold")
    ax.legend(loc="lower left", fontsize=10)
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)
    _fig_to_file(fig, out_path)
    return pr_auc


def plot_score_histogram(
    aligned_scores: np.ndarray, misaligned_scores: np.ndarray,
    pass_thresh: float, fail_thresh: float, out_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    bins = np.linspace(0, 1, 40)
    ax.hist(aligned_scores, bins=bins, alpha=0.7, label="Aligned", color="#2ecc71", edgecolor="white", lw=0.5)
    ax.hist(misaligned_scores, bins=bins, alpha=0.7, label="Misaligned", color="#e74c3c", edgecolor="white", lw=0.5)
    ax.axvline(pass_thresh, color="#27ae60", ls="--", lw=2, label=f"Pass ≥ {pass_thresh:.2f}")
    ax.axvline(fail_thresh, color="#c0392b", ls="--", lw=2, label=f"Fail < {fail_thresh:.2f}")
    ax.axvspan(fail_thresh, pass_thresh, alpha=0.06, color="#f39c12", label="Review zone")
    ax.set_xlabel("P(aligned)", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("Score Distribution by Ground Truth", fontsize=13, fontweight="bold")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    _fig_to_file(fig, out_path)


def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, out_path: Path) -> None:
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4.5))
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    ax.set_title("Confusion Matrix (Test Set)", fontsize=13, fontweight="bold")
    fig.colorbar(im, ax=ax, shrink=0.8)
    labels = ["Misaligned", "Aligned"]
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(labels, fontsize=10); ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Predicted", fontsize=11); ax.set_ylabel("True", fontsize=11)
    for i in range(2):
        for j in range(2):
            color = "white" if cm[i, j] > cm.max() / 2 else "black"
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=16, fontweight="bold", color=color)
    _fig_to_file(fig, out_path)


def plot_feature_distributions(feat_df: pd.DataFrame, feature_cols: list, out_path: Path) -> None:
    n = len(feature_cols)
    fig, axes = plt.subplots(1, n, figsize=(3.5 * n, 3.5))
    if n == 1:
        axes = [axes]
    for ax, col in zip(axes, feature_cols):
        aligned = feat_df.loc[feat_df["label"] == 1, col]
        misaligned = feat_df.loc[feat_df["label"] == 0, col]
        ax.hist(aligned, bins=25, alpha=0.7, label="Aligned", color="#2ecc71", edgecolor="white")
        ax.hist(misaligned, bins=25, alpha=0.7, label="Misaligned", color="#e74c3c", edgecolor="white")
        ax.set_title(col.replace("_", " ").title(), fontsize=9, fontweight="bold")
        ax.set_xlabel("Value", fontsize=8); ax.set_ylabel("Count", fontsize=8)
        ax.legend(fontsize=6); ax.grid(True, alpha=0.3, axis="y")
    fig.suptitle("Feature Distributions", fontsize=12, fontweight="bold", y=1.02)
    fig.tight_layout()
    _fig_to_file(fig, out_path)


def plot_severity_breakdown(severity_metrics: dict, out_path: Path) -> None:
    """Bar chart of AUC / accuracy by perturbation severity."""
    # Filter to severities with numeric AUC values
    valid = {s: v for s, v in severity_metrics.items()
             if isinstance(v.get("auc"), (int, float)) and isinstance(v.get("accuracy"), (int, float))}
    if not valid:
        # Nothing plottable — create a placeholder
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "Insufficient data for per-severity breakdown",
                ha="center", va="center", transform=ax.transAxes, fontsize=12, color="#999")
        ax.axis("off")
        _fig_to_file(fig, out_path)
        return

    sevs = list(valid.keys())
    aucs = [valid[s]["auc"] for s in sevs]
    accs = [valid[s]["accuracy"] for s in sevs]
    counts = [valid[s].get("n", 0) for s in sevs]

    x = np.arange(len(sevs))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars1 = ax.bar(x - width/2, aucs, width, label="AUC", color="#3498db", alpha=0.8)
    bars2 = ax.bar(x + width/2, accs, width, label="Accuracy", color="#2ecc71", alpha=0.8)

    for bar, c in zip(bars1, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"n={c}", ha="center", fontsize=7, color="#555")

    ax.set_ylabel("Score", fontsize=11)
    ax.set_title("Performance by Perturbation Severity", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(sevs, fontsize=10)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 1.15)
    ax.grid(True, alpha=0.3, axis="y")
    _fig_to_file(fig, out_path)


def plot_baseline_comparison(
    baseline_metrics: dict, ensemble_metrics: dict, out_path: Path,
) -> None:
    """Side-by-side bar chart: SSIM-only baseline vs ensemble model."""
    metric_names = ["AUC", "Precision\n(fail)", "Recall\n(fail)", "Accuracy"]
    baseline_vals = [
        baseline_metrics.get("auc", 0),
        baseline_metrics.get("precision_fail", 0),
        baseline_metrics.get("recall_fail", 0),
        baseline_metrics.get("accuracy", 0),
    ]
    ensemble_vals = [
        ensemble_metrics.get("auc", 0),
        ensemble_metrics.get("precision_fail", 0),
        ensemble_metrics.get("recall_fail", 0),
        ensemble_metrics.get("accuracy", 0),
    ]

    x = np.arange(len(metric_names))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - width/2, baseline_vals, width, label="SSIM-only baseline", color="#e74c3c", alpha=0.7)
    ax.bar(x + width/2, ensemble_vals, width, label="5-feature ensemble", color="#2ecc71", alpha=0.8)
    ax.set_ylabel("Score", fontsize=11)
    ax.set_title("Baseline vs Ensemble Comparison", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(metric_names, fontsize=10)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 1.15)
    ax.grid(True, alpha=0.3, axis="y")

    # Annotate values
    for i, (bv, ev) in enumerate(zip(baseline_vals, ensemble_vals)):
        ax.text(i - width/2, bv + 0.02, f"{bv:.2f}", ha="center", fontsize=8, color="#c0392b")
        ax.text(i + width/2, ev + 0.02, f"{ev:.2f}", ha="center", fontsize=8, color="#1e8449")

    _fig_to_file(fig, out_path)


# ---------------------------------------------------------------------------
# HTML Report
# ---------------------------------------------------------------------------

def _img_tag(path: Path, width: int = 700) -> str:
    """Create base64-embedded img tag from a PNG file."""
    if not path.exists():
        return f"<p><em>[Image not found: {path.name}]</em></p>"
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f'<img src="data:image/png;base64,{b64}" width="{width}" style="border:1px solid #ddd; border-radius:4px; margin:8px 0;">'


def generate_html_report(
    metrics: dict,
    baseline_metrics: dict,
    severity_metrics: dict,
    predictions_df: pd.DataFrame,
    results_dir: Path,
    overlay_files: list[str],
) -> None:
    """Generate comprehensive HTML evaluation report."""

    # Build overlay gallery HTML
    overlay_html = ""
    figures_dir = results_dir / "figures"
    for fname in overlay_files[:20]:
        fpath = figures_dir / fname
        if fpath.exists():
            overlay_html += _img_tag(fpath, width=850) + "\n"

    # Severity table
    sev_rows = ""
    for sev, sm in severity_metrics.items():
        sev_rows += f"""<tr>
            <td>{sev}</td><td>{sm.get('n',0)}</td><td>{sm.get('auc','—')}</td>
            <td>{sm.get('accuracy','—')}</td><td>{sm.get('precision_fail','—')}</td>
            <td>{sm.get('recall_fail','—')}</td>
        </tr>"""

    # Per-sample table (top 30 interesting cases)
    df = predictions_df.copy()
    interesting = pd.concat([
        df.nsmallest(10, "score"),
        df.nlargest(10, "score"),
        df[df["prediction"] == "needs_review"].head(10),
    ]).drop_duplicates(subset="pair_id")

    sample_rows = ""
    for _, r in interesting.iterrows():
        gt = "aligned" if r["label"] == 1 else "misaligned"
        pred_class = "pass-cell" if r["prediction"] == "pass" else ("fail-cell" if r["prediction"] == "fail" else "review-cell")
        correct = "✓" if (r["label"] == 1 and r["score"] >= 0.5) or (r["label"] == 0 and r["score"] < 0.5) else "✗"
        sample_rows += f"""<tr>
            <td>{r['pair_id']}</td><td>{gt}</td><td class="{pred_class}">{r['prediction']}</td>
            <td>{r['score']:.4f}</td><td>{r['confidence']:.4f}</td>
            <td>{r.get('perturbation_type','—')}</td><td>{r.get('severity','—')}</td>
            <td>{correct}</td>
        </tr>"""

    m = metrics
    bm = baseline_metrics

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Light Sheet Alignment QC — Evaluation Report</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 20px; color: #333; line-height: 1.6; }}
h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
h2 {{ color: #2c3e50; margin-top: 40px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
h3 {{ color: #34495e; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #f8f9fa; font-weight: 600; }}
tr:nth-child(even) {{ background: #fafafa; }}
.metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
.metric-card {{ background: #f8f9fa; border-radius: 8px; padding: 15px; text-align: center; border-left: 4px solid #3498db; }}
.metric-card .value {{ font-size: 28px; font-weight: bold; color: #2c3e50; }}
.metric-card .label {{ font-size: 13px; color: #7f8c8d; margin-top: 4px; }}
.pass {{ color: #27ae60; font-weight: bold; }}
.fail {{ color: #e74c3c; font-weight: bold; }}
.near {{ color: #f39c12; font-weight: bold; }}
.pass-cell {{ background: #d5f5e3; }}
.fail-cell {{ background: #fadbd8; }}
.review-cell {{ background: #fef9e7; }}
.target-table td:last-child {{ font-weight: bold; }}
code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
.section-note {{ background: #eaf2f8; border-left: 4px solid #3498db; padding: 12px 16px; margin: 15px 0; border-radius: 0 4px 4px 0; }}
</style>
</head>
<body>

<h1>🔬 Light Sheet Alignment QC — Evaluation Report</h1>

<div class="section-note">
<strong>Challenge 04</strong> — Allen Institute Hackathon | Proposer: Sean Fite, Neural Dynamics<br>
Build a QC system that detects alignment failures in light-sheet microscopy tile stitching,
routes uncertain cases to human review, and outperforms a naive single-metric baseline.
</div>

<h2>1. Executive Summary</h2>

<div class="metric-grid">
<div class="metric-card"><div class="value">{m.get('auc', '—')}</div><div class="label">AUC (target ≥ 0.90)</div></div>
<div class="metric-card"><div class="value">{m.get('pr_auc', '—')}</div><div class="label">PR-AUC (target ≥ 0.85)</div></div>
<div class="metric-card"><div class="value">{m.get('precision_fail', '—')}</div><div class="label">Precision (fail) (target ≥ 0.85)</div></div>
<div class="metric-card"><div class="value">{m.get('recall_fail', '—')}</div><div class="label">Recall (fail) (target ≥ 0.80)</div></div>
<div class="metric-card"><div class="value">{m.get('review_rate_pct', '—')}%</div><div class="label">Review Rate (target ≤ 15%)</div></div>
<div class="metric-card"><div class="value">{m.get('test_accuracy', '—')}</div><div class="label">Test Accuracy</div></div>
</div>

<h3>Target Checklist</h3>
<table class="target-table">
<tr><th>Metric</th><th>Target</th><th>Achieved</th><th>Status</th></tr>
<tr><td>ROC-AUC</td><td>≥ 0.90</td><td>{m.get('auc','—')}</td><td class="{'pass' if m.get('auc',0)>=0.90 else 'fail'}">{'PASS' if m.get('auc',0)>=0.90 else 'MISS'}</td></tr>
<tr><td>PR-AUC</td><td>≥ 0.85</td><td>{m.get('pr_auc','—')}</td><td class="{'pass' if m.get('pr_auc',0)>=0.85 else 'fail'}">{'PASS' if m.get('pr_auc',0)>=0.85 else 'MISS'}</td></tr>
<tr><td>Precision (fail)</td><td>≥ 0.85</td><td>{m.get('precision_fail','—')}</td><td class="{'pass' if m.get('precision_fail',0)>=0.85 else 'fail'}">{'PASS' if m.get('precision_fail',0)>=0.85 else 'MISS'}</td></tr>
<tr><td>Recall (fail)</td><td>≥ 0.80</td><td>{m.get('recall_fail','—')}</td><td class="{'pass' if m.get('recall_fail',0)>=0.80 else 'near'}">{'PASS' if m.get('recall_fail',0)>=0.80 else 'NEAR'}</td></tr>
<tr><td>Review rate</td><td>≤ 15%</td><td>{m.get('review_rate_pct','—')}%</td><td class="{'pass' if m.get('review_rate',0)<=0.15 else 'fail'}">{'PASS' if m.get('review_rate',0)<=0.15 else 'MISS'}</td></tr>
</table>

<h2>2. Baseline Comparison</h2>
<p>The ensemble model (5 features + LogisticRegression + isotonic calibration) is compared against
a naive <strong>SSIM-only threshold baseline</strong> (SSIM &lt; 0.7 = fail).</p>

{_img_tag(results_dir / "baseline_comparison.png", 700)}

<table>
<tr><th>Metric</th><th>SSIM Baseline</th><th>5-Feature Ensemble</th><th>Improvement</th></tr>
<tr><td>AUC</td><td>{bm.get('auc','—')}</td><td>{m.get('auc','—')}</td><td>{'+' if m.get('auc',0)>bm.get('auc',0) else ''}{(m.get('auc',0)-bm.get('auc',0)):.3f}</td></tr>
<tr><td>Precision (fail)</td><td>{bm.get('precision_fail','—')}</td><td>{m.get('precision_fail','—')}</td><td>{'+' if m.get('precision_fail',0)>bm.get('precision_fail',0) else ''}{(m.get('precision_fail',0)-bm.get('precision_fail',0)):.3f}</td></tr>
<tr><td>Recall (fail)</td><td>{bm.get('recall_fail','—')}</td><td>{m.get('recall_fail','—')}</td><td>{'+' if m.get('recall_fail',0)>bm.get('recall_fail',0) else ''}{(m.get('recall_fail',0)-bm.get('recall_fail',0)):.3f}</td></tr>
<tr><td>Accuracy</td><td>{bm.get('accuracy','—')}</td><td>{m.get('test_accuracy','—')}</td><td>{'+' if m.get('test_accuracy',0)>bm.get('accuracy',0) else ''}{(m.get('test_accuracy',0)-bm.get('accuracy',0)):.3f}</td></tr>
</table>

<h2>3. ROC and PR Curves</h2>
<div style="display:flex; gap:10px; flex-wrap:wrap;">
{_img_tag(results_dir / "roc_curve.png", 480)}
{_img_tag(results_dir / "pr_curve.png", 480)}
</div>

<h2>4. Score Distribution</h2>
{_img_tag(results_dir / "score_histogram.png", 750)}

<h2>5. Confusion Matrix</h2>
{_img_tag(results_dir / "confusion_matrix.png", 400)}

<h2>6. Feature Distributions</h2>
{_img_tag(results_dir / "feature_distributions.png", 900)}

<h2>7. Per-Severity Performance</h2>
{_img_tag(results_dir / "severity_breakdown.png", 700)}

<table>
<tr><th>Severity</th><th>N pairs</th><th>AUC</th><th>Accuracy</th><th>Precision (fail)</th><th>Recall (fail)</th></tr>
{sev_rows}
</table>

<h2>8. Visual QC Overlays</h2>
<p>Each overlay shows: <strong>Left tile | Right tile | |Difference| | Alpha blend</strong></p>
{overlay_html}

<h2>9. Example Gallery (TP / FP / TN / FN)</h2>
{_img_tag(results_dir / "example_gallery.png", 900)}

<h2>10. Per-Sample QC Report (selected cases)</h2>
<table>
<tr><th>Pair ID</th><th>Ground Truth</th><th>Prediction</th><th>Score</th><th>Confidence</th><th>Perturbation</th><th>Severity</th><th>Correct</th></tr>
{sample_rows}
</table>

<h2>11. Configuration</h2>
<table>
<tr><th>Parameter</th><th>Value</th></tr>
<tr><td>Total pairs</td><td>{m.get('n_pairs','—')}</td></tr>
<tr><td>Train / Test split</td><td>{m.get('n_train','—')} / {m.get('n_test','—')}</td></tr>
<tr><td>Features</td><td>{', '.join(m.get('features_used',[]))}</td></tr>
<tr><td>Classifier</td><td>{m.get('classifier','—')}</td></tr>
<tr><td>Calibration</td><td>{m.get('calibration','—')}</td></tr>
<tr><td>Pass threshold</td><td>{m.get('pass_threshold','—')}</td></tr>
<tr><td>Fail threshold</td><td>{m.get('fail_threshold','—')}</td></tr>
<tr><td>Seed</td><td>42</td></tr>
</table>

<h2>12. Limitations</h2>
<ul>
<li>Training data is <strong>synthetic</strong> — procedural tissue textures + controlled perturbations.
Not validated on real AIND SmartSPIM/ExaSPIM data.</li>
<li>2D overlap pairs only — does not address 3D volumetric alignment QC.</li>
<li>Metric-ensemble approach (no deep learning). A CNN-based scorer could improve borderline case detection.</li>
<li>Edge continuity metric is directional (left→right boundary only).</li>
<li>Thresholds calibrated on synthetic distribution — would need recalibration on real data.</li>
</ul>

<hr>
<p style="color:#999; font-size:12px;">Generated by Light Sheet Alignment QC Pipeline | Challenge 04 | Seed=42</p>
</body>
</html>"""

    out_path = results_dir / "evaluation_report.html"
    out_path.write_text(html)
    print(f"Wrote {out_path}")
