from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_endpoint_control_survivor_spine_pocket_orders import (
    EXPECTED_CONSTRAINTS,
    EXPECTED_ORDERS,
    assert_expected,
    audit,
    crossing_constraints,
    enumerate_crossing_orders,
)


ROOT = Path(__file__).resolve().parents[1]


def test_endpoint_control_survivor_spine_pocket_constraints() -> None:
    assert crossing_constraints() == EXPECTED_CONSTRAINTS


def test_endpoint_control_survivor_spine_pocket_orders() -> None:
    orders, nodes_visited = enumerate_crossing_orders()

    assert orders == EXPECTED_ORDERS
    assert nodes_visited > 0


def test_endpoint_control_survivor_spine_pocket_audit() -> None:
    payload = audit()

    assert payload["constraint_count"] == 17
    assert payload["order_count"] == 5
    assert payload["nodes_visited"] == 38
    assert payload["expected_constraints_match"] is True
    assert payload["expected_orders_match"] is True
    assert_expected(payload)


def test_endpoint_control_survivor_spine_pocket_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_endpoint_control_survivor_spine_pocket_orders.py",
            "--assert-expected",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "crossing constraints: 17" in result.stdout
    assert "crossing-compatible orders: 5" in result.stdout
    assert "nodes visited: 38" in result.stdout
    assert "OK: expected spine-pocket frontier verified" in result.stdout
