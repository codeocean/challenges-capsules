# Results — Challenge 16: SciDEX - Scientific Discovery Exchange

## Latest Successful Run
- **Computation ID:** `2baa2e2c-84ce-44e0-8801-d82633b07396`
- **Status:** Succeeded (exit code 0)
- **Runtime:** 132 seconds

## Evaluation Results

### Two-Session Scientific Discovery Workflow
| Session | Hypotheses | Description |
|---------|-----------|-------------|
| Session 1 | 5+ hypotheses | Initial extraction from paper corpus |
| Session 2 | Refined set | Applied human decisions, re-scored |

### Evidence Store
- **17 evidence entries** in `evidence.jsonl`, all verified
- All paper_ids reference real corpus entries
- Evidence types: supports (all 17 entries)

### Paper Corpus
- 20+ papers about Parkinson's disease, substantia nigra, cell types
- Topics: dopaminergic neuron vulnerability, calcium stress, mitochondrial dysfunction, neuroinflammation, genetic factors (GBA1, LRRK2, PINK1, Parkin)

### Persistence
- SQLite database (`session_state.db`, 53 KB) with tables: papers, evidence, hypotheses, decisions

### Session Artifacts
| File | Description |
|------|-------------|
| `session_001_hypotheses.jsonl` (5.8 KB) | Session 1 hypotheses with citations |
| `session_002_hypotheses.jsonl` (2.7 KB) | Session 2 refined hypotheses |
| `evidence.jsonl` (3.8 KB) | Structured evidence claims |
| `session_state.db` (53 KB) | SQLite persistence store |
| `question.json` | Seed research question |
| `corpus/` | Paper corpus data |
