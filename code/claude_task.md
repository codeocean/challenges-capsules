# Claude Code Mission: Challenge 08 — Query BFF (Round 2)

## Context
Existing code: run.py (32KB), fetch_bff_data.py. NL-to-filter with Bedrock.

## CRITICAL: EXECUTION + PROOF
1. Read existing code, run the pipeline
2. Verify: evaluation_report.json with 25+ queries, 2 manifests, per-manifest metrics
3. Verify: relevance_verification section, overconfident-wrong detection
4. Verify: schema extraction works on both manifests independently
5. Fix anything broken and re-run
6. All results to /results/, backup to /results/backup/code/
