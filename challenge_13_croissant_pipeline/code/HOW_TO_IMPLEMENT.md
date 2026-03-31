# How to Implement: Croissant Pipeline for AI-Ready Data — For Your Own Data

> **Goal**: Package *your* dataset as a Croissant-compliant (MLCommons standard)
> ML-ready resource with validated metadata, documented schema, reproducible
> splits, and working data loading examples.

---

## 1. What You Need (Your Data)

### Input Data Format

| Input | Format | Description |
|-------|--------|-------------|
| **Source dataset** | H5AD, CSV, or Parquet | Your dataset with observations and metadata |

### What Your Data Should Look Like

**Option A: Single-cell H5AD (AnnData)**
```
my_dataset.h5ad
├── X (matrix)         # Gene expression matrix (cells × genes)
├── obs (DataFrame)    # Cell metadata: cell_type, donor, region, etc.
├── var (DataFrame)    # Gene metadata: gene_symbol, ensembl_id, etc.
└── obsm (dict)        # Embeddings: X_umap, X_pca, etc.
```

**Option B: Tabular CSV/Parquet**
```csv
# my_dataset.csv
sample_id,feature_1,feature_2,...,label,split
S001,0.45,1.23,...,classA,train
S002,0.67,0.89,...,classB,test
```

**Key requirements:**
- Must have a clear observation/sample table with metadata columns
- Column names should be descriptive (not `col1`, `col2`)
- If you want train/test splits, include a `split` column or provide split criteria
- Minimum ~1000 rows recommended for meaningful ML use
- All columns should have consistent types (no mixed string/numeric)

---

## 2. Step-by-Step: Recreate This Capsule with Aqua

### Step 1: Create a New Capsule

> **Ask Aqua:**
> *"Create a new capsule called 'Croissant Packaging — [My Dataset Name]' with Python 3.10, and install packages: mlcroissant, anndata, pandas, numpy"*

### Step 2: Prepare Your Dataset

> **Ask Aqua:**
> *"Create a data asset called 'my-source-dataset' with my H5AD/CSV file, then attach it at /data/source"*

### Step 3: Export Metadata Tables

> **Ask Aqua:**
> *"Modify export_tables.py to load my dataset from /data/source/my_dataset.h5ad and export the cell metadata (obs) to CSV at /results/cell_metadata.csv. Include columns: [list your key columns, e.g., cell_type, donor_id, brain_region, n_genes]."*

### Step 4: Build the Croissant Descriptor

> **Ask Aqua:**
> *"Modify build_croissant.py to create a Croissant JSON-LD descriptor for my dataset. Set the name to '[My Dataset]', description to '[your description]', and map my CSV columns to Croissant fields with proper data types."*

### Step 5: Validate and Load

> **Ask Aqua:**
> *"Run validate_and_load.py to check the Croissant descriptor validates with mlcroissant and can load 5 real rows back from the CSV."*

### Step 6: Run the Full Pipeline

> **Ask Aqua:**
> *"Run my capsule to execute the complete pipeline: export → build Croissant → validate → load test"*

---

## 3. Outputs You'll Get

| File | What It Contains |
|------|-----------------|
| `croissant_metadata.json` | Valid Croissant JSON-LD descriptor (MLCommons standard) |
| `cell_metadata.csv` | Exported observation metadata table |
| `validation_report.json` | Validation status, any errors, sample rows loaded |

---

## 4. Adapting for Different Use Cases

### Use Case A: Imaging dataset
Package microscopy images with metadata.

> **Ask Aqua:**
> *"Create a Croissant descriptor for my imaging dataset. The CSV has columns: image_path, magnification, stain_type, diagnosis, split. Map image_path as a FileObject reference."*

### Use Case B: Genomics / multi-omics
Package sequencing data with clinical metadata.

> **Ask Aqua:**
> *"Create Croissant metadata for my RNA-seq dataset. Include gene expression matrix as a separate resource and the sample metadata CSV as another. Link them via sample_id."*

### Use Case C: Time-series / longitudinal data
Package data with temporal structure.

> **Ask Aqua:**
> *"Add temporal annotations to my Croissant descriptor. The dataset has columns: patient_id, visit_date, measurement, value. Document the time-series structure."*

### Use Case D: Adding reproducible train/test splits
Ensure ML reproducibility.

> **Ask Aqua:**
> *"Add a stratified 80/20 train/test split to my dataset based on the 'label' column. Save the split assignments as a column in the exported CSV and document the split strategy in the Croissant descriptor."*

---

## 5. Tips

- **Validation is binary**: The Croissant file either validates or doesn't — fix all errors before publishing
- **Column documentation**: Add descriptions for every field in the Croissant descriptor
- **Loading test**: Always verify you can load real rows from the descriptor — this catches schema mismatches
- **MLCommons standard**: Croissant is recognized by Hugging Face, Google Dataset Search, and other ML platforms
- **Versioning**: Include a version field in the descriptor; update when the source data changes
- **File references**: For large files (images, matrices), use URL references rather than embedding data

---

## 6. Environment Requirements

| Package | Purpose |
|---------|---------|
| `mlcroissant` | Croissant JSON-LD validation and loading |
| `anndata` | H5AD file I/O (for single-cell data) |
| `pandas` | CSV/Parquet I/O, data manipulation |
| `numpy` | Array operations |

**Compute**: CPU only, X-Small tier sufficient
