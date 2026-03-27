#!/usr/bin/env python3
"""generate.py — Seed generation, genetic algorithm, controls, filtering,
and diversity selection for K562 enhancer design.

Includes a proper Euler-path dinucleotide shuffle (Altschul & Erickson 1985),
manufacturability + motif-explosion filters, and k-mer farthest-point
diversity selection.
"""
from __future__ import annotations

import random
from collections import defaultdict, deque
from itertools import product as iproduct
from typing import Callable, Optional

import numpy as np

from score import (
    BASES,
    K562_MOTIFS,
    MAX_MOTIF_COVERAGE,
    gc_content,
    motif_coverage_fraction,
    one_hot,
    reverse_complement,
)

# ── Seed generation ───────────────────────────────────────────────────────

def generate_seeds(
    n: int = 100, seq_len: int = 200, rng: Optional[random.Random] = None,
) -> list[str]:
    """K562-like seeds: embed 2-4 real TF motifs in GC-matched background."""
    rng = rng or random.Random(42)
    gc = 0.52
    bw = [(1 - gc) / 2, gc / 2, gc / 2, (1 - gc) / 2]
    motifs = list(K562_MOTIFS.values())
    seeds: list[str] = []
    for _ in range(n):
        bg = rng.choices(list(BASES), weights=bw, k=seq_len)
        used: list[tuple[int, int]] = []
        for idx in rng.sample(range(len(motifs)), rng.randint(2, 4)):
            m = motifs[idx]
            ms = seq_len - len(m)
            if ms < 0:
                continue
            for _ in range(30):
                p = rng.randint(0, ms)
                e = p + len(m)
                if all(e <= s or p >= en for s, en in used):
                    for j, b in enumerate(m):
                        bg[p + j] = b
                    used.append((p, e))
                    break
        seeds.append("".join(bg))
    print(f"Generated {n} synthetic K562 seed sequences ({seq_len} bp)")
    return seeds


def load_seeds_fasta(path) -> list[str]:
    from Bio import SeqIO
    seqs = [str(r.seq).upper() for r in SeqIO.parse(str(path), "fasta")]
    if not seqs:
        raise ValueError(f"No sequences in {path}")
    print(f"Loaded {len(seqs)} seed sequences from {path}")
    return seqs


# ── Controls — proper Euler-path dinucleotide shuffle ─────────────────────

def _dinuc_shuffle_euler(seq: str, rng: random.Random) -> str:
    """Dinucleotide-preserving shuffle via random Eulerian path.

    Constructs the dinucleotide multigraph and finds a random Euler path
    using Hierholzer's algorithm (Altschul & Erickson 1985; Kandel et al.
    1996).  Preserves exact first-order Markov statistics.
    """
    s = seq.upper()
    if len(s) <= 2:
        return s

    # Build multigraph  (edge from s[i] → s[i+1])
    adj: dict[str, list[str]] = defaultdict(list)
    for i in range(len(s) - 1):
        adj[s[i]].append(s[i + 1])

    # Shuffle edges — keep last edge per node fixed for connectivity
    for node in adj:
        edges = adj[node]
        if len(edges) > 1:
            last = edges[-1]
            rest = edges[:-1]
            rng.shuffle(rest)
            adj[node] = rest + [last]

    # Hierholzer's algorithm (Euler PATH from s[0])
    adj_q: dict[str, deque[str]] = {k: deque(v) for k, v in adj.items()}
    stack = [s[0]]
    path: list[str] = []
    while stack:
        v = stack[-1]
        if v in adj_q and adj_q[v]:
            stack.append(adj_q[v].popleft())
        else:
            path.append(stack.pop())
    path.reverse()

    return "".join(path) if len(path) == len(s) else s


def generate_controls(
    seeds: list[str], n: int = 100, rng: Optional[random.Random] = None,
) -> tuple[list[str], list[str]]:
    rng = rng or random.Random(42)
    L = len(seeds[0])
    rand_seqs = ["".join(rng.choices(list(BASES), k=L)) for _ in range(n)]
    shuf_seqs = [_dinuc_shuffle_euler(rng.choice(seeds), rng) for _ in range(n)]
    return rand_seqs, shuf_seqs


# ── Mutation / crossover ──────────────────────────────────────────────────

def _mutate(seq: str, rate: float, rng: random.Random) -> str:
    out = list(seq)
    for i in range(len(out)):
        if rng.random() < rate:
            out[i] = rng.choice([b for b in BASES if b != out[i]])
    return "".join(out)


def _crossover(p1: str, p2: str, rng: random.Random) -> str:
    """Two-point crossover — swap a central segment."""
    a, b = sorted(rng.sample(range(1, len(p1)), 2))
    return p1[:a] + p2[a:b] + p1[b:]


def _tournament(pop, scores, size, rng):
    idxs = rng.sample(range(len(pop)), size)
    return pop[max(idxs, key=lambda i: scores[i])]


# ── Genetic algorithm ─────────────────────────────────────────────────────

