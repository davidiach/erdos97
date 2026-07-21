#!/usr/bin/env python3
"""Replay Kalmanson certificates for the endpoint survivor spine-pocket orders."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erdos97.quotient_cone import check_quotient_cone_certificate  # noqa: E402
from scripts.check_endpoint_control_survivor_spine_pocket_orders import (  # noqa: E402
    EXPECTED_ORDERS,
    SURVIVOR_ROWS,
    assert_expected as assert_spine_pocket_expected,
    audit as spine_pocket_audit,
)


def row(kind: str, quad: list[int], weight: int) -> dict[str, object]:
    """Return one weighted Kalmanson strict-row item."""
    return {
        "source": "kalmanson",
        "kind": kind,
        "quad": quad,
        "weight": weight,
    }


K1 = "K1_diag_gt_sides"
K2 = "K2_diag_gt_other"

STRICT_ROWS_BY_ORDER: list[list[dict[str, object]]] = [
    [
        row(K2, [0, 1, 2, 4], 20),
        row(K2, [0, 1, 6, 8], 55),
        row(K2, [0, 2, 4, 9], 10),
        row(K1, [0, 2, 7, 9], 20),
        row(K2, [0, 2, 8, 10], 55),
        row(K1, [0, 3, 4, 10], 10),
        row(K2, [0, 3, 6, 10], 4),
        row(K2, [0, 4, 9, 10], 10),
        row(K2, [0, 5, 6, 7], 26),
        row(K1, [0, 5, 7, 10], 6),
        row(K2, [1, 2, 3, 5], 18),
        row(K2, [1, 2, 5, 6], 18),
        row(K1, [1, 3, 7, 9], 18),
        row(K2, [1, 4, 7, 8], 55),
        row(K2, [1, 5, 6, 9], 73),
        row(K1, [2, 6, 8, 9], 18),
        row(K2, [2, 7, 8, 9], 37),
        row(K1, [3, 4, 6, 9], 4),
        row(K2, [3, 5, 8, 9], 32),
        row(K2, [3, 6, 9, 10], 14),
        row(K2, [4, 5, 7, 8], 26),
        row(K1, [4, 7, 9, 10], 6),
        row(K2, [5, 6, 8, 10], 6),
    ],
    [
        row(K1, [0, 1, 3, 9], 11),
        row(K1, [0, 1, 9, 10], 2),
        row(K2, [0, 2, 6, 9], 2),
        row(K2, [1, 2, 3, 5], 5),
        row(K1, [1, 3, 4, 10], 5),
        row(K2, [1, 3, 5, 10], 5),
        row(K2, [2, 3, 6, 8], 2),
        row(K2, [2, 4, 8, 10], 2),
        row(K1, [3, 4, 9, 10], 3),
        row(K1, [3, 5, 6, 8], 2),
        row(K2, [3, 5, 8, 9], 2),
        row(K2, [3, 8, 9, 10], 10),
    ],
    [
        row(K1, [0, 1, 2, 5], 4),
        row(K1, [0, 2, 4, 7], 4),
        row(K2, [0, 2, 6, 8], 4),
        row(K1, [0, 3, 9, 10], 1),
        row(K1, [0, 4, 6, 9], 4),
        row(K2, [0, 4, 8, 9], 4),
        row(K2, [0, 6, 9, 10], 3),
        row(K2, [1, 2, 4, 6], 4),
        row(K1, [1, 2, 4, 10], 9),
        row(K1, [1, 5, 6, 9], 4),
        row(K2, [2, 4, 7, 8], 15),
        row(K2, [2, 4, 9, 10], 9),
        row(K2, [2, 6, 8, 9], 11),
        row(K2, [3, 4, 8, 9], 1),
        row(K2, [3, 7, 9, 10], 1),
        row(K2, [7, 6, 8, 10], 1),
    ],
    [
        row(K2, [0, 1, 2, 4], 3),
        row(K2, [0, 1, 4, 7], 2),
        row(K1, [0, 1, 8, 10], 6),
        row(K1, [0, 2, 5, 10], 3),
        row(K2, [0, 3, 5, 8], 6),
        row(K1, [0, 5, 4, 7], 1),
        row(K2, [0, 5, 7, 9], 1),
        row(K1, [0, 6, 7, 9], 1),
        row(K2, [0, 6, 9, 10], 1),
        row(K2, [1, 5, 9, 10], 3),
    ],
    [
        row(K2, [0, 1, 2, 4], 3),
        row(K1, [0, 1, 4, 9], 2),
        row(K1, [0, 1, 8, 10], 10),
        row(K1, [0, 2, 5, 10], 3),
        row(K2, [0, 2, 9, 10], 1),
        row(K2, [0, 3, 5, 8], 10),
        row(K2, [0, 3, 4, 9], 1),
        row(K2, [1, 5, 9, 10], 4),
        row(K2, [3, 4, 6, 9], 1),
        row(K1, [3, 6, 8, 9], 1),
        row(K2, [5, 4, 6, 10], 1),
        row(K2, [4, 6, 9, 10], 1),
    ],
]

EXPECTED_STRICT_ROWS = [23, 12, 16, 10, 12]
EXPECTED_WEIGHT_SUMS = [541, 51, 79, 27, 38]
EXPECTED_MAX_WEIGHTS = [73, 11, 15, 6, 10]


def certificate_for_order(index: int) -> dict[str, object]:
    """Return the stored certificate for one crossing-compatible order."""
    strict_rows = STRICT_ROWS_BY_ORDER[index]
    return {
        "type": "endpoint_control_survivor_spine_pocket_kalmanson_certificate",
        "schema": "erdos97.endpoint_control_survivor_spine_pocket_kalmanson.v1",
        "status": "EXACT_OBSTRUCTION_FOR_FIXED_SURVIVOR_AND_CYCLIC_ORDER",
        "claim_strength": (
            "Exact Kalmanson obstruction for the fixed Cycle 674 "
            "endpoint-control survivor and this fixed cyclic order only."
        ),
        "pattern": {
            "name": "endpoint_control_survivor_cycle_674",
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
    frontier = spine_pocket_audit()
    assert_spine_pocket_expected(frontier)
    certificates = [
        certificate_for_order(index) for index in range(len(EXPECTED_ORDERS))
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
        "type": "endpoint_control_survivor_spine_pocket_kalmanson_audit",
        "schema": "erdos97.endpoint_control_survivor_spine_pocket_kalmanson.v1",
        "status": "EXACT_OBSTRUCTION_FOR_FIXED_SURVIVOR_AND_CROSSING_ORDERS",
        "claim_strength": (
            "Exact obstruction for the fixed Cycle 674 endpoint-control survivor "
            "across the five crossing-compatible cyclic orders. This is not an "
            "all-extension endpoint-control proof and not an Erdos97 proof."
        ),
        "pattern": {
            "name": "endpoint_control_survivor_cycle_674",
            "n": len(SURVIVOR_ROWS),
            "selected_rows": SURVIVOR_ROWS,
        },
        "crossing_frontier": {
            "constraint_count": frontier["constraint_count"],
            "order_count": frontier["order_count"],
            "nodes_visited": frontier["nodes_visited"],
            "orders": frontier["orders"],
        },
        "order_summaries": order_summaries,
        "obstructed_order_count": sum(
            1 for summary in order_summaries if summary["zero_sum_verified"]
        ),
        "certificates": certificates,
        "interpretation": (
            "The crossing-only frontier has five cyclic orders, and each order "
            "has an exact positive integer Kalmanson quotient-cone certificate. "
            "Therefore this fixed full selected-row extension is obstructed in "
            "every cyclic order satisfying the necessary two-overlap crossing "
            "constraints."
        ),
    }


def assert_expected(payload: dict[str, object]) -> None:
    if payload["crossing_frontier"]["order_count"] != 5:  # type: ignore[index]
        raise AssertionError("unexpected crossing-order count")
    if payload["obstructed_order_count"] != 5:
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
        print("endpoint-control survivor spine-pocket Kalmanson audit")
        print(
            f"crossing-compatible orders: {payload['crossing_frontier']['order_count']}"
        )
        print(f"obstructed orders: {payload['obstructed_order_count']}")
        for summary in payload["order_summaries"]:  # type: ignore[assignment]
            print(
                f"order {summary['order_index']}: "
                f"rows={summary['strict_rows']} "
                f"weight_sum={summary['weight_sum']} "
                f"zero_sum={summary['zero_sum_verified']}"
            )
        if args.assert_expected:
            print("OK: expected spine-pocket Kalmanson certificates verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
