# How to Implement: Light Sheet Alignment QC — For Your Own Data

> **Goal**: Build a quality control system that automatically detects alignment
> failures in *your* microscopy image registrations, routes uncertain cases to
> human review, and provides confidence-calibrated predictions.

---

## 1. What You Need (Your Data)

### Input Data Format

| Input | Format | Description |
|-------|--------|-------------|
| **Registered image pairs** | TIFF or PNG tiles | Pairs of images that should be aligned (e.g., adjacent tiles, channels, timepoints) |
| **Ground truth labels** (for training) | CSV: `pair_id, is_aligned (0/1)` | Manual annotations of pass/fail for training the classifier |
| **Tissue type metadata** (optional) | Column in CSV | Helps stratify evaluation (e.g., dense, sparse, border, empty) |

### What Your Data Should Look Like

```
my_qc_data/
├── tile_pairs/
│   ├── pair_001_left.tif
│   ├── pair_001_right.tif
│   ├── pair_002_left.tif
│   ├── pair_002_right.tif
│   └── ...
├── labels.csv
│   # pair_id,is_aligned,tissue_type,severity
│   # pair_001,1,dense,
│   # pair_002,0,border,moderate
│   # pair_003,1,sparse,
└── metadata.json   # optional: imaging parameters
```

**Key requirements:**
- Image pairs must be the same dimensions
- Labels: `1` = properly aligned, `0` = misaligned
- At least 100 labeled pairs recommended for training (50+ per class)
- 16-bit or 8-bit TIFF/PNG supported

---

## 2. Step-by-Step: Recreate This Capsule with Aqua

### Step 1: Create a New Capsule

> **Ask Aqua:**
> *"Create a new capsule called 'Image Registration QC — [My Microscope/Project]' with Python 3.10, and install packages: scikit-image, scikit-learn, numpy, matplotlib, tifffile, pandas, scipy"*

### Step 2: Prepare Your Data

**Option A: You have labeled data (recommended)**
Upload your image pairs + labels as a data asset.

> **Ask Aqua:**
> *"Create a data asset called 'my-registration-qc-data' with my labeled image pairs, then attach it to my capsule at /data/qc_pairs"*

**Option B: You want to start with synthetic data (for prototyping)**
The capsule can generate synthetic pairs with controlled perturbations.

> **Ask Aqua:**
> *"Keep the synthetic data generator but configure it for my image characteristics: [image size, typical intensity range, tissue density patterns]"*

### Step 3: Adapt the Feature Extraction

The pipeline extracts 7 features per image pair:

| Feature | What It Measures |
|---------|-----------------|
| SSIM | Structural similarity |
| NCC | Normalized cross-correlation |
| Edge continuity | Gradient coherence across tile boundary |
| Mutual information | Shared information content |
| Gradient similarity | Edge pattern agreement |
| Content quality | Signal-to-noise ratio |
| Intensity difference | Mean brightness mismatch |

> **Ask Aqua:**
> *"Modify the feature extraction in run.py to load my image pairs from /data/qc_pairs/tile_pairs/ with the naming convention pair_XXX_left.tif / pair_XXX_right.tif, and read labels from /data/qc_pairs/labels.csv"*

### Step 4: Train and Evaluate

> **Ask Aqua:**
> *"Run my capsule to train the GradientBoosting classifier on my labeled pairs with 5-fold cross-validation"*

### Step 5: Deploy for Inference (optional)

> **Ask Aqua:**
> *"Add an inference mode that takes a directory of unlabeled image pairs and outputs predictions with confidence scores and pass/fail/review routing"*

---

## 3. Outputs You'll Get

| File | What It Contains |
|------|-----------------|
| `evaluation_report.html` | Interactive HTML report with all metrics and visualizations |
| `predictions.csv` | Per-pair: score, prediction, confidence, features, metadata |
| `metrics.json` | ROC-AUC, PR-AUC, precision, recall by threshold |
| `roc_curve.png` | ROC curve with AUC |
| `confusion_matrix.png` | Test set performance breakdown |
| `example_gallery.png` | Visual examples of TP/FP/TN/FN cases |

---

## 4. Adapting for Different Use Cases

### Use Case A: Fluorescence microscopy (not light-sheet)
The 7 features are modality-agnostic. Just provide your image pairs.

> **Ask Aqua:**
> *"Adapt the pipeline for confocal tile stitching QC — my images are 1024x1024 16-bit TIFF with 4 channels. Extract features from the DAPI channel only."*

### Use Case B: 3D volume registration QC
Extend to volumetric data by processing z-slices.

> **Ask Aqua:**
> *"Modify the pipeline to handle 3D TIFF stacks. Extract features from the middle 5 z-slices and aggregate scores."*

### Use Case C: Production monitoring (no retraining)
Use the pre-trained model on new data batches.

> **Ask Aqua:**
> *"Add a --predict-only mode that loads the trained model from a previous run's results and applies it to new unlabeled pairs at /data/new_batch/"*

---

## 5. Tips

- **Minimum 100 labeled pairs**: The classifier needs balanced examples of pass/fail
- **Include edge cases**: Borderline alignments are the most informative training examples
- **Tune review threshold**: Adjust the confidence band for "needs_review" based on your tolerance for false positives
- **Feature importance**: Check which features matter most for your data — you may be able to simplify
- **Self-contained mode**: The capsule works out-of-the-box with synthetic data for quick prototyping

---

## 6. Environment Requirements

| Package | Purpose |
|---------|---------|
| `scikit-image` | Image quality metrics (SSIM, etc.) |
| `scikit-learn` | GradientBoosting classifier, cross-validation |
| `tifffile` | TIFF I/O |
| `matplotlib` | Visualization |
| `pandas` | Data handling |
| `scipy` | Statistical analysis |

**Compute**: CPU only, X-Small to Small tier (< 2 min for 250 pairs)
