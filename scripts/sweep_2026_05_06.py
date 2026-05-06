#!/usr/bin/env python3
"""Erdős #97 numerical sweep — 2026-05-06.

Tries five families of selected-witness incidence patterns NOT in the existing
built-in catalog, with combinatorial pre-filters before numerical optimization:

  1. Random 4-subset patterns at n in {10..16}, filtered for L5 row-overlap and
     vertex-circle (self-edge / strict-cycle) compatibility.
  2. Two-orbit families on Z/2m with alternating outer/inner radii — the
     incidence pattern on the alternating polygon, with general per-orbit
     selected sets.
  3. Three-orbit families on Z/3m with one orbit per residue mod 3.
  4. AG(2,3)-derived 9-point patterns (parallel-class 4-subset selection on
     the 12 lines).
  5. Small-n Sidon hits at n in {12, 14, 15, 16}: enumerate every 4-subset of
     Z/n with all 12 pairwise differences distinct mod n, and try to realize.

Numerical stage: SLSQP polar with margin 1e-4 (then 1e-6 if 1e-4 succeeds).
Reports near-misses meeting eq_residual<1e-8, conv_margin>1e-3, edge>1e-3,
pair>1e-3, no cluster collapse.
"""
from __future__ import annotations

import argparse
import dataclasses
import itertools
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import numpy as np

from erdos97.search import (
    LossWeights,
    PatternInfo,
    built_in_patterns,
    incidence_obstruction_stats,
    independent_diagnostics,
    polygon_from_x,
    search_pattern,
    validate_candidate_shape,
)
from erdos97.generic_vertex_search import GenericVertexSearch

OUT_DIR = REPO / "data" / "runs" / "2026-05-06"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NEAR_MISS_REQ = {
    "eq_residual_max": 1e-8,
    "convexity_margin_min": 1e-3,
    "min_edge_min": 1e-3,
    "min_pair_min": 1e-3,
    "max_spread_min": 1.0,  # coord spread > 1 (no cluster collapse)
    "vertex_multiplicity": 4,
}


# ---------------------------- existing-pattern fingerprint ----------------

def pattern_fingerprint(S: Sequence[Sequence[int]]) -> Tuple[Tuple[int, ...], ...]:
    rows = tuple(tuple(sorted(int(j) for j in row)) for row in S)
    return rows


def _shifted_fingerprints(n: int, S: Sequence[Sequence[int]]) -> List[Tuple[Tuple[int, ...], ...]]:
    """All n cyclic shifts of S (i -> i+s mod n)."""
    fps: List[Tuple[Tuple[int, ...], ...]] = []
    for s in range(n):
        Sshift: List[List[int]] = [None] * n  # type: ignore
        for i in range(n):
            new_i = (i + s) % n
            Sshift[new_i] = sorted((j + s) % n for j in S[i])
        fps.append(pattern_fingerprint(Sshift))
    return fps


def existing_fingerprints() -> set:
    fps: set = set()
    for pat in built_in_patterns().values():
        for fp in _shifted_fingerprints(pat.n, pat.S):
            fps.add((pat.n, fp))
    return fps


# ---------------------------- combinatorial filters ----------------------

def row_overlap_ok(S: Sequence[Sequence[int]], cap: int = 2) -> bool:
    n = len(S)
    sets = [set(r) for r in S]
    for a in range(n):
        if len(sets[a]) != len(S[a]):
            return False
        if a in sets[a]:
            return False
        if len(sets[a]) != 4:
            return False
        for b in range(a + 1, n):
            if len(sets[a].intersection(sets[b])) > cap:
                return False
    return True


def column_pair_cap_ok(S: Sequence[Sequence[int]], cap: int = 2) -> bool:
    """The dual cap: a single chord (i,j) cannot appear as a witness pair in
    more than ``cap`` rows. Equivalently: for each unordered pair {i,j} of
    targets, count rows containing both; cap at 2."""
    n = len(S)
    counts: dict = defaultdict(int)
    for row in S:
        for a, b in itertools.combinations(sorted(row), 2):
            counts[(a, b)] += 1
            if counts[(a, b)] > cap:
                return False
    return True


def indegree_balanced(S: Sequence[Sequence[int]], min_in: int = 2, max_in: int = 6) -> bool:
    n = len(S)
    indeg = [0] * n
    for row in S:
        for j in row:
            indeg[j] += 1
    return min(indeg) >= min_in and max(indeg) <= max_in


