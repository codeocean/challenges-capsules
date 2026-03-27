#!/usr/bin/env python3
"""Create self-contained test repositories with intentional bugs.

Each repo is a small Python module with one known bug and pytest tests
that expose the bug. After creation, each repo is bundled as a git bundle
for the engineering automation agent.
"""

import json
import shutil
import subprocess
from pathlib import Path

SCRATCH = Path("/scratch")
REPOS_DIR = SCRATCH / "repos"
TASKS_PATH = SCRATCH / "tasks.jsonl"


def _git(repo_dir: Path, *args: str) -> None:
    subprocess.run(
        ["git"] + list(args),
        cwd=str(repo_dir),
        capture_output=True,
        check=True,
    )


def _create_and_bundle(name: str, files: dict, task: dict) -> dict:
    repo_dir = REPOS_DIR / name
    if repo_dir.exists():
        shutil.rmtree(repo_dir)
    for rel_path, content in files.items():
        p = repo_dir / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    _git(repo_dir, "init", "-b", "main")
    _git(repo_dir, "config", "user.email", "test@example.com")
    _git(repo_dir, "config", "user.name", "Test User")
    _git(repo_dir, "add", ".")
    _git(repo_dir, "commit", "-m", f"Initial commit: {name} with known bug")
    bundle = REPOS_DIR / f"{name}.bundle"
    _git(repo_dir, "bundle", "create", str(bundle), "--all")
    print(f"  Created {name} -> {bundle}")
    return task


# =====================================================================
# Repo 1: mathlib — safe_divide does not check for zero
# =====================================================================
MATHLIB_SRC = '''\
"""Simple calculator module."""


def add(a, b):
    """Add two numbers."""
    return a + b


def subtract(a, b):
    """Subtract b from a."""
    return a - b


def multiply(a, b):
    """Multiply two numbers."""
    return a * b


def safe_divide(a, b):
    """Divide a by b safely.

    Raises ValueError with message 'Cannot divide by zero' if b is zero.
    """
    return a / b
'''

MATHLIB_TEST = '''\
"""Tests for calculator module."""
import pytest
from mathlib.calculator import add, subtract, multiply, safe_divide


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0


def test_subtract():
    assert subtract(5, 3) == 2


def test_multiply():
    assert multiply(3, 4) == 12


def test_safe_divide_normal():
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(7, 2) == 3.5


def test_safe_divide_by_zero():
    """Division by zero must raise ValueError, not ZeroDivisionError."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        safe_divide(10, 0)
'''


# =====================================================================
# Repo 2: texttools — truncate off-by-one (< vs <=)
# =====================================================================
TEXTTOOLS_SRC = '''\
"""Text formatting utilities."""


def truncate(text, max_length, suffix="..."):
    """Truncate text to max_length characters (including suffix).

    If text length is within max_length, return it unchanged.
    """
    if len(text) < max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def pad_right(text, width, char=" "):
    """Pad text on the right to given width."""
    return text + char * max(0, width - len(text))
'''

TEXTTOOLS_TEST = '''\
"""Tests for text formatter."""
from texttools.formatter import truncate, pad_right


def test_truncate_short():
    assert truncate("Hi", 10) == "Hi"


def test_truncate_exact_length():
    """Text exactly at max_length should NOT be truncated."""
    assert truncate("Hello", 5) == "Hello"


def test_truncate_long():
    result = truncate("Hello World", 8)
    assert result == "Hello..."
    assert len(result) == 8


def test_pad_right():
    assert pad_right("Hi", 5) == "Hi   "
'''


# =====================================================================
# Repo 3: dataproc — clean_records crashes on None value
# =====================================================================
DATAPROC_SRC = '''\
"""Data cleaning utilities."""


def clean_records(records):
    """Clean a list of record dicts.

    Each record has 'name' (str) and 'value' (numeric or None).
    Records with None values should get value=0.0.
    """
    cleaned = []
    for rec in records:
        cleaned.append({
            "name": rec["name"].strip(),
            "value": float(rec["value"]),
        })
    return cleaned


def summarize(records):
    """Compute summary statistics from cleaned records."""
    if not records:
        return {"count": 0, "total": 0.0, "mean": 0.0}
    values = [r["value"] for r in records]
    return {
        "count": len(values),
        "total": sum(values),
        "mean": sum(values) / len(values),
    }
'''

