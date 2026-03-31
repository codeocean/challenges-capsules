# AQUA PROMPT — Replicate Challenge 11: ABC Atlas Literature Assistant

> Copy this entire prompt and paste it to Aqua to have it fully recreate this capsule from scratch.

---

## Prompt

```
I need you to replicate the "Challenge 11: ABC Atlas Literature Assistant" capsule from the Allen Institute Hackathon. Follow these steps exactly:

### STEP 1: Create the capsule from GitHub
Create a new capsule by copying (not cloning) from the GitHub repository:
- Repository URL: https://github.com/codeocean/challenges-capsules
- After import, the code for this challenge is in the `challenge-11-abc-atlas-literature-assistant/` folder within the repo. Move all files from that subfolder to `/code/` so they are at the root of the capsule's code directory. Remove any other challenge folders that were imported.

### STEP 2: Set capsule metadata
- Name: "Challenge 11: ABC Atlas Literature Assistant"
- Description: "Expand ABC Atlas with a literature agent that contextualizes atlas data within published research, distinguishing source papers from reuse/validation studies with passage-level evidence and explicit relationship labeling for dataset-aware scientific discovery."
- Tags: hackathon-challenge, literature-mining, ABC-Atlas, RAG, scientific-search, cell-types, evidence-grounding, knowledge-graph

### STEP 3: Configure the environment
- Starter environment: Python (codeocean/mambaforge3:22.11.1-4-ubuntu22.04) — Python 3.10
- Pip packages (install these exact versions):
  - biopython==1.87
  - boto3==1.42.79
  - numpy==2.2.6
  - pandas==2.3.3
  - rapidfuzz==3.14.3
  - requests==2.33.1
  - scikit-learn==1.7.2
  - tqdm==4.67.3

### STEP 4: Set compute resources
- Flex tier: Small (2 cores / 16 GB RAM)
- Machine type: CPU (general_purpose)

### STEP 5: Data assets
This capsule is self-contained. No data assets need to be attached.
It pre-stages ~100 papers as JSONL and generates embeddings at runtime.

### STEP 6: Verify the run script
The `/code/run` file should contain:
```bash
#!/usr/bin/env bash
set -euo pipefail
python /code/run.py "$@"
```

### STEP 7: Verify code structure
The capsule should have these key files in /code/:
- run.py — Main pipeline: stage papers → embed → run 5 queries → classify relationships → evaluate

### STEP 8: Run the capsule
Run the capsule. It should produce:
- demo_outputs.json (per-query answer with citations and relationship labels: SOURCE/REUSE/VALIDATION/MENTION)
- eval_report.json (citation verification stats)

Note: Requires AWS Bedrock credentials for LLM-powered classification.
```
