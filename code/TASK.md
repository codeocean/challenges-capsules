You are running Round 2 REPAIR for this hackathon challenge capsule.

## Mission
1. Read the challenge spec from /data/hackathon_challanges/ (find the matching challenge_XX_.md file)
2. Read the Round 2 planning reports from /results/reports/ if they exist
3. Read ALL current code in /code/
4. Inspect ALL data in /data/

## Critical Rules — ZERO FABRICATED DATA
- NEVER generate synthetic, fake, mock, or placeholder data
- NEVER hardcode results or outputs that should come from real computation
- All results must come from real computation on real data
- If the challenge requires data you cannot access, document the blocker honestly

## Requirements
1. Fix all code issues identified in the planning reports
2. Make /code/run work end-to-end as a bash entrypoint
3. Make the capsule usable as an App Panel app where possible
4. Ensure all outputs go to /results/
5. Use AWS Bedrock for any LLM calls (boto3 bedrock-runtime, NOT direct Anthropic/OpenAI)
6. Test by running the code and verifying outputs exist and contain real data

## Deliverables: challenge outputs + /results/CHALLENGE_REPORT.md + /results/DATA_PROVENANCE.md
Do NOT leave fabricated data. Either fix or document blockers honestly.
