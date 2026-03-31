# AQUA PROMPT — Replicate Challenge 06: Plasmid Forge

> Copy this entire prompt and paste it to Aqua to have it fully recreate this capsule from scratch.

---

## Prompt

```
I need you to replicate the "Challenge 06: Plasmid Forge" capsule from the Allen Institute Hackathon. Follow these steps exactly:

### STEP 1: Create the capsule from GitHub
Create a new capsule by copying (not cloning) from the GitHub repository:
- Repository URL: https://github.com/codeocean/challenges-capsules
- After import, the code for this challenge is in the `challenge-06-plasmid-forge/` folder within the repo. Move all files from that subfolder to `/code/` so they are at the root of the capsule's code directory. Remove any other challenge folders that were imported.

### STEP 2: Set capsule metadata
- Name: "Challenge 06: Plasmid Forge"
- Description: "Build a natural-language-to-plasmid design workflow that converts biological requests into synthesis-ready constructs with Gibson Assembly, part retrieval from registries, validation checks, safety screening, and complete documentation for E. coli expression systems."
- Tags: hackathon-challenge, plasmid-design, synthetic-biology, molecular-cloning, Gibson-assembly, bioinformatics, automation, genetic-engineering

### STEP 3: Configure the environment
- Starter environment: Python (codeocean/mambaforge3:22.11.1-4-ubuntu22.04) — Python 3.10
- Pip packages (install these exact versions):
  - biopython==1.86
  - boto3==1.42.77
  - pydantic==2.12.5
  - pydna==5.5.8

### STEP 4: Set compute resources
- Flex tier: Small (2 cores / 16 GB RAM)
- Machine type: CPU (general_purpose)

### STEP 5: Data assets
This capsule is self-contained. No data assets need to be attached.
The code generates a curated parts library (~20 GenBank parts) and backbone vectors at runtime via create_data.py.

### STEP 6: Verify the run script
The `/code/run` file should contain:
```bash
#!/usr/bin/env bash
set -euo pipefail
python /code/run.py "$@"
```

IMPORTANT: There is also a `/code/run_cc` file which is the Claude Code orchestration entrypoint — this is NOT the standard run script. The standard `/code/run` is the one that executes the pipeline.

### STEP 7: Verify code structure
The capsule should have these key files in /code/:
- run.py — Main pipeline: parse request → select parts → assemble plasmid → validate → output
- create_data.py — Generates synthetic parts library and backbone vectors

### STEP 8: Run the capsule
Run the capsule. It should produce:
- construct.gb (annotated circular plasmid GenBank file)
- manifest.json (every assumption: parts selected, alternatives, rationale)
- protocol.md (Gibson Assembly protocol with primer sequences)
```
