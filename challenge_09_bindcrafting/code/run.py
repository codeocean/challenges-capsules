#!/usr/bin/env python3
"""Challenge 09: BindCrafting — Main Orchestrator.

Executes the complete protein binder analysis pipeline:
  1. Generate synthetic BindCraft design data (scores + PDBs)
  2. Load and filter candidates on predeclared AF2 thresholds
  3. Rank survivors by iPTM
  4. Check fluorescent fusion compatibility (terminus-distance geometry)
  5. Invoke AWS Bedrock agent for scientific interpretation
  6. Generate visualizations
  7. Write mandatory protocol artifacts

All LLM calls go through AWS Bedrock (boto3 + bedrock-runtime).
No openai or anthropic Python packages are used.
"""

from __future__ import annotations

import json
import sys
import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd

# Local modules
from generate_data import main as generate_synthetic_data
from bedrock_agent import run_agent_analysis
from visualize import score_scatter, fusion_distance_chart, filtering_funnel

# ---------------------------------------------------------------------------
# Configuration — predeclared thresholds (set BEFORE seeing data)
# ---------------------------------------------------------------------------

IPTM_MIN = 0.7
PLDDT_MIN = 80.0
PAE_MAX = 10.0
MAX_LENGTH = 120
FUSION_DISTANCE_THRESHOLD = 15.0  # Angstroms
TOP_N = 5

RESULTS_DIR = Path("/results")


# ---------------------------------------------------------------------------
# PDB parsing (BioPython)
# ---------------------------------------------------------------------------

def get_terminus_distances(pdb_path: Path) -> dict:
    """Compute N-term and C-term CA distances to nearest interface residue."""
    try:
        from Bio.PDB import PDBParser
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure("complex", str(pdb_path))
        model = structure[0]

        chains = list(model.get_chains())
        if len(chains) < 2:
            return {"n_term_distance": 0.0, "c_term_distance": 0.0, "error": "single chain"}

        binder_chain = chains[-1]
        target_chains = chains[:-1]
        binder_residues = list(binder_chain.get_residues())
        if not binder_residues:
            return {"n_term_distance": 0.0, "c_term_distance": 0.0, "error": "no residues"}

        # Get N-term and C-term CA positions
        n_term_ca, c_term_ca = None, None
        for atom in binder_residues[0]:
            if atom.get_name() == "CA":
                n_term_ca = atom.get_vector().get_array()
        for atom in binder_residues[-1]:
            if atom.get_name() == "CA":
                c_term_ca = atom.get_vector().get_array()

        if n_term_ca is None or c_term_ca is None:
            return {"n_term_distance": 0.0, "c_term_distance": 0.0, "error": "no CA atoms"}

        # Collect all target atom coordinates
        target_coords = np.array([
            atom.get_vector().get_array()
            for chain in target_chains
            for atom in chain.get_atoms()
        ])

        # Find interface: binder residues within 8Å of any target atom
        interface_cas = []
        for res in binder_residues:
            for atom in res:
                if atom.get_name() == "CA":
                    ca = atom.get_vector().get_array()
                    dists = np.linalg.norm(target_coords - ca, axis=1)
                    if dists.min() < 8.0:
                        interface_cas.append(ca)

        if not interface_cas:
            return {"n_term_distance": 999.0, "c_term_distance": 999.0,
                    "note": "no interface residues found"}

        interface_coords = np.array(interface_cas)
        n_dist = float(np.linalg.norm(interface_coords - n_term_ca, axis=1).min())
        c_dist = float(np.linalg.norm(interface_coords - c_term_ca, axis=1).min())

        return {
            "n_term_distance": round(n_dist, 2),
            "c_term_distance": round(c_dist, 2),
        }
    except Exception as e:
        return {"n_term_distance": 0.0, "c_term_distance": 0.0, "error": str(e)}


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------

def stage_generate(data_dir: Path) -> Path:
    """Stage 1: Generate synthetic BindCraft data."""
    print("\n" + "=" * 60)
    print("STAGE 1: Generating synthetic BindCraft design data")
    print("=" * 60)
    return generate_synthetic_data(data_dir)


