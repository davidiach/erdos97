#!/usr/bin/env python3
"""
Falsification search engine for Erdős Problem #97.

Target: find a strictly convex n-gon p[0..n-1] and 4-sets S_i such that
|p_i-p_j|^2 is constant over j in S_i for every i.

This script is deliberately research-oriented:
  * incidence-pattern generators,
  * robust convex-polygon parameterizations,
  * numerical minimization with diagnostics,
  * independent verifier,
  * optional SAT-style finite incidence search (uses z3 if installed; fallback random).

Dependencies: numpy, scipy. Optional: sympy, z3-solver.

Example:
  python erdos97_search.py --pattern C12_pm_2_5 --restarts 50 --mode polar --out best.json
  python erdos97_search.py --list-patterns
  python erdos97_search.py --verify best.json
"""
from __future__ import annotations

import argparse
import dataclasses
import itertools
import json
import math
import random
import time
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import least_squares, differential_evolution

Array = NDArray[np.float64]
Pattern = List[List[int]]


@dataclasses.dataclass
class PatternInfo:
    name: str
    n: int
    S: Pattern
    family: str = ""
    formula: str = ""
    notes: str = ""


@dataclasses.dataclass
class LossWeights:
    eq: float = 1.0
    convex: float = 50.0
    edge: float = 10.0
    pair: float = 1.0
    concyclic_avoid: float = 0.0
    angle_gap: float = 0.0


@dataclasses.dataclass
class SearchResult:
    pattern_name: str
    n: int
    mode: str
    loss: float
    eq_rms: float
    max_spread: float
    max_rel_spread: float
    convexity_margin: float
    min_edge_length: float
    min_pair_distance: float
    success: bool
    message: str
    elapsed_sec: float
    seed: int
    x: List[float]
    coordinates: List[List[float]]
    S: Pattern
    distance_table: List[Dict[str, object]]


# ----------------------------- pattern helpers -----------------------------

def modset(i: int, n: int, offsets: Sequence[int]) -> List[int]:
    vals = sorted({(i + o) % n for o in offsets})
    if i in vals or len(vals) != len(offsets):
        raise ValueError(f"bad offsets {offsets} at i={i}, n={n}: {vals}")
    return vals


def circulant_pattern(n: int, offsets: Sequence[int], name: Optional[str] = None) -> PatternInfo:
    S = [modset(i, n, offsets) for i in range(n)]
    if name is None:
        name = f"C{n}_" + "_".join(str(o).replace('-', 'm') for o in offsets)
    return PatternInfo(name=name, n=n, S=S, family="circulant", formula=f"S_i = i + {list(offsets)} mod {n}")


def parity_pattern(n: int, even_offsets: Sequence[int], odd_offsets: Sequence[int], name: str) -> PatternInfo:
    S = [modset(i, n, even_offsets if i % 2 == 0 else odd_offsets) for i in range(n)]
    return PatternInfo(name=name, n=n, S=S, family="period-2", formula=f"even: i+{list(even_offsets)}, odd: i+{list(odd_offsets)} mod {n}")


def block_pattern(m: int, q: int, offsets: Sequence[Tuple[int, int]], name: str) -> PatternInfo:
    """Torus-like pattern on m*q vertices ordered by index a*q+b.

    Vertex i corresponds to (a,b) with a mod m, b mod q. The provided offsets are
    added in this torus and flattened back. This gives incidence designs inspired
    by multi-orbit constructions while still preserving a cyclic order.
    """
    n = m * q
    S: Pattern = []
    for a in range(m):
        for b in range(q):
            i = a * q + b
            vals = []
            for da, db in offsets:
                aa = (a + da) % m
                bb = (b + db) % q
                vals.append(aa * q + bb)
            vals = sorted(set(vals))
            if i in vals or len(vals) != len(offsets):
                raise ValueError(f"bad block offsets at {(a,b)} -> {vals}")
            S.append(vals)
    return PatternInfo(name=name, n=n, S=S, family=f"block-{m}x{q}", formula=f"i=(a,b), S_i=(a,b)+{list(offsets)} mod ({m},{q})")


