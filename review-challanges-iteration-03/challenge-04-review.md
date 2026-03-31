# Challenge 04 — Light Sheet Alignment QC

## Original Challenge
Build a quality control system for light-sheet microscopy image registration that automatically detects alignment failures and routes uncertain cases to human review.

## Intended Goal
Implement multiple ML models that classify image pairs as aligned, uncertain, or misaligned, outperforming baseline metrics with calibrated decision thresholds.

## Initial State
A multi-model ML pipeline existed with synthetic data generation, achieving over 90% accuracy.

## Improvement Plan
Verify 4 distinct model types, add calibration report with Platt-scaled probabilities, improve synthetic data realism, and prepare for real AIND data integration.

## Final Implementation
The capsule generates synthetic image pairs with physics-informed perturbations, trains and evaluates multiple models (classical baseline with SSIM/NCC features, ResNet-style CNN, DINOv2/ViT features, and Siamese CNN), produces calibrated three-tier decisions, and generates comprehensive visualizations.

## Final Result
Produces predictions.csv (55KB), ROC curves, PR curves, confusion matrices, score histograms, severity breakdowns, example gallery (1.6MB), and a full HTML evaluation report (14MB). Reports 93.8% accuracy with AUC = 0.977.

## Evaluation
This is the most polished capsule in terms of output quality. Rich visualizations, multiple model comparison, and calibrated decisions. All metrics are internally consistent.

## Remaining Limitations
100% synthetic data. No real AIND SmartSPIM overlap pairs have been tested. The synthetic generator approximates tissue textures and failure modes, but real-world performance is unproven. Requires real microscopy data for external validation.

## Overall Verdict
Completed. Strong ML pipeline with excellent visualization. The synthetic-only caveat is significant but the framework is ready for real data integration.

## Usage Documentation
The capsule has a README.md.

## Final Runnable State
Clean `/code/run` entrypoint. Runs standalone.
