"""Dynamic-witness (free-pattern) numerical search for Erdos Problem #97.

Unlike ``erdos97.search``, which optimizes coordinates for one fixed
registered selected-witness pattern at a time, this module lets every center
re-select its own best witness 4-set at every evaluation, via a sliding
window over that center's sorted squared distances.  A single continuous
optimization run therefore probes every selected-witness pattern reachable by
the configuration family at once, instead of only the registered catalog
patterns.

Modes:

* Equivariant mode: cyclic symmetry ``C_m`` with ``t`` free orbits
  (``n = m * t`` points, ``2 * t - 2`` free parameters after fixing the
  scale and rotation gauges).  Only the ``t`` orbit representatives need
  witness windows, so evaluations stay cheap for large ``n``.
* Asymmetric mode: ``m = 1`` and ``t = n`` reduces to a fully general
  point search.

Anti-degeneracy guards are part of the objective, not an afterthought: the
known cheap failure mode for this problem (seen both in the historical B12
near-miss and in the published 2025 AlphaEvolve attempt on this problem) is
collapsing many points into near-coincident clusters so that float distances
become indistinguishable.  All searches here keep hard normalized floors on
pairwise separation, angular gaps, and the strict-convexity cross-product
margin, and every reported metric is recomputed at the final point.

Trust label for all outputs: ``NUMERICAL_EVIDENCE`` / ``HEURISTIC`` search
diagnostics only.  Nothing in this module is a proof, and nothing in this
module is a counterexample; the repo exactification standards apply before
any claim upgrade.
"""

from __future__ import annotations

import dataclasses
import math
import time
from typing import Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import least_squares

Array = NDArray[np.float64]

WITNESS_COUNT = 4


@dataclasses.dataclass(frozen=True)
class GuardConfig:
    """Normalized anti-degeneracy floors and penalty weights.

    ``convex_floor_scale`` is measured relative to the consecutive-edge
    cross-product margin of a regular n-gon with the same diameter, which
    scales like ``2 * pi**3 / n**3`` after dividing by the squared diameter.
    ``pair_floor_scale`` and ``angle_floor_scale`` are measured relative to
    the mean spacing ``1 / n`` (as a fraction of the diameter) and the mean
    angular gap ``2 * pi / n``.
    """

    convex_floor_scale: float = 0.05
    pair_floor_scale: float = 0.10
    angle_floor_scale: float = 0.10
    require_convexity: bool = True
    weight_eq: float = 1.0
    weight_convex: float = 30.0
    weight_pair: float = 30.0
    weight_angle: float = 10.0

    def convex_floor(self, n: int) -> float:
        return self.convex_floor_scale * 2.0 * math.pi**3 / float(n**3)

    def pair_floor(self, n: int) -> float:
        return self.pair_floor_scale / float(n)

    def angle_floor(self, n: int) -> float:
        return self.angle_floor_scale * 2.0 * math.pi / float(n)


def unfold_orbits(m: int, radii: Sequence[float], thetas: Sequence[float]) -> Array:
    """Return the ``t * m`` points of ``t`` concentric ``C_m`` orbits.

    Point ``j * m + k`` is orbit ``j`` rotated by ``2 * pi * k / m``.
    """

    radii_arr = np.asarray(radii, dtype=float)
    thetas_arr = np.asarray(thetas, dtype=float)
    if radii_arr.shape != thetas_arr.shape:
        raise ValueError("radii and thetas must have the same shape")
    steps = 2.0 * np.pi * np.arange(m) / float(m)
    angles = thetas_arr[:, None] + steps[None, :]
    x = radii_arr[:, None] * np.cos(angles)
    y = radii_arr[:, None] * np.sin(angles)
    return np.stack([x.ravel(), y.ravel()], axis=1)


def squared_distance_rows(points: Array, centers: Sequence[int]) -> list[Array]:
    """Squared distances from each requested center to all other points."""

    rows: list[Array] = []
    for center in centers:
        delta = points - points[center]
        sq = np.einsum("ij,ij->i", delta, delta)
        rows.append(np.delete(sq, center))
    return rows


def best_window(sq_row: Array) -> tuple[float, float, Array]:
    """Best (min-spread) sliding 4-window of one sorted squared-distance row.

    Returns ``(spread, mean_value, indices_into_row)`` where ``indices``
    refer to the unsorted input row.
    """

    order = np.argsort(sq_row, kind="stable")
    sorted_sq = sq_row[order]
    spreads = sorted_sq[WITNESS_COUNT - 1 :] - sorted_sq[: 1 - WITNESS_COUNT]
    best = int(np.argmin(spreads))
    window = order[best : best + WITNESS_COUNT]
    mean_value = float(np.mean(sorted_sq[best : best + WITNESS_COUNT]))
    return float(spreads[best]), mean_value, window