def random_pattern(n: int, rng: random.Random, max_pair_common: int = 2, balanced: bool = True,
                   max_tries: int = 100000, name: str = "random") -> PatternInfo:
    """Generate a random 4-out pattern with pairwise |S_a cap S_b| <= max_pair_common.

    If balanced=True, keep indegrees near 4 using a soft greedy objective.
    """
    if max_tries <= 0:
        raise ValueError(f"max_tries must be positive, got {max_tries}")

    for _ in range(max_tries):
        S: Pattern = [[] for _ in range(n)]
        indeg = [0] * n
        failed = False
        for i in range(n):
            candidates = [j for j in range(n) if j != i]
            ok_sets = []
            for comb in itertools.combinations(candidates, 4):
                ss = set(comb)
                if all(len(ss.intersection(S[a])) <= max_pair_common for a in range(i)):
                    score = sum((indeg[j] + 1 - 4) ** 2 - (indeg[j] - 4) ** 2 for j in comb) if balanced else 0
                    # Discourage four clustered choices on one side in cyclic order.
                    gaps = cyclic_gaps(sorted(comb), n)
                    cluster_penalty = max(gaps)  # if max gap huge, selected points are clustered
                    ok_sets.append((score + 0.02 * cluster_penalty + rng.random() * 1e-3, list(comb)))
            if not ok_sets:
                failed = True
                break
            ok_sets.sort(key=lambda t: t[0])
            # Pick from a small elite set for diversity.
            chosen = rng.choice(ok_sets[: min(50, len(ok_sets))])[1]
            S[i] = sorted(chosen)
            for j in chosen:
                indeg[j] += 1
        if not failed:
            return PatternInfo(
                name=name,
                n=n,
                S=S,
                family="random-greedy",
                formula="greedy random 4-out, pairwise common-neighbor cap",
            )

    raise RuntimeError(f"random_pattern failed after {max_tries} attempts; try larger n or max_pair_common")


def cyclic_gaps(vals: Sequence[int], n: int) -> List[int]:
    vals = sorted(vals)
    return [((vals[(k + 1) % len(vals)] - vals[k]) % n) for k in range(len(vals))]


def built_in_patterns() -> Dict[str, PatternInfo]:
    pats: List[PatternInfo] = []
    # Balanced two-chord circulants: selected vertices lie on both sides of the center.
    pats.append(circulant_pattern(9, [-4, -2, 2, 4], "C9_pm_2_4"))
    pats.append(circulant_pattern(12, [-5, -2, 2, 5], "C12_pm_2_5"))
    pats.append(circulant_pattern(13, [-5, -3, 3, 5], "C13_pm_3_5"))
    pats.append(circulant_pattern(16, [-6, -1, 1, 6], "C16_pm_1_6"))
    pats.append(circulant_pattern(20, [-9, -4, 4, 9], "C20_pm_4_9"))
    # Non-palindromic circulants: fewer forced mirror symmetries in coordinates.
    pats.append(circulant_pattern(17, [-7, -2, 4, 8], "C17_skew"))
    pats.append(circulant_pattern(19, [-8, -3, 5, 9], "C19_skew"))
    # Period-2 patterns: keep local balance but break global dihedral rigidity.
    pats.append(parity_pattern(18, [-7, -2, 4, 8], [-8, -4, 2, 7], "P18_parity_balanced"))
    pats.append(parity_pattern(24, [-10, -3, 5, 11], [-11, -5, 3, 10], "P24_parity_balanced"))
    # Multi-orbit/block patterns inspired by Danzer-style layered configurations.
    pats.append(block_pattern(3, 4, [(1, 0), (2, 0), (1, 1), (2, -1)], "B12_3x4_danzer_lift"))
    pats.append(block_pattern(4, 5, [(1, 0), (3, 0), (1, 2), (3, -2)], "B20_4x5_FR_lift"))
    return {p.name: p for p in pats}


# -------------------------- geometry and diagnostics -------------------------

