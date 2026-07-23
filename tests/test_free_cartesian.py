from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

from erdos97.free_cartesian import (
    CartesianConfig,
    convex_starts,
    pack_points,
    residual_jacobian,
    search_fixed_order,
    unpack_points,
)
from erdos97.search import convexity_margin


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "exploration"
    / "search_free_cartesian_sparse.py"
)
SPEC = importlib.util.spec_from_file_location("free_cartesian_sparse_search", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
SEARCH = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SEARCH
SPEC.loader.exec_module(SEARCH)


def toy_pattern(n: int = 6) -> list[list[int]]:
    return [
        [((center + offset) % n) for offset in (1, 2, 3, 4)]
        for center in range(n)
    ]


def finite_difference_jacobian(function, vector: np.ndarray) -> np.ndarray:
    columns = []
    step = 1.0e-7
    for index in range(len(vector)):
        left = vector.copy()
        right = vector.copy()
        left[index] -= step
        right[index] += step
        columns.append((function(right) - function(left)) / (2.0 * step))
    return np.column_stack(columns)


def test_pack_unpack_fixes_similarity_gauge() -> None:
    points = np.asarray(
        [[2.0, -1.0], [4.0, 2.0], [1.0, 4.0], [-2.0, 1.0]], dtype=float
    )
    normalized = unpack_points(pack_points(points), len(points))

    assert np.allclose(normalized[0], [0.0, 0.0])
    assert np.allclose(normalized[1], [1.0, 0.0])


def test_full_analytic_jacobian_matches_finite_difference() -> None:
    pattern = toy_pattern()
    vector = next(convex_starts(len(pattern), restarts=1, seed=4))
    config = CartesianConfig(
        pair_floor=10.0,
        side_floor=10.0,
        weight_pair=3.0,
        weight_side=4.0,
    )
    residuals, analytic = residual_jacobian(vector, pattern, config)
    numerical = finite_difference_jacobian(
        lambda value: residual_jacobian(value, pattern, config)[0], vector
    )

    assert residuals.shape == (3 * len(pattern) + 15 + 24,)
    assert analytic.shape == numerical.shape
    assert np.allclose(analytic, numerical, atol=2.0e-7, rtol=2.0e-7)


def test_random_starts_preserve_natural_strict_convexity() -> None:
    starts = list(convex_starts(12, restarts=8, seed=17))

    assert len(starts) == 8
    assert all(convexity_margin(unpack_points(start, 12)) > 0.0 for start in starts)


def test_guard_rows_stay_fixed_and_optimizer_smoke_runs() -> None:
    pattern = toy_pattern()
    vector = next(convex_starts(len(pattern), restarts=1, seed=9))
    config = CartesianConfig()
    residuals, jacobian = residual_jacobian(vector, pattern, config)

    assert residuals.shape == (3 * len(pattern) + 15 + 24,)
    assert jacobian.shape == (len(residuals), len(vector))
    report = search_fixed_order(
        pattern, restarts=1, max_nfev=3, seed=9, config=config
    )
    assert report["nfev"] <= 3


def test_sparse_order_sampler_is_deterministic_and_rotation_fixed() -> None:
    first = SEARCH.sampled_orders(25, 4, 123)
    second = SEARCH.sampled_orders(25, 4, 123)

    assert first == second
    assert len({tuple(order) for order in first}) == 4
    assert all(order[0] == 0 and sorted(order) == list(range(25)) for order in first)
