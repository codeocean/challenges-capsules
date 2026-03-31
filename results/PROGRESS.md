# PROGRESS.md — Capsule 10: NeuroBase
## Status: BLOCKED (data + GPU)
- Code: run.py 12KB in /code/
- Git: ❌ no implementation commit
- Claude Code: ❓ unverified
- Artifacts: ❌ no successful run
- Provider: ✅ no LLM used
- Run: exit_code=1 — fails on missing data
- Env: GPU PyTorch, matplotlib, numpy, pandas, pynrrd, scikit-learn, torch
- Missing: brain_volume.nrrd, annotation.nrrd, neurobase_weights/, region_mapping.json
- Next: create/attach data assets, delegate debug to Claude Code, commit
