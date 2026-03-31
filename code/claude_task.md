# Claude Code Mission: Challenge 04 — Light Sheet Alignment QC (Round 2)

## Context
Existing code: run.py (38KB), generate_pairs.py, visualize.py. Pipeline already has 4 models + calibration.

## CRITICAL: EXECUTION + PROOF
1. Read existing code, then run: python /code/run.py --mode smoke-test (or full)
2. Verify all outputs exist: model_comparison.csv (4 models), calibration_report.json, metrics.json
3. Verify figures: roc_curves.png, confusion_matrices.png, example_gallery.png, calibration_reliability.png, threshold_decision_map.png
4. Verify: calibration review_rate < 20%, at least one learned model beats classical baseline
5. Verify: pipeline_integration.md exists with architecture diagram
6. Fix anything broken and re-run
7. All results to /results/, backup to /results/backup/code/
