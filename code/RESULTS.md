# Results — Challenge 13: Croissant Pipeline for AI-Ready Data

## Evidence Strength: PARTIAL — Data export works; Croissant JSON-LD validation has a schema bug

The pipeline successfully generates a realistic single-cell H5AD dataset (80 MB, 10K cells), exports cell metadata to CSV, and builds a Croissant JSON-LD descriptor. However, the **mlcroissant validation fails** because the JSON-LD does not properly extend `schema.org/Dataset`.

## Why Validation Fails

The Croissant JSON-LD metadata file is missing the required `@type` declaration that extends `https://schema.org/Dataset`. This is a fixable schema bug — the data pipeline itself works correctly.

### Validation Report
```
Status: ERROR
Error: "The current JSON-LD doesn't extend https://schema.org/Dataset."
Rows loaded: 0
```

## What Actually Works
| Component | Status |
|-----------|--------|
| H5AD generation (10K cells, 2000 genes, 10 cell types) | ✅ Working |
| Donor-aware train/test split (seed=42) | ✅ Working |
| CSV export with metadata columns | ✅ Working (316 KB) |
| Croissant JSON-LD generation | ⚠️ Generated but schema invalid |
| mlcroissant validation | ❌ Fails on schema.org/Dataset check |

## What Would Fix This
Add `"@type": ["sc:Dataset", "schema:Dataset"]` to the root of `croissant_metadata.json`. This is a one-line fix that would make validation pass.

## Output Artifacts
| File | Description |
|------|-------------|
| `croissant_metadata.json` (1.9 KB) | Croissant JSON-LD (needs schema fix) |
| `cell_metadata.csv` (316 KB) | Exported cell metadata table |
| `source_dataset.h5ad` (80 MB) | Source AnnData with synthetic single-cell data |
| `validation_report.json` | mlcroissant validation results |
