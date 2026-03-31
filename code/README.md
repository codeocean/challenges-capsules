# Challenge 13: Croissant Pipeline for AI-Ready Data

## What This Capsule Does
Takes a frozen 10K-cell H5AD, exports cell metadata to CSV, generates a Croissant
JSON-LD descriptor, validates with mlcroissant, and loads 5 real rows back.

## Evaluation
Binary pass/fail — does the Croissant file validate AND can you load real data from it?

## Required Data Assets
| File | Description |
|------|-------------|
| `source_dataset.h5ad` | Frozen 10K-cell ABC Atlas subset |

## Expected Outputs
| File | Description |
|------|-------------|
| `croissant_metadata.json` | Valid Croissant JSON-LD |
| `cell_metadata.csv` | Exported from H5AD obs |
| `validation_report.json` | Status, errors, rows loaded |

## Environment
- CPU only. `mlcroissant`, `anndata`, `pandas`, `numpy`
