from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.check_s12a_equilateral_ears import (
    CLAIM_SCOPE,
    STATUS,
    TRUST,
    build_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_s12a_payload_has_exact_fixed_order_obstruction() -> None:
    payload = build_payload()

    assert validate_payload(payload) == []
    assert payload["status"] == STATUS
    assert payload["trust"] == TRUST
    assert payload["claim_scope"] == CLAIM_SCOPE
    assert payload["forced_middle_vertices"] == [1, 3, 5, 7, 9, 11]
    assert payload["forced_turn_over_pi"] == [4, 1]
    assert payload["strictly_convex_total_turn_over_pi"] == [2, 1]


def test_s12a_cli_replays_stored_artifact() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_s12a_equilateral_ears.py",
            "--check",
            "--assert-expected",
            "--summary-json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["status"] == STATUS
    assert payload["forced_ear_count"] == 6
    assert payload["contradiction"] == "4*pi > 2*pi"
