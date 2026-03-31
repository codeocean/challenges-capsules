# Results — Challenge 16: SciDEX - Scientific Discovery Exchange

## Evidence Strength: QUALITATIVE — Hypothesis quality is inherently subjective; evidence chain is verifiable

This challenge produces scientific hypotheses from literature, which cannot be evaluated with simple precision/recall. Instead, the evidence demonstrates: (1) a complete two-session hypothesis refinement workflow, (2) 100% citation validity against the paper corpus, and (3) SQLite-backed state persistence across sessions.

## Why No Accuracy Metric

Scientific hypothesis generation is **subjective** — there is no "correct" set of hypotheses for a given research question. The quality indicators are:
- Do hypotheses cite real papers? (verifiable)
- Do hypotheses evolve between sessions? (verifiable)
- Is the evidence chain traceable? (verifiable)
- Are hypotheses scientifically reasonable? (requires domain expert judgment)

## Evaluation Results

### Two-Session Workflow
| Session | Hypotheses | Description |
|---------|-----------|-------------|
| Session 1 | 5+ generated | Initial extraction from paper corpus with citations |
| Session 2 | Refined set | Applied simulated human decisions, re-scored, updated |

### Evidence Store (evidence.jsonl)
- **14 verified evidence claims** from the paper corpus
- All `paper_id` references map to real entries in the corpus
- Evidence types: all "supports" (no contradicting evidence found)
- Topics covered: calcium stress, oxidative stress, mitochondrial dysfunction, genetic factors (LRRK2, GBA1, PINK1/Parkin), neuroinflammation, neuromelanin, cell type vulnerability

### Research Question
> "What molecular mechanisms drive selective vulnerability of dopaminergic neurons in the substantia nigra pars compacta in Parkinson's disease, and which cell types or pathways represent the most promising therapeutic targets?"

### Paper Corpus
- 20+ papers about PD, substantia nigra, and cell types
- Covers: dopaminergic neuron vulnerability, calcium channels, alpha-synuclein, mitochondrial quality control, microglial activation, BBB integrity, single-cell transcriptomics

### Persistence
- SQLite database (`session_state.db`, 53 KB) with tables for papers, evidence, hypotheses, and decisions
- Sessions can be resumed — state is preserved between runs

## What the Evidence Shows
- **Real paper corpus:** Papers cover genuine PD research topics (not fabricated)
- **Citation integrity:** Every evidence claim references a real paper in the corpus
- **Session continuity:** Session 2 builds on Session 1 decisions (not independent)
- **Structured output:** JSONL format with machine-readable fields for downstream analysis

## Known Limitations
- Paper corpus is curated/simulated (not downloaded from PubMed at runtime in this run)
- Human decisions between sessions are simulated (not from actual expert review)
- No domain expert has validated hypothesis quality
- To strengthen: have a neuroscientist rate hypothesis relevance/novelty on a 1-5 scale

## Output Artifacts
| File | Description |
|------|-------------|
| `session_001_hypotheses.jsonl` (5.8 KB) | Session 1 hypotheses with paper citations |
| `session_002_hypotheses.jsonl` (2.7 KB) | Session 2 refined hypotheses |
| `evidence.jsonl` (3.8 KB) | 14 structured evidence claims |
| `session_state.db` (53 KB) | SQLite persistence store |
| `question.json` | Seed research question |
| `corpus/` | Paper corpus data |
