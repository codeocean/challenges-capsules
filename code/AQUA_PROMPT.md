# AQUA PROMPT — Replicate Challenge 07: Engineering Automation

> Copy this entire prompt and paste it to Aqua to have it fully recreate this capsule from scratch.

---

## Prompt

```
I need you to replicate the "Challenge 07: Engineering Automation" capsule from the Allen Institute Hackathon. Follow these steps exactly:

### STEP 1: Create the capsule from GitHub
Create a new capsule by copying (not cloning) from the GitHub repository:
- Repository URL: https://github.com/codeocean/challenges-capsules
- After import, the code for this challenge is in the `challenge-07-engineering-automation/` folder within the repo. Move all files from that subfolder to `/code/` so they are at the root of the capsule's code directory. Remove any other challenge folders that were imported.

### STEP 2: Set capsule metadata
- Name: "Challenge 07: Engineering Automation"
- Description: "Demonstrate AI-powered software maintenance automation through targeted refactoring, dependency updates, or bug fixes with structured context building, test validation, safe stopping conditions, and reviewer-ready output demonstrating trustworthy code generation."
- Tags: hackathon-challenge, software-engineering, AI-coding, refactoring, automation, code-review, maintenance, testing

### STEP 3: Configure the environment
- Starter environment: Python (codeocean/mambaforge3:22.11.1-4-ubuntu22.04) — Python 3.10
- Pip packages (install these exact versions):
  - boto3==1.42.77
  - gitpython==3.1.46
  - pytest==9.0.2
  - tqdm==4.67.3

### STEP 4: Set compute resources
- Flex tier: Small (2 cores / 16 GB RAM)
- Machine type: CPU (general_purpose)

### STEP 5: Data assets
This capsule is fully self-contained. No data assets need to be attached.
It generates synthetic test repositories with intentional bugs at runtime via create_test_repos.py.

### STEP 6: Verify the run script
The `/code/run` file should contain:
```bash
#!/usr/bin/env bash
set -euo pipefail
python /code/create_test_repos.py
python /code/run.py "$@"
```
Note: The run script first creates test repos, then executes the AI-powered edit-test-retry loop.

### STEP 7: Verify code structure
The capsule should have these key files in /code/:
- run.py — Main pipeline: load tasks → AI edit-test-retry loop → output diffs and reports
- create_test_repos.py — Generates small well-tested repos with intentional bugs/issues

### STEP 8: Run the capsule
Run the capsule. It should produce:
- patches/task_XXX.diff (git diff for each task)
- reports/task_XXX_summary.json (status, iterations, wall time per task)
- dashboard.json (aggregate: resolve rate, avg iterations, total cost)

Note: Requires AWS Bedrock credentials for Claude-powered code editing.
```
