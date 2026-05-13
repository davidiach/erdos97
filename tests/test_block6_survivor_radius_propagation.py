from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_block6_survivor_radius_propagation import audit


ROOT = Path(__file__).resolve().parents[1]


def test_block6_survivor_passes_radius_propagation() -> None:
    payload = audit()

    assert payload["status"] == "PASS_RADIUS_PROPAGATION"
    assert payload["obstructed"] is False
    assert payload["acyclic_choice_found"] is True

    radius = payload["radius_propagation"]
    assert radius["n"] == 12
    assert radius["nodes_visited"] == 13
    assert radius["short_gap_choice_count"] == 531441
    assert len(radius["acyclic_choice"]) == 12


def test_block6_survivor_radius_propagation_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_survivor_radius_propagation.py",
            "--assert-pass",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "status: PASS_RADIUS_PROPAGATION" in result.stdout
    assert "short-gap choices: 531441" in result.stdout
    assert "OK: radius-propagation pass expectation verified" in result.stdout
