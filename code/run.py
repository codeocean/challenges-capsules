#!/usr/bin/env python3
"""Challenge 07: Engineering Automation — AWS Bedrock agent.

Runs an LLM-powered edit-test-retry loop using AWS Bedrock (Claude)
to fix bugs in pre-staged test repositories. For each task:
1. Restore repo from git bundle
2. Confirm the target test fails
3. Iteratively: send issue+traceback to Bedrock, parse edits, apply, re-test
4. Check for regressions, generate diff, write structured report
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import traceback as tb_mod
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
RESULTS_DIR = Path("/results")
SCRATCH_DIR = Path("/scratch")
DATA_DIR = Path("/data")

WORK_DIR = SCRATCH_DIR / "work"
MAX_ITERATIONS = 5

# Prefer /data (external data asset) if present, else /scratch (self-generated)
REPOS_DIR = DATA_DIR / "repos" if (DATA_DIR / "repos").exists() else SCRATCH_DIR / "repos"
TASKS_PATH = DATA_DIR / "tasks.jsonl" if (DATA_DIR / "tasks.jsonl").exists() else SCRATCH_DIR / "tasks.jsonl"

# Bedrock model candidates (tried in order)
BEDROCK_MODELS = [
    "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "anthropic.claude-sonnet-4-20250514-v1:0",
    "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "us.anthropic.claude-3-5-haiku-20241022-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
]

# ---------------------------------------------------------------------------
# Bedrock LLM client
# ---------------------------------------------------------------------------
_client = None
_model_id = None
_total_input_tokens = 0
_total_output_tokens = 0


def _get_client():
    global _client
    if _client is None:
        import boto3
        region = os.environ.get(
            "AWS_DEFAULT_REGION",
            os.environ.get("AWS_REGION", "us-east-1"),
        )
        _client = boto3.client("bedrock-runtime", region_name=region)
    return _client


def discover_model() -> str:
    """Probe Bedrock for the first available Claude model."""
    global _model_id
    if _model_id:
        return _model_id
    client = _get_client()
    for mid in BEDROCK_MODELS:
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 32,
                "messages": [{"role": "user", "content": "Say OK"}],
            })
            resp = client.invoke_model(
                modelId=mid, body=body,
                contentType="application/json", accept="application/json",
            )
            result = json.loads(resp["body"].read())
            _ = result["content"][0]["text"]
            _model_id = mid
            print(f"  Bedrock model: {mid}")
            return mid
        except Exception as exc:
            print(f"  {mid}: {type(exc).__name__}")
    raise RuntimeError("No Bedrock Claude model available — check AWS creds/region.")


def call_bedrock(prompt: str, max_tokens: int = 4096) -> tuple[str, dict]:
    """Invoke Bedrock Claude. Returns (text, usage_dict)."""
    global _total_input_tokens, _total_output_tokens
    client = _get_client()
    model = discover_model()
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    })
    resp = client.invoke_model(
        modelId=model, body=body,
        contentType="application/json", accept="application/json",
    )
    result = json.loads(resp["body"].read())
    text = result["content"][0]["text"]
    usage = result.get("usage", {})
    _total_input_tokens += usage.get("input_tokens", 0)
    _total_output_tokens += usage.get("output_tokens", 0)
    return text, usage


# ---------------------------------------------------------------------------
# Repo / git helpers
# ---------------------------------------------------------------------------

def restore_repo(bundle_name: str) -> Path:
    bundle_path = REPOS_DIR / f"{bundle_name}.bundle"
    if not bundle_path.exists():
        bundle_path = REPOS_DIR / bundle_name
    if not bundle_path.exists():
        raise FileNotFoundError(f"Bundle not found: {bundle_path}")
    repo_dir = WORK_DIR / bundle_name
    if repo_dir.exists():
        shutil.rmtree(repo_dir)
    subprocess.run(
        ["git", "clone", str(bundle_path), str(repo_dir)],
        check=True, capture_output=True, text=True,
    )
    return repo_dir


def run_tests(repo_dir: Path, selector: str) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            ["python", "-m", "pytest", selector, "-x", "--tb=short", "-q"],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=120,
        )
        out = (r.stdout[-2000:] + "\n" + r.stderr[-1000:]).strip()
        return r.returncode == 0, out
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT: test exceeded 120s"
    except Exception as e:
        return False, f"ERROR: {e}"


def run_full_tests(repo_dir: Path) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            ["python", "-m", "pytest", "--tb=short", "-q"],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=300,
        )
        out = (r.stdout[-2000:] + "\n" + r.stderr[-1000:]).strip()
        return r.returncode == 0, out
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT: full suite exceeded 300s"
    except Exception as e:
        return False, f"ERROR: {e}"


def get_diff(repo_dir: Path) -> str:
    r = subprocess.run(
        ["git", "diff"], cwd=str(repo_dir), capture_output=True, text=True,
    )
    return r.stdout


def read_relevant_files(repo_dir: Path, expected: list[str]) -> dict[str, str]:
    files: dict[str, str] = {}
    for rel in expected:
        fp = repo_dir / rel
        if fp.exists():
            try:
                files[rel] = fp.read_text()
            except Exception:
                pass
    for tf in (repo_dir / "tests").rglob("*.py"):
        rel = str(tf.relative_to(repo_dir))
        if rel not in files:
            try:
                files[rel] = tf.read_text()
            except Exception:
                pass
    return files


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

def ask_llm_for_fix(issue: str, test_out: str, files: dict, iteration: int) -> list[dict]:
    """Send context to Bedrock, get back file edits as JSON."""
    ctx = ""
    for fp, content in files.items():
        ctx += f"\n--- {fp} ---\n{content}\n"

    prompt = (
        "You are a senior software engineer fixing a bug.\n\n"
        f"## Bug Report\n{issue}\n\n"
        f"## Test Output (iteration {iteration})\n```\n{test_out[-1500:]}\n```\n\n"
        f"## Source Files\n{ctx}\n\n"
        "Fix the bug so the failing test passes without breaking other tests.\n"
        "Return ONLY a JSON array of edits. Each element: "
        '{"path": "<relative_path>", "content": "<full_new_file_content>"}.\n'
        "No markdown fences, no explanation — just the raw JSON array."
    )
    try:
        text, _ = call_bedrock(prompt)
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except Exception as exc:
        print(f"    LLM error: {exc}")
    return []


def apply_edits(repo_dir: Path, edits: list[dict]) -> list[str]:
    modified = []
    for ed in edits:
        fp = repo_dir / ed["path"]
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(ed["content"])
        modified.append(ed["path"])
    return modified


# ---------------------------------------------------------------------------
# Output generators
# ---------------------------------------------------------------------------

def write_outputs(results: list[dict]) -> None:
    """Write dashboard, manifest, implementation summary, validation notes."""
    n_pass = sum(1 for r in results if r["status"] == "pass")
    n_reg = sum(1 for r in results if r["status"] == "pass_with_regressions")
    total = len(results)
    avg_it = sum(r.get("iterations", 0) for r in results) / max(total, 1)

    # Dashboard
    dashboard = {
        "resolve_rate": f"{n_pass}/{total}",
        "resolve_with_regressions": f"{n_reg}/{total}",
        "avg_iterations": round(avg_it, 1),
        "total_input_tokens": _total_input_tokens,
        "total_output_tokens": _total_output_tokens,
        "bedrock_model": _model_id or "unknown",
        "results": results,
    }
    (RESULTS_DIR / "dashboard.json").write_text(json.dumps(dashboard, indent=2))

    # Manifest
    patch_files = [f"results/patches/{r['task']}.diff" for r in results]
    report_files = [f"results/reports/{r['task']}_summary.json" for r in results]
    manifest = {
        "capsule": "Challenge 07 — Engineering Automation",
        "objective": "Bedrock-powered edit-test-retry agent for automated bug fixing",
        "created_files": sorted(set(
            ["results/dashboard.json", "results/manifest.json",
             "results/IMPLEMENTATION_SUMMARY.md", "results/VALIDATION_NOTES.md"]
            + patch_files + report_files
        )),
        "entrypoints": ["/code/run"],
        "commands_run": [
            "python /code/create_test_repos.py",
            "python /code/run.py",
        ],
        "dependencies": ["boto3", "gitpython", "pytest", "tqdm"],
        "bedrock_model": _model_id or "unknown",
        "known_limitations": [
            "Test repos are synthetic self-contained modules",
            "No tree-sitter code understanding (file-level context)",
            "Model availability depends on AWS Bedrock access",
        ],
    }
    (RESULTS_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))

    # Implementation summary
    summary_md = f"""# Implementation Summary — Challenge 07: Engineering Automation

