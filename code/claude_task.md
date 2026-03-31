# Claude Code Mission: Challenge 15 — Single-Cell Model Pantry (Round 2)

## Context
Existing code: run.py, adapters/scvi_adapter.py, adapters/geneformer_adapter.py.

## CRITICAL: EXECUTION + PROOF
1. Read existing code, run the pipeline
2. Verify: leaderboard.csv with at least 2 models (PCA + scVI minimum)
3. Verify: confusion matrix PNGs for each model x eval method
4. Verify: model_cards/ directory with per-model markdown
5. Verify: CONTRIBUTING.md with adapter interface documentation
6. Verify: benchmark_config.json with reproducibility info
7. Fix anything broken (e.g. Geneformer download — use scANVI fallback instead)
8. All results to /results/, backup to /results/backup/code/
