You are running Round 2 REPAIR for this hackathon challenge capsule.

## Mission
1. Read the challenge spec from /data/hackathon_challanges/ (find the matching challenge_XX_.md file)
2. Read the Round 2 planning reports from /results/reports/ if they exist
3. Read ALL current code in /code/
4. Inspect ALL data in /data/

## Critical Rules — ZERO FABRICATED DATA
- NEVER generate synthetic, fake, mock, or placeholder data
- NEVER hardcode results or outputs that should come from real computation
- If real data is needed and not available in /data/, write code that downloads it from public sources (APIs, S3, etc.) or fails with a clear error
- All results must come from real computation on real data
- If the challenge requires data you cannot access, document the blocker honestly

## Requirements
1. Fix all code issues identified in the planning reports
2. Make /code/run work end-to-end as a bash entrypoint (#!/usr/bin/env bash, set -euo pipefail)
3. Make the capsule usable as an App Panel app where possible (CLI params via --flags)
4. Ensure all outputs go to /results/
5. Use AWS Bedrock for any LLM calls (boto3 bedrock-runtime, NOT direct Anthropic/OpenAI)
6. Write clean, documented Python code
7. Test by running the code and verifying outputs exist and contain real data

## Deliverables to /results/
- All challenge-required output files
- /results/CHALLENGE_REPORT.md — summary of what was built, what works, what's blocked
- /results/DATA_PROVENANCE.md — document every data source (real vs downloaded vs computed)

## After fixing, run the code to verify it works. Do NOT leave fabricated data. Either fix or document blockers honestly.
