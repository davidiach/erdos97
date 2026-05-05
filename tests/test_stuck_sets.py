from __future__ import annotations

from erdos97.search import built_in_patterns
from erdos97.stuck_sets import (
    fragile_cover_snapshot,
    find_minimal_stuck_sets,
    forward_ear_order,
    greedy_peeling_run,
    is_stuck_subset,
    optimize_radius_choice_edges,
    pattern_filter_snapshot,
    radius_propagation_obstruction,
    radius_result_to_json,
    radius_choice_optimization_to_json,
    result_to_json,
)

N9_RECTANGLE_TRAP_PATTERN = [
    [1, 2, 3, 8],
    [0, 2, 4, 7],
    [1, 3, 5, 7],
    [1, 4, 6, 8],
    [0, 2, 5, 6],
    [3, 4, 6, 7],
    [2, 5, 7, 8],
    [0, 3, 6, 8],
    [0, 1, 4, 5],
]


def test_detects_fixed_selection_stuck_subset() -> None:
    S = [
        [1, 2, 4, 5],
        [0, 2, 4, 5],
        [0, 1, 4, 5],
        [0, 1, 4, 5],
        [0, 1, 2, 3],
        [0, 1, 2, 3],
    ]

    assert is_stuck_subset(S, [0, 1, 2, 3])

    result = find_minimal_stuck_sets(S)

    assert result.found
    assert result.key_peeling_ok is False
    assert result.minimal_size == 4
    assert result.examples[0].vertices == [0, 1, 2, 3]
    assert [row.internal_count for row in result.examples[0].rows] == [2, 2, 2, 2]


def test_forward_ear_order_is_reported_separately_from_stuck_sets() -> None:
    S = [
        [1, 2, 4, 5],
        [0, 2, 4, 5],
        [0, 1, 4, 5],
        [0, 1, 4, 5],
        [0, 1, 2, 3],
        [0, 1, 2, 3],
    ]

    forward = forward_ear_order(S)
    stuck = find_minimal_stuck_sets(S)
    greedy = greedy_peeling_run(S)
    payload = result_to_json("toy", S, stuck, forward, greedy_result=greedy)

    assert forward.exists
    assert forward.seed == [0, 1, 2]
    assert payload["forward_ear_order"]["exists"] is True
    assert len(payload["fingerprint"]["cyclic_dihedral_sha256"]) == 64
    assert payload["key_peeling_status"] == "STUCK_SET_FOUND"
    assert payload["greedy_reverse_peeling"]["terminal_vertices"] == [2, 3, 4, 5]


def test_all_other_pentagon_has_complete_no_stuck_certificate() -> None:
    S = [[j for j in range(5) if j != i] for i in range(5)]

    result = find_minimal_stuck_sets(S)
    shifted = find_minimal_stuck_sets(S, min_size=5)
    radius = radius_propagation_obstruction(S)
    radius_payload = radius_result_to_json(radius)
    fragile = fragile_cover_snapshot(S)

    assert not result.found
    assert result.search_complete
    assert result.key_peeling_ok is True
    assert shifted.search_complete
    assert shifted.key_peeling_ok is None
    assert radius.obstructed is True
    assert radius_payload["type"] == "stuck_radius_propagation_short_chord_result"
    assert radius_payload["radius_propagation_status"] == "EXACT_RADIUS_PROPAGATION_OBSTRUCTION"
    assert radius_payload["edge_direction"] == "center -> smaller_center means r_smaller_center < r_center"
    assert fragile["cover_stats"]["cover_exists"] is True
    assert fragile["cover_stats"]["min_cover_size"] == 2


def test_c19_skew_snapshot_records_sparse_filter_wall() -> None:
    pattern = built_in_patterns()["C19_skew"]

    filters = pattern_filter_snapshot(pattern.S)
    stuck = find_minimal_stuck_sets(pattern.S, min_size=8, max_size=8, max_examples=1)
    greedy = greedy_peeling_run(pattern.S)

    assert filters["row_pair_cap_ok"] is True
    assert filters["column_pair_cap_ok"] is True
    assert filters["phi_edges"] == 0
    assert filters["odd_forced_perpendicular_cycle_length"] is None
    assert filters["minimum_radius_obstructed_in_order"] is False
    assert filters["minimum_radius_order_free_blocked_centers"] == []
    assert filters["minimum_radius_order_free_empty_gap_centers"] == list(range(19))
    assert filters["radius_propagation"]["status"] == "PASS_ACYCLIC_CHOICE"
    assert filters["fragile_cover"]["cover_stats"]["cover_exists"] is True
    assert stuck.minimal_size == 8
    assert stuck.examples[0].vertices == list(range(8))
    assert not greedy.success
    assert len(greedy.terminal_vertices) >= 4


def test_pattern_snapshot_records_phi4_rectangle_trap() -> None:
    filters = pattern_filter_snapshot(N9_RECTANGLE_TRAP_PATTERN)

    assert filters["rectangle_trap_4_cycles"] == 1
    assert filters["rectangle_trap_certificates"][0]["phi_cycle"] == [
        [0, 6],
        [2, 8],
        [1, 5],
        [4, 7],
    ]


def test_large_sidon_fragile_cover_window_is_truncated() -> None:
    pattern = built_in_patterns()["C25_sidon_2_5_9_14"]

    fragile = fragile_cover_snapshot(pattern.S, max_cover_size=7)
    stats = fragile["cover_stats"]

    assert stats["status"] == "SEARCHED"
    assert stats["cover_exists"] is False
    assert stats["search_complete"] is False
    assert stats["searched_up_to_size"] == 7


def test_radius_choice_optimization_certifies_c13_adversarial_minimum() -> None:
    pattern = built_in_patterns()["C13_sidon_1_2_4_10"]
    order = [0, 1, 3, 7, 4, 10, 6, 2, 12, 8, 5, 9, 11]

    result = optimize_radius_choice_edges(pattern.S, order=order)
    payload = radius_choice_optimization_to_json(result)

    assert result.status == "PASS_OPTIMAL_CHOICE"
    assert result.obstructed is False
    assert result.optimality_certified is True
    assert result.edge_count == 8
    assert result.edge_lower_bound == 8
    assert result.edge_upper_bound == 13
    assert payload["edge_count"] == 8