def deficiency_profile(
    points: Array, centers: Sequence[int]
) -> list[dict[str, object]]:
    """Per-center best dynamic witness windows, as global point indices."""

    profile: list[dict[str, object]] = []
    for center, sq_row in zip(centers, squared_distance_rows(points, centers)):
        spread, mean_value, window = best_window(sq_row)
        witness_indices = [int(w) if w < center else int(w) + 1 for w in window]
        rel = spread / mean_value if mean_value > 0.0 else float("inf")
        profile.append(
            {
                "center": int(center),
                "witnesses": sorted(witness_indices),
                "spread": spread,
                "mean_sq_distance": mean_value,
                "relative_spread": rel,
            }
        )
    return profile


def convexity_metrics(points: Array) -> dict[str, float]:
    """Strict-convexity diagnostics for the angular-order polygon.

    The points are sorted by angle around the centroid; the closed polygon in
    that order winds once around the centroid, so it is strictly convex if
    and only if every consecutive cross product is strictly positive and all
    angular gaps are strictly positive.  All returned quantities are
    normalized: cross products by the squared diameter, separations by the
    diameter.
    """

    n = len(points)
    centroid = points.mean(axis=0)
    shifted = points - centroid
    angles = np.arctan2(shifted[:, 1], shifted[:, 0])
    order = np.argsort(angles, kind="stable")
    poly = points[order]
    gaps = np.diff(np.concatenate([np.sort(angles), [np.sort(angles)[0] + 2 * np.pi]]))

    edges = np.roll(poly, -1, axis=0) - poly
    cross = edges[:, 0] * np.roll(edges[:, 1], -1) - edges[:, 1] * np.roll(
        edges[:, 0], -1
    )

    diffs = points[:, None, :] - points[None, :, :]
    pair_sq = np.einsum("ijk,ijk->ij", diffs, diffs)
    diameter = math.sqrt(float(pair_sq.max()))
    pair_sq_off = pair_sq + np.diag(np.full(n, np.inf))
    min_pair = math.sqrt(float(pair_sq_off.min()))
    min_edge = float(np.sqrt(np.einsum("ij,ij->i", edges, edges)).min())

    if diameter <= 0.0:
        return {
            "diameter": 0.0,
            "min_cross_normalized": float("-inf"),
            "min_angle_gap": 0.0,
            "min_pair_normalized": 0.0,
            "min_edge_normalized": 0.0,
        }
    return {
        "diameter": diameter,
        "min_cross_normalized": float(cross.min()) / diameter**2,
        "min_angle_gap": float(gaps.min()),
        "min_pair_normalized": min_pair / diameter,
        "min_edge_normalized": min_edge / diameter,
    }


def evaluate_configuration(
    points: Array, centers: Sequence[int], guards: GuardConfig
) -> dict[str, object]:
    """Exact (non-smoothed) diagnostics for one configuration."""

    n = len(points)
    profile = deficiency_profile(points, centers)
    convex = convexity_metrics(points)
    max_spread = max(float(entry["spread"]) for entry in profile)
    max_rel = max(float(entry["relative_spread"]) for entry in profile)
    strictly_convex = (
        convex["min_cross_normalized"] > 0.0 and convex["min_angle_gap"] > 0.0
    )
    guards_ok = convex["min_pair_normalized"] >= guards.pair_floor(n)
    if guards.require_convexity:
        guards_ok = (
            guards_ok
            and convex["min_cross_normalized"] >= guards.convex_floor(n)
            and convex["min_angle_gap"] >= guards.angle_floor(n)
        )
    return {
        "n": n,
        "max_window_spread": max_spread,
        "max_relative_spread": max_rel,
        "strictly_convex": bool(strictly_convex),
        "guards_satisfied": bool(guards_ok),
        "convexity": convex,
        "windows": profile,
    }


def _unpack(x: Array, t: int) -> tuple[Array, Array]:
    radii = np.concatenate([[1.0], np.exp(x[: t - 1])])
    thetas = np.concatenate([[0.0], x[t - 1 :]])
    return radii, thetas


