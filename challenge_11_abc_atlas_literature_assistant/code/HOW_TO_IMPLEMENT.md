# How to Implement: ABC Atlas Literature Assistant — For Your Own Data

> **Goal**: Build a literature retrieval agent that contextualizes *your* dataset
> or atlas within published research, classifying papers as source/reuse/validation
> studies with passage-level evidence and grounded citations.

---

## 1. What You Need (Your Data)

### Input Data Format

| Input | Format | Description |
|-------|--------|-------------|
| **Paper corpus** | JSONL file | ~50–200 papers with title, abstract, DOI, year |
| **Paper embeddings** (optional) | NumPy `.npy` file | Pre-computed dense vectors for similarity search |
| **Domain taxonomy** (optional) | JSON | Your dataset's cell type / entity taxonomy |
| **Evaluation queries** (optional) | JSON | Test questions with expected relationship types |

### What Your Data Should Look Like

```jsonl
// papers.jsonl — one JSON object per line
{"doi": "10.1234/example.2024", "title": "Single-cell atlas of the human cortex", "abstract": "We present a comprehensive...", "year": 2024, "authors": ["Smith J", "Lee K"]}
{"doi": "10.5678/example.2023", "title": "Validation of cortical cell types using Patch-seq", "abstract": "Using the recently published atlas...", "year": 2023, "authors": ["Chen M"]}
```

```json
// eval_queries.json — optional, for benchmarking
[
  {
    "query": "Which papers originally defined the L2/3 IT neuron type?",
    "expected_relationship": "SOURCE",
    "expected_dois": ["10.1234/example.2024"]
  },
  {
    "query": "What studies validated the glutamatergic cell type taxonomy?",
    "expected_relationship": "VALIDATION"
  }
]
```

```
my_literature/
├── papers.jsonl               # Your paper corpus
├── paper_embeddings.npy       # Optional: pre-computed embeddings
├── taxonomy.json              # Optional: your dataset's entity types
└── eval_queries.json          # Optional: test queries
```

**Key requirements:**
- Each paper must have at least `title` and `abstract`
- DOIs strongly recommended for citation linking
- 50–200 papers is a sweet spot; more is fine but slower to embed
- Abstracts should be full text (not truncated)

---

## 2. Step-by-Step: Recreate This Capsule with Aqua

### Step 1: Create a New Capsule

> **Ask Aqua:**
> *"Create a new capsule called 'Literature Assistant — [My Dataset Name]' with Python 3.10, and install packages: numpy, pandas, rapidfuzz, boto3, pydantic"*

### Step 2: Collect Your Paper Corpus

Build your JSONL corpus from PubMed, Semantic Scholar, or your reference manager:

> **Ask Aqua:**
> *"Create a data asset called 'my-paper-corpus' with my papers.jsonl and optional embeddings, then attach it at /data/literature"*

**Tip**: Export from Zotero/Mendeley → BibTeX → convert to JSONL, or use the Semantic Scholar API.

### Step 3: Adapt the Pipeline

> **Ask Aqua:**
> *"Modify run.py to load papers from /data/literature/papers.jsonl. Configure the relationship classifier to use these categories: SOURCE (papers that created/defined the dataset), REUSE (papers that used the dataset for new analyses), VALIDATION (papers that independently validated findings), MENTION (papers that cite but don't use the data)."*

### Step 4: Run Queries

> **Ask Aqua:**
> *"Run my capsule with the 5 evaluation queries to test retrieval quality"*

---

## 3. Outputs You'll Get

| File | What It Contains |
|------|-----------------|
| `demo_outputs.json` | Per-query answer with citations, relationship labels, and evidence passages |
| `eval_report.json` | Citation verification stats and retrieval accuracy |

---

## 4. Adapting for Different Use Cases

### Use Case A: Drug discovery literature
Track how your compound/target is discussed in publications.

> **Ask Aqua:**
> *"Configure relationship types for drug discovery: DISCOVERY (first reports of compound), MECHANISM (papers on mechanism of action), CLINICAL (clinical trial results), REVIEW (review articles)."*

### Use Case B: Dataset provenance tracking
Understand how a public dataset has been used by the community.

> **Ask Aqua:**
> *"Build a literature graph showing which papers cite my dataset, what analyses they performed, and whether they reproduced or extended our findings."*

### Use Case C: Systematic review assistant
Semi-automate literature screening for a review paper.

> **Ask Aqua:**
> *"Adapt as a screening tool: classify each paper as INCLUDE/EXCLUDE/MAYBE for my systematic review on [topic]. Add screening criteria as classification rules."*

---

## 5. Tips

- **Quality over quantity**: 100 well-curated papers beat 1000 noisy abstracts
- **Pre-compute embeddings**: If your corpus doesn't change often, save embeddings to avoid recomputation
- **Relationship labels matter**: Define categories that match your actual research questions
- **Iterate on queries**: Start with 5 test queries, review results, refine the prompt/classification
- **Evidence passages**: The system extracts specific sentences — use them to verify classifications

---

## 6. Environment Requirements

| Package | Purpose |
|---------|---------|
| `numpy` | Embedding operations, similarity search |
| `pandas` | Data manipulation |
| `rapidfuzz` | Fuzzy text matching for entity resolution |
| `boto3` | AWS Bedrock for LLM-powered classification |
| `pydantic` | Data validation |

**Compute**: CPU only, X-Small tier sufficient for <200 papers
**LLM**: AWS Bedrock (Claude) for answer generation and classification
