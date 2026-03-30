# Challenge 02: Agentic Data Harmonization

## What This Capsule Does

Takes cell type labels from two different neuroscience datasets, matches each label
to a Cell Ontology term using fuzzy string matching and synonym lookup, and outputs
a mapping table split into mapped / needs-review / unmapped buckets.

## Evaluation Criteria

Precision and recall of the mappings against a hand-curated gold standard of 30–50
label pairs.

## Required Data Assets

Attach a data asset containing:

| File | Description |
|------|-------------|
| `labels_a.csv` | Unique cell type labels from ABC Atlas (column: `label`) |
| `labels_b.csv` | Unique cell type labels from a GEO study (column: `label`) |
| `cl.obo` | Cell Ontology OBO file (~15 MB, from OBO Foundry) |
| `gold_mappings.csv` | 30–50 hand-curated mappings: `source_label`, `cl_id`, `cl_name` |

## Expected Outputs

| File | Description |
|------|-------------|
| `mapping_table.csv` | `source_label`, `cl_id`, `cl_name`, `confidence`, `status` |
| `eval_report.json` | Precision, recall, F1, and bucket counts |

## Environment

- Python 3.10+, CPU only
- `pandas`, `pronto`, `rapidfuzz`
