# AQUA PROMPT — Replicate Challenge 12: Brain Map + BKP Assistant

> Copy this entire prompt and paste it to Aqua to have it fully recreate this capsule from scratch.

---

## Prompt

```
I need you to replicate the "Challenge 12: Brain Map + BKP Assistant" capsule from the Allen Institute Hackathon. Follow these steps exactly:

### STEP 1: Create the capsule from GitHub
Create a new capsule by copying (not cloning) from the GitHub repository:
- Repository URL: https://github.com/codeocean/challenges-capsules
- After import, the code for this challenge is in the `challenge-12-brain-map-bkp-assistant/` folder within the repo. Move all files from that subfolder to `/code/` so they are at the root of the capsule's code directory. Remove any other challenge folders that were imported.

### STEP 2: Set capsule metadata
- Name: "Challenge 12: Brain Map + BKP Assistant"
- Description: "Build a grounded discovery assistant over brain-map and Brain Knowledge Platform content that finds resources, explains matches, handles deprecated content, and evaluates cross-product retrieval quality for Allen neuroscience tools and datasets."
- Tags: hackathon-challenge, knowledge-assistant, brain-map, BKP, product-discovery, RAG, documentation-search, neuroscience

### STEP 3: Configure the environment
- Starter environment: Python (codeocean/mambaforge3:22.11.1-4-ubuntu22.04) — Python 3.10
- Pip packages (install these exact versions):
  - boto3==1.42.78
  - faiss-cpu==1.13.2
  - numpy==2.2.6
  - pandas==2.3.3
  - pydantic==2.12.5
  - scikit-learn==1.7.2
  - sentence-transformers==5.3.0

### STEP 4: Set compute resources
- Flex tier: Small (2 cores / 16 GB RAM)
- Machine type: CPU (general_purpose)

### STEP 5: Data assets
This capsule is self-contained. No data assets need to be attached.
It pre-curates ~100 Allen Institute web pages as JSONL and builds a FAISS index at runtime.

### STEP 6: Verify the run script
The `/code/run` file should contain:
```bash
#!/usr/bin/env bash
set -euo pipefail
python /code/run.py "$@"
```

### STEP 7: Verify code structure
The capsule should have these key files in /code/:
- run.py — Main pipeline: curate corpus → embed with sentence-transformers → build FAISS index → RAG retrieval → answer generation
- build_index.py — FAISS index construction from document embeddings
- evaluate.py — Top-5 retrieval accuracy evaluation against gold-standard queries

### STEP 8: Run the capsule
Run the capsule. It should produce:
- answers.jsonl (per-query grounded answers with cited URLs and deprecation warnings)
- evaluation_report.json (top-5 accuracy, citation precision)

Note: Requires AWS Bedrock credentials for answer generation via Claude.
```
