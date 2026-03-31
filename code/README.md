# Challenge 09: BindCrafting


## Results Summary
- **Top Candidate iPTM:** 0.926 (binder_0124, pLDDT 96.55)
- **5 ranked candidates** passing iPTM ≥ 0.7 and pLDDT ≥ 80
- **Target:** PDB 1RK9 (Parvalbumin) — real structure
- **Fusion compatibility** assessed for fluorescent protein tagging

> See [RESULTS.md](RESULTS.md) for ranked candidate table and filtering details.

## Overview

Protein binder analysis pipeline that filters, ranks, and analyzes pre-computed
BindCraft design candidates against a neuroscience target (Parvalbumin). Includes
an **AWS Bedrock-based agentic analysis** that generates scientific interpretation
of the binder panel using Claude via `boto3 + bedrock-runtime`.

## Pipeline Stages

1. **Data Generation** — Synthetic BindCraft outputs (200 trajectories + PDBs)
2. **Filtering** — Predeclared thresholds: iPTM≥0.7, pLDDT≥80, pAE≤10, len≤120
3. **Ranking** — Sort survivors by iPTM, select top 5
4. **Fusion Check** — N/C-term distance to interface via BioPython PDB parsing
5. **Bedrock Agent** — Claude via AWS Bedrock generates scientific analysis
6. **Visualization** — Score scatter, fusion distances, filtering funnel
7. **Artifacts** — Mandatory manifest, summary, validation notes

## Required Packages

- `numpy`, `pandas`, `matplotlib`, `biopython` — analysis and visualization
- `boto3` — AWS Bedrock integration (Claude model invocation)

## Expected Outputs

| File | Description |
|------|-------------|
| `ranked_candidates.csv` | Top 5 candidates with metrics and fusion terminus |
| `fusion_compatibility.json` | Per-candidate terminus distances and safety |
| `filtering_funnel.json` | Design attrition through filter stages |
| `agent_analysis.md` | Bedrock-generated scientific interpretation |
| `top5_visualizations/` | Score scatter, fusion distance, funnel charts |
| `manifest.json` | Complete artifact manifest |
| `IMPLEMENTATION_SUMMARY.md` | Implementation documentation |
| `VALIDATION_NOTES.md` | Completeness and limitations |

## Agentic Component

The Bedrock agent (`bedrock_agent.py`) uses `boto3.client('bedrock-runtime')` to
invoke Claude. **No `anthropic` or `openai` packages** are used. If Bedrock
credentials are unavailable, a deterministic local analysis fallback runs.

## Running

```bash
/code/run
```
