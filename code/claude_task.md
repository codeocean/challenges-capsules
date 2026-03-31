# Claude Code Mission: Challenge 07 — Engineering Automation (Round 2)

## Context
Existing code: run.py (20KB), create_test_repos.py (11KB). Edit-test-retry agent with Bedrock.

## CRITICAL: EXECUTION + PROOF
1. Read existing code, run the full pipeline
2. Verify: dashboard.json exists with 15+ tasks, resolve rate by type, risk calibration, explanation quality
3. Verify: run_log.jsonl with per-task traces
4. Verify: patches/ folder with diffs, reports/ with per-task summaries
5. Fix anything broken and re-run
6. All results to /results/, backup to /results/backup/code/
