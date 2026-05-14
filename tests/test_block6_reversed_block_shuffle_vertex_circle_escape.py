from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_block6_reversed_block_shuffle_vertex_circle_escape import (
    EXPECTED_CLEAN_INDICES,
    OUT,
    assert_expected,
    payload,
    reversed_second_block_shuffle_orders,
)

ROOT = Path(__file__).resolve().parents[1]


def test_reversed_second_block_shuffle_orders_are_expected_family() -> None:
    orders = reversed_second_block_shuffle_orders()

    assert len(orders) == 462
    assert orders[0]["order"] == [0, 1, 2, 3, 4, 5, 11, 10, 9, 8, 7, 6]
    assert orders[461]["order"] == [0, 11, 10, 9, 8, 7, 6, 1, 2, 3, 4, 5]


def test_reversed_block_shuffle_partial_escape_payload() -> None:
    data = payload(indices=[0, 13])

    assert data["summary"]["shuffle_order_count"] == 2
    assert data["summary"]["closed_order_count"] == 1
    assert data["summary"]["orders_with_clean_pruned_solution"] == 1
    assert [record["index"] for record in data["clean_order_records"]] == [13]


def test_reversed_block_shuffle_escape_artifact() -> None:
    data = json.loads(OUT.read_text(encoding="utf-8"))

    assert_expected(data)
    assert data["summary"]["orders_with_clean_pruned_solution"] == 16
    assert [record["index"] for record in data["clean_order_records"]] == (
        EXPECTED_CLEAN_INDICES
    )
    assert "not a counterexample" in data["claim_scope"]


def test_reversed_block_shuffle_escape_cli_partial() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_reversed_block_shuffle_vertex_circle_escape.py",
            "--indices",
            "0,13",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
