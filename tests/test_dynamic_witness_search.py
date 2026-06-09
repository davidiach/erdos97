"""Tests for the dynamic-witness (free-pattern) search module."""

from __future__ import annotations

import math

import numpy as np

from erdos97.dynamic_witness_search import (
    GuardConfig,
    evaluate_configuration,
    refine,
    search_cell,
    squared_distance_rows,
    unfold_orbits,
)


def p24_control_points() -> np.ndarray:
    """Float copy of the exact 24-point metric-linear nonconvex control.

    Two C_12 orbits: radius 1 at angle 0 and radius 2*cos(pi/12) at angle
    pi/12.  Every vertex has four exactly equidistant other vertices, but the
    cyclic angular order is not convex (see
    ``scripts/verify_p24_metric_linear_nonconvex.py``).
    """

    return unfold_orbits(
        12,
        [1.0, 2.0 * math.cos(math.pi / 12.0)],
        [0.0, math.pi / 12.0],
    )


def test_unfold_orbits_shape_and_symmetry() -> None:
    points = unfold_orbits(7, [1.0, 0.6, 1.3], [0.0, 0.31, 0.62])
    assert points.shape == (21, 2)
    rows = squared_distance_rows(points, [0, 3])
    rotated = sorted(rows[1].tolist())
    base = sorted(squared_distance_rows(points, [0])[0].tolist())
    base_orbitmate = sorted(
        squared_distance_rows(points, [1])[0].tolist()
    )
    assert np.allclose(base, base_orbitmate, atol=1e-12)
    assert len(rotated) == 20


def test_p24_control_has_zero_deficiency_but_not_convex() -> None:
    points = p24_control_points()
    centers = [0, 12]
    report = evaluate_configuration(points, centers, GuardConfig())
    assert report["max_relative_spread"] < 1e-12
    assert report["strictly_convex"] is False
    assert report["guards_satisfied"] is False


def test_regular_nonagon_has_positive_deficiency() -> None:
    points = unfold_orbits(9, [1.0], [0.0])
    report = evaluate_configuration(points, [0], GuardConfig())
    assert report["strictly_convex"] is True
    assert report["max_relative_spread"] > 0.1


def test_refine_converges_to_known_nonconvex_solution() -> None:
    guards = GuardConfig(require_convexity=False)
    x0 = np.array([math.log(2.0 * math.cos(math.pi / 12.0)) + 0.05, math.pi / 12.0 + 0.03])
    _, report = refine(12, 2, x0, guards, max_cycles=6)
    assert report["max_relative_spread"] < 1e-10
    assert report["strictly_convex"] is False


def test_search_cell_smoke() -> None:
    record = search_cell(4, 2, restarts=2, seed=7, max_cycles=4)
    assert record["n"] == 8
    best = record["best"]
    assert set(best) >= {
        "radii",
        "thetas",
        "guards_satisfied",
        "strictly_convex",
        "max_relative_spread",
        "windows",
    }
    assert len(best["windows"]) == 2
    assert all(len(entry["witnesses"]) == 4 for entry in best["windows"])
