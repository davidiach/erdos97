from __future__ import annotations

from fractions import Fraction

import pytest

from erdos97.two_parabola_lens_closure import (
    fraction_to_json,
    grid_edges,
    grid_search_summary,
    greatest_fixed_point_for_c,
    summarize_grid_case,
    zero_sum_pattern_summary,
)


def test_grid_edges_include_known_zero_sum_quadruple() -> None:
    edges = grid_edges(max_abs=4, denominator=1)
    target = (
        Fraction(-2),
        Fraction(-1),
        Fraction(0),
        Fraction(3),
    )

    matching = [edge for edge in edges if edge.witnesses == target]

    assert len(matching) == 1
    assert matching[0].center == 3
    assert matching[0].c_value == -25


def test_tiny_integer_grid_has_no_four_point_fixed_closure() -> None:
    summary = summarize_grid_case(max_abs=4, denominator=1)

    assert summary.closure_found is False
    assert summary.c_value_count == 6
    assert summary.max_fixed_point_size < 4


def test_greatest_fixed_point_detects_synthetic_closure() -> None:
    edges = grid_edges(max_abs=4, denominator=1)
    c_edges = [edge for edge in edges if edge.c_value == -25]

    fixed_point = greatest_fixed_point_for_c(c_edges)

    assert fixed_point == frozenset()


@pytest.mark.slow
def test_default_summary_keeps_claim_boundary_explicit_for_small_case() -> None:
    payload = grid_search_summary(cases=((1, 4),))

    assert payload["schema"] == "erdos97.two_parabola_lens_grid_search.v1"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert payload["closure_found"] is False
    assert payload["opposite_chain_size_floor"]["min_total_points"] == 16
    assert "not a proof" in str(payload["claim_scope"])
    assert "strict-convex lens inequalities" in str(payload["does_not_check"])


@pytest.mark.slow
def test_zero_sum_pattern_summary_for_seven_points() -> None:
    summary = zero_sum_pattern_summary(7)

    assert summary.max_zero_sum_four_subsets == 5
    assert summary.feasible_pattern_count_at_max > 0
    assert summary.checked_pattern_count_at_next == 210


def test_fraction_to_json_is_stable() -> None:
    assert fraction_to_json(Fraction(3, 1)) == "3"
    assert fraction_to_json(Fraction(-7, 12)) == "-7/12"
