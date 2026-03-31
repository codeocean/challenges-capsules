# How to Implement: NeuroBase Foundation Model Evaluation — For Your Own Data

> **Goal**: Benchmark 3D neuroimaging foundation models on *your* brain imaging
> data, comparing downstream task performance (region classification, segmentation)
> against classical baselines and random-weight controls.

---

## 1. What You Need (Your Data)

### Input Data Format

| Input | Format | Description |
|-------|--------|-------------|
| **3D image volume** | NIfTI (`.nii.gz`) or NRRD (`.nrrd`) | Your brain imaging data (MRI, STPT, light-sheet, etc.) |
| **Annotation volume** | NIfTI or NRRD (same dimensions) | Region labels / segmentation ground truth |
| **Region ontology** (optional) | JSON or CSV | Mapping from annotation IDs to region names and hierarchy |
| **Model weights** (optional) | PyTorch checkpoint (`.pt`) | Pre-trained foundation model to evaluate |

### What Your Data Should Look Like

```
my_neuro_data/
├── brain_template.nrrd        # 3D intensity volume (e.g., 25µm Allen CCFv3)
├── brain_annotations.nrrd     # 3D annotation volume (integer region IDs)
├── region_ontology.json       # Optional: ID → region name mapping
└── model_weights/             # Optional: your foundation model checkpoint
    └── neurobase_v1.pt
```

**Key requirements:**
- Image and annotation volumes must be co-registered (same voxel space and dimensions)
- Annotation volume: integer values where each integer = a brain region
- Voxel size: 10–100 µm typical for mouse brain; any resolution supported
- Minimum ~100 patches extractable (volume at least ~128³ voxels)

**Region ontology format:**
```json
// region_ontology.json
{
  "1": {"name": "Isocortex", "parent": "Cerebrum"},
  "2": {"name": "Hippocampal formation", "parent": "Cerebrum"},
  "3": {"name": "Cerebellum", "parent": "Hindbrain"},
  ...
}
```

---

## 2. Step-by-Step: Recreate This Capsule with Aqua

### Step 1: Create a New Capsule

> **Ask Aqua:**
> *"Create a new capsule called 'Foundation Model Benchmark — [My Brain Data]' with PyTorch 2.4 base image, and install packages: numpy, pandas, scikit-learn, matplotlib, pynrrd, nibabel, requests, torch"*

### Step 2: Prepare Your Data

**Option A: Use Allen CCFv3 (automatic download)**
The capsule can download Allen Brain Atlas data at runtime — no data asset needed.

> **Ask Aqua:**
> *"Keep the Allen CCFv3 auto-download. I want to evaluate on the standard mouse brain atlas."*

**Option B: Bring your own brain data**

> **Ask Aqua:**
> *"Create a data asset called 'my-brain-volumes' with my NIfTI/NRRD volumes, then attach it at /data/brain_data"*

### Step 3: Configure the Benchmark

> **Ask Aqua:**
> *"Modify run.py to load my volumes from /data/brain_data/. Set patch size to 32³, stride to 24, and map my annotation IDs to [list your major regions] using my region ontology."*

### Step 4: Add Your Model (optional)

> **Ask Aqua:**
> *"Mount my model weights at /data/model_weights/. Add a custom encoder that loads my checkpoint and extracts 64-dim embeddings from 32³ patches."*

If you don't have a model yet, the pipeline evaluates:
- **Classical features**: Histogram + gradient + Laplacian (28-dim, no training needed)
- **Self-supervised proxy**: Rotation-prediction pretrained CNN (64-dim)
- **Random baseline**: Untrained CNN (64-dim)

### Step 5: Run

> **Ask Aqua:**
> *"Run my capsule"*

---

## 3. Outputs You'll Get

| File | What It Contains |
|------|-----------------|
| `summary.json` | All metrics, resource profiling, conclusion |
| `dice_scores.csv` | Per-region Dice scores for all encoders |
| `evaluation_report.md` | Narrative evaluation report |
| `dice_barplot.png` | Per-region comparison bar chart |
| `confusion_matrix.png` | Best encoder confusion matrix |
| `overlay_*.png` | Brain slice annotation overlays (coronal, sagittal, horizontal) |
| `embeddings/*.npy` | Saved embeddings for reuse |

---

## 4. Adapting for Different Use Cases

### Use Case A: Human brain MRI (not mouse)
Replace the Allen CCFv3 with your human brain atlas.

> **Ask Aqua:**
> *"Adapt for human brain MRI at 1mm resolution. Load my FreeSurfer parcellation as the annotation volume. Map Desikan-Killiany regions to 8 major lobes."*

### Use Case B: Cell-level 3D segmentation (not brain regions)
Evaluate on cell detection/segmentation tasks.

> **Ask Aqua:**
> *"Modify the downstream task from region classification to cell detection. Each patch should predict cell count or cell type instead of brain region."*

### Use Case C: Compare multiple foundation models
Add more encoder options to the benchmark.

> **Ask Aqua:**
> *"Add a fourth encoder for my second model checkpoint at /data/model_v2.pt. Run all four encoders in the same benchmark and add to the comparison plots."*

---

## 5. Tips

- **Patch size matters**: 32³ is good for 25µm mouse brain; adjust for your resolution
- **Stratified splits**: Ensure every region appears in both train and test sets
- **Classical baseline first**: If classical features beat your model, the model may not be learning useful representations
- **Caching**: Allen CCFv3 data is cached to `/scratch/allen/` across runs
- **Reproducibility**: Set random seed (default 42) for deterministic results
- **Memory**: ~5 GB peak RAM for Allen CCFv3 at 25µm; plan accordingly for larger volumes

---

## 6. Environment Requirements

| Package | Purpose |
|---------|---------|
| `torch` | Neural network encoders |
| `numpy` | Array operations |
| `pandas` | Metrics tabulation |
| `scikit-learn` | Logistic regression classifier, cross-validation |
| `matplotlib` | Visualization |
| `pynrrd` | NRRD file I/O |
| `nibabel` | NIfTI file I/O (if using `.nii.gz`) |
| `requests` | Allen API/data download |

**Compute**: CPU sufficient for standard benchmark; GPU recommended for large volumes or many encoders
**Runtime**: ~15 min including data download; ~2 min with cached data
