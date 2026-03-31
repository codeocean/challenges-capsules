# PROGRESS.md — Capsule 15: Single-Cell Pantry
## Status: BLOCKED (data + GPU)
- Code: run.py 6KB, adapters/scvi_adapter.py, adapters/geneformer_adapter.py in /code/
- Git: ❌ no implementation commit
- Claude Code: ❓ unverified
- Artifacts: ❌ no successful run
- Provider: ✅ no LLM used
- Run: exit_code=1 — fails on missing data
- Env: GPU PyTorch, anndata, scanpy, scikit-learn, scvi-tools, torch, transformers
- Missing: mtg_dataset.h5ad, gene_mapping.csv, geneformer_weights/
- Next: create/attach data assets, delegate debug to Claude Code, commit
