# How to Implement: SciDEX — Scientific Discovery Exchange — For Your Own Data

> **Goal**: Build a persistent hypothesis workbench where AI agents generate
> testable hypotheses from *your* data and literature, critique reasoning,
> link evidence, and maintain decision history across sessions.

---

## 1. What You Need (Your Data)

### Input Data Format

| Input | Format | Description |
|-------|--------|-------------|
| **Research question** | JSON file | Your driving scientific question |
| **Paper corpus** | JSONL file | ~50 relevant abstracts/papers |
| **Human decisions** (optional) | JSON file | Simulated or real review decisions for session 2+ |

### What Your Data Should Look Like

```json
// question.json
{
  "question": "What molecular mechanisms drive the transition from oligodendrocyte precursor cells to mature myelinating oligodendrocytes, and which transcription factors are most critical?"
}
```

```jsonl
// papers.jsonl — one per line
{"id": "paper_001", "title": "SOX10 drives oligodendrocyte differentiation", "abstract": "We show that SOX10 is necessary and sufficient for...", "doi": "10.1234/example", "year": 2023}
{"id": "paper_002", "title": "MYRF activates myelin gene expression", "abstract": "The transcription factor MYRF...", "doi": "10.5678/example", "year": 2022}
```

```json
// human_decisions.json — for session 2 (iterative refinement)
{
  "decisions": [
    {"hypothesis_id": "hyp_001", "action": "accept", "comment": "Strong evidence from multiple studies"},
    {"hypothesis_id": "hyp_002", "action": "refine", "comment": "Need to narrow the mechanism to a specific pathway"},
    {"hypothesis_id": "hyp_003", "action": "reject", "comment": "Contradicted by recent knockout studies"}
  ]
}
```

```
my_discovery/
├── question.json              # Your research question
├── corpus/
│   └── papers.jsonl           # Relevant literature
└── human_decisions.json       # Optional: for multi-session refinement
```

**Key requirements:**
- Research question should be specific enough to generate testable hypotheses
- Paper corpus should be relevant to the question (quality > quantity)
- Each paper needs at least `title` and `abstract`
- For session continuity, the SQLite state database persists between runs

---

## 2. Step-by-Step: Recreate This Capsule with Aqua

### Step 1: Create a New Capsule

> **Ask Aqua:**
> *"Create a new capsule called 'SciDEX — [My Research Topic]' with Python 3.10, and install packages: boto3, pydantic, numpy, pandas"*

### Step 2: Prepare Your Literature Corpus

Collect relevant papers via PubMed, Semantic Scholar, or your reference manager:

> **Ask Aqua:**
> *"Create a data asset called 'my-discovery-corpus' with my question.json and papers.jsonl, then attach it at /data/discovery"*

### Step 3: Configure the Hypothesis Pipeline

> **Ask Aqua:**
> *"Modify run.py to: (1) load the research question from /data/discovery/question.json, (2) load papers from /data/discovery/corpus/papers.jsonl, (3) use AWS Bedrock (Claude) to generate structured hypotheses citing specific papers, (4) critique each hypothesis for logical soundness and evidence strength, (5) save to SQLite at /results/session_state.db."*

### Step 4: Run Session 1 (Initial Hypothesis Generation)

> **Ask Aqua:**
> *"Run my capsule for session 1 — generate initial hypotheses from the question and literature"*

### Step 5: Review and Run Session 2 (Iterative Refinement)

After reviewing session 1 outputs, create `human_decisions.json` and re-run:

> **Ask Aqua:**
> *"Run session 2 with human decisions from /data/discovery/human_decisions.json. The system should load prior state from the session 1 database and refine hypotheses based on my feedback."*

---

## 3. Outputs You'll Get

| File | What It Contains |
|------|-----------------|
| `session_001_hypotheses.jsonl` | Generated hypotheses with evidence citations and critique |
| `session_002_hypotheses.jsonl` | Refined hypotheses after human feedback |
| `session_state.db` | SQLite database with full session state and decision history |
| `evidence.jsonl` | Extracted evidence records linked to specific papers and passages |

---

## 4. Adapting for Different Use Cases

### Use Case A: Drug target discovery
Generate hypotheses about therapeutic targets.

> **Ask Aqua:**
> *"Configure the hypothesis generator for drug discovery. My question is about potential targets for [disease]. Add structured fields: target_gene, mechanism_of_action, druggability_score, supporting_evidence."*

### Use Case B: Experimental design suggestions
Go beyond hypotheses to suggest experiments.

> **Ask Aqua:**
> *"Extend the pipeline to also generate experimental design proposals for each hypothesis: suggested assay, expected outcome, controls needed, estimated timeline and cost."*

### Use Case C: Literature gap analysis
Identify what's missing in the field.

> **Ask Aqua:**
> *"Add a gap analysis step: after generating hypotheses, identify which ones lack sufficient evidence and flag them as 'testable unknowns' with suggested studies to fill the gap."*

### Use Case D: Multi-team collaborative discovery
Enable team-based hypothesis review.

> **Ask Aqua:**
> *"Add multi-reviewer support: each team member submits their own human_decisions.json. Aggregate decisions by majority vote and flag disagreements for discussion."*

---

## 5. Tips

- **Specific questions work best**: "What causes X?" generates vague hypotheses; "Does TF-A regulate gene-B via pathway-C in cell-type-D?" generates testable ones
- **Curate your corpus**: 50 highly relevant papers beat 500 tangentially related ones
- **Session persistence**: The SQLite database preserves everything — you can resume weeks later
- **Critique is valuable**: The AI critique step catches logical flaws and missing evidence
- **Human in the loop**: Always review and decide on hypotheses before the next session — this is where scientific judgment matters
- **Export for presentations**: Session hypotheses export as structured JSON — easy to convert to slides or reports

---

## 6. Environment Requirements

| Package | Purpose |
|---------|---------|
| `boto3` | AWS Bedrock for hypothesis generation and critique |
| `pydantic` | Structured hypothesis validation |
| `numpy` | Embedding operations |
| `pandas` | Evidence table manipulation |

**Compute**: CPU only, X-Small tier sufficient
**LLM**: AWS Bedrock (Claude) via managed credentials
**Storage**: SQLite database grows with sessions; ~1 MB per session for 50-paper corpus
