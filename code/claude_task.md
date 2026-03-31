# Claude Code Mission: Challenge 03 — Enhancer Designer (Round 2)

## Context
Existing code: run.py, generate.py, score.py, report.py. The GA framework and oracle are already implemented.

## CRITICAL: This round focuses on EXECUTION + PROOF
1. Read ALL existing code files
2. Run the pipeline: python /code/run.py
3. Verify outputs: stats.json has all required fields, evolved_top20.fasta exists, cross-oracle validation done
4. Check: p < 0.01 for evolved vs random, shuffled, AND seeds
5. Check: anti-overfitting pass (mean pairwise edit distance > 0.10)
6. If anything fails, fix and re-run
7. Write all results to /results/, backup code to /results/backup/code/

## Required Outputs
- /results/stats.json (with evolved_vs_seeds, cross_oracle_validation)
- /results/evolved_top20.fasta
- /results/k562_seeds.fasta
- /results/oracle_model.pt or equivalent
- /results/manifest.json