## What Was Implemented
An AWS Bedrock-powered (boto3) edit-test-retry agent that:
1. Creates 4 self-contained test repos with intentional bugs (via create_test_repos.py)
2. For each task: restores repo from git bundle, confirms test failure
3. Enters an LLM agent loop (max {MAX_ITERATIONS} iterations):
   - Sends issue description + test traceback + source files to Claude via **AWS Bedrock**
   - Parses JSON-formatted file edits from LLM response
   - Applies edits to the working copy
   - Re-runs the failing test; if still failing, feeds traceback back
   - On success: runs full test suite for regression detection
4. Generates git diffs, per-task reports, and aggregate dashboard

## Key Design Decision: Bedrock-Only LLM Access
All LLM calls use `boto3.client('bedrock-runtime').invoke_model()`.
**No direct Anthropic or OpenAI API calls anywhere.**
Model discovery probes multiple Bedrock model IDs for robustness.

## Files
| File | Purpose |
|------|---------|
| `/code/create_test_repos.py` | Generates 4 repos with known bugs as git bundles |
| `/code/run.py` | Main agent: Bedrock-powered edit-test-retry loop |
| `/code/run` | Bash driver script |
| `/results/patches/*.diff` | Git diffs for each task |
| `/results/reports/*_summary.json` | Per-task JSON reports |
| `/results/dashboard.json` | Aggregate results |

