from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_block6_shuffle_order_vertex_circle_sweep import (
    OUT,
    assert_expected,
    payload,
    shuffle_orders,
)

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.slow


def test_block6_shuffle_orders_are_the_expected_family() -> None:
    orders = shuffle_orders()

    assert len(orders) == 462
    assert orders[0]["order"] == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    assert orders[461]["order"] == [0, 6, 7, 8, 9, 10, 11, 1, 2, 3, 4, 5]


def test_block6_shuffle_order_partial_payload() -> None:
    data = payload(indices=[0, 1])

    assert data["summary"]["shuffle_order_count"] == 2
    assert data["summary"]["closed_order_count"] == 2
    assert data["summary"]["orders_with_terminal_extension"] == 2
    assert data["summary"]["orders_with_clean_pruned_solution"] == 0
    assert data["summary"]["vc_prunes"] == {
        "self_edge": 1101,
        "strict_cycle": 1412,
    }


def test_block6_shuffle_order_artifact() -> None:
    data = json.loads(OUT.read_text(encoding="utf-8"))

    assert_expected(data)
    assert data["summary"]["shuffle_order_count"] == 462
    assert data["summary"]["closed_order_count"] == 462
    assert data["summary"]["orders_without_terminal_extension"] == 4


def test_block6_shuffle_order_cli_partial() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_shuffle_order_vertex_circle_sweep.py",
            "--indices",
            "0,1",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
