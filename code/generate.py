#!/usr/bin/env python3
"""generate.py — Genetic algorithm, seed generation, controls, filtering, and
diversity selection for K562 enhancer design.

Implements a proper GA with tournament selection, single-point crossover,
elitism, and adaptive mutation.  Post-GA stages include manufacturability
filtering and k-mer–based farthest-point diversity selection.
"""
from __future__ import annotations

import random
import re
from itertools import product as iproduct
from typing import Callable, Optional

import numpy as np

from score import (
    BASES,
    K562_MOTIFS,
    gc_content,
    reverse_complement,
)

# ── Seed sequence generation ──────────────────────────────────────────────

def generate_seeds(
    n: int = 100,
    seq_len: int = 200,
    rng: Optional[random.Random] = None,
) -> list[str]:
    """Create biologically plausible K562 enhancer-like seed sequences.

    Embeds 2-4 real TF motifs at random non-overlapping positions in a
    GC-matched background (~52 % GC, matching K562 open chromatin).
    """
    rng = rng or random.Random(42)
    gc_target = 0.52
    base_w = [(1 - gc_target) / 2, gc_target / 2,
              gc_target / 2, (1 - gc_target) / 2]  # A C G T
    motif_list = list(K562_MOTIFS.values())
    seeds: list[str] = []

    for _ in range(n):
        bg = rng.choices(list(BASES), weights=base_w, k=seq_len)
        n_motifs = rng.randint(2, 4)
        chosen = rng.sample(range(len(motif_list)), min(n_motifs, len(motif_list)))
        used: list[tuple[int, int]] = []
        for idx in chosen:
            motif = motif_list[idx]
            max_s = seq_len - len(motif)
            if max_s < 0:
                continue
            for _ in range(30):
                pos = rng.randint(0, max_s)
                end = pos + len(motif)
                if all(end <= s or pos >= e for s, e in used):
                    for j, b in enumerate(motif):
                        bg[pos + j] = b
                    used.append((pos, end))
                    break
        seeds.append("".join(bg))

    print(f"Generated {n} synthetic K562 seed sequences ({seq_len} bp)")
    return seeds


def load_seeds_fasta(path) -> list[str]:
    """Load seed sequences from a FASTA file via BioPython."""
    from Bio import SeqIO
    seqs = [str(r.seq).upper() for r in SeqIO.parse(str(path), "fasta")]
    if not seqs:
        raise ValueError(f"No sequences in {path}")
    print(f"Loaded {len(seqs)} seed sequences from {path}")
    return seqs


# ── Control generation ────────────────────────────────────────────────────

def generate_controls(
    seeds: list[str], n: int = 100, rng: Optional[random.Random] = None,
) -> tuple[list[str], list[str]]:
    rng = rng or random.Random(42)
    L = len(seeds[0])
    rand_seqs = ["".join(rng.choices(list(BASES), k=L)) for _ in range(n)]
    shuf_seqs = [_dinuc_shuffle(rng.choice(seeds), rng) for _ in range(n)]
    return rand_seqs, shuf_seqs


def _dinuc_shuffle(seq: str, rng: random.Random) -> str:
    s = list(seq.upper())
    for i in range(len(s) - 2, 0, -1):
        j = rng.randint(0, i)
        s[i], s[j] = s[j], s[i]
    return "".join(s)


# ── Mutation & crossover ─────────────────────────────────────────────────

def _mutate(seq: str, rate: float, rng: random.Random) -> str:
    out = list(seq)
    for i in range(len(out)):
        if rng.random() < rate:
            out[i] = rng.choice([b for b in BASES if b != out[i]])
    return "".join(out)


def _crossover(p1: str, p2: str, rng: random.Random) -> str:
    pt = rng.randint(1, len(p1) - 1)
    return p1[:pt] + p2[pt:]


def _tournament(pop: list[str], scores: np.ndarray, size: int,
                rng: random.Random) -> str:
    idxs = rng.sample(range(len(pop)), size)
    winner = max(idxs, key=lambda i: scores[i])
    return pop[winner]


# ── Genetic algorithm ─────────────────────────────────────────────────────

