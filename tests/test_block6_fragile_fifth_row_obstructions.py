from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_block6_fragile_fifth_row_obstructions import (
    assert_expected,
    catalog_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_block6_fifth_row_catalog_matches_expected() -> None:
    payload = catalog_payload()

    assert_expected(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert "not a proof" in payload["claim_scope"]
    assert payload["totals"] == {
        "valid": 342,
        "ok": 166,
        "self_edge": 82,
        "strict_cycle": 94,
    }
    assert payload["center_counts"]["5"]["first_examples"]["ok"] == [0, 1, 6, 7]


def test_block6_fifth_row_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_fragile_fifth_row_obstructions.py",
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
