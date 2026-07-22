from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "exploration"
    / "search_complex_three_mode_cyclic.py"
)
SPEC = importlib.util.spec_from_file_location("complex_three_mode_search", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
SEARCH = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SEARCH
SPEC.loader.exec_module(SEARCH)


def test_lifted_rows_match_direct_squared_distances() -> None:
    n = 13
    k = 4
    ell = 9
    center = 3
    coefficient_c = 0.2 + 0.1j
    coefficient_d = -0.15 + 0.3j
    predicted = SEARCH.lifted_distance_rows(n, k, ell, center) @ (
        SEARCH.lifted_variables(coefficient_c, coefficient_d)
    )

    point_array = SEARCH.points(n, k, ell, coefficient_c, coefficient_d)
    direct = []
    for shift in range(1, n):
        delta = point_array[(center + shift) % n] - point_array[center]
        direct.append(float(np.dot(delta, delta)))

    assert np.allclose(predicted, direct, atol=1.0e-12, rtol=1.0e-12)


def test_regular_polygon_is_convex_but_not_a_fourfold_candidate() -> None:
    report = SEARCH.evaluate(12, 3, 5, np.zeros(4), SEARCH.SearchConfig())

    assert report["strictly_convex"] is True
    assert report["candidate"] is False
    assert report["max_relative_spread"] > 1.0e-6


def test_duplicate_two_mode_mirage_is_rejected() -> None:
    coefficient_c = 1j * (2.0 + math.sqrt(3.0))
    report = SEARCH.evaluate(
        12,
        7,
        5,
        np.asarray([coefficient_c.real, coefficient_c.imag, 0.0, 0.0]),
        SEARCH.SearchConfig(),
    )

    assert report["max_relative_spread"] < 1.0e-12
    assert report["strictly_convex"] is False
    assert report["candidate"] is False


def test_special_starts_honor_restart_budget() -> None:
    for budget in (1, 2, 3, 5):
        generated = list(SEARCH.starts(12, 7, 9, budget, seed=17))
        assert len(generated) == budget
