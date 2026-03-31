# Challenge 11: ABC Atlas Literature Assistant

## What This Capsule Does
Pre-stages ~100 papers as JSONL, runs 5 queries, retrieves passages via similarity,
classifies paper relationship (SOURCE/REUSE/VALIDATION/MENTION), generates grounded answers.

## Evaluation
Correct relationship labels and verifiable citations for each query.

## Required Data Assets
| File | Description |
|------|-------------|
| `seed_papers.jsonl` | ~100 papers with title, abstract, doi, year |
| `paper_embeddings.npy` | Pre-computed dense embeddings |
| `abc_taxonomy.json` | CCN taxonomy tree |
| `eval_queries.json` | 5 queries with expected relationship types |

## Expected Outputs
| File | Description |
|------|-------------|
| `demo_outputs.json` | Per-query answer + citations with relationships |
| `eval_report.json` | Citation verification stats |

## Environment
- CPU only. `anthropic`/`openai`, `numpy`, `pandas`, `rapidfuzz`
