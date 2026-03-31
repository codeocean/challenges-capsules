# PROGRESS.md — Capsule 14: Segment Intestine Villi

## Status: ❌ FAILING

## Current State
- /code/: run.py (6,226B), run (3 files, ~7KB)
- Environment: pip: anndata, matplotlib, numpy, pandas, scanpy, squidpy — no LLM
- Latest run: exit_code=1, has_results=false
- Git: NO implementation commit

## Root Cause (Likely)
- Missing data: xenium_ileum/ (Xenium cell feature matrix + spatial coords)
- This is real experimental data that must be obtained

## Fix Needed
1. Diagnose exact error
2. Create synthetic Xenium-like data or confirm data availability
3. Delegate to Claude Code
4. Run, iterate, commit
