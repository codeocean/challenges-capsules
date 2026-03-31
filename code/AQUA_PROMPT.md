# AQUA PROMPT — Replicate Challenge 03: Enhancer Designer

> Copy this entire prompt and paste it to Aqua to have it fully recreate this capsule from scratch.

---

## Prompt

```
I need you to replicate the "Challenge 03: Enhancer Designer" capsule from the Allen Institute Hackathon. Follow these steps exactly:

### STEP 1: Create the capsule from GitHub
Create a new capsule by copying (not cloning) from the GitHub repository:
- Repository URL: https://github.com/codeocean/challenges-capsules
- After import, the code for this challenge is in the `challenge-03-enhancer-designer/` folder within the repo. Move all files from that subfolder to `/code/` so they are at the root of the capsule's code directory. Remove any other challenge folders that were imported.

### STEP 2: Set capsule metadata
- Name: "Challenge 03: Enhancer Designer"
- Description: "Generate synthetic enhancer-like DNA sequences for K562 cells using computational design loops with in silico oracles (DeepSTARR, ChromBPNet, Enformer), demonstrating reproducible enhancer design with scoring, filtering, and diversity selection for experimental validation."
- Tags: hackathon-challenge, enhancer-design, synthetic-biology, deep-learning, genomics, K562, regulatory-elements, DNA-design

### STEP 3: Configure the environment
- Starter environment: Python (codeocean/mambaforge3:22.11.1-4-ubuntu22.04) — Python 3.10
- Pip packages (install these exact versions):
  - biopython==1.86
  - matplotlib==3.10.8
  - numpy==2.2.6
  - scipy==1.15.3
  - torch==2.11.0

### STEP 4: Set compute resources
- Flex tier: Small (2 cores / 16 GB RAM)
- Machine type: CPU (general_purpose)

### STEP 5: Data assets
This capsule is fully self-contained. No data assets need to be attached.
It generates synthetic K562-like seed sequences with embedded TF motifs at runtime.

Optional: If you have real K562 ATAC-seq peaks, attach as a data asset at /data/k562_peaks.fasta

### STEP 6: Verify the run script
The `/code/run` file should contain:
```bash
#!/usr/bin/env bash
set -euo pipefail
python /code/run.py "$@"
```

### STEP 7: Verify code structure
The capsule should have these key files in /code/:
- run.py — Main orchestrator with argparse
- generate.py — Seeds, genetic algorithm, Euler shuffle, filters, diversity selection
- score.py — PWM scanning, cooperativity model, scoring engine
- report.py — 6-panel figure, stats JSON, FASTA output, manifest

### STEP 8: Run the capsule
Run the capsule. It should produce:
- enhancer_report.png (6-panel visualization)
- stats.json (statistical evaluation)
- top20.fasta (top 20 diverse enhancer candidates)
- run_manifest.yaml (reproducibility record)
```