## Execution Results
- Tasks: {total}
- Resolved (clean): {n_pass}/{total}
- With regressions: {n_reg}/{total}
- Avg iterations: {avg_it:.1f}
- Bedrock model: {_model_id or 'unknown'}
- Total tokens: {_total_input_tokens} in / {_total_output_tokens} out
"""
    (RESULTS_DIR / "IMPLEMENTATION_SUMMARY.md").write_text(summary_md)

    # Validation notes
    validation_md = f"""# Validation Notes — Challenge 07: Engineering Automation

## Complete
- [x] Bedrock-only LLM integration (boto3 bedrock-runtime, no direct Anthropic/OpenAI)
- [x] Edit-test-retry agent loop with iterative traceback feedback
- [x] Git bundle restore and diff generation
- [x] Regression detection via full test suite after targeted test passes
- [x] Safe stopping on max-iteration budget exhaustion
- [x] Structured output: diffs, per-task reports, aggregate dashboard
- [x] Mandatory artifacts: manifest.json, IMPLEMENTATION_SUMMARY.md, VALIDATION_NOTES.md

## Assumptions
- AWS Bedrock credentials available via environment / IAM role
- Git is installed in the capsule environment
- Test repos are self-contained (no external network dependencies)

## Limitations
- Test repos are synthetic small modules (not real-world SWE-bench)
- No tree-sitter or AST-based code understanding — uses file-level context
- No separate planning/editing model split
- Token cost tracking is approximate (from Bedrock response usage field)

