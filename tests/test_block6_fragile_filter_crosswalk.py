from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_block6_fragile_filter_crosswalk import (
    assert_expected,
    audit,
)

ROOT = Path(__file__).resolve().parents[1]


def test_block6_filter_crosswalk_matches_expected() -> None:
    payload = audit()

    assert_expected(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert "not a proof" in payload["claim_scope"]

    layers = payload["fixed_survivor_layers"]
    assert layers["quotient_ptolemy"]["positive_assignment"] is True
    assert layers["radius_propagation"]["acyclic_choice_found"] is True
    assert layers["natural_order_vertex_circle"]["status"] == "self_edge"
    assert layers["crossing_kalmanson"]["obstructed_order_count"] == 4


def test_block6_filter_crosswalk_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_fragile_filter_crosswalk.py",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
