# Claude Code Mission: Challenge 14 — Segment Intestine Villi (Round 2)

## Context
Existing code: run.py (6KB). Villus segmentation on spatial transcriptomics data.

## CRITICAL: EXECUTION + PROOF
1. Read existing code, run the pipeline
2. Verify: 4 GeoJSON boundary files (strategies A/B/C/D) - POLYGON geometries, not just cluster IDs
3. Verify: strategy_comparison.csv, villus_assignments.csv, per_villus_summary.csv
4. Verify: villus_segmentation_qc.png (6-panel figure)
5. Verify: segmentation_report.json with PARTIAL status (if simulated data)
6. Verify: >50% of villi have 50-800 cells
7. Fix anything broken and re-run
8. All results to /results/, backup to /results/backup/code/
