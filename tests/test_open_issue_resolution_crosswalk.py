from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_open_issue_resolution_crosswalk import (
    EXPECTED_ISSUES,
    assert_expected,
    crosswalk_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_open_issue_resolution_crosswalk_expected() -> None:
    payload = crosswalk_payload()

    assert_expected(payload)
    assert payload["ok"] is True
    assert payload["issue_numbers"] == list(EXPECTED_ISSUES)
    assert payload["safe_closure_recommendation_issue_numbers"] == list(EXPECTED_ISSUES)


def test_open_issue_resolution_crosswalk_rows_are_scoped() -> None:
    payload = crosswalk_payload()
    by_number = {row["issue_number"]: row for row in payload["issues"]}

    assert by_number[5]["evidence"]["b12_failure_mode"] == "floating_near_miss"
    assert by_number[81]["evidence"]["survivor_order"] is None
    assert by_number[82]["evidence"]["incidence_state"] == "UNKNOWN"
    assert by_number[83]["evidence"]["compact_inequality_count"] == 2
    for row in payload["issues"]:
        assert "proof" in row["claim_boundary"]
        assert row["safe_closure_recommendation"] is True


def test_open_issue_resolution_crosswalk_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_open_issue_resolution_crosswalk.py",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema"] == "erdos97.open_issue_resolution_crosswalk.v1"
    assert payload["safe_closure_recommendation_issue_numbers"] == [5, 81, 82, 83]
