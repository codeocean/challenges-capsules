# Challenge 08: Your Query BFF (BioFileFinder)


## Results Summary
- **Query Accuracy:** 75% (3/4 correct on real BFF data)
- **Data Source:** Real Allen Cell Collection MYH10 metadata (395 rows)
- **LLM:** Bedrock Claude Sonnet

> See [RESULTS.md](RESULTS.md) for per-query results and schema details.

## What This Capsule Does

Translates natural-language questions about Allen Cell Collection metadata into
schema-grounded structured filters using **AWS Bedrock** (Claude), then executes
them against a BioFileFinder metadata manifest via pandas.

## Two Modes

### 1. Agentic / Single Query Mode (for Aqua)

Pass `--query "your question"` to translate one NL question into filters and
get back a structured JSON answer with matching rows.

```bash
python /code/run.py --query "Show me lamin B1 images"
```

**Output**: `/results/query_answer.json` with filters, explanation, result
count, and up to 10 sample rows.

This is the mode Aqua uses when invoked via `run_capsule()` with a named
parameter `query`.

### 2. Evaluation Mode (batch)

Run without `--query` to execute all 15 gold-standard evaluation queries and
compute precision/recall/F1 metrics.

```bash
python /code/run.py
```

**Output**: `/results/evaluation_report.json` with per-query results and
aggregate success rate.

## LLM Integration

- **Provider**: AWS Bedrock Runtime (Converse API)
- **Model**: Claude Sonnet 4 with automatic fallback chain
- **Credentials**: Code Ocean managed IAM — no API keys needed
- **No direct Anthropic or OpenAI API calls**

## Data

| File | Description |
|------|-------------|
| `bff_manifest.parquet` | BFF metadata manifest (attach as data asset, or synthetic generated) |
| `eval_queries.json` | 15 evaluation queries with gold filters (embedded in code if missing) |

## Outputs

| File | Description |
|------|-------------|
| `query_answer.json` | Single-query answer (agentic mode) |
| `evaluation_report.json` | Full evaluation results (batch mode) |
| `extracted_schema.json` | Runtime-extracted manifest schema |

## App Panel

The capsule has an App Panel with one parameter:
- **Query**: Natural-language question. Leave empty for evaluation mode.

## Environment

- Python 3.10+, CPU only
- `boto3`, `pandas`, `pyarrow`, `pydantic`, `numpy`
