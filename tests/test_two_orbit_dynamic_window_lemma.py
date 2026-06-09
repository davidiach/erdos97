"""Tests for the two-orbit dynamic-window lemma audit checker."""

from __future__ import annotations

import math

import mpmath as mp
import numpy as np

from erdos97.dynamic_witness_search import GuardConfig, evaluate_configuration, unfold_orbits
from scripts.check_two_orbit_dynamic_window_lemma import (
    check_m,
    interval_form_root_exists,
    valid_pairs,
    window_root_exists,
)


def test_valid_pairs_counts() -> None:
    assert valid_pairs(3) == [(1, 1)]
    assert len(valid_pairs(9)) == 4 * 4
    assert len(valid_pairs(10)) == 4 * 5


def test_window_clear_up_to_m_60_with_single_boundary_hit() -> None:
    total_boundary = 0
    for m in range(3, 61):
        record = check_m(m)
        assert record["window_roots"] == [], f"unexpected window root at m={m}"
        total_boundary += record["boundary_hits"]
    assert total_boundary == 1


def test_m3_boundary_is_exactly_sec_h() -> None:
    in_window, boundary = window_root_exists(3, 1, 1)
    assert in_window is False
    assert boundary == 1
    assert interval_form_root_exists(3, 1, 1) is False
    # The boundary root solves E_A at exactly x = sec(pi/3) = 2.
    h = mp.pi / 3
    x = 1 / mp.cos(h)
    residual = x * x + 1 - 2 * x * mp.cos(h) - 4 * mp.sin(h) ** 2
    assert abs(residual) < mp.mpf("1e-50")


def test_half_step_two_orbit_deficiency_positive_inside_window() -> None:
    # Numerical cross-check against the dynamic-witness evaluator: across the
    # strict-convexity window for m = 7, every half-step two-orbit
    # configuration keeps a positive dynamic-witness deficiency.
    m = 7
    h = math.pi / m
    guards = GuardConfig()
    worst = float("inf")
    for x in np.linspace(math.cos(h) + 1e-3, 1.0 / math.cos(h) - 1e-3, 41):
        points = unfold_orbits(m, [1.0, float(x)], [0.0, h])
        report = evaluate_configuration(points, [0, m], guards)
        assert report["strictly_convex"] is True
        worst = min(worst, float(report["max_relative_spread"]))
    assert worst > 1e-4