def softmax(z: Array) -> Array:
    z = np.asarray(z, dtype=float)
    z = z - np.max(z)
    e = np.exp(z)
    return e / np.sum(e)


def softplus(x: Array, beta: float = 20.0) -> Array:
    # stable softplus(x) / beta approx max(x, 0)
    bx = beta * x
    return np.where(bx > 40, x, np.log1p(np.exp(bx)) / beta)


def rotate_points(P: Array, theta: float) -> Array:
    c, s = math.cos(theta), math.sin(theta)
    R = np.array([[c, -s], [s, c]], dtype=float)
    return P @ R.T


def normalize_points(P: Array, rotate_gauge: bool = True) -> Array:
    Q = np.asarray(P, dtype=float).copy()
    Q -= Q.mean(axis=0)
    sc = math.sqrt(float(np.mean(np.sum(Q * Q, axis=1))))
    if not np.isfinite(sc) or sc <= 1e-300:
        sc = 1.0
    Q /= sc
    if rotate_gauge:
        # Align p0 to the positive x-axis when possible; otherwise align first edge.
        v = Q[0]
        if np.linalg.norm(v) < 1e-10:
            v = Q[1] - Q[0]
        theta = -math.atan2(float(v[1]), float(v[0]))
        Q = rotate_points(Q, theta)
    return Q


def polygon_area2(P: Array) -> float:
    x, y = P[:, 0], P[:, 1]
    return float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def orient_margins(P: Array) -> Array:
    A = P
    E1 = np.roll(A, -1, axis=0) - A
    E2 = np.roll(A, -2, axis=0) - np.roll(A, -1, axis=0)
    return E1[:, 0] * E2[:, 1] - E1[:, 1] * E2[:, 0]


def pairwise_distances(P: Array) -> Array:
    D = P[:, None, :] - P[None, :, :]
    return np.sqrt(np.sum(D * D, axis=2))


def pairwise_sqdist(P: Array) -> Array:
    D = P[:, None, :] - P[None, :, :]
    return np.sum(D * D, axis=2)


def convexity_margin(P: Array) -> float:
    """Return the strict convexity margin for the supplied cyclic order.

    The margin is the minimum signed area over every directed boundary edge and
    every non-incident vertex. Positive margin means every other vertex lies
    strictly to the same side of each oriented edge.
    """
    Q = np.asarray(P, dtype=float)
    n = len(Q)
    if n < 3:
        return float("-inf")
    if polygon_area2(Q) < 0:
        Q = Q[::-1]
    margins: List[float] = []
    for i in range(n):
        a = Q[i]
        b = Q[(i + 1) % n]
        edge = b - a
        for j in range(n):
            if j == i or j == (i + 1) % n:
                continue
            v = Q[j] - a
            margins.append(float(edge[0] * v[1] - edge[1] * v[0]))
    return min(margins) if margins else float("-inf")


def min_edge_length(P: Array) -> float:
    return float(np.min(np.linalg.norm(np.roll(P, -1, axis=0) - P, axis=1)))


def min_pair_distance(P: Array) -> float:
    D = pairwise_distances(P)
    n = len(P)
    if n < 2:
        return float("inf")
    iu = np.triu_indices(n, 1)
    return float(np.min(D[iu]))


def validate_candidate_shape(P: Array, S: Pattern) -> List[str]:
    """Validate the structural contract for a numerical k=4 candidate."""
    errors: List[str] = []

    if P.ndim != 2 or P.shape[1] != 2:
        errors.append(f"coordinates must have shape (n, 2), got {P.shape}")
        return errors

    if not np.all(np.isfinite(P)):
        errors.append("coordinates contain NaN or infinite values")

    n = int(P.shape[0])
    if n < 5:
        errors.append(f"n must be at least 5, got {n}")

    if len(S) != n:
        errors.append(f"expected {n} witness rows, got {len(S)}")
        return errors

    for i, row in enumerate(S):
        if len(row) != 4:
            errors.append(f"row {i} has length {len(row)}, expected 4")
        if len(set(row)) != len(row):
            errors.append(f"row {i} contains duplicate targets: {row}")
        if i in row:
            errors.append(f"row {i} contains its own center")
        bad = [j for j in row if j < 0 or j >= n]
        if bad:
            errors.append(f"row {i} contains out-of-range targets: {bad}")

    return errors


