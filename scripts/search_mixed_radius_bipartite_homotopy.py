#!/usr/bin/env python3
"""Mixed-radius bipartite arc homotopy probe for Erdos Problem #97.

Trust label: NUMERICAL_EVIDENCE / FAILED_APPROACH when paths lose strict
convexity.  This script intentionally treats convexity margin and minimum edge
length as primary path diagnostics.

The incidence template is the repository's Fishburn--Reeds-inspired
``B20_4x5_FR_lift`` selected-witness pattern.  Labels are written as
``i = 5*a + b`` with ``a mod 4`` and ``b mod 5``.  The two bipartite classes
are ``a even`` and ``a odd``; every selected witness lies in the opposite
class.  For homotopy leg ``drop = d`` the t=0 equations enforce the other
three witnesses in each row, and t=1 also enforces the dropped witness.

Parameterization.  A convex 20-gon is represented by 20 support offsets
``h_i = h_floor + exp(u_i)`` for fixed outward normals at angles ``2*pi*i/n``.
The actual vertices are consecutive line intersections.  This is a
mixed-radius arc family in the sense used in this run: after normalization,
every boundary label has its own radial distance from the centroid, and no
class-wide radius is shared or optimized.  The support coordinates are only a
numerically stable chart; every accepted point is separately checked by the
edge-vs-all-vertices strict convexity margin.
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
            row: list[int] = []
            for da, db in OFFSETS:
                row.append(((a + da) % 4) * 5 + ((b + db) % 5))
            rows.append(row)
    return rows


def class_labels() -> list[str]:
    out: list[str] = []
    for i in range(20):
        a, _b = divmod(i, 5)
        out.append("A" if a % 2 == 0 else "B")
    return out


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
    rot = np.array([[c, -s], [s, c]], dtype=float)
    return q @ rot.T


def points_from_support(x: Array, h_floor: float = 0.25) -> Array:
    n = 20
    theta = 2.0 * math.pi * np.arange(n, dtype=float) / n
    normals = np.column_stack([np.cos(theta), np.sin(theta)])
    h = h_floor + np.exp(np.clip(np.asarray(x, dtype=float), -12.0, 12.0))
    points = np.zeros((n, 2), dtype=float)
    for i in range(n):
        mat = np.vstack([normals[i], normals[(i + 1) % n]])
        rhs = np.array([h[i], h[(i + 1) % n]], dtype=float)
        points[i] = np.linalg.solve(mat, rhs)
    return normalize_points(points)


def polygon_area2(points: Array) -> float:
    x, y = points[:, 0], points[:, 1]
    return float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def convexity_margins(points: Array) -> Array:
    n = len(points)
    sign = -1.0 if polygon_area2(points) < 0.0 else 1.0
    margins: list[float] = []
    for i in range(n):
        a = points[i]
        b = points[(i + 1) % n]
        edge = b - a
        for j in range(n):
            if j == i or j == (i + 1) % n:
                continue
            v = points[j] - a
            margins.append(float(sign * (edge[0] * v[1] - edge[1] * v[0])))
    return np.array(margins, dtype=float)


def pairwise_sqdist(points: Array) -> Array:
    delta = points[:, None, :] - points[None, :, :]
    return np.sum(delta * delta, axis=2)


def min_edge_length(points: Array) -> float:
    return float(np.min(np.linalg.norm(np.roll(points, -1, axis=0) - points, axis=1)))


def min_pair_distance(points: Array) -> float:
    d2 = pairwise_sqdist(points)
    vals = np.sqrt(d2[np.triu_indices(len(points), 1)])
    return float(np.min(vals))


def equality_residuals_for_row(
    d2: Array, row: list[int], center: int, drop: int, t: float
) -> list[float]:
    introduced = row[drop]
    base = row[0] if drop != 0 else row[1]
    out: list[float] = []
    for target in row:
        if target == base:
            continue
        weight = t if target == introduced else 1.0
        out.append(float(weight * (d2[center, target] - d2[center, base])))
    return out


def equality_residual_vector(x: Array, rows: Pattern, drop: int, t: float) -> Array:
    points = points_from_support(x)
    d2 = pairwise_sqdist(points)
    values: list[float] = []
    for center, row in enumerate(rows):
        values.extend(equality_residuals_for_row(d2, row, center, drop, t))
    return np.array(values, dtype=float)


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
    points = points_from_support(x)
    d2 = pairwise_sqdist(points)
    values: list[float] = []
    for center, row in enumerate(rows):
        values.extend(equality_residuals_for_row(d2, row, center, drop, t))

    # Soft guards only; the accepted-point decision below checks these first.
    margins = convexity_margins(points)
    values.extend((convex_weight * np.maximum(0.0, convex_floor - margins)).tolist())
    edges = np.linalg.norm(np.roll(points, -1, axis=0) - points, axis=1)
    values.extend((edge_weight * np.maximum(0.0, edge_floor - edges)).tolist())
    pairs = np.sqrt(d2[np.triu_indices(len(points), 1)])
    values.extend((pair_weight * np.maximum(0.0, pair_floor - pairs)).tolist())
    return np.array(values, dtype=float)


def diagnostics(points: Array, rows: Pattern) -> Diagnostics:
    d2 = pairwise_sqdist(points)
    spreads: list[float] = []
    rel_spreads: list[float] = []
    centered_terms: list[float] = []
    for i, row in enumerate(rows):
        vals = np.array([d2[i, j] for j in row], dtype=float)
        spread = float(vals.max() - vals.min())
        mean = float(vals.mean())
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


def distance_table(points: Array, rows: Pattern) -> list[dict[str, Any]]:
    d2 = pairwise_sqdist(points)
    table: list[dict[str, Any]] = []
    for i, row in enumerate(rows):
        vals = [float(d2[i, j]) for j in row]
        mean = float(np.mean(vals))
        table.append(
            {
                "i": i,
                "S_i": row,
                "sqdistances": vals,
                "mean_sqdistance": mean,
                "spread": float(max(vals) - min(vals)),
                "relative_spread": float(
                    (max(vals) - min(vals)) / max(abs(mean), 1e-15)
                ),
            }
        )
    return table


def solve_seed(
    rng: np.random.Generator,
    rows: Pattern,
    drop: int,
    attempts: int,
    max_nfev: int,
    floors: dict[str, float],
) -> tuple[Array, dict[str, Any]]:
    best_x: Array | None = None
    best_record: dict[str, Any] | None = None
    for attempt in range(attempts):
        x0 = 0.08 * rng.normal(size=20)
        sol = least_squares(
            lambda z: residual_vector(
                z,
                rows,
                drop,
                0.0,
                convex_floor=floors["convex"],
                edge_floor=floors["edge"],
                pair_floor=floors["pair"],
                convex_weight=20.0,
                edge_weight=5.0,
                pair_weight=2.0,
            ),
            x0,
            max_nfev=max_nfev,
            ftol=1e-10,
            xtol=1e-10,
            gtol=1e-10,
        )
        pts = points_from_support(sol.x)
        diag = diagnostics(pts, rows)
        active = equality_residual_vector(sol.x, rows, drop, 0.0)
        active_rms = float(
            np.linalg.norm(active)
            / math.sqrt(max(1, np.count_nonzero(np.ones_like(active))))
        )
        score = (
            active_rms
            + 100.0 * max(0.0, floors["convex"] - diag.convexity_margin)
            + 10.0 * max(0.0, floors["edge"] - diag.min_edge_length)
            + max(0.0, floors["pair"] - diag.min_pair_distance)
        )
        record = {
            "attempt": attempt,
            "score": score,
            "active_rms_at_t0": active_rms,
            "cost": float(sol.cost),
            "optimality": float(sol.optimality),
            "nfev": int(sol.nfev),
            "status": int(sol.status),
            "message": str(sol.message),
            "diagnostics": dataclasses.asdict(diag),
        }
        if best_record is None or score < best_record["score"]:
            best_x = sol.x.copy()
            best_record = record
    assert best_x is not None and best_record is not None
    return best_x, best_record


def track_path(
    x_seed: Array,
    rows: Pattern,
    drop: int,
    max_nfev: int,
    floors: dict[str, float],
    *,
    initial_dt: float = 0.05,
    min_dt: float = 1.0e-4,
) -> dict[str, Any]:
    t = 0.0
    x_prev = x_seed.copy()
    x_prev2: Array | None = None
    dt = initial_dt
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    def make_point_record(
        t_value: float, x_value: Array, phase: str, solver: Any | None = None
    ) -> dict[str, Any]:
        pts = points_from_support(x_value)
        diag = diagnostics(pts, rows)
        # Primary diagnostics are intentionally first in this record.
        record: dict[str, Any] = {
            "t": float(t_value),
            "phase": phase,
            "convexity_margin": diag.convexity_margin,
            "min_edge_length": diag.min_edge_length,
            "min_pair_distance": diag.min_pair_distance,
            "eq_rms": diag.eq_rms,
            "max_spread": diag.max_spread,
            "max_rel_spread": diag.max_rel_spread,
            "area2": diag.area2,
        }
        if solver is not None:
            record.update(
                {
                    "nfev": int(solver.nfev),
                    "cost": float(solver.cost),
                    "optimality": float(solver.optimality),
                    "status": int(solver.status),
                }
            )
        return record

    seed_record = make_point_record(0.0, x_prev, "seed")
    accepted.append(seed_record)
    termination = "not_started"

    while t < 1.0 - 1e-15:
        target_t = min(1.0, t + dt)
        if x_prev2 is None:
            predictor = x_prev.copy()
            predictor_type = "constant"
        else:
            predictor = x_prev + (x_prev - x_prev2) * (
                (target_t - t) / max(t - accepted[-2]["t"], 1e-12)
            )
            predictor_type = "secant"
        sol = least_squares(
            lambda z: residual_vector(
                z,
                rows,
                drop,
                target_t,
                convex_floor=floors["convex"],
                edge_floor=floors["edge"],
                pair_floor=floors["pair"],
                convex_weight=20.0,
                edge_weight=5.0,
                pair_weight=2.0,
            ),
            predictor,
            max_nfev=max_nfev,
            ftol=1e-10,
            xtol=1e-10,
            gtol=1e-10,
        )
        rec = make_point_record(target_t, sol.x, "corrected", sol)
        rec["dt"] = float(dt)
        rec["predictor"] = predictor_type

        # Convexity and edge length are checked before equality residual.
        convex_ok = rec["convexity_margin"] > 0.0 and rec["min_edge_length"] > 0.0
        finite_ok = all(
            math.isfinite(float(rec[key]))
            for key in ("convexity_margin", "min_edge_length", "eq_rms")
        )
        solver_ok = finite_ok and sol.cost <= max(
            1.0, 25.0 * accepted[-1].get("cost", sol.cost + 1e-9)
        )
        if convex_ok and solver_ok:
            accepted.append(rec)
            x_prev2 = x_prev
            x_prev = sol.x.copy()
            t = target_t
            dt = min(0.15, dt * 1.25)
            if (
                rec["convexity_margin"] < floors["convex"]
                or rec["min_edge_length"] < floors["edge"]
            ):
                termination = "convexity_floor_riding"
                # Continue only one tiny bit beyond the first floor ride; this is
                # the known failure mode and prevents recording residual-only wins.
                if (
                    rec["convexity_margin"] < 0.1 * floors["convex"]
                    or rec["min_edge_length"] < 0.1 * floors["edge"]
                ):
                    break
        else:
            rec["reject_reason"] = "convexity_or_solver_failure_checked_before_residual"
            rejected.append(rec)
            dt *= 0.5
            if dt < min_dt:
                termination = "step_underflow_after_convexity_collapse"
                break
    else:
        termination = "reached_t1"

    final_x = x_prev
    final_points = points_from_support(final_x)
    final_diag = diagnostics(final_points, rows)
    return {
        "drop": int(drop),
        "termination": termination,
        "accepted_points": accepted,
        "rejected_points": rejected[-10:],
        "accepted_count": len(accepted),
        "last_t": float(accepted[-1]["t"]),
        "final_x": [float(v) for v in final_x],
        "final_coordinates": [[float(a), float(b)] for a, b in final_points.tolist()],
        "final_radial_distances": [
            float(v) for v in np.linalg.norm(final_points, axis=1)
        ],
        "final_diagnostics": dataclasses.asdict(final_diag),
        "final_distance_table": distance_table(final_points, rows),
    }


def classify_run(
    paths: list[dict[str, Any]], exact_trigger: dict[str, float]
) -> tuple[str, list[str]]:
    notes: list[str] = []
    triggered = []
    for path in paths:
        diag = path["final_diagnostics"]
        if (
            diag["max_spread"] < exact_trigger["max_spread"]
            and diag["convexity_margin"] > exact_trigger["convexity"]
            and diag["min_edge_length"] > exact_trigger["min_edge_length"]
            and diag["min_pair_distance"] > exact_trigger["min_pair_distance"]
        ):
            triggered.append(path["drop"])
    if triggered:
        return "COUNTEREXAMPLE_CANDIDATE_NEEDS_EXACT_RECHECK", [
            f"exact verifier trigger reached for drops {triggered}"
        ]
    if all(path["termination"] != "reached_t1" for path in paths):
        notes.append("all paths terminated before t=1 or rode the convexity/edge floor")
        return "FAILED_APPROACH", notes
    if any(
        path["final_diagnostics"]["convexity_margin"] <= exact_trigger["convexity"]
        or path["final_diagnostics"]["min_edge_length"]
        <= exact_trigger["min_edge_length"]
        or path["final_diagnostics"]["min_pair_distance"]
        <= exact_trigger["min_pair_distance"]
        for path in paths
    ):
        notes.append(
            "some paths reached t=1 only with inadequate convexity, edge, or pair margin"
        )
        return "NUMERICAL_EVIDENCE", notes
    return "NUMERICAL_EVIDENCE", notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20260609)
    parser.add_argument("--attempts", type=int, default=4)
    parser.add_argument("--seed-max-nfev", type=int, default=220)
    parser.add_argument("--path-max-nfev", type=int, default=160)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/runs/mixed_radius_bipartite_fr_homotopy_seed20260609.json"),
    )
    args = parser.parse_args()

    t0 = time.time()
    rows = b20_fr_lift_pattern()
    rng = np.random.default_rng(args.seed)
    floors = {"convex": 1.0e-4, "edge": 1.0e-3, "pair": 1.0e-3}
    exact_trigger = {
        "max_spread": 1.0e-10,
        "convexity": 1.0e-3,
        "min_edge_length": 1.0e-3,
        "min_pair_distance": 1.0e-3,
    }

    seed_records: list[dict[str, Any]] = []
    paths: list[dict[str, Any]] = []
    for drop in range(4):
        x_seed, seed_record = solve_seed(
            rng,
            rows,
            drop,
            attempts=args.attempts,
            max_nfev=args.seed_max_nfev,
            floors=floors,
        )
        seed_records.append({"drop": drop, **seed_record})
        paths.append(track_path(x_seed, rows, drop, args.path_max_nfev, floors))

    trust_label, notes = classify_run(paths, exact_trigger)
    best_path = min(
        paths,
        key=lambda p: (
            p["final_diagnostics"]["max_spread"],
            -p["final_diagnostics"]["convexity_margin"],
        ),
    )
    elapsed = time.time() - t0
    artifact: dict[str, Any] = {
        "schema_version": "mixed_radius_bipartite_homotopy_v1",
        "trust_label": trust_label,
        "status": trust_label,
        "does_not_claim": [
            "general proof of Erdos Problem #97",
            "counterexample to Erdos Problem #97",
            "exact equality from floating point residuals",
            "historical Fishburn-Reeds coordinate reproduction",
        ],
        "notes": notes,
        "pattern_name": "B20_4x5_FR_lift_mixed_radius_bipartite_homotopy",
        "source_pattern_name": "B20_4x5_FR_lift",
        "n": 20,
        "seed": args.seed,
        "elapsed_sec": elapsed,
        "parameterization": {
            "name": "mixed_radius_bipartite_support_arc_family",
            "vertex_classes": {
                "A": [i for i, c in enumerate(class_labels()) if c == "A"],
                "B": [i for i, c in enumerate(class_labels()) if c == "B"],
            },
            "class_labels": class_labels(),
            "support_offsets": "h_i = 0.25 + exp(u_i), one independent u_i per vertex",
            "normal_angles": "2*pi*i/20, i=0..19",
            "normalization": "centroid removed, RMS radius set to 1, p0 rotation gauge",
            "bipartite_property": "for row i=5*a+b, selected witnesses have a parity opposite to center a",
            "per_vertex_radii_recorded_as": "radial distances from normalized centroid for every vertex; no shared class radius",
        },
        "homotopy": {
            "equations": "Rows from B20_4x5_FR_lift.  For each drop d, t=0 enforces the other three witnesses and t=1 enforces all four.",
            "corrector": "scipy.optimize.least_squares",
            "predictor": "constant first step, then secant predictor",
            "step_control": {
                "initial_dt": 0.05,
                "growth": 1.25,
                "max_dt": 0.15,
                "shrink_on_reject": 0.5,
                "min_dt": 1e-4,
                "acceptance_order": "check convexity_margin and min_edge_length before equality residual",
            },
            "floors": floors,
            "exact_recheck_trigger": exact_trigger,
        },
        "S": rows,
        "seed_records": seed_records,
        "paths": paths,
        "best_path_summary": {
            "drop": best_path["drop"],
            "termination": best_path["termination"],
            "last_t": best_path["last_t"],
            "final_diagnostics": best_path["final_diagnostics"],
        },
        # Existing repo verifier-compatible convenience fields point to the best path.
        "mode": "mixed_radius_bipartite_support_arc_homotopy",
        "success": trust_label == "COUNTEREXAMPLE_CANDIDATE_NEEDS_EXACT_RECHECK",
        "message": "; ".join(notes) if notes else trust_label,
        "loss": float(best_path["final_diagnostics"]["eq_rms"] ** 2),
        "eq_rms": best_path["final_diagnostics"]["eq_rms"],
        "max_spread": best_path["final_diagnostics"]["max_spread"],
        "max_rel_spread": best_path["final_diagnostics"]["max_rel_spread"],
        "convexity_margin": best_path["final_diagnostics"]["convexity_margin"],
        "min_edge_length": best_path["final_diagnostics"]["min_edge_length"],
        "min_pair_distance": best_path["final_diagnostics"]["min_pair_distance"],
        "x": best_path["final_x"],
        "coordinates": best_path["final_coordinates"],
        "distance_table": best_path["final_distance_table"],
        "pattern_family": "mixed-radius bipartite arc homotopy",
        "pattern_formula": "i=5*a+b; S_i={(a+1,b),(a+3,b),(a+1,b+2),(a+3,b-2)} mod (4,5)",
        "pattern_notes": "Numerical homotopy probe; convexity collapse is the primary observed obstruction.",
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "out": str(args.out),
                "trust_label": trust_label,
                "best_path_summary": artifact["best_path_summary"],
                "elapsed_sec": elapsed,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
