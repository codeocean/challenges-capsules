# AQUA PROMPT — Replicate Challenge 16: SciDEX — Scientific Discovery Exchange

> Copy this entire prompt and paste it to Aqua to have it fully recreate this capsule from scratch.

---

## Prompt

```
I need you to replicate the "Challenge 16: SciDEX — Scientific Discovery Exchange" capsule from the Allen Institute Hackathon. Follow these steps exactly:

### STEP 1: Create the capsule from GitHub
Create a new capsule by copying (not cloning) from the GitHub repository:
- Repository URL: https://github.com/codeocean/challenges-capsules
- After import, the code for this challenge is in the `challenge-16-scidex/` folder within the repo. Move all files from that subfolder to `/code/` so they are at the root of the capsule's code directory. Remove any other challenge folders that were imported.

### STEP 2: Set capsule metadata
- Name: "Challenge 16: SciDEX — Scientific Discovery Exchange"
- Description: "Prototype a persistent hypothesis workbench where AI agents generate testable hypotheses from Allen data and literature, critique reasoning, link evidence, and maintain decision history across sessions for reproducible scientific discovery workflows."
- Tags: hackathon-challenge, hypothesis-generation, scientific-discovery, AI-agents, literature-mining, Allen-data, evidence-grounding, knowledge-work

### STEP 3: Configure the environment
- Starter environment: Python (codeocean/mambaforge3:22.11.1-4-ubuntu22.04) — Python 3.10
- Pip packages (install these exact versions):
  - boto3==1.42.77
  - numpy==2.2.6
  - pandas==2.3.3
  - pydantic==2.12.5
  - requests==2.33.0
  - tqdm==4.67.3

### STEP 4: Set compute resources
- Flex tier: Small (2 cores / 16 GB RAM)
- Machine type: CPU (general_purpose)

### STEP 5: Data assets
This capsule is self-contained. No data assets need to be attached.
It generates a synthetic research question, ~50 paper abstracts, and simulated human review decisions at runtime.

### STEP 6: Verify the run script
The `/code/run` file should contain:
```bash
#!/usr/bin/env bash
set -euo pipefail
python /code/run.py
python /code/run_session2.py
```
IMPORTANT: This capsule runs TWO sessions sequentially. Session 1 generates hypotheses, Session 2 loads prior state and refines based on human decisions.

### STEP 7: Verify code structure
The capsule should have these key files in /code/:
- run.py — Session 1: load question + papers → generate hypotheses → critique → save to SQLite
- run_session2.py — Session 2: load prior state → apply human decisions → refine hypotheses → save updated state
- schemas.py — Pydantic models for hypothesis, evidence, and decision structures

### STEP 8: Run the capsule
Run the capsule. It should produce:
- session_001_hypotheses.jsonl (generated hypotheses with evidence citations and AI critique)
- session_002_hypotheses.jsonl (refined hypotheses after simulated human feedback)
- session_state.db (SQLite with full persistent state and decision history)
- evidence.jsonl (extracted evidence records linked to papers)

The key success criterion: diff session 1 vs session 2 — the system should demonstrably remember and build on prior decisions.

Note: Requires AWS Bedrock credentials for hypothesis generation via Claude.
```
