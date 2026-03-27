#!/usr/bin/env python3
"""Generate realistic synthetic BindCraft design data for Challenge 09.

Creates:
- design_scores.csv: 200 trajectories with iPTM, pLDDT, pAE, length, sequence
- Minimal PDB files for top candidates (multi-chain: target A + binder B)
- target.pdb: simplified target structure (Parvalbumin-like)

All outputs go to /results/synthetic_data/ which run.py then reads.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

AMINO_ACIDS = list("ACDEFGHIKLMNPQRSTVWY")
SEED = 42


def _random_sequence(rng: np.random.Generator, length: int) -> str:
    """Generate a random amino acid sequence."""
    return "".join(rng.choice(AMINO_ACIDS, size=length))


def _helix_coords(start: np.ndarray, n_residues: int, axis: np.ndarray) -> list[np.ndarray]:
    """Generate CA coordinates along a helix-like path."""
    coords = []
    rise = 1.5  # angstroms per residue along axis
    radius = 2.3
    axis_norm = axis / np.linalg.norm(axis)
    # build a local coordinate frame
    perp1 = np.cross(axis_norm, [1, 0, 0])
    if np.linalg.norm(perp1) < 0.01:
        perp1 = np.cross(axis_norm, [0, 1, 0])
    perp1 = perp1 / np.linalg.norm(perp1)
    perp2 = np.cross(axis_norm, perp1)

    for i in range(n_residues):
        angle = i * 100.0 * math.pi / 180.0  # ~100 degrees per residue
        pos = (
            start
            + axis_norm * (i * rise)
            + perp1 * radius * math.cos(angle)
            + perp2 * radius * math.sin(angle)
        )
        coords.append(pos)
    return coords


def _write_pdb(
    path: Path,
    target_coords: list[np.ndarray],
    binder_coords: list[np.ndarray],
    target_seq: str,
    binder_seq: str,
) -> None:
    """Write a minimal two-chain PDB file."""
    three_letter = {
        "A": "ALA", "C": "CYS", "D": "ASP", "E": "GLU", "F": "PHE",
        "G": "GLY", "H": "HIS", "I": "ILE", "K": "LYS", "L": "LEU",
        "M": "MET", "N": "ASN", "P": "PRO", "Q": "GLN", "R": "ARG",
        "S": "SER", "T": "THR", "V": "VAL", "W": "TRP", "Y": "TYR",
    }
    lines = []
    atom_num = 1

    # Chain A — target
    for i, (coord, aa) in enumerate(zip(target_coords, target_seq)):
        res_name = three_letter.get(aa, "ALA")
        res_num = i + 1
        x, y, z = coord
        lines.append(
            f"ATOM  {atom_num:5d}  CA  {res_name} A{res_num:4d}    "
            f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00 80.00           C  "
        )
        atom_num += 1
    lines.append("TER")

    # Chain B — binder
    for i, (coord, aa) in enumerate(zip(binder_coords, binder_seq)):
        res_name = three_letter.get(aa, "ALA")
        res_num = i + 1
        x, y, z = coord
        lines.append(
            f"ATOM  {atom_num:5d}  CA  {res_name} B{res_num:4d}    "
            f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00 85.00           C  "
        )
        atom_num += 1
    lines.append("TER")
    lines.append("END")

    path.write_text("\n".join(lines) + "\n")


def generate_scores(out_dir: Path, n_designs: int = 200) -> pd.DataFrame:
    """Generate a realistic design_scores.csv.

    Distributions are calibrated so ~10-12% of designs pass all four filters
    simultaneously (iPTM≥0.7, pLDDT≥80, pAE≤10, length≤120), matching
    published BindCraft benchmarks of 5-15% survival.
    """
    rng = np.random.default_rng(SEED)

    names = [f"binder_{i:04d}" for i in range(n_designs)]
    lengths = rng.integers(55, 130, size=n_designs)
    sequences = [_random_sequence(rng, int(l)) for l in lengths]

    # --- Correlated metric generation ---
    # Base quality factor per design (latent variable driving correlation)
    quality = rng.beta(2.0, 3.0, size=n_designs)  # 0-1, right-skewed

    # iPTM: shifted/scaled so ~15-20% exceed 0.7
    iptm = 0.30 + quality * 0.65 + rng.normal(0, 0.04, size=n_designs)
    iptm = iptm.clip(0.25, 0.95)

    # pLDDT: correlated with quality, shifted so ~25-30% exceed 80
    plddt = 55 + quality * 40 + rng.normal(0, 5, size=n_designs)
    plddt = plddt.clip(35, 98)

    # pAE: inversely correlated with quality, shifted so ~40% are ≤10
    pae = 20 - quality * 18 + rng.normal(0, 3, size=n_designs)
    pae = pae.clip(2, 30)

    df = pd.DataFrame({
        "design_name": names,
        "sequence": sequences,
        "length": lengths,
        "iptm": np.round(iptm, 4),
        "plddt": np.round(plddt, 2),
        "pae": np.round(pae, 2),
    })

    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "design_scores.csv"
    df.to_csv(csv_path, index=False)
    print(f"  Generated {n_designs} design scores → {csv_path}")
    return df


def generate_pdbs(
    out_dir: Path,
    df: pd.DataFrame,
    target_residues: int = 110,
) -> None:
    """Generate PDB files for candidates that pass filters + the target."""
    rng = np.random.default_rng(SEED + 1)

    # Filter to candidates likely to survive (pre-generate PDBs for top ~25)
    candidates = df.nlargest(25, "iptm")

    # Target structure: helix along z-axis centred at origin
    target_seq = _random_sequence(rng, target_residues)
    target_coords = _helix_coords(
        start=np.array([0.0, 0.0, 0.0]),
        n_residues=target_residues,
        axis=np.array([0.0, 0.0, 1.0]),
    )

    # Write target PDB (chain A only)
    target_dir = out_dir / "target"
    target_dir.mkdir(parents=True, exist_ok=True)
    _write_target_pdb(target_dir / "target.pdb", target_coords, target_seq)

    # Interface zone: residues 40-60 of the target (z ~ 60-90 Å)
    interface_center = target_coords[50]

    designs_dir = out_dir / "design_results"
    designs_dir.mkdir(parents=True, exist_ok=True)

    for idx, (_, row) in enumerate(candidates.iterrows()):
        binder_len = int(row["length"])
        binder_seq = row["sequence"][:binder_len]

        # Position binder so interface residues are near target,
        # but termini at varied, realistic distances (8-30 Å).
        # Alternate between N-close/C-far and N-far/C-close patterns.
        if idx % 3 == 0:
            # N-term close to interface (~8-12Å), C-term far (~18-30Å)
            n_offset = rng.uniform(3, 8)
            c_offset = rng.uniform(15, 28)
        elif idx % 3 == 1:
            # N-term far, C-term close
            n_offset = rng.uniform(15, 28)
            c_offset = rng.uniform(3, 8)
        else:
            # Both moderate
            n_offset = rng.uniform(10, 20)
            c_offset = rng.uniform(10, 20)

        # Start binder along a direction away from target, with N-term offset
        binder_axis = np.array([1.0, 0.3, 0.1])
        binder_axis = binder_axis / np.linalg.norm(binder_axis)
        binder_start = interface_center + np.array([n_offset, 4.0, -5.0])
        binder_coords = _helix_coords(
            start=binder_start,
            n_residues=binder_len,
            axis=binder_axis,
        )

        # Pull middle ~20 residues toward interface (make them within 8Å)
        mid = binder_len // 2
        for j in range(max(0, mid - 10), min(binder_len, mid + 10)):
            direction = interface_center - binder_coords[j]
            dist = np.linalg.norm(direction)
            if dist > 5:
                binder_coords[j] += direction / dist * (dist - 4.5)

        # Adjust C-term position to achieve target offset
        if binder_len > 5:
            c_direction = binder_coords[-1] - interface_center
            c_dist_current = np.linalg.norm(c_direction)
            if c_dist_current > 1.0:
                target_c_pos = interface_center + c_direction / c_dist_current * c_offset
                binder_coords[-1] = target_c_pos
                # Smooth last few residues toward adjusted C-term
                n_smooth = min(5, binder_len - 1)
                for k in range(binder_len - n_smooth - 1, binder_len - 1):
                    alpha = (k - (binder_len - n_smooth - 2)) / (n_smooth + 1)
                    alpha = max(0.0, min(1.0, alpha))
                    binder_coords[k] = (
                        (1 - alpha) * binder_coords[k] + alpha * target_c_pos
                    )

        pdb_path = designs_dir / f"{row['design_name']}.pdb"
        _write_pdb(pdb_path, target_coords, binder_coords, target_seq, binder_seq)

    print(f"  Generated {len(candidates)} candidate PDBs → {designs_dir}")


def _write_target_pdb(path: Path, coords: list[np.ndarray], seq: str) -> None:
    """Write a single-chain target PDB (plus a second dummy chain for structure)."""
    three_letter = {
        "A": "ALA", "C": "CYS", "D": "ASP", "E": "GLU", "F": "PHE",
        "G": "GLY", "H": "HIS", "I": "ILE", "K": "LYS", "L": "LEU",
        "M": "MET", "N": "ASN", "P": "PRO", "Q": "GLN", "R": "ARG",
        "S": "SER", "T": "THR", "V": "VAL", "W": "TRP", "Y": "TYR",
    }
    lines = []
    atom_num = 1
    for i, (coord, aa) in enumerate(zip(coords, seq)):
        res_name = three_letter.get(aa, "ALA")
        res_num = i + 1
        x, y, z = coord
        lines.append(
            f"ATOM  {atom_num:5d}  CA  {res_name} A{res_num:4d}    "
            f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00 85.00           C  "
        )
        atom_num += 1
    lines.append("TER")
    lines.append("END")
    path.write_text("\n".join(lines) + "\n")


def generate_settings(out_dir: Path) -> None:
    """Write a BindCraft settings.json for reproducibility."""
    settings = {
        "target_settings": {
            "pdb_id": "1RK9",
            "protein": "Parvalbumin (Rattus norvegicus)",
            "chain": "A",
            "hotspot_residues": "A:45,A:46,A:47,A:78,A:82",
            "notes": "Calcium-binding protein relevant to inhibitory neurons",
        },
        "binder_settings": {
            "length_range": [55, 120],
            "starting_mode": "poly_glycine",
        },
        "design_settings": {
            "num_designs": 200,
            "max_iterations": 200,
            "learning_rate": 0.1,
        },
        "alphafold_settings": {
            "model_names": ["model_1_multimer_v3"],
            "num_recycles": 3,
        },
        "filtering_settings": {
            "min_iptm": 0.7,
            "min_plddt": 80,
            "max_pae": 10,
            "max_length": 120,
        },
    }
    path = out_dir / "settings.json"
    path.write_text(json.dumps(settings, indent=2) + "\n")
    print(f"  Generated settings → {path}")


def main(out_dir: Path | None = None) -> Path:
    """Generate all synthetic data. Returns the output directory."""
    if out_dir is None:
        out_dir = Path("/results/synthetic_data")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Generating synthetic BindCraft data ...")
    df = generate_scores(out_dir / "design_results", n_designs=200)
    generate_pdbs(out_dir, df)
    generate_settings(out_dir)

    # Summary
    passing = df[
        (df["iptm"] >= 0.7) & (df["plddt"] >= 80) & (df["pae"] <= 10) & (df["length"] <= 120)
    ]
    print(f"  Designs passing all filters: {len(passing)}/{len(df)}")
    print("Data generation complete.")
    return out_dir


if __name__ == "__main__":
    main()
