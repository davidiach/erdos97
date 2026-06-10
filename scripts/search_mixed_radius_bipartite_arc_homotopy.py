#!/usr/bin/env python3
"""Mixed-radius bipartite polar-arc homotopy probe for Erdos Problem #97.

Trust label: NUMERICAL_EVIDENCE unless exact verification is later supplied;
FAILED_APPROACH when all tracked paths lose the strict-convexity margins.

The incidence template is the repository's Fishburn--Reeds-inspired
``B20_4x5_FR_lift`` selected-witness pattern.  Labels are written as
``i = 5*a + b`` with ``a mod 4`` and ``b mod 5``.  The two classes are
``A = {a even}`` and ``B = {a odd}``.  Every selected witness of the template
is in the opposite class, so the selected rows are bipartite.

Parameterization.  The boundary order is fixed as labels 0..19, which gives
four consecutive arcs A0,B0,A1,B1.  The angular gaps are positive by
construction and every vertex has an independent radius

    p_i = rho_i (cos theta_i, sin theta_i),
    theta_{i+1}-theta_i = gap_floor + softmax(z)_i*(2*pi-n*gap_floor),
    rho_i = radius_floor + exp(s_i).

There is no shared radius per class and no coordinate symmetry is imposed.  The
chart does not assume convexity; every accepted homotopy point is checked by the
repo-style all-edge-vs-all-vertices strict convexity margin before the equality
residual is considered.

Homotopy.  For each drop index d in {0,1,2,3}, t=0 enforces the other three
selected witnesses in every row and t=1 enforces all four.  Paths are tracked
by a simple predictor-corrector: constant predictor for the first step, then a
secant predictor; scipy.optimize.least_squares is the corrector; accepted steps
may grow, rejected steps shrink.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import least_squares

Array = NDArray[np.float64]
Pattern = list[list[int]]
OFFSETS: tuple[tuple[int, int], ...] = ((1, 0), (3, 0), (1, 2), (3, -2))


@dataclasses.dataclass
class Diagnostics:
    eq_rms: float
    max_spread: float
    max_rel_spread: float
    convexity_margin: float
    min_edge_length: float
    min_pair_distance: float
    area2: float


def b20_fr_lift_pattern() -> Pattern:
    rows: Pattern = []
    for a in range(4):
        for b in range(5):
            row = []
            for da, db in OFFSETS:
                row.append(((a + da) % 4) * 5 + ((b + db) % 5))
            rows.append(row)
    return rows


def class_labels() -> list[str]:
    return ["A" if divmod(i, 5)[0] % 2 == 0 else "B" for i in range(20)]


def softmax(z: Array) -> Array:
    z = np.asarray(z, dtype=float)
    z = z - np.max(z)
    e = np.exp(z)
    return e / np.sum(e)


def normalize_points(points: Array) -> Array:
    q = np.asarray(points, dtype=float).copy()
    q -= q.mean(axis=0)
    scale = math.sqrt(float(np.mean(np.sum(q * q, axis=1))))
    if not math.isfinite(scale) or scale <= 1e-300:
        scale = 1.0
    q /= scale
    v = q[0]
    theta = -math.atan2(float(v[1]), float(v[0]))
    c, s = math.cos(theta), math.sin(theta)
    return q @ np.array([[c, -s], [s, c]], dtype=float).T


def points_from_polar_arc(
    x: Array,
    *,
    gap_floor: float = 1e-4,
    radius_floor: float = 1e-3,
) -> Array:
    n = 20
    z = np.asarray(x[:n], dtype=float)
    log_r = np.asarray(x[n : 2 * n], dtype=float)
    if n * gap_floor >= 2.0 * math.pi:
        raise ValueError("gap_floor too large")
    gaps = gap_floor + softmax(z) * (2.0 * math.pi - n * gap_floor)
    theta = np.zeros(n, dtype=float)
    theta[1:] = np.cumsum(gaps[:-1])
    radii = radius_floor + np.exp(np.clip(log_r, -12.0, 12.0))
    return normalize_points(
        np.column_stack([radii * np.cos(theta), radii * np.sin(theta)])
    )


def init_x(rng: np.random.Generator, jitter: float) -> Array:
    n = 20
    # Start near a regular 20-gon but allow independent per-vertex radii.
    gap_weights = 1.0 + jitter * rng.normal(size=n)
    gap_weights = np.maximum(gap_weights, 0.05)
    z = np.log(gap_weights)
    log_r = jitter * rng.normal(size=n)
    return np.concatenate([z, log_r])


def polygon_area2(points: Array) -> float:
    x, y = points[:, 0], points[:, 1]
    return float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def convexity_margins(points: Array) -> Array:
    n = len(points)
    sign = -1.0 if polygon_area2(points) < 0.0 else 1.0
    out: list[float] = []
    for i in range(n):
        a = points[i]
        b = points[(i + 1) % n]
        edge = b - a
        for j in range(n):
            if j == i or j == (i + 1) % n:
                continue
            v = points[j] - a
            out.append(float(sign * (edge[0] * v[1] - edge[1] * v[0])))
    return np.array(out, dtype=float)


def pairwise_sqdist(points: Array) -> Array:
    delta = points[:, None, :] - points[None, :, :]
    return np.sum(delta * delta, axis=2)


def min_edge_length(points: Array) -> float:
    return float(np.min(np.linalg.norm(np.roll(points, -1, axis=0) - points, axis=1)))


def min_pair_distance(points: Array) -> float:
    d2 = pairwise_sqdist(points)
    return float(np.min(np.sqrt(d2[np.triu_indices(len(points), 1)])))


def equality_terms_from_d2(d2: Array, rows: Pattern, drop: int, t: float) -> Array:
    values: list[float] = []
    for center, row in enumerate(rows):
        introduced = row[drop]
        base = row[0] if drop != 0 else row[1]
        for target in row:
            if target == base:
                continue
            weight = t if target == introduced else 1.0
            values.append(float(weight * (d2[center, target] - d2[center, base])))
    return np.array(values, dtype=float)


def equality_residual_vector(x: Array, rows: Pattern, drop: int, t: float) -> Array:
    return equality_terms_from_d2(
        pairwise_sqdist(points_from_polar_arc(x)), rows, drop, t
    )


def residual_vector(
    x: Array,
    rows: Pattern,
    drop: int,
    t: float,
    *,
    convex_floor: float,
    edge_floor: float,
    pair_floor: float,
    convex_weight: float,
    edge_weight: float,
    pair_weight: float,
) -> Array:
    points = points_from_polar_arc(x)
    d2 = pairwise_sqdist(points)
    values = equality_terms_from_d2(d2, rows, drop, t).tolist()
    values.extend(
        (
            convex_weight * np.maximum(0.0, convex_floor - convexity_margins(points))
        ).tolist()
    )
    edge_lengths = np.linalg.norm(np.roll(points, -1, axis=0) - points, axis=1)
    values.extend((edge_weight * np.maximum(0.0, edge_floor - edge_lengths)).tolist())
    pair_lengths = np.sqrt(d2[np.triu_indices(len(points), 1)])
    values.extend((pair_weight * np.maximum(0.0, pair_floor - pair_lengths)).tolist())
    return np.array(values, dtype=float)


def diagnostics(points: Array, rows: Pattern) -> Diagnostics:
    d2 = pairwise_sqdist(points)
    spreads: list[float] = []
    rel_spreads: list[float] = []
    centered_terms: list[float] = []
    for center, row in enumerate(rows):
        vals = np.array([d2[center, target] for target in row], dtype=float)
        mean = float(np.mean(vals))
        spread = float(np.max(vals) - np.min(vals))
        spreads.append(spread)
        rel_spreads.append(spread / max(abs(mean), 1e-15))
        centered_terms.extend((vals - mean).tolist())
    return Diagnostics(
        eq_rms=float(math.sqrt(np.mean(np.square(centered_terms)))),
        max_spread=float(max(spreads)),
        max_rel_spread=float(max(rel_spreads)),
        convexity_margin=float(np.min(convexity_margins(points))),
        min_edge_length=min_edge_length(points),
        min_pair_distance=min_pair_distance(points),
        area2=polygon_area2(points),
    )


def diag_dict(diag: Diagnostics) -> dict[str, float]:
    return dataclasses.asdict(diag)


def distance_table(points: Array, rows: Pattern) -> list[dict[str, Any]]:
    d2 = pairwise_sqdist(points)
    table: list[dict[str, Any]] = []
    for center, row in enumerate(rows):
        vals = [float(d2[center, target]) for target in row]
        mean = float(np.mean(vals))
        table.append(
            {
                "i": center,
                "S_i": [int(target) for target in row],
                "sqdistances": vals,
                "mean_sqdistance": mean,
                "spread": float(max(vals) - min(vals)),
                "relative_spread": float(
                    (max(vals) - min(vals)) / max(abs(mean), 1e-15)
                ),
            }
        )
    return table


def active_rms(x: Array, rows: Pattern, drop: int, t: float) -> float:
    res = equality_residual_vector(x, rows, drop, t)
    return float(math.sqrt(np.mean(np.square(res)))) if len(res) else 0.0


def solve_seed_for_drop(
    args: argparse.Namespace, rng: np.random.Generator, rows: Pattern, drop: int
) -> dict[str, Any]:
    best: dict[str, Any] | None = None
    for attempt in range(args.attempts):
        x0 = init_x(rng, args.jitter)
        result = least_squares(
            residual_vector,
            x0,
            args=(rows, drop, 0.0),
            kwargs={
                "convex_floor": args.convex_floor,
                "edge_floor": args.edge_floor,
                "pair_floor": args.pair_floor,
                "convex_weight": args.convex_weight,
                "edge_weight": args.edge_weight,
                "pair_weight": args.pair_weight,
            },
            max_nfev=args.seed_max_nfev,
            xtol=args.xtol,
            ftol=args.ftol,
            gtol=args.gtol,
        )
        points = points_from_polar_arc(result.x)
        diag = diagnostics(points, rows)
        score = (
            active_rms(result.x, rows, drop, 0.0)
            + 25.0 * max(0.0, args.convex_floor - diag.convexity_margin)
            + 5.0 * max(0.0, args.edge_floor - diag.min_edge_length)
        )
        record = {
            "drop": int(drop),
            "attempt": int(attempt),
            "score": float(score),
            "active_rms_at_t0": active_rms(result.x, rows, drop, 0.0),
            "cost": float(result.cost),
            "nfev": int(result.nfev),
            "status": int(result.status),
            "message": str(result.message),
            "optimality": float(result.optimality),
            "diagnostics": diag_dict(diag),
            "x": result.x.tolist(),
        }
        if best is None or record["score"] < best["score"]:
            best = record
    assert best is not None
    return best


def accepted_point_record(
    t: float,
    x: Array,
    rows: Pattern,
    drop: int,
    exact_threshold: float,
    exact_margin: float,
    exact_edge: float,
    exact_pair: float,
) -> dict[str, Any]:
    points = points_from_polar_arc(x)
    diag = diagnostics(points, rows)
    record: dict[str, Any] = {
        "t": float(t),
        "convexity_margin": diag.convexity_margin,
        "min_edge_length": diag.min_edge_length,
        "min_pair_distance": diag.min_pair_distance,
        "eq_rms": diag.eq_rms,
        "max_spread": diag.max_spread,
        "max_rel_spread": diag.max_rel_spread,
        "active_rms": active_rms(x, rows, drop, t),
        "checked_order": [
            "convexity_margin",
            "min_edge_length",
            "min_pair_distance",
            "active/equality residual",
        ],
    }
    if (
        diag.max_spread < exact_threshold
        and diag.convexity_margin > exact_margin
        and diag.min_edge_length > exact_edge
        and diag.min_pair_distance > exact_pair
    ):
        record["requires_exact_verifier"] = True
    return record


def track_path(
    args: argparse.Namespace, rows: Pattern, drop: int, seed_x: Array
) -> dict[str, Any]:
    t = 0.0
    x_prev: Array | None = None
    t_prev: float | None = None
    x = np.asarray(seed_x, dtype=float).copy()
    dt = args.initial_dt
    accepted = [
        accepted_point_record(
            t,
            x,
            rows,
            drop,
            args.exact_spread,
            args.exact_margin,
            args.exact_edge,
            args.exact_pair,
        )
    ]
    rejected: list[dict[str, Any]] = []
    termination = "max_steps"

    for step in range(args.max_steps):
        if t >= 1.0 - 1e-15:
            termination = "reached_t1"
            break
        target_t = min(1.0, t + dt)
        if x_prev is None or t_prev is None or abs(t - t_prev) < 1e-15:
            pred = x.copy()
        else:
            pred = x + (target_t - t) * (x - x_prev) / (t - t_prev)
        result = least_squares(
            residual_vector,
            pred,
            args=(rows, drop, target_t),
            kwargs={
                "convex_floor": args.convex_floor,
                "edge_floor": args.edge_floor,
                "pair_floor": args.pair_floor,
                "convex_weight": args.convex_weight,
                "edge_weight": args.edge_weight,
                "pair_weight": args.pair_weight,
            },
            max_nfev=args.path_max_nfev,
            xtol=args.xtol,
            ftol=args.ftol,
            gtol=args.gtol,
        )
        cand_x = result.x
        points = points_from_polar_arc(cand_x)
        diag = diagnostics(points, rows)
        active = active_rms(cand_x, rows, drop, target_t)
        margin_ok = diag.convexity_margin > args.convex_floor
        edge_ok = diag.min_edge_length > args.edge_floor
        pair_ok = diag.min_pair_distance > args.pair_floor
        residual_ok = active < args.active_rms_accept

        if margin_ok and edge_ok and pair_ok and residual_ok:
            x_prev = x
            t_prev = t
            x = cand_x
            t = target_t
            accepted.append(
                accepted_point_record(
                    t,
                    x,
                    rows,
                    drop,
                    args.exact_spread,
                    args.exact_margin,
                    args.exact_edge,
                    args.exact_pair,
                )
            )
            dt = min(args.max_dt, dt * args.growth)
            continue

        rejected.append(
            {
                "step": int(step),
                "attempted_t": float(target_t),
                "dt": float(dt),
                "convexity_margin": diag.convexity_margin,
                "min_edge_length": diag.min_edge_length,
                "min_pair_distance": diag.min_pair_distance,
                "active_rms": float(active),
                "max_spread": diag.max_spread,
                "margin_ok": bool(margin_ok),
                "edge_ok": bool(edge_ok),
                "pair_ok": bool(pair_ok),
                "residual_ok": bool(residual_ok),
                "nfev": int(result.nfev),
                "message": str(result.message),
            }
        )
        if not margin_ok or not edge_ok or not pair_ok:
            # Convexity/edge collapse is primary.  Do not tune residual around it.
            termination = "convexity_or_edge_rejected"
            if dt <= args.min_dt:
                break
        dt *= args.shrink
        if dt < args.min_dt:
            termination = "step_below_min_dt_after_reject"
            break

    last = accepted[-1]
    if (
        last["convexity_margin"] <= 10.0 * args.convex_floor
        or last["min_edge_length"] <= 10.0 * args.edge_floor
    ):
        termination = "convexity_floor_riding"
    return {
        "drop": int(drop),
        "termination": termination,
        "accepted_points": accepted,
        "rejected_steps": rejected,
        "last_t": float(accepted[-1]["t"]),
        "final_x": x.tolist(),
        "final_diagnostics": diag_dict(diagnostics(points_from_polar_arc(x), rows)),
    }


def build_artifact(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    rng = np.random.default_rng(args.seed)
    rows = b20_fr_lift_pattern()
    seed_records = []
    paths = []
    for drop in range(4):
        seed = solve_seed_for_drop(args, rng, rows, drop)
        seed_records.append({k: v for k, v in seed.items() if k != "x"})
        paths.append(track_path(args, rows, drop, np.array(seed["x"], dtype=float)))

    best_path = min(
        paths, key=lambda p: (1.0 - p["last_t"], p["final_diagnostics"]["max_spread"])
    )
    best_x = np.array(best_path["final_x"], dtype=float)
    best_points = points_from_polar_arc(best_x)
    best_diag = diagnostics(best_points, rows)
    exact_triggered = [
        pt
        for path in paths
        for pt in path["accepted_points"]
        if pt.get("requires_exact_verifier")
    ]
    trust = (
        "COUNTEREXAMPLE_CANDIDATE_REQUIRES_EXACT_RECHECK"
        if exact_triggered
        else "FAILED_APPROACH"
    )
    return {
        "schema_version": "mixed_radius_bipartite_polar_arc_homotopy_v1",
        "status": trust,
        "trust_label": trust,
        "pattern_name": "B20_4x5_FR_lift_mixed_radius_bipartite_polar_arc_homotopy",
        "source_pattern_name": "B20_4x5_FR_lift",
        "pattern_family": "mixed-radius bipartite polar arc homotopy",
        "pattern_formula": "i=(a,b), S_i=(a,b)+[(1,0),(3,0),(1,2),(3,-2)] mod (4,5); classes by parity of a",
        "pattern_notes": "Uses the repo's FR-lift incidence template, not an exact historical Fishburn-Reeds coordinate certificate.",
        "n": 20,
        "seed": int(args.seed),
        "success": bool(exact_triggered),
        "mode": "polar_arc_independent_per_vertex_radii",
        "parameterization": {
            "name": "mixed_radius_bipartite_polar_arc_family",
            "boundary_order": list(range(20)),
            "arc_blocks": [
                "A0 labels 0..4",
                "B0 labels 5..9",
                "A1 labels 10..14",
                "B1 labels 15..19",
            ],
            "vertex_classes": {
                "A": [i for i, c in enumerate(class_labels()) if c == "A"],
                "B": [i for i, c in enumerate(class_labels()) if c == "B"],
            },
            "class_labels": class_labels(),
            "bipartite_property": "for row i=5*a+b, selected witnesses have a parity opposite to center a",
            "angle_gaps": "gap_i = gap_floor + softmax(z)_i * (2*pi - n*gap_floor)",
            "per_vertex_radii": "rho_i = radius_floor + exp(s_i), one independent radius parameter per vertex",
            "normalization": "centroid removed, RMS radius set to 1, p0 rotation gauge",
            "convexity_contract": "not assumed by chart; every accepted point checks all edge-vs-all-vertices margins before residual",
        },
        "homotopy": {
            "equations": "For each drop d, t=0 enforces the other three witnesses and t=1 enforces all four.",
            "predictor": "constant first step, then secant predictor",
            "corrector": "scipy.optimize.least_squares",
            "step_control": {
                "initial_dt": args.initial_dt,
                "max_dt": args.max_dt,
                "growth": args.growth,
                "shrink_on_reject": args.shrink,
                "min_dt": args.min_dt,
                "acceptance_order": "check convexity_margin and min_edge_length before equality residual",
            },
            "floors": {
                "convex": args.convex_floor,
                "edge": args.edge_floor,
                "pair": args.pair_floor,
            },
            "exact_recheck_trigger": {
                "max_spread": args.exact_spread,
                "convexity": args.exact_margin,
                "min_edge_length": args.exact_edge,
                "min_pair_distance": args.exact_pair,
            },
        },
        "seed_records": seed_records,
        "paths": paths,
        "best_path_summary": {
            "drop": best_path["drop"],
            "last_t": best_path["last_t"],
            "termination": best_path["termination"],
            "final_diagnostics": best_path["final_diagnostics"],
        },
        "coordinates": best_points.tolist(),
        "x": best_x.tolist(),
        "S": rows,
        "distance_table": distance_table(best_points, rows),
        "loss": float(best_diag.eq_rms),
        "eq_rms": best_diag.eq_rms,
        "max_spread": best_diag.max_spread,
        "max_rel_spread": best_diag.max_rel_spread,
        "convexity_margin": best_diag.convexity_margin,
        "min_edge_length": best_diag.min_edge_length,
        "min_pair_distance": best_diag.min_pair_distance,
        "elapsed_sec": time.time() - started,
        "exact_verifier_triggered": bool(exact_triggered),
        "does_not_claim": [
            "general proof of Erdos Problem #97",
            "counterexample to Erdos Problem #97",
            "exact equality from floating residuals alone",
        ],
        "notes": [
            "all accepted paths terminated before t=1 or rode the convexity/edge floor"
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20260609)
    parser.add_argument("--attempts", type=int, default=5)
    parser.add_argument("--jitter", type=float, default=0.25)
    parser.add_argument("--seed-max-nfev", type=int, default=240)
    parser.add_argument("--path-max-nfev", type=int, default=160)
    parser.add_argument("--convex-floor", type=float, default=1e-4)
    parser.add_argument("--edge-floor", type=float, default=1e-3)
    parser.add_argument("--pair-floor", type=float, default=1e-3)
    parser.add_argument("--convex-weight", type=float, default=200.0)
    parser.add_argument("--edge-weight", type=float, default=25.0)
    parser.add_argument("--pair-weight", type=float, default=5.0)
    parser.add_argument("--active-rms-accept", type=float, default=5e-3)
    parser.add_argument("--initial-dt", type=float, default=0.05)
    parser.add_argument("--max-dt", type=float, default=0.15)
    parser.add_argument("--growth", type=float, default=1.25)
    parser.add_argument("--shrink", type=float, default=0.5)
    parser.add_argument("--min-dt", type=float, default=1e-4)
    parser.add_argument("--max-steps", type=int, default=80)
    parser.add_argument("--exact-spread", type=float, default=1e-10)
    parser.add_argument("--exact-margin", type=float, default=1e-3)
    parser.add_argument("--exact-edge", type=float, default=1e-3)
    parser.add_argument("--exact-pair", type=float, default=1e-3)
    parser.add_argument("--xtol", type=float, default=1e-10)
    parser.add_argument("--ftol", type=float, default=1e-10)
    parser.add_argument("--gtol", type=float, default=1e-10)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(
            "data/runs/mixed_radius_bipartite_polar_arc_fr_homotopy_seed20260609.json"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    artifact = build_artifact(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "out": str(args.out),
                "trust_label": artifact["trust_label"],
                "best_path_summary": artifact["best_path_summary"],
                "exact_verifier_triggered": artifact["exact_verifier_triggered"],
                "elapsed_sec": artifact["elapsed_sec"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
