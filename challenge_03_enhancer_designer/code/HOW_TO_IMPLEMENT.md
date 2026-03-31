# How to Implement: Enhancer Designer — For Your Own Data

> **Goal**: Design synthetic enhancer-like DNA sequences for *your* cell type or
> regulatory context using a genetic algorithm with biologically-informed scoring,
> manufacturability filtering, and diversity selection.

---

## 1. What You Need (Your Data)

### Required Inputs

| Input | Format | Required? | Description |
|-------|--------|-----------|-------------|
| **Target TF motifs** | PWM matrices or JASPAR IDs | Yes (or use defaults) | Position weight matrices for transcription factors active in your cell type |
| **ATAC-seq peaks** (optional) | FASTA file, 200bp sequences | No | Real open chromatin regions from your cell type to seed the GA |
| **Oracle model** (optional) | PyTorch checkpoint (`.pt`) | No | Trained activity predictor (e.g., DeepSTARR, ChromBPNet) |

### What Your Data Should Look Like

**Option A: Minimal — just specify TF motifs**
```
# No data asset needed — configure via App Panel parameters
# Specify your TFs of interest: e.g., GATA1, TAL1, SP1 for K562
# The capsule uses built-in PWM matrices for common TFs
```

**Option B: Custom peak sequences**
```
# k562_peaks.fasta (or your_celltype_peaks.fasta)
>peak_001 chr1:1000-1200
ATCGATCG...
>peak_002 chr2:5000-5200
GCTAGCTA...
```
- Each sequence should be ~200 bp
- These are used as seeds for the genetic algorithm
- More diverse seeds → more diverse output enhancers

---

## 2. Step-by-Step: Recreate This Capsule with Aqua

### Step 1: Create a New Capsule

> **Ask Aqua:**
> *"Create a new capsule called 'Enhancer Design — [My Cell Type]' with Python 3.10, and install packages: numpy, scipy, matplotlib, biopython"*

### Step 2: Prepare Your Data (Optional)

If you have ATAC-seq peaks or a custom oracle model:

> **Ask Aqua:**
> *"Create a data asset called 'my-enhancer-inputs' and attach it to my capsule at /data/enhancer_inputs"*

Upload structure:
```
enhancer_inputs/
├── my_peaks.fasta              # Optional: ATAC-seq peak sequences
└── model_weights/
    └── my_oracle.pt            # Optional: trained activity predictor
```

### Step 3: Configure the Design Parameters

The capsule uses an App Panel for configuration. Key parameters:

| Parameter | What to Set | Your Decision |
|-----------|-------------|---------------|
| **Generations** | 50–200 | More = better optimization, slower |
| **Population Size** | 200–500 | Larger = more diversity explored |
| **Mutation Rate** | 0.01–0.1 | Higher = more exploration, less exploitation |
| **Top-K Finalists** | 10–50 | How many diverse candidates you want |
| **Random Seed** | Any integer | For reproducibility |

> **Ask Aqua:**
> *"Set up the App Panel for my enhancer design capsule with parameters: generations (default 100), population_size (default 300), mutation_rate (default 0.04), top_k (default 30), random_seed (default 42)"*

### Step 4: Customize for Your Cell Type

> **Ask Aqua:**
> *"Modify the scoring function to use PWM motifs for [your TFs, e.g., SOX2, OCT4, NANOG for stem cells] instead of the default K562 TFs. Keep the GC content filter, homopolymer filter, and restriction site exclusion."*

### Step 5: Run

> **Ask Aqua:**
> *"Run my capsule with parameters: generations=100, population_size=300, top_k=30"*

---

## 3. Outputs You'll Get

| File | What It Contains |
|------|-----------------|
| `top20.fasta` | Your designed enhancer sequences with scores and motif annotations |
| `enhancer_report.png` | 6-panel figure: score distributions, GA trajectory, motif heatmap, GC scatter, diversity, enrichment |
| `stats.json` | Statistical tests (evolved vs random/shuffled), effect sizes, diversity metrics |
| `run_manifest.yaml` | Complete parameter record for reproducibility |

---

## 4. Adapting for Different Use Cases

### Use Case A: Different cell type (e.g., hepatocyte enhancers)
Replace TF motifs with liver-specific factors (HNF4A, FOXA1, CEBPA).

> **Ask Aqua:**
> *"Replace the K562 TF motif set with hepatocyte TFs: HNF4A, FOXA1, CEBPA, HNF1A. Update the cooperativity model for liver-specific motif spacing."*

### Use Case B: Longer regulatory elements (e.g., 500bp promoters)
Adjust sequence length and filter parameters.

> **Ask Aqua:**
> *"Change the target sequence length from 200bp to 500bp, adjust the homopolymer filter to allow up to 8bp runs, and increase population size to 500."*

### Use Case C: Using a real oracle (DeepSTARR / ChromBPNet)
Mount your trained model and wire it into the scoring function.

> **Ask Aqua:**
> *"Integrate my DeepSTARR model at /data/enhancer_inputs/model_weights/deepstarr.pt as the scoring oracle. Use the model's predicted activity score instead of PWM-based scoring."*

---

## 5. Tips

- **Start with defaults**: The built-in K562 motifs work as a proof-of-concept even without custom data
- **Check the diversity matrix**: If near-duplicate fraction is high (>50%), increase mutation rate or population size
- **Restriction sites matter**: The default excludes EcoRI/BamHI/HindIII/NotI — add your cloning sites to the exclusion list
- **Validate computationally first**: Before wet-lab testing, run candidates through an independent predictor
- **GC content**: Default filter is 30–70% — tighten for specific organisms/contexts

---

## 6. Environment Requirements

| Package | Purpose |
|---------|---------|
| `numpy` | Vectorized PWM scanning |
| `scipy` | Statistical tests |
| `matplotlib` | Visualization |
| `biopython` | FASTA I/O, sequence handling |

**Compute**: CPU only, Small tier sufficient (vectorized numpy operations)
