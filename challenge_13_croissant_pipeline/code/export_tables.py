#!/usr/bin/env python3
"""export_tables.py — Export H5AD obs to CSV with train/test split."""
from __future__ import annotations
import sys
from pathlib import Path
import anndata as ad
import numpy as np
import pandas as pd

DATA_DIR = Path("/data")
RESULTS_DIR = Path("/results")
SEED = 42

def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    h5ad_path = DATA_DIR / "source_dataset.h5ad"
    if not h5ad_path.exists():
        print(f"ERROR: {h5ad_path} not found", file=sys.stderr); sys.exit(1)

    print(f"Loading {h5ad_path} ...")
    adata = ad.read_h5ad(h5ad_path)
    print(f"  {adata.n_obs} cells, {adata.n_vars} genes")

    df = adata.obs.copy().reset_index()
    # Add random train/test split
    rng = np.random.RandomState(SEED)
    df["split"] = rng.choice(["train", "test"], size=len(df), p=[0.8, 0.2])

    out = RESULTS_DIR / "cell_metadata.csv"
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} rows to {out}")
    print(f"  Columns: {list(df.columns)}")

if __name__ == "__main__":
    main()
