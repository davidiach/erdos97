from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from erdos97.quotient_cone import check_quotient_cone_certificate
from scripts.check_block6_survivor_crossing_kalmanson import (
    EXPECTED_CONSTRAINTS,
    EXPECTED_MAX_WEIGHTS,
    EXPECTED_ORDERS,
    EXPECTED_STRICT_ROWS,
    EXPECTED_WEIGHT_SUMS,
    assert_expected,
    audit,
    certificate_for_order,
    crossing_constraints,
    enumerate_crossing_orders,
)


ROOT = Path(__file__).resolve().parents[1]


def test_block6_survivor_crossing_constraints() -> None:
    assert crossing_constraints() == EXPECTED_CONSTRAINTS


def test_block6_survivor_crossing_orders() -> None:
    orders, nodes_visited = enumerate_crossing_orders()

    assert orders == EXPECTED_ORDERS
    assert nodes_visited == 146


def test_block6_survivor_crossing_kalmanson_each_certificate_replays() -> None:
    for index in range(4):
        result = check_quotient_cone_certificate(certificate_for_order(index))

        assert result.strict_rows == EXPECTED_STRICT_ROWS[index]
        assert result.weight_sum == EXPECTED_WEIGHT_SUMS[index]
        assert result.max_weight == EXPECTED_MAX_WEIGHTS[index]
        assert result.distance_classes == 33
        assert result.zero_sum_verified is True
        assert result.combined_nonzero_coefficient_count == 0


def test_block6_survivor_crossing_kalmanson_audit() -> None:
    payload = audit()

    assert payload["crossing_order_count"] == 4
    assert payload["obstructed_order_count"] == 4
    assert [
        summary["strict_rows"] for summary in payload["order_summaries"]
    ] == EXPECTED_STRICT_ROWS
    assert [
        summary["weight_sum"] for summary in payload["order_summaries"]
    ] == EXPECTED_WEIGHT_SUMS
    assert_expected(payload)


def test_block6_survivor_crossing_kalmanson_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_survivor_crossing_kalmanson.py",
            "--assert-expected",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "crossing-compatible orders: 4" in result.stdout
    assert "obstructed orders: 4" in result.stdout
    assert "order 0: rows=9 weight_sum=13 zero_sum=True" in result.stdout
    assert (
        "OK: expected block6 crossing-order Kalmanson certificates verified"
        in result.stdout
    )
