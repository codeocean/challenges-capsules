# Working Capsules Summary — Iteration 03

## Overview

Of the 15 challenge capsules, 14 now run standalone and produce results. One capsule (Challenge 10) remains blocked due to a persistent environment build failure. All 14 working capsules have clean `/code/run` entrypoints free of Claude Code orchestration template logic.

## Status Table

| # | Challenge | Status | Exit | Results | Clean Run | README |
|---|-----------|--------|------|---------|-----------|--------|
| 02 | Agentic Data Harmonization | Completed | 0 | Yes | Yes | Yes |
| 03 | Enhancer Designer | Completed | 0 | Yes | Yes | Yes |
| 04 | Light Sheet Alignment QC | Completed | 0 | Yes | Yes | Yes |
| 05 | Automate Your Productivity | Partially completed | 0 | Yes | Yes | Yes |
| 06 | Plasmid Forge | Partially completed | 0 | Yes | Yes | Yes |
| 07 | Engineering Automation | Completed | 0 | Yes | Yes | Yes |
| 08 | Query BFF | Completed | 0 | Yes | Yes | Yes |
| 09 | BindCrafting | Partially completed | 0 | Yes | Yes | Yes |
| 10 | NeuroBase Evaluation | **Blocked** | 1 | No | Yes | No |
| 11 | ABC Atlas Literature | Completed | 0 | Yes | Yes | Yes |
| 12 | Brain Map + BKP | Completed | 0 | Yes | Yes | Yes |
| 13 | Croissant Pipeline | Completed | 0 | Yes | Yes | Yes |
| 14 | Segment Intestine Villi | Completed | 0 | Yes | Yes | Yes |
| 15 | Model Pantry | Partially completed | 0 | Yes | Yes | Yes |
| 16 | SciDEX | Completed | 0 | Yes | Yes | Yes |

## Completed Capsules (10)

These capsules run standalone, produce meaningful results, and demonstrate the core challenge requirement.

- **Ch02** — Maps cell types across WHB and CELLxGENE taxonomies using fuzzy matching + Bedrock LLM. Produces mapping_table.csv and evaluation with P/R/F1 = 0.949 on 493 gold labels.
- **Ch03** — Genetic algorithm evolves enhancer DNA sequences scored by PWM-based oracle. Produces top20.fasta with statistically significant improvement (p < 1e-12).
- **Ch04** — Multi-model ML pipeline for light sheet microscopy QC. Produces predictions, ROC/PR curves, confusion matrices with 93.8% accuracy on synthetic data.
- **Ch07** — Bedrock-powered code repair agent on 15 test tasks across bugfix, migration, refactoring, and won't-fix categories. Resolves 5/15 with honest cost tracking.
- **Ch08** — Natural language query interface for BioFileFinder metadata on real Allen Cell Collection data. 75% accuracy with schema auto-extraction and Bedrock-powered filter generation.
- **Ch11** — Literature retrieval agent over 39 real PubMed papers about Allen Brain Cell Atlas. 15 queries with citation verification and Bedrock-powered classification.
- **Ch12** — Knowledge assistant for brain-map and BKP resources. 86.7% accuracy on 15 queries including adversarial out-of-corpus tests (33% adversarial accuracy proves honest limits).
- **Ch13** — Croissant JSON-LD metadata pipeline for scRNA-seq data. Generates h5ad, exports CSV, builds Croissant metadata, validates with mlcroissant.
- **Ch14** — Spatial segmentation of intestinal villi using Leiden clustering on squidpy neighbor graphs. Produces GeoJSON boundaries, per-villus summary, and spatial plots on synthetic data.
- **Ch16** — Two-session hypothesis workbench with SQLite persistence. Generates and critiques hypotheses from PubMed corpus, tracks score evolution across sessions.

## Partially Completed Capsules (4)

These capsules run and produce output, but have significant limitations.

- **Ch05** — Runs in MOCK_MODE. Missing key artifacts (ICS calendar file, audit log). Pattern detection works but automation workflow is incomplete.
- **Ch06** — Only 1 of 6 test cases passes (safety refusal). Core plasmid design fails for standard requests. Heuristic fallback parser works but part selection is too limited.
- **Ch09** — All binder candidates are simulated. No real BindCraft or AlphaFold2 code exists. GPU upgraded to g6e.8xlarge but unused. Pipeline demonstrates the analysis framework only.
- **Ch15** — PCA baseline produces F1 = 1.0 on trivially separable synthetic data. scVI adapter crashes due to torchvision dependency (fix in progress). Benchmark framework exists but results are not meaningful.

## Blocked Capsules (1)

- **Ch10** — Environment build failure prevents any standalone run. Latest bare run exits with code 1 after 597 seconds. The code has download paths for Allen CCFv3 data and synthetic fallback, but runtime crashes persist. NeuroBase model weights are unavailable (organizer-provided). Only baseline evaluation is feasible.

## Important Caveats

- Capsules Ch03, Ch04, Ch09, Ch13, Ch14, Ch15 use **synthetic data** instead of real experimental data. This is clearly labeled in their outputs.
- Capsules Ch02, Ch06, Ch07, Ch09, Ch11, Ch16 use **AWS Bedrock** for LLM calls, with fallback paths when Bedrock is unavailable.
- Ch08 is the only capsule validated on **real attached data** (BFF metadata from Allen Cell Collection).
- Ch12's evaluation includes **adversarial queries** that intentionally fail, proving honest evaluation.
- No capsule has been **released** as an immutable version yet.
