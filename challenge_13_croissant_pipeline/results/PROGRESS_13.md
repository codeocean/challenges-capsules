# PROGRESS.md — Capsule 13: Croissant Pipeline

## Status: ❌ FAILING

## Current State
- /code/: export_tables.py, build_croissant.py, validate_and_load.py, run (5 files, ~6KB)
- Environment: pip: anndata, mlcroissant, numpy, pandas — no LLM needed
- Latest run: exit_code=1, has_results=false
- Git: NO implementation commit

## Root Cause (Likely)
- Missing data: source_dataset.h5ad
- Code expects h5ad file in /data/

## Fix Needed
1. Diagnose exact error
2. Create synthetic h5ad or attach real ABC Atlas subset
3. Delegate to Claude Code
4. Run, iterate, commit
