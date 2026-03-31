# PROGRESS.md — Capsule 16: SciDEX

## Status: ❌ FAILING

## Current State
- /code/: run.py (5,398B), run_session2.py, schemas.py, run (5 files, ~11KB)
- Environment: pip: boto3, numpy, pandas, pydantic, requests, tqdm — provider OK
- Latest run: exit_code=1, has_results=false
- Git: NO implementation commit

## Root Cause (Likely)
- Missing data: question.json, corpus/papers.jsonl, human_decisions.json
- These need to be generated synthetically or attached

## Fix Needed
1. Diagnose exact error
2. Create synthetic seed data
3. Delegate to Claude Code
4. Run, iterate, commit
