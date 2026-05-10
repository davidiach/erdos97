from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_block6_fragile_sixth_row_survivors import (
    assert_expected,
    survivor_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_block6_sixth_row_survivor_catalog_matches_expected() -> None:
    payload = survivor_payload()

    assert_expected(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert "not a proof" in payload["claim_scope"]
    assert payload["totals"]["clean_fifth_rows"] == 166
    assert payload["totals"]["clean_fifth_rows_with_clean_sixth"] == 166
    assert payload["totals"]["unique_clean_six_row_states"] == 6047
    assert payload["totals"]["clean_center_pairs"] == 28
    assert payload["totals"]["clean_center_pair_block_swap_orbits"] == 16
    assert payload["clean_by_center_pair"]["4,5"] == 28
    assert payload["clean_by_center_pair"]["2,8"] == 1074
    assert payload["clean_by_center_pair_orbit"]["4,5|10,11"] == 56
    assert payload["clean_by_center_pair_orbit"]["2,8"] == 1074
    low_support_forms = payload["low_support_row_content_forms"]
    assert low_support_forms["4,5"]["clean_states"] == 28
    assert low_support_forms["4,5"]["all_disjoint_pool_edges_present"] is True
    assert low_support_forms["10,11"]["clean_states"] == 28
    assert low_support_forms["10,11"]["all_disjoint_pool_edges_present"] is True
    assert low_support_forms["4,5"]["same_block_pair_counts"] == {
        "0,3|0,1": 14,
        "0,3|0,4": 14,
    }
    assert payload["first_clean_sixth_example"] == {
        "fifth": {"center": 1, "row": [0, 2, 6, 7]},
        "sixth": {"center": 2, "row": [0, 1, 3, 8]},
    }


def test_block6_sixth_row_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_fragile_sixth_row_survivors.py",
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
