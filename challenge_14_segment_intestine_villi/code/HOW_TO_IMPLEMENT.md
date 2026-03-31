# How to Implement: Segment Intestine Villi — For Your Own Data

> **Goal**: Segment individual tissue structures (villi, crypts, glands) from
> *your* spatial transcriptomics data by integrating spatial coordinates, gene
> expression, and cell-type composition into biologically meaningful boundaries.

---

## 1. What You Need (Your Data)

### Input Data Format

| Input | Format | Description |
|-------|--------|-------------|
| **Spatial transcriptomics data** | H5AD (AnnData) or Xenium output | Cell-level expression + spatial coordinates |

### What Your Data Should Look Like

**Option A: Xenium output directory**
```
xenium_output/
├── cell_feature_matrix/       # Sparse gene × cell matrix
│   ├── barcodes.tsv.gz
│   ├── features.tsv.gz
│   └── matrix.mtx.gz
├── cells.csv.gz               # Cell metadata with x_centroid, y_centroid
└── cell_boundaries.parquet    # Optional: cell boundary polygons
```

**Option B: Pre-processed H5AD (AnnData)**
```python
# Required fields in your AnnData object:
adata.X                        # Gene expression matrix (cells × genes)
adata.obs['x_centroid']        # Spatial X coordinate per cell
adata.obs['y_centroid']        # Spatial Y coordinate per cell
adata.var_names                # Gene names (must include marker genes)
```

**Key requirements:**
- Spatial coordinates (x, y) for every cell
- Gene expression data (raw counts preferred)
- **Marker genes for your tissue structure**: The algorithm uses marker genes to score cell types. For intestine villi, the defaults are: `EPCAM`, `FABP1`, `FABP2`, `VIL1`
- At least 1,000 cells recommended; works well up to 100K+
- Tissue should contain spatially distinct structures to segment

---

## 2. Step-by-Step: Recreate This Capsule with Aqua

### Step 1: Create a New Capsule

> **Ask Aqua:**
> *"Create a new capsule called 'Spatial Segmentation — [My Tissue Type]' with Python 3.10, and install packages: scanpy, squidpy, matplotlib, pandas, numpy, anndata"*

### Step 2: Prepare Your Data

> **Ask Aqua:**
> *"Create a data asset called 'my-spatial-data' with my Xenium output directory (or H5AD file), then attach it at /data/spatial"*

### Step 3: Configure Marker Genes

This is the most important customization — choose markers for *your* tissue structures:

| Tissue | Structure | Example Markers |
|--------|-----------|-----------------|
| **Intestine** | Villi (epithelial) | EPCAM, FABP1, FABP2, VIL1 |
| **Lung** | Alveoli | AGER, SFTPC, SFTPB, AQP5 |
| **Kidney** | Glomeruli | NPHS1, NPHS2, WT1, PODXL |
| **Liver** | Lobules | ALB, HNF4A, CYP3A4, GLUL |
| **Skin** | Epidermis | KRT14, KRT5, KRT1, KRT10 |

> **Ask Aqua:**
> *"Modify run.py to use my tissue-specific markers: [list your markers]. Score cells as [your cell type] based on expression of these genes, then build the spatial neighbor graph and run Leiden clustering."*

### Step 4: Tune Spatial Parameters

> **Ask Aqua:**
> *"Set the spatial neighbor graph parameters: n_neighbors=15 (adjust for cell density), Leiden resolution=0.5 (adjust for cluster size). My cells are spaced approximately [X] µm apart."*

### Step 5: Run

> **Ask Aqua:**
> *"Run my capsule to segment spatial structures"*

---

## 3. Outputs You'll Get

| File | What It Contains |
|------|-----------------|
| `spatial_plot.png` | Color-coded spatial map (each color = one segmented structure) |
| `villus_assignments.csv` | cell_id, cluster_id, is_marker_positive, x, y |
| `per_villus_summary.csv` | cluster_id, n_cells, mean_marker_score, spatial_extent |

---

## 4. Adapting for Different Use Cases

### Use Case A: Brain region segmentation from MERFISH
Segment cortical layers or brain regions.

> **Ask Aqua:**
> *"Adapt for MERFISH brain data. Use layer markers: CUX2 (L2/3), RORB (L4), FOXP2 (L5/6), and cluster into cortical layers based on spatial position and marker expression."*

### Use Case B: Tumor microenvironment segmentation
Identify tumor vs stroma vs immune regions.

> **Ask Aqua:**
> *"Segment my tumor spatial data into regions: tumor (KRT markers), stroma (VIM, COL1A1), immune (CD45, CD3, CD8). Use larger spatial neighborhoods (n_neighbors=30) for region-level segmentation."*

### Use Case C: Visium (spot-level, not single-cell)
Adapt for lower-resolution spatial data.

> **Ask Aqua:**
> *"Adapt for 10x Visium data. Load from the Space Ranger output. Use spot coordinates instead of cell centroids. Adjust neighbor graph for 55µm inter-spot distance."*

### Use Case D: 3D spatial segmentation
Extend to volumetric spatial data.

> **Ask Aqua:**
> *"Adapt for 3D spatial data with x, y, z coordinates. Build a 3D neighbor graph using squidpy. Segment into 3D tissue domains."*

---

## 5. Tips

- **Marker genes are critical**: Choose 3–5 highly specific markers for your target structure
- **Resolution tuning**: Lower Leiden resolution = fewer, larger clusters; higher = more, smaller clusters
- **Visual validation**: The spatial plot is the primary quality check — structures should look biologically plausible
- **Cell density varies**: Adjust n_neighbors based on your tissue's cell density (5–30 typical range)
- **Filter first**: Remove low-quality cells (low gene count, high mitochondrial %) before spatial analysis
- **Iterate**: Start with default parameters, visualize, adjust resolution and markers, repeat

---

## 6. Environment Requirements

| Package | Purpose |
|---------|---------|
| `scanpy` | Single-cell preprocessing, Leiden clustering |
| `squidpy` | Spatial neighbor graph construction |
| `anndata` | AnnData I/O |
| `matplotlib` | Spatial visualization |
| `pandas` | Data export |
| `numpy` | Array operations |

**Compute**: CPU only, Small tier for <50K cells; Medium for 50K–500K cells
