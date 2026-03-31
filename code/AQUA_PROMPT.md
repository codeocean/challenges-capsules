# AQUA PROMPT — Replicate Challenge 08: Query BFF

> Copy this entire prompt and paste it to Aqua to have it fully recreate this capsule from scratch.

---

## Prompt

```
I need you to replicate the "Challenge 08: Query BFF — Natural Language Search for BioFileFinder Metadata" capsule from the Allen Institute Hackathon. Follow these steps exactly:

### STEP 1: Create the capsule from GitHub
Create a new capsule by copying (not cloning) from the GitHub repository:
- Repository URL: https://github.com/codeocean/challenges-capsules
- After import, the code for this challenge is in the `challenge-08-query-bff/` folder within the repo. Move all files from that subfolder to `/code/` so they are at the root of the capsule's code directory. Remove any other challenge folders that were imported.

### STEP 2: Set capsule metadata
- Name: "Query BFF: Natural Language Search for BioFileFinder Metadata"
- Description: "Natural language query interface for BioFileFinder (BFF) cell imaging metadata from the Allen Cell Collection. Translates plain-English researcher questions into validated, schema-grounded filters using AWS Bedrock (Claude Sonnet). Includes data fetcher that downloads real Allen Cell metadata from the public s3://allencell bucket."
- Tags: hackathon-challenge, BioFileFinder, natural-language-query, metadata-search, Allen-Cell-Collection, schema-grounding, bioinformatics, LLM, cell-biology, Bedrock

### STEP 3: Configure the environment
- Starter environment: Python (codeocean/mambaforge3:22.11.1-4-ubuntu22.04) — Python 3.10
- Pip packages (install these exact versions):
  - boto3==1.42.77
  - numpy==2.2.6
  - pandas==2.3.3
  - pyarrow==23.0.1
  - pydantic==2.12.5

### STEP 4: Set compute resources
- Flex tier: Small (2 cores / 16 GB RAM)
- Machine type: CPU (general_purpose)

### STEP 5: Data assets
This capsule is self-contained. No data assets need to be attached.
It includes a data fetcher (fetch_bff_data.py) that downloads real Allen Cell metadata from the public s3://allencell bucket at runtime, or generates synthetic BFF-compatible manifests if download fails.

### STEP 6: Verify the run script
The `/code/run` file should contain:
```bash
#!/usr/bin/env bash
set -euo pipefail
python /code/run.py "$@"
```

### STEP 7: Verify code structure
The capsule should have these key files in /code/:
- run.py — Main pipeline: schema extraction → NL-to-filter translation → execution → evaluation
- fetch_bff_data.py — Downloads real Allen Cell metadata from public S3

### STEP 8: Two run modes
Mode 1 — Single query (pass --query parameter):
  Run with: --query "Show me lamin B1 images"
  Produces: /results/query_answer.json

Mode 2 — Evaluation (no --query parameter):
  Run without parameters to execute all 15 gold-standard evaluation queries
  Produces: /results/evaluation_report.json with precision/recall/F1 metrics

### STEP 9: Run the capsule
Run the capsule in evaluation mode (no parameters). It should produce:
- evaluation_report.json (per-query results and aggregate success rate)
- extracted_schema.json (auto-detected manifest schema)

Note: Requires AWS Bedrock credentials for Claude Sonnet via the Converse API.
```
