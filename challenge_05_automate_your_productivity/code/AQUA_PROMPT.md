# AQUA PROMPT — Replicate Challenge 05: Automate Your Productivity

> Copy this entire prompt and paste it to Aqua to have it fully recreate this capsule from scratch.

---

## Prompt

```
I need you to replicate the "Challenge 05: Automate Your Productivity" capsule from the Allen Institute Hackathon. Follow these steps exactly:

### STEP 1: Create the capsule from GitHub
Create a new capsule by copying (not cloning) from the GitHub repository:
- Repository URL: https://github.com/codeocean/challenges-capsules
- After import, the code for this challenge is in the `challenge-05-automate-your-productivity/` folder within the repo. Move all files from that subfolder to `/code/` so they are at the root of the capsule's code directory. Remove any other challenge folders that were imported.

### STEP 2: Set capsule metadata
- Name: "Challenge 05: Automate Your Productivity"
- Description: "Analyze Microsoft 365 behavioral data to build a trustworthy productivity agent that detects work patterns, proposes reversible automations with human approval, maintains audit logs, and demonstrates safe AI-assisted workflow optimization."
- Tags: hackathon-challenge, productivity, automation, microsoft-365, ai-agent, workflow-optimization, copilot, enterprise-AI

### STEP 3: Configure the environment
- Starter environment: Python (codeocean/mambaforge3:22.11.1-4-ubuntu22.04) — Python 3.10
- Pip packages (install these exact versions):
  - boto3==1.42.77
  - pydantic==2.12.5
  - streamlit==1.55.0

### STEP 4: Set compute resources
- Flex tier: Small (2 cores / 16 GB RAM)
- Machine type: CPU (general_purpose)

### STEP 5: Data assets
This capsule is fully self-contained. No data assets need to be attached.
It generates synthetic Microsoft 365 calendar events and email threads for two personas at runtime via scenarios.py.

### STEP 6: Verify the run script
The `/code/run` file should contain:
```bash
#!/usr/bin/env bash
set -euo pipefail
python /code/run.py "$@"
```

### STEP 7: Verify code structure
The capsule should have these key files in /code/:
- run.py — Main orchestrator (--scenario all runs both personas)
- bedrock_agent.py — AWS Bedrock Claude tool-use agent with 8 analysis tools
- scenarios.py — Synthetic scenario generator (Meeting-Heavy Manager, Context-Switching Developer)
- tools.py — Analysis tool implementations (calendar scanning, email analysis, cross-referencing)
- streamlit_app.py — Interactive Streamlit UI for cloud workstation mode

### STEP 8: Run the capsule
Run the capsule. It should produce per-scenario outputs in /results/:
- scenarios/meeting_heavy_manager/habit_summary.json, proposals.json, audit_log.jsonl
- scenarios/context_switching_developer/habit_summary.json, proposals.json, audit_log.jsonl
- manifest.json
- IMPLEMENTATION_SUMMARY.md
- VALIDATION_NOTES.md

Note: If AWS Bedrock credentials are unavailable, the capsule falls back to a deterministic heuristic pipeline.
```
