# AQUA PROMPT — Replicate Challenge 15: Allen Single-Cell Model Pantry

> Copy this entire prompt and paste it to Aqua to have it fully recreate this capsule from scratch.

---

## Prompt

```
I need you to replicate the "Challenge 15: Allen Single-Cell Model Pantry" capsule from the Allen Institute Hackathon. Follow these steps exactly:

### STEP 1: Create the capsule from GitHub
Create a new capsule by copying (not cloning) from the GitHub repository:
- Repository URL: https://github.com/codeocean/challenges-capsules
- After import, the code for this challenge is in the `challenge-15-single-cell-model-pantry/` folder within the repo. Move all files from that subfolder to `/code/` so they are at the root of the capsule's code directory. Remove any other challenge folders that were imported.

### STEP 2: Set capsule metadata
- Name: "Challenge 15: Allen Single-Cell Model Pantry"
- Description: "Build a reproducible benchmark system for single-cell foundation models on Allen datasets with frozen splits, shared evaluation contracts, and comparable metrics across models demonstrating fair performance assessment for cell type annotation and batch integration."
- Tags: hackathon-challenge, foundation-models, single-cell, benchmarking, scRNA-seq, evaluation, ABC-Atlas, machine-learning

### STEP 3: Configure the environment
IMPORTANT: This capsule requires a GPU-enabled PyTorch base image.
- Starter environment: PyTorch (codeocean/pytorch:2.4.0-cuda12.4.0-mambaforge24.5.0-0-python3.12.4-ubuntu22.04)
- Machine type: GPU
- Pip packages (install WITHOUT version pins — let PyTorch compatibility resolve):
  - anndata
  - matplotlib
  - numpy
  - pandas
  - scanpy
  - scikit-learn
  - scvi-tools
  - torch
  - torchvision
  - transformers

### STEP 4: Set compute resources
- Flex tier: X-Small (1 GPU / 16 GB GPU RAM / 4 cores / 15 GB RAM)
- Machine type: GPU

### STEP 5: Data assets
This capsule is self-contained. No data assets need to be attached.
It generates a synthetic frozen pre-split Allen Human MTG-like dataset at runtime with cell type labels and train/test splits.

If you have the real Allen Human MTG dataset, attach it as a data asset:
- mtg_dataset.h5ad at /data/mtg_dataset.h5ad (with 'split' column: 'train'/'test')
- gene_mapping.csv at /data/gene_mapping.csv
- Geneformer weights at /data/geneformer_weights/

### STEP 6: Verify the run script
The `/code/run` file should contain:
```bash
#!/usr/bin/env bash
set -euo pipefail
python /code/run.py "$@"
```

### STEP 7: Verify code structure
The capsule should have these key files in /code/:
- run.py — Main benchmark pipeline: load data → run model adapters → KNN evaluation → leaderboard
- adapters/scvi_adapter.py — scVI model adapter
- adapters/geneformer_adapter.py — Geneformer model adapter

### STEP 8: Run the capsule
Run the capsule WITH GPU. It should produce:
- leaderboard.csv (model, accuracy, macro_f1, runtime_seconds)
- confusion_scvi.png (scVI confusion matrix)
- confusion_geneformer.png (Geneformer confusion matrix)
- summary.json (winner, test cells, per-model F1 details)
```
