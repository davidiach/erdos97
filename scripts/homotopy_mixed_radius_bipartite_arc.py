#!/usr/bin/env python3
"""Mixed-radius bipartite-arc homotopy diagnostic for Erdos Problem #97.

This is a numerical diagnostic, not a proof and not a counterexample claim.
It implements a two-arc, bipartite family motivated by Fishburn--Reeds k=3
seed geometry and the repository B20_4x5_FR_lift incidence scaffold.

The endpoint t=1 imposes four selected witnesses per center with independent
per-center radii rho_i.  The continuation gate checks strict convexity margin
and minimum edge length before looking at residuals.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import List
import numpy as np
from scipy.optimize import least_squares

Array = np.ndarray
Pattern = List[List[int]]
N, M, EPS = 20, 10, 0.15
BOUNDARY_FROM_TORUS = [
    0,
    1,
    2,
    3,
    4,
    10,
    11,
    12,
    13,
    14,
    19,
    18,
    17,
    16,
    15,
    9,
    8,
    7,
    6,
    5,
]
B20_OFFSETS = [(1, 0), (3, 0), (1, 2), (3, -2)]
INVERSE_OFFSET = {0: 1, 1: 0, 2: 3, 3: 2}


def softmax(z: Array) -> Array:
    z = np.asarray(z, dtype=float)
    z = z - np.max(z)
    e = np.exp(z)
    return e / e.sum()


def torus_label(a: int, b: int) -> int:
    return (a % 4) * 5 + (b % 5)


def b20_torus_pattern() -> Pattern:
    return [
        [torus_label(a + da, b + db) for da, db in B20_OFFSETS]
        for a in range(4)
        for b in range(5)
    ]


def relabel_pattern(rows: Pattern, order: list[int]) -> Pattern:
    pos = {old: new for new, old in enumerate(order)}
    out = [[] for _ in rows]
    for old_center, row in enumerate(rows):
        out[pos[old_center]] = [pos[w] for w in row]
    return out


def mixed_radius_pattern() -> Pattern:
    return relabel_pattern(b20_torus_pattern(), BOUNDARY_FROM_TORUS)


def cubic_seed_pattern(match_offset: int) -> Pattern:
    rows = []
    for a in range(4):
        for b in range(5):
            deleted = match_offset if a % 2 == 0 else INVERSE_OFFSET[match_offset]
            rows.append(
                [
                    torus_label(a + da, b + db)
                    for k, (da, db) in enumerate(B20_OFFSETS)
                    if k != deleted
                ]
            )
    return relabel_pattern(rows, BOUNDARY_FROM_TORUS)


def row_overlap_cap(rows: Pattern) -> dict:
    max_common = 0
    bad = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            c = len(set(rows[i]).intersection(rows[j]))
            max_common = max(max_common, c)
            if c > 2:
                bad.append([i, j, c])
    return {
        "max_common": max_common,
        "num_pairs_common_gt_2": len(bad),
        "pairs_common_gt_2": bad[:20],
    }


def polygon_area2(P: Array) -> float:
    x, y = P[:, 0], P[:, 1]
    return float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def normalize_points(P: Array) -> Array:
    Q = np.asarray(P, dtype=float).copy()
    Q -= Q.mean(axis=0)
    sc = math.sqrt(float(np.mean(np.sum(Q * Q, axis=1))))
    if not np.isfinite(sc) or sc <= 1e-300:
        sc = 1.0
    Q /= sc
    v = Q[0]
    if np.linalg.norm(v) < 1e-10:
        v = Q[1] - Q[0]
    th = -math.atan2(float(v[1]), float(v[0]))
    c, s = math.cos(th), math.sin(th)
    return Q @ np.array([[c, -s], [s, c]]).T


def pairwise_sqdist(P: Array) -> Array:
    D = P[:, None, :] - P[None, :, :]
    return np.sum(D * D, axis=2)


def convexity_margins(P: Array) -> Array:
    sign = -1.0 if polygon_area2(P) < 0 else 1.0
    vals = []
    n = len(P)
    for i in range(n):
        a = P[i]
        b = P[(i + 1) % n]
        e = b - a
        for j in range(n):
            if j == i or j == (i + 1) % n:
                continue
            v = P[j] - a
            vals.append(float(sign * (e[0] * v[1] - e[1] * v[0])))
    return np.asarray(vals)


def convexity_margin(P: Array) -> float:
    return float(np.min(convexity_margins(P)))


def edge_lengths(P: Array) -> Array:
    return np.linalg.norm(np.roll(P, -1, axis=0) - P, axis=1)


def min_edge_length(P: Array) -> float:
    return float(np.min(edge_lengths(P)))


def min_pair_distance(P: Array) -> float:
    D = np.sqrt(np.maximum(pairwise_sqdist(P), 0))
    iu = np.triu_indices(len(P), 1)
    return float(np.min(D[iu]))


def params_to_points(g: Array) -> Array:
    top_gaps = softmax(g[:9]) * (math.pi - 2 * EPS)
    bot_gaps = softmax(g[9:18]) * (math.pi - 2 * EPS)
    top = np.empty(M)
    bot = np.empty(M)
    top[0] = math.pi - EPS
    bot[0] = -EPS
    for k in range(1, M):
        top[k] = top[k - 1] - top_gaps[k - 1]
        bot[k] = bot[k - 1] - bot_gaps[k - 1]
    theta = np.concatenate([top, bot])
    rv = np.exp(np.clip(g[18:38], -6, 6))
    return normalize_points(np.column_stack([rv * np.cos(theta), rv * np.sin(theta)]))


def selected_sqdist(P: Array, rows: Pattern) -> Array:
    D2 = pairwise_sqdist(P)
    return np.asarray(
        [[D2[i, j] for j in row] for i, row in enumerate(rows)], dtype=float
    )


def independent_diagnostics(P: Array, rows: Pattern) -> dict:
    D2 = pairwise_sqdist(P)
    spreads = []
    rel = []
    centered = []
    table = []
    for i, row in enumerate(rows):
        vals = np.asarray([D2[i, j] for j in row])
        mean = float(vals.mean())
        spread = float(vals.max() - vals.min())
        spreads.append(spread)
        rel.append(spread / max(abs(mean), 1e-15))
        centered.extend((vals - mean).tolist())
        table.append(
            {
                "i": i,
                "S_i": [int(j) for j in row],
                "sqdistances": [float(v) for v in vals],
                "mean_sqdistance": mean,
                "spread": spread,
                "relative_spread": float(spread / max(abs(mean), 1e-15)),
            }
        )
    return {
        "eq_rms": float(math.sqrt(np.mean(np.square(centered)))),
        "max_spread": float(max(spreads)),
        "max_rel_spread": float(max(rel)),
        "convexity_margin": convexity_margin(P),
        "min_edge_length": min_edge_length(P),
        "min_pair_distance": min_pair_distance(P),
        "area2": polygon_area2(P),
        "distance_table": table,
    }


def pack(g: Array, log_rho: Array) -> Array:
    return np.concatenate([g, log_rho])


def unpack(z: Array) -> tuple[Array, Array, Array]:
    g = np.asarray(z[:38])
    log_rho = np.asarray(z[38:58])
    return params_to_points(g), g, np.exp(np.clip(2 * log_rho, -30, 30))


def homotopy_terms(z: Array, t: float, seed_d2: Array, rows: Pattern) -> Array:
    P, _, rho2 = unpack(z)
    curr = selected_sqdist(P, rows)
    target = (1 - t) * seed_d2 + t * rho2[:, None]
    return (curr - target).reshape(-1)


def point_summary(P: Array, rows: Pattern, z: Array, t: float, seed_d2: Array) -> dict:
    # Primary diagnostics are intentionally computed before residual.
    conv = convexity_margin(P)
    edge = min_edge_length(P)
    pair = min_pair_distance(P)
    h = homotopy_terms(z, t, seed_d2, rows)
    diag = independent_diagnostics(P, rows)
    return {
        "t": float(t),
        "convexity_margin": conv,
        "min_edge_length": edge,
        "min_pair_distance": pair,
        "homotopy_rms": float(math.sqrt(np.mean(h * h))),
        "homotopy_max_abs": float(np.max(np.abs(h))),
        "eq_rms_t1_spread_metric": float(diag["eq_rms"]),
        "max_spread_t1_spread_metric": float(diag["max_spread"]),
        "max_rel_spread_t1_spread_metric": float(diag["max_rel_spread"]),
    }


def cubic_preflight(match: int) -> dict:
    rows3 = cubic_seed_pattern(match)
    return {
        "match_offset_deleted_even_side": match,
        "S3": rows3,
        "row_overlap_cap": row_overlap_cap(rows3),
        "interpretation": "3-neighbor Fishburn--Reeds-style scaffold only; no exact FR coordinates asserted",
    }


def track(args: argparse.Namespace, match: int) -> dict:
    rows = mixed_radius_pattern()
    g0 = np.zeros(38)
    P0 = params_to_points(g0)
    seed_d2 = selected_sqdist(P0, rows)
    z = pack(g0, 0.5 * np.log(np.maximum(seed_d2.mean(axis=1), 1e-14)))
    t = 0.0
    dt = args.dt0
    accepted = []
    rejected = []
    attempts = 0
    termination = "max_steps_or_t1_reached"
    p0 = point_summary(P0, rows, z, 0.0, seed_d2)
    p0.update({"status": "seed", "step_dt": 0.0, "nfev": 0})
    accepted.append(p0)
    while t < 1.0 - 1e-12 and attempts < args.max_attempts:
        attempts += 1
        tt = min(1.0, t + dt)
        sol = least_squares(
            lambda y: homotopy_terms(y, tt, seed_d2, rows),
            z,
            method="trf",
            max_nfev=args.step_nfev,
            ftol=1e-10,
            xtol=1e-10,
            gtol=1e-10,
            x_scale="jac",
        )
        P, _, _ = unpack(sol.x)
        # Primary gate before residual.
        conv = convexity_margin(P)
        edge = min_edge_length(P)
        pair = min_pair_distance(P)
        point = point_summary(P, rows, sol.x, tt, seed_d2)
        point.update(
            {
                "attempt": attempts,
                "from_t": float(t),
                "target_t": float(tt),
                "step_dt": float(dt),
                "nfev": int(sol.nfev),
                "solver_success": bool(sol.success),
                "solver_message": str(sol.message),
                "solver_cost": float(sol.cost),
                "primary_diagnostics_checked_before_residual": {
                    "convexity_margin": conv,
                    "min_edge_length": edge,
                    "min_pair_distance": pair,
                },
            }
        )
        if conv <= args.collapse_margin or edge <= args.collapse_edge:
            point["status"] = "rejected_convexity_collapse"
            rejected.append(point)
            dt *= 0.5
            if dt < args.min_dt:
                termination = "convexity_collapse_dt_below_min"
                break
            continue
        if point["homotopy_max_abs"] > args.accept_max_abs:
            point["status"] = "rejected_residual_after_primary_gate"
            rejected.append(point)
            dt *= 0.5
            if dt < args.min_dt:
                termination = "residual_stall_dt_below_min"
                break
            continue
        point["status"] = "accepted"
        accepted.append(point)
        t = tt
        z = sol.x.copy()
        dt = min(args.max_dt, dt * 1.4)
    start = time.time()
    sol = least_squares(
        lambda y: homotopy_terms(y, 1.0, seed_d2, rows),
        z,
        method="trf",
        max_nfev=args.endpoint_nfev,
        ftol=1e-12,
        xtol=1e-12,
        gtol=1e-12,
        x_scale="jac",
    )
    P, _, _ = unpack(sol.x)
    diag = independent_diagnostics(P, rows)
    endpoint = point_summary(P, rows, sol.x, 1.0, seed_d2)
    final = {
        "pattern_name": "B20_FR_bipartite_mixed_radius_arc",
        "n": N,
        "mode": "two_arc_equality_homotopy_trf",
        "loss": float(sol.cost),
        "eq_rms": float(diag["eq_rms"]),
        "max_spread": float(diag["max_spread"]),
        "max_rel_spread": float(diag["max_rel_spread"]),
        "convexity_margin": float(diag["convexity_margin"]),
        "min_edge_length": float(diag["min_edge_length"]),
        "min_pair_distance": float(diag["min_pair_distance"]),
        "success": bool(sol.success),
        "message": str(sol.message),
        "elapsed_sec": float(time.time() - start),
        "seed": int(args.seed),
        "coordinates": [[float(a), float(b)] for a, b in P],
        "S": rows,
        "distance_table": diag["distance_table"],
        "trust": "NUMERICAL_EVIDENCE",
        "interpretation": "failed approach unless exact verifier trigger is met",
    }
    verifier = {
        "status": "not_triggered",
        "reason": "residual/convexity trigger not met",
    }
    if (
        final["max_spread"] < 1e-10
        and final["convexity_margin"] > 1e-3
        and final["min_edge_length"] > 1e-3
        and final["min_pair_distance"] > 1e-3
    ):
        verifier = {
            "status": "would_trigger",
            "reason": "standalone verifier should be run in full repo checkout",
        }
    return {
        "match_offset_context": match,
        "pattern_name": final["pattern_name"],
        "n": N,
        "S": rows,
        "row_overlap_cap": row_overlap_cap(rows),
        "parameterization": {
            "family": "two_arc_bipartite_independent_vertex_radii",
            "geometric_variables": 38,
            "selected_radius_variables": 20,
            "upper_arc_vertices": list(range(10)),
            "lower_arc_vertices": list(range(10, 20)),
            "torus_boundary_order": BOUNDARY_FROM_TORUS,
            "description": "B20 torus labels relabelled into two arcs; every vertex has its own polar radius and every center has its own selected circle radius rho_i.",
        },
        "homotopy": {
            "t0": "convex bipartite-arc seed with frozen selected squared distances",
            "t1": "independent per-center rho_i^2 equal-distance equations on four witnesses",
            "residual_equation": "D2(i,w_k)-((1-t)*D2_seed(i,w_k)+t*rho_i^2)=0",
            "step_control": {
                "predictor": "previous accepted point",
                "corrector": "scipy.optimize.least_squares on homotopy equations only",
                "dt0": args.dt0,
                "max_dt": args.max_dt,
                "min_dt": args.min_dt,
                "accept_max_abs": args.accept_max_abs,
                "primary_gate": "strict convexity margin and minimum edge length checked before equality residual",
                "collapse_margin": args.collapse_margin,
                "collapse_edge": args.collapse_edge,
            },
        },
        "termination": termination,
        "accepted_points": accepted,
        "rejected_points": rejected,
        "endpoint_polish": {
            "success": bool(sol.success),
            "message": str(sol.message),
            "nfev": int(sol.nfev),
            "cost": float(sol.cost),
            "elapsed_sec": float(time.time() - start),
            "primary_diagnostics_checked_before_residual": {
                "convexity_margin": convexity_margin(P),
                "min_edge_length": min_edge_length(P),
                "min_pair_distance": min_pair_distance(P),
            },
            "diagnostics": endpoint,
            "final_independent_diagnostics": {
                k: v for k, v in diag.items() if k != "distance_table"
            },
        },
        "final_result_schema_compatible": {
            k: v
            for k, v in final.items()
            if k not in ("coordinates", "S", "distance_table")
        },
        "standalone_verifier": verifier,
    }


def collapse_analysis(runs: list[dict]) -> dict:
    rejs = [p for r in runs for p in r["homotopy_run"]["rejected_points"]]
    finals = [r["homotopy_run"]["final_result_schema_compatible"] for r in runs]
    best = min(finals, key=lambda x: (x["max_spread"], -x["convexity_margin"]))
    cand = [
        f
        for f in finals
        if f["max_spread"] < 1e-10
        and f["convexity_margin"] > 1e-3
        and f["min_edge_length"] > 1e-3
        and f["min_pair_distance"] > 1e-3
    ]
    return {
        "trust": "FAILED_APPROACH / NUMERICAL_EVIDENCE",
        "counterexample_candidate_count": len(cand),
        "standalone_verifier_triggered": bool(cand),
        "best_final_by_max_spread": best,
        "rejection_count": len(rejs),
        "minimum_rejected_convexity_margin": min(
            (p["convexity_margin"] for p in rejs), default=None
        ),
        "minimum_rejected_edge_length": min(
            (p["min_edge_length"] for p in rejs), default=None
        ),
        "diagnosis": "Continuation reduces homotopy residual only by driving the two-arc scaffold toward the boundary of strict convexity; active constraints are edge-line convexity margin and then minimum edge/pair separation.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=20260609)
    ap.add_argument("--matchings", type=int, nargs="*", default=[0, 1, 2, 3])
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(
            "data/runs/mixed_radius_bipartite_arc_homotopy_2026-06-09/summary.json"
        ),
    )
    ap.add_argument("--dt0", type=float, default=0.1)
    ap.add_argument("--max-dt", type=float, default=0.2)
    ap.add_argument("--min-dt", type=float, default=1e-4)
    ap.add_argument("--max-attempts", type=int, default=40)
    ap.add_argument("--step-nfev", type=int, default=120)
    ap.add_argument("--endpoint-nfev", type=int, default=500)
    ap.add_argument("--accept-max-abs", type=float, default=1e-6)
    ap.add_argument("--collapse-margin", type=float, default=1e-6)
    ap.add_argument("--collapse-edge", type=float, default=2e-5)
    args = ap.parse_args()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    runs = []
    first_run = None
    for match in args.matchings:
        # The full four-neighbor homotopy is independent of which cubic matching was deleted in preflight.
        if first_run is None:
            first_run = track(args, match)
        run = json.loads(json.dumps(first_run))
        run["match_offset_context"] = match
        runs.append(
            {
                "matching": match,
                "cubic_unit_preflight": cubic_preflight(match),
                "homotopy_run": run,
            }
        )
        f = run["final_result_schema_compatible"]
        print(
            f"match={match} termination={run['termination']} accepted={len(run['accepted_points'])} rejected={len(run['rejected_points'])} final_spread={f['max_spread']:.3e} final_conv={f['convexity_margin']:.3e} final_edge={f['min_edge_length']:.3e}",
            flush=True,
        )
    payload = {
        "tool": "scripts/homotopy_mixed_radius_bipartite_arc.py",
        "pattern_name": "B20_FR_bipartite_mixed_radius_arc",
        "seed": args.seed,
        "started_utc": started,
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "trust": "FAILED_APPROACH / NUMERICAL_EVIDENCE",
        "source_context": {
            "repo_files_read_before_coding": [
                "README.md",
                "STATE.md",
                "docs/failed-ideas.md",
                "docs/candidate-patterns.md",
                "docs/exactification-plan.md",
            ],
            "fishburn_reeds_seed_status": "Fishburn--Reeds used as k=3 seed/scaffold context; no exact coordinate file was found in the available repo snapshot.",
            "contradictions_or_guardrails": [
                "B20_4x5_FR_lift is archived as exactly killed as a fixed selected pattern; this run uses it only as an incidence scaffold.",
                "Repo exactification threshold is stricter than the session trigger; candidate status remains gated by repo trust labels.",
            ],
        },
        "runs": runs,
        "collapse_analysis": collapse_analysis(runs),
    }
    payload["best_final_by_max_spread"] = payload["collapse_analysis"].pop(
        "best_final_by_max_spread"
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
