from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97 import n9_vertex_circle_exhaustive as n9
from erdos97.vertex_circle_quotient_replay import parse_selected_rows
from scripts.check_n9_vertex_circle_quotient_soundness import (
    CLAIM_SCOPE,
    EXPECTED_FRONTIER_CORE,
    EXPECTED_FRONTIER_FULL,
    EXPECTED_LOCAL_CORE,
    assert_expected_quotient_soundness,
    direct_quotient_result,
    quotient_soundness_payload,
    summary_json_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_direct_quotient_result_matches_checker_for_sample_rows() -> None:
    rows = parse_selected_rows(
        [
            [0, 1, 2, 3, 8],
            [1, 0, 2, 4, 7],
            [8, 0, 1, 4, 5],
        ]
    )
    direct = direct_quotient_result(n9.N, n9.ORDER, rows)

    assert direct.status == "self_edge"
    assert direct.selected_row_count == 3
    assert direct.strict_edge_count == 27
    assert direct.self_edge_count > 0
    assert direct.row_equality_component_violations == 0


def test_quotient_soundness_expected_counts_and_scope() -> None:
    payload = quotient_soundness_payload()

    assert_expected_quotient_soundness(payload)
    assert payload["validation_status"] == "passed"
    assert payload["local_core_packet"]["row_set_count"] == EXPECTED_LOCAL_CORE["row_set_count"]
    assert (
        payload["frontier_full_assignments"]["selected_row_total"]
        == EXPECTED_FRONTIER_FULL["selected_row_total"]
    )
    assert (
        payload["frontier_core_assignments"]["spoke_pairs_checked"]
        == EXPECTED_FRONTIER_CORE["spoke_pairs_checked"]
    )
    assert "strict-edge geometry" in payload["claim_scope"]
    assert "counterexample" in payload["claim_scope"]
    assert "official/global status update" in payload["claim_scope"]


def test_quotient_soundness_rejects_top_level_claim_scope_append() -> None:
    payload = quotient_soundness_payload()
    payload["claim_scope"] = CLAIM_SCOPE + " This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_quotient_soundness(payload)


def test_quotient_soundness_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_quotient_soundness.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    parsed = json.loads(result.stdout)
    assert parsed["validation_status"] == "passed"
    assert parsed["local_core_packet"]["status_counts"] == {
        "self_edge": 13,
        "strict_cycle": 3,
    }
    assert parsed["frontier_full_assignments"]["strict_edge_count_histogram"] == {
        "81": 184
    }


def test_quotient_soundness_summary_json_payload() -> None:
    payload = quotient_soundness_payload()

    summary = summary_json_payload(payload)

    assert "local_core_packet" not in summary
    assert "frontier_full_assignments" not in summary
    assert "frontier_core_assignments" not in summary
    assert summary["schema"] == payload["schema"]
    assert summary["claim_scope"] == payload["claim_scope"]
    local_core = summary["local_core_packet_summary"]
    frontier_full = summary["frontier_full_assignments_summary"]
    frontier_core = summary["frontier_core_assignments_summary"]
    assert local_core["row_set_count"] == EXPECTED_LOCAL_CORE["row_set_count"]
    assert frontier_full["selected_row_total"] == EXPECTED_FRONTIER_FULL["selected_row_total"]
    assert frontier_core["spoke_pairs_checked"] == EXPECTED_FRONTIER_CORE["spoke_pairs_checked"]
    assert frontier_full["status_mismatches"] == 0
    assert "recorded_status_counts" not in frontier_full
    assert "example_mismatches" not in frontier_core
    assert summary["validation_status"] == "passed"


def test_quotient_soundness_cli_summary_json() -> None:
    payload = quotient_soundness_payload()
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_quotient_soundness.py",
            "--check",
            "--assert-expected",
            "--summary-json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    expected = json.loads(json.dumps(summary_json_payload(payload), sort_keys=True))
    assert json.loads(result.stdout) == expected