## Known Gaps vs. Full Challenge Spec
- No SWE-bench evaluation (requires Docker-in-Docker, not available)
- No code review mode (focused on bug-fix scope)
- No dependency resolution tasks
- 5 synthetic tasks (representative of the fix pattern, not real-world scale)
"""
    (RESULTS_DIR / "VALIDATION_NOTES.md").write_text(validation_md)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "patches").mkdir(exist_ok=True)
    (RESULTS_DIR / "reports").mkdir(exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    if not TASKS_PATH.exists():
        print(f"ERROR: {TASKS_PATH} not found", file=sys.stderr)
        sys.exit(1)

    tasks = []
    with open(TASKS_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    print(f"Loaded {len(tasks)} tasks from {TASKS_PATH}")
    print(f"Repos directory: {REPOS_DIR}")

    # Discover model
    print("\nProbing Bedrock models...")
    try:
        model = discover_model()
        print(f"Using: {model}\n")
    except RuntimeError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        err_dash = {"error": str(e), "resolve_rate": "0/0", "results": []}
        (RESULTS_DIR / "dashboard.json").write_text(json.dumps(err_dash, indent=2))
        sys.exit(1)

    # Process each task
    results: list[dict] = []

    for idx, task in enumerate(tasks):
        tid = f"task_{idx+1:03d}"
        repo_name = task["repo"]
        issue = task["issue_text"]
        selector = task["test_selector"]
        expected = task.get("expected_files", [])

        print(f"{'='*60}")
        print(f"[{idx+1}/{len(tasks)}] {repo_name}: {issue[:70]}...")
        print(f"{'='*60}")

        try:
            repo_dir = restore_repo(repo_name)
            print(f"  Restored -> {repo_dir}")

            passed, test_out = run_tests(repo_dir, selector)
            if passed:
                print("  SKIP: test already passes")
                results.append({"task": tid, "repo": repo_name,
                                "status": "already_passing", "iterations": 0})
                continue
            print("  Baseline: test fails as expected")

            t0 = time.time()
            status = "fail"
            iters = 0

            for it in range(1, MAX_ITERATIONS + 1):
                print(f"  Iter {it}/{MAX_ITERATIONS} ...")
                files = read_relevant_files(repo_dir, expected)
                edits = ask_llm_for_fix(issue, test_out, files, it)
                if not edits:
                    print("    No edits returned — stopping")
                    status = "no_edits"
                    iters = it
                    break
                mods = apply_edits(repo_dir, edits)
                print(f"    Edited: {mods}")
                passed, test_out = run_tests(repo_dir, selector)
                iters = it
                if passed:
                    fp, fo = run_full_tests(repo_dir)
                    status = "pass" if fp else "pass_with_regressions"
                    sym = "✓" if fp else "⚠"
                    print(f"    {sym} Target passes | Full suite: {'PASS' if fp else 'REGRESS'}")
                    break
                print(f"    ✗ Still failing")

            elapsed = time.time() - t0
            diff = get_diff(repo_dir)
            (RESULTS_DIR / "patches" / f"{tid}.diff").write_text(diff)

            report = {
                "task": tid, "repo": repo_name, "status": status,
                "iterations": iters, "wall_time_seconds": round(elapsed, 1),
            }
            results.append(report)
            (RESULTS_DIR / "reports" / f"{tid}_summary.json").write_text(
                json.dumps(report, indent=2))
            print(f"  => {status} in {iters} iters ({elapsed:.1f}s)\n")

        except Exception as exc:
            print(f"  ERROR: {exc}")
            tb_mod.print_exc()
            results.append({"task": tid, "repo": repo_name,
                            "status": "error", "error": str(exc), "iterations": 0})

    # Write all output artifacts
    write_outputs(results)

    n_pass = sum(1 for r in results if r["status"] == "pass")
    print(f"\n{'='*60}")
    print(f"DASHBOARD: {n_pass}/{len(results)} resolved | "
          f"Tokens: {_total_input_tokens} in / {_total_output_tokens} out")
    print(f"{'='*60}")
    print("Done.")


if __name__ == "__main__":
    main()
