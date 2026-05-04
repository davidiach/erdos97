from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "c13_sidon_all_orders_kalmanson_two_search.json"


def test_c13_all_orders_kalmanson_two_search_artifact() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["type"] == "kalmanson_two_inverse_pair_order_search_v1"
    assert payload["trust"] == "EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN"
    assert payload["status"] == "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION"
    assert payload["pattern"] == {
        "circulant_offsets": [1, 2, 4, 10],
        "n": 13,
        "name": "C13_sidon_1_2_4_10",
    }
    assert payload["nodes_visited"] == 1496677
    assert payload["branches_pruned_by_completed_two_certificate"] == 6192576
    assert payload["max_surviving_prefix_depth"] == 11
    assert payload["survivor_order"] is None
    assert "elapsed_seconds" not in payload
    assert "does not prove Erdos Problem #97" in payload["semantics"]


def test_kalmanson_two_order_search_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_kalmanson_two_order_search.py", "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Search cyclic orders" in result.stdout


def test_kalmanson_two_order_search_json_is_deterministic_shape() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_kalmanson_two_order_search.py",
            "--name",
            "toy",
            "--n",
            "5",
            "--offsets",
            "1,2,3,4",
            "--node-limit",
            "1",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert "elapsed_seconds" not in payload
    assert payload["status"] == "UNKNOWN_NODE_LIMIT_REACHED"


@pytest.mark.slow
@pytest.mark.exhaustive
def test_c13_all_orders_kalmanson_two_search_replay() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_kalmanson_two_order_search.py",
            "--name",
            "C13_sidon_1_2_4_10",
            "--n",
            "13",
            "--offsets",
            "1,2,4,10",
            "--assert-obstructed",
            "--assert-c13-expected",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION" in result.stdout
