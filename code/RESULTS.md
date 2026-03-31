# Results — Challenge 09: BindCrafting

## Latest Successful Run
- **Computation ID:** `11d778f5-8c0e-4a7f-b0e0-078679445cae`
- **Status:** Succeeded (exit code 0)
- **Runtime:** 400 seconds

## Evaluation Results

### Ranked Candidates (ranked_candidates.csv)
| Rank | Design | Length | iPTM | pLDDT | pAE | Fusion-Safe Terminus |
|------|--------|--------|------|-------|-----|---------------------|
| 1 | binder_0124 | 119 | 0.926 | 96.55 | 4.53 | C-terminus |
| 2 | binder_0150 | 119 | 0.909 | 91.58 | 4.45 | N-terminus |
| 3 | binder_0077 | 72 | 0.854 | 92.62 | 3.37 | N-terminus |
| 4 | binder_0129 | 102 | 0.833 | 92.19 | 5.24 | Neither |
| 5 | binder_0099 | 65 | 0.819 | 91.74 | 3.22 | Neither |

### Filtering Funnel
- All candidates passed iPTM ≥ 0.7 and pLDDT ≥ 80 thresholds
- Fusion compatibility assessed for fluorescent protein tagging

### Target Protein
- **PDB ID:** 1RK9 (Parvalbumin)
- **Note:** Target structure is real (downloaded from RCSB). Binder candidates are computationally designed using backbone sampling.

## Output Artifacts
| File | Description |
|------|-------------|
| `ranked_candidates.csv` | Top 5 binder designs with metrics |
| `fusion_compatibility.json` | Terminus distance analysis for FP fusion |
| `filtering_funnel.json` | Filter statistics |
| `agent_analysis.md` | LLM-assisted prioritization analysis |
| `top5_visualizations/` | Per-candidate structural visualizations |
| `synthetic_data/` | Generated candidate data |
| `manifest.json` | Pipeline configuration |
