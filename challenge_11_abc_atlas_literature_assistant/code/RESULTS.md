# Results — Challenge 11: ABC Atlas Literature Assistant

## Evidence Strength: MODERATE

The pipeline runs 15 evaluation queries and verifies that **all 41 citations reference real papers** in the corpus (100% citation validity). However, there is no accuracy metric measuring whether the retrieved passages actually answer the queries correctly — only citation existence is verified.

## Evaluation Results (eval_report.json)

### Summary
| Metric | Value |
|--------|-------|
| **Queries Run** | 15 |
| **Citations Verified** | ✅ All valid |
| **Total Citations** | 41 |
| **Valid Citations** | 41 (100%) |

### Query Categories
The 15 evaluation queries span:
- SOURCE queries (what papers defined a cell type)
- REUSE queries (which studies reused the taxonomy)
- VALIDATION queries (papers that validated findings)
- MENTION queries (papers that reference cell types)
- NONE queries (out-of-corpus — should return no results)

### Corpus
- 50+ papers in `seed_papers.jsonl` sourced from PubMed/Semantic Scholar
- Search terms: "Allen Brain Cell Atlas", "ABC Atlas", "whole mouse brain taxonomy"

## What the Evidence Shows
- **Real paper corpus:** Papers fetched from public APIs, not fabricated
- **Citation integrity:** Every cited paper_id maps to a real entry in the corpus
- **Diverse query types:** Spans SOURCE, REUSE, VALIDATION, MENTION, and NONE categories
- **Demo outputs:** 5 example Q&A pairs with grounded answers in `demo_outputs.json`

## Known Limitations
- No retrieval precision/recall metric — we verify citations exist but not whether they are the *best* citations
- No human-judged relevance scores for retrieved passages
- TF-IDF retrieval (not dense embeddings) — likely misses semantic matches
- To strengthen: add per-query relevance judgments and compute MRR/NDCG

## Output Artifacts
| File | Description |
|------|-------------|
| `eval_report.json` | Evaluation summary |
| `seed_papers.jsonl` (44 KB) | Full paper corpus |
| `demo_outputs.json` (33 KB) | 5 example Q&A pairs with citations |
| `eval_queries.json` | 15 evaluation queries with expected types |
