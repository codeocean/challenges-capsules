# AQUA PROMPT — Replicate Challenge 14: Segment Intestine Villi

> Copy this entire prompt and paste it to Aqua to have it fully recreate this capsule from scratch.

---

## Prompt

```
I need you to replicate the "Challenge 14: Segment Intestine Villi" capsule from the Allen Institute Hackathon. Follow these steps exactly:

### STEP 1: Create the capsule from GitHub
Create a new capsule by copying (not cloning) from the GitHub repository:
- Repository URL: https://github.com/codeocean/challenges-capsules
- After import, the code for this challenge is in the `challenge-14-segment-intestine-villi/` folder within the repo. Move all files from that subfolder to `/code/` so they are at the root of the capsule's code directory. Remove any other challenge folders that were imported.

### STEP 2: Set capsule metadata
- Name: "Challenge 14: Segment Intestine Villi"
- Description: "Segment individual intestinal villi from ileum Xenium spatial transcriptomics data by integrating spatial coordinates, gene expression gradients, and cell-type composition into biologically meaningful villus-scale boundaries with cell assignments and QC metrics."
- Tags: hackathon-challenge, spatial-transcriptomics, Xenium, image-segmentation, intestine, villi, immunology, computational-biology

### STEP 3: Configure the environment
- Starter environment: Python (codeocean/mambaforge3:22.11.1-4-ubuntu22.04) — Python 3.10
- Pip packages (install these exact versions):
  - anndata==0.11.4
  - igraph==1.0.0
  - leidenalg==0.11.0
  - matplotlib==3.10.8
  - numpy==2.2.6
  - pandas==2.3.3
  - scanpy==1.11.5
  - scikit-learn==1.7.2
  - scipy==1.15.3
  - squidpy==1.6.5

### STEP 4: Set compute resources
- Flex tier: Small (2 cores / 16 GB RAM)
- Machine type: CPU (general_purpose)

### STEP 5: Data assets
This capsule is self-contained. No data assets need to be attached.
It generates synthetic Xenium-like spatial transcriptomics data at runtime, simulating ileum tissue with epithelial cells organized into villus structures.

If you have real Xenium ileum data, attach it as a data asset mounted at /data/xenium_ileum/

### STEP 6: Verify the run script
The `/code/run` file should contain:
```bash
#!/usr/bin/env bash
set -euo pipefail
python /code/run.py "$@"
```

### STEP 7: Verify code structure
The capsule should have this key file in /code/:
- run.py — Complete pipeline: load/generate spatial data → score epithelial cells with marker genes (EPCAM, FABP1, FABP2, VIL1) → build spatial neighbor graph → Leiden clustering → output spatial map + assignments

### STEP 8: Run the capsule
Run the capsule. It should produce:
- spatial_plot.png (color-coded spatial map, each color = one villus cluster)
- villus_assignments.csv (cell_id, villus_cluster_id, is_epithelial, x, y)
- per_villus_summary.csv (villus_cluster_id, n_cells, etc.)

The key success criterion is visual: do the colored clusters correspond to individual villi-like structures?
```