def stage_filter(scores_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Stage 2: Load scores and apply predeclared hard filters."""
    print("\n" + "=" * 60)
    print("STAGE 2: Filtering candidates on predeclared thresholds")
    print("=" * 60)

    df = pd.read_csv(scores_path)
    initial_count = len(df)
    print(f"  Loaded {initial_count} design trajectories.")

    # Normalize columns
    col_map = {}
    for col in df.columns:
        low = col.lower().replace(" ", "_")
        if "iptm" in low:
            col_map[col] = "iptm"
        elif "plddt" in low:
            col_map[col] = "plddt"
        elif "pae" in low:
            col_map[col] = "pae"
        elif "length" in low or "len" in low:
            col_map[col] = "length"
        elif "name" in low or "design" in low:
            col_map[col] = "design_name"
        elif "seq" in low:
            col_map[col] = "sequence"
    df = df.rename(columns=col_map)

    # Apply filters
    filtered = df.copy()
    if "iptm" in filtered.columns:
        filtered = filtered[filtered["iptm"] >= IPTM_MIN]
        print(f"  iPTM ≥ {IPTM_MIN}: {len(filtered)} remain")
    if "plddt" in filtered.columns:
        filtered = filtered[filtered["plddt"] >= PLDDT_MIN]
        print(f"  pLDDT ≥ {PLDDT_MIN}: {len(filtered)} remain")
    if "pae" in filtered.columns:
        filtered = filtered[filtered["pae"] <= PAE_MAX]
        print(f"  pAE ≤ {PAE_MAX}: {len(filtered)} remain")
    if "length" in filtered.columns:
        filtered = filtered[filtered["length"] <= MAX_LENGTH]
        print(f"  Length ≤ {MAX_LENGTH}: {len(filtered)} remain")

    surviving_count = len(filtered)
    print(f"  Survival rate: {surviving_count}/{initial_count} "
          f"({surviving_count / initial_count * 100:.1f}%)")

    funnel = {
        "total_trajectories": initial_count,
        "surviving_filters": surviving_count,
        "top_ranked": 0,  # updated later
    }

    return df, filtered, funnel


def stage_rank(filtered: pd.DataFrame, funnel: dict) -> pd.DataFrame:
    """Stage 3: Rank survivors by iPTM, select top N."""
    print("\n" + "=" * 60)
    print("STAGE 3: Ranking candidates by iPTM")
    print("=" * 60)

    if len(filtered) == 0:
        print("  WARNING: No candidates survive filters.")
        funnel["top_ranked"] = 0
        return pd.DataFrame()

    ranked = filtered.sort_values("iptm", ascending=False).head(TOP_N).copy()
    ranked["rank"] = range(1, len(ranked) + 1)
    funnel["top_ranked"] = len(ranked)

    print(f"  Top {len(ranked)} candidates selected:")
    for _, row in ranked.iterrows():
        name = row.get("design_name", f"rank_{row['rank']}")
        print(f"    #{row['rank']} {name}: iPTM={row['iptm']:.3f} "
              f"pLDDT={row['plddt']:.1f} pAE={row['pae']:.1f}")

    return ranked


def stage_fusion(ranked: pd.DataFrame, designs_dir: Path) -> list[dict]:
    """Stage 4: Check fluorescent fusion compatibility."""
    print("\n" + "=" * 60)
    print("STAGE 4: Checking fluorescent fusion compatibility")
    print("=" * 60)

    fusion_results = []
    for _, row in ranked.iterrows():
        design_name = row.get("design_name", f"design_{row['rank']}")
        pdb_path = designs_dir / f"{design_name}.pdb"

        if pdb_path.exists():
            distances = get_terminus_distances(pdb_path)
        else:
            distances = {"n_term_distance": 999.0, "c_term_distance": 999.0,
                         "note": "PDB not found"}

        n_dist = distances.get("n_term_distance", 0)
        c_dist = distances.get("c_term_distance", 0)

        # Handle errors: 0.0 from a parse error is different from 0.0 meaning "at interface"
        has_error = "error" in distances
        if has_error:
            recommended = "unknown"
            fusion_safe = False
        elif n_dist > c_dist and n_dist > FUSION_DISTANCE_THRESHOLD:
            recommended = "N"
            fusion_safe = True
        elif c_dist > FUSION_DISTANCE_THRESHOLD:
            recommended = "C"
            fusion_safe = True
        elif n_dist > FUSION_DISTANCE_THRESHOLD:
            recommended = "N"
            fusion_safe = True
        else:
            recommended = "neither"
            fusion_safe = False

        result = {
            "design": design_name,
            "n_term_distance_to_interface": round(n_dist, 2),
            "c_term_distance_to_interface": round(c_dist, 2),
            "recommended_terminus": recommended,
            "fusion_safe": fusion_safe,
        }
        fusion_results.append(result)
        status = "✅ safe" if fusion_safe else "⚠ RISK"
        print(f"  {design_name}: N={n_dist:.1f}Å  C={c_dist:.1f}Å → {recommended} ({status})")

    return fusion_results


def stage_agent(
    ranked_path: Path,
    fusion_path: Path,
    funnel_path: Path,
    settings_path: Path | None,
) -> str:
    """Stage 5: Invoke Bedrock agent for scientific interpretation."""
    print("\n" + "=" * 60)
    print("STAGE 5: Bedrock agentic scientific analysis")
    print("=" * 60)
    return run_agent_analysis(ranked_path, fusion_path, funnel_path, settings_path)


def stage_visualize(
    ranked: pd.DataFrame,
    all_df: pd.DataFrame,
    fusion_results: list[dict],
    funnel: dict,
) -> None:
    """Stage 6: Generate all visualizations."""
    print("\n" + "=" * 60)
    print("STAGE 6: Generating visualizations")
    print("=" * 60)

    viz_dir = RESULTS_DIR / "top5_visualizations"
    viz_dir.mkdir(parents=True, exist_ok=True)

    score_scatter(ranked, all_df, viz_dir / "score_scatter.png", IPTM_MIN, PLDDT_MIN)
    fusion_distance_chart(fusion_results, viz_dir / "fusion_distance.png", FUSION_DISTANCE_THRESHOLD)
    filtering_funnel(funnel, viz_dir / "filtering_funnel.png")


def stage_write_artifacts(
    ranked: pd.DataFrame,
    fusion_results: list[dict],
    funnel: dict,
    agent_analysis: str,
    data_dir: Path,
) -> None:
    """Stage 7: Write all mandatory protocol artifacts."""
    print("\n" + "=" * 60)
    print("STAGE 7: Writing output artifacts")
    print("=" * 60)

    # 1. Ranked candidates CSV
    ranked_path = RESULTS_DIR / "ranked_candidates.csv"
    ranked.to_csv(ranked_path, index=False)
    print(f"  ✓ {ranked_path}")

    # 2. Fusion compatibility JSON
    fusion_path = RESULTS_DIR / "fusion_compatibility.json"
    with open(fusion_path, "w") as f:
        json.dump(fusion_results, f, indent=2)
    print(f"  ✓ {fusion_path}")

    # 3. Filtering funnel JSON
    funnel_path = RESULTS_DIR / "filtering_funnel.json"
    with open(funnel_path, "w") as f:
        json.dump(funnel, f, indent=2)
    print(f"  ✓ {funnel_path}")

    # 4. Manifest JSON (mandatory)
    manifest = {
        "capsule_number": 9,
        "capsule_objective": "BindCrafting — Protein binder analysis with Bedrock agentic interpretation",
        "created_files": [
            "results/ranked_candidates.csv",
            "results/fusion_compatibility.json",
            "results/filtering_funnel.json",
            "results/agent_analysis.md",
            "results/top5_visualizations/score_scatter.png",
            "results/top5_visualizations/fusion_distance.png",
            "results/top5_visualizations/filtering_funnel.png",
            "results/manifest.json",
            "results/IMPLEMENTATION_SUMMARY.md",
            "results/VALIDATION_NOTES.md",
            "results/synthetic_data/design_results/design_scores.csv",
            "results/synthetic_data/design_results/*.pdb",
            "results/synthetic_data/target/target.pdb",
            "results/synthetic_data/settings.json",
        ],
        "main_entrypoints": ["/code/run", "/code/run.py"],
        "commands_run": [
            "python /code/run.py",
        ],
        "outputs_produced": {
            "ranked_candidates.csv": f"{len(ranked)} top-ranked binder candidates",
            "fusion_compatibility.json": "Per-candidate terminus distances and fusion safety",
            "filtering_funnel.json": f"Funnel: {funnel['total_trajectories']} → {funnel['surviving_filters']} → {funnel['top_ranked']}",
            "agent_analysis.md": "Bedrock-generated scientific interpretation",
            "top5_visualizations/": "Score scatter, fusion distance chart, filtering funnel",
        },
        "dependencies": {
            "python_packages": ["numpy", "pandas", "matplotlib", "biopython", "boto3"],
            "aws_services": ["bedrock-runtime (Claude via Bedrock)"],
        },
        "known_limitations": [
            "Uses synthetic data — no real BindCraft outputs attached",
            "Bedrock agent may fall back to local analysis if IAM credentials unavailable",
            "PDB files are minimal CA-only representations, not full-atom models",
            "No MMseqs2 sequence clustering (would require additional binary)",
        ],
        "unresolved_issues": [],
    }
    manifest_path = RESULTS_DIR / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  ✓ {manifest_path}")

    # 5. IMPLEMENTATION_SUMMARY.md (mandatory)
    summary = f"""# Implementation Summary — Challenge 09: BindCrafting

## What Was Implemented

A complete protein binder analysis pipeline with AWS Bedrock agentic interpretation:

1. **Synthetic Data Generation** (`generate_data.py`): Creates 200 realistic BindCraft
   design trajectories with iPTM/pLDDT/pAE distributions matching published benchmarks,
   plus minimal PDB files for structural analysis.

2. **Filtering & Ranking** (`run.py`): Applies predeclared hard thresholds
   (iPTM≥{IPTM_MIN}, pLDDT≥{PLDDT_MIN}, pAE≤{PAE_MAX}, length≤{MAX_LENGTH}),
   ranks survivors by iPTM, selects top {TOP_N}.

3. **Fusion Compatibility** (`run.py`): For each top candidate, uses BioPython PDB
   parser to compute N-term and C-term CA distances to the nearest interface residue
   (defined as binder residues within 8Å of target atoms). Terminus is fusion-safe
   if distance > {FUSION_DISTANCE_THRESHOLD}Å.

4. **Bedrock Agentic Analysis** (`bedrock_agent.py`): Invokes Claude via AWS Bedrock
   (`boto3` + `bedrock-runtime`) — NOT the `anthropic` or `openai` packages. The agent
   receives all candidate data and generates scientific interpretation with structural
   insights, fusion recommendations, and experimental next-steps.

5. **Visualizations** (`visualize.py`): Score scatter (iPTM vs pLDDT), fusion distance
   bar chart, and filtering funnel.

## Files Created

| File | Purpose |
|------|---------|
| `run.py` | Main orchestrator (7 pipeline stages) |
| `generate_data.py` | Synthetic BindCraft data generator |
| `bedrock_agent.py` | AWS Bedrock agent for scientific interpretation |
| `visualize.py` | Matplotlib visualization helpers |

## Execution

```bash
/code/run  # Bash entrypoint → python /code/run.py
```

## Key Design Decisions

- **Bedrock-only LLM access**: All LLM calls use `boto3.client('bedrock-runtime')`
  with model fallback chain. No direct Anthropic/OpenAI API usage.
- **Predeclared thresholds**: Filter values are set in code constants BEFORE data
  generation, preventing post-hoc cherry-picking.
- **Graceful degradation**: If Bedrock is unreachable, a deterministic local analysis
  module generates the scientific report.
- **Deterministic data**: All random generation uses `numpy.random.Generator` with
  fixed seed (42) for reproducibility.

## Filtering Results

- Total trajectories: {funnel['total_trajectories']}
- Surviving filters: {funnel['surviving_filters']}
- Top ranked: {funnel['top_ranked']}
"""
    summary_path = RESULTS_DIR / "IMPLEMENTATION_SUMMARY.md"
    summary_path.write_text(summary)
    print(f"  ✓ {summary_path}")

    # 6. VALIDATION_NOTES.md (mandatory)
    safe_count = sum(1 for f in fusion_results if f.get("fusion_safe", False))
    validation = f"""# Validation Notes — Challenge 09: BindCrafting

## What Is Complete

- ✅ Synthetic data generation (200 trajectories + PDBs + target PDB)
- ✅ Hard filtering with predeclared thresholds
- ✅ iPTM-based ranking with top-{TOP_N} selection
- ✅ Fusion compatibility analysis via BioPython PDB terminus-distance calculation
- ✅ AWS Bedrock agent integration (with graceful fallback)
- ✅ Three visualization types (scatter, fusion bar, funnel)
- ✅ All mandatory artifacts (manifest, summary, validation notes)

## What Is Partial

- ⚠ Sequence diversity analysis: No MMseqs2 clustering (requires external binary).
  Diversity is discussed qualitatively in the agent analysis.
- ⚠ py3Dmol visualizations: Replaced with matplotlib charts. py3Dmol requires
  a notebook/HTML context that doesn't suit headless batch execution.

## Assumptions Made

1. Parvalbumin (PDB 1RK9) is used as the target — a neuroscience-relevant
   calcium-binding protein in inhibitory interneurons.
2. Synthetic data distributions (iPTM beta(2.5,4), pLDDT N(68,14)) approximate
   published BindCraft benchmarks.
3. Interface is defined as binder CA atoms within 8Å of any target atom.
4. Fusion safety threshold of {FUSION_DISTANCE_THRESHOLD}Å is based on literature
   (FP barrel diameter ~24Å, linker span ~15-20Å with GGGGS×3).
5. AWS Bedrock region defaults to us-east-1 (overridable via AWS_REGION env var).

## Limitations

- **Synthetic data only**: No real BindCraft design run was performed. Real outputs
  require GPU hours of computation and actual AF2 weights.
- **CA-only PDBs**: Generated structures contain only CA atoms, not full-atom models.
  This is sufficient for terminus-distance calculations but not for detailed
  interface analysis.
- **Bedrock availability**: The agentic analysis depends on AWS Bedrock credentials
  being configured in the Code Ocean environment. Falls back to deterministic local
  analysis if unavailable.
- **No AF2 re-scoring**: The plan calls for AF2 multimer re-scoring of top candidates
  with 12 recycles. This requires AF2 weights (~5.3GB) and GPU time, omitted here.

## Blockers / Uncertainties

- Bedrock credential configuration depends on deployment IAM setup
- Real BindCraft outputs would require pre-computation (2-12 hours GPU time)

## Fusion Compatibility Summary

- {safe_count}/{len(fusion_results)} candidates have at least one safe fusion terminus
"""
    validation_path = RESULTS_DIR / "VALIDATION_NOTES.md"
    validation_path.write_text(validation)
    print(f"  ✓ {validation_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Execute the full BindCrafting pipeline."""
    print("=" * 60)
    print("  Challenge 09: BindCrafting — Full Pipeline")
    print(f"  Started: {datetime.datetime.now().isoformat()}")
    print("=" * 60)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Stage 1: Generate synthetic data
    data_dir = stage_generate(RESULTS_DIR / "synthetic_data")
    scores_path = data_dir / "design_results" / "design_scores.csv"
    designs_dir = data_dir / "design_results"
    settings_path = data_dir / "settings.json"

    # Stage 2: Filter
    all_df, filtered, funnel = stage_filter(scores_path)

    # Stage 3: Rank
    ranked = stage_rank(filtered, funnel)

    if len(ranked) == 0:
        print("\nERROR: No candidates survive filtering. Exiting.")
        # Still write minimal artifacts
        stage_write_artifacts(ranked, [], funnel, "", data_dir)
        sys.exit(1)

    # Stage 4: Fusion compatibility
    fusion_results = stage_fusion(ranked, designs_dir)

    # Add fusion info to ranked table
    ranked["fusion_safe_terminus"] = [r["recommended_terminus"] for r in fusion_results]

    # Write intermediate outputs needed by agent
    ranked_path = RESULTS_DIR / "ranked_candidates.csv"
    ranked.to_csv(ranked_path, index=False)
    fusion_path = RESULTS_DIR / "fusion_compatibility.json"
    with open(fusion_path, "w") as f:
        json.dump(fusion_results, f, indent=2)
    funnel_path = RESULTS_DIR / "filtering_funnel.json"
    with open(funnel_path, "w") as f:
        json.dump(funnel, f, indent=2)

    # Stage 5: Bedrock agentic analysis
    agent_md = stage_agent(ranked_path, fusion_path, funnel_path, settings_path)

    # Stage 6: Visualizations
    stage_visualize(ranked, all_df, fusion_results, funnel)

    # Stage 7: Write all mandatory artifacts (overwrites intermediates with final versions)
    stage_write_artifacts(ranked, fusion_results, funnel, agent_md, data_dir)

    print("\n" + "=" * 60)
    print("  Pipeline complete!")
    safe_count = sum(1 for f in fusion_results if f.get("fusion_safe", False))
    print(f"  Funnel: {funnel['total_trajectories']} → "
          f"{funnel['surviving_filters']} → {funnel['top_ranked']} top candidates")
    print(f"  Fusion-safe: {safe_count}/{len(fusion_results)}")
    print(f"  Finished: {datetime.datetime.now().isoformat()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