def independent_diagnostics(P: Array, S: Pattern) -> Dict[str, object]:
    D2 = pairwise_sqdist(P)
    spreads = []
    rel_spreads = []
    rms_terms = []
    table = []
    for i, Si in enumerate(S):
        vals = np.array([D2[i, j] for j in Si], dtype=float)
        spread = float(vals.max() - vals.min())
        mean = float(vals.mean())
        rel = spread / max(abs(mean), 1e-15)
        centered = vals - mean
        spreads.append(spread)
        rel_spreads.append(rel)
        rms_terms.extend(centered.tolist())
        table.append({
            "i": i,
            "S_i": list(map(int, Si)),
            "sqdistances": [float(x) for x in vals],
            "mean_sqdistance": mean,
            "spread": spread,
            "relative_spread": rel,
        })
    return {
        "eq_rms": float(math.sqrt(np.mean(np.square(rms_terms)))) if rms_terms else 0.0,
        "max_spread": float(max(spreads)) if spreads else 0.0,
        "max_rel_spread": float(max(rel_spreads)) if rel_spreads else 0.0,
        "convexity_margin": convexity_margin(P),
        "min_edge_length": min_edge_length(P),
        "min_pair_distance": min_pair_distance(P),
        "area2": polygon_area2(P),
        "distance_table": table,
    }


def empirical_E_values(P: Array, tol: float = 1e-8) -> List[int]:
    """Cluster equal squared distances numerically and return max class size at each vertex."""
    D2 = pairwise_sqdist(P)
    n = len(P)
    out = []
    for i in range(n):
        vals = sorted(D2[i, j] for j in range(n) if j != i)
        best = 1 if n > 1 else 0
        cur = 1
        for a, b in zip(vals, vals[1:]):
            if abs(b - a) <= tol * max(1.0, abs(a), abs(b)):
                cur += 1
            else:
                best = max(best, cur)
                cur = 1
        best = max(best, cur)
        out.append(best)
    return out


# --------------------------- parameterizations ------------------------------

def polygon_from_polar_x(x: Array, n: int) -> Array:
    z = np.asarray(x[:n], dtype=float)
    logr = np.asarray(x[n:2 * n], dtype=float)
    gaps = softmax(z) * (2.0 * math.pi)
    theta = np.zeros(n, dtype=float)
    theta[1:] = np.cumsum(gaps[:-1])
    r = np.exp(np.clip(logr, -20, 20))
    P = np.column_stack([r * np.cos(theta), r * np.sin(theta)])
    # If orientation flipped after centering/gauge, keep order but reverse to CCW for diagnostics only.
    return normalize_points(P)


def init_polar_x(n: int, rng: np.random.Generator, jitter: float = 0.20) -> Array:
    gaps = np.ones(n) + jitter * rng.normal(size=n)
    gaps = np.maximum(gaps, 0.05)
    z = np.log(gaps)
    logr = jitter * rng.normal(size=n)
    return np.concatenate([z, logr])


def inverse_polar_x(P: Array) -> Array:
    Q = normalize_points(P, rotate_gauge=False)
    angles = np.unwrap(np.arctan2(Q[:, 1], Q[:, 0]))
    # rotate so first angle is 0 and force increasing by sorting order as given.
    angles = angles - angles[0]
    angles = np.mod(angles, 2 * np.pi)
    # If input order crosses 2pi, unwrap by adding 2pi when needed.
    for k in range(1, len(angles)):
        while angles[k] <= angles[k - 1] + 1e-8:
            angles[k] += 2 * np.pi
    gaps = np.diff(np.r_[angles, angles[0] + 2 * np.pi])
    gaps = np.maximum(gaps, 1e-4)
    z = np.log(gaps)
    r = np.linalg.norm(Q, axis=1)
    logr = np.log(np.maximum(r, 1e-8))
    return np.concatenate([z, logr])


