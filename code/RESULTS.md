# Results — Challenge 02: Agentic Data Harmonization

## Latest Successful Run
- **Computation ID:** `3164b109-2ea2-4705-adb2-ac0e885fddb6`
- **Status:** Succeeded (exit code 0)
- **Runtime:** 301 seconds

## Evaluation Results

### WHB Taxonomy Mapping (eval_report.json)
| Metric | Value |
|--------|-------|
| Precision | 0.9493 |
| Recall | 0.9493 |
| F1 Score | 0.9493 |
| True Positives | 468 |
| False Positives | 25 |
| False Negatives | 25 |
| Gold Standard Size | 493 labels |

### CELLxGENE Cross-Dataset Mapping (cellxgene_eval_report.json)
| Metric | Value |
|--------|-------|
| Precision | 0.9721 |
| Recall | 0.9721 |
| F1 Score | 0.9721 |
| True Positives | 453 |
| False Positives | 13 |
| False Negatives | 13 |
| Gold Standard Size | 466 labels |

### Difficulty Breakdown (difficulty_analysis.json)
| Difficulty | Total Labels | Mapped | Mapping Rate |
|------------|-------------|--------|-------------|
| Easy | 6 | 6 | 100.0% |
| Medium | 1,080 | 1,011 | 93.6% |
| Hard | 2,706 | 750 | 27.7% |
| Opaque | 32 | 18 | 56.2% |

### Agentic LLM Component (agentic_proof.json)
- LLM attempted: Yes (Strands Agent + Bedrock)
- Method: `boto3_bedrock_direct`
- Model: `us.anthropic.claude-sonnet-4-20250514-v1:0`

## Output Artifacts
| File | Description |
|------|-------------|
| `mapping_table.csv` (350 KB) | Full mapping of 3,824 WHB labels to Cell Ontology |
| `cellxgene_mapping_table.csv` (44 KB) | CELLxGENE brain cell type mappings |
| `eval_report.json` | WHB evaluation with per-label details |
| `cellxgene_eval_report.json` | CELLxGENE evaluation with per-label details |
| `difficulty_analysis.json` | Per-tier mapping success rates |
| `gold_mappings_v3.csv` | Algorithmically derived gold standard |
| `provenance.jsonl` (1.4 MB) | Full decision audit trail |
| `review_queue.json` (565 KB) | Labels needing human review |
| `quality_report.json` | Criteria checklist |
| `agentic_proof.json` | LLM usage evidence |
| `scope.md` | Problem scope declaration |
| `IMPLEMENTATION_SUMMARY.md` | Architecture and approach |
| `VALIDATION_NOTES.md` | Honest assessment and limitations |

## Methodology
- **Source A:** Allen WHB taxonomy (`cluster_annotation_term.csv`) — 3,824 unique cluster labels
- **Source B:** CELLxGENE brain cell types — 466 labels
- **Target Ontology:** Cell Ontology (`cl.obo`) — 3,319 active CL terms
- **Matching Pipeline:** Expert override map → Abbreviation expansion → Exact match → Fuzzy matching (rapidfuzz)
- **Gold Standard:** Algorithmically derived from WHB description fields (independent of pipeline's name/synonym matching)
