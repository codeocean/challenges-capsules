# How to Implement: BindCrafting — For Your Own Data

> **Goal**: Analyze and rank protein binder design candidates for *your* target
> protein using BindCraft/AlphaFold2-style metrics, with filtering, fusion
> compatibility assessment, and AI-powered scientific interpretation.

---

## 1. What You Need (Your Data)

### Input Data Format

| Input | Format | Description |
|-------|--------|-------------|
| **BindCraft trajectories** | CSV or JSON | Design trajectory metrics (iPTM, pLDDT, pAE, sequence length, etc.) |
| **Candidate PDB structures** | PDB files | 3D structures of designed binders complexed with target |
| **Target protein** | PDB file (optional) | Your target protein structure for interface analysis |

### What Your Data Should Look Like

```csv
# bindcraft_results.csv — BindCraft or similar design tool output
design_id,sequence,length,iptm,plddt,pae,rmsd,target
binder_001,MKTLLILAVL...,85,0.82,91.3,7.2,1.8,Parvalbumin
binder_002,MDWKEFQAIL...,72,0.75,85.6,9.1,2.3,Parvalbumin
binder_003,MAQFNYLKEE...,110,0.69,78.2,12.4,3.1,Parvalbumin
...
```

```
my_binder_data/
├── bindcraft_results.csv       # Design metrics
├── structures/
│   ├── binder_001_complex.pdb  # Binder-target complexes
│   ├── binder_002_complex.pdb
│   └── ...
└── target/
    └── my_target.pdb           # Optional: target structure
```

**Key requirements:**
- Metrics CSV must include: `iptm` (interface predicted TM-score), `plddt` (predicted LDDT), `pae` (predicted aligned error)
- PDB files should contain both binder and target chains
- At least 50–200 design candidates for meaningful filtering
- Sequence column optional but useful for diversity analysis

---

## 2. Step-by-Step: Recreate This Capsule with Aqua

### Step 1: Create a New Capsule

> **Ask Aqua:**
> *"Create a new capsule called 'Binder Analysis — [My Target Protein]' with Python 3.10, and install packages: numpy, pandas, matplotlib, biopython, boto3"*

### Step 2: Prepare Your BindCraft Output

> **Ask Aqua:**
> *"Create a data asset called 'my-binder-candidates' with my BindCraft results CSV and PDB structures, then attach it at /data/binder_data"*

### Step 3: Configure Filtering Thresholds

Adjust thresholds based on your design campaign:

| Metric | Default Threshold | Your Decision |
|--------|------------------|---------------|
| iPTM | ≥ 0.7 | Higher = more confident interface |
| pLDDT | ≥ 80 | Higher = better local structure |
| pAE | ≤ 10 | Lower = better alignment |
| Length | ≤ 120 residues | Depends on your expression system |

> **Ask Aqua:**
> *"Modify the filtering thresholds: iPTM ≥ 0.75, pLDDT ≥ 85, pAE ≤ 8, length ≤ 100 for my stringent selection."*

### Step 4: Run

> **Ask Aqua:**
> *"Run my capsule to filter, rank, and analyze my binder candidates"*

---

## 3. Outputs You'll Get

| File | What It Contains |
|------|-----------------|
| `ranked_candidates.csv` | Top 5 candidates with all metrics and fusion terminus recommendation |
| `fusion_compatibility.json` | Per-candidate N/C-term distances to interface and fusion safety |
| `filtering_funnel.json` | Design attrition through each filter stage |
| `agent_analysis.md` | AI-generated scientific interpretation of the panel |
| `top5_visualizations/` | Score scatter, fusion distance, filtering funnel charts |

---

## 4. Adapting for Different Use Cases

### Use Case A: Different target protein
Just change the input data — the pipeline is target-agnostic.

> **Ask Aqua:**
> *"Load my BindCraft results for [your target, e.g., GFP, insulin receptor, PD-L1]. Keep the same filtering pipeline but adjust length threshold to ≤ 150 for larger interfaces."*

### Use Case B: RFdiffusion + ProteinMPNN output (not BindCraft)
Adapt the input parsing for different design tools.

> **Ask Aqua:**
> *"Modify the input parser to read RFdiffusion/ProteinMPNN output format. Map their metrics to the standard columns: confidence → plddt, interface_score → iptm."*

### Use Case C: Nanobody / VHH design
Adjust for single-domain antibody constraints.

> **Ask Aqua:**
> *"Add nanobody-specific filters: CDR3 length 9–20 residues, framework conservation check, and VHH hallmark residue verification."*

### Use Case D: Fluorescent protein fusion compatibility
The pipeline already checks fusion termini — customize for your fusion strategy.

> **Ask Aqua:**
> *"Configure fusion analysis for C-terminal GFP tagging. Flag any candidate where the C-terminus is within 15Å of the binding interface."*

---

## 5. Tips

- **More candidates = better**: Start with 200+ designs and filter down to top 5–10
- **Diversity matters**: The ranking selects for metric quality, but check sequence diversity among top hits
- **Fusion terminus**: N-terminal or C-terminal fusion can dramatically affect function — check distances
- **Validate experimentally**: Computational scores are predictive but not definitive — plan for wet-lab validation
- **AI analysis**: The Bedrock agent provides scientific context; falls back to deterministic analysis if unavailable

---

## 6. Environment Requirements

| Package | Purpose |
|---------|---------|
| `numpy` | Numerical operations |
| `pandas` | Data handling and ranking |
| `matplotlib` | Visualization |
| `biopython` | PDB parsing, structural analysis |
| `boto3` | AWS Bedrock for scientific interpretation |

**Compute**: CPU only, X-Small tier sufficient
**LLM**: AWS Bedrock (Claude) for agentic analysis — deterministic fallback available
