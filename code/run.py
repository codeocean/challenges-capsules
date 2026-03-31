#!/usr/bin/env python3
"""Challenge 14: Segment Intestine Villi — Single-file implementation.

Loads Xenium ileum spatial transcriptomics data, scores cells as epithelial using
marker genes, builds spatial neighbor graph with squidpy, runs Leiden clustering,
and outputs a color-coded spatial map plus per-villus cell type composition table.

Eval: Visual — do the colored clusters correspond to individual villi?
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR = Path("/data")
RESULTS_DIR = Path("/results")
XENIUM_DIR = DATA_DIR / "xenium_ileum"

EPITHELIAL_MARKERS = ["EPCAM", "FABP1", "FABP2", "VIL1"]
SPATIAL_RADIUS = 50  # microns
LEIDEN_RESOLUTION = 0.5
SEED = 42


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # --- Validate inputs / generate synthetic if missing --------------------
    data_source = "real"
    if not XENIUM_DIR.exists() or not list(XENIUM_DIR.glob("*.h5*")):
        print("Xenium data not found. Generating synthetic villus-like spatial data...")
        data_source = "synthetic"

        rng = np.random.RandomState(SEED)
        n_cells = 3000
        n_villi = 8
        n_genes = 50

        # Generate villus-like finger projections
        coords_x = []
        coords_y = []
        villus_ids = []
        cell_types = []

        for v in range(n_villi):
            n_v = rng.randint(200, 500)
            cx = rng.uniform(100, 900)
            cy = rng.uniform(100, 900)
            # Elongated villus shape
            angle = rng.uniform(0, 2 * np.pi)
            length = rng.uniform(80, 200)
            width = rng.uniform(20, 50)
            for _ in range(n_v):
                t = rng.uniform(0, 1)
                offset = rng.normal(0, width)
                x = cx + t * length * np.cos(angle) + offset * np.sin(angle)
                y = cy + t * length * np.sin(angle) - offset * np.cos(angle)
                coords_x.append(x)
                coords_y.append(y)
                villus_ids.append(v)
                # Cell type gradient: stem cells at base, enterocytes at tip
                if t < 0.2:
                    cell_types.append("stem_cell")
                elif t < 0.5:
                    cell_types.append("transit_amplifying")
                elif rng.random() < 0.15:
                    cell_types.append("goblet_cell")
                else:
                    cell_types.append("enterocyte")

        actual_n = len(coords_x)
        # Gene expression (sparse count matrix)
        X = rng.negative_binomial(2, 0.5, size=(actual_n, n_genes)).astype(np.float32)
        # Add marker gene enrichment by cell type
        gene_names = [f"Gene_{i}" for i in range(n_genes)]
        gene_names[0] = "EPCAM"; gene_names[1] = "FABP1"; gene_names[2] = "FABP2"; gene_names[3] = "VIL1"
        for i, ct in enumerate(cell_types):
            if ct == "enterocyte":
                X[i, :4] += rng.poisson(5, 4)  # epithelial markers high
            elif ct == "goblet_cell":
                X[i, 0] += rng.poisson(3)
            elif ct == "stem_cell":
                X[i, :4] += rng.poisson(1, 4)

        obs = pd.DataFrame({
            "cell_type": cell_types,
            "ground_truth_villus": villus_ids,
        })
        adata = sc.AnnData(X=X, obs=obs)
        adata.var_names = gene_names
        adata.obsm["spatial"] = np.column_stack([coords_x, coords_y])
        print(f"  Synthetic: {adata.n_obs} cells, {n_villi} villi, {n_genes} genes")
        print(f"  DISCLAIMER: Using synthetic spatial data. Real Xenium ileum not available.")
    else:
        # --- Load real Xenium data -----------------------------------------
        print("Loading Xenium data ...")
        h5_candidates = list(XENIUM_DIR.glob("*.h5")) + list(XENIUM_DIR.glob("*.h5ad"))
        if not h5_candidates:
            print("ERROR: No .h5 or .h5ad file found in xenium_ileum/", file=sys.stderr)
            sys.exit(1)

        h5_path = h5_candidates[0]
        if h5_path.suffix == ".h5ad":
            adata = sc.read_h5ad(str(h5_path))
        else:
            adata = sc.read_10x_h5(str(h5_path))
        print(f"  Loaded {adata.n_obs} cells, {adata.n_vars} genes")

    # Load spatial coordinates if not in adata.obsm
    if "spatial" not in adata.obsm:
        coord_files = list(XENIUM_DIR.glob("*coordinates*")) + list(XENIUM_DIR.glob("*cells.csv*"))
        if coord_files:
            coords = pd.read_csv(coord_files[0])
            # Try common column names
            for x_col, y_col in [("x_centroid", "y_centroid"), ("x", "y"), ("X", "Y")]:
                if x_col in coords.columns and y_col in coords.columns:
                    adata.obsm["spatial"] = coords[[x_col, y_col]].values[:adata.n_obs]
                    break

    if "spatial" not in adata.obsm:
        print("ERROR: No spatial coordinates found.", file=sys.stderr)
        sys.exit(1)

    # --- Normalize ---------------------------------------------------------
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

    # --- Score epithelial cells --------------------------------------------
    print("Scoring epithelial cells ...")
    available_markers = [g for g in EPITHELIAL_MARKERS if g in adata.var_names]
    if not available_markers:
        # Try lowercase
        available_markers = [g for g in EPITHELIAL_MARKERS if g.lower() in [v.lower() for v in adata.var_names]]
    print(f"  Using markers: {available_markers}")

    if available_markers:
        sc.tl.score_genes(adata, gene_list=available_markers, score_name="epithelial_score")
        threshold = adata.obs["epithelial_score"].quantile(0.5)
        adata.obs["is_epithelial"] = adata.obs["epithelial_score"] > threshold
    else:
        print("  WARNING: No epithelial markers found. Using all cells.")
        adata.obs["is_epithelial"] = True

    n_epi = adata.obs["is_epithelial"].sum()
    print(f"  Epithelial cells: {n_epi}/{adata.n_obs}")

    # --- Subset to epithelial cells ----------------------------------------
    adata_epi = adata[adata.obs["is_epithelial"]].copy()

    # --- Build spatial neighbor graph --------------------------------------
    print("Building spatial neighbor graph ...")
    import squidpy as sq
    sq.gr.spatial_neighbors(adata_epi, radius=SPATIAL_RADIUS, coord_type="generic")

    # Wire squidpy spatial graph into scanpy neighbors structure.
    # squidpy stores in .obsp["spatial_connectivities"] / ["spatial_distances"]
    # and .uns["spatial_neighbors"].  scanpy.tl.leiden needs .uns["neighbors"].
    for src, dst in [("spatial_connectivities", "connectivities"),
                     ("spatial_distances", "distances")]:
        if src in adata_epi.obsp:
            adata_epi.obsp[dst] = adata_epi.obsp[src]
    adata_epi.uns["neighbors"] = {
        "connectivities_key": "connectivities",
        "distances_key": "distances",
        "params": {"method": "squidpy_spatial", "radius": SPATIAL_RADIUS},
    }
    print(f"  obsp keys: {list(adata_epi.obsp.keys())}")
    print(f"  uns keys: {list(adata_epi.uns.keys())}")

    # --- Leiden clustering -------------------------------------------------
    print("Running Leiden clustering ...")
    try:
        sc.tl.leiden(adata_epi, resolution=LEIDEN_RESOLUTION, random_state=SEED,
                     flavor="igraph", n_iterations=2, directed=False)
    except Exception as e:
        print(f"  Leiden with igraph failed ({e}), trying default flavor...")
        sc.tl.leiden(adata_epi, resolution=LEIDEN_RESOLUTION, random_state=SEED)
    n_clusters = adata_epi.obs["leiden"].nunique()
    print(f"  Found {n_clusters} clusters (villus candidates)")

    # --- Spatial plot -------------------------------------------------------
    print("Generating spatial plot ...")
    fig, ax = plt.subplots(figsize=(12, 10))
    coords = adata_epi.obsm["spatial"]
    clusters = adata_epi.obs["leiden"].astype(int)
    scatter = ax.scatter(coords[:, 0], coords[:, 1], c=clusters, cmap="tab20",
                         s=1, alpha=0.7, rasterized=True)
    ax.set_title(f"Villus Segmentation — {n_clusters} clusters (Leiden res={LEIDEN_RESOLUTION})")
    ax.set_xlabel("X (μm)")
    ax.set_ylabel("Y (μm)")
    ax.set_aspect("equal")
    fig.colorbar(scatter, ax=ax, label="Cluster ID", shrink=0.5)
    fig.tight_layout()
    fig.savefig(str(RESULTS_DIR / "spatial_plot.png"), dpi=200)
    plt.close(fig)
    print("  Wrote spatial_plot.png")

    # --- Villus assignments ------------------------------------------------
    assignments = pd.DataFrame({
        "cell_id": adata_epi.obs.index,
        "villus_cluster_id": adata_epi.obs["leiden"].values,
        "is_epithelial": True,
        "x": coords[:, 0],
        "y": coords[:, 1],
    })
    assignments.to_csv(RESULTS_DIR / "villus_assignments.csv", index=False)
    print(f"  Wrote villus_assignments.csv ({len(assignments)} cells)")

    # --- Per-villus summary with area, centroids, marker expression ---------
    summary_rows = []
    geojson_features = []
    for cluster_id in sorted(adata_epi.obs["leiden"].unique(), key=int):
        mask = adata_epi.obs["leiden"] == cluster_id
        n_cells = int(mask.sum())
        cluster_coords = coords[mask.values]
        cx, cy = float(cluster_coords[:, 0].mean()), float(cluster_coords[:, 1].mean())

        # Compute area using convex hull
        try:
            from scipy.spatial import ConvexHull
            if len(cluster_coords) >= 4:
                hull = ConvexHull(cluster_coords)
                area = float(hull.volume)  # 2D: volume = area
                # Build GeoJSON polygon from hull vertices
                hull_pts = cluster_coords[hull.vertices]
                polygon_coords = [[float(p[0]), float(p[1])] for p in hull_pts]
                polygon_coords.append(polygon_coords[0])  # close ring
            else:
                area = 0.0
                polygon_coords = [[float(p[0]), float(p[1])] for p in cluster_coords]
                if polygon_coords:
                    polygon_coords.append(polygon_coords[0])
        except Exception:
            area = 0.0
            polygon_coords = []

        # Mean epithelial marker expression
        if available_markers:
            marker_expr = float(adata_epi[mask, :].obs.get("epithelial_score", pd.Series([0])).mean())
        else:
            marker_expr = 0.0

        summary_rows.append({
            "villus_cluster_id": int(cluster_id),
            "n_cells": n_cells,
            "area_um2": round(area, 1),
            "centroid_x": round(cx, 1),
            "centroid_y": round(cy, 1),
            "mean_epithelial_score": round(marker_expr, 4),
        })

        # GeoJSON feature
        if polygon_coords:
            geojson_features.append({
                "type": "Feature",
                "properties": {
                    "villus_id": int(cluster_id),
                    "n_cells": n_cells,
                    "area_um2": round(area, 1),
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [polygon_coords],
                }
            })

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(RESULTS_DIR / "per_villus_summary.csv", index=False)
    print(f"  Wrote per_villus_summary.csv ({len(summary_df)} clusters, {summary_df.columns.tolist()})")

    # --- Write GeoJSON boundaries ------------------------------------------
    import json
    geojson = {
        "type": "FeatureCollection",
        "features": geojson_features,
    }
    with open(RESULTS_DIR / "villus_boundaries.geojson", "w") as f:
        json.dump(geojson, f, indent=2, default=str)
    print(f"  Wrote villus_boundaries.geojson ({len(geojson_features)} polygons)")

    # --- Data provenance ---------------------------------------------------
    provenance = {
        "data_source": data_source,
        "n_cells": int(adata.n_obs),
        "n_epithelial": int(n_epi),
        "n_villi": n_clusters,
        "disclaimer": "Using synthetic spatial data. Real Xenium ileum not available." if data_source == "synthetic" else "Real Xenium data.",
    }
    with open(RESULTS_DIR / "data_provenance.json", "w") as f:
        json.dump(provenance, f, indent=2)

    print("\nDone.")


if __name__ == "__main__":
    main()
