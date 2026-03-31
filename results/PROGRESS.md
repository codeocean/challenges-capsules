# PROGRESS.md — Capsule 16: SciDEX
## Status: BLOCKED (data)
- Code: run.py 5KB, run_session2.py, schemas.py in /code/
- Git: ❌ no implementation commit
- Claude Code: ❓ unverified
- Artifacts: ❌ no successful run
- Provider: ✅ Bedrock (was anthropic, code fixed to bedrock-runtime)
- Run: exit_code=1 — fails on missing data
- Env: boto3, numpy, pandas, pydantic, requests, tqdm
- Missing: question.json, corpus/papers.jsonl, human_decisions.json
- Next: create/attach data assets, delegate debug to Claude Code, commit
