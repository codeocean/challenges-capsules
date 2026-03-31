# AQUA PROMPT — Replicate Challenge 02: Agentic Data Harmonization

> Copy this entire prompt and paste it to Aqua to have it fully recreate this capsule from scratch.

---

## Prompt

```
I need you to replicate the "Challenge 02: Agentic Data Harmonization" capsule from the Allen Institute Hackathon. Follow these steps exactly:

### STEP 1: Create the capsule from GitHub
Create a new capsule by copying (not cloning) from the GitHub repository:
- Repository URL: https://github.com/codeocean/challenges-capsules
- After import, the code for this challenge is in the `challenge-02-agentic-data-harmonization/` folder within the repo. Move all files from that subfolder to `/code/` so they are at the root of the capsule's code directory. Remove any other challenge folders that were imported.

### STEP 2: Set capsule metadata
- Name: "Challenge 02: Agentic Data Harmonization"
- Description: "Build an AI agent system that harmonizes Allen Institute single-cell datasets by inferring and aligning cell type mappings across studies with different taxonomies, demonstrating autonomous schema reconciliation, quality validation, and transparent decision-making in biological data integration."
- Tags: hackathon-challenge, agentic-AI, data-harmonization, single-cell, cell-type-mapping, schema-alignment, bioinformatics, ABC-Atlas

### STEP 3: Configure the environment
- Starter environment: Python (codeocean/mambaforge3:22.11.1-4-ubuntu22.04) — Python 3.10
- Pip packages (install these exact versions):
  - boto3==1.42.78
  - pandas==2.3.3
  - pronto==2.7.3
  - rapidfuzz==3.14.3
  - requests==2.33.1
  - strands-agents==1.33.0
  - strands-agents-tools==0.3.0

### STEP 4: Set compute resources
- Flex tier: Small (2 cores / 16 GB RAM)
- Machine type: CPU (general_purpose)

### STEP 5: Data assets
This capsule is self-contained — it generates/downloads its own data at runtime (Cell Ontology OBO, WHB taxonomy, CELLxGENE brain data). No data assets need to be attached.

However, if you want to use the original challenge data assets, search for and attach:
- "challenge_02_input" mounted at /data/challenge_02_input
- "WHB-taxonomy" mounted at /data/WHB-taxonomy  
- "cellxgene_brain" mounted at /data/cellxgene_brain

### STEP 6: Verify the run script
The `/code/run` file should contain:
```bash
#!/usr/bin/env bash
set -euo pipefail
python /code/run.py "$@"
```

### STEP 7: Run the capsule
Run the capsule. It should produce:
- mapping_table.csv (full mapping table)
- eval_report.json (WHB evaluation metrics)
- cellxgene_eval_report.json (CELLxGENE evaluation metrics)
- provenance.jsonl (decision audit trail)
- review_queue.json (labels needing human review)
```
