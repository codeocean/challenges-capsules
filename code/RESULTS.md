# Results — Challenge 08: Query BFF

## Latest Successful Run
- **Computation ID:** `6d49ce5e-b101-4545-bdd7-1b4134aee3ce`
- **Status:** Succeeded (exit code 0)
- **Runtime:** 179 seconds

## Evaluation Results (evaluation_report.json)

### Query Accuracy
| Metric | Value |
|--------|-------|
| **Total Queries** | 4 |
| **Correct** | 3 |
| **Success Rate** | 75% |
| **Avg Latency** | 4.25 sec |
| **Bedrock Model** | claude-sonnet-4-20250514-v1:0 |

### Data Source
- **Real data:** Allen Cell Collection MYH10 metadata (395 rows × 26 columns)

### Per-Query Results
| Query | Category | Matches Gold | Latency |
|-------|----------|-------------|---------|
| Find MYH10 images | structure_lookup | ✅ | 2.27s |
| Contains lookup (nbr_dist) | contains_lookup | ❌ | 8.36s |
| Cell stage = M1M2 | direct_lookup | ✅ | 1.86s |
| WellId = 266579 | direct_lookup | ✅ | 4.51s |

## Output Artifacts
| File | Description |
|------|-------------|
| `evaluation_report.json` (3.4 KB) | Per-query evaluation |
| `extracted_schema.json` (26 KB) | Auto-extracted BFF manifest schema |
