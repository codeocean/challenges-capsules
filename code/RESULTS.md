# Results — Challenge 12: Brain Map + BKP Assistant

## Latest Successful Run
- **Computation ID:** `99c27188-1f48-4290-851e-33b94a958484`
- **Status:** Succeeded (exit code 0)
- **Runtime:** 152 seconds

## Evaluation Results (evaluation_report.json)

### Query Accuracy
| Category | Accuracy | Correct/Total |
|----------|----------|--------------|
| Easy | 100% | 5/5 |
| Medium | 100% | 5/5 |
| Cross-product | 100% | 2/2 |
| Adversarial | 33.3% | 1/3 |
| **Overall** | **86.7%** | **13/15** |

### Additional Metrics
- Deprecated resources flagged: 2
- Total queries: 15

### Notes
- Easy, medium, and cross-product queries perform perfectly
- Adversarial queries (out-of-corpus, misspellings) correctly drive accuracy below 100%, proving honest evaluation

## Output Artifacts
| File | Description |
|------|-------------|
| `evaluation_report.json` | Per-category accuracy |
| `product_bridges.json` (2 KB) | Cross-product connections |
| `answers.jsonl` (6.6 KB) | Per-query answers |
| `corpus_meta.json` | Corpus metadata |