def polygon_from_direct_x(x: Array, n: int) -> Array:
    P = np.asarray(x[:2 * n], dtype=float).reshape(n, 2)
    return normalize_points(P)


def init_direct_x(n: int, rng: np.random.Generator, jitter: float = 0.20) -> Array:
    xpol = init_polar_x(n, rng, jitter=jitter)
    P = polygon_from_polar_x(xpol, n)
    return P.reshape(-1)


def polygon_from_support_x(x: Array, n: int) -> Array:
    """Fixed-normal support parameterization. Conservative but strongly convex.

    Lines are <u_k, X> = h_k with u_k=(cos theta_k, sin theta_k), theta_k=2pi*k/n.
    Vertex k is intersection of lines k and k+1.
    """
    theta = 2.0 * math.pi * np.arange(n) / n
    U = np.column_stack([np.cos(theta), np.sin(theta)])
    h = 0.2 + np.exp(np.clip(np.asarray(x[:n], dtype=float), -20, 20))
    P = np.zeros((n, 2), dtype=float)
    for k in range(n):
        A = np.vstack([U[k], U[(k + 1) % n]])
        b = np.array([h[k], h[(k + 1) % n]])
        P[k] = np.linalg.solve(A, b)
    return normalize_points(P)


def init_support_x(n: int, rng: np.random.Generator, jitter: float = 0.15) -> Array:
    return jitter * rng.normal(size=n)


def polygon_from_x(x: Array, n: int, mode: str) -> Array:
    if mode == "polar":
        return polygon_from_polar_x(x, n)
    if mode == "direct":
        return polygon_from_direct_x(x, n)
    if mode == "support":
        return polygon_from_support_x(x, n)
    raise ValueError(f"unknown mode {mode}")


def init_x(n: int, rng: np.random.Generator, mode: str, jitter: float = 0.20) -> Array:
    if mode == "polar":
        return init_polar_x(n, rng, jitter)
    if mode == "direct":
        return init_direct_x(n, rng, jitter)
    if mode == "support":
        return init_support_x(n, rng, jitter)
    raise ValueError(f"unknown mode {mode}")


# ------------------------------ objective -----------------------------------

def residual_vector(x: Array, n: int, S: Pattern, mode: str, weights: LossWeights,
                    convex_margin: float = 1e-3, min_edge: float = 1e-3,
                    min_pair: float = 1e-3) -> Array:
    P = polygon_from_x(x, n, mode)
    if polygon_area2(P) < 0:
        # preserve cyclic labels if orientation is wrong? For penalties we use signed orientations as is.
        pass
    D2 = pairwise_sqdist(P)
    res: List[Array] = []

    eq_terms = []
    for i, Si in enumerate(S):
        vals = np.array([D2[i, j] for j in Si], dtype=float)
        eq_terms.append(vals - vals.mean())
    if eq_terms:
        res.append(math.sqrt(weights.eq) * np.concatenate(eq_terms))

    # Strict convexity: all consecutive orientation determinants positive.
    ori = orient_margins(P)
    if polygon_area2(P) < 0:
        ori = -ori
    res.append(math.sqrt(weights.convex) * softplus(convex_margin - ori))

    # Edge and pair separation.
    ed = np.linalg.norm(np.roll(P, -1, axis=0) - P, axis=1)
    res.append(math.sqrt(weights.edge) * softplus(min_edge - ed))

    if weights.pair > 0:
        D = pairwise_distances(P)
        iu = np.triu_indices(n, 1)
        res.append(math.sqrt(weights.pair) * softplus(min_pair - D[iu]))

    if weights.concyclic_avoid > 0:
        rr = np.sum(P * P, axis=1)
        # Penalize too-small radial variance around centroid, but only weakly.
        res.append(np.array([math.sqrt(weights.concyclic_avoid) * softplus(1e-3 - float(np.var(rr)))], dtype=float))

    if weights.angle_gap > 0 and mode == "polar":
        gaps = softmax(np.asarray(x[:n])) * (2.0 * math.pi)
        res.append(math.sqrt(weights.angle_gap) * softplus((2.0 * math.pi / n) * 0.03 - gaps))

    return np.concatenate(res) if res else np.zeros(0)


