# How to Implement: Agentic Data Harmonization — For Your Own Data

> **Goal**: Map cell type labels from *your* single-cell datasets to standardized
> Cell Ontology (CL) terms using a multi-strategy pipeline (expert overrides,
> abbreviation expansion, fuzzy matching, optional LLM validation).

---

## 1. What You Need (Your Data)

### Input Data Format

You need **three** types of data:

| Input | Format | Example |
|-------|--------|---------|
| **Your cell type labels** | CSV or TSV with a column of cell type label strings | `cluster_label`, `cell_type`, `annotation` |
| **Cell Ontology reference** | OBO file (`cl.obo`) from [Cell Ontology](http://obofoundry.org/ontology/cl.html) | Standard ontology file |
| **Gold-standard mappings** (optional) | CSV with columns `label` → `CL_term` for evaluation | Used to measure precision/recall |

### What Your Data Should Look Like

```
# your_taxonomy.csv
label
"GABAergic neuron"
"L2/3 IT cortical neuron"
"Pvalb+ interneuron"
"Astrocyte - fibrous"
"OPC"
...
```

- Each row is a unique cell type label from your experiment
- Labels can be messy (abbreviations, lab-specific naming, mixed case)
- No limit on number of labels — the pipeline handles thousands

---

## 2. Step-by-Step: Recreate This Capsule with Aqua

### Step 1: Create a New Capsule

> **Ask Aqua:**
> *"Create a new capsule called 'Cell Type Harmonization — [My Project Name]' with Python 3.10 environment and packages: pandas, rapidfuzz, boto3, pronto"*

### Step 2: Prepare Your Data as a Data Asset

1. Upload your cell type label CSV and the Cell Ontology OBO file as a **data asset**
2. If you have gold-standard mappings for evaluation, include those too

> **Ask Aqua:**
> *"Create a data asset from S3 bucket [your-bucket] with prefix [your-prefix] named 'my-cell-type-data', then attach it to my capsule"*

**Or** if uploading from the UI: go to **Data Assets → New Data Asset → Upload** and include:
```
my_data/
├── my_taxonomy.csv          # Your cell type labels
├── cl.obo                   # Cell Ontology (download from OBO Foundry)
└── gold_mappings.csv        # Optional: known correct mappings for eval
```

### Step 3: Attach Data to Your Capsule

> **Ask Aqua:**
> *"Attach data asset 'my-cell-type-data' to my capsule mounted at /data/my_taxonomy"*

### Step 4: Adapt the Code

> **Ask Aqua:**
> *"Modify run.py to read cell type labels from /data/my_taxonomy/my_taxonomy.csv (column 'label') and map them to Cell Ontology terms using the harmonization pipeline. Write results to /results/mapping_table.csv"*

Key customization points:
- **Label column name**: Tell Aqua which column contains your cell type strings
- **Expert overrides**: If you have domain-specific abbreviations (e.g., "PV" → "Parvalbumin-expressing neuron"), provide a mapping dict
- **Confidence threshold**: Default is 0.8 for fuzzy matching; adjust based on your naming conventions
- **LLM validation**: Enable if you have AWS Bedrock access for low-confidence mappings

### Step 5: Run

> **Ask Aqua:**
> *"Run my capsule"*

---

## 3. Outputs You'll Get

| File | What It Contains |
|------|-----------------|
| `mapping_table.csv` | Every label → CL term with confidence score and method used |
| `provenance.jsonl` | Audit trail: why each mapping was chosen |
| `review_queue.json` | Labels below confidence threshold needing human review |
| `eval_report.json` | Precision/recall/F1 (only if gold-standard provided) |

---

## 4. Adapting for Different Use Cases

### Use Case A: Cross-study integration
You have multiple single-cell studies with different taxonomies. Run the pipeline on each study's labels separately, then join on the standardized CL terms.

> **Ask Aqua:**
> *"Run the harmonization for each of my three studies and create a combined mapping table showing which labels from Study A, B, and C map to the same CL terms"*

### Use Case B: Custom ontology (not Cell Ontology)
Replace `cl.obo` with your own ontology OBO/OWL file. Update the code to load your ontology terms.

> **Ask Aqua:**
> *"Modify the pipeline to use my custom ontology at /data/my_ontology.obo instead of Cell Ontology"*

### Use Case C: Non-brain tissues
The expert override mappings in this capsule are brain-focused. Clear them and let fuzzy matching + LLM handle your tissue-specific labels.

> **Ask Aqua:**
> *"Remove the brain-specific expert overrides and rely on fuzzy matching for my [tissue type] labels"*

---

## 5. Tips

- **Start small**: Test with 50–100 labels first to calibrate confidence thresholds
- **Review the review queue**: Low-confidence mappings often reveal systematic naming issues
- **Save gold mappings**: After manual review, save corrected mappings as a new gold-standard for future runs
- **Versioning**: Capture results as a data asset after each run for reproducibility

---

## 6. Environment Requirements

| Package | Purpose |
|---------|---------|
| `pandas` | Data manipulation |
| `rapidfuzz` | Fuzzy string matching |
| `pronto` | OBO ontology parsing |
| `boto3` | AWS Bedrock for LLM validation (optional) |

**Compute**: CPU only, X-Small tier sufficient for up to 10,000 labels