DATAPROC_TEST = '''\
"""Tests for data cleaner."""
from dataproc.cleaner import clean_records, summarize


def test_clean_basic():
    records = [{"name": "a", "value": 1}, {"name": "b", "value": 2.5}]
    result = clean_records(records)
    assert result == [{"name": "a", "value": 1.0}, {"name": "b", "value": 2.5}]


def test_clean_strips_whitespace():
    records = [{"name": "  hello  ", "value": 3}]
    result = clean_records(records)
    assert result[0]["name"] == "hello"


def test_clean_none_values():
    """Records with None values should get value=0.0, not crash."""
    records = [
        {"name": "a", "value": 10},
        {"name": "b", "value": None},
        {"name": "c", "value": 5},
    ]
    result = clean_records(records)
    assert len(result) == 3
    assert result[1]["value"] == 0.0


def test_summarize():
    records = [{"name": "a", "value": 10.0}, {"name": "b", "value": 20.0}]
    s = summarize(records)
    assert s["count"] == 2
    assert s["total"] == 30.0
'''


# =====================================================================
# Repo 4: configlib — split("=") without maxsplit=1
# =====================================================================
CONFIGLIB_SRC = '''\
"""Configuration file parser."""


def parse_config(text):
    """Parse KEY=VALUE configuration format.

    Supports comments (#), blank lines, and values containing = signs.
    """
    config = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split("=")
        config[key.strip()] = value.strip()
    return config


def write_config(config):
    """Write config dict back to KEY=VALUE format."""
    lines = []
    for key in sorted(config):
        lines.append(f"{key}={config[key]}")
    return chr(10).join(lines)
'''

CONFIGLIB_TEST = '''\
"""Tests for config parser."""
from configlib.parser import parse_config, write_config


def test_parse_simple():
    text = """NAME=Alice
AGE=30"""
    result = parse_config(text)
    assert result == {"NAME": "Alice", "AGE": "30"}


def test_parse_with_comments():
    text = """# comment
NAME=Bob
# another
AGE=25"""
    result = parse_config(text)
    assert result == {"NAME": "Bob", "AGE": "25"}


def test_parse_blank_lines():
    text = """A=1

B=2

"""
    result = parse_config(text)
    assert result == {"A": "1", "B": "2"}


def test_parse_value_with_equals():
    """Values can contain = signs (e.g. URLs with query params)."""
    text = """PATH=/usr/bin:/usr/local/bin
DB_URL=postgres://host:5432/db?opt=val"""
    result = parse_config(text)
    assert result["PATH"] == "/usr/bin:/usr/local/bin"
    assert result["DB_URL"] == "postgres://host:5432/db?opt=val"


def test_write_config():
    config = {"B": "2", "A": "1"}
    result = write_config(config)
    assert "A=1" in result
    assert "B=2" in result
'''


SETUP_TPL = (
    'from setuptools import setup, find_packages\n'
    'setup(name="{name}", version="0.1.0", packages=find_packages())\n'
)


def make_mathlib():
    files = {
        "mathlib/__init__.py": "",
        "mathlib/calculator.py": MATHLIB_SRC,
        "tests/__init__.py": "",
        "tests/test_calculator.py": MATHLIB_TEST,
        "setup.py": SETUP_TPL.format(name="mathlib"),
    }
    task = {
        "repo": "mathlib",
        "issue_text": (
            "safe_divide(10, 0) raises ZeroDivisionError instead of ValueError. "
            "The function should check if b is zero and raise "
            "ValueError('Cannot divide by zero') before attempting division."
        ),
        "test_selector": "tests/test_calculator.py::test_safe_divide_by_zero",
        "expected_files": ["mathlib/calculator.py"],
    }
    return _create_and_bundle("mathlib", files, task)


def make_texttools():
    files = {
        "texttools/__init__.py": "",
        "texttools/formatter.py": TEXTTOOLS_SRC,
        "tests/__init__.py": "",
        "tests/test_formatter.py": TEXTTOOLS_TEST,
        "setup.py": SETUP_TPL.format(name="texttools"),
    }
    task = {
        "repo": "texttools",
        "issue_text": (
            "truncate('Hello', 5) returns 'He...' instead of 'Hello'. "
            "The comparison uses len(text) < max_length but should use "
            "len(text) <= max_length so text exactly at max_length is unchanged."
        ),
        "test_selector": "tests/test_formatter.py::test_truncate_exact_length",
        "expected_files": ["texttools/formatter.py"],
    }
    return _create_and_bundle("texttools", files, task)


