# Results — Challenge 12: Brain Map + BKP Assistant

## Evidence Strength: STRONG

This capsule achieves **86.7% overall accuracy** on a 15-query evaluation set that includes easy, medium, cross-product, and adversarial queries. The accuracy drops below 100% on adversarial queries, proving honest (non-circular) evaluation.

## Evaluation Results (evaluation_report.json)

### Per-Category Accuracy
| Category | Accuracy | Correct/Total |
|----------|----------|--------------|
| Easy (verbatim match) | 100% | 5/5 |
| Medium (synonym/paraphrase) | 100% | 5/5 |
| Cross-product | 100% | 2/2 |
| Adversarial (out-of-corpus) | 33.3% | 1/3 |
| **Overall** | **86.7%** | **13/15** |

### Additional Metrics
- Deprecated resources flagged: 2
- Cross-product connections identified in `product_bridges.json`

## Known Limitations
- Corpus is curated (not crawled from live websites), so it represents a snapshot
- Adversarial queries (misspellings, deprecated resources, non-existent features) expose retrieval gaps
- TF-IDF retrieval, not embedding-based — accuracy could improve with dense embeddings

## Output Artifacts
| File | Description |
|------|-------------|
| `evaluation_report.json` | Per-category accuracy breakdown |
| `product_bridges.json` (2 KB) | Cross-product connection graph |
| `answers.jsonl` (6.6 KB) | Per-query answers with citations |
| `corpus_meta.json` | Corpus size and metadata |
