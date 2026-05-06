#!/usr/bin/env python3
"""Simulated-annealing / random-walk counterexample search for Erdős #97.

The script searches strictly convex n-gons (n in {11..15}) for configurations
in which every vertex has 4 others equidistant -- i.e. a counterexample to
Erdős Problem #97. We use a hard convex feasibility region and a Metropolis-
Hastings-style random walk on coordinates, followed by SLSQP refinement once
the random walk has discovered a coherent selected-witness incidence pattern.

Usage:

  python scripts/anneal_search.py --n 11 --seeds 100 \
      --out data/runs/2026-05-06/anneal_n11.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import numpy as np
from scipy.optimize import minimize

from erdos97.search import (
    convexity_margin,
    convexity_margins,
    independent_diagnostics,
    min_edge_length,
    min_pair_distance,
    normalize_points,
    pairwise_sqdist,
    polygon_area2,
    validate_candidate_shape,
)


# ---------------------------------------------------------------------------
# Initial configurations
# ---------------------------------------------------------------------------

def regular_polygon(n: int, radius: float = 1.0) -> np.ndarray:
    angles = 2.0 * math.pi * np.arange(n) / n
    return np.column_stack([radius * np.cos(angles), radius * np.sin(angles)])


def two_radius_polygon(n: int, r1: float = 1.0, r2: float = 1.05) -> np.ndarray:
    angles = 2.0 * math.pi * np.arange(n) / n
    radii = np.where(np.arange(n) % 2 == 0, r1, r2)
    return np.column_stack([radii * np.cos(angles), radii * np.sin(angles)])


def three_radius_polygon(n: int, radii: Sequence[float] = (1.0, 1.05, 0.97)) -> np.ndarray:
    angles = 2.0 * math.pi * np.arange(n) / n
    rr = np.array([radii[i % 3] for i in range(n)], dtype=float)
    return np.column_stack([rr * np.cos(angles), rr * np.sin(angles)])


def regular_with_one_perturbed(n: int, idx: int, dx: float, dy: float) -> np.ndarray:
    pts = regular_polygon(n)
    pts[idx, 0] += dx
    pts[idx, 1] += dy
    return pts


def initial_configuration(kind: str, n: int, rng: np.random.Generator) -> np.ndarray:
    sigma = 0.01
    if kind == "regular":
        base = regular_polygon(n)
    elif kind == "regular_one_moved":
        base = regular_with_one_perturbed(n, idx=0, dx=0.05, dy=-0.03)
    elif kind == "two_radius":
        base = two_radius_polygon(n, r1=1.0, r2=1.04)
    elif kind == "three_radius":
        base = three_radius_polygon(n, radii=(1.0, 1.05, 0.97))
    else:
        raise ValueError(f"unknown init kind: {kind}")
    base = base + rng.normal(scale=sigma, size=base.shape)
    return base


# ---------------------------------------------------------------------------
# Witness selection and cost
# ---------------------------------------------------------------------------

def _pairwise_sqdist_fast(P: np.ndarray) -> np.ndarray:
    diff = P[:, None, :] - P[None, :, :]
    return np.einsum("ijk,ijk->ij", diff, diff)


def closest_4_witnesses_from_D2(D2: np.ndarray) -> tuple[list[list[int]], float]:
    """Slide a 4-window over sorted squared distances per row; return chosen
    indices and per-vertex max spread."""
    n = D2.shape[0]
    D2c = D2.copy()
    np.fill_diagonal(D2c, np.inf)
    order = np.argsort(D2c, axis=1)
    sorted_D2 = np.take_along_axis(D2c, order, axis=1)
    sorted_D2 = sorted_D2[:, : n - 1]
    order = order[:, : n - 1]
    if sorted_D2.shape[1] < 4:
        return [sorted(map(int, order[i, :4])) for i in range(n)], float("inf")
    spreads = sorted_D2[:, 3:] - sorted_D2[:, :-3]
    best_lo = np.argmin(spreads, axis=1)
    rows = order[np.arange(n)[:, None], best_lo[:, None] + np.arange(4)[None, :]]
    chosen = [sorted(map(int, rows[i])) for i in range(n)]
    worst = float(spreads[np.arange(n), best_lo].max())
    return chosen, worst


def fast_convex_margins(P: np.ndarray) -> np.ndarray:
    """Vectorized strict-convexity margins: n*(n-2) entries."""
    n = len(P)
    a = P
    b = np.roll(P, -1, axis=0)
    edge = b - a  # (n, 2)
    diff = P[None, :, :] - a[:, None, :]  # (n, n, 2)
    cross = edge[:, None, 0] * diff[:, :, 1] - edge[:, None, 1] * diff[:, :, 0]
    sign = -1.0 if (
        np.dot(P[:, 0], np.roll(P[:, 1], -1)) - np.dot(P[:, 1], np.roll(P[:, 0], -1))
    ) < 0 else 1.0
    cross = sign * cross
    idx = np.arange(n)
    mask = np.ones((n, n), dtype=bool)
    mask[idx, idx] = False
    mask[idx, (idx + 1) % n] = False
    return cross[mask]


def closest_4_witnesses(P: np.ndarray) -> list[list[int]]:
    D2 = _pairwise_sqdist_fast(P)
    chosen, _ = closest_4_witnesses_from_D2(D2)
    return chosen


def per_vertex_min_spread(P: np.ndarray) -> tuple[float, list[list[int]]]:
    D2 = _pairwise_sqdist_fast(P)
    chosen, spread = closest_4_witnesses_from_D2(D2)
    return spread, chosen


def convex_feasible(P: np.ndarray, eps: float = 0.0) -> bool:
    margins = fast_convex_margins(P)
    return bool(margins.size and margins.min() > eps)


def cost_of(P: np.ndarray, conv_lambda: float = 1000.0) -> tuple[float, list[list[int]], float]:
    D2 = _pairwise_sqdist_fast(P)
    chosen, spread = closest_4_witnesses_from_D2(D2)
    margins = fast_convex_margins(P)
    margin_min = float(margins.min()) if margins.size else float("-inf")
    convex_violation = max(0.0, -margin_min)
    return spread + conv_lambda * convex_violation, chosen, margin_min


# ---------------------------------------------------------------------------
# Metropolis-Hastings random walk with hard convexity
# ---------------------------------------------------------------------------

@dataclass
class WalkResult:
    cost: float
    spread: float
    margin: float
    P: np.ndarray
    S: list[list[int]]
    accepted: int
    proposed: int
    rejected_convex: int


def random_walk(
    P0: np.ndarray,
    *,
    rng: np.random.Generator,
    steps: int = 20000,
    init_step: float = 0.05,
    final_step: float = 1e-4,
    init_temp: float = 0.2,
    final_temp: float = 1e-6,
    conv_lambda: float = 1000.0,
) -> WalkResult:
    n = len(P0)
    P = P0.copy()
    if not convex_feasible(P):
        # Try to pull back to feasibility by averaging with regular n-gon.
        for alpha in (0.5, 0.25, 0.1, 0.0):
            test = alpha * P + (1.0 - alpha) * regular_polygon(n)
            if convex_feasible(test):
                P = test
                break
        else:
            return WalkResult(float("inf"), float("inf"), -1.0, P, [], 0, 0, 0)

    cost, S, margin = cost_of(P, conv_lambda)
    best_cost = cost
    best_P = P.copy()
    best_S = S
    best_margin = margin
    accepted = 0
    proposed = 0
    rej_convex = 0

    for step in range(steps):
        frac = step / max(1, steps - 1)
        sigma = init_step * (final_step / init_step) ** frac
        T = init_temp * (final_temp / init_temp) ** frac

        i = int(rng.integers(0, n))
        delta = rng.normal(scale=sigma, size=2)
        candidate = P.copy()
        candidate[i] += delta
        proposed += 1
        if not convex_feasible(candidate):
            rej_convex += 1
            continue
        new_cost, new_S, new_margin = cost_of(candidate, conv_lambda)
        dC = new_cost - cost
        if dC <= 0.0 or rng.random() < math.exp(-dC / max(T, 1e-30)):
            P = candidate
            cost = new_cost
            S = new_S
            margin = new_margin
            accepted += 1
            if cost < best_cost:
                best_cost = cost
                best_P = P.copy()
                best_S = S
                best_margin = margin

    spread, _ = per_vertex_min_spread(best_P)
    return WalkResult(
        cost=best_cost,
        spread=spread,
        margin=best_margin,
        P=best_P,
        S=best_S,
        accepted=accepted,
        proposed=proposed,
        rejected_convex=rej_convex,
    )


# ---------------------------------------------------------------------------
# SLSQP refinement on the discovered selected-witness pattern
# ---------------------------------------------------------------------------

def equality_residual(P: np.ndarray, S: Sequence[Sequence[int]]) -> np.ndarray:
    D2 = pairwise_sqdist(P)
    terms: list[np.ndarray] = []
    for i, row in enumerate(S):
        vals = np.array([D2[i, j] for j in row], dtype=float)
        terms.append(vals - vals.mean())
    return np.concatenate(terms) if terms else np.zeros(0)


def slsqp_refine(P0: np.ndarray, S: Sequence[Sequence[int]], *, margin: float = 1e-3,
                 max_iter: int = 400) -> tuple[np.ndarray, float, dict]:
    n = len(P0)
    x0 = P0.flatten().astype(float)
    # Build (edge, vertex) index list once.
    edge_vertex_pairs = [
        (i, j)
        for i in range(n)
        for j in range(n)
        if j != i and j != (i + 1) % n
    ]

    # ---- equality residual & Jacobian (for the loss = ||r||^2) ----
    # Each row i contributes 4 residuals r_{i,k} = D2[i, S[i][k]] - mean_j(D2[i, S[i][j]])
    # Jacobian rows are computed in closed form.
    rows_S = [list(map(int, row)) for row in S]

    def eq_residuals_and_jac(P: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        D2 = _pairwise_sqdist_fast(P)
        m = 4 * n
        r = np.zeros(m, dtype=float)
        # Jacobian shape (m, 2n)
        J = np.zeros((m, 2 * n), dtype=float)
        idx = 0
        for i, row in enumerate(rows_S):
            vals = np.array([D2[i, j] for j in row], dtype=float)
            mean = vals.mean()
            r[idx:idx + 4] = vals - mean
            # d D2[i, j] / d P[a, c] = 2*(P[i,c] - P[j,c]) if a==i, -2*(P[i,c] - P[j,c]) if a==j, 0 else
            # Build dD2 rows for j in row
            dvals = np.zeros((4, 2 * n), dtype=float)
            for k, j in enumerate(row):
                d = P[i] - P[j]
                dvals[k, 2 * i: 2 * i + 2] = 2.0 * d
                dvals[k, 2 * j: 2 * j + 2] = -2.0 * d
            mean_j = dvals.mean(axis=0)
            J[idx:idx + 4] = dvals - mean_j[None, :]
            idx += 4
        return r, J

    def loss_and_grad(x: np.ndarray) -> tuple[float, np.ndarray]:
        P = x.reshape(n, 2)
        r, J = eq_residuals_and_jac(P)
        loss = float(np.dot(r, r))
        grad = 2.0 * J.T @ r
        return loss, grad

    def loss(x: np.ndarray) -> float:
        return loss_and_grad(x)[0]

    def loss_jac(x: np.ndarray) -> np.ndarray:
        return loss_and_grad(x)[1]

    # ---- convexity constraint & analytic Jacobian ----
    # g_e = sign * ((P[i+1]-P[i]) x (P[j]-P[i])) - margin
    # Sign is fixed across the polygon (we'll evaluate per-call).
    sign0 = 1.0 if polygon_area2(P0) >= 0 else -1.0

    def convex_value_and_jac(P: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        # Evaluate vectorized.
        n_pairs = len(edge_vertex_pairs)
        vals = np.zeros(n_pairs, dtype=float)
        J = np.zeros((n_pairs, 2 * n), dtype=float)
        # Determine sign from current P (allow flipping mid-search).
        sign = 1.0 if polygon_area2(P) >= 0 else -1.0
        for k, (i, j) in enumerate(edge_vertex_pairs):
            ip1 = (i + 1) % n
            ax, ay = P[i]
            bx, by = P[ip1]
            cx, cy = P[j]
            dxe, dye = bx - ax, by - ay  # edge
            dxv, dyv = cx - ax, cy - ay  # vertex offset
            cross = dxe * dyv - dye * dxv
            vals[k] = sign * cross - margin
            # Partial derivatives w.r.t. (P[i], P[i+1], P[j]):
            # d cross / d P[i] = (dye - dyv, dxv - dxe)  [from chain rule]
            # d cross / d P[i+1] = (dyv, -dxv)
            # d cross / d P[j] = (-dye, dxe)
            J[k, 2 * i] = sign * (dye - dyv)
            J[k, 2 * i + 1] = sign * (dxv - dxe)
            J[k, 2 * ip1] = sign * dyv
            J[k, 2 * ip1 + 1] = sign * (-dxv)
            J[k, 2 * j] = sign * (-dye)
            J[k, 2 * j + 1] = sign * dxe
        return vals, J

    def convexity_constraint(x: np.ndarray) -> np.ndarray:
        P = x.reshape(n, 2)
        return convex_value_and_jac(P)[0]

    def convexity_jac(x: np.ndarray) -> np.ndarray:
        P = x.reshape(n, 2)
        return convex_value_and_jac(P)[1]

    # ---- edge constraint & Jacobian: ||P[i+1]-P[i]|| - margin >= 0 ----
    def edge_value_and_jac(P: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        diff = np.roll(P, -1, axis=0) - P  # (n, 2)
        lens = np.linalg.norm(diff, axis=1)
        vals = lens - margin
        J = np.zeros((n, 2 * n), dtype=float)
        for i in range(n):
            ip1 = (i + 1) % n
            L = lens[i]
            if L < 1e-15:
                continue
            J[i, 2 * i: 2 * i + 2] = -diff[i] / L
            J[i, 2 * ip1: 2 * ip1 + 2] = diff[i] / L
        return vals, J

    def edge_constraint(x: np.ndarray) -> np.ndarray:
        P = x.reshape(n, 2)
        return edge_value_and_jac(P)[0]

    def edge_jac(x: np.ndarray) -> np.ndarray:
        P = x.reshape(n, 2)
        return edge_value_and_jac(P)[1]

    constraints = [
        {"type": "ineq", "fun": convexity_constraint, "jac": convexity_jac},
        {"type": "ineq", "fun": edge_constraint, "jac": edge_jac},
    ]

    try:
        result = minimize(
            loss,
            x0,
            jac=loss_jac,
            method="SLSQP",
            constraints=constraints,
            options={"maxiter": max_iter, "ftol": 1e-10, "disp": False},
        )
    except Exception as exc:
        return P0, float("inf"), {"refine_error": str(exc)}

    P_refined = result.x.reshape(n, 2)
    diag = {
        "slsqp_loss": float(result.fun),
        "slsqp_message": str(result.message),
        "slsqp_status": int(result.status),
        "slsqp_success": bool(result.success),
    }
    if not np.all(np.isfinite(P_refined)):
        return P0, float("inf"), diag
    return P_refined, float(result.fun), diag


# ---------------------------------------------------------------------------
# Validation / acceptance gates
# ---------------------------------------------------------------------------

@dataclass
class Reject:
    reason: str


def validate_final(P: np.ndarray, S: Sequence[Sequence[int]]) -> str | None:
    """Return rejection reason or None if the candidate clears acceptance gates."""
    n = len(P)
    if min_pair_distance(P) < 0.01:
        return "collapse_to_clusters"
    margin = convexity_margin(P)
    if margin <= 0:
        return f"non_convex_margin={margin:.3e}"
    # Reject solutions whose multiplicities (number of "tied" 4-targets) drop below 4.
    D2 = pairwise_sqdist(P)
    for i, row in enumerate(S):
        vals = sorted(float(D2[i, j]) for j in row)
        spread = vals[-1] - vals[0]
        if spread > 1e-3:
            return f"row_{i}_spread_{spread:.3e}_above_1e-3"
        if len(set(row)) != 4:
            return f"row_{i}_not_unique"
    errs = validate_candidate_shape(P, [list(r) for r in S])
    if errs:
        return f"shape_errors:{';'.join(errs[:2])}"
    return None


# ---------------------------------------------------------------------------
# Top-level driver
# ---------------------------------------------------------------------------

INIT_KINDS = ("regular", "regular_one_moved", "two_radius", "three_radius")


def run_for_n(n: int, seeds: int, *, steps: int, conv_lambda: float,
              verbose: bool = False) -> dict:
    rng_master = np.random.default_rng(20260506 + 1000 * n)
    history: list[dict] = []
    pattern_tabulation: dict[str, int] = {}
    best_overall: dict | None = None
    start = time.time()

    init_kinds = INIT_KINDS

    for trial in range(seeds):
        kind = init_kinds[trial % len(init_kinds)]
        seed = int(rng_master.integers(1, 2**31 - 1))
        rng = np.random.default_rng(seed)
        try:
            P0 = initial_configuration(kind, n, rng)
        except Exception as exc:
            history.append({
                "trial": trial,
                "init_kind": kind,
                "seed": seed,
                "error": f"init_failed: {exc}",
            })
            continue
        walk = random_walk(
            P0,
            rng=rng,
            steps=steps,
            conv_lambda=conv_lambda,
        )
        if not np.all(np.isfinite(walk.P)) or walk.cost == float("inf"):
            history.append({
                "trial": trial,
                "init_kind": kind,
                "seed": seed,
                "walk_cost": float("inf"),
                "note": "walk failed to remain feasible",
            })
            continue

        # Refine via SLSQP on the discovered S (single margin pass).
        best_local: dict | None = None
        for margin in (1e-3,):
            P_ref, refined_loss, refine_meta = slsqp_refine(
                walk.P, walk.S, margin=margin, max_iter=60
            )
            P_norm = normalize_points(P_ref)
            S_after = closest_4_witnesses(P_norm)
            try:
                diag = independent_diagnostics(P_norm, S_after)
            except Exception as exc:
                diag = {"diag_error": str(exc)}
            entry = {
                "trial": trial,
                "init_kind": kind,
                "seed": seed,
                "margin_target": margin,
                "walk_cost": float(walk.cost),
                "walk_spread": float(walk.spread),
                "walk_margin": float(walk.margin),
                "refined_loss": float(refined_loss),
                "diag": {k: (v if not isinstance(v, list) else v) for k, v in diag.items()
                         if k in ("eq_rms", "max_spread", "max_rel_spread",
                                  "convexity_margin", "min_edge_length",
                                  "min_pair_distance", "area2")},
                "S_walk": [list(r) for r in walk.S],
                "S_after": [list(r) for r in S_after],
                "refine_meta": refine_meta,
                "accepted_walk_steps": walk.accepted,
                "rejected_convex_steps": walk.rejected_convex,
            }
            reject = validate_final(P_norm, S_after)
            entry["rejection"] = reject
            if best_local is None or float(diag.get("max_spread", float("inf"))) < float(
                best_local["diag"].get("max_spread", float("inf"))
            ):
                best_local = entry
                best_local["coordinates"] = P_norm.tolist()

        history.append(best_local)
        # Tabulate the pattern from the walk (offset signature)
        sig = pattern_signature(walk.S, n)
        pattern_tabulation[sig] = pattern_tabulation.get(sig, 0) + 1

        # Track best overall (lowest max_spread among non-rejected entries; else lowest spread)
        score = best_local["diag"].get("max_spread", float("inf"))
        if (best_overall is None
            or (best_local["rejection"] is None
                and (best_overall.get("rejection") is not None
                     or score < best_overall["diag"].get("max_spread", float("inf"))))
            or (best_overall.get("rejection") is None
                and best_local["rejection"] is None
                and score < best_overall["diag"].get("max_spread", float("inf")))):
            # Replace best_overall when:
            # - we currently have a rejected best and this one is non-rejected; OR
            # - both are non-rejected but this one has lower max_spread; OR
            # - both are rejected: take the smaller spread anyway
            if best_overall is None:
                best_overall = best_local
            elif best_overall.get("rejection") is not None and best_local["rejection"] is None:
                best_overall = best_local
            elif (best_overall.get("rejection") is None) == (best_local["rejection"] is None):
                if score < best_overall["diag"].get("max_spread", float("inf")):
                    best_overall = best_local

        if verbose and trial % 20 == 0:
            print(f"  n={n} trial={trial} kind={kind} walk_spread={walk.spread:.3e} "
                  f"best max_spread={best_overall['diag'].get('max_spread') if best_overall else None}",
                  flush=True)

    elapsed = time.time() - start
    return {
        "n": n,
        "seeds": seeds,
        "steps": steps,
        "conv_lambda": conv_lambda,
        "elapsed_sec": elapsed,
        "init_kinds": list(INIT_KINDS),
        "best": best_overall,
        "pattern_signatures": pattern_tabulation,
        "history": history,
    }


def pattern_signature(S: Sequence[Sequence[int]], n: int) -> str:
    """Compute a translation-invariant offset signature of the witness pattern.

    For each vertex i, list (j - i) mod n for j in S_i, sorted.
    Then list rows in canonical (sorted-tuple) form.
    """
    rows = []
    for i, row in enumerate(S):
        offsets = sorted(((int(j) - i) % n) for j in row)
        rows.append(tuple(offsets))
    # Canonicalise by lex-sorting the row multiset
    rows_sorted = sorted(rows)
    return ";".join(",".join(str(x) for x in r) for r in rows_sorted)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--seeds", type=int, default=120)
    parser.add_argument("--steps", type=int, default=8000)
    parser.add_argument("--conv-lambda", type=float, default=1000.0)
    parser.add_argument("--out", type=str, required=True)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    result = run_for_n(args.n, args.seeds,
                       steps=args.steps, conv_lambda=args.conv_lambda,
                       verbose=args.verbose)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=False), encoding="utf-8")
    print(f"wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
