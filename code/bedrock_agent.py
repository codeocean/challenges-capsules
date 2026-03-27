#!/usr/bin/env python3
"""AWS Bedrock-based agentic analysis for BindCrafting Challenge 09.

Uses boto3 + bedrock-runtime to invoke Claude models — NEVER the anthropic
or openai Python packages directly.  Falls back to a deterministic local
report if Bedrock is unreachable (no credentials / region mismatch).

The agent receives filtered binder candidate data and fusion analysis,
then generates:
  - Scientific interpretation of the binder panel
  - Structural biology insights
  - Fluorescent fusion recommendations
  - Experimental next-steps
"""

from __future__ import annotations

import json
import os
import textwrap
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Bedrock client
# ---------------------------------------------------------------------------

# Model priority list — try newer first, fall back
_MODEL_IDS = [
    "anthropic.claude-sonnet-4-20250514-v1:0",
    "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
]


def _get_bedrock_client():
    """Create a bedrock-runtime client via boto3."""
    import boto3  # noqa: import here so module loads even without boto3

    region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
    return boto3.client("bedrock-runtime", region_name=region)


def invoke_bedrock(prompt: str, max_tokens: int = 4096, temperature: float = 0.3) -> str:
    """Invoke Claude on Bedrock. Tries multiple model IDs. Returns text."""
    client = _get_bedrock_client()

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }

    last_error: Exception | None = None
    for model_id in _MODEL_IDS:
        try:
            response = client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )
            result = json.loads(response["body"].read())
            text = result.get("content", [{}])[0].get("text", "")
            if text:
                print(f"  Bedrock model used: {model_id}")
                return text
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(
        f"All Bedrock models failed. Last error: {last_error}"
    )


# ---------------------------------------------------------------------------
# Agent analysis
# ---------------------------------------------------------------------------

def build_analysis_prompt(
    candidates_csv: str,
    fusion_data: list[dict[str, Any]],
    funnel: dict[str, Any],
    settings: dict[str, Any] | None = None,
) -> str:
    """Build a structured prompt for the Bedrock agent."""
    return textwrap.dedent(f"""\
    You are a computational structural biology expert reviewing protein binder
    design results from BindCraft + AlphaFold2.

    ## Context
    Target: Parvalbumin (PDB 1RK9) — a calcium-binding protein expressed in
    fast-spiking inhibitory interneurons, relevant to neuroscience research.

    Design settings (thresholds predeclared before data inspection):
    {json.dumps(settings or {}, indent=2)}

    ## Filtering Funnel
    {json.dumps(funnel, indent=2)}

    ## Top Ranked Candidates (CSV)
    ```
    {candidates_csv}
    ```

    ## Fluorescent Fusion Compatibility Analysis
    {json.dumps(fusion_data, indent=2)}

    ## Instructions
    Provide a detailed scientific analysis covering:

    1. **Panel Quality Assessment** — Are the iPTM/pLDDT/pAE distributions
       consistent with successful binder design? How does the survival rate
       compare to published BindCraft benchmarks (~5-15% at iPTM≥0.7)?

    2. **Structural Interpretation** — What do the confidence metrics tell us
       about likely binding mode? Which candidates show the strongest evidence
       of a well-defined interface?

    3. **Fusion Compatibility Review** — For each candidate, assess the
       terminus distances. Which terminus is safest for mNeonGreen fusion?
       Are any candidates problematic?

    4. **Diversity & Redundancy** — Comment on sequence/structural diversity
       among the top candidates. Is the panel diverse enough for experimental
       testing?

    5. **Experimental Recommendations** — Rank the top 3 candidates for
       wet-lab validation. Suggest expression system, purification strategy,
       and binding assay (BLI/SPR/pull-down). Estimate expected Kd range.

    6. **Limitations & Caveats** — What are the key uncertainties?
       iPTM > 0.7 does NOT guarantee binding. What experimental controls
       are essential?

    Format as markdown with clear headers.
    """)


def run_agent_analysis(
    ranked_df_path: Path,
    fusion_path: Path,
    funnel_path: Path,
    settings_path: Path | None = None,
    output_path: Path | None = None,
) -> str:
    """Run the Bedrock agent and return the analysis markdown."""
    import pandas as pd

    if output_path is None:
        output_path = Path("/results/agent_analysis.md")

    # Load data
    df = pd.read_csv(ranked_df_path)
    candidates_csv = df.to_csv(index=False)

    with open(fusion_path) as f:
        fusion_data = json.load(f)
    with open(funnel_path) as f:
        funnel = json.load(f)
    settings = None
    if settings_path and settings_path.exists():
        with open(settings_path) as f:
            settings = json.load(f)

    prompt = build_analysis_prompt(candidates_csv, fusion_data, funnel, settings)

    # Try Bedrock first; fall back to local analysis
    analysis_md = ""
    bedrock_used = False
    try:
        print("  Invoking Bedrock agent for scientific analysis ...")
        analysis_md = invoke_bedrock(prompt)
        bedrock_used = True
        print("  Bedrock agent analysis received successfully.")
    except Exception as e:
        print(f"  Bedrock unavailable ({e}). Generating local deterministic analysis.")
        analysis_md = _generate_local_analysis(df, fusion_data, funnel)

    # Wrap with header
    header = (
        "# BindCrafting — Agentic Scientific Analysis\n\n"
        f"**Analysis engine:** {'AWS Bedrock (Claude)' if bedrock_used else 'Local deterministic fallback'}\n\n"
        "---\n\n"
    )
    full_md = header + analysis_md

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(full_md)
    print(f"  Agent analysis written → {output_path}")
    return full_md