def _residuals(
    x: Array,
    m: int,
    t: int,
    assignments: list[Array],
    guards: GuardConfig,
) -> Array:
    radii, thetas = _unpack(x, t)
    points = unfold_orbits(m, radii, thetas)
    n = len(points)
    centers = [j * m for j in range(t)]

    parts: list[Array] = []
    for center, witnesses in zip(centers, assignments):
        delta = points[witnesses] - points[center]
        sq = np.einsum("ij,ij->i", delta, delta)
        parts.append(guards.weight_eq * (sq - sq.mean()))

    convex = convexity_metrics(points)
    diameter = convex["diameter"]
    if diameter <= 0.0:
        parts.append(np.full(3, 1e6))
        return np.concatenate(parts)

    centroid = points.mean(axis=0)
    shifted = points - centroid
    angles = np.arctan2(shifted[:, 1], shifted[:, 0])
    order = np.argsort(angles, kind="stable")
    poly = points[order]
    edges = np.roll(poly, -1, axis=0) - poly
    cross = (
        edges[:, 0] * np.roll(edges[:, 1], -1) - edges[:, 1] * np.roll(edges[:, 0], -1)
    ) / diameter**2
    sorted_angles = np.sort(angles)
    gaps = np.diff(np.concatenate([sorted_angles, [sorted_angles[0] + 2 * np.pi]]))

    if guards.require_convexity:
        parts.append(guards.weight_convex * np.maximum(0.0, guards.convex_floor(n) - cross))
        parts.append(guards.weight_angle * np.maximum(0.0, guards.angle_floor(n) - gaps))

    diffs = points[:, None, :] - points[None, :, :]
    pair = np.sqrt(np.einsum("ijk,ijk->ij", diffs, diffs)) / diameter
    iu = np.triu_indices(n, k=1)
    parts.append(guards.weight_pair * np.maximum(0.0, guards.pair_floor(n) - pair[iu]))

    return np.concatenate(parts)


def _assign(points: Array, centers: Sequence[int]) -> list[Array]:
    assignments: list[Array] = []
    for center, sq_row in zip(centers, squared_distance_rows(points, centers)):
        _, _, window = best_window(sq_row)
        global_idx = np.array(
            [int(w) if w < center else int(w) + 1 for w in window], dtype=int
        )
        assignments.append(global_idx)
    return assignments


def refine(
    m: int,
    t: int,
    x0: Array,
    guards: GuardConfig,
    max_cycles: int = 12,
    max_nfev: int = 400,
) -> tuple[Array, dict[str, object]]:
    """Alternate dynamic witness assignment with Levenberg-Marquardt steps."""

    if t < 2:
        raise ValueError("dynamic-witness refinement needs at least two orbits")
    x = np.array(x0, dtype=float)
    centers = [j * m for j in range(t)]
    best_x = x.copy()
    best_metric = float("inf")
    previous_keys: set[tuple[tuple[int, ...], ...]] = set()
    for _ in range(max_cycles):
        radii, thetas = _unpack(x, t)
        points = unfold_orbits(m, radii, thetas)
        assignments = _assign(points, centers)
        key = tuple(tuple(int(w) for w in a) for a in assignments)
        x_before = x.copy()
        result = least_squares(
            _residuals,
            x,
            args=(m, t, assignments, guards),
            method="trf",
            max_nfev=max_nfev,
        )
        x = result.x
        radii, thetas = _unpack(x, t)
        points = unfold_orbits(m, radii, thetas)
        report = evaluate_configuration(points, centers, guards)
        feasible = bool(report["guards_satisfied"])
        metric = float(report["max_relative_spread"]) + (0.0 if feasible else 1e3)
        if metric < best_metric:
            best_metric = metric
            best_x = x.copy()
        if key in previous_keys and np.linalg.norm(x - x_before) < 1e-10:
            break
        previous_keys.add(key)
    radii, thetas = _unpack(best_x, t)
    points = unfold_orbits(m, radii, thetas)
    final_report = evaluate_configuration(points, centers, guards)
    return best_x, final_report


def convex_ok(report: dict[str, object], guards: GuardConfig) -> bool:
    """Strictly convex with the anti-cluster pair floor still enforced.

    This is the claim-relevant gate: the convexity *floor* is only a search
    aid, while a genuine candidate merely needs a strictly positive margin
    plus non-collapsing points.
    """

    convex = report["convexity"]
    return bool(
        report["strictly_convex"]
        and convex["min_pair_normalized"] >= guards.pair_floor(int(report["n"]))
    )


