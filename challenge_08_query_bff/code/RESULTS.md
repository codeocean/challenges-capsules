# Results — Challenge 08: Query BFF

## Evidence Strength: MODERATE

The pipeline achieves **75% accuracy** (3/4 correct) on real Allen Cell Collection BFF metadata using Bedrock LLM for natural-language-to-filter translation. The evaluation is on real data but uses a very small query set (4 queries). A larger evaluation (15+ queries) would strengthen the evidence.

## Evaluation Results (evaluation_report.json)

### Summary
| Metric | Value |
|--------|-------|
| **Total Queries** | 4 |
| **Correct** | 3 |
| **Success Rate** | 75% |
| **Avg Latency** | 4.25 sec |
| **Data Source** | Real Allen Cell Collection MYH10 metadata |
| **Manifest Size** | 395 rows × 26 columns |

### Per-Query Results
| Query | Category | Correct | Result Count | Latency |
|-------|----------|---------|-------------|---------|
| Find MYH10 images | structure_lookup | ✅ | 395 | 2.27s |
| Contains lookup (nbr_dist) | contains_lookup | ❌ | 395 | 8.36s |
| Cell stage = M1M2 | direct_lookup | ✅ | 2 | 1.86s |
| WellId = 266579 | direct_lookup | ✅ | 69 | 4.51s |

## What the Evidence Shows
- **Real data:** Queries run against actual Allen Cell Collection metadata (not synthetic)
- **Real LLM calls:** Bedrock Claude translates natural language to structured JSON filters
- **Schema auto-extraction:** Pipeline auto-discovers column names, types, and value distributions

## Known Limitations
- Only 4 evaluation queries — too few for robust accuracy estimation
- The failed query involves a complex substring match that the LLM generates slightly differently than the gold
- All queries are "easy" category — no medium/hard/adversarial queries in this eval set
- To strengthen: expand to 15+ queries across difficulty levels (the infrastructure supports it)

## Output Artifacts
| File | Description |
|------|-------------|
| `evaluation_report.json` (3.4 KB) | Per-query evaluation with filters and metrics |
| `extracted_schema.json` (26 KB) | Auto-extracted BFF manifest schema |
