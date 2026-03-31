# AQUA PROMPT — Replicate Challenge 04: Light Sheet Alignment QC

> Copy this entire prompt and paste it to Aqua to have it fully recreate this capsule from scratch.

---

## Prompt

```
I need you to replicate the "Challenge 04: Light Sheet Alignment QC" capsule from the Allen Institute Hackathon. Follow these steps exactly:

### STEP 1: Create the capsule from GitHub
Create a new capsule by copying (not cloning) from the GitHub repository:
- Repository URL: https://github.com/codeocean/challenges-capsules
- After import, the code for this challenge is in the `challenge-04-light-sheet-alignment-qc/` folder within the repo. Move all files from that subfolder to `/code/` so they are at the root of the capsule's code directory. Remove any other challenge folders that were imported.

### STEP 2: Set capsule metadata
- Name: "Challenge 04: Light Sheet Alignment QC"
- Description: "Build a quality control system for light-sheet microscopy image registration that automatically detects alignment failures, routes uncertain cases to human review, and outperforms baseline metrics, ensuring reliable downstream neuroanatomical analysis."
- Tags: hackathon-challenge, image-processing, quality-control, light-sheet-microscopy, image-alignment, neural-dynamics, computer-vision, registration-QC

### STEP 3: Configure the environment
- Starter environment: Python (codeocean/mambaforge3:22.11.1-4-ubuntu22.04) — Python 3.10
- Pip packages (install these exact versions):
  - matplotlib==3.10.8
  - numpy==2.2.6
  - pandas==2.3.3
  - scikit-image==0.25.2
  - scikit-learn==1.7.2
  - scipy==1.15.3
  - tifffile==2025.5.10

### STEP 4: Set compute resources
- Flex tier: Small (2 cores / 16 GB RAM)
- Machine type: CPU (general_purpose)

### STEP 5: Data assets
This capsule is fully self-contained. No data assets need to be attached.
It generates 250 synthetic tile pairs with controlled perturbations at runtime via generate_pairs.py.

### STEP 6: Verify the run script
The `/code/run` file should contain:
```bash
#!/usr/bin/env bash
set -euo pipefail
python /code/run.py "$@"
```

### STEP 7: Verify code structure
The capsule should have these key files in /code/:
- run.py — Main pipeline: feature extraction → GradientBoosting classifier → evaluation
- generate_pairs.py — Synthetic tile pair generator (10 tissue types, 6 perturbation types, 4 severities)
- visualize.py — HTML report + QC overlay montages + performance plots

### STEP 8: Run the capsule
Run the capsule. Expected runtime ~55 seconds on CPU. It should produce:
- evaluation_report.html (comprehensive HTML report)
- predictions.csv (per-pair scores and predictions)
- metrics.json (ROC-AUC ≥0.90, PR-AUC ≥0.85)
- roc_curve.png, pr_curve.png, confusion_matrix.png, and other visualization files
- figures/ directory with QC overlay montages
```
