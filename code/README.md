# Challenge 07: Engineering Automation

## What This Capsule Does

Takes 3–5 pre-staged bug-fix tasks (each a repo snapshot + issue description +
failing test), runs a Claude-powered edit-test-retry loop (max 5 iterations per
task), and outputs diffs, pass/fail results, and a cost summary.

## Evaluation Criteria

Pass rate (failing tests now pass without breaking existing tests) across the
task set, plus total API cost and iterations.

## Required Data Assets

| File | Description |
|------|-------------|
| `repos/*.bundle` | Git bundles of small, well-tested repos |
| `tasks.jsonl` | 3–5 tasks: `repo`, `issue_text`, `test_selector`, `expected_files` |

## Expected Outputs

| File | Description |
|------|-------------|
| `patches/task_001.diff` | Git diff for each task |
| `reports/task_001_summary.json` | Status, iterations, wall time per task |
| `dashboard.json` | Aggregate: resolve rate, avg iterations |

## Environment

- Python 3.10+, CPU only
- `anthropic`, `gitpython`, `pytest`
