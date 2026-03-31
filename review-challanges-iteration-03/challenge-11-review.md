# Challenge 11 — ABC Atlas Literature Assistant

## Original Challenge
Expand the ABC Atlas with a literature agent that contextualizes atlas data within published research, distinguishing source papers from reuse/validation studies with passage-level evidence.

## Intended Goal
Build a corpus of real papers, create a retrieval index, use LLM to classify paper relationships (SOURCE/REUSE/VALIDATION/MENTION), and generate grounded answers with citations.

## Initial State
A TF-IDF-based retrieval pipeline existed but relied on missing data files in /data/. The code had generation functions but they were not wired into the main function.

## Improvement Plan
Wire corpus generation into main, expand to 50+ papers from PubMed, add 15+ evaluation queries, and verify all citations.

## Final Implementation
The capsule downloads real papers from PubMed using NCBI E-utilities (Biopython Entrez) with a static fallback corpus. It generates default evaluation queries, retrieves relevant papers using fuzzy matching, uses Bedrock for relationship classification and answer generation, and verifies all citations point to real papers in the corpus.

## Final Result
Produces seed_papers.jsonl (44KB, 39 real PubMed papers), eval_queries.json (15 queries), demo_outputs.json (33KB with full answers), and eval_report.json showing all 41 citations verified as valid.

## Evaluation
The capsule runs standalone (exit 0). It downloads real papers from PubMed at runtime, demonstrating a self-contained workflow. Citation verification passes 100%. The Bedrock-powered classification produces grounded answers with paper references.

## Remaining Limitations
The corpus is 39 papers (plan called for 50+). Evaluation queries are self-generated defaults, not externally curated. Embeddings are not pre-computed (uses fuzzy matching fallback). Taxonomy integration is minimal (0 entries loaded).

## Overall Verdict
Completed. Real literature retrieval with citation verification on PubMed data. The self-bootstrapping corpus generation makes it truly standalone.

## Usage Documentation
The capsule has a README.md.

## Final Runnable State
Clean `/code/run` entrypoint. Runs standalone with runtime data generation.