def equality_only_loss(P: Array, S: Pattern) -> float:
    D2 = pairwise_sqdist(P)
    terms = []
    for i, Si in enumerate(S):
        vals = np.array([D2[i, j] for j in Si])
        terms.extend((vals - vals.mean()).tolist())
    return float(np.mean(np.square(terms))) if terms else 0.0


# ------------------------------ search --------------------------------------

def search_pattern(pat: PatternInfo, mode: str = "polar", restarts: int = 20,
                   seed: int = 0, max_nfev: int = 3000,
                   weights: Optional[LossWeights] = None,
                   use_de: bool = False, verbose: bool = False) -> SearchResult:
    rng = np.random.default_rng(seed)
    weights = weights or LossWeights()
    n = pat.n
    best = None
    best_x = None
    start = time.time()

    def fun(x: Array) -> Array:
        return residual_vector(x, n, pat.S, mode, weights)

    # Optional global pre-search on a modest box. Often too slow for n>16, but useful for smoke tests.
    if use_de:
        dim = {"support": n, "polar": 2 * n, "direct": 2 * n}[mode]
        bounds = [(-1.5, 1.5)] * dim
        de = differential_evolution(lambda y: float(np.sum(fun(y) ** 2)), bounds, maxiter=80, popsize=8,
                                    polish=False, seed=seed, workers=1, updating="immediate")
        x0s = [de.x]
    else:
        x0s = []

    for r in range(restarts):
        x0s.append(init_x(n, rng, mode, jitter=0.45 if r else 0.10))

    for r, x0 in enumerate(x0s):
        try:
            sol = least_squares(fun, x0, method="trf", max_nfev=max_nfev, x_scale="jac",
                                ftol=1e-11, xtol=1e-11, gtol=1e-11)
            score = float(np.sum(sol.fun ** 2))
            if best is None or score < best[0]:
                best = (score, sol)
                best_x = sol.x.copy()
                if verbose:
                    P = polygon_from_x(best_x, n, mode)
                    diag = independent_diagnostics(P, pat.S)
                    print(f"restart {r}: score={score:.3e} max_spread={diag['max_spread']:.3e} conv={diag['convexity_margin']:.3e}", flush=True)
        except Exception as e:
            if verbose:
                print(f"restart {r} failed: {e}", flush=True)
            continue

    if best is None or best_x is None:
        raise RuntimeError("all restarts failed")
    P = polygon_from_x(best_x, n, mode)
    # If overall orientation is clockwise, flip coordinates and relabel S accordingly? We do not relabel;
    # the generated polar order should be CCW unless centering causes numerical area flip. Report as is.
    diag = independent_diagnostics(P, pat.S)
    elapsed = time.time() - start
    return SearchResult(
        pattern_name=pat.name,
        n=n,
        mode=mode,
        loss=float(best[0]),
        eq_rms=float(diag["eq_rms"]),
        max_spread=float(diag["max_spread"]),
        max_rel_spread=float(diag["max_rel_spread"]),
        convexity_margin=float(diag["convexity_margin"]),
        min_edge_length=float(diag["min_edge_length"]),
        min_pair_distance=float(diag["min_pair_distance"]),
        success=bool(best[1].success),
        message=str(best[1].message),
        elapsed_sec=float(elapsed),
        seed=int(seed),
        x=[float(v) for v in best_x],
        coordinates=[[float(a), float(b)] for a, b in P],
        S=[[int(j) for j in row] for row in pat.S],
        distance_table=diag["distance_table"],
    )


def result_to_json(result: SearchResult) -> Dict[str, object]:
    return dataclasses.asdict(result)


def load_json_result(path: str) -> Tuple[Array, Pattern]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    P = np.array(data["coordinates"], dtype=float)
    S = [[int(j) for j in row] for row in data["S"]]
    return P, S


