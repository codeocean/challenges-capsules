#!/usr/bin/env python3
"""Query BFF — NL-to-filter pipeline over real BioFileFinder metadata.

Two modes:
  1. SINGLE QUERY  (--query "..."):  Translate one NL question into filters,
     execute against the manifest, write /results/query_answer.json.
  2. EVALUATION    (no --query):  Run gold-standard queries, compute metrics,
     write /results/evaluation_report.json.

LLM: AWS Bedrock Converse API (Claude Sonnet). No direct Anthropic/OpenAI SDK.
Data: Real Allen Cell metadata from attached data assets or public S3 download.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import boto3
import pandas as pd
from pydantic import BaseModel, field_validator, ValidationError

# ── Paths ─────────────────────────────────────────────────────────

DATA_DIR = Path("/data")
RESULTS_DIR = Path("/results")
SCRATCH_DIR = Path("/scratch")

# ── Bedrock config ────────────────────────────────────────────────

MAX_ENUM_VALUES = 200
BEDROCK_MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0"
)
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
FALLBACK_MODELS = [
    "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "anthropic.claude-sonnet-4-20250514-v1:0",
    "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "us.anthropic.claude-3-haiku-20240307-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
]

# ── Schema extraction ─────────────────────────────────────────────

def extract_schema(df: pd.DataFrame) -> list[dict]:
    """Auto-extract compact schema from real manifest columns."""
    schema = []
    for col in df.columns:
        if col.startswith("_"):
            continue  # skip internal columns
        info: dict = {
            "name": col,
            "dtype": str(df[col].dtype),
            "nunique": int(df[col].nunique()),
            "null_count": int(df[col].isnull().sum()),
            "total_rows": len(df),
        }
        if info["nunique"] <= MAX_ENUM_VALUES and info["nunique"] > 0:
            vals = df[col].dropna().unique().tolist()
            info["values"] = sorted(
                [str(v) if not isinstance(v, (str, int, float, bool)) else v for v in vals],
                key=str,
            )
        else:
            info["sample_values"] = [str(v) for v in df[col].dropna().head(10).tolist()]
        schema.append(info)
    return schema


def schema_to_prompt(schema: list[dict]) -> str:
    """Format schema for LLM prompt — concise, values included."""
    lines = ["Available columns in the BFF manifest:\n"]
    for col in schema:
        line = f"- **{col['name']}** (type: {col['dtype']}, {col['nunique']} unique values)"
        if "values" in col:
            vs = ", ".join(str(v) for v in col["values"][:40])
            if len(col["values"]) > 40:
                vs += f", ... ({len(col['values'])} total)"
            line += f"\n  Values: [{vs}]"
        elif "sample_values" in col:
            line += f"\n  Sample: {col['sample_values']}"
        lines.append(line)
    return "\n".join(lines)


# ── Synonym maps (scientific vocabulary normalization) ────────────

GENE_SYNONYMS: dict[str, str] = {
    "lamin b": "LMNB1", "lamin b1": "LMNB1", "lamin a": "LMNA",
    "alpha actinin": "ACTN1", "actinin": "ACTN1",
    "myosin": "MYH10", "non-muscle myosin": "MYH10",
    "tom20": "TOMM20", "tomm20": "TOMM20",
    "sec61": "SEC61B", "sec61b": "SEC61B",
    "tubulin": "TUBA1B", "alpha tubulin": "TUBA1B",
    "beta actin": "ACTB", "actin beta": "ACTB",
    "fibrillarin": "FBL", "connexin 43": "GJA1",
    "desmoplakin": "DSP", "paxillin": "PXN", "lamp1": "LAMP1",
    "npm1": "NPM1", "nucleophosmin": "NPM1",
}

STRUCTURE_SYNONYMS: dict[str, str] = {
    "nucleus": "Nuclear envelope", "nuclear": "Nuclear envelope",
    "nuclear membrane": "Nuclear envelope",
    "actin": "Actin filaments", "actin filament": "Actin filaments",
    "tubulin": "Microtubules", "microtubule": "Microtubules",
    "er": "Endoplasmic reticulum",
    "endoplasmic reticulum": "Endoplasmic reticulum",
    "golgi": "Golgi", "golgi apparatus": "Golgi",
    "mitochondria": "Mitochondria", "mitochondrion": "Mitochondria",
    "lysosome": "Lysosomes", "lysosomes": "Lysosomes",
    "plasma membrane": "Plasma membrane", "cell membrane": "Plasma membrane",
    "nucleolus": "Nucleolus (fibrillar center)",
    "tight junction": "Tight junctions", "tight junctions": "Tight junctions",
    "gap junction": "Gap junctions", "gap junctions": "Gap junctions",
    "desmosome": "Desmosomes", "desmosomes": "Desmosomes",
    "nuclear pore": "Nuclear pores", "nuclear pores": "Nuclear pores",
    "nuclear speckle": "Nuclear speckles", "nuclear speckles": "Nuclear speckles",
    "peroxisome": "Peroxisomes", "peroxisomes": "Peroxisomes",
    "endosome": "Endosomes", "endosomes": "Endosomes",
    "centriole": "Centrioles", "centrioles": "Centrioles",
}


def _synonym_prompt() -> str:
    """Build synonym reference for the LLM system prompt."""
    lines = ["Gene synonyms (informal → canonical Gene value):"]
    for k, v in sorted(GENE_SYNONYMS.items()):
        lines.append(f"  '{k}' → '{v}'")
    lines.append("\nStructure synonyms (informal → canonical Structure Name value):")
    for k, v in sorted(STRUCTURE_SYNONYMS.items()):
        lines.append(f"  '{k}' → '{v}'")
    return "\n".join(lines)


# ── Pydantic filter model ────────────────────────────────────────

VALID_COLUMNS: set[str] = set()


class FilterSpec(BaseModel):
    column: str
    operator: str  # ==, !=, contains, in, >, <
    value: Any

    @field_validator("column")
    @classmethod
    def column_must_exist(cls, v: str) -> str:
        if not VALID_COLUMNS:
            return v
        if v in VALID_COLUMNS:
            return v
        # Case-insensitive match
        for vc in VALID_COLUMNS:
            if vc.lower() == v.lower():
                return vc
        # Substring match
        for vc in VALID_COLUMNS:
            if v.lower() in vc.lower() or vc.lower() in v.lower():
                return vc
        raise ValueError(f"Unknown column '{v}'. Valid: {sorted(VALID_COLUMNS)}")


class QueryResult(BaseModel):
    filters: list[FilterSpec]
    explanation: str
    confidence: float = 1.0


# ── Bedrock LLM ──────────────────────────────────────────────────

_bedrock_client = None


def _get_bedrock():
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
    return _bedrock_client


def _call_bedrock(system: str, user: str) -> dict:
    """Call Bedrock Converse → parsed JSON dict. Tries fallback models."""
    client = _get_bedrock()
    models = [BEDROCK_MODEL_ID] + [m for m in FALLBACK_MODELS if m != BEDROCK_MODEL_ID]
    last_err: Exception | None = None
    for mid in models:
        try:
            resp = client.converse(
                modelId=mid,
                messages=[{"role": "user", "content": [{"text": user}]}],
                system=[{"text": system}],
                inferenceConfig={"maxTokens": 2048, "temperature": 0.0},
            )
            text = "".join(
                b["text"] for b in resp["output"]["message"]["content"] if "text" in b
            )
            s, e = text.find("{"), text.rfind("}") + 1
            if s == -1 or e == 0:
                raise ValueError(f"No JSON in response: {text[:300]}")
            return json.loads(text[s:e])
        except Exception as exc:
            last_err = exc
            el = str(exc).lower()
            if any(k in el for k in ("validation", "access", "not supported",
                                     "not found", "not available", "throttl")):
                print(f"    [{mid}] {type(exc).__name__}, trying next …", file=sys.stderr)
                continue
            raise
    raise RuntimeError(f"All Bedrock models failed. Last: {last_err}")


# ── NL → Filter translation ──────────────────────────────────────

def _fuzzy_col(name: str, valid: set[str]) -> str:
    nl = name.lower().strip()
    for c in valid:
        if c.lower() == nl:
            return c
    for c in valid:
        if nl in c.lower() or c.lower() in nl:
            return c
    return name


def translate_query(query: str, schema_prompt: str) -> QueryResult:
    """Translate one NL query → structured filters via Bedrock."""
    system = (
        "You are a metadata search assistant for the Allen Cell Collection "
        "(BioFileFinder). Given a natural language query, return a JSON object:\n"
        '{"filters": [{"column": "...", "operator": "==|!=|contains|in|>|<", '
        '"value": ...}], "explanation": "one sentence explaining interpretation", '
        '"confidence": 0.0-1.0}\n\n'
        "RULES:\n"
        "1. Use ONLY column names from the schema below.\n"
        "2. Use exact values from the schema value lists when available.\n"
        "3. Normalize gene/structure names using the synonym maps.\n"
        "4. Numeric values stay numeric (not strings).\n"
        "5. Set confidence < 0.5 if unsure about the mapping.\n"
        "6. Return ONLY JSON, no markdown fences.\n\n"
        f"{_synonym_prompt()}\n"
    )
    user = f"Schema:\n{schema_prompt}\n\nQuery: {query}"
    try:
        d = _call_bedrock(system, user)
    except Exception as exc:
        return QueryResult(filters=[], explanation=f"LLM error: {exc}", confidence=0.0)

    # Fix column names
    for f in d.get("filters", []):
        col = f.get("column", "")
        if col not in VALID_COLUMNS:
            f["column"] = _fuzzy_col(col, VALID_COLUMNS)

    try:
        return QueryResult(**d)
    except ValidationError as exc:
        return QueryResult(filters=[], explanation=f"Validation: {exc}", confidence=0.0)


# ── Clarification loop ───────────────────────────────────────────

def translate_with_clarification(query: str, schema_prompt: str, df: pd.DataFrame) -> QueryResult:
    """Translate query; if empty results or low confidence, try relaxed version."""
    qr = translate_query(query, schema_prompt)
    filtered = apply_filters(df, qr.filters)

    # If empty results, retry with relaxed prompt
    if len(filtered) == 0 and qr.filters:
        filter_desc = ", ".join(f"{f.column}{f.operator}{f.value}" for f in qr.filters)
        relaxed_query = (
            f"The previous query returned 0 results. Original: '{query}'. "
            f"Filters tried: [{filter_desc}]. "
            f"Try broader or fewer filters. Maybe use 'contains' instead of '=='."
        )
        qr2 = translate_query(relaxed_query, schema_prompt)
        filtered2 = apply_filters(df, qr2.filters)
        if len(filtered2) > 0:
            qr2.explanation += " [Relaxed: original filters returned 0 results]"
            return qr2
        qr.explanation += " [WARNING: 0 results even after relaxation]"

    if qr.confidence < 0.5:
        qr.explanation += " [LOW CONFIDENCE: manual review recommended]"

    return qr


# ── Filter execution ──────────────────────────────────────────────

def apply_filters(df: pd.DataFrame, filters: list[FilterSpec]) -> pd.DataFrame:
    result = df.copy()
    for f in filters:
        col, op, val = f.column, f.operator, f.value
        if col not in result.columns:
            continue
        try:
            if op == "==":
                if isinstance(val, (int, float)):
                    result = result[pd.to_numeric(result[col], errors="coerce") == float(val)]
                else:
                    result = result[result[col].astype(str).str.lower() == str(val).lower()]
            elif op == "!=":
                result = result[result[col].astype(str).str.lower() != str(val).lower()]
            elif op == "contains":
                result = result[result[col].astype(str).str.contains(str(val), case=False, na=False)]
            elif op == "in" and isinstance(val, list):
                lower_vals = [str(v).lower() for v in val]
                result = result[result[col].astype(str).str.lower().isin(lower_vals)]
            elif op == ">":
                result = result[pd.to_numeric(result[col], errors="coerce") > float(val)]
            elif op == "<":
                result = result[pd.to_numeric(result[col], errors="coerce") < float(val)]
        except Exception:
            pass
    return result


# ── Manifest loader ───────────────────────────────────────────────

def load_manifest() -> pd.DataFrame:
    """Load BFF manifest from /data or /scratch. Never generate synthetic data."""

    # 1. Check /scratch for merged manifest from fetch_bff_data.py
    scratch_manifest = SCRATCH_DIR / "bff_manifest.csv"
    if scratch_manifest.exists() and scratch_manifest.stat().st_size > 1000:
        print(f"Loading manifest from: {scratch_manifest}")
        return pd.read_csv(scratch_manifest, low_memory=False)

    # 2. Search /data for any CSV/Parquet (skip challenge spec docs)
    for ext in ("*.csv", "*.parquet"):
        for p in DATA_DIR.rglob(ext):
            if p.stat().st_size > 1000 and "hackathon_challang" not in str(p):
                print(f"Loading manifest from: {p}")
                return pd.read_parquet(p) if p.suffix == ".parquet" else pd.read_csv(p, low_memory=False)

    raise FileNotFoundError(
        "No BFF manifest found. Attach a CSV/Parquet manifest as a data asset, "
        "or run fetch_bff_data.py first to download from s3://allencell."
    )


# ── Evaluation ────────────────────────────────────────────────────

def build_eval_queries(df: pd.DataFrame) -> list[dict]:
    """Build evaluation queries dynamically from real manifest values.

    Inspects actual column values to create gold-standard filters
    that are guaranteed to exist in the data.
    """
    queries = []
    cols = set(df.columns)

    # Helper: get first value for a column matching a condition
    def first_val(col: str, contains: str | None = None) -> str | None:
        if col not in cols:
            return None
        vals = df[col].dropna().unique()
        if contains:
            matches = [v for v in vals if contains.lower() in str(v).lower()]
            return str(matches[0]) if matches else None
        return str(vals[0]) if len(vals) > 0 else None

    # Gene-based queries
    if "gene" in [c.lower() for c in cols]:
        gene_col = next(c for c in cols if c.lower() == "gene")
        genes = df[gene_col].dropna().unique()
        if len(genes) > 0:
            g = str(genes[0])
            queries.append({
                "query": f"Show me all images with gene {g}",
                "gold_filters": [{"name": gene_col, "value": g}],
                "category": "gene_lookup", "difficulty": "easy",
            })

    # Structure-based queries
    struct_col = None
    for c in cols:
        if "structure" in c.lower():
            struct_col = c
            break
    if struct_col:
        structs = df[struct_col].dropna().unique()
        if len(structs) > 0:
            s = str(structs[0])
            queries.append({
                "query": f"Find {s} images",
                "gold_filters": [{"name": struct_col, "value": s}],
                "category": "structure_lookup", "difficulty": "easy",
            })
            if len(structs) > 1:
                s2 = str(structs[1])
                queries.append({
                    "query": f"Show me {s2} data",
                    "gold_filters": [{"name": struct_col, "value": s2}],
                    "category": "structure_lookup", "difficulty": "easy",
                })

    # Cell line queries
    cl_col = None
    for c in cols:
        if "cell" in c.lower() and "line" in c.lower():
            cl_col = c
            break
    if cl_col:
        lines = df[cl_col].dropna().unique()
        if len(lines) > 0:
            cl = str(lines[0])
            queries.append({
                "query": f"Show me images from cell line {cl}",
                "gold_filters": [{"name": cl_col, "value": cl}],
                "category": "cell_line_lookup", "difficulty": "easy",
            })

    # Multi-field queries
    if struct_col and cl_col:
        # Find a combo that has data
        for s in df[struct_col].dropna().unique()[:5]:
            sub = df[df[struct_col] == s]
            for cl in sub[cl_col].dropna().unique()[:3]:
                queries.append({
                    "query": f"Find {s} images from cell line {cl}",
                    "gold_filters": [
                        {"name": struct_col, "value": str(s)},
                        {"name": cl_col, "value": str(cl)},
                    ],
                    "category": "multi_field", "difficulty": "medium",
                })
                break
            break

    # Synonym queries (only if relevant columns exist)
    if struct_col and "Nuclear envelope" in df[struct_col].values:
        queries.append({
            "query": "Find nuclear envelope images",
            "gold_filters": [{"name": struct_col, "value": "Nuclear envelope"}],
            "category": "structure_lookup", "difficulty": "easy",
        })
    if struct_col and "Actin filaments" in df[struct_col].values:
        queries.append({
            "query": "Which cell lines have actin filament data?",
            "gold_filters": [{"name": struct_col, "value": "Actin filaments"}],
            "category": "structure_synonym", "difficulty": "easy",
        })

    # Add a few keyword-contains queries
    for c in cols:
        if df[c].dtype == "object" and df[c].nunique() > 5:
            sample = str(df[c].dropna().iloc[0]) if len(df[c].dropna()) > 0 else None
            if sample and len(sample) > 3:
                queries.append({
                    "query": f"Find entries containing '{sample[:20]}' in {c}",
                    "gold_filters": [{"name": c, "value": sample}],
                    "category": "contains_lookup", "difficulty": "easy",
                })
                break

    # Pad to at least 10 queries with generic column lookups
    for c in list(cols)[:15]:
        if len(queries) >= 15:
            break
        if c.startswith("_"):
            continue
        vals = df[c].dropna().unique()
        if 2 <= len(vals) <= 50:
            v = str(vals[min(1, len(vals) - 1)])
            queries.append({
                "query": f"Show me entries where {c} is {v}",
                "gold_filters": [{"name": c, "value": v}],
                "category": "direct_lookup", "difficulty": "easy",
            })

    return queries[:15]


def eval_filters(gen: list[dict], gold: list[dict]) -> dict:
    """Compare generated filters against gold standard."""
    matches = 0
    for gf in gold:
        gn = gf["name"]
        gv = str(gf["value"]).lower().strip()
        for gf2 in gen:
            col = gf2.get("column", "")
            val = str(gf2.get("value", "")).lower().strip()
            if col.lower() == gn.lower() and val == gv:
                matches += 1
                break
    p = matches / len(gen) if gen else 0.0
    r = matches / len(gold) if gold else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    return {"matches": matches, "gen_count": len(gen), "gold_count": len(gold),
            "precision": round(p, 4), "recall": round(r, 4), "f1": round(f1, 4)}


# ── Mode 1: Single query ─────────────────────────────────────────

def run_single_query(query: str, df: pd.DataFrame, schema_prompt: str) -> dict:
    t0 = time.time()
    qr = translate_with_clarification(query, schema_prompt, df)
    elapsed = time.time() - t0

    filtered = apply_filters(df, qr.filters)
    sample_rows = filtered.head(10).to_dict(orient="records")
    # Stringify datetimes
    for row in sample_rows:
        for k, v in row.items():
            if isinstance(v, (pd.Timestamp, datetime)):
                row[k] = str(v)

    answer = {
        "query": query,
        "data_source": "REAL Allen Cell Collection metadata",
        "filters_generated": [f.model_dump() for f in qr.filters],
        "explanation": qr.explanation,
        "confidence": qr.confidence,
        "total_matching_rows": len(filtered),
        "sample_results": sample_rows,
        "latency_seconds": round(elapsed, 2),
        "manifest_rows": len(df),
        "manifest_columns": len(df.columns),
    }

    path = RESULTS_DIR / "query_answer.json"
    with open(path, "w") as fh:
        json.dump(answer, fh, indent=2, default=str)
    print(json.dumps(answer, indent=2, default=str))

    # Generate HTML summary + download thumbnails
    thumb_paths = download_thumbnails(filtered.head(6), df)
    generate_html_report(answer, thumb_paths)

    return answer


# ── Mode 2: Evaluation ───────────────────────────────────────────

def run_evaluation(df: pd.DataFrame, schema_prompt: str) -> dict:
    eval_qs = build_eval_queries(df)
    print(f"\nRunning {len(eval_qs)} evaluation queries (derived from real data) …")

    results, correct, total_t = [], 0, 0.0
    for i, q in enumerate(eval_qs):
        qt = q["query"]
        gf = q.get("gold_filters", [])
        print(f"\n  [{i+1}/{len(eval_qs)}] {qt}")

        t0 = time.time()
        qr = translate_query(qt, schema_prompt)
        el = time.time() - t0
        total_t += el

        filtered = apply_filters(df, qr.filters)
        gd = [f.model_dump() for f in qr.filters]
        ev = eval_filters(gd, gf)
        gold_match = ev["recall"] >= 0.99
        if gold_match:
            correct += 1

        results.append({
            "query": qt, "category": q.get("category", ""),
            "difficulty": q.get("difficulty", ""),
            "generated_filters": gd, "gold_filters": gf,
            "result_count": len(filtered), "explanation": qr.explanation,
            "confidence": qr.confidence,
            "matches_gold": gold_match, "eval_metrics": ev,
            "latency_seconds": round(el, 2),
        })
        print(f"    → Filters: {gd}")
        print(f"    Results={len(filtered)}, Gold={gold_match}, {el:.1f}s")

    sr = correct / len(eval_qs) if eval_qs else 0.0
    al = total_t / len(eval_qs) if eval_qs else 0.0

    report = {
        "data_source": "REAL Allen Cell Collection metadata",
        "total_queries": len(eval_qs), "correct": correct,
        "success_rate": round(sr, 4),
        "average_latency_seconds": round(al, 2),
        "bedrock_model": BEDROCK_MODEL_ID,
        "manifest_rows": len(df), "manifest_columns": len(df.columns),
        "queries": results,
    }
    out = RESULTS_DIR / "evaluation_report.json"
    with open(out, "w") as fh:
        json.dump(report, fh, indent=2, default=str)
    print(f"\n{'='*60}")
    print(f"Success: {correct}/{len(eval_qs)} ({sr:.0%}), avg {al:.1f}s")
    print(f"{'='*60}")
    return report


# ── Thumbnail download ────────────────────────────────────────────

THUMB_BUCKET = "allencell"
THUMB_PREFIX_MAP = {
    "crop_raw": "aics/hipsc_single_cell_image_dataset_supp_myh10/",
    "crop_seg": "aics/hipsc_single_cell_image_dataset_supp_myh10/",
}


def download_thumbnails(filtered: pd.DataFrame, full_df: pd.DataFrame, max_thumbs: int = 6) -> list[str]:
    """Try to download thumbnail images from S3 for matching cells."""
    from botocore import UNSIGNED
    from botocore.config import Config

    thumbs_dir = RESULTS_DIR / "thumbnails"
    thumbs_dir.mkdir(parents=True, exist_ok=True)
    downloaded = []

    # Identify image path columns
    img_cols = [c for c in filtered.columns if any(k in c.lower() for k in ("crop_raw", "crop_seg", "fov_path"))]
    if not img_cols:
        return downloaded

    col = img_cols[0]  # prefer crop_raw or crop_seg
    try:
        s3 = boto3.client("s3", region_name=AWS_REGION, config=Config(signature_version=UNSIGNED))
    except Exception:
        return downloaded

    for idx, row in filtered.head(max_thumbs).iterrows():
        rel_path = str(row.get(col, ""))
        if not rel_path or rel_path == "nan":
            continue
        # Build S3 key: prefix + relative path
        prefix = THUMB_PREFIX_MAP.get(col, "aics/hipsc_single_cell_image_dataset_supp_myh10/")
        s3_key = prefix + rel_path.lstrip("./")
        local_name = Path(rel_path).name
        local_path = thumbs_dir / local_name
        try:
            s3.download_file(THUMB_BUCKET, s3_key, str(local_path))
            downloaded.append(f"thumbnails/{local_name}")
            print(f"  ↓ Thumbnail: {local_name} ({local_path.stat().st_size / 1024:.0f} KB)")
        except Exception as e:
            print(f"  ✗ Thumbnail skip: {local_name} ({e})")
    return downloaded


# ── HTML report generation ────────────────────────────────────────

def generate_html_report(answer: dict, thumb_paths: list[str]) -> None:
    """Generate a visual HTML summary of the query results."""
    query = answer.get("query", "")
    explanation = answer.get("explanation", "")
    confidence = answer.get("confidence", 0)
    total = answer.get("total_matching_rows", 0)
    filters = answer.get("filters_generated", [])
    samples = answer.get("sample_results", [])
    latency = answer.get("latency_seconds", 0)
    manifest_rows = answer.get("manifest_rows", 0)

    conf_color = "#28a745" if confidence >= 0.8 else "#ffc107" if confidence >= 0.5 else "#dc3545"
    filter_html = "".join(
        f'<span class="filter">{f["column"]} {f["operator"]} {f["value"]}</span>'
        for f in filters
    )

    # Thumbnails gallery
    thumb_html = ""
    if thumb_paths:
        imgs = "".join(f'<div class="thumb"><img src="{p}" alt="cell"><div class="cap">{Path(p).stem[:20]}</div></div>' for p in thumb_paths)
        thumb_html = f'<div class="gallery"><h3>🔬 Cell Thumbnails</h3><div class="thumb-row">{imgs}</div></div>'

    # Results table (first 10 rows, limited columns)
    table_html = ""
    if samples:
        # Pick interesting columns (skip paths)
        skip = {"crop_raw", "crop_seg", "crop_seg_nuc", "fov_path", "fov_seg_path",
                "struct_seg_path", "name_dict", "scale_micron", "roi", "this_cell_nbr_dist_2d"}
        show_cols = [k for k in samples[0].keys() if k not in skip][:8]
        headers = "".join(f"<th>{c}</th>" for c in show_cols)
        rows = ""
        for r in samples[:10]:
            cells = "".join(f"<td>{r.get(c, '')}</td>" for c in show_cols)
            rows += f"<tr>{cells}</tr>"
        table_html = f"""
        <h3>📋 Sample Results (top 10 of {total})</h3>
        <div class="table-wrap"><table><tr>{headers}</tr>{rows}</table></div>"""

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Query BFF Results</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 20px; background: #f8f9fa; }}
  .card {{ background: white; border-radius: 12px; padding: 24px; margin: 16px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
  h1 {{ color: #1a1a2e; font-size: 1.6em; }}
  h3 {{ color: #16213e; margin-top: 20px; }}
  .query {{ font-size: 1.2em; color: #0f3460; background: #e8f4f8; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #0f3460; }}
  .meta {{ display: flex; gap: 24px; flex-wrap: wrap; margin: 16px 0; }}
  .meta-item {{ background: #f0f2f5; padding: 8px 16px; border-radius: 6px; }}
  .meta-item strong {{ color: #333; }}
  .confidence {{ display: inline-block; padding: 4px 12px; border-radius: 12px; color: white; font-weight: bold; background: {conf_color}; }}
  .filter {{ display: inline-block; background: #e3f2fd; color: #1565c0; padding: 4px 10px; border-radius: 4px; margin: 2px 4px; font-family: monospace; font-size: 0.9em; }}
  .explanation {{ color: #555; font-style: italic; padding: 8px 0; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.85em; }}
  th {{ background: #1a1a2e; color: white; padding: 8px 12px; text-align: left; }}
  td {{ padding: 6px 12px; border-bottom: 1px solid #eee; }}
  tr:hover {{ background: #f5f5f5; }}
  .table-wrap {{ overflow-x: auto; }}
  .gallery {{ margin-top: 20px; }}
  .thumb-row {{ display: flex; gap: 12px; flex-wrap: wrap; }}
  .thumb {{ text-align: center; }}
  .thumb img {{ max-width: 150px; max-height: 150px; border-radius: 8px; border: 2px solid #ddd; }}
  .cap {{ font-size: 0.75em; color: #666; margin-top: 4px; }}
  .footer {{ color: #999; font-size: 0.8em; margin-top: 24px; }}
</style></head>
<body>
<div class="card">
  <h1>🔍 Query BFF — Results</h1>
  <div class="query">"{query}"</div>
  <div class="meta">
    <div class="meta-item">🎯 <strong>{total}</strong> matching rows</div>
    <div class="meta-item">📊 out of <strong>{manifest_rows}</strong> total</div>
    <div class="meta-item">⏱️ <strong>{latency}s</strong></div>
    <div class="meta-item">Confidence: <span class="confidence">{confidence:.0%}</span></div>
  </div>
  <p class="explanation">💡 {explanation}</p>
  <div>Filters applied: {filter_html if filter_html else '<em>none</em>'}</div>
  {thumb_html}
  {table_html}
  <div class="footer">Data: REAL Allen Cell Collection metadata | LLM: AWS Bedrock Claude Sonnet</div>
</div>
</body></html>"""

    out = RESULTS_DIR / "results_summary.html"
    out.write_text(html)
    print(f"  ✓ HTML report: {out}")


# ── Main ──────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Query BFF — NL search over BioFileFinder metadata")
    p.add_argument("--query", "-q", type=str, default=None,
                   help="Single NL query. Omit for evaluation mode.")
    return p.parse_args()


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    args = parse_args()

    # Load real manifest
    df = load_manifest()
    print(f"  Manifest: {len(df)} rows × {len(df.columns)} columns")
    print(f"  Columns: {list(df.columns)}")

    # Extract schema
    schema = extract_schema(df)
    schema_prompt = schema_to_prompt(schema)
    global VALID_COLUMNS
    VALID_COLUMNS = {col for col in df.columns if not col.startswith("_")}

    with open(RESULTS_DIR / "extracted_schema.json", "w") as fh:
        json.dump(schema, fh, indent=2, default=str)

    # Dispatch
    if args.query:
        print(f"\n[SINGLE QUERY] {args.query!r}\n")
        run_single_query(args.query, df, schema_prompt)
    else:
        run_evaluation(df, schema_prompt)


if __name__ == "__main__":
    main()
