# Capsule 04 — Light Sheet Alignment QC — Protocol Progress

## Status: NEEDS_PROTOCOL_COMPLIANCE

## Capsule ID: 66d8d446-c416-4296-9677-585b870524d0
## Slug: 0359654

## Assessment
- **Code state**: run.py (37K, comprehensive QC pipeline), generate_pairs.py (synthetic data), visualize.py (reports)
- **Previous runs**: 16+ rounds of iteration, latest "FINAL (Round 16, 8/8 targets, 93.8% acc, AUC=0.977)"
- **Quality**: STRONG — real ML pipeline with LogisticRegression ensemble, isotonic calibration, 5-feature extraction
- **Key metrics**: AUC 0.977, PR-AUC 0.969, 93.8% accuracy, 92.6% precision on failures
- **Baseline comparison**: Ensemble (AUC 0.977) vs SSIM-only (AUC 0.789)
- **LLM needed**: NO — computational image analysis
- **Outputs**: 19 files including HTML report, ROC/PR curves, confusion matrix, severity breakdown

## Protocol Defects
1. Layout non-compliant: All outputs flat in /results/ instead of /results/code/, /results/reports/, /results/outputs/
2. Unclear Claude Code provenance
3. No LLM needed — Bedrock compliance N/A

## What's Strong
- Substantive ML pipeline (not stubs)
- 5 image features (SSIM, NCC, edge continuity, MI, gradient similarity)
- Isotonic calibration for reliable confidence scores
- 3-class output (pass/fail/needs_review)
- Per-severity evaluation
- Comprehensive HTML evaluation report with embedded figures
- Honest validation notes about synthetic-only limitation

## Next Step
Create Claude Code TASK.md for layout compliance, run, evaluate
