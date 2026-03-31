# Claude Code Mission: Challenge 13 — Croissant Pipeline (Round 2)

## Context
Existing code: build_croissant.py, export_tables.py, validate_and_load.py. Croissant metadata packaging.

## CRITICAL: EXECUTION + PROOF
1. Read existing code, run the pipeline end-to-end
2. Verify: source_dataset.h5ad created, cell_metadata.csv (10K+ rows), gene_expression.csv
3. Verify: croissant_metadata.json passes mlcroissant validation (zero errors)
4. Verify: validation_report.json shows status=PASS, donor-aware splits verified, no leakage
5. Verify: two distributions (cell metadata + gene expression) in Croissant metadata
6. Fix anything broken and re-run
7. All results to /results/, backup to /results/backup/code/
