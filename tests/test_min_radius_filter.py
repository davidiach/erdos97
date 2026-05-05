from __future__ import annotations

from erdos97.min_radius_filter import (
    covered_witness_path_orders,
    minimum_radius_order_obstruction,
    radius_propagation_order_obstruction,
    radius_result_to_json,
    row_is_order_free_blocked,
    row_has_order_free_empty_gap,
    selected_pair_sources,
)
from erdos97.search import built_in_patterns


def test_min_radius_filter_kills_all_other_pentagon_pattern() -> None:
    S = [[j for j in range(5) if j != i] for i in range(5)]

    result = minimum_radius_order_obstruction(S, list(range(5)), "K5_all_other")

    assert result.obstructed
    assert result.possible_min_centers == []
    assert result.blocked_centers == list(range(5))
    assert all(row.blocked for row in result.rows)
    assert all(row_is_order_free_blocked(S, center) for center in range(5))
    assert result.order_free_empty_gap_centers == []

    propagation = radius_propagation_order_obstruction(S, list(range(5)), "K5_all_other")
    assert propagation.status == "EXACT_RADIUS_PROPAGATION_OBSTRUCTION"
    assert propagation.obstructed is True
    assert propagation.acyclic_choice is None
    payload = radius_result_to_json(propagation)
    assert payload["status_schema"] == "min_radius_filter.v1"
    assert payload["edge_direction"] == "source -> target means r_source < r_target; here target is the row center"


def test_min_radius_filter_c19_survives_natural_order() -> None:
    pattern = built_in_patterns()["C19_skew"]

    result = minimum_radius_order_obstruction(pattern.S, pattern=pattern.name)

    assert not result.obstructed
    assert result.blocked_centers == []
    assert result.possible_min_centers == list(range(19))
    assert result.rows[0].witness_order == [5, 9, 11, 16]
    assert result.rows[0].uncovered_consecutive_pairs == [(5, 9), (9, 11)]
    assert selected_pair_sources(pattern.S, 11, 16) == [11]
    assert row_has_order_free_empty_gap(pattern.S, 0)
    assert covered_witness_path_orders(pattern.S, 0) == []


def test_c13_sidon_has_local_covered_witness_paths() -> None:
    pattern = built_in_patterns()["C13_sidon_1_2_4_10"]

    result = minimum_radius_order_obstruction(pattern.S, pattern=pattern.name)
    paths = covered_witness_path_orders(pattern.S, 0)

    assert not row_has_order_free_empty_gap(pattern.S, 0)
    assert result.order_free_empty_gap_centers == []
    assert [4, 2, 1, 10] in paths


def test_c13_sidon_passes_natural_order_radius_propagation() -> None:
    pattern = built_in_patterns()["C13_sidon_1_2_4_10"]

    result = radius_propagation_order_obstruction(pattern.S, pattern=pattern.name)

    assert result.status == "PASS_RADIUS_PROPAGATION"
    assert result.obstructed is False
    assert result.acyclic_choice is not None
    assert len(result.acyclic_choice) == pattern.n


def test_radius_propagation_node_limit_reports_unknown() -> None:
    pattern = built_in_patterns()["C13_sidon_1_2_4_10"]

    result = radius_propagation_order_obstruction(
        pattern.S,
        pattern=pattern.name,
        max_nodes=1,
    )

    assert result.status == "UNKNOWN_RADIUS_PROPAGATION_NODE_LIMIT"
    assert result.obstructed is None
    assert result.search_truncated
