# 🔄 Challenge 02: Agentic Data Harmonization

## What This Capsule Does

Maps cell type labels from Allen Institute single-cell datasets to standardized Cell Ontology (CL) terms using a multi-strategy pipeline: expert override mappings, abbreviation expansion, and fuzzy string matching (rapidfuzz). Optionally validates low-confidence mappings using an LLM agent (AWS Bedrock).

## Results Summary

| Metric | WHB Taxonomy | CELLxGENE |
|--------|-------------|-----------|
| **Precision** | 0.9493 | 0.9721 |
| **Recall** | 0.9493 | 0.9721 |
| **F1 Score** | 0.9493 | 0.9721 |
| **Labels Evaluated** | 493 | 466 |

### Difficulty Breakdown (WHB)
| Tier | Labels | Mapped | Rate |
|------|--------|--------|------|
| Easy | 6 | 6 | 100% |
| Medium | 1,080 | 1,011 | 93.6% |
| Hard | 2,706 | 750 | 27.7% |
| Opaque | 32 | 18 | 56.2% |

> See [RESULTS.md](RESULTS.md) for detailed evaluation, output artifact descriptions, and methodology.

## Required Data Assets

| Data Asset | Mount | Description |
|-----------|-------|-------------|
| `challenge_02_input` | `/data/challenge_02_input` | Cell Ontology OBO, gold mappings |
| `WHB-taxonomy` | `/data/WHB-taxonomy` | Allen Brain Cell Atlas WHB taxonomy |
| `cellxgene_brain` | `/data/cellxgene_brain` | CELLxGENE brain cell types |

## Key Outputs

| File | Description |
|------|-------------|
| `mapping_table.csv` | Full mapping table (3,824 labels) |
| `eval_report.json` | WHB evaluation metrics |
| `cellxgene_eval_report.json` | CELLxGENE evaluation metrics |
| `difficulty_analysis.json` | Per-tier mapping rates |
| `provenance.jsonl` | Decision audit trail |
| `review_queue.json` | Labels needing human review |

## Environment

- Python 3.10+, CPU only
- `pandas`, `rapidfuzz`, `boto3` (optional for LLM agent)
