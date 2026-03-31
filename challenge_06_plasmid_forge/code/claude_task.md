# Claude Code Mission: Challenge 06 — Plasmid Forge (Round 2)

## Context
Existing code: run.py, create_data.py. Pipeline has Strands agent + pydna assembly.

## CRITICAL: EXECUTION + PROOF
1. Read existing code, run the pipeline on all 6 test cases
2. Verify: evaluation_summary.json shows >= 4/6 tests pass
3. Verify: safety test blocks dangerous request (botulinum toxin)
4. Verify: construct.gb and construct.fasta produced for valid requests
5. Verify: synthesis_readiness.json, ordering_sheet.json exist
6. Fix anything broken and re-run
7. All results to /results/, backup to /results/backup/code/
