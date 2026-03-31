#!/usr/bin/env python3
"""Challenge 13: Croissant Pipeline — Orchestrator.

Generates a synthetic scRNA-seq dataset (if not provided), exports cell
metadata CSV with donor-aware train/test splits, builds Croissant JSON-LD
metadata, and validates with mlcroissant.
"""
from __future__ import annotations

import sys
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd

DATA_DIR = Path("/data")
RESULTS_DIR = Path("/results")
SEED = 42


def generate_synthetic_h5ad(out_path: Path) -> None:
    """Create a realistic 10K-cell single-cell dataset with donor-aware splits."""
    rng = np.random.RandomState(SEED)
    n_cells = 10_000
    n_genes = 2000
    n_donors = 6
    cell_types = [
        "Excitatory_L2/3", "Excitatory_L4", "Excitatory_L5",
        "Inhibitory_Pvalb", "Inhibitory_Sst", "Inhibitory_Vip",
        "Astrocyte", "Oligodendrocyte", "Microglia", "OPC",
    ]

    # Assign donors and cell types
    donors = [f"donor_{i}" for i in range(n_donors)]
    obs_donors = rng.choice(donors, n_cells)
    obs_types = rng.choice(cell_types, n_cells)

    # Generate sparse-ish counts
    X = rng.negative_binomial(2, 0.5, size=(n_cells, n_genes)).astype(np.float32)
    # Add cell-type-specific signal
    for i, ct in enumerate(cell_types):
        mask = obs_types == ct
        marker_start = i * 20
        X[mask, marker_start:marker_start + 20] += rng.poisson(5, size=(mask.sum(), 20))

    gene_names = [f"Gene_{i}" for i in range(n_genes)]
    # Use real-ish gene names for first few
    real_genes = ["SNAP25", "GAD1", "GAD2", "SLC17A7", "PVALB", "SST", "VIP",
                  "AQP4", "OLIG2", "CSF1R", "PDGFRA", "MBP", "GFAP", "RBFOX3"]
    for i, g in enumerate(real_genes):
        if i < n_genes:
            gene_names[i] = g

    # Donor-aware train/test split (hold out 2 donors for test)
    test_donors = set(donors[-2:])
    splits = ["test" if d in test_donors else "train" for d in obs_donors]

    obs = pd.DataFrame({
        "cell_type": obs_types,
        "donor": obs_donors,
        "split": splits,
    })

    adata = ad.AnnData(X=X, obs=obs)
    adata.var_names = gene_names
    adata.write_h5ad(out_path)
    print(f"  Generated {out_path}: {n_cells} cells, {n_genes} genes, {n_donors} donors")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Step 0: Generate or find source dataset
    h5ad_path = DATA_DIR / "source_dataset.h5ad"
    if not h5ad_path.exists():
        print("Source h5ad not found. Generating synthetic scRNA-seq dataset...")
        h5ad_path = RESULTS_DIR / "source_dataset.h5ad"
        generate_synthetic_h5ad(h5ad_path)
        print("  DISCLAIMER: Using synthetic data. Real Allen dataset not attached.")

    # Step 1: Export tables
    print("\nExporting cell metadata CSV...")
    adata = ad.read_h5ad(h5ad_path)
    df = adata.obs.copy().reset_index()
    if "split" not in df.columns:
        rng = np.random.RandomState(SEED)
        df["split"] = rng.choice(["train", "test"], size=len(df), p=[0.8, 0.2])
    csv_path = RESULTS_DIR / "cell_metadata.csv"
    df.to_csv(csv_path, index=False)
    print(f"  Wrote {len(df)} rows to {csv_path}")

    # Step 2: Build Croissant JSON-LD
    print("\nBuilding Croissant metadata...")
    import json
    fields = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        cr_type = "sc:Text"
        if "int" in dtype:
            cr_type = "sc:Integer"
        elif "float" in dtype:
            cr_type = "sc:Float"
        fields.append({
            "@type": "cr:Field",
            "name": col,
            "dataType": cr_type,
            "source": {"fileObject": {"@id": "cell_metadata_csv"}, "extract": {"column": col}},
        })

    croissant = {
        "@context": {"@vocab": "https://schema.org/", "cr": "http://mlcommons.org/croissant/"},
        "@type": "cr:Dataset",
        "name": "Allen Brain Cell Atlas — Single-Cell Metadata",
        "description": "Cell metadata with donor-aware train/test splits for ML benchmarking.",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "distribution": [
            {
                "@type": "cr:FileObject",
                "@id": "cell_metadata_csv",
                "name": "cell_metadata.csv",
                "contentUrl": "cell_metadata.csv",
                "encodingFormat": "text/csv",
            },
        ],
        "recordSet": [
            {
                "@type": "cr:RecordSet",
                "name": "cell_records",
                "field": fields,
            },
        ],
    }

    croissant_path = RESULTS_DIR / "croissant_metadata.json"
    with open(croissant_path, "w") as f:
        json.dump(croissant, f, indent=2)
    print(f"  Wrote {croissant_path}")

    # Step 3: Validate with mlcroissant
    print("\nValidating Croissant metadata...")
    try:
        import mlcroissant as mlc
        ds = mlc.Dataset(jsonld=croissant_path)
        rows = 0
        for record in ds.records(record_set="cell_records"):
            rows += 1
            if rows >= 5:
                break
        report = {"status": "valid", "errors": [], "rows_loaded": rows}
        print(f"  Validation PASSED: loaded {rows} rows")
    except Exception as e:
        report = {"status": "error", "errors": [str(e)], "rows_loaded": 0}
        print(f"  Validation FAILED: {e}")

    with open(RESULTS_DIR / "validation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\nDone.")


if __name__ == "__main__":
    main()
