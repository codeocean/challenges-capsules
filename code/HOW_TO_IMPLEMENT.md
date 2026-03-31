# How to Implement: Engineering Automation — For Your Own Data

> **Goal**: Use an AI-powered edit-test-retry loop to automatically fix bugs,
> refactor code, or update dependencies in *your* repositories, with structured
> diffs, test validation, and reviewer-ready output.

---

## 1. What You Need (Your Data)

### Input Data Format

| Input | Format | Description |
|-------|--------|-------------|
| **Repository snapshots** | Git bundles (`.bundle`) or directories | Small, well-tested repos with failing tests |
| **Task descriptions** | JSONL file | Issue text, test selector, expected files per task |

### What Your Data Should Look Like

```json
// tasks.jsonl — one JSON object per line
{"repo": "my_api_server", "issue_text": "Fix the date parsing bug in utils.py that causes 500 errors on ISO dates with timezone offsets", "test_selector": "tests/test_utils.py::test_parse_iso_date", "expected_files": ["src/utils.py"]}
{"repo": "data_pipeline", "issue_text": "Update pandas from 1.5 to 2.0 and fix all deprecation warnings", "test_selector": "tests/", "expected_files": ["requirements.txt", "src/transform.py"]}
{"repo": "ml_trainer", "issue_text": "Refactor the monolithic train() function into separate data loading, model creation, and training loop functions", "test_selector": "tests/test_trainer.py", "expected_files": ["src/trainer.py"]}
```

```
my_repos/
├── my_api_server.bundle     # git bundle create my_api_server.bundle --all
├── data_pipeline.bundle
├── ml_trainer.bundle
└── tasks.jsonl
```

**Key requirements:**
- Each repo must have a test suite that can run with `pytest` (or specify your test runner)
- Tasks should have at least one failing test that defines success
- Keep repos small (< 50 files) for reliable AI-assisted editing
- Git bundles preserve full history: `git bundle create repo.bundle --all`

---

## 2. Step-by-Step: Recreate This Capsule with Aqua

### Step 1: Create a New Capsule

> **Ask Aqua:**
> *"Create a new capsule called 'AI Code Maintenance — [My Project]' with Python 3.10, and install packages: boto3, gitpython, pytest"*

### Step 2: Prepare Your Repositories

Bundle your repos and create the task file:

```bash
# In each repo directory:
git bundle create my_repo.bundle --all
```

> **Ask Aqua:**
> *"Create a data asset called 'my-code-tasks' with my git bundles and tasks.jsonl, then attach it at /data/code_tasks"*

### Step 3: Configure the Edit-Test Loop

> **Ask Aqua:**
> *"Adapt run.py to load tasks from /data/code_tasks/tasks.jsonl and repos from /data/code_tasks/*.bundle. Set max iterations to 5 per task, use pytest as the test runner."*

### Step 4: Run

> **Ask Aqua:**
> *"Run my capsule"*

---

## 3. Outputs You'll Get

| File | What It Contains |
|------|-----------------|
| `patches/task_001.diff` | Git diff showing the changes made for each task |
| `reports/task_001_summary.json` | Status (pass/fail), iterations used, wall time, test results |
| `dashboard.json` | Aggregate: resolve rate, average iterations, total cost |

---

## 4. Adapting for Different Use Cases

### Use Case A: Dependency updates
Batch-update a library across multiple repos.

> **Ask Aqua:**
> *"Create tasks for updating numpy from 1.x to 2.x across 5 repos. The agent should update requirements, fix breaking API changes, and ensure all tests pass."*

### Use Case B: Code style refactoring
Apply consistent patterns across a codebase.

> **Ask Aqua:**
> *"Create tasks for refactoring all repos to use pathlib instead of os.path, type hints on all public functions, and f-strings instead of format()."*

### Use Case C: Security patch application
Fix known vulnerabilities.

> **Ask Aqua:**
> *"Create tasks for each CVE-affected dependency. The agent should update the vulnerable package, adjust API usage if needed, and verify tests pass."*

---

## 5. Tips

- **Small, focused tasks**: One bug/refactor per task works better than large multi-issue tasks
- **Good test coverage**: The agent's success depends on having tests that catch regressions
- **Review the diffs**: Always human-review generated patches before merging
- **Safe stopping**: The loop stops after max iterations even if unfixed — check `dashboard.json`
- **Cost tracking**: Monitor API cost per task to estimate budgets for larger batches

---

## 6. Environment Requirements

| Package | Purpose |
|---------|---------|
| `boto3` | AWS Bedrock for Claude-powered code editing |
| `gitpython` | Git operations (bundle extraction, diff, commit) |
| `pytest` | Test execution and validation |

**Compute**: CPU only, Small tier sufficient
**LLM**: AWS Bedrock (Claude) via managed credentials
