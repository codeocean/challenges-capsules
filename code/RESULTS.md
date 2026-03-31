# Results — Challenge 07: Engineering Automation

## Latest Successful Run
- **Computation ID:** `250342eb-44cd-44b9-aa38-48dd8cc7e1bb`
- **Status:** Succeeded (exit code 0)
- **Runtime:** 89 seconds

## Evaluation Results (dashboard.json)

### Task Resolution
| Metric | Value |
|--------|-------|
| **Resolve Rate** | 5/15 tasks |
| **Average Iterations** | 1.0 |
| **Total Cost (USD)** | $0.08 |
| **Bedrock Model** | claude-sonnet-4-20250514-v1:0 |

### Per-Task Results
| Task | Repo | Status | Iterations |
|------|------|--------|-----------|
| task_001 | mathlib | ✅ Pass | 1 |
| task_002 | configlib | ✅ Pass | 1 |
| task_003 | cachelib | ✅ Pass | 1 |
| task_004 | numextract | ✅ Pass | 1 |
| task_005 | tempconv | ⚠️ Pass with regressions | 5 |
| task_006–013 | various | Already passing | 0 |
| task_014 | multifile_bug | ✅ Pass | 1 |
| task_015 | cross_module | ❌ Fail (budget exhausted) | 5 |

### Task Types Covered
- Bug fixes (5 tasks)
- Migrations (3 tasks)
- Refactoring (3 tasks)
- Won't-fix/already passing (4 tasks)

## Output Artifacts
| File | Description |
|------|-------------|
| `dashboard.json` (3.6 KB) | Full results with per-task metrics |
| `run_log.jsonl` (9 KB) | Detailed execution log |
| `patches/` | Generated diff patches per task |
| `reports/` | Per-task summary reports |
| `manifest.json` | Pipeline configuration |
