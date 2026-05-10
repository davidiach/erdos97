from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_block6_survivor_ptolemy_feasibility import audit


ROOT = Path(__file__).resolve().parents[1]


def test_block6_survivor_has_positive_quotient_ptolemy_assignment() -> None:
    payload = audit()

    assert payload["distance_class_count"] == 33
    assert payload["positive_assignment"] is True
    assert payload["row_ptolemy_equations_verified"] == 12

    values = payload["distance_class_values"]
    assert values["0"] == "1"
    assert values["5"] == "3"
    assert values["9"] == "1/2"
    assert values["27"] == "6"

    rows = payload["records"]
    assert rows[0]["classes"] == {
        "d01": 0,
        "d02": 5,
        "d03": 6,
        "d12": 0,
        "d13": 9,
        "d23": 0,
    }
    assert rows[0]["ptolemy_lhs"] == "3/2"
    assert rows[0]["ptolemy_rhs"] == "3/2"


def test_block6_survivor_ptolemy_feasibility_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_survivor_ptolemy_feasibility.py",
            "--assert-expected",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "distance classes: 33" in result.stdout
    assert "row-Ptolemy equations verified: 12" in result.stdout
    assert "OK: expected feasibility certificate verified" in result.stdout