def make_dataproc():
    files = {
        "dataproc/__init__.py": "",
        "dataproc/cleaner.py": DATAPROC_SRC,
        "tests/__init__.py": "",
        "tests/test_cleaner.py": DATAPROC_TEST,
        "setup.py": SETUP_TPL.format(name="dataproc"),
    }
    task = {
        "repo": "dataproc",
        "issue_text": (
            "clean_records crashes with TypeError when a record has "
            "value=None. float(None) raises TypeError. The function "
            "should check for None and substitute 0.0."
        ),
        "test_selector": "tests/test_cleaner.py::test_clean_none_values",
        "expected_files": ["dataproc/cleaner.py"],
    }
    return _create_and_bundle("dataproc", files, task)


def make_configlib():
    files = {
        "configlib/__init__.py": "",
        "configlib/parser.py": CONFIGLIB_SRC,
        "tests/__init__.py": "",
        "tests/test_parser.py": CONFIGLIB_TEST,
        "setup.py": SETUP_TPL.format(name="configlib"),
    }
    task = {
        "repo": "configlib",
        "issue_text": (
            "parse_config crashes with 'too many values to unpack' when a "
            "value contains '=' characters (e.g. DB_URL=postgres://host/db?opt=val). "
            "Fix: use split('=', 1) to split on only the first '='."
        ),
        "test_selector": "tests/test_parser.py::test_parse_value_with_equals",
        "expected_files": ["configlib/parser.py"],
    }
    return _create_and_bundle("configlib", files, task)


# =====================================================================
# Repo 5: cachelib — TTL cache with TWO interacting bugs
#   Bug A: expired entries not evicted on get() (stale data returned)
#   Bug B: size() counts expired entries (should only count live ones)
# =====================================================================
CACHELIB_SRC = '''\
"""Simple TTL cache."""
import time


class TTLCache:
    """Key-value cache with time-to-live expiration."""

    def __init__(self, default_ttl: float = 60.0):
        self._store: dict = {}
        self._default_ttl = default_ttl

    def set(self, key: str, value, ttl: float | None = None) -> None:
        """Store a value with optional custom TTL."""
        t = ttl if ttl is not None else self._default_ttl
        self._store[key] = (value, time.time() + t)

    def get(self, key: str, default=None):
        """Retrieve value if key exists and is not expired."""
        if key not in self._store:
            return default
        value, expires = self._store[key]
        # BUG A: should check if expired and evict, but doesn't
        return value

    def size(self) -> int:
        """Return count of live (non-expired) entries."""
        # BUG B: counts ALL entries, including expired ones
        return len(self._store)

    def clear(self) -> None:
        self._store.clear()
'''

CACHELIB_TEST = '''\
"""Tests for TTL cache."""
import time
from cachelib.cache import TTLCache


def test_set_and_get():
    c = TTLCache(default_ttl=10)
    c.set("a", 1)
    assert c.get("a") == 1


def test_get_missing():
    c = TTLCache()
    assert c.get("nope") is None
    assert c.get("nope", 42) == 42


def test_clear():
    c = TTLCache()
    c.set("a", 1)
    c.clear()
    assert c.size() == 0


def test_expired_get_returns_default():
    """Expired entries must return default, not stale data."""
    c = TTLCache()
    c.set("x", "fresh", ttl=0.05)
    time.sleep(0.1)
    assert c.get("x") is None, "Expected None for expired key"


def test_size_excludes_expired():
    """size() should only count non-expired entries."""
    c = TTLCache()
    c.set("live", 1, ttl=10)
    c.set("dead", 2, ttl=0.05)
    time.sleep(0.1)
    assert c.size() == 1, "Expired entry should not count"
'''


def make_cachelib():
    files = {
        "cachelib/__init__.py": "",
        "cachelib/cache.py": CACHELIB_SRC,
        "tests/__init__.py": "",
        "tests/test_cache.py": CACHELIB_TEST,
        "setup.py": SETUP_TPL.format(name="cachelib"),
    }
    task = {
        "repo": "cachelib",
        "issue_text": (
            "TTLCache has two bugs: (1) get() returns stale data for expired "
            "keys instead of returning the default and evicting the entry, and "
            "(2) size() counts expired entries. Both need fixing: get() should "
            "check if time.time() > expires and evict/return default, and "
            "size() should filter out expired entries."
        ),
        "test_selector": "tests/test_cache.py",
        "expected_files": ["cachelib/cache.py"],
    }
    return _create_and_bundle("cachelib", files, task)


def main():
    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    print("Creating test repositories with known bugs...")
    tasks = [
        make_mathlib(),
        make_texttools(),
        make_dataproc(),
        make_configlib(),
        make_cachelib(),
    ]
    with open(TASKS_PATH, "w") as f:
        for t in tasks:
            f.write(json.dumps(t) + "\n")
    print(f"\nCreated {len(tasks)} repos -> {TASKS_PATH}")


if __name__ == "__main__":
    main()
