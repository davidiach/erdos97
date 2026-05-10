from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_endpoint_control_survivor_ptolemy_feasibility import audit


ROOT = Path(__file__).resolve().parents[1]


def test_endpoint_control_survivor_has_positive_quotient_ptolemy_assignment() -> None:
    payload = audit()

    assert payload["distance_class_count"] == 25
    assert payload["positive_assignment"] is True
    assert payload["row_ptolemy_equations_verified"] == 11

    values = payload["distance_class_values"]
    assert values["0"] == "1"
    assert values["2"] == "1/2"
    assert values["4"] == "3"
    assert values["6"] == "2"
    assert values["14"] == "19/4"
    assert values["15"] == "11/4"

    rows = payload["records"]
    assert rows[0]["classes"] == {
        "d01": 7,
        "d02": 8,
        "d03": 9,
        "d12": 0,
        "d13": 13,
        "d23": 0,
    }
    assert rows[0]["ptolemy_lhs"] == "1"
    assert rows[0]["ptolemy_rhs"] == "1"
    assert rows[6]["classes"] == {
        "d01": 6,
        "d02": 4,
        "d03": 0,
        "d12": 6,
        "d13": 18,
        "d23": 2,
    }
    assert rows[6]["ptolemy_lhs"] == "3"
    assert rows[6]["ptolemy_rhs"] == "3"


def test_endpoint_control_survivor_ptolemy_feasibility_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_endpoint_control_survivor_ptolemy_feasibility.py",
            "--assert-expected",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "distance classes: 25" in result.stdout
    assert "row-Ptolemy equations verified: 11" in result.stdout
    assert "OK: expected feasibility certificate verified" in result.stdout
