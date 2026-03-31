# PROGRESS.md — Capsule 12: Brain-map + BKP
## Status: BLOCKED (data)
- Code: build_index.py, evaluate.py in /code/ (~7KB)
- Git: ❌ no implementation commit
- Claude Code: ❓ unverified
- Artifacts: ❌ no successful run
- Provider: ✅ Bedrock (was anthropic/openai, code fixed to bedrock-runtime)
- Run: exit_code=1 — fails on missing data
- Env: boto3, faiss-cpu, numpy, pandas, pydantic, sentence-transformers
- Missing: corpus.jsonl, eval_queries.jsonl
- Next: create/attach data assets, delegate debug to Claude Code, commit