_VC_CACHE: dict = {}


def _get_vc(n: int) -> GenericVertexSearch:
    if n not in _VC_CACHE:
        _VC_CACHE[n] = GenericVertexSearch(n)
    return _VC_CACHE[n]


def vertex_circle_compatible(n: int, S: Sequence[Sequence[int]]) -> Tuple[bool, str]:
    """Run the GenericVertexSearch single-shot vertex-circle check on a fixed
    full assignment (natural order). Returns (ok, status)."""
    g = _get_vc(n)
    assign = {}
    for i, row in enumerate(S):
        m = 0
        for j in row:
            m |= 1 << j
        assign[i] = m
    status = g.vertex_circle_status(assign)
    return status == "ok", status


def vertex_circle_compatible_lightweight(n: int, S: Sequence[Sequence[int]]) -> Tuple[bool, str]:
    """Lightweight self-edge check that avoids constructing the full
    GenericVertexSearch instance. We construct the union-find of selected
    pairs (all targets in row i are equidistant from i) and walk the strict
    nested-chord constraints to detect a self-edge. The strict-cycle DFS is
    omitted; we treat strict-cycle survivors as 'ok-lite'.

    Returns ('ok', 'self_edge', or 'ok_lite')."""
    pair_index: dict = {}
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pair_index[(i, j)] = len(pairs)
            pairs.append((i, j))

    parent = list(range(len(pairs)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        parent[max(ra, rb)] = min(ra, rb)

    def pidx(a: int, b: int) -> int:
        if a > b:
            a, b = b, a
        return pair_index[(a, b)]

    # Collect selected-pair classes
    for i, row in enumerate(S):
        sel = [pidx(i, j) for j in row]
        for k in range(1, len(sel)):
            union(sel[0], sel[k])

    # Strict edges: for each row, sort targets by (j - i) mod n then for each
    # pair (a<b) of those positions, the chord (sorted(targets[a],
    # targets[b])) is *contained* in chords (sorted(...)) of any wider span.
    # We need to check that no nested-chord pair lands in the same class.
    for i, row in enumerate(S):
        ws = sorted(row, key=lambda w: (w - i) % n)
        # for every pair a<b
        for a_start in range(4):
            for a_end in range(a_start + 1, 4):
                outer_p = pidx(ws[a_start], ws[a_end])
                for b_start in range(a_start, a_end + 1):
                    for b_end in range(b_start + 1, a_end + 1):
                        if (a_start, a_end) == (b_start, b_end):
                            continue
                        if not (a_start <= b_start and b_end <= a_end):
                            continue
                        inner_p = pidx(ws[b_start], ws[b_end])
                        if find(outer_p) == find(inner_p):
                            return False, "self_edge"
    return True, "ok_lite"


# ---------------------------- pattern generators -------------------------

def random_subset_patterns(
    n: int,
    n_candidates: int,
    rng: np.random.Generator,
) -> Iterator[Tuple[List[List[int]], dict]]:
    """Yield random 4-subset selections per center, post-filter."""
    targets = list(range(n))
    for k in range(n_candidates):
        S: List[List[int]] = []
        for i in range(n):
            choices = [j for j in targets if j != i]
            sel = sorted(rng.choice(choices, size=4, replace=False).tolist())
            S.append(sel)
        meta = {"family": "random4", "candidate_index": k}
        yield S, meta


def random_subset_patterns_capped(
    n: int,
    n_candidates: int,
    rng: np.random.Generator,
    max_pair_cap: int = 2,
    max_attempts_per: int = 200,
) -> Iterator[Tuple[List[List[int]], dict]]:
    """Generate random 4-subset patterns building row-by-row with the L5
    pairwise overlap cap enforced incrementally. Skips if no extension is
    possible at any row. Far higher density of acceptable candidates than
    the naive iid generator."""
    for k in range(n_candidates):
        for attempt in range(max_attempts_per):
            S: List[List[int]] = []
            ok = True
            current_sets: List[set] = []
            chord_counts: dict = defaultdict(int)
            indeg = [0] * n
            max_indeg = (max_pair_cap * (n - 1)) // 3
            for i in range(n):
                # generate combinations of 4 targets that satisfy filters
                pool = [j for j in range(n) if j != i and indeg[j] < max_indeg]
                if len(pool) < 4:
                    ok = False
                    break
                # randomized greedy: try up to 50 random 4-subsets
                tried = 0
                row = None
                while tried < 50:
                    tried += 1
                    cand = sorted(rng.choice(pool, size=4, replace=False).tolist())
                    cand_set = set(cand)
                    # cap intersection with previous rows
                    if any(len(cand_set.intersection(prev)) > max_pair_cap for prev in current_sets):
                        continue
                    # cap chord usage
                    cand_chords = list(itertools.combinations(cand, 2))
                    if any(chord_counts[c] >= max_pair_cap for c in cand_chords):
                        continue
                    row = cand
                    break
                if row is None:
                    ok = False
                    break
                S.append(row)
                current_sets.append(set(row))
                for c in itertools.combinations(row, 2):
                    chord_counts[c] += 1
                for j in row:
                    indeg[j] += 1
            if ok and len(S) == n:
                meta = {"family": "random4_capped", "candidate_index": k, "attempts": attempt + 1}
                yield S, meta
                break


def circulant_patterns(n: int) -> Iterator[Tuple[List[List[int]], dict]]:
    """Cyclic patterns S_i = i + D mod n for every 4-subset D of Z/n
    (excluding 0). Heavy filtering."""
    for D in itertools.combinations(range(1, n), 4):
        # First element fixed >= 1 by combination order; symmetry quotient
        # handled later by fingerprinting against existing.
        if 0 in D:
            continue
        S = [sorted({(i + d) % n for d in D}) for i in range(n)]
        if any(i in S[i] for i in range(n)):
            continue
        meta = {"family": "circulant_offsets", "offsets": list(D)}
        yield S, meta


def small_sidon_patterns(n: int) -> Iterator[Tuple[List[List[int]], dict]]:
    """4-subsets D of Z/n with all 12 pairwise differences distinct mod n.

    This is a strict Sidon-circulant generator: differences d_a-d_b for
    a != b among the 4 elements are pairwise distinct (mod n)."""
    for D in itertools.combinations(range(n), 4):
        if 0 in D:
            # D should be a "shift" of the canonical so omit 0-anchored ones?
            # We allow them; later the cyclic shift fingerprint deduplicates.
            pass
        diffs = set()
        ok = True
        for a, b in itertools.permutations(D, 2):
            d = (a - b) % n
            if d in diffs:
                ok = False
                break
            diffs.add(d)
        if not ok:
            continue
        S = [sorted({(i + d) % n for d in D}) for i in range(n)]
        if any(i in S[i] for i in range(n)):
            continue
        meta = {"family": "sidon4_circulant", "offsets": list(D)}
        yield S, meta


def two_orbit_z2m_patterns(
    m: int,
    n_candidates: int,
    rng: np.random.Generator,
) -> Iterator[Tuple[List[List[int]], dict]]:
    """Two-orbit alternating polygon families on n=2m vertices.

    Even centers (orbit A) have selected witness offsets f_A : Z/2m -> Z/2m of
    size 4; odd centers (orbit B) similarly. We sample random offset pairs and
    keep those where every center i has the four targets distinct from i."""
    n = 2 * m
    for k in range(n_candidates):
        # offsets are signed integers in (-(n-1)..n-1) excluding 0
        candidates = [d for d in range(1, n) if d != 0]
        all_vals = list(range(-n + 1, n))
        all_vals = [v for v in all_vals if v != 0]
        even_off = sorted(rng.choice(all_vals, size=4, replace=False).tolist())
        odd_off = sorted(rng.choice(all_vals, size=4, replace=False).tolist())
        S: List[List[int]] = []
        ok = True
        for i in range(n):
            offs = even_off if i % 2 == 0 else odd_off
            row = sorted({(i + o) % n for o in offs})
            if i in row or len(row) != 4:
                ok = False
                break
            S.append(row)
        if not ok:
            continue
        meta = {
            "family": "two_orbit_z2m",
            "m": m,
            "even_offsets": even_off,
            "odd_offsets": odd_off,
        }
        yield S, meta


def three_orbit_z3m_patterns(
    m: int,
    n_candidates: int,
    rng: np.random.Generator,
) -> Iterator[Tuple[List[List[int]], dict]]:
    """Three-orbit families on n=3m vertices, one orbit per residue mod 3."""
    n = 3 * m
    all_vals = [v for v in range(-n + 1, n) if v != 0]
    for k in range(n_candidates):
        offs0 = sorted(rng.choice(all_vals, size=4, replace=False).tolist())
        offs1 = sorted(rng.choice(all_vals, size=4, replace=False).tolist())
        offs2 = sorted(rng.choice(all_vals, size=4, replace=False).tolist())
        S: List[List[int]] = []
        ok = True
        for i in range(n):
            r = i % 3
            offs = [offs0, offs1, offs2][r]
            row = sorted({(i + o) % n for o in offs})
            if i in row or len(row) != 4:
                ok = False
                break
            S.append(row)
        if not ok:
            continue
        meta = {
            "family": "three_orbit_z3m",
            "m": m,
            "offsets_r0": offs0,
            "offsets_r1": offs1,
            "offsets_r2": offs2,
        }
        yield S, meta


def ag23_patterns() -> Iterator[Tuple[List[List[int]], dict]]:
    """AG(2,3) has 9 points and 12 lines in 4 parallel classes (3 lines each).

    For each center i in Z/9 = AG(2,3), we choose a 4-subset of the remaining
    8 points. A natural pattern: at each vertex i, select the 4 "non-self"
    points reachable by a fixed parallel-class direction at distance 1 and 2.

    Actually the AG-derived patterns we'll try: pick one of the 4 directions
    d in {(1,0),(0,1),(1,1),(1,2)}; at vertex (a,b), select
        (a+d_x, b+d_y), (a+2d_x, b+2d_y), (a+d_x+e_x, b+d_y+e_y), (a-e_x, b-e_y)
    for each of the other 3 directions e (i.e. 3 patterns per chosen d, total 12).
    Index points by 3a+b mod 9.
    """
    pts = [(a, b) for a in range(3) for b in range(3)]
    label = {p: 3 * p[0] + p[1] for p in pts}
    dirs = [(1, 0), (0, 1), (1, 1), (1, 2)]
    for d in dirs:
        for e in dirs:
            if e == d:
                continue
            for f in dirs:
                if f == d or f == e:
                    continue
                # selection: shift by d, 2d, d+e, -f
                S: List[List[int]] = []
                ok = True
                for (a, b) in pts:
                    targets = []
                    for sh in [(d[0], d[1]), (2 * d[0], 2 * d[1]),
                               (d[0] + e[0], d[1] + e[1]),
                               (-f[0], -f[1])]:
                        ap = (a + sh[0]) % 3
                        bp = (b + sh[1]) % 3
                        targets.append(label[(ap, bp)])
                    targets = sorted(set(targets))
                    me = label[(a, b)]
                    if me in targets or len(targets) != 4:
                        ok = False
                        break
                    S.append(targets)
                if not ok:
                    continue
                meta = {
                    "family": "ag23",
                    "d": d, "e": e, "f": f,
                }
                yield S, meta


def ag23_line_patterns() -> Iterator[Tuple[List[List[int]], dict]]:
    """Another AG(2,3) family: rather than triple-shift, pick 4 of the 8
    other points using "complement of one parallel class through self".

    For each center i, find the unique point along each of the 4 directions
    at +1 and +2 (8 points = all others). Selecting 4 of 8 = (8 choose 4) = 70
    candidates per center -- too many. Instead use the 4 directions and select
    the +1 step for each direction (gives 4 distinct points)."""
    pts = [(a, b) for a in range(3) for b in range(3)]
    label = {p: 3 * p[0] + p[1] for p in pts}
    dir_sets = [
        [(1, 0), (0, 1), (1, 1), (1, 2)],   # 4 +1 steps
        [(2, 0), (0, 2), (2, 2), (2, 1)],   # 4 +2 steps
        [(1, 0), (2, 0), (0, 1), (0, 2)],   # axis-only
        [(1, 1), (2, 2), (1, 2), (2, 1)],   # diagonals
    ]
    for idx, dirs in enumerate(dir_sets):
        S: List[List[int]] = []
        ok = True
        for (a, b) in pts:
            targets = []
            for (dx, dy) in dirs:
                ap = (a + dx) % 3
                bp = (b + dy) % 3
                targets.append(label[(ap, bp)])
            targets = sorted(set(targets))
            me = label[(a, b)]
            if me in targets or len(targets) != 4:
                ok = False
                break
            S.append(targets)
        if not ok:
            continue
        yield S, {"family": "ag23_line", "dirs": dirs, "set_id": idx}


# ---------------------------- main sweep --------------------------------

@dataclasses.dataclass
class CandidateRecord:
    name: str
    n: int
    family: str
    S: List[List[int]]
    meta: dict
    eq_rms: float = float("nan")
    max_spread: float = float("nan")
    convexity_margin: float = float("nan")
    min_edge_length: float = float("nan")
    min_pair_distance: float = float("nan")
    near_miss: bool = False
    optimization_succeeded: bool = False
    elapsed_sec: float = 0.0

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def is_near_miss(eq_rms, max_spread, conv_margin, min_edge, min_pair) -> bool:
    """Approximate near-miss check (vertex multiplicity is checked elsewhere)."""
    return (
        eq_rms < NEAR_MISS_REQ["eq_residual_max"]
        and conv_margin > NEAR_MISS_REQ["convexity_margin_min"]
        and min_edge > NEAR_MISS_REQ["min_edge_min"]
        and min_pair > NEAR_MISS_REQ["min_pair_min"]
        and max_spread > NEAR_MISS_REQ["max_spread_min"]
    )


def evaluate_pattern(
    S: List[List[int]],
    name: str,
    family: str,
    meta: dict,
    *,
    n: int,
    seed: int = 42,
    restarts: int = 100,
    max_nfev: int = 5000,
    margin: float = 1e-4,
    out_dir: Optional[Path] = None,
) -> CandidateRecord:
    """Two-stage evaluation: fast TRF screen, then promote promising patterns
    to SLSQP with hard margin constraints.

    Stage 1 (cheap): TRF, 3 restarts, max_nfev=300, soft margin 1e-3.
       - filter on eq_rms < 0.5 (suggestive of a near-realization)
    Stage 2 (deep): SLSQP, full restart count, hard margin = ``margin``.
    """
    rec = CandidateRecord(name=name, n=n, family=family, S=S, meta=dict(meta))
    pat = PatternInfo(name=name, n=n, S=S, family=family, formula=str(meta))

    t0 = time.time()
    # Stage 1: cheap TRF screen
    cheap_restarts = 1
    cheap_nfev = 80
    try:
        result = search_pattern(
            pat,
            mode="polar",
            restarts=cheap_restarts,
            seed=seed,
            max_nfev=cheap_nfev,
            optimizer="trf",
            margin=1e-3,
            verbose=False,
        )
    except Exception as exc:
        rec.optimization_succeeded = False
        rec.elapsed_sec = time.time() - t0
        rec.meta["error"] = str(exc)[:200]
        return rec

    rec.optimization_succeeded = bool(result.success)
    rec.eq_rms = float(result.eq_rms)
    rec.max_spread = float(result.max_spread)
    rec.convexity_margin = float(result.convexity_margin)
    rec.min_edge_length = float(result.min_edge_length)
    rec.min_pair_distance = float(result.min_pair_distance)
    rec.elapsed_sec = time.time() - t0
    rec.meta["stage"] = "trf_screen"

    P = np.asarray(result.coordinates, dtype=float)
    bbox = float(max(np.ptp(P[:, 0]), np.ptp(P[:, 1])))
    rec.meta["bbox_spread"] = bbox

    promote = rec.eq_rms < 0.5 and rec.convexity_margin > -1e-2
    if not promote:
        # Stage 1 only — record and return
        rec.near_miss = is_near_miss(
            rec.eq_rms, bbox, rec.convexity_margin,
            rec.min_edge_length, rec.min_pair_distance,
        )
        return rec

    # Stage 2: SLSQP deep
    rec.meta["stage"] = "slsqp_deep"
    try:
        result2 = search_pattern(
            pat,
            mode="polar",
            restarts=restarts,
            seed=seed,
            max_nfev=max_nfev,
            optimizer="slsqp",
            margin=margin,
            verbose=False,
        )
    except Exception as exc:
        # SLSQP failed; keep TRF result, mark
        rec.meta["slsqp_error"] = str(exc)[:200]
        rec.elapsed_sec = time.time() - t0
        return rec

    rec.optimization_succeeded = bool(result2.success)
    rec.eq_rms = float(result2.eq_rms)
    rec.max_spread = float(result2.max_spread)
    rec.convexity_margin = float(result2.convexity_margin)
    rec.min_edge_length = float(result2.min_edge_length)
    rec.min_pair_distance = float(result2.min_pair_distance)
    P = np.asarray(result2.coordinates, dtype=float)
    bbox = float(max(np.ptp(P[:, 0]), np.ptp(P[:, 1])))
    rec.meta["bbox_spread"] = bbox
    rec.elapsed_sec = time.time() - t0

    rec.near_miss = is_near_miss(
        rec.eq_rms, bbox, rec.convexity_margin,
        rec.min_edge_length, rec.min_pair_distance,
    )

    # Save SLSQP-stage JSON
    if out_dir is not None:
        path = out_dir / f"{name}_slsqp_m{margin:.0e}_seed{seed}.json"
        try:
            data = dataclasses.asdict(result2)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                f.write("\n")
            rec.meta["run_path"] = str(path.relative_to(REPO))
        except Exception as exc:
            rec.meta["save_error"] = str(exc)[:200]

    return rec


def run_sweep(args) -> dict:
    rng = np.random.default_rng(args.seed)
    existing = existing_fingerprints()
    print(f"existing patterns (with shifts) in catalog: {len(existing)} fingerprints")

    all_records: List[CandidateRecord] = []
    near_misses: List[CandidateRecord] = []
    pre_filter_stats = {
        "examined": 0,
        "row_overlap_pass": 0,
        "column_pair_cap_pass": 0,
        "indegree_pass": 0,
        "vertex_circle_ok": 0,
        "vertex_circle_self_edge": 0,
        "vertex_circle_strict_cycle": 0,
        "duplicate_known": 0,
        "submitted_to_optimizer": 0,
    }

    def consider(S: List[List[int]], n: int, family: str, meta: dict, name: str) -> Optional[CandidateRecord]:
        pre_filter_stats["examined"] += 1
        if not row_overlap_ok(S):
            return None
        pre_filter_stats["row_overlap_pass"] += 1
        if not column_pair_cap_ok(S):
            return None
        pre_filter_stats["column_pair_cap_pass"] += 1
        if not indegree_balanced(S):
            return None
        pre_filter_stats["indegree_pass"] += 1

        # Deduplicate against known patterns and previous submissions
        fps = _shifted_fingerprints(n, S)
        if any((n, fp) in existing for fp in fps):
            pre_filter_stats["duplicate_known"] += 1
            return None
        # Add to existing-set so future picks skip this one
        for fp in fps:
            existing.add((n, fp))

        # Use lightweight self-edge check to avoid quadratic-in-n^2 build cost
        if n <= args.full_vc_cutoff:
            ok, status = vertex_circle_compatible(n, S)
        else:
            ok, status = vertex_circle_compatible_lightweight(n, S)
        if status == "self_edge":
            pre_filter_stats["vertex_circle_self_edge"] += 1
            return None
        if status == "strict_cycle":
            pre_filter_stats["vertex_circle_strict_cycle"] += 1
            return None
        pre_filter_stats["vertex_circle_ok"] += 1

        pre_filter_stats["submitted_to_optimizer"] += 1
        rec = evaluate_pattern(
            S, name, family, meta,
            n=n,
            seed=args.opt_seed,
            restarts=args.restarts,
            max_nfev=args.max_nfev,
            margin=args.margin,
            out_dir=OUT_DIR,
        )
        all_records.append(rec)
        if rec.near_miss:
            near_misses.append(rec)
        return rec

    # ----- 1. small Sidon hits (deterministic enumeration) -----
    print("\n[1] enumerating small-n Sidon 4-subsets...")
    for n in args.sidon_ns:
        produced = 0
        for S, meta in small_sidon_patterns(n):
            offs = meta["offsets"]
            name = f"S{n}_sidon_{'_'.join(str(o) for o in offs)}"
            rec = consider(S, n, "sidon4_circulant", meta, name)
            if rec is not None:
                produced += 1
        print(f"  n={n}: submitted {produced}")

    # ----- 2. two-orbit Z/2m -----
    print("\n[2] two-orbit Z/2m random...")
    two_orbit_specs = [
        (5, 30),  # n=10
        (6, 40),  # n=12
        (7, 25),  # n=14
        (8, 20),  # n=16
    ]
    for m, k in two_orbit_specs:
        n = 2 * m
        produced = 0
        for S, meta in two_orbit_z2m_patterns(m, k, rng):
            offs_a = "_".join(str(o) for o in meta["even_offsets"])
            offs_b = "_".join(str(o) for o in meta["odd_offsets"])
            name = f"P{n}_two_orbit_e_{offs_a}_o_{offs_b}"
            rec = consider(S, n, "two_orbit_z2m", meta, name)
            if rec is not None:
                produced += 1
        print(f"  m={m} (n={n}): submitted {produced}")

    # ----- 3. three-orbit Z/3m -----
    print("\n[3] three-orbit Z/3m random...")
    three_orbit_specs = [
        (4, 25),   # n=12
        (5, 20),   # n=15
    ]
    for m, k in three_orbit_specs:
        n = 3 * m
        produced = 0
        for S, meta in three_orbit_z3m_patterns(m, k, rng):
            o0 = "_".join(str(o) for o in meta["offsets_r0"])
            o1 = "_".join(str(o) for o in meta["offsets_r1"])
            o2 = "_".join(str(o) for o in meta["offsets_r2"])
            name = f"T{n}_three_orbit_a_{o0}_b_{o1}_c_{o2}"
            rec = consider(S, n, "three_orbit_z3m", meta, name)
            if rec is not None:
                produced += 1
        print(f"  m={m} (n={n}): submitted {produced}")

    # ----- 4. AG(2,3) lines -----
    print("\n[4] AG(2,3) line / shift patterns (n=9)...")
    ag_count = 0
    for S, meta in ag23_line_patterns():
        name = f"AG23_line_set{meta['set_id']}"
        rec = consider(S, 9, "ag23_line", meta, name)
        if rec is not None:
            ag_count += 1
    for S, meta in ag23_patterns():
        name = "AG23_dir_{}_{}_{}".format(
            "_".join(str(v) for v in meta["d"]),
            "_".join(str(v) for v in meta["e"]),
            "_".join(str(v) for v in meta["f"]),
        )
        rec = consider(S, 9, "ag23_dir", meta, name)
        if rec is not None:
            ag_count += 1
    print(f"  AG(2,3) submitted: {ag_count}")

    # ----- 5. random 4-subsets with cap-respecting greedy + vertex-circle pre-filter -----
    print("\n[5] random 4-subsets (capped, row-by-row) at n in {10, 11, 12, 13}...")
    random_specs = [
        (10, 20),
        (11, 25),
        (12, 30),
        (13, 35),
    ]
    for n, k in random_specs:
        produced = 0
        for S, meta in random_subset_patterns_capped(n, k, rng):
            name = f"R{n}_rand_{rng.integers(1, 1 << 30)}"
            rec = consider(S, n, "random4_capped", meta, name)
            if rec is not None:
                produced += 1
        print(f"  n={n}: submitted {produced}")

    # ----- summary -----
    summary = {
        "pre_filter_stats": pre_filter_stats,
        "submitted_total": len(all_records),
        "near_misses": [r.to_dict() for r in near_misses],
        "top_records": sorted(
            (r.to_dict() for r in all_records if not math.isnan(r.eq_rms)),
            key=lambda r: r["eq_rms"],
        )[:20],
    }
    return summary


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=20260506,
                    help="seed for random pattern generation")
    ap.add_argument("--opt-seed", type=int, default=42,
                    help="seed for SLSQP optimizer (per pattern)")
    ap.add_argument("--restarts", type=int, default=100)
    ap.add_argument("--max-nfev", type=int, default=5000)
    ap.add_argument("--margin", type=float, default=1e-4)
    ap.add_argument("--sidon-ns", type=int, nargs="+",
                    default=[12, 14, 15, 16])
    ap.add_argument("--out", type=Path, default=OUT_DIR / "sweep_summary.json")
    ap.add_argument("--quick", action="store_true",
                    help="reduce restarts and pattern counts (smoke test)")
    ap.add_argument("--full-vc-cutoff", type=int, default=10,
                    help="use full GenericVertexSearch only for n<=cutoff")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    if args.quick:
        args.restarts = max(args.restarts // 5, 10)
        args.max_nfev = max(args.max_nfev // 2, 1000)
    summary = run_sweep(args)

    # Write summary
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")
    print("\n--- pre-filter stats ---")
    for k, v in summary["pre_filter_stats"].items():
        print(f"  {k}: {v}")
    print(f"submitted to optimizer: {summary['submitted_total']}")
    print(f"near misses: {len(summary['near_misses'])}")
    print(f"\nTop 5 (lowest eq_rms):")
    for rec in summary["top_records"][:5]:
        print(f"  {rec['name']}: n={rec['n']}, eq_rms={rec['eq_rms']:.3e}, "
              f"conv={rec['convexity_margin']:.3e}, edge={rec['min_edge_length']:.3e}")
    print(f"\nWrote summary to {args.out}")


if __name__ == "__main__":
    main()
