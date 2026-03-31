# Challenge 07 — Engineering Automation

## Original Challenge
Demonstrate AI-powered software maintenance automation through targeted refactoring, dependency updates, or bug fixes with structured context building, test validation, and reviewer-ready output.

## Intended Goal
Build an agent that accepts code tasks, analyzes repos, proposes fixes via LLM, validates with tests, handles regressions, and produces patches with explanations. Target: 15+ tasks across bugfix, migration, refactoring, and won't-fix types.

## Initial State
A 5-task bugfix agent existed using Bedrock and git. Tasks were generated from synthetic repos. The task generator was later expanded to 22KB with diverse task types.

## Improvement Plan
Expand to 15+ tasks with migration, refactoring, and won't-fix categories. Add risk calibration, explanation quality scoring, regression handling, and cost tracking.

## Final Implementation
The capsule auto-generates 15 test repositories (bugfix, migration, refactoring, won't-fix) via create_test_repos.py, then runs a Bedrock-powered agent loop that clones each repo, runs baseline tests, generates fixes, applies patches, and re-tests. It tracks iterations, token usage, and cost per task.

## Final Result
Produces dashboard.json (3.6KB, 15 tasks), patches/, reports/, run_log.jsonl (9KB). The dashboard shows 5/15 tasks resolved, with honest reporting of failures including budget exhaustion and regressions. Total cost: $0.08 USD.

## Evaluation
The capsule runs standalone (exit 0). Task diversity is good: bugfix, migration, refactoring, multi-file, won't-fix types are all represented. The 33% resolution rate is honest — the agent correctly identifies cases it cannot solve. Bedrock integration with cost tracking is working.

## Remaining Limitations
Only 5/15 tasks resolved. Many tasks show "already_passing" status, suggesting the test repos may not properly demonstrate failures. No tree-sitter integration as originally discussed. All repos are synthetic.

## Overall Verdict
Completed. The agent framework works end-to-end with honest metrics and diverse task types. The resolution rate is low but the transparency is a strength.

## Usage Documentation
The capsule has a README.md.

## Final Runnable State
Clean `/code/run` entrypoint. Runs standalone (auto-generates tasks before processing).
