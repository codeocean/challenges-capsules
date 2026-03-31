# Claude Code Mission: Challenge 05 — Automate Your Productivity (Round 2)

## Context
Existing code: run.py, bedrock_agent.py, scenarios.py, tools.py, streamlit_app.py.

## CRITICAL: EXECUTION + PROOF  
1. Read existing code, run in MOCK_MODE: python /code/run.py
2. Verify these outputs exist and are non-empty:
   - /results/focus_blocks.ics (valid iCal with VCALENDAR/VEVENT)
   - /results/audit_log.jsonl (13+ entries)
   - /results/approval_log.json
   - /results/metrics_report.json (step reduction > 0)
   - /results/goal_report.json (3+ goals)
   - /results/preference_model.json
   - /results/second_pass_proposals.json (differs from first pass)
3. Fix anything missing/broken and re-run
4. All results to /results/, backup to /results/backup/code/
