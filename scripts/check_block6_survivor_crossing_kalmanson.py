#!/usr/bin/env python3
"""Replay crossing-order Kalmanson certificates for the block-6 survivor."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from erdos97.fragile_benchmarks import (
    block6_two_block_survivor_extension_3_rows,
)
from erdos97.incidence_filters import Chord, chords_cross_in_order, phi_map
from erdos97.quotient_cone import check_quotient_cone_certificate
from erdos97.sparse_frontier import normalize_cyclic_order

Constraint = tuple[Chord, Chord]

PATTERN_NAME = "block6_two_block_survivor_extension_3"
SURVIVOR_ROWS: list[list[int]] = block6_two_block_survivor_extension_3_rows()

EXPECTED_CONSTRAINTS: list[Constraint] = [
    ((0, 2), (1, 3)),
    ((0, 3), (2, 4)),
    ((1, 4), (3, 11)),
    ((1, 9), (6, 11)),
    ((1, 10), (9, 11)),
    ((2, 7), (1, 5)),
    ((3, 8), (0, 5)),
    ((3, 10), (2, 5)),
    ((3, 11), (0, 4)),
    ((4, 9), (8, 11)),
    ((5, 7), (1, 6)),
    ((5, 8), (0, 7)),
    ((5, 11), (0, 6)),
    ((6, 8), (7, 9)),
    ((6, 9), (8, 10)),
    ((7, 9), (6, 8)),
    ((8, 10), (5, 9)),
    ((9, 11), (6, 10)),
]

EXPECTED_ORDERS: list[list[int]] = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    [0, 1, 2, 3, 5, 4, 6, 7, 8, 9, 10, 11],
    [0, 1, 2, 3, 5, 6, 4, 7, 8, 9, 10, 11],
    [0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11],
]

K1 = "K1_diag_gt_sides"
K2 = "K2_diag_gt_other"


def row(kind: str, quad: list[int], weight: int) -> dict[str, object]:
    """Return one weighted Kalmanson strict-row item."""
    return {
        "source": "kalmanson",
        "kind": kind,
        "quad": quad,
        "weight": weight,
    }


STRICT_ROWS_BY_ORDER: list[list[dict[str, object]]] = [
    [
        row(K1, [0, 1, 3, 8], 2),
        row(K1, [0, 2, 3, 10], 1),
        row(K1, [0, 2, 8, 10], 2),
        row(K1, [0, 3, 4, 8], 2),
        row(K1, [1, 3, 5, 9], 1),
        row(K2, [1, 3, 7, 11], 1),
        row(K1, [1, 8, 9, 10], 2),
        row(K2, [3, 5, 7, 9], 1),
        row(K2, [3, 6, 10, 11], 1),
    ],
    [
        row(K2, [0, 1, 3, 9], 60),
        row(K2, [0, 1, 6, 7], 30),
        row(K1, [0, 1, 6, 9], 30),
        row(K1, [0, 2, 3, 6], 7),
        row(K2, [0, 2, 7, 11], 21),
        row(K2, [0, 2, 9, 10], 27),
        row(K2, [0, 5, 9, 10], 33),
        row(K1, [0, 4, 7, 11], 22),
        row(K1, [0, 4, 8, 10], 13),
        row(K1, [0, 6, 10, 11], 60),
        row(K1, [0, 7, 8, 9], 13),
        row(K1, [1, 2, 4, 10], 13),
        row(K1, [1, 4, 7, 9], 13),
        row(K2, [2, 3, 4, 8], 7),
        row(K2, [2, 3, 7, 11], 7),
        row(K1, [2, 5, 8, 11], 34),
        row(K1, [2, 4, 6, 9], 7),
        row(K1, [2, 6, 7, 8], 14),
        row(K2, [2, 7, 10, 11], 14),
        row(K1, [2, 8, 9, 10], 27),
        row(K2, [3, 5, 6, 11], 7),
        row(K2, [3, 4, 7, 8], 7),
        row(K2, [5, 4, 9, 11], 33),
        row(K2, [5, 7, 8, 11], 8),
        row(K2, [4, 6, 7, 9], 21),
        row(K1, [4, 7, 8, 10], 14),
        row(K1, [4, 8, 9, 11], 34),
    ],
    [
        row(K1, [0, 1, 3, 7], 85),
        row(K1, [0, 1, 5, 11], 49),
        row(K2, [0, 1, 6, 7], 30),
        row(K2, [0, 2, 3, 6], 8),
        row(K2, [0, 2, 4, 9], 13),
        row(K2, [0, 2, 7, 8], 30),
        row(K2, [0, 3, 9, 11], 13),
        row(K1, [0, 6, 4, 10], 22),
        row(K2, [1, 2, 5, 4], 56),
        row(K2, [1, 2, 7, 11], 12),
        row(K2, [1, 2, 8, 10], 52),
        row(K1, [1, 3, 5, 9], 25),
        row(K2, [1, 3, 4, 8], 56),
        row(K1, [1, 3, 8, 11], 4),
        row(K1, [1, 5, 10, 11], 74),
        row(K2, [1, 8, 9, 10], 22),
        row(K2, [2, 3, 10, 11], 12),
        row(K2, [2, 5, 6, 4], 21),
        row(K2, [2, 6, 7, 9], 13),
        row(K1, [2, 6, 7, 11], 29),
        row(K1, [2, 4, 8, 10], 22),
        row(K2, [3, 5, 7, 8], 85),
        row(K2, [3, 7, 8, 11], 29),
        row(K1, [3, 9, 10, 11], 12),
        row(K1, [5, 4, 8, 11], 21),
        row(K2, [5, 8, 9, 11], 25),
    ],
    [
        row(K1, [0, 1, 2, 7], 12),
        row(K1, [0, 1, 3, 8], 2),
        row(K1, [0, 1, 7, 9], 6),
        row(K2, [0, 2, 3, 7], 6),
        row(K2, [1, 2, 5, 8], 6),
        row(K1, [1, 3, 5, 9], 1),
        row(K1, [1, 3, 7, 11], 1),
        row(K2, [1, 5, 4, 9], 1),
        row(K2, [1, 5, 8, 10], 3),
        row(K1, [1, 4, 8, 10], 1),
        row(K2, [1, 4, 10, 11], 3),
        row(K2, [2, 5, 4, 8], 6),
        row(K2, [2, 6, 7, 4], 6),
        row(K2, [3, 4, 8, 10], 2),
        row(K2, [3, 4, 9, 11], 1),
        row(K1, [3, 9, 10, 11], 2),
        row(K1, [5, 7, 4, 11], 7),
        row(K1, [6, 4, 8, 11], 6),
        row(K2, [7, 8, 9, 10], 6),
        row(K2, [7, 8, 10, 11], 6),
        row(K1, [4, 8, 9, 10], 1),
    ],
]

EXPECTED_STRICT_ROWS = [9, 27, 26, 21]
EXPECTED_WEIGHT_SUMS = [13, 576, 820, 85]
EXPECTED_MAX_WEIGHTS = [2, 60, 85, 12]


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

    search([0], {0})

    return [list(order) for order in sorted(orders)], nodes_visited


def certificate_for_order(index: int) -> dict[str, object]:
    """Return the stored Kalmanson certificate for one crossing-compatible order."""
    strict_rows = STRICT_ROWS_BY_ORDER[index]
    return {
        "type": "block6_survivor_crossing_kalmanson_certificate",
        "schema": "erdos97.block6_survivor_crossing_kalmanson.v1",
        "status": "EXACT_OBSTRUCTION_FOR_FIXED_SURVIVOR_AND_CYCLIC_ORDER",
        "claim_strength": (
            "Exact Kalmanson obstruction for the fixed two-block block-6 "
            "survivor extension and this fixed cyclic order only."
        ),
        "pattern": {
            "name": PATTERN_NAME,
            "n": len(SURVIVOR_ROWS),
            "selected_rows": SURVIVOR_ROWS,
        },
        "cyclic_order": EXPECTED_ORDERS[index],
        "order_index": index,
        "strict_rows": strict_rows,
        "num_inequalities": len(strict_rows),
        "weight_sum": sum(int(item["weight"]) for item in strict_rows),
    }


def audit() -> dict[str, object]:
    """Replay the crossing frontier and every stored Kalmanson certificate."""
    constraints = crossing_constraints()
    orders, nodes_visited = enumerate_crossing_orders()
    expected_order_index = {
        tuple(order): index for index, order in enumerate(EXPECTED_ORDERS)
    }
    missing_certificate_orders = [
        order for order in orders if tuple(order) not in expected_order_index
    ]
    if missing_certificate_orders:
        raise AssertionError(
            "enumerated crossing order has no stored Kalmanson certificate: "
            f"{missing_certificate_orders[0]}"
        )
    certificates = [
        certificate_for_order(expected_order_index[tuple(order)]) for order in orders
    ]
    checks = [check_quotient_cone_certificate(cert) for cert in certificates]
    order_summaries = []
    for index, (cert, check) in enumerate(zip(certificates, checks, strict=True)):
        order_summaries.append(
            {
                "order_index": index,
                "cyclic_order": cert["cyclic_order"],
                "strict_rows": check.strict_rows,
                "distance_classes": check.distance_classes,
                "weight_sum": check.weight_sum,
                "max_weight": check.max_weight,
                "zero_sum_verified": check.zero_sum_verified,
                "nonpositive_sum_verified": check.nonpositive_sum_verified,
                "combined_nonzero_coefficient_count": (
                    check.combined_nonzero_coefficient_count
                ),
            }
        )
    return {
        "type": "block6_survivor_crossing_kalmanson_audit",
        "schema": "erdos97.block6_survivor_crossing_kalmanson.v1",
        "status": "EXACT_OBSTRUCTION_FOR_FIXED_SURVIVOR_AND_CROSSING_ORDERS",
        "claim_strength": (
            "Exact obstruction for the fixed two-block block-6 survivor "
            "extension across its crossing-compatible cyclic orders. This is "
            "not an all-extension block-6 fragile-cover proof and not an "
            "Erdos97 proof."
        ),
        "pattern": {
            "name": PATTERN_NAME,
            "n": len(SURVIVOR_ROWS),
            "selected_rows": SURVIVOR_ROWS,
        },
        "constraints": [_json_constraint(constraint) for constraint in constraints],
        "constraint_count": len(constraints),
        "crossing_orders": orders,
        "crossing_order_count": len(orders),
        "nodes_visited": nodes_visited,
        "expected_constraints_match": constraints == EXPECTED_CONSTRAINTS,
        "expected_orders_match": orders == EXPECTED_ORDERS,
        "order_summaries": order_summaries,
        "obstructed_order_count": sum(
            1 for summary in order_summaries if summary["zero_sum_verified"]
        ),
        "certificates": certificates,
        "interpretation": (
            "The crossing-only frontier has four cyclic orders, and each order "
            "has an exact positive integer Kalmanson quotient-cone certificate. "
            "Therefore this fixed full selected-row extension is obstructed in "
            "every cyclic order satisfying its necessary two-overlap crossing "
            "constraints."
        ),
    }


def assert_expected(payload: dict[str, object]) -> None:
    if payload["constraint_count"] != 18:
        raise AssertionError("unexpected crossing-constraint count")
    if payload["crossing_order_count"] != 4:
        raise AssertionError("unexpected crossing-compatible order count")
    if payload["nodes_visited"] != 146:
        raise AssertionError("unexpected search-node count")
    if payload["expected_constraints_match"] is not True:
        raise AssertionError("unexpected crossing constraints")
    if payload["expected_orders_match"] is not True:
        raise AssertionError("unexpected crossing-compatible orders")
    if payload["obstructed_order_count"] != 4:
        raise AssertionError("not all crossing-compatible orders are obstructed")
    summaries = payload["order_summaries"]
    if not isinstance(summaries, list):
        raise AssertionError("order summaries must be a list")
    strict_rows = [summary["strict_rows"] for summary in summaries]
    weight_sums = [summary["weight_sum"] for summary in summaries]
    max_weights = [summary["max_weight"] for summary in summaries]
    if strict_rows != EXPECTED_STRICT_ROWS:
        raise AssertionError("unexpected strict-row counts")
    if weight_sums != EXPECTED_WEIGHT_SUMS:
        raise AssertionError("unexpected weight sums")
    if max_weights != EXPECTED_MAX_WEIGHTS:
        raise AssertionError("unexpected max weights")
    if not all(summary["zero_sum_verified"] for summary in summaries):
        raise AssertionError("expected every certificate to be zero-sum")
    if not all(
        summary["combined_nonzero_coefficient_count"] == 0 for summary in summaries
    ):
        raise AssertionError("expected every combined coefficient vector to vanish")


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
        print("block6 survivor crossing-order Kalmanson audit")
        print(f"crossing constraints: {payload['constraint_count']}")
        print(f"crossing-compatible orders: {payload['crossing_order_count']}")
        print(f"obstructed orders: {payload['obstructed_order_count']}")
        print(f"nodes visited: {payload['nodes_visited']}")
        for summary in payload["order_summaries"]:  # type: ignore[assignment]
            print(
                f"order {summary['order_index']}: "
                f"rows={summary['strict_rows']} "
                f"weight_sum={summary['weight_sum']} "
                f"zero_sum={summary['zero_sum_verified']}"
            )
        if args.assert_expected:
            print("OK: expected block6 crossing-order Kalmanson certificates verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
