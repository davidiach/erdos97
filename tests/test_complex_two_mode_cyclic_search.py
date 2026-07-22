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
    / "search_complex_two_mode_cyclic.py"
)
SPEC = importlib.util.spec_from_file_location("complex_two_mode_screen", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
SCREEN = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SCREEN
SPEC.loader.exec_module(SCREEN)


def test_distance_coefficients_match_direct_complex_distances() -> None:
    n = 12
    k = 7
    center = 3
    coefficient = 0.3 + 0.2j
    affine_rows = SCREEN.row_coefficients(n, k, center)
    lifted = np.asarray(
        [1.0, abs(coefficient) ** 2, coefficient.real, coefficient.imag]
    )
    predicted = affine_rows @ lifted

    points = SCREEN.points(n, k, coefficient)
    direct = []
    for shift in range(1, n):
        delta = points[(center + shift) % n] - points[center]
        direct.append(float(np.dot(delta, delta)))

    assert np.allclose(predicted, direct, atol=1.0e-12, rtol=1.0e-12)


def test_duplicate_exact_equality_mirage_is_not_convex() -> None:
    coefficient = 1j * (2.0 + math.sqrt(3.0))
    report = SCREEN.all_row_report(12, 7, coefficient)

    assert report["max_relative_spread"] < 1.0e-12
    assert report["min_pair_normalized"] < 1.0e-12
    assert report["strictly_convex"] is False


def test_rank_one_n12_k7_branch_is_cross_row_enumerated() -> None:
    _candidates, stats = SCREEN.rank_one_intersection_candidates(
        12, 7, SCREEN.ScreenConfig()
    )

    assert stats["rank_zero_identity_quadruples"] == 0
    assert stats["rank_one_unique_planes"] == 1
    assert stats["rank_one_intersection_candidates"] > 0
    assert stats["rank_one_continuous_all_row_planes"] == 0


def test_n9_k4_screen_has_no_valid_hit() -> None:
    report = SCREEN.screen_case(9, 4, SCREEN.ScreenConfig())

    assert report["hits"] == []
    assert report["rank_zero_identity_quadruples"] == 0
    assert report["invalid_exact_like_count"] > 0
    invalid = report["best_invalid_exact_like"]
    assert invalid is not None
    assert invalid["max_relative_spread"] < SCREEN.ScreenConfig().equality_tol
    assert invalid["strictly_convex"] is False
