# ⚡ Challenge 05: Automate Your Productivity


## Results Summary
- **Status:** Pipeline runs end-to-end producing scenario-based analyses
- **Output:** Productivity proposals, comparison reports, synthetic workspace analysis
- **LLM Integration:** Bedrock mock mode with deterministic fallback

> See [RESULTS.md](RESULTS.md) for full output artifact listing.

## What This Capsule Does

An **agentic productivity analyser** that uses AWS Bedrock (Anthropic Claude)
with tool-use to autonomously detect work pattern anti-patterns in calendar
events and email threads, then generate ranked, explainable automation
proposals.

### Key Features

- **Genuine agentic workflow**: Bedrock tool-use loop where the LLM decides
  which analysis tools to call, in what order, and synthesises the results
- **8 analysis tools**: calendar load, back-to-back detection, recurring
  meeting analysis, focus-time estimation, stale email detection, FYI chain
  detection, email volume summary, cross-referencing
- **2 distinct scenarios**: Meeting-Heavy Manager and Context-Switching
  Developer — completely different personas with different anti-patterns
- **Streamlit standalone app**: Interactive UI for exploring data, watching
  agent reasoning, and approving/rejecting proposals
- **Complete audit trail**: JSONL log of every agent step, tool call, and
  decision
- **Deterministic fallback**: Works without AWS credentials via heuristic
  pipeline

## Architecture

```
Bedrock Agent (Claude via boto3 bedrock-runtime)
  ├─ Tool: scan_calendar_load
  ├─ Tool: scan_calendar_back_to_back
  ├─ Tool: scan_calendar_recurring
  ├─ Tool: scan_calendar_focus_time
  ├─ Tool: scan_email_stale
  ├─ Tool: scan_email_long_chains
  ├─ Tool: scan_email_volume
  └─ Tool: cross_reference
```

## Running

### Batch Mode (Reproducible Run)

The `/code/run` script executes both scenarios:
```bash
python /code/run.py --scenario all
```

### Interactive Mode (Cloud Workstation)

Launch a Streamlit cloud workstation. The app at `/code/streamlit_app.py`
provides:
- Scenario selection or custom JSON upload
- Real-time agent analysis
- Pattern and proposal exploration
- Interactive approval/rejection

## Expected Outputs

| File | Description |
|------|-------------|
| `scenarios/meeting_heavy_manager/habit_summary.json` | Detected patterns for Scenario 1 |
| `scenarios/meeting_heavy_manager/proposals.json` | Ranked proposals for Scenario 1 |
| `scenarios/meeting_heavy_manager/audit_log.jsonl` | Agent audit trail for Scenario 1 |
| `scenarios/context_switching_developer/habit_summary.json` | Detected patterns for Scenario 2 |
| `scenarios/context_switching_developer/proposals.json` | Ranked proposals for Scenario 2 |
| `scenarios/context_switching_developer/audit_log.jsonl` | Agent audit trail for Scenario 2 |
| `manifest.json` | Full capsule manifest |
| `IMPLEMENTATION_SUMMARY.md` | What was built and how |
| `VALIDATION_NOTES.md` | Honest assessment of completeness |

## Environment

- **Base**: Python 3.10 (CPU only)
- **Packages**: `boto3`, `pydantic`, `streamlit`
- **LLM Backend**: AWS Bedrock (Anthropic Claude) — no direct API calls
- **Fallback**: deterministic heuristic pipeline when Bedrock unavailable
