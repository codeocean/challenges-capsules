#!/usr/bin/env python3
"""Create 5 self-contained test repos with intentional bugs.

Task mix designed to demonstrate the full agent capability spectrum:
  1. mathlib      — easy single-bug (division by zero)
  2. configlib    — easy single-bug (split without maxsplit)
  3. cachelib     — medium two-bug (TTL expiration)
  4. numextract   — HARD: naive fix causes regression, forces multi-iteration
  5. tempconv     — IMPOSSIBLE: contradictory test, demonstrates graceful stop
"""

import json
import shutil
import subprocess
from pathlib import Path

SCRATCH = Path("/scratch")
REPOS_DIR = SCRATCH / "repos"
TASKS_PATH = SCRATCH / "tasks.jsonl"

SETUP_TPL = (
    'from setuptools import setup, find_packages\n'
    'setup(name="{name}", version="0.1.0", packages=find_packages())\n'
)


def _git(d: Path, *args: str) -> None:
    subprocess.run(["git"] + list(args), cwd=str(d),
                   capture_output=True, check=True)


def _create(name: str, files: dict, task: dict) -> dict:
    d = REPOS_DIR / name
    if d.exists():
        shutil.rmtree(d)
    for p, c in files.items():
        fp = d / p
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(c)
    _git(d, "init", "-b", "main")
    _git(d, "config", "user.email", "test@example.com")
    _git(d, "config", "user.name", "Test")
    _git(d, "add", ".")
    _git(d, "commit", "-m", f"Initial: {name}")
    bun = REPOS_DIR / f"{name}.bundle"
    _git(d, "bundle", "create", str(bun), "--all")
    print(f"  {name} -> {bun}")
    return task


# === Repo 1: mathlib (easy) ================================================
MATH_SRC = '''\
"""Calculator module."""


def add(a, b):
    return a + b


def safe_divide(a, b):
    """Raises ValueError('Cannot divide by zero') if b is zero."""
    return a / b
'''
MATH_TEST = '''\
import pytest
from mathlib.calculator import add, safe_divide

def test_add():
    assert add(2, 3) == 5

def test_safe_divide():
    assert safe_divide(10, 2) == 5.0

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        safe_divide(10, 0)
'''


def make_mathlib():
    return _create("mathlib", {
        "mathlib/__init__.py": "", "mathlib/calculator.py": MATH_SRC,
        "tests/__init__.py": "", "tests/test_calculator.py": MATH_TEST,
        "setup.py": SETUP_TPL.format(name="mathlib"),
    }, {
        "repo": "mathlib",
        "issue_text": "safe_divide(10, 0) raises ZeroDivisionError instead of "
                      "ValueError. Add a zero check that raises "
                      "ValueError('Cannot divide by zero').",
        "test_selector": "tests/test_calculator.py::test_divide_by_zero",
        "expected_files": ["mathlib/calculator.py"],
    })


# === Repo 2: configlib (easy) ==============================================
CFG_SRC = '''\
"""Configuration file parser."""


def parse_config(text):
    """Parse KEY=VALUE lines. Supports comments (#) and values with = signs."""
    config = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split("=")
        config[key.strip()] = value.strip()
    return config
'''
CFG_TEST = '''\
from configlib.parser import parse_config

def test_simple():
    assert parse_config("A=1") == {"A": "1"}

def test_comments():
    text = """# comment
NAME=Bob"""
    assert parse_config(text) == {"NAME": "Bob"}

def test_value_with_equals():
    text = """DB=postgres://h:5432/db?x=1"""
    result = parse_config(text)
    assert result["DB"] == "postgres://h:5432/db?x=1"
'''


def make_configlib():
    return _create("configlib", {
        "configlib/__init__.py": "", "configlib/parser.py": CFG_SRC,
        "tests/__init__.py": "", "tests/test_parser.py": CFG_TEST,
        "setup.py": SETUP_TPL.format(name="configlib"),
    }, {
        "repo": "configlib",
        "issue_text": "parse_config crashes with 'too many values to unpack' when "
                      "a value contains '=' (e.g. DB=postgres://h/db?x=1). "
                      "Use split('=', 1) to split on only the first '='.",
        "test_selector": "tests/test_parser.py::test_value_with_equals",
        "expected_files": ["configlib/parser.py"],
    })


# === Repo 3: cachelib (medium — two bugs) ==================================
CACHE_SRC = '''\
"""Simple TTL cache."""
import time


class TTLCache:
    def __init__(self, default_ttl=60.0):
        self._store = {}
        self._default_ttl = default_ttl

    def set(self, key, value, ttl=None):
        t = ttl if ttl is not None else self._default_ttl
        self._store[key] = (value, time.time() + t)

    def get(self, key, default=None):
        if key not in self._store:
            return default
        value, expires = self._store[key]
        # BUG: does not check expiration
        return value

    def size(self):
        """Count of live (non-expired) entries."""
        # BUG: counts expired entries too
        return len(self._store)

    def clear(self):
        self._store.clear()
'''
CACHE_TEST = '''\
import time
from cachelib.cache import TTLCache

def test_basic():
    c = TTLCache(default_ttl=10)
    c.set("a", 1)
    assert c.get("a") == 1

def test_missing():
    c = TTLCache()
    assert c.get("x", 42) == 42

def test_expired_returns_default():
    c = TTLCache()
    c.set("k", "v", ttl=0.05)
    time.sleep(0.1)
    assert c.get("k") is None

def test_size_excludes_expired():
    c = TTLCache()
    c.set("live", 1, ttl=10)
    c.set("dead", 2, ttl=0.05)
    time.sleep(0.1)
    assert c.size() == 1
'''


