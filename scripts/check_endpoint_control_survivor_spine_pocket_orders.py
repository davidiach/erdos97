#!/usr/bin/env python3
"""Replay the crossing-only spine-pocket orders for the endpoint survivor."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from erdos97.incidence_filters import Chord, chords_cross_in_order, phi_map
from erdos97.sparse_frontier import normalize_cyclic_order

Constraint = tuple[Chord, Chord]

SURVIVOR_ROWS: list[list[int]] = [
    [1, 3, 5, 6],
    [0, 2, 7, 9],
    [1, 3, 4, 10],
    [2, 4, 5, 7],
    [1, 6, 7, 8],
    [0, 2, 3, 6],
    [0, 4, 8, 10],
    [1, 2, 4, 9],
    [3, 7, 9, 10],
    [2, 5, 8, 10],
    [0, 1, 8, 9],
]

EXPECTED_CONSTRAINTS: list[Constraint] = [
    ((0, 2), (1, 3)),
    ((0, 4), (1, 6)),
    ((0, 5), (3, 6)),
    ((1, 3), (2, 7)),
    ((1, 5), (0, 2)),
    ((1, 7), (2, 9)),
    ((1, 8), (7, 9)),
    ((1, 10), (0, 9)),
    ((2, 6), (4, 10)),
    ((2, 7), (1, 4)),
    ((2, 8), (3, 10)),
    ((3, 7), (2, 4)),
    ((3, 9), (2, 5)),
    ((4, 10), (1, 8)),
    ((6, 9), (8, 10)),
    ((6, 10), (0, 8)),
    ((7, 10), (1, 9)),
]

EXPECTED_ORDERS: list[list[int]] = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    [0, 1, 2, 3, 4, 5, 7, 6, 8, 9, 10],
    [0, 1, 2, 3, 4, 7, 5, 6, 8, 9, 10],
    [0, 1, 2, 3, 5, 4, 6, 7, 8, 9, 10],
    [0, 1, 2, 3, 5, 4, 7, 6, 8, 9, 10],
]


def _json_chord(chord: Chord) -> list[int]:
    return [int(chord[0]), int(chord[1])]


def _json_constraint(constraint: Constraint) -> dict[str, list[int]]:
    return {
        "source": _json_chord(constraint[0]),
        "target": _json_chord(constraint[1]),
    }


def crossing_constraints() -> list[Constraint]:
    """Return the fixed survivor's two-overlap crossing constraints."""
    return sorted(phi_map(SURVIVOR_ROWS).items())


def enumerate_crossing_orders() -> tuple[list[list[int]], int]:
    """Return all normalized crossing-compatible orders and search-node count."""
    constraints = crossing_constraints()
    n = len(SURVIVOR_ROWS)
    labels = set(range(n))
    constraint_label_sets = [
        set(source) | set(target) for source, target in constraints
    ]
    label_to_constraints: dict[int, list[int]] = {label: [] for label in labels}
    for idx, constraint_labels in enumerate(constraint_label_sets):
        for label in constraint_labels:
            label_to_constraints[label].append(idx)

    nodes_visited = 0
    orders: set[tuple[int, ...]] = set()

    def completed_failure(
        order: Sequence[int],
        placed: set[int],
        affected_labels: set[int] | None = None,
    ) -> bool:
        if affected_labels is None:
            candidate_idxs = range(len(constraints))
        else:
            idxs: set[int] = set()
            for label in affected_labels:
                idxs.update(label_to_constraints[label])
            candidate_idxs = sorted(idxs)
        for idx in candidate_idxs:
            if constraint_label_sets[idx] <= placed:
                source, target = constraints[idx]
                if not chords_cross_in_order(source, target, order):
                    return True
        return False

    def choose_label(placed: set[int]) -> int:
        def score(label: int) -> tuple[int, int, int, int, int]:
            touches = [
                len(constraint_label_sets[idx] & placed)
                for idx in label_to_constraints[label]
            ]
            return (
                sum(count == 3 for count in touches),
                sum(count == 2 for count in touches),
                sum(count == 1 for count in touches),
                len(label_to_constraints[label]),
                -label,
            )

        return max(labels - placed, key=score)

    def search(order: list[int], placed: set[int]) -> None:
        nonlocal nodes_visited
        nodes_visited += 1
        if len(placed) == n:
            if not completed_failure(order, placed):
                orders.add(tuple(normalize_cyclic_order(order)))
            return

        label = choose_label(placed)
        for position in range(1, len(order) + 1):
            candidate_order = order[:position] + [label] + order[position:]
            candidate_placed = placed | {label}
            if not completed_failure(candidate_order, candidate_placed, {label}):
                search(candidate_order, candidate_placed)

    for initial_order in ([0, 1, 2, 3], [0, 3, 2, 1]):
        search(list(initial_order), set(initial_order))

    return [list(order) for order in sorted(orders)], nodes_visited


def audit() -> dict[str, object]:
    constraints = crossing_constraints()
    orders, nodes_visited = enumerate_crossing_orders()
    return {
        "type": "endpoint_control_survivor_spine_pocket_order_audit",
        "schema": "erdos97.endpoint_control_survivor_spine_pocket_order_audit.v1",
        "status": "EXACT_CROSSING_ONLY_FRONTIER_FOR_FIXED_SURVIVOR",
        "claim_strength": (
            "Exact crossing-only cyclic-order frontier for the fixed Cycle 674 "
            "endpoint-control survivor; not an obstruction, endpoint-control "
            "proof, or Erdos97 proof."
        ),
        "pattern": {
            "name": "endpoint_control_survivor_cycle_674",
            "n": len(SURVIVOR_ROWS),
            "selected_rows": SURVIVOR_ROWS,
        },
        "constraints": [_json_constraint(constraint) for constraint in constraints],
        "constraint_count": len(constraints),
        "orders": orders,
        "order_count": len(orders),
        "nodes_visited": nodes_visited,
        "expected_constraints_match": constraints == EXPECTED_CONSTRAINTS,
        "expected_orders_match": orders == EXPECTED_ORDERS,
        "spine_pocket_summary": {
            "left_spine": [0, 1, 2, 3],
            "pocket": [4, 5, 6, 7],
            "right_spine": [8, 9, 10],
            "forced_pocket_relations": [[4, 6], [4, 7], [5, 6]],
        },
        "next_metric_gate": (
            "Replay a Kalmanson quotient-cone certificate for each of the five "
            "crossing-compatible orders."
        ),
    }


def assert_expected(payload: dict[str, object]) -> None:
    if payload["constraint_count"] != 17:
        raise AssertionError("unexpected crossing-constraint count")
    if payload["order_count"] != 5:
        raise AssertionError("unexpected crossing-compatible order count")
    if payload["nodes_visited"] != 38:
        raise AssertionError("unexpected search-node count")
    if payload["expected_constraints_match"] is not True:
        raise AssertionError("unexpected crossing constraints")
    if payload["expected_orders_match"] is not True:
        raise AssertionError("unexpected crossing-compatible orders")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    payload = audit()
    if args.assert_expected:
        assert_expected(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("endpoint-control survivor spine-pocket crossing-order audit")
        print(f"crossing constraints: {payload['constraint_count']}")
        print(f"crossing-compatible orders: {payload['order_count']}")
        print(f"nodes visited: {payload['nodes_visited']}")
        print(f"expected constraints match: {payload['expected_constraints_match']}")
        print(f"expected orders match: {payload['expected_orders_match']}")
        if args.assert_expected:
            print("OK: expected spine-pocket frontier verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
