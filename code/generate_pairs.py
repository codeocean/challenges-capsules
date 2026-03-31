#!/usr/bin/env python3
"""Synthetic light-sheet overlap pair generator (v3 — comprehensive).

Generates 200 pairs across multiple categories:
  - 80 aligned (with tissue variation)
  - 80 misaligned (6 perturbation types x 3 severity levels)
  - 20 edge cases (empty tiles, sparse tissue, tissue borders, stitching artifacts)
  - 20 borderline cases (very mild perturbations for the "needs_review" class)

Tracks perturbation_type, severity, and source in metadata.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Tuple

import numpy as np
from scipy.ndimage import gaussian_filter, rotate, shift
from scipy.ndimage import zoom as scipy_zoom
import tifffile

SEED = 42
IMG_SIZE = 256
OUTPUT_DIR = Path("/scratch/overlap_pairs")
META_PATH = Path("/scratch/metadata.csv")


# ---------------------------------------------------------------------------
# Tissue texture generators — varied appearance
# ---------------------------------------------------------------------------

def _make_base_texture(rng: np.random.Generator, size: int) -> np.ndarray:
    """Multi-scale filtered noise for general brain tissue."""
    base = rng.standard_normal((size, size))
    base = gaussian_filter(base, sigma=rng.uniform(8, 15))
    base = (base - base.min()) / (base.max() - base.min() + 1e-9)

    mid = rng.standard_normal((size, size))
    mid = gaussian_filter(mid, sigma=rng.uniform(2.5, 5.0))
    mid = (mid - mid.min()) / (mid.max() - mid.min() + 1e-9)

    fine = rng.standard_normal((size, size))
    fine = gaussian_filter(fine, sigma=rng.uniform(0.8, 2.0))
    fine = (fine - fine.min()) / (fine.max() - fine.min() + 1e-9)
    return base, mid, fine


def _add_cell_blobs(rng: np.random.Generator, size: int, n_range=(20, 100)) -> np.ndarray:
    """Scattered Gaussian cell-body blobs."""
    cells = np.zeros((size, size), dtype=np.float64)
    n_cells = rng.integers(*n_range)
    for _ in range(n_cells):
        cy, cx = rng.integers(6, size - 6, size=2)
        radius = rng.uniform(1.5, 6.0)
        brightness = rng.uniform(0.3, 1.0)
        yy, xx = np.ogrid[-cy:size - cy, -cx:size - cx]
        blob = np.exp(-(yy**2 + xx**2) / (2 * radius**2)) * brightness
        cells = np.maximum(cells, blob)
    return cells


def _add_vasculature(rng: np.random.Generator, size: int) -> np.ndarray:
    """Dark branching vessel-like structures."""
    vessels = np.ones((size, size), dtype=np.float64)
    n_vessels = rng.integers(2, 8)
    for _ in range(n_vessels):
        y = rng.integers(0, size)
        x = rng.integers(0, size)
        for _ in range(rng.integers(30, 100)):
            dy, dx = rng.integers(-2, 3, size=2)
            y = np.clip(y + dy, 0, size - 1)
            x = np.clip(x + dx, 0, size - 1)
            r = rng.integers(1, 3)
            yy, xx = np.ogrid[max(0, y-r):min(size, y+r+1), max(0, x-r):min(size, x+r+1)]
            vessels[yy, xx] *= 0.4
    vessels = gaussian_filter(vessels, sigma=1.0)
    return vessels


def make_dense_tissue(rng: np.random.Generator, size: int = IMG_SIZE) -> np.ndarray:
    """Dense tissue region (cortex-like) with many cells and vessels."""
    base, mid, fine = _make_base_texture(rng, size)
    cells = _add_cell_blobs(rng, size, (50, 120))
    vessels = _add_vasculature(rng, size)
    w = rng.dirichlet([3, 2, 1, 3])
    texture = (w[0]*base + w[1]*mid + w[2]*fine + w[3]*cells) * vessels
    texture = (texture - texture.min()) / (texture.max() - texture.min() + 1e-9)
    floor, ceiling = rng.uniform(400, 1500), rng.uniform(15000, 55000)
    return (texture * (ceiling - floor) + floor).astype(np.uint16)


def make_sparse_tissue(rng: np.random.Generator, size: int = IMG_SIZE) -> np.ndarray:
    """Sparse tissue (ventricle/white matter) — low signal, few cells."""
    base = rng.standard_normal((size, size))
    base = gaussian_filter(base, sigma=15)
    base = (base - base.min()) / (base.max() - base.min() + 1e-9) * 0.3
    cells = _add_cell_blobs(rng, size, (3, 12))
    texture = base + cells * 0.4
    texture = (texture - texture.min()) / (texture.max() - texture.min() + 1e-9)
    floor, ceiling = rng.uniform(100, 400), rng.uniform(2000, 6000)
    return (texture * (ceiling - floor) + floor).astype(np.uint16)


def make_tissue_border(rng: np.random.Generator, size: int = IMG_SIZE) -> np.ndarray:
    """Half-tissue, half-background — brain edge."""
    tissue = make_dense_tissue(rng, size).astype(np.float64)
    # Create a sigmoid boundary at a random position
    boundary_pos = rng.integers(size // 4, 3 * size // 4)
    angle = rng.uniform(-15, 15)
    x = np.arange(size)
    y = np.arange(size)
    xx, yy = np.meshgrid(x, y)
    # Rotated boundary
    rad = np.radians(angle)
    boundary_dist = (xx - boundary_pos) * np.cos(rad) + (yy - size//2) * np.sin(rad)
    mask = 1.0 / (1.0 + np.exp(-boundary_dist / 3.0))
    result = tissue * mask + rng.uniform(100, 300)  # background floor
    return np.clip(result, 0, 65535).astype(np.uint16)


def make_empty_tile(rng: np.random.Generator, size: int = IMG_SIZE) -> np.ndarray:
    """Nearly empty tile — just noise + faint background."""
    noise = rng.normal(200, 50, (size, size))
    return np.clip(noise, 0, 65535).astype(np.uint16)


# ---------------------------------------------------------------------------
# Perturbation functions
# ---------------------------------------------------------------------------

SEVERITY_PARAMS = {
    "translation": {"mild": (3, 7), "moderate": (8, 18), "severe": (18, 35), "borderline": (1, 3)},
    "rotation": {"mild": (0.5, 1.5), "moderate": (1.5, 4.0), "severe": (4.0, 8.0), "borderline": (0.15, 0.5)},
    "intensity_drift": {"mild": (0.08, 0.16), "moderate": (0.16, 0.32), "severe": (0.32, 0.55), "borderline": (0.03, 0.08)},
    "seam_artifact": {"mild": (0.06, 0.15), "moderate": (0.15, 0.30), "severe": (0.30, 0.50), "borderline": (0.02, 0.06)},
    "scale_mismatch": {"mild": (0.96, 0.985), "moderate": (0.93, 0.96), "severe": (0.87, 0.93), "borderline": (0.99, 0.995)},
    "blur": {"mild": (1.2, 2.5), "moderate": (2.5, 5.0), "severe": (5.0, 9.0), "borderline": (0.5, 1.2)},
    "affine_shear": {"mild": (0.01, 0.03), "moderate": (0.03, 0.06), "severe": (0.06, 0.12), "borderline": (0.005, 0.01)},
}


def apply_translation(img: np.ndarray, rng: np.random.Generator, severity: str) -> np.ndarray:
    lo, hi = SEVERITY_PARAMS["translation"][severity]
    dx = rng.uniform(lo, hi) * rng.choice([-1, 1])
    dy = rng.uniform(lo, hi) * rng.choice([-1, 1])
    return shift(img.astype(np.float64), (dy, dx), order=1, mode="reflect").astype(np.uint16)


def apply_rotation(img: np.ndarray, rng: np.random.Generator, severity: str) -> np.ndarray:
    lo, hi = SEVERITY_PARAMS["rotation"][severity]
    angle = rng.uniform(lo, hi) * rng.choice([-1, 1])
    rotated = rotate(img.astype(np.float64), angle, reshape=False, order=1, mode="reflect")
    return np.clip(rotated, 0, 65535).astype(np.uint16)


def apply_intensity_drift(img: np.ndarray, rng: np.random.Generator, severity: str) -> np.ndarray:
    lo, hi = SEVERITY_PARAMS["intensity_drift"][severity]
    strength = rng.uniform(lo, hi)
    h, w = img.shape
    gradient = np.linspace(1.0 - strength, 1.0 + strength, w)
    if rng.random() > 0.5:
        gradient = gradient[::-1]
    if rng.random() > 0.5:
        v_grad = np.linspace(1.0 - strength*0.4, 1.0 + strength*0.4, h)
        combined = gradient[np.newaxis, :] * v_grad[:, np.newaxis]
    else:
        combined = gradient[np.newaxis, :]
    return np.clip(img.astype(np.float64) * combined, 0, 65535).astype(np.uint16)


def apply_seam_artifact(img: np.ndarray, rng: np.random.Generator, severity: str) -> np.ndarray:
    lo, hi = SEVERITY_PARAMS["seam_artifact"][severity]
    strength = rng.uniform(lo, hi)
    result = img.astype(np.float64).copy()
    seam_col = rng.integers(img.shape[1]//4, 3*img.shape[1]//4)
    width = rng.integers(1, 5)
    result[:, seam_col:seam_col+width] *= max(0.01, 1.0 - strength*4)
    result[:, seam_col+width:] *= (1.0 + strength)
    return np.clip(result, 0, 65535).astype(np.uint16)


def apply_scale_mismatch(img: np.ndarray, rng: np.random.Generator, severity: str) -> np.ndarray:
    lo, hi = SEVERITY_PARAMS["scale_mismatch"][severity]
    scale = rng.uniform(lo, hi) if rng.random() > 0.5 else rng.uniform(2.0-hi, 2.0-lo)
    zoomed = scipy_zoom(img.astype(np.float64), scale, order=1)
    h, w = img.shape
    result = np.zeros_like(img, dtype=np.float64)
    ch, cw = min(h, zoomed.shape[0]), min(w, zoomed.shape[1])
    result[:ch, :cw] = zoomed[:ch, :cw]
    return np.clip(result, 0, 65535).astype(np.uint16)


def apply_blur(img: np.ndarray, rng: np.random.Generator, severity: str) -> np.ndarray:
    lo, hi = SEVERITY_PARAMS["blur"][severity]
    sigma = rng.uniform(lo, hi)
    return np.clip(gaussian_filter(img.astype(np.float64), sigma=sigma), 0, 65535).astype(np.uint16)


def apply_affine_shear(img: np.ndarray, rng: np.random.Generator, severity: str) -> np.ndarray:
    """Apply affine shear transform."""
    from scipy.ndimage import affine_transform
    lo, hi = SEVERITY_PARAMS["affine_shear"][severity]
    shear = rng.uniform(lo, hi) * rng.choice([-1, 1])
    # Shear matrix: [[1, shear], [0, 1]]
    matrix = np.array([[1, shear], [0, 1]])
    offset = np.array([0, -shear * img.shape[1] / 2])
    result = affine_transform(img.astype(np.float64), matrix, offset=offset, order=1, mode="reflect")
    return np.clip(result, 0, 65535).astype(np.uint16)


PERTURBATION_FUNCS = {
    "translation": apply_translation,
    "rotation": apply_rotation,
    "intensity_drift": apply_intensity_drift,
    "seam_artifact": apply_seam_artifact,
    "scale_mismatch": apply_scale_mismatch,
    "blur": apply_blur,
    "affine_shear": apply_affine_shear,
}


# ---------------------------------------------------------------------------
# Pair generators
# ---------------------------------------------------------------------------

def make_aligned_pair(rng: np.random.Generator, texture_fn=None) -> Tuple[np.ndarray, np.ndarray]:
    if texture_fn is None:
        texture_fn = make_dense_tissue
    base = texture_fn(rng)
    noise_scale = rng.uniform(30, 100)
    left = np.clip(base.astype(np.float64) + rng.normal(0, noise_scale, base.shape), 0, 65535).astype(np.uint16)
    # Add slight global intensity offset to simulate real acquisition variation
    intensity_offset = rng.normal(0, 150)
    right = np.clip(base.astype(np.float64) + rng.normal(0, noise_scale, base.shape) + intensity_offset, 0, 65535).astype(np.uint16)
    return left, right


def make_misaligned_pair(
    rng: np.random.Generator,
    perturbation_types: list[str] | None = None,
    severity: str = "moderate",
    texture_fn=None,
) -> Tuple[np.ndarray, np.ndarray]:
    left, right = make_aligned_pair(rng, texture_fn)
    if perturbation_types is None:
        n = rng.choice([1, 2, 3], p=[0.30, 0.45, 0.25])
        perturbation_types = list(rng.choice(list(PERTURBATION_FUNCS.keys()), size=n, replace=False))
    for pt in perturbation_types:
        right = PERTURBATION_FUNCS[pt](right, rng, severity)
    return left, right


# ---------------------------------------------------------------------------
# Full dataset generation
# ---------------------------------------------------------------------------

def generate_all_pairs() -> None:
    rng = np.random.default_rng(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    pair_idx = 0

    def save_pair(left, right, label, ptype, severity, source):
        nonlocal pair_idx
        pair_idx += 1
        pid = f"pair_{pair_idx:03d}"
        tifffile.imwrite(str(OUTPUT_DIR / f"{pid}_left.tif"), left)
        tifffile.imwrite(str(OUTPUT_DIR / f"{pid}_right.tif"), right)
        rows.append({
            "pair_id": pid, "label": label,
            "perturbation_type": ptype, "severity": severity, "source": source,
        })

    # --- 100 aligned pairs (varied tissue types) ---
    print("Generating 100 aligned pairs...")
    for i in range(100):
        if i < 65:
            fn = make_dense_tissue
            src = "dense_tissue"
        elif i < 82:
            fn = make_sparse_tissue
            src = "sparse_tissue"
        else:
            fn = make_tissue_border
            src = "tissue_border"
        left, right = make_aligned_pair(rng, fn)
        save_pair(left, right, "aligned", "none", "none", src)

    # --- 100 misaligned pairs (systematic perturbation coverage) ---
    print("Generating 100 misaligned pairs...")
    perturbation_names = list(PERTURBATION_FUNCS.keys())
    severities = ["mild", "moderate", "severe"]

    # 54 single-perturbation pairs (6 types x 3 severities x 3 repeats)
    for pt in perturbation_names:
        for sev in severities:
            for _ in range(3):
                fn = rng.choice([make_dense_tissue, make_sparse_tissue, make_tissue_border])
                left, right = make_misaligned_pair(rng, [pt], sev, fn)
                save_pair(left, right, "misaligned", pt, sev, "systematic")

    # 37 mixed-perturbation pairs
    for _ in range(37):
        n = rng.choice([2, 3])
        pts = list(rng.choice(perturbation_names, size=n, replace=False))
        sev = rng.choice(severities)
        fn = rng.choice([make_dense_tissue, make_sparse_tissue])
        left, right = make_misaligned_pair(rng, pts, sev, fn)
        save_pair(left, right, "misaligned", "+".join(pts), sev, "mixed")

    # --- 10 edge cases (aligned, but tricky) ---
    print("Generating 10 edge-case pairs...")
    # 3 sparse tissue
    for _ in range(3):
        left, right = make_aligned_pair(rng, make_sparse_tissue)
        save_pair(left, right, "aligned", "none", "none", "sparse_edge_case")
    # 4 tissue borders (but aligned)
    for _ in range(4):
        left, right = make_aligned_pair(rng, make_tissue_border)
        save_pair(left, right, "aligned", "none", "none", "tissue_border_edge")
    # 3 with extra noise (NOT misalignment)
    for _ in range(3):
        left, right = make_aligned_pair(rng, make_dense_tissue)
        extra_noise = rng.normal(0, 200, right.shape)
        right = np.clip(right.astype(np.float64) + extra_noise, 0, 65535).astype(np.uint16)
        save_pair(left, right, "aligned", "noise_only", "none", "hard_negative")

    # --- 30 borderline pairs (very subtle misalignment) ---
    print("Generating 30 borderline pairs...")
    for _ in range(30):
        pt = rng.choice(perturbation_names)
        fn = rng.choice([make_dense_tissue, make_sparse_tissue])
        left, right = make_misaligned_pair(rng, [pt], "borderline", fn)
        save_pair(left, right, "misaligned", pt, "borderline", "borderline")

    # Shuffle
    order = rng.permutation(len(rows))
    rows_shuffled = [rows[i] for i in order]

    with open(META_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["pair_id", "label", "perturbation_type", "severity", "source"])
        writer.writeheader()
        writer.writerows(rows_shuffled)

    n_aligned = sum(1 for r in rows if r["label"] == "aligned")
    n_misaligned = sum(1 for r in rows if r["label"] == "misaligned")
    print(f"Generated {len(rows)} pairs ({n_aligned} aligned, {n_misaligned} misaligned)")
    print(f"  Sources: {set(r['source'] for r in rows)}")
    print(f"  Pairs: {OUTPUT_DIR}")
    print(f"  Metadata: {META_PATH}")


if __name__ == "__main__":
    generate_all_pairs()
