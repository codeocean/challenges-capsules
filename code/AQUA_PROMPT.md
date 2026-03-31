# AQUA PROMPT — Replicate Challenge 09: BindCrafting

> Copy this entire prompt and paste it to Aqua to have it fully recreate this capsule from scratch.

---

## Prompt

```
I need you to replicate the "Challenge 09: BindCrafting" capsule from the Allen Institute Hackathon. Follow these steps exactly:

### STEP 1: Create the capsule from GitHub
Create a new capsule by copying (not cloning) from the GitHub repository:
- Repository URL: https://github.com/codeocean/challenges-capsules
- After import, the code for this challenge is in the `challenge-09-bindcrafting/` folder within the repo. Move all files from that subfolder to `/code/` so they are at the root of the capsule's code directory. Remove any other challenge folders that were imported.

### STEP 2: Set capsule metadata
- Name: "Challenge 09: BindCrafting"
- Description: "Design protein binders using BindCraft and AlphaFold2 for target proteins, generating fluorescent-compatible affinity reagents with computational design, structural validation, and ranked diverse candidates for experimental testing as antibody alternatives."
- Tags: hackathon-challenge, protein-design, BindCraft, AlphaFold2, binder-design, structural-biology, computational-biology, neural-dynamics

### STEP 3: Configure the environment
- Starter environment: PyTorch (codeocean/pytorch:2.4.0-cuda12.4.0-mambaforge24.5.0-0-python3.12.4-ubuntu22.04)
- Machine type: GPU
- Pip packages (install these exact versions):
  - biopython==1.86
  - boto3==1.42.77
  - matplotlib==3.10.8
  - numpy==2.4.3
  - pandas==3.0.1

### STEP 4: Set compute resources
- Flex tier: X-Small (1 GPU / 16 GB GPU RAM / 4 cores / 15 GB RAM)
- Machine type: GPU

### STEP 5: Data assets
This capsule is self-contained. No data assets need to be attached.
It generates synthetic BindCraft design trajectories (200 candidates) and PDB structures at runtime via generate_data.py.

### STEP 6: Verify the run script
The `/code/run` file should contain:
```bash
#!/usr/bin/env bash
set -euo pipefail
python /code/run.py "$@"
```

### STEP 7: Verify code structure
The capsule should have these key files in /code/:
- run.py — Main pipeline: generate data → filter → rank → fusion check → agent analysis → visualize
- generate_data.py — Synthetic BindCraft output generator (200 trajectories + PDB files)
- bedrock_agent.py — AWS Bedrock Claude integration for scientific interpretation
- visualize.py — Score scatter, fusion distances, filtering funnel charts

### STEP 8: Run the capsule
Run the capsule. It should produce:
- ranked_candidates.csv (top 5 candidates with metrics)
- fusion_compatibility.json (per-candidate terminus distances)
- filtering_funnel.json (design attrition through filter stages)
- agent_analysis.md (AI-generated scientific interpretation)
- top5_visualizations/ (charts and plots)
- manifest.json, IMPLEMENTATION_SUMMARY.md, VALIDATION_NOTES.md

Note: Uses AWS Bedrock for agentic analysis. Falls back to deterministic local analysis if Bedrock unavailable.
```
