# Claude Code Mission: Challenge 02 — Agentic Data Harmonization (Round 2)

## Context
You have data assets mounted at /data/: WHB-taxonomy, cellxgene_brain, challenge_02_input, hackathon_challanges. 
The existing run.py has a working pipeline (~50KB). Build on it.

## CRITICAL: This round focuses on EXECUTION + PROOF
1. Read the existing run.py — it already has harmonization logic
2. Run the pipeline end-to-end and capture all outputs
3. Verify: mapping_table.csv >= 4000 rows, harmonized.parquet exists, eval_report.json has P/R/F1 < 1.0
4. If the pipeline fails, fix it and re-run
5. Write all results to /results/
6. Backup code to /results/backup/code/

## Required Outputs (verify each exists and is non-empty)
- /results/mapping_table.csv
- /results/harmonized.parquet  
- /results/harmonized_sample.csv
- /results/schema_reconciliation.json
- /results/entity_linkage.csv
- /results/data_quality_report.json
- /results/eval_report.json
- /results/provenance.jsonl
- /results/gold_standard.csv
- /results/review_queue.csv or review_queue.json
- /results/manifest.json

## Success criteria
- ALL labels processed (zero scope exclusion)
- P, R, F1 all < 1.0 (not circular)
- Harmonized output has records from both datasets
