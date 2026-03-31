# Challenge 12: Brain-map + BKP Assistant


## Results Summary
- **Overall Accuracy:** 86.7% (13/15 queries)
- Easy/Medium/Cross-product: **100%** | Adversarial: **33.3%**
- Deprecated resources correctly flagged

> See [RESULTS.md](RESULTS.md) for per-category breakdown.

## What This Capsule Does
Pre-curates ~100 Allen Institute web pages as JSONL, embeds into FAISS, runs 20 eval
questions through retrieve-then-generate pipeline that returns cited answers.

## Evaluation
Top-5 retrieval accuracy — does the correct gold-standard URL appear in top-5?

## Required Data Assets
| File | Description |
|------|-------------|
| `corpus.jsonl` | ~100 pages: url, title, product, body_text, is_deprecated |
| `eval_queries.jsonl` | 20 questions with gold_urls, expected_product |

## Expected Outputs
| File | Description |
|------|-------------|
| `answers.jsonl` | Per-query answers with cited URLs and deprecation warnings |
| `evaluation_report.json` | Top-5 accuracy, citation precision |

## Environment
- CPU only. `sentence-transformers`, `faiss-cpu`, `anthropic`/`openai`, `pydantic`, `pandas`, `numpy`
