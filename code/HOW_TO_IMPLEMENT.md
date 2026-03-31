# How to Implement: Allen Single-Cell Model Pantry — For Your Own Data

> **Goal**: Build a reproducible benchmark system that evaluates *your* single-cell
> foundation models on cell type annotation tasks with frozen splits, shared
> evaluation contracts, and fair head-to-head comparisons.

---

## 1. What You Need (Your Data)

### Input Data Format

| Input | Format | Description |
|-------|--------|-------------|
| **Annotated scRNA-seq dataset** | H5AD (AnnData) | Gene expression + cell type labels + train/test split |
| **Gene mapping** (optional) | CSV | Symbol → Ensembl ID mapping for models requiring Ensembl IDs |
| **Model checkpoints** | Directory per model | Pre-trained model weights |

### What Your Data Should Look Like

```python
# my_dataset.h5ad — AnnData object
adata.X                          # Raw gene counts (cells × genes)
adata.obs['cell_type']           # Ground truth cell type labels
adata.obs['split']               # 'train' or 'test' (frozen split)
adata.obs['donor']               # Optional: for donor-held-out evaluation
adata.var_names                  # Gene symbols (e.g., 'GAPDH', 'ACTB')
adata.var['ensembl_id']          # Optional: Ensembl IDs for some models
```

```
my_benchmark/
├── my_dataset.h5ad              # Pre-split dataset
├── gene_mapping.csv             # gene_symbol → ensembl_id
└── models/
    ├── scvi_weights/            # scVI checkpoint
    ├── geneformer_weights/      # Geneformer checkpoint
    └── scgpt_weights/           # Any other model
```

**Key requirements:**
- **Frozen split**: The `split` column must be pre-defined (not random at runtime) for fair comparison
- **Cell type labels**: Must be in `adata.obs` — this is the classification target
- **Raw counts**: Most models expect unnormalized counts in `adata.X`
- **Minimum 5,000 cells** for meaningful evaluation; 10K–100K recommended
- **Balanced classes**: At least 20 cells per cell type in both train and test

---

## 2. Step-by-Step: Recreate This Capsule with Aqua

### Step 1: Create a New Capsule

> **Ask Aqua:**
> *"Create a new capsule called 'SC Model Benchmark — [My Dataset]' with a GPU-enabled PyTorch base image, and install packages: scanpy, anndata, scvi-tools, torch, transformers, scikit-learn, matplotlib, pandas"*

### Step 2: Prepare Your Dataset

> **Ask Aqua:**
> *"Create a data asset called 'my-benchmark-dataset' with my pre-split H5AD and model checkpoints, then attach it at /data/benchmark"*

**Creating a frozen split:**
```python
import scanpy as sc
import numpy as np

adata = sc.read_h5ad('my_data.h5ad')

# Donor-held-out split (recommended for generalization)
test_donors = ['donor_3', 'donor_7']  # ~20% of donors
adata.obs['split'] = np.where(
    adata.obs['donor'].isin(test_donors), 'test', 'train'
)
adata.write('my_dataset_split.h5ad')
```

### Step 3: Add Model Adapters

Each model needs a thin adapter that conforms to the shared evaluation interface:

> **Ask Aqua:**
> *"Create a model adapter for [your model, e.g., scGPT] in /code/adapters/scgpt_adapter.py. It should implement: load_model(checkpoint_path), encode(adata) → embeddings, and follow the same interface as the existing scVI and Geneformer adapters."*

**Adapter interface:**
```python
class ModelAdapter:
    def load(self, checkpoint_path: str) -> None: ...
    def encode(self, adata) -> np.ndarray: ...  # Returns (n_cells, n_features)
```

### Step 4: Configure the Benchmark

> **Ask Aqua:**
> *"Modify run.py to load my dataset from /data/benchmark/my_dataset.h5ad, run all registered model adapters, evaluate with KNN classifier (k=15), and compute macro F1 on the frozen test split."*

### Step 5: Run

> **Ask Aqua:**
> *"Run my capsule with GPU"*

---

## 3. Outputs You'll Get

| File | What It Contains |
|------|-----------------|
| `leaderboard.csv` | model_name, accuracy, macro_f1, runtime_seconds |
| `confusion_*.png` | Confusion matrix per model |
| `summary.json` | Winner, per-model detailed metrics, test set size |

---

## 4. Adapting for Different Use Cases

### Use Case A: Adding a new model to the benchmark
Write a new adapter and register it.

> **Ask Aqua:**
> *"Add a new adapter for [CellPLM / scFoundation / UCE]. Download the checkpoint, implement the encode() method, and add it to the model registry in run.py."*

### Use Case B: Different evaluation tasks (batch integration, not classification)
Change the downstream evaluation.

> **Ask Aqua:**
> *"Replace the KNN classifier evaluation with batch integration metrics: silhouette score, kBET, and graph connectivity (scib-metrics). Compare how well each model's embeddings integrate across donors/batches."*

### Use Case C: Cross-dataset generalization
Train on one dataset, evaluate on another.

> **Ask Aqua:**
> *"Set up a cross-dataset evaluation: encode training cells from Dataset A, build KNN classifier, then predict cell types on Dataset B. Report transfer accuracy."*

### Use Case D: Few-shot evaluation
Test with limited labeled data.

> **Ask Aqua:**
> *"Add few-shot evaluation: train the KNN classifier on 10/50/100 labeled cells per type and report macro F1 at each label budget."*

---

## 5. Tips

- **Freeze the split first**: Never change train/test splits between model evaluations
- **Same classifier for all**: Use the same KNN (k=15) for all models to isolate embedding quality
- **Raw counts**: Most models expect unnormalized counts — don't log-normalize before encoding
- **GPU memory**: Large models (Geneformer, scGPT) may need 16GB+ VRAM; use appropriate instance
- **Gene name alignment**: Some models use Ensembl IDs, others use symbols — the gene mapping CSV bridges this
- **Runtime tracking**: Record encoding time per model — it's a key practical metric

---

## 6. Environment Requirements

| Package | Purpose |
|---------|---------|
| `scanpy` | Single-cell data handling |
| `anndata` | H5AD I/O |
| `scvi-tools` | scVI model |
| `torch` | PyTorch backend |
| `transformers` | Geneformer / transformer-based models |
| `scikit-learn` | KNN classifier, evaluation metrics |
| `matplotlib` | Confusion matrix plots |
| `pandas` | Leaderboard table |

**Compute**: GPU required (at least 16 GB VRAM for large models)
**Runtime**: Depends on dataset size and number of models; ~5–30 min typical