def verify_json(path: str, tol: float = 1e-8, min_margin: float = 1e-8) -> Dict[str, object]:
    P_raw, S = load_json_result(path)
    validation_errors = validate_candidate_shape(P_raw, S)

    if validation_errors:
        return {
            "ok_at_tol": False,
            "tol": tol,
            "min_margin": min_margin,
            "validation_errors": validation_errors,
            "empirical_E_values": [],
        }

    # Distance equalities are scale invariant; normalize before applying any
    # absolute spread tolerance so tiny malformed inputs cannot pass.
    P = normalize_points(P_raw)
    diag = independent_diagnostics(P, S)
    E = empirical_E_values(P, tol=tol)
    ok = bool(
        diag["max_spread"] <= tol
        and diag["max_rel_spread"] <= tol
        and diag["convexity_margin"] > min_margin
        and diag["min_pair_distance"] > min_margin
    )
    return {
        "ok_at_tol": ok,
        "tol": tol,
        "min_margin": min_margin,
        "validation_errors": validation_errors,
        "empirical_E_values": E,
        **diag,
    }


# ------------------------- finite/SAT-style abstraction ----------------------

def incidence_obstruction_stats(S: Pattern) -> Dict[str, object]:
    n = len(S)
    indeg = [0] * n
    for row in S:
        for j in row:
            indeg[j] += 1
    max_common = 0
    pairs_over_2 = []
    for a in range(n):
        for b in range(a + 1, n):
            c = len(set(S[a]).intersection(S[b]))
            max_common = max(max_common, c)
            if c > 2:
                pairs_over_2.append((a, b, c))
    cluster_scores = []
    for i, row in enumerate(S):
        gaps = cyclic_gaps(row, n)
        cluster_scores.append(max(gaps))
    reciprocals = sum(1 for i in range(n) for j in S[i] if i in S[j]) // 2
    return {
        "n": n,
        "indegree_min": min(indeg),
        "indegree_max": max(indeg),
        "indegree": indeg,
        "max_common_selected_neighbors": max_common,
        "pairs_with_common_gt_2": pairs_over_2[:20],
        "num_pairs_common_gt_2": len(pairs_over_2),
        "max_cluster_gap_mean": float(np.mean(cluster_scores)),
        "max_cluster_gap_max": int(max(cluster_scores)),
        "reciprocal_edge_pairs": reciprocals,
    }


