# PROGRESS.md — Capsule 11: ABC Atlas Lit Assistant

## Status: ❌ FAILING

## Current State
- /code/: run.py (8,700B), run — code exists but fails
- Environment: pip: boto3, numpy, pandas, rapidfuzz, tqdm — provider OK
- Code uses Bedrock (boto3 bedrock-runtime) — provider correct
- Latest run: exit_code=1, has_results=false
- Git: NO implementation commit

## Root Cause (Likely)
- Missing data assets: seed_papers.jsonl, paper_embeddings.npy, abc_taxonomy.json, eval_queries.json
- These need to be created/generated or attached

## Fix Needed
1. Diagnose exact error
2. Create synthetic seed data generation or attach real data
3. Delegate fix to Claude Code
4. Run, iterate 3 rounds
5. Commit code