def _record(
    m: int,
    t: int,
    restart: int,
    x: Array,
    report: dict[str, object],
    guards: GuardConfig,
) -> dict[str, object]:
    radii, thetas = _unpack(x, t)
    n = m * t
    convex = report["convexity"]
    return {
        "m": m,
        "t": t,
        "n": n,
        "restart": restart,
        "radii": [float(r) for r in radii],
        "thetas": [float(v) for v in thetas],
        "guards_satisfied": bool(report["guards_satisfied"]),
        "strictly_convex": bool(report["strictly_convex"]),
        # Riding the anti-cluster floor marks the known degenerate exploit:
        # near-coincident point clusters that fake small spreads.
        "near_pair_floor": bool(
            convex["min_pair_normalized"] < 1.5 * guards.pair_floor(n)
        ),
        "max_window_spread": float(report["max_window_spread"]),
        "max_relative_spread": float(report["max_relative_spread"]),
        "convexity": convex,
        "windows": report["windows"],
    }


def search_cell(
    m: int,
    t: int,
    restarts: int,
    seed: int,
    guards: GuardConfig | None = None,
    max_cycles: int = 12,
) -> dict[str, object]:
    """Multi-restart dynamic-witness search for one ``(m, t)`` cell.

    Each restart runs the floor-guarded alternation and then an annealing
    pass with the convexity/angle floors lowered, because the meaningful
    convex optimum can sit below the conservative default floor.  Results are
    reported in three tiers: best under the default floors, best strictly
    convex (with the anti-cluster pair floor), and best overall.
    """

    if guards is None:
        guards = GuardConfig()
    annealed_guards = dataclasses.replace(
        guards,
        convex_floor_scale=guards.convex_floor_scale * 0.05,
        angle_floor_scale=guards.angle_floor_scale * 0.3,
    )
    rng = np.random.default_rng(seed)
    n = m * t
    centers = [j * m for j in range(t)]
    start = time.monotonic()
    best_feasible: dict[str, object] | None = None
    best_convex: dict[str, object] | None = None
    best_any: dict[str, object] | None = None
    feasible_hits = 0
    convex_hits = 0
    for restart in range(restarts):
        # Near-regular interleaved start: orbit j near angle j * 2*pi / n
        # with unit-ish radius keeps the initial polygon strictly convex, so
        # the optimizer explores outward from the feasible region instead of
        # trying to repair a random star.  The jitter scale grows with the
        # restart index for diversity.
        jitter = 0.02 + 0.28 * (restart / max(1, restarts - 1))
        u = rng.normal(0.0, jitter, size=t - 1)
        base_angles = (np.arange(1, t) * 2.0 * np.pi / float(n)) % (2.0 * np.pi / m)
        th = base_angles + rng.normal(0.0, jitter * 2.0 * np.pi / n, size=t - 1)
        x0 = np.concatenate([u, th])
        stage_results: list[tuple[Array, dict[str, object]]] = []
        x1, _ = refine(m, t, x0, guards, max_cycles=max_cycles)
        radii, thetas = _unpack(x1, t)
        report1 = evaluate_configuration(
            unfold_orbits(m, radii, thetas), centers, guards
        )
        stage_results.append((x1, report1))
        if guards.require_convexity:
            x2, _ = refine(m, t, x1, annealed_guards, max_cycles=4)
            radii, thetas = _unpack(x2, t)
            report2 = evaluate_configuration(
                unfold_orbits(m, radii, thetas), centers, guards
            )
            stage_results.append((x2, report2))
        restart_feasible = False
        restart_convex = False
        for x, report in stage_results:
            rel = float(report["max_relative_spread"])
            record = _record(m, t, restart, x, report, guards)
            if report["guards_satisfied"]:
                restart_feasible = True
                if best_feasible is None or rel < float(
                    best_feasible["max_relative_spread"]
                ):
                    best_feasible = record
            if convex_ok(report, guards):
                restart_convex = True
                if best_convex is None or rel < float(
                    best_convex["max_relative_spread"]
                ):
                    best_convex = record
            if best_any is None or rel < float(best_any["max_relative_spread"]):
                best_any = record
        feasible_hits += int(restart_feasible)
        convex_hits += int(restart_convex)
    elapsed = time.monotonic() - start
    assert best_any is not None
    return {
        "m": m,
        "t": t,
        "n": n,
        "restarts": restarts,
        "seed": seed,
        "require_convexity": guards.require_convexity,
        "feasible_restarts": feasible_hits,
        "convex_restarts": convex_hits,
        "elapsed_sec": elapsed,
        "best_feasible": best_feasible,
        "best_convex": best_convex,
        "best": best_any,
    }
