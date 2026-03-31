# Results — Challenge 07: Engineering Automation

## Evidence Strength: MODERATE

The agent successfully resolves 5 out of 15 benchmark tasks using Bedrock LLM-generated patches. However, 8 tasks were pre-configured as "already passing" (migrations, refactoring, won't-fix), meaning only 7 tasks were genuine fix attempts — of which 5 passed and 2 failed. The evidence demonstrates a working agentic loop with real LLM calls, but the benchmark could be more challenging.

## Evaluation Results (dashboard.json)

### Summary
| Metric | Value |
|--------|-------|
| **Resolve Rate** | 5/15 tasks |
| **Genuine Fix Attempts** | 7 (5 pass, 1 with regressions, 1 fail) |
| **Average Iterations** | 1.0 per successful fix |
| **Total LLM Cost** | $0.08 |
| **Bedrock Model** | claude-sonnet-4-20250514-v1:0 |

### Per-Task Breakdown
| Task | Type | Status | Iterations | Cost |
|------|------|--------|-----------|------|
| task_001 (mathlib) | bugfix | ✅ Pass | 1 | $0.003 |
| task_002 (configlib) | bugfix | ✅ Pass | 1 | $0.004 |
| task_003 (cachelib) | bugfix | ✅ Pass | 1 | $0.008 |
| task_004 (numextract) | bugfix | ✅ Pass | 1 | $0.004 |
| task_005 (tempconv) | bugfix | ⚠️ Pass w/ regressions | 5 | $0.045 |
| task_006–013 | migration/refactoring/wontfix | Already passing | 0 | — |
| task_014 (multifile_bug) | bugfix | ✅ Pass | 1 | $0.005 |
| task_015 (cross_module) | bugfix | ❌ Fail (budget) | 5 | $0.013 |

## What the Evidence Shows
- **Agentic loop works:** The agent reads test output, generates patches via LLM, applies them, and re-tests
- **Real Bedrock calls:** $0.08 total spent on actual API calls (not mocked)
- **Failure modes are honest:** task_005 introduced regressions, task_015 exhausted its iteration budget

## Known Limitations
- 8 of 15 tasks are "already passing" — they test decline/no-op behavior, not fix capability
- All test repos are synthetic (not real open-source repos or SWE-bench tasks)
- No tree-sitter AST analysis — fixes are generated from raw code context
- To strengthen: expand to 15+ genuine failing tasks from real repositories

## Output Artifacts
| File | Description |
|------|-------------|
| `dashboard.json` (3.6 KB) | Full results with per-task metrics and costs |
| `run_log.jsonl` (9 KB) | Detailed execution log |
| `patches/` | Generated diff patches per task |
| `reports/` | Per-task summary reports |