def _generate_local_analysis(
    df: "pd.DataFrame",
    fusion_data: list[dict],
    funnel: dict,
) -> str:
    """Deterministic local analysis when Bedrock is unavailable."""
    total = funnel.get("total_trajectories", 0)
    surviving = funnel.get("surviving_filters", 0)
    top_n = funnel.get("top_ranked", 0)
    survival_pct = (surviving / total * 100) if total > 0 else 0

    best = df.iloc[0] if len(df) > 0 else None
    safe_count = sum(1 for f in fusion_data if f.get("fusion_safe", False))

    lines = [
        "## 1. Panel Quality Assessment\n",
        f"From {total} BindCraft design trajectories, {surviving} ({survival_pct:.1f}%) "
        f"survived predeclared hard filters (iPTM≥0.7, pLDDT≥80, pAE≤10, length≤120). "
        "Published BindCraft benchmarks report 5-15% survival at comparable thresholds, ",
    ]
    if survival_pct > 15:
        lines.append("so this yield is above average — possibly because the target has a "
                      "well-defined binding pocket.\n\n")
    elif survival_pct > 5:
        lines.append("so this yield is within the expected range for a standard target.\n\n")
    else:
        lines.append("so this yield is below typical. The target may present a challenging "
                      "binding surface (flat, charged, or flexible).\n\n")

    lines.append("## 2. Structural Interpretation\n\n")
    if best is not None:
        lines.append(
            f"The top candidate ({best.get('design_name', 'N/A')}) achieves "
            f"iPTM={best.get('iptm', 0):.3f} and pLDDT={best.get('plddt', 0):.1f}, "
            f"with pAE={best.get('pae', 0):.1f}Å. "
            "An iPTM above 0.7 indicates that AlphaFold2 is confident the binder-target "
            "complex adopts a well-defined interface geometry. The pLDDT above 80 confirms "
            "the binder's fold is well-predicted.\n\n"
        )

    lines.append("## 3. Fusion Compatibility Review\n\n")
    for fd in fusion_data:
        name = fd.get("design", "unknown")
        n_dist = fd.get("n_term_distance_to_interface", 0)
        c_dist = fd.get("c_term_distance_to_interface", 0)
        rec = fd.get("recommended_terminus", "unknown")
        safe = fd.get("fusion_safe", False)
        lines.append(
            f"- **{name}**: N-term={n_dist:.1f}Å, C-term={c_dist:.1f}Å → "
            f"Recommended: {rec}-terminal fusion ({'✅ safe' if safe else '⚠️ risk'})\n"
        )
    lines.append(f"\n{safe_count}/{len(fusion_data)} candidates have a safe fusion terminus.\n\n")

    lines.append("## 4. Diversity & Redundancy\n\n")
    if len(df) > 0 and "sequence" in df.columns:
        avg_len = df["length"].mean() if "length" in df.columns else 0
        lines.append(
            f"The top {len(df)} candidates have an average length of {avg_len:.0f} residues. "
            "Sequence diversity should be assessed via clustering at 50% identity using MMseqs2 "
            "before experimental testing to ensure the panel explores multiple binding modes.\n\n"
        )

    lines.append("## 5. Experimental Recommendations\n\n")
    lines.append(
        "1. Express top 3 candidates as His-tagged constructs in *E. coli* BL21(DE3)\n"
        "2. Purify via Ni-NTA affinity chromatography + size exclusion\n"
        "3. Validate binding via BLI (BioLayer Interferometry) with immobilized Parvalbumin\n"
        "4. Expected Kd range: 10-500 nM (based on iPTM 0.7-0.85 benchmarks)\n"
        "5. For fusion validation: clone mNeonGreen onto recommended terminus with GGGGS×3 linker\n\n"
    )

    lines.append("## 6. Limitations & Caveats\n\n")
    lines.append(
        "- **iPTM is a proxy, not a guarantee**: ~30% of designs with iPTM>0.8 bind in vitro\n"
        "- **Synthetic data**: This analysis uses computationally generated data, not real BindCraft outputs\n"
        "- **No experimental validation**: All metrics are predicted; binding must be confirmed experimentally\n"
        "- **Fusion distance is geometric**: Actual steric effects depend on linker dynamics and FP folding\n"
        "- **No sequence clustering**: True diversity requires MMseqs2 clustering at 50% identity\n"
    )

    return "".join(lines)


if __name__ == "__main__":
    # Standalone test
    run_agent_analysis(
        ranked_df_path=Path("/results/ranked_candidates.csv"),
        fusion_path=Path("/results/fusion_compatibility.json"),
        funnel_path=Path("/results/filtering_funnel.json"),
        settings_path=Path("/results/synthetic_data/settings.json"),
    )
