# Challenge 08 — Query BFF: Natural Language Search for BioFileFinder Metadata

## Original Challenge
Build a natural language query interface for BioFileFinder cell imaging metadata from the Allen Cell Collection.

## Intended Goal
Auto-extract schema from any BFF-compatible manifest, translate plain-English researcher questions into validated schema-grounded filters using AWS Bedrock, execute filters against the manifest, and evaluate with a gold-standard query set.

## Initial State
A working NL-to-filter pipeline with schema extraction, Bedrock integration, and evaluation existed. Real BFF metadata was attached as a data asset.

## Improvement Plan
Add second manifest generalization, HGNC synonym resolution, overconfident-wrong detection, no-results explanation, and expand to 25+ evaluation queries.

## Final Implementation
The capsule loads real Allen Cell Collection metadata (BFF manifest), auto-extracts schema (field names, types, enumerated values), uses Bedrock to translate natural language queries into filter expressions, validates filters against the schema, and executes against the manifest using pandas.

## Final Result
Produces evaluation_report.json with 75% success rate on 4 real queries against 395-row MYH10 manifest, extracted_schema.json (26KB with full field metadata). Includes confidence scoring and explanations for each query.

## Evaluation
This is the best capsule overall. It uses real attached data (not synthetic), has a working App Panel with a query parameter, provides honest accuracy metrics, and demonstrates the full NL-to-data pipeline. The 75% accuracy on real data is credible and honest.

## Remaining Limitations
Evaluation set is small (4 queries in latest run). The plan called for 25+ queries and second manifest testing. Complex queries involving substring matching or multiple conditions sometimes fail.

## Overall Verdict
Completed. The strongest capsule — real data, honest metrics, working App Panel interface. The only capsule where a researcher could immediately use it as a tool.

## Usage Documentation
The capsule has a detailed README.md and App Panel configuration.

## Final Runnable State
Clean `/code/run` entrypoint. Runs standalone with or without App Panel query parameter.