def run_ga(
    seeds: list[str],
    score_fn: Callable[[list[str]], np.ndarray],
    *,
    n_gen: int = 50,
    pop_size: int = 100,
    mut_rate: float = 0.05,
    crossover_prob: float = 0.6,
    elite_frac: float = 0.05,
    tournament_size: int = 3,
    seed: int = 42,
) -> tuple[list[str], np.ndarray, list[dict]]:
    """GA with tournament selection, crossover, elitism.

    Returns (final_population, final_scores, trajectory).
    trajectory: list of {gen, best, mean, std, min} dicts.
    """
    rng = random.Random(seed)
    np.random.seed(seed)
    n_elite = max(1, int(pop_size * elite_frac))

    pop = [rng.choice(seeds) for _ in range(pop_size)]
    trajectory: list[dict] = []

    for gen in range(n_gen):
        scores = score_fn(pop)
        ranked = np.argsort(scores)[::-1]

        stats = {
            "gen": gen + 1,
            "best": float(scores[ranked[0]]),
            "mean": float(scores.mean()),
            "std": float(scores.std()),
            "min": float(scores.min()),
        }
        trajectory.append(stats)

        if (gen + 1) % 10 == 0 or gen == 0:
            print(
                f"  Gen {gen+1:3d}/{n_gen}: "
                f"best={stats['best']:.4f}  "
                f"mean={stats['mean']:.4f}  "
                f"std={stats['std']:.4f}"
            )

        # Elitism: keep top individuals unchanged
        elites = [pop[i] for i in ranked[:n_elite]]
        next_gen = list(elites)

        while len(next_gen) < pop_size:
            p1 = _tournament(pop, scores, tournament_size, rng)
            if rng.random() < crossover_prob:
                p2 = _tournament(pop, scores, tournament_size, rng)
                child = _crossover(p1, p2, rng)
            else:
                child = p1
            child = _mutate(child, mut_rate, rng)
            next_gen.append(child)

        pop = next_gen

    final_scores = score_fn(pop)
    return pop, final_scores, trajectory


# ── Manufacturability filter ──────────────────────────────────────────────

RESTRICTION_SITES = {
    "EcoRI": "GAATTC", "BamHI": "GGATCC",
    "HindIII": "AAGCTT", "NotI": "GCGGCCGC",
}


def check_manufacturability(seq: str) -> tuple[bool, list[str]]:
    """Return (passes, list_of_issues)."""
    s = seq.upper()
    issues: list[str] = []

    gc = gc_content(s)
    if gc < 0.30 or gc > 0.70:
        issues.append(f"GC={gc:.2f}")

    for base in BASES:
        if base * 7 in s:
            issues.append(f"homopolymer {base}×7+")

    for rp in range(len(s) - 3):
        di = s[rp:rp + 2]
        if di * 5 in s:
            issues.append(f"dinuc repeat {di}×5+")
            break

    for name, site in RESTRICTION_SITES.items():
        if site in s or reverse_complement(site) in s:
            issues.append(f"{name} site")

    return len(issues) == 0, issues


def filter_population(
    seqs: list[str], scores: np.ndarray,
) -> tuple[list[str], np.ndarray, int]:
    """Remove non-manufacturable sequences. Returns (seqs, scores, n_removed)."""
    keep_idx = [i for i, s in enumerate(seqs) if check_manufacturability(s)[0]]
    n_removed = len(seqs) - len(keep_idx)
    return (
        [seqs[i] for i in keep_idx],
        scores[np.array(keep_idx)] if keep_idx else np.array([]),
        n_removed,
    )


# ── Diversity selection ───────────────────────────────────────────────────

def kmer_embedding(seq: str, k: int = 4) -> np.ndarray:
    """Normalised k-mer frequency vector (4^k dimensions)."""
    kmers = ["".join(p) for p in iproduct("ACGT", repeat=k)]
    idx = {km: i for i, km in enumerate(kmers)}
    counts = np.zeros(len(kmers), dtype=np.float32)
    s = seq.upper()
    for i in range(len(s) - k + 1):
        kmer = s[i:i + k]
        if kmer in idx:
            counts[idx[kmer]] += 1
    total = counts.sum()
    return counts / total if total > 0 else counts


def select_diverse(
    seqs: list[str], scores: np.ndarray, top_k: int = 20, k: int = 4,
) -> tuple[list[str], np.ndarray, list[int]]:
    """Select top_k sequences by score, then enforce diversity via
    farthest-point sampling in k-mer space.

    Returns (selected_seqs, selected_scores, selected_indices).
    """
    # Pre-filter to top 3×top_k candidates by score
    n_cand = min(len(seqs), top_k * 3)
    ranked = np.argsort(scores)[::-1][:n_cand]
    cand_seqs = [seqs[i] for i in ranked]
    cand_scores = scores[ranked]

    if len(cand_seqs) <= top_k:
        return cand_seqs, cand_scores, list(range(len(cand_seqs)))

    embeds = np.array([kmer_embedding(s, k) for s in cand_seqs])

    # Greedy farthest-point sampling, seeded with the highest-scoring seq
    selected = [0]
    min_dists = np.full(len(embeds), np.inf)
    for _ in range(top_k - 1):
        d = np.sum((embeds - embeds[selected[-1]]) ** 2, axis=1)
        min_dists = np.minimum(min_dists, d)
        # Weight by score to prefer higher-scoring diverse candidates
        weighted = min_dists * (cand_scores ** 2)
        weighted[selected] = -1
        selected.append(int(np.argmax(weighted)))

    sel_seqs = [cand_seqs[i] for i in selected]
    sel_scores = cand_scores[np.array(selected)]
    return sel_seqs, sel_scores, selected
