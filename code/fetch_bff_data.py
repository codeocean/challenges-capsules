#!/usr/bin/env python3
"""fetch_bff_data.py — Download real Allen Cell BFF metadata from public S3.

Downloads three metadata CSVs from s3://allencell (no credentials needed),
writes them to /results so they can be captured as a Code Ocean data asset.

Usage:
  python /code/fetch_bff_data.py          # download to /results
  python /code/fetch_bff_data.py --check  # just check if data exists in /data
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import boto3
import pandas as pd
from botocore import UNSIGNED
from botocore.config import Config

BUCKET = "allencell"
REGION = "us-east-1"
RESULTS = Path("/results")
DATA = Path("/data")

S3_FILES = [
    ("aics/hipsc_12x_overview_image_dataset/metadata.csv", "hipsc_12x_metadata.csv"),
    ("aics/NPM1_single_cell_drug_perturbations/manifest.csv", "npm1_drug_manifest.csv"),
    ("aics/hipsc_single_cell_image_dataset_supp_myh10/metadata.csv", "myh10_metadata.csv"),
]


def find_manifests_in_data() -> list[Path]:
    """Search /data for any CSV/Parquet that looks like a BFF manifest."""
    found = []
    for pattern in ("*.csv", "*.parquet"):
        for p in DATA.rglob(pattern):
            if p.stat().st_size > 1000 and "hackathon_challang" not in str(p):
                found.append(p)
    return found


def download_all() -> list[Path]:
    """Download metadata CSVs from public S3 to /results."""
    s3 = boto3.client("s3", region_name=REGION, config=Config(signature_version=UNSIGNED))
    RESULTS.mkdir(parents=True, exist_ok=True)
    downloaded = []
    for s3_key, local_name in S3_FILES:
        local = RESULTS / local_name
        print(f"  ↓ s3://{BUCKET}/{s3_key} → {local}")
        try:
            s3.download_file(BUCKET, s3_key, str(local))
            size_kb = local.stat().st_size / 1024
            print(f"    ✓ {size_kb:.1f} KB")
            downloaded.append(local)
        except Exception as e:
            print(f"    ✗ Failed: {e}", file=sys.stderr)
    return downloaded


def preview_file(path: Path) -> dict:
    """Load and return summary info for a CSV/Parquet file."""
    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path, low_memory=False)
    return {
        "file": path.name,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": {c: str(df[c].dtype) for c in df.columns},
        "sample_row": df.head(1).to_dict(orient="records")[0] if len(df) > 0 else {},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="Only check if data exists in /data, do not download")
    args = parser.parse_args()

    # Check existing data
    existing = find_manifests_in_data()
    if existing:
        print(f"Found {len(existing)} manifest(s) in /data:")
        for p in existing:
            print(f"  {p} ({p.stat().st_size / 1024:.1f} KB)")
        if args.check:
            print("Data already available — no download needed.")
            return

    if args.check and not existing:
        print("No manifest found in /data — download required.")
        sys.exit(1)

    # Download
    print(f"\nDownloading BFF metadata from s3://{BUCKET} ...")
    downloaded = download_all()

    if not downloaded:
        print("ERROR: No files downloaded.", file=sys.stderr)
        sys.exit(1)

    # Preview each file
    RESULTS.mkdir(parents=True, exist_ok=True)
    summaries = []
    print(f"\n{'='*60}")
    print("DOWNLOADED FILE SUMMARIES")
    print(f"{'='*60}")
    for p in downloaded:
        info = preview_file(p)
        summaries.append(info)
        print(f"\n  {info['file']}: {info['rows']} rows × {info['columns']} cols")
        print(f"  Columns: {info['column_names']}")

    # Write manifest of what we downloaded
    with open(RESULTS / "download_manifest.json", "w") as f:
        json.dump({
            "source_bucket": f"s3://{BUCKET}",
            "files_downloaded": len(downloaded),
            "files": summaries,
        }, f, indent=2, default=str)

    print(f"\n✓ Downloaded {len(downloaded)} files to {RESULTS}")


if __name__ == "__main__":
    main()