def z3_incidence_search(n: int, max_pair_common: int = 2, balance_indegree: bool = True,
                        symmetry_break: bool = True) -> Optional[Pattern]:
    """SAT-style incidence search.

    Requires z3-solver. It proves only existence/nonexistence of a Boolean incidence
    matrix satisfying the chosen finite constraints; it says nothing directly about
    Euclidean realizability.
    """
    try:
        import z3  # type: ignore
    except Exception as e:
        raise RuntimeError("z3-solver is not installed. pip install z3-solver to use this.") from e

    X = [[z3.Bool(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    s = z3.Solver()
    for i in range(n):
        s.add(z3.Not(X[i][i]))
        s.add(z3.PbEq([(X[i][j], 1) for j in range(n)], 4))
    # Two centers cannot share >2 selected vertices: circle intersection necessary condition.
    for a in range(n):
        for b in range(a + 1, n):
            s.add(z3.PbLe([(z3.And(X[a][j], X[b][j]), 1) for j in range(n)], max_pair_common))
    if balance_indegree:
        for j in range(n):
            s.add(z3.PbGe([(X[i][j], 1) for i in range(n)], 2))
            s.add(z3.PbLe([(X[i][j], 1) for i in range(n)], 6))
    if symmetry_break:
        # Anchor row 0 to a balanced four-set; harmless only for searching a subclass.
        anchor = {n // 5, 2 * n // 5, 3 * n // 5, 4 * n // 5}
        for j in range(n):
            s.add(X[0][j] == (j in anchor and j != 0))
    if s.check() != z3.sat:
        return None
    m = s.model()
    return [[j for j in range(n) if bool(m.evaluate(X[i][j]))] for i in range(n)]


def _load_catalog_status() -> Dict[str, Dict[str, object]]:
    """Best-effort load of pattern status from data/patterns/candidate_patterns.json.

    Returns ``{}`` if the file is absent or malformed; the caller treats
    missing entries as having no recorded status.
    """
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.normpath(os.path.join(here, "..", "..", "data", "patterns", "candidate_patterns.json")),
        os.path.normpath(os.path.join(os.getcwd(), "data", "patterns", "candidate_patterns.json")),
    ]
    for path in candidates:
        try:
            with open(path, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        return {entry["name"]: entry for entry in entries if "name" in entry}
    return {}


def write_certificate_template(path: str, result: SearchResult) -> None:
    """Write a machine-readable certificate skeleton for later exactification."""
    cert = {
        "type": "erdos97_candidate_certificate_v0",
        "status": "numerical_only_not_a_proof",
        "n": result.n,
        "pattern_name": result.pattern_name,
        "S": result.S,
        "coordinates_float": result.coordinates,
        "normalization": "centroid zero, mean squared radius one, p0 rotation gauge",
        "required_exact_data": {
            "coordinate_field": "e.g. QQ(sqrt(d)) or algebraic number field",
            "coordinates_exact": None,
            "orientation_determinants_positive": None,
            "distance_equalities_zero": None,
            "verification_script": None,
        },
        "numerical_diagnostics": {
            "loss": result.loss,
            "eq_rms": result.eq_rms,
            "max_spread": result.max_spread,
            "max_rel_spread": result.max_rel_spread,
            "convexity_margin": result.convexity_margin,
            "min_edge_length": result.min_edge_length,
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cert, f, indent=2)


# ------------------------------ CLI -----------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list-patterns", action="store_true")
    ap.add_argument("--pattern", default="C12_pm_2_5")
    ap.add_argument("--mode", choices=["polar", "direct", "support"], default="polar")
    ap.add_argument("--restarts", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-nfev", type=int, default=3000)
    ap.add_argument("--out", default="")
    ap.add_argument("--certificate", default="")
    ap.add_argument("--use-de", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--verify", default="")
    ap.add_argument("--tol", type=float, default=1e-8)
    ap.add_argument("--min-margin", type=float, default=1e-8)
    args = ap.parse_args()

    pats = built_in_patterns()
    if args.list_patterns:
        catalog_status = _load_catalog_status()
        for p in pats.values():
            stats = incidence_obstruction_stats(p.S)
            print(f"{p.name}: n={p.n}, family={p.family}, formula={p.formula}")
            print(f"  stats: max_common={stats['max_common_selected_neighbors']}, indeg=[{stats['indegree_min']},{stats['indegree_max']}], cluster_gap_mean={stats['max_cluster_gap_mean']:.2f}")
            entry = catalog_status.get(p.name)
            if entry is not None:
                retired_by = entry.get("retired_by")
                tag = "RETIRED" if retired_by else entry.get("trust", "live")
                print(f"  status: {tag} - {entry.get('status', '')}")
                if retired_by:
                    print(f"  retired_by: {retired_by}")
        return

    if args.verify:
        diag = verify_json(args.verify, tol=args.tol, min_margin=args.min_margin)
        print(json.dumps(diag, indent=2))
        return

    if args.pattern not in pats:
        raise SystemExit(f"unknown pattern {args.pattern}; use --list-patterns")
    pat = pats[args.pattern]
    result = search_pattern(pat, mode=args.mode, restarts=args.restarts, seed=args.seed,
                            max_nfev=args.max_nfev, use_de=args.use_de, verbose=args.verbose)
    data = result_to_json(result)
    print(json.dumps({k: data[k] for k in [
        "pattern_name", "n", "mode", "loss", "eq_rms", "max_spread", "max_rel_spread",
        "convexity_margin", "min_edge_length", "min_pair_distance", "success", "elapsed_sec"]}, indent=2))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"wrote {args.out}")
    if args.certificate:
        write_certificate_template(args.certificate, result)
        print(f"wrote {args.certificate}")


if __name__ == "__main__":
    main()
