# AQUA PROMPT — Replicate Challenge 10: NeuroBase Foundation Model Evaluation

> Copy this entire prompt and paste it to Aqua to have it fully recreate this capsule from scratch.

---

## Prompt

```
I need you to replicate the "Challenge 10: NeuroBase Foundation Model Evaluation" capsule from the Allen Institute Hackathon. Follow these steps exactly:

### STEP 1: Create the capsule from GitHub
Create a new capsule by copying (not cloning) from the GitHub repository:
- Repository URL: https://github.com/codeocean/challenges-capsules
- After import, the code for this challenge is in the `challenge-10-neurobase-evaluation/` folder within the repo. Move all files from that subfolder to `/code/` so they are at the root of the capsule's code directory. Remove any other challenge folders that were imported.

### STEP 2: Set capsule metadata
- Name: "Challenge 10: NeuroBase Foundation Model Evaluation"
- Description: "Benchmark NeuroBase 3D neuroanatomical foundation model on Allen brain imaging data, comparing downstream task performance against conventional baselines to evaluate practical utility, runtime efficiency, and labeling cost trade-offs for neuroscience applications."
- Tags: hackathon-challenge, foundation-models, neuroimaging, 3D-imaging, benchmark, evaluation, STPT, brain-atlas

### STEP 3: Configure the environment
- Starter environment: PyTorch (codeocean/pytorch:2.4.0-cuda12.4.0-mambaforge24.5.0-0-python3.12.4-ubuntu22.04)
- Machine type: GPU
- Pip packages (install these exact versions):
  - matplotlib==3.10.8
  - numpy==2.4.4
  - pandas==3.0.1
  - pynrrd==1.1.3
  - requests==2.33.1
  - scikit-learn==1.8.0
  - torch==2.11.0

### STEP 4: Set compute resources
- Flex tier: X-Small (1 GPU / 16 GB GPU RAM / 4 cores / 15 GB RAM)
- Machine type: GPU

### STEP 5: Data assets
This capsule is self-contained. No data assets need to be attached.
It downloads real Allen CCFv3 data at runtime:
- Annotation volume (25 µm, ~4 MB compressed)
- Average template intensity volume (25 µm, ~33 MB compressed)
- Structure ontology JSON from Allen Brain Atlas API (1,327 structures)

Data is cached to /scratch/allen/ across runs for faster re-runs.

### STEP 6: Verify the run script
The `/code/run` file should contain:
```bash
#!/usr/bin/env bash
set -euo pipefail
python /code/run.py "$@"
```

### STEP 7: Verify code structure
The capsule should have this key file in /code/:
- run.py — Complete pipeline: download Allen data → build region mapping → extract patches → encode with 3 methods → train classifiers → evaluate → visualize

The pipeline compares three encoders:
1. Classical Features (28-dim: histogram + gradient + Laplacian + spatial)
2. Pretrained Proxy (64-dim: self-supervised rotation prediction CNN)
3. Random Baseline (64-dim: untrained CNN)

### STEP 8: Run the capsule
Run the capsule. Expected runtime ~15 minutes including data download. It should produce:
- summary.json (all metrics, resource profiling)
- dice_scores.csv (per-region Dice for all 3 encoders)
- evaluation_report.md (full narrative report)
- opportunity_analysis.json (per-region best encoder assessment)
- dice_barplot.png, confusion_matrix.png
- overlay_coronal.png, overlay_sagittal.png, overlay_horizontal.png
- embeddings/*.npy (saved embeddings for reuse)
- scope.md, failures.md
```
