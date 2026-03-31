# Challenge 15 — Allen Single-Cell Model Pantry

## Original Challenge
Build a reproducible benchmark system for single-cell foundation models on Allen datasets with frozen splits, shared evaluation contracts, and comparable metrics across models.

## Intended Goal
Create a benchmark with multiple model adapters (PCA baseline, scVI, scANVI, Geneformer), frozen train/test splits, KNN and linear probe evaluation, and a leaderboard comparing F1 scores.

## Initial State
A benchmark framework existed with PCA and scVI adapters, but the CC template prevented standalone execution. scVI crashed due to a missing torchvision dependency.

## Improvement Plan
Fix the entrypoint, add torchvision to resolve scVI crash, generate synthetic data when h5ad is missing, and produce meaningful benchmark results.

## Final Implementation
The capsule generates synthetic MTG-like h5ad data (10K cells, 2K genes, 10 cell types) when no real data is attached. It runs PCA baseline embedding + KNN classification, attempts scVI, and produces a leaderboard CSV and confusion matrix plots.

## Final Result
Produces leaderboard.csv, confusion_matrix_pca.png, benchmark_config.json, and summary.json. The latest successful bare run (16 seconds, exit 0) produces these artifacts. Torchvision was added to the environment to fix the scVI import chain.

## Evaluation
The capsule runs standalone (exit 0). However, the PCA baseline achieves F1 = 1.0, which is meaningless — the synthetic data is trivially separable with PCA. The scVI adapter may still crash depending on whether the torchvision fix has propagated to the build. The benchmark framework exists but produces no meaningful comparison.

## Remaining Limitations
PCA F1 = 1.0 on synthetic data proves nothing. scVI adapter may still crash. No real Allen MTG data is attached. The benchmark only demonstrates that a framework exists, not that it produces useful model comparisons. Synthetic data needs more noise/overlap between cell types.

## Overall Verdict
Partially completed. The benchmark framework runs, but the results are not meaningful because the synthetic data is trivially easy. With real data or harder synthetic data, this framework would produce useful comparisons.

## Usage Documentation
The capsule has a README.md.

## Final Runnable State
Clean `/code/run` entrypoint. Runs standalone.
