# AQUA PROMPT — Replicate Challenge 13: Croissant Pipeline for AI-Ready Data

> Copy this entire prompt and paste it to Aqua to have it fully recreate this capsule from scratch.

---

## Prompt

```
I need you to replicate the "Challenge 13: Croissant Pipeline for AI-Ready Data" capsule from the Allen Institute Hackathon. Follow these steps exactly:

### STEP 1: Create the capsule from GitHub
Create a new capsule by copying (not cloning) from the GitHub repository:
- Repository URL: https://github.com/codeocean/challenges-capsules
- After import, the code for this challenge is in the `challenge-13-croissant-pipeline/` folder within the repo. Move all files from that subfolder to `/code/` so they are at the root of the capsule's code directory. Remove any other challenge folders that were imported.

### STEP 2: Set capsule metadata
- Name: "Challenge 13: Croissant Pipeline for AI-Ready Data"
- Description: "Package Allen datasets as Croissant-compliant ML-ready resources with validated metadata, reproducible train/test splits, documented schemas, and working loading examples demonstrating the MLCommons standard for scientific data interoperability."
- Tags: hackathon-challenge, data-packaging, Croissant, ML-ready-data, metadata, reproducibility, ABC-Atlas, interoperability

### STEP 3: Configure the environment
- Starter environment: Python (codeocean/mambaforge3:22.11.1-4-ubuntu22.04) — Python 3.10
- Pip packages (install these exact versions):
  - anndata==0.11.4
  - mlcroissant==1.0.22
  - numpy==2.2.6
  - pandas==2.3.3

### STEP 4: Set compute resources
- Flex tier: Small (2 cores / 16 GB RAM)
- Machine type: CPU (general_purpose)

### STEP 5: Data assets
This capsule is self-contained. No data assets need to be attached.
It generates a synthetic frozen 10K-cell H5AD (AnnData) dataset at runtime that mimics the ABC Atlas subset structure.

If you have the real frozen ABC Atlas H5AD subset, attach it as a data asset at /data/source_dataset.h5ad

### STEP 6: Verify the run script
The `/code/run` file should contain:
```bash
#!/usr/bin/env bash
set -euo pipefail
python /code/run.py "$@"
```

### STEP 7: Verify code structure
The capsule should have these key files in /code/:
- run.py — Main orchestrator: generates data (if needed) → export → build Croissant → validate → load test
- export_tables.py — Exports cell metadata from H5AD to CSV
- build_croissant.py — Generates Croissant JSON-LD descriptor
- validate_and_load.py — Validates with mlcroissant and loads 5 real rows back

### STEP 8: Run the capsule
Run the capsule. It should produce:
- croissant_metadata.json (valid Croissant JSON-LD descriptor)
- cell_metadata.csv (exported observation metadata table)
- validation_report.json (validation status, errors if any, sample rows loaded)

The key success criterion is binary: the Croissant file must validate AND you must be able to load real data from it.
```
