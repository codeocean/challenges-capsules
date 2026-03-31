# Claude Code Mission: Challenge 16 — SciDEX (Round 2)

## Context
Existing code: run.py, run_session2.py, schemas.py. Scientific discovery workflow.

## CRITICAL: EXECUTION + PROOF
1. Read existing code, run both sessions: python /code/run.py then python /code/run_session2.py
2. Verify: scidex_state.db (SQLite with evidence, hypotheses, contradictions tables)
3. Verify: evidence.jsonl, session_001_hypotheses.jsonl, session_002_hypotheses.jsonl
4. Verify: validation_report.json (21/21 checks pass, zero fabricated citations)
5. Verify: session_diff.json shows session 2 has both carried + new hypotheses
6. Verify: discovery_report.md is readable and has all sections
7. Fix anything broken and re-run
8. All results to /results/, backup to /results/backup/code/
