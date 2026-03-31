# PROGRESS.md — Capsule 10: NeuroBase

## Status: ❌ FAILING

## Current State
- /code/: run.py (11,772B), run — code exists but fails
- Environment: GPU PyTorch, pip: matplotlib, numpy, pandas, pynrrd, scikit-learn, torch
- Latest run: exit_code=1, has_results=false
- Git: NO implementation commit

## Root Cause (Likely)
- Missing data assets: brain_volume.nrrd, annotation.nrrd, neurobase_weights/, region_mapping.json
- These must be attached as data assets or generated synthetically
- GPU capsule — may need specific GPU availability

## Fix Needed
1. Diagnose exact error (run and read output log)
2. Create synthetic data generation or attach real data assets
3. Delegate fix to Claude Code (NOT Aqua direct edit)
4. Run, verify exit_code=0
5. Commit code
6. Iterate 3 rounds minimum
