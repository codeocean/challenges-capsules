# How to Implement: Brain Map + BKP Assistant — For Your Own Data

> **Goal**: Build a grounded discovery assistant over *your* organization's
> documentation, tools, and datasets that retrieves relevant resources, explains
> matches, handles deprecated content, and evaluates retrieval quality.

---

## 1. What You Need (Your Data)

### Input Data Format

| Input | Format | Description |
|-------|--------|-------------|
| **Documentation corpus** | JSONL file | Web pages, docs, or resources with URL, title, body text |
| **Evaluation queries** | JSONL file | Test questions with gold-standard URLs/answers |

### What Your Data Should Look Like

```jsonl
// corpus.jsonl — one JSON object per line
{"url": "https://myorg.com/tools/tool-a", "title": "Tool A: Data Visualization", "product": "Analytics Suite", "body_text": "Tool A provides interactive visualization...", "is_deprecated": false}
{"url": "https://myorg.com/tools/tool-b-legacy", "title": "Tool B (Legacy)", "product": "Old Platform", "body_text": "Tool B was our original...", "is_deprecated": true, "successor": "https://myorg.com/tools/tool-c"}
{"url": "https://myorg.com/datasets/dataset-1", "title": "Gene Expression Dataset v3", "product": "Data Portal", "body_text": "This dataset contains...", "is_deprecated": false}
```

```jsonl
// eval_queries.jsonl — one per line
{"question": "Where can I find gene expression data?", "gold_urls": ["https://myorg.com/datasets/dataset-1"], "expected_product": "Data Portal"}
{"question": "How do I use Tool B?", "gold_urls": ["https://myorg.com/tools/tool-b-legacy"], "expect_deprecation_warning": true}
```

```
my_docs/
├── corpus.jsonl              # Your documentation pages
└── eval_queries.jsonl        # Test questions
```

**Key requirements:**
- Each document needs `url`, `title`, and `body_text` at minimum
- `is_deprecated` flag enables deprecation warnings in answers
- `product` field enables cross-product retrieval
- 50–500 documents is the recommended range
- Body text should be clean (no HTML tags, no navigation chrome)

---

## 2. Step-by-Step: Recreate This Capsule with Aqua

### Step 1: Create a New Capsule

> **Ask Aqua:**
> *"Create a new capsule called 'Documentation Assistant — [My Org]' with Python 3.10, and install packages: sentence-transformers, faiss-cpu, boto3, pydantic, pandas, numpy"*

### Step 2: Prepare Your Documentation Corpus

Scrape or export your documentation:

> **Ask Aqua:**
> *"Create a data asset called 'my-org-docs' with my corpus.jsonl and eval_queries.jsonl, then attach it at /data/docs"*

**Tip**: Use `wget --mirror` or a sitemap-based scraper to collect pages, then extract text with BeautifulSoup.

### Step 3: Build the Index

> **Ask Aqua:**
> *"Modify build_index.py to load documents from /data/docs/corpus.jsonl, embed them with sentence-transformers, and build a FAISS index."*

### Step 4: Configure the RAG Pipeline

> **Ask Aqua:**
> *"Set up the retrieve-then-generate pipeline: for each user query, retrieve top-5 documents from FAISS, pass them to Claude via AWS Bedrock, and generate a grounded answer with cited URLs. Add deprecation warnings for any deprecated resources."*

### Step 5: Run Evaluation

> **Ask Aqua:**
> *"Run my capsule to execute all evaluation queries and compute top-5 retrieval accuracy"*

---

## 3. Outputs You'll Get

| File | What It Contains |
|------|-----------------|
| `answers.jsonl` | Per-query grounded answers with cited URLs and deprecation warnings |
| `evaluation_report.json` | Top-5 accuracy, citation precision, deprecation handling stats |

---

## 4. Adapting for Different Use Cases

### Use Case A: Internal knowledge base / wiki
Index your company's Confluence/Notion/wiki pages.

> **Ask Aqua:**
> *"Adapt the corpus loader for Confluence export format (HTML). Add a preprocessing step that strips HTML, extracts text, and builds the JSONL corpus."*

### Use Case B: API documentation assistant
Help developers find the right API endpoint.

> **Ask Aqua:**
> *"Index my API reference docs. Add structured fields: endpoint, method, parameters, response_schema. Enable queries like 'How do I list all users?' to return the exact endpoint."*

### Use Case C: Multi-product support portal
Cross-product retrieval with product routing.

> **Ask Aqua:**
> *"Configure product-aware retrieval. When a user asks about a specific product, prioritize documents from that product but also show relevant cross-product results."*

### Use Case D: Version-aware documentation
Handle multiple versions of the same resource.

> **Ask Aqua:**
> *"Add version fields to the corpus. When a user asks about a feature, return the latest version's documentation and note if older versions differ significantly."*

---

## 5. Tips

- **Clean text extraction**: Strip navigation, footers, headers from web pages before indexing
- **Deprecation handling is key**: Always flag deprecated content and point to successors
- **Evaluation queries first**: Write 20 representative questions before building the system
- **Embedding model choice**: `all-MiniLM-L6-v2` is fast and good enough; `e5-large-v2` is better for technical docs
- **FAISS index size**: Up to ~10K documents works fine with flat index; use IVF for larger corpora
- **Update strategy**: Re-index weekly/monthly as docs change; store embeddings for incremental updates

---

## 6. Environment Requirements

| Package | Purpose |
|---------|---------|
| `sentence-transformers` | Document embedding |
| `faiss-cpu` | Vector similarity search |
| `boto3` | AWS Bedrock for answer generation |
| `pydantic` | Data validation |
| `pandas` | Data handling |
| `numpy` | Embedding operations |

**Compute**: CPU only, Small tier (embedding ~100 docs takes ~2 min)
**LLM**: AWS Bedrock (Claude) for grounded answer generation
