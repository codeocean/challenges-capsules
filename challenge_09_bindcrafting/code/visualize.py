#!/usr/bin/env python3
"""Visualization helpers for BindCrafting Challenge 09.

Generates:
- Score scatter: iPTM vs pLDDT with filter threshold lines
- Fusion distance chart: per-candidate terminus distances
- Filtering funnel: bar chart showing design attrition
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def score_scatter(
    df: pd.DataFrame,
    all_df: pd.DataFrame | None = None,
    output_path: Path = Path("/results/top5_visualizations/score_scatter.png"),
    iptm_min: float = 0.7,
    plddt_min: float = 80.0,
) -> None:
    """iPTM vs pLDDT scatter with filter thresholds and top candidates highlighted."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 6))

    # Plot all designs in grey if available
    if all_df is not None and "iptm" in all_df.columns and "plddt" in all_df.columns:
        ax.scatter(
            all_df["iptm"], all_df["plddt"],
            c="#cccccc", s=20, alpha=0.5, zorder=2, label="All designs",
        )

    # Plot top candidates
    if "iptm" in df.columns and "plddt" in df.columns:
        scatter = ax.scatter(
            df["iptm"], df["plddt"],
            c="#2ecc71", s=120, edgecolors="black", linewidths=1.2, zorder=5,
            label="Top ranked",
        )
        # Annotate
        for _, row in df.iterrows():
            label = row.get("design_name", f"rank {row.get('rank', '?')}")
            ax.annotate(
                label,
                (row["iptm"], row["plddt"]),
                fontsize=7,
                ha="left",
                va="bottom",
                xytext=(4, 4),
                textcoords="offset points",
            )

    # Filter thresholds
    ax.axvline(iptm_min, color="red", linestyle="--", alpha=0.6, label=f"iPTM ≥ {iptm_min}")
    ax.axhline(plddt_min, color="blue", linestyle="--", alpha=0.6, label=f"pLDDT ≥ {plddt_min}")

    # Shade passing region
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    ax.fill_between(
        [iptm_min, xlim[1]], plddt_min, ylim[1],
        alpha=0.08, color="green", zorder=1,
    )

    ax.set_xlabel("iPTM (Interface Predicted TM-score)", fontsize=11)
    ax.set_ylabel("pLDDT (Predicted Local Distance Difference Test)", fontsize=11)
    ax.set_title("BindCraft Candidates — AF2 Confidence Metrics", fontsize=13, fontweight="bold")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Score scatter → {output_path}")


def fusion_distance_chart(
    fusion_data: list[dict[str, Any]],
    output_path: Path = Path("/results/top5_visualizations/fusion_distance.png"),
    threshold: float = 15.0,
) -> None:
    """Bar chart comparing N-term and C-term distances to interface."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    names = [d.get("design", "?") for d in fusion_data]
    n_dists = [d.get("n_term_distance_to_interface", 0) for d in fusion_data]
    c_dists = [d.get("c_term_distance_to_interface", 0) for d in fusion_data]

    x = np.arange(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    bars_n = ax.bar(x - width / 2, n_dists, width, label="N-terminus", color="#3498db", edgecolor="black")
    bars_c = ax.bar(x + width / 2, c_dists, width, label="C-terminus", color="#e74c3c", edgecolor="black")

    # Safety threshold line
    ax.axhline(threshold, color="green", linestyle="--", linewidth=2, alpha=0.7,
               label=f"Safety threshold ({threshold} Å)")

    ax.set_xlabel("Candidate", fontsize=11)
    ax.set_ylabel("Distance to Nearest Interface Residue (Å)", fontsize=11)
    ax.set_title("Fluorescent Fusion Compatibility — Terminus Distances", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=30, ha="right", fontsize=9)
    ax.legend(fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)

    # Annotate recommended terminus
    for i, fd in enumerate(fusion_data):
        rec = fd.get("recommended_terminus", "?")
        safe = fd.get("fusion_safe", False)
        color = "green" if safe else "red"
        y_max = max(n_dists[i], c_dists[i])
        ax.annotate(
            f"{rec}-term" if safe else "⚠",
            (i, y_max + 1),
            ha="center", fontsize=8, fontweight="bold", color=color,
        )

    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Fusion distance chart → {output_path}")


def filtering_funnel(
    funnel: dict[str, Any],
    output_path: Path = Path("/results/top5_visualizations/filtering_funnel.png"),
) -> None:
    """Funnel bar chart showing design attrition through filtering stages."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    stages = ["Total\nTrajectories", "Surviving\nFilters", "Top\nRanked"]
    counts = [
        funnel.get("total_trajectories", 0),
        funnel.get("surviving_filters", 0),
        funnel.get("top_ranked", 0),
    ]

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = ["#95a5a6", "#f39c12", "#27ae60"]
    bars = ax.bar(stages, counts, color=colors, edgecolor="black", linewidth=1.2)

    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 2,
            str(count),
            ha="center",
            va="bottom",
            fontsize=14,
            fontweight="bold",
        )

    ax.set_ylabel("Number of Designs", fontsize=11)
    ax.set_title("Design Filtering Funnel", fontsize=13, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Filtering funnel → {output_path}")
