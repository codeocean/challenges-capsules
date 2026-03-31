#!/usr/bin/env python3
"""build_croissant.py — Generate Croissant JSON-LD metadata for the exported CSV."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

RESULTS_DIR = Path("/results")

def main() -> None:
    csv_path = RESULTS_DIR / "cell_metadata.csv"
    df = pd.read_csv(csv_path, nrows=5)

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
        "name": "Allen Brain Cell Atlas — 10K Cell Subset",
        "description": "A 10,000-cell subset of the Allen Brain Cell Atlas, packaged as a Croissant-compliant ML dataset.",
        "license": "https://alleninstitute.org/terms-of-use/",
        "distribution": [
            {
                "@type": "cr:FileObject",
                "@id": "cell_metadata_csv",
                "name": "cell_metadata.csv",
                "contentUrl": "cell_metadata.csv",
                "encodingFormat": "text/csv",
            }
        ],
        "recordSet": [
            {
                "@type": "cr:RecordSet",
                "name": "cells",
                "field": fields,
            }
        ],
    }

    out = RESULTS_DIR / "croissant_metadata.json"
    with open(out, "w") as f:
        json.dump(croissant, f, indent=2)
    print(f"Wrote Croissant metadata: {out}")

if __name__ == "__main__":
    main()
