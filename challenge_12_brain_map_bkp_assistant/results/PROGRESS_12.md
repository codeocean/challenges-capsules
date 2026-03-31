# PROGRESS.md — Capsule 12: Brain-map + BKP

## Status: ❌ FAILING

## Current State
- /code/: build_index.py, evaluate.py, run (4 files, ~7KB) — NO run.py
- Environment: pip: boto3, faiss-cpu, numpy, pandas, pydantic, sentence-transformers
- Latest run: exit_code=1, has_results=false
- Git: NO implementation commit

## Root Cause (Likely)
- Missing data: corpus.jsonl, eval_queries.jsonl
- Code structure: run calls build_index.py && evaluate.py

## Fix Needed
1. Diagnose exact error
2. Create synthetic corpus and eval data
3. Delegate to Claude Code
4. Run, iterate, commit
