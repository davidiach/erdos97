from __future__ import annotations

import sympy as sp

from erdos97.two_orbit_radius_propagation import (
    alternating_turns,
    selected_distance_residuals,
    summary_to_json,
    two_orbit_summary,
)


def test_forced_ratio_solves_both_distance_equations() -> None:
    for t in (1, 2, 3):
        summary = two_orbit_summary(t)

        assert sp.simplify(summary.distance_equation) == 0
        assert sp.simplify(summary.a_distance_gap) == 0
        assert sp.simplify(summary.b_distance_gap) == 0


def test_forced_ratio_violates_convexity_threshold() -> None:
    for t in (1, 2, 3):
        summary = two_orbit_summary(t)

        assert sp.N(summary.cos_minus_ratio, 50) > 0
        assert sp.N(summary.sec_minus_ratio, 50) > 0
        assert sp.N(summary.turn_at_b, 50) < 0
        assert sp.N(summary.turn_at_a, 50) > 0
        assert summary.forced_concave


def test_explicit_selected_distances_for_t2_are_exactly_equal() -> None:
    residuals = selected_distance_residuals(2)

    assert len(residuals) == 16
    assert all(
        sp.simplify(residual) == 0
        for row_residuals in residuals
        for residual in row_residuals
    )


def test_alternating_turns_for_t2_have_reflex_b_vertices() -> None:
    turns = alternating_turns(2)

    assert len(turns) == 16
    assert all(sp.N(turns[2 * j], 50) < 0 for j in range(8))
    assert all(sp.N(turns[2 * j + 1], 50) > 0 for j in range(8))


def test_json_summary_keeps_claim_boundary_explicit() -> None:
    row = summary_to_json(two_orbit_summary(2))

    assert row["status"] == "exact_ansatz_obstruction_not_general_proof"
    assert row["forced_concave"] is True