def make_cachelib():
    return _create("cachelib", {
        "cachelib/__init__.py": "", "cachelib/cache.py": CACHE_SRC,
        "tests/__init__.py": "", "tests/test_cache.py": CACHE_TEST,
        "setup.py": SETUP_TPL.format(name="cachelib"),
    }, {
        "repo": "cachelib",
        "issue_text": "TTLCache has two bugs: (1) get() returns stale data for "
                      "expired keys — it should check time.time() > expires and "
                      "evict; (2) size() counts expired entries.",
        "test_selector": "tests/test_cache.py",
        "expected_files": ["cachelib/cache.py"],
    })


# === Repo 4: numextract (HARD — naive fix causes regression) ===============
NUMEX_SRC = '''\
"""Number extraction from text."""
import re


def extract_numbers(text):
    """Extract all numbers from text.

    Handles integers (42), decimals (3.14), and negative numbers (-5).
    Hyphens in ranges like '3-5' are NOT treated as negative signs.
    """
    pattern = r'\\d+\\.?\\d*'
    return [float(m) for m in re.findall(pattern, text)]
'''
NUMEX_TEST = '''\
from numextract.extractor import extract_numbers

def test_integers():
    assert extract_numbers("found 3 and 42") == [3.0, 42.0]

def test_decimals():
    assert extract_numbers("pi is 3.14") == [3.14]

def test_negative():
    """Negative numbers must include their sign."""
    assert extract_numbers("temp is -5 and -3.2") == [-5.0, -3.2]

def test_range_not_negative():
    """Hyphens in ranges must NOT make numbers negative."""
    assert extract_numbers("pages 3-5") == [3.0, 5.0]

def test_empty():
    assert extract_numbers("nothing") == []
'''


def make_numextract():
    return _create("numextract", {
        "numextract/__init__.py": "", "numextract/extractor.py": NUMEX_SRC,
        "tests/__init__.py": "", "tests/test_extractor.py": NUMEX_TEST,
        "setup.py": SETUP_TPL.format(name="numextract"),
    }, {
        "repo": "numextract",
        "issue_text": "extract_numbers does not find negative numbers. "
                      "extract_numbers('temp is -5') returns [5.0] "
                      "instead of [-5.0]. The regex needs to handle "
                      "the minus sign.",
        "test_selector": "tests/test_extractor.py::test_negative",
        "expected_files": ["numextract/extractor.py"],
    })


# === Repo 5: tempconv (IMPOSSIBLE — contradictory test) ====================
TEMP_SRC = '''\
"""Temperature conversion utilities."""


def celsius_to_fahrenheit(c):
    """Convert Celsius to Fahrenheit. F = C * 9/5 + 32"""
    return c * 9.0 / 5.0 + 32.0


def fahrenheit_to_celsius(f):
    """Convert Fahrenheit to Celsius. C = (F - 32) * 5/9"""
    return (f - 32.0) * 5.0 / 9.0
'''
TEMP_TEST = '''\
from tempconv.convert import celsius_to_fahrenheit, fahrenheit_to_celsius

def test_freezing():
    assert celsius_to_fahrenheit(0) == 32.0

def test_boiling():
    assert celsius_to_fahrenheit(100) == 212.0

def test_body_temp():
    """37C should convert to 97.7F."""
    result = celsius_to_fahrenheit(37)
    assert abs(result - 97.7) < 0.01, f"Expected ~97.7, got {result}"

def test_roundtrip():
    for c in [0, 25, 100, -40]:
        f = celsius_to_fahrenheit(c)
        c2 = fahrenheit_to_celsius(f)
        assert abs(c - c2) < 0.001, f"Roundtrip failed for {c}"

def test_linearity():
    """Conversion must be purely linear: f(a) + f(b) - f(0) == f(a+b)."""
    f = celsius_to_fahrenheit
    for a, b in [(10, 20), (37, 0), (0, 37), (50, 50)]:
        lhs = f(a) + f(b) - f(0)
        rhs = f(a + b)
        assert abs(lhs - rhs) < 0.001, (
            f"Not linear: f({a})+f({b})-f(0)={lhs} != f({a+b})={rhs}")

def test_monotonic():
    """Every 1C increase must give exactly 1.8F increase."""
    f = celsius_to_fahrenheit
    for c in range(-40, 101):
        diff = f(c + 1) - f(c)
        assert abs(diff - 1.8) < 0.001, (
            f"Non-uniform slope at {c}C: delta={diff}, expected 1.8")
'''


def make_tempconv():
    return _create("tempconv", {
        "tempconv/__init__.py": "", "tempconv/convert.py": TEMP_SRC,
        "tests/__init__.py": "", "tests/test_convert.py": TEMP_TEST,
        "setup.py": SETUP_TPL.format(name="tempconv"),
    }, {
        "repo": "tempconv",
        "issue_text": "celsius_to_fahrenheit(37) returns 98.6 but should "
                      "return 97.7 (normal body temperature). "
                      "The conversion formula seems wrong.",
        "test_selector": "tests/test_convert.py::test_body_temp",
        "expected_files": ["tempconv/convert.py"],
    })


# === Main ===================================================================

def main():
    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    print("Creating 5 test repositories...")
    tasks = [
        make_mathlib(),
        make_configlib(),
        make_cachelib(),
        make_numextract(),
        make_tempconv(),
    ]
    with open(TASKS_PATH, "w") as f:
        for t in tasks:
            f.write(json.dumps(t) + "\n")
    print(f"\nCreated {len(tasks)} repos -> {TASKS_PATH}")


if __name__ == "__main__":
    main()
