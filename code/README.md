# Challenge 16: SciDEX — Scientific Discovery Exchange


## Results Summary
- **2 sessions** completed (initial extraction + refinement)
- **17 verified evidence claims** from real paper corpus
- **SQLite persistence** with full state tracking
- **100% citation validity** — all paper_ids verified

> See [RESULTS.md](RESULTS.md) for session details and evidence summary.

## What This Capsule Does
Takes a neuroscience research question, retrieves ~50 paper abstracts, uses LLM to
generate and critique structured hypotheses (citing specific papers), saves to SQLite,
then runs a second session that loads prior state and refines hypotheses.

## Evaluation
Diff session 1 vs session 2 — does the system demonstrably remember and build on prior decisions?

## Required Data Assets
| File | Description |
|------|-------------|
| `question.json` | `{"question": "..."}` |
| `corpus/papers.jsonl` | ~50 pre-fetched abstracts |
| `human_decisions.json` | Simulated human review decisions for session 2 |

## Expected Outputs
| File | Description |
|------|-------------|
| `session_001_hypotheses.jsonl` | Session 1 hypotheses with evidence and critique |
| `session_002_hypotheses.jsonl` | Session 2 refined hypotheses |
| `session_state.db` | SQLite with full state |
| `evidence.jsonl` | Extracted evidence records |

## Environment
- CPU only. `anthropic`/`openai`, `pydantic`, `numpy`, `pandas`
