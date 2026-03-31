# PROGRESS.md — Capsule 15: Single-Cell Pantry

## Status: ❌ FAILING

## Current State
- /code/: run.py (5,563B), adapters/scvi_adapter.py, adapters/geneformer_adapter.py (4 items, ~9KB)
- Environment: GPU PyTorch, pip: anndata, matplotlib, numpy, pandas, scanpy, scikit-learn, scvi-tools, torch, transformers
- Latest run: exit_code=1, has_results=false
- Git: NO implementation commit

## Root Cause (Likely)
- Missing data: mtg_dataset.h5ad, gene_mapping.csv, geneformer_weights/
- Requires GPU for model inference

## Fix Needed
1. Diagnose exact error
2. Create synthetic h5ad or attach real MTG dataset
3. Handle missing model weights gracefully
4. Delegate to Claude Code
5. Run, iterate, commit
