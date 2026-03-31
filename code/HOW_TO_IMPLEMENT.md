# How to Implement: Query BFF (Natural Language Search) — For Your Own Data

> **Goal**: Build a natural language query interface for *your* metadata manifest
> (CSV or Parquet) that translates plain-English questions into schema-grounded
> filters, executes them, and returns matching results with explanations.

---

## 1. What You Need (Your Data)

### Input Data Format

| Input | Format | Description |
|-------|--------|-------------|
| **Metadata manifest** | CSV or Parquet | Your structured metadata with columns for filtering |
| **Evaluation queries** (optional) | JSON array | Gold-standard questions with expected filters for benchmarking |

### What Your Data Should Look Like

```csv
# my_manifest.csv — any structured metadata table
file_id,gene,structure_name,cell_line,plate,imaging_mode,fov_id
ABC001,LMNB1,nuclear envelope,hIPSC,P001,3D,FOV_001
ABC002,NPM1,nucleolus,hIPSC,P002,3D,FOV_002
ABC003,MYH10,actomyosin bundles,hIPSC,P001,timelapse,FOV_003
...
```

**Key requirements:**
- Must be a flat table (CSV or Parquet) — no nested JSON
- Column names should be human-readable (the LLM uses them for schema grounding)
- Enumerated/categorical columns work best (gene names, cell lines, imaging modes)
- Numeric columns supported for range queries
- Any domain: biology, imaging, clinical, environmental, etc.

**Optional: Evaluation queries**
```json
// eval_queries.json
[
  {
    "question": "Show me all lamin B1 images",
    "expected_filters": {"gene": "LMNB1"},
    "expected_min_results": 10
  },
  {
    "question": "Find 3D images of nucleolus structures on plate P002",
    "expected_filters": {"structure_name": "nucleolus", "imaging_mode": "3D", "plate": "P002"}
  }
]
```

---

## 2. Step-by-Step: Recreate This Capsule with Aqua

### Step 1: Create a New Capsule

> **Ask Aqua:**
> *"Create a new capsule called 'NL Query Interface — [My Dataset Name]' with Python 3.10, and install packages: boto3, pandas, pyarrow, pydantic, numpy"*

### Step 2: Prepare Your Manifest

> **Ask Aqua:**
> *"Create a data asset called 'my-metadata-manifest' containing my CSV manifest file, then attach it at /data/manifest"*

Upload:
```
manifest/
├── my_manifest.csv           # or .parquet
└── eval_queries.json         # optional
```

### Step 3: Adapt the Code

> **Ask Aqua:**
> *"Modify run.py to load the metadata manifest from /data/manifest/my_manifest.csv. The schema auto-extraction should detect all columns, their types, and enumerate unique values for categorical columns."*

The pipeline will automatically:
1. Extract the schema (field names, types, unique values)
2. Build a prompt that grounds the LLM on your specific schema
3. Translate natural language → structured filters
4. Execute filters via pandas
5. Return results with explanations

### Step 4: Set Up the App Panel

> **Ask Aqua:**
> *"Set up an App Panel with a 'query' parameter (text type) so users can type natural language questions"*

### Step 5: Run

**Single query mode:**
> **Ask Aqua:**
> *"Run my capsule with query='Find all samples with high expression of MYH10'"*

**Evaluation mode (batch):**
> **Ask Aqua:**
> *"Run my capsule without a query parameter to execute all evaluation queries and compute precision/recall/F1"*

---

## 3. Outputs You'll Get

| File | What It Contains |
|------|-----------------|
| `query_answer.json` | Translated filters, matching rows, explanation, confidence score |
| `evaluation_report.json` | Per-query precision/recall/F1 (evaluation mode) |
| `extracted_schema.json` | Auto-detected schema of your manifest |

---

## 4. Adapting for Different Use Cases

### Use Case A: Clinical trial metadata
Query patient cohort data with natural language.

> **Ask Aqua:**
> *"Adapt for my clinical metadata CSV with columns: patient_id, age, sex, diagnosis, treatment_arm, response, biomarker_level. Add synonym handling for medical terms."*

### Use Case B: Genomics file catalog
Search a large sequencing file manifest.

> **Ask Aqua:**
> *"Configure for my genomics manifest with columns: sample_id, organism, tissue, assay_type, read_length, file_format, file_size_gb. Add range query support for file_size_gb."*

### Use Case C: Environmental sensor data
Query IoT/sensor metadata.

> **Ask Aqua:**
> *"Adapt for my sensor data manifest: sensor_id, location, measurement_type, unit, deployment_date, status. Handle date-range queries for deployment_date."*

### Use Case D: Custom vocabulary normalization
Teach the system your domain synonyms.

> **Ask Aqua:**
> *"Add a synonym mapping: 'lamin' → 'LMNB1', 'actin' → 'ACTB', 'tubulin' → 'TUBA1B' so users can query with common names instead of gene symbols."*

---

## 5. Tips

- **Schema quality matters**: Clean, consistent column names and values improve query accuracy dramatically
- **Start with evaluation**: Create 10–15 test queries with expected answers to measure performance
- **Categorical is king**: The system works best when columns have a finite set of known values
- **Confidence scores**: Check the confidence score in results — low confidence often means ambiguous queries
- **No data copying**: The manifest stays in your data asset; queries execute locally via pandas
- **Fallback**: If AWS Bedrock is unavailable, queries will fail — ensure managed IAM credentials are configured

---

## 6. Environment Requirements

| Package | Purpose |
|---------|---------|
| `boto3` | AWS Bedrock for natural language → filter translation |
| `pandas` | Manifest loading and filter execution |
| `pyarrow` | Parquet support |
| `pydantic` | Schema validation |
| `numpy` | Numeric operations |

**Compute**: CPU only, X-Small tier sufficient
**LLM**: AWS Bedrock (Claude Sonnet) via managed credentials
