You are running Round 2 REPAIR for Challenge 08: Query BFF (BioFileFinder).

## Mission
1. Read /data/hackathon_challanges/challenge_08_your_query_bff.md
2. Read the Round 2 planning reports from /results/reports/ if they exist
3. Read ALL current code in /code/ — the NL-to-filter pipeline is already working
4. Real data is at /data/bff_metadata/ (3 CSV files from Allen Cell Collection)

## Critical Rules — ZERO FABRICATED DATA
- NEVER generate synthetic data. Real CSVs are in /data/bff_metadata/
- All query results must come from real filtering on real manifest data
- The generate_manifest() function must NOT exist in the code

## What needs fixing
1. Ensure /code/run runs python directly (no Claude Code launcher)
2. Verify the App Panel works with --query parameter
3. Add HTML results summary (results_summary.html) for App Panel display
4. Ensure evaluation queries are derived from real data values
5. Test with real NL queries and verify results are real

## Deliverables: query_answer.json, evaluation_report.json, extracted_schema.json, results_summary.html, CHALLENGE_REPORT.md, DATA_PROVENANCE.md