def run_ga(
    seeds: list[str],
    score_fn: Callable[[list[str]], np.ndarray],
    *,
    n_gen: int = 50,
    pop_size: int = 200,
    mut_rate: float = 0.04,
    xover_prob: float = 0.6,
    elite_frac: float = 0.05,
    tourn_size: int = 3,
    seed: int = 42,
) -> tuple[list[str], np.ndarray, list[dict]]:
    """GA with tournament selection, two-point crossover, and elitism.

    Returns (population, scores, trajectory).
    """
    rng = random.Random(seed)
    np.random.seed(seed)
    n_elite = max(1, int(pop_size * elite_frac))

    pop = [rng.choice(seeds) for _ in range(pop_size)]
    traj: list[dict] = []

    for gen in range(n_gen):
        sc = score_fn(pop)
        ranked = np.argsort(sc)[::-1]
        traj.append({
            "gen": gen + 1,
            "best": float(sc[ranked[0]]),
            "mean": float(sc.mean()),
            "std": float(sc.std()),
            "min": float(sc.min()),
        })
        if (gen + 1) % 10 == 0 or gen == 0:
            t = traj[-1]
            print(f"  Gen {gen+1:3d}/{n_gen}: best={t['best']:.4f} "
                  f"mean={t['mean']:.4f} std={t['std']:.4f}")

        elites = [pop[i] for i in ranked[:n_elite]]
        nxt = list(elites)
        while len(nxt) < pop_size:
            p1 = _tournament(pop, sc, tourn_size, rng)
            child = (_crossover(p1, _tournament(pop, sc, tourn_size, rng), rng)
                     if rng.random() < xover_prob else p1)
            nxt.append(_mutate(child, mut_rate, rng))
        pop = nxt

    return pop, score_fn(pop), traj


# ── Filters ───────────────────────────────────────────────────────────────

RESTRICTION_SITES = {
    "EcoRI": "GAATTC", "BamHI": "GGATCC",
    "HindIII": "AAGCTT", "NotI": "GCGGCCGC",
}


def check_manufacturability(seq: str) -> tuple[bool, list[str]]:
    s = seq.upper()
    issues: list[str] = []

    gc = gc_content(s)
    if gc < 0.30 or gc > 0.70:
        issues.append(f"GC={gc:.2f}")
    for base in BASES:
        if base * 7 in s:
            issues.append(f"homopoly {base}×7+")
    for i in range(len(s) - 7):
        di = s[i:i + 2]
        if s[i:i + 10] == di * 5:
            issues.append(f"dinuc {di}×5+")
            break
    for name, site in RESTRICTION_SITES.items():
        if site in s or reverse_complement(site) in s:
            issues.append(name)
    return len(issues) == 0, issues


def check_motif_explosion(seq: str) -> tuple[bool, str]:
    """Reject if any single TF motif covers > MAX_MOTIF_COVERAGE of sequence."""
    oh = one_hot(seq.upper())
    for name in K562_MOTIFS:
        cov = motif_coverage_fraction(oh, name)
        if cov > MAX_MOTIF_COVERAGE:
            return False, f"{name}={cov:.0%}"
    return True, ""


def filter_population(
    seqs: list[str], scores: np.ndarray,
) -> tuple[list[str], np.ndarray, dict]:
    """Apply manufacturability + motif-explosion filters.

    Returns (kept_seqs, kept_scores, filter_stats).
    """
    mfg_fail = motif_fail = 0
    keep: list[int] = []
    for i, s in enumerate(seqs):
        ok_m, _ = check_manufacturability(s)
        ok_e, _ = check_motif_explosion(s)
        if not ok_m:
            mfg_fail += 1
        if not ok_e:
            motif_fail += 1
        if ok_m and ok_e:
            keep.append(i)
    stats = {"mfg_fail": mfg_fail, "motif_explosion_fail": motif_fail,
             "kept": len(keep), "total": len(seqs)}
    return (
        [seqs[i] for i in keep],
        scores[np.array(keep)] if keep else np.array([]),
        stats,
    )


# ── Diversity ─────────────────────────────────────────────────────────────

def kmer_embedding(seq: str, k: int = 4) -> np.ndarray:
    kmers = ["".join(p) for p in iproduct("ACGT", repeat=k)]
    idx = {km: i for i, km in enumerate(kmers)}
    c = np.zeros(len(kmers), dtype=np.float32)
    s = seq.upper()
    for i in range(len(s) - k + 1):
        km = s[i:i + k]
        if km in idx:
            c[idx[km]] += 1
    t = c.sum()
    return c / t if t > 0 else c


def pairwise_edit_distance(seqs: list[str]) -> np.ndarray:
    """Normalised pairwise Hamming distance matrix."""
    n = len(seqs)
    mat = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = sum(a != b for a, b in zip(seqs[i], seqs[j])) / len(seqs[i])
            mat[i, j] = mat[j, i] = d
    return mat


def near_duplicate_fraction(seqs: list[str], threshold: float = 0.10) -> float:
    """Fraction of sequence pairs that are near-duplicates (<threshold edit dist)."""
    mat = pairwise_edit_distance(seqs)
    triu = mat[np.triu_indices(len(mat), k=1)]
    return float((triu < threshold).mean()) if len(triu) > 0 else 0.0


def select_diverse(
    seqs: list[str], scores: np.ndarray, top_k: int = 20, k: int = 4,
) -> tuple[list[str], np.ndarray, list[int]]:
    """Score-weighted farthest-point sampling in k-mer space."""
    n_cand = min(len(seqs), top_k * 3)
    ranked = np.argsort(scores)[::-1][:n_cand]
    cs, csc = [seqs[i] for i in ranked], scores[ranked]

    if len(cs) <= top_k:
        return cs, csc, list(range(len(cs)))

    emb = np.array([kmer_embedding(s, k) for s in cs])
    sel = [0]
    min_d = np.full(len(emb), np.inf)
    for _ in range(top_k - 1):
        d = np.sum((emb - emb[sel[-1]]) ** 2, axis=1)
        min_d = np.minimum(min_d, d)
        w = min_d * (csc ** 2)
        w[sel] = -1
        sel.append(int(np.argmax(w)))

    return [cs[i] for i in sel], csc[np.array(sel)], sel
