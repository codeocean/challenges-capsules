# PROGRESS.md — Capsule 11: ABC Atlas Lit Assistant
## Status: BLOCKED (data)
- Code: run.py 9KB in /code/
- Git: ❌ no implementation commit
- Claude Code: ❓ unverified
- Artifacts: ❌ no successful run
- Provider: ✅ Bedrock (was anthropic/openai, env fixed to boto3, code fixed to bedrock-runtime)
- Run: exit_code=1 — fails on missing data
- Env: boto3, numpy, pandas, rapidfuzz, tqdm
- Missing: seed_papers.jsonl, paper_embeddings.npy, abc_taxonomy.json, eval_queries.json
- Next: create/attach data assets, delegate debug to Claude Code, commit
