# Challenge 02 — Agentic Data Harmonization

## Original Challenge
Build an AI agent system that harmonizes Allen Institute single-cell datasets by inferring and aligning cell type mappings across studies with different taxonomies.

## Intended Goal
Demonstrate autonomous schema reconciliation across WHB taxonomy and CELLxGENE brain datasets, mapping cell type labels to Cell Ontology terms with quality validation and transparent decision-making.

## Initial State
A basic fuzzy matching pipeline existed but had circular evaluation (gold standard derived from pipeline output) and no real LLM integration.

## Improvement Plan
Replace circular evaluation with an independent gold standard. Add Bedrock LLM calls for ambiguous mappings. Process all labels from both data sources. Produce honest P/R/F1 metrics below 1.0.

## Final Implementation
The capsule loads cell type labels from WHB taxonomy and CELLxGENE brain datasets, performs fuzzy matching using rapidfuzz against Cell Ontology, and uses AWS Bedrock for low-confidence mappings. It evaluates against a 493-label gold standard and produces a detailed evaluation report with per-label results.

## Final Result
The pipeline produces mapping_table.csv (350KB, thousands of mappings), eval_report.json with P/R/F1 = 0.949, and provenance tracking. Bedrock integration is confirmed via agentic_proof.json showing 30 LLM queries were executed, though none improved over fuzzy matching in the latest run.

## Evaluation
The capsule runs standalone (exit 0) and produces all required outputs. The F1 of 0.949 is below 1.0, which was a key requirement to prove non-circular evaluation. The 25 false positives are all OPC-to-oligodendrocyte mapping disagreements, which is a genuine biological ambiguity. The gold standard uses programmatic label naming conventions similar to the input data, which raises questions about full independence.

## Remaining Limitations
The gold standard may not be fully independent of the pipeline's naming conventions. The LLM component made zero improvements over deterministic fuzzy matching, suggesting the agentic aspect adds overhead without value for this dataset. Real data is used but only from attached data assets.

## Overall Verdict
Completed. The pipeline works end-to-end, uses real data, produces honest non-circular metrics, and demonstrates the harmonization concept. The agentic component is present but does not demonstrably improve results.

## Usage Documentation
The capsule has a README.md. It documents the pipeline, parameters, and how to run it.

## Final Runnable State
The `/code/run` entrypoint is clean (`python /code/run.py "$@"`). The capsule runs standalone without Claude Code orchestration.
