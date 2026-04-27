from __future__ import annotations

from erdos97.cyclic_crossing_csp import (
    all_constraints_cross,
    crossing_constraints,
    find_cyclic_crossing_order,
)
from erdos97.search import built_in_patterns


def test_p18_known_order_satisfies_crossing_csp() -> None:
    pattern = built_in_patterns()["P18_parity_balanced"]
    order = [0, 8, 4, 15, 1, 5, 11, 9, 3, 7, 17, 13, 2, 6, 14, 10, 16, 12]

    assert len(crossing_constraints(pattern.S)) == 27
    assert all_constraints_cross(order, crossing_constraints(pattern.S))


def test_p18_crossing_csp_sat() -> None:
    pattern = built_in_patterns()["P18_parity_balanced"]
    result = find_cyclic_crossing_order(pattern.S, pattern.name)

    assert result.sat
    assert result.order is not None
    assert all_constraints_cross(result.order, result.constraints)


def test_p24_crossing_csp_unsat() -> None:
    pattern = built_in_patterns()["P24_parity_balanced"]
    result = find_cyclic_crossing_order(pattern.S, pattern.name)

    assert len(result.constraints) == 36
    assert not result.sat
    assert result.order is None
    assert result.nodes_visited > 0
    assert result.terminal_conflicts
