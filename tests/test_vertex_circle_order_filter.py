from __future__ import annotations

import json
from pathlib import Path

from erdos97.search import built_in_patterns
from erdos97.vertex_circle_order_filter import (
    find_cyclic_order_with_vertex_circle_filter,
    pair,
    search_result_to_json,
    vertex_circle_order_obstruction,
    vertex_circle_strict_inequalities,
)


ROOT = Path(__file__).resolve().parents[1]
P18_CERTIFICATE = ROOT / "data" / "certificates" / "p18_vertex_circle_order_unsat.json"

P18_CROSSING_COMPATIBLE_ORDER = [
    0,
    8,
    4,
    15,
    1,
    5,
    11,
    9,
    3,
    7,
    17,
    13,
    2,
    6,
    14,
    10,
    16,
    12,
]

C19_VERTEX_CIRCLE_ACYCLIC_ORDER = [
    18,
    10,
    7,
    17,
    6,
    3,
    5,
    9,
    14,
    11,
    2,
    13,
    4,
    16,
    12,
    15,
    0,
    8,
    1,
]


def test_p18_known_order_has_human_readable_vertex_circle_cycle() -> None:
    pattern = built_in_patterns()["P18_parity_balanced"]
    result = vertex_circle_order_obstruction(
        pattern.S,
        P18_CROSSING_COMPATIBLE_ORDER,
        pattern.name,
    )

    assert result.obstructed
    assert not result.self_edge_conflicts
    assert result.cycle_edges
    assert result.row_count_completed == 18
    assert result.strict_edge_count == 162

    inequalities, _ = vertex_circle_strict_inequalities(
        pattern.S,
        P18_CROSSING_COMPATIBLE_ORDER,
    )
    row3 = next(
        edge
        for edge in inequalities
        if edge.row == 3
        and edge.outer_pair == pair(5, 13)
        and edge.inner_pair == pair(5, 10)
    )
    row12 = next(
        edge
        for edge in inequalities
        if edge.row == 12
        and edge.outer_pair == pair(5, 10)
        and edge.inner_pair == pair(2, 10)
    )

    assert row3.witness_order == [17, 13, 10, 5]
    assert row12.witness_order == [5, 2, 10, 16]
    assert row3.outer_class == row12.inner_class
    assert row3.inner_class == row12.outer_class


def test_p18_crossing_plus_vertex_circle_search_unsat() -> None:
    pattern = built_in_patterns()["P18_parity_balanced"]
    result = find_cyclic_order_with_vertex_circle_filter(pattern.S, pattern.name)

    assert not result.sat
    assert result.order is None
    assert result.nodes_visited > 0
    assert result.crossing_prunes > 0
    assert result.vertex_circle_prunes > 0


def test_p18_certificate_matches_generator_with_documented_conflict_cap() -> None:
    pattern = built_in_patterns()["P18_parity_balanced"]
    result = find_cyclic_order_with_vertex_circle_filter(
        pattern.S,
        pattern.name,
        max_terminal_conflicts=16,
    )

    checked_in = json.loads(P18_CERTIFICATE.read_text(encoding="utf-8"))
    assert search_result_to_json(result) == checked_in


def test_c19_supplied_order_passes_vertex_circle_filter() -> None:
    pattern = built_in_patterns()["C19_skew"]
    result = vertex_circle_order_obstruction(
        pattern.S,
        C19_VERTEX_CIRCLE_ACYCLIC_ORDER,
        pattern.name,
    )

    assert not result.obstructed
    assert not result.self_edge_conflicts
    assert not result.cycle_edges
    assert result.row_count_completed == 19
    assert result.strict_edge_count == 171
