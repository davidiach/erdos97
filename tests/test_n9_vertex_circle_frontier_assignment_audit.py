from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_frontier_assignment_audit import (
    CLAIM_SCOPE,
    EXPECTED_ASSIGNMENT_WITNESS_PAIR_PROFILES,
    EXPECTED_CENTER_PAIR_INTERSECTION_HISTOGRAM,
    EXPECTED_SELECTED_INDEGREE_VALUE_HISTOGRAM,
    EXPECTED_WITNESS_PAIR_FREQUENCY_HISTOGRAM,
    assert_expected_frontier_assignment_audit,
    frontier_assignment_audit_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_frontier_assignment_audit_payload_scope_and_counts() -> None:
    payload = frontier_assignment_audit_payload()

    assert_expected_frontier_assignment_audit(payload)
    assert payload["validation_status"] == "passed"
    summary = payload["frontier_assignment_audit"]
    assert summary["assignment_count"] == 184
    assert summary["row_count_total"] == 1_656
    assert summary["status_counts"] == {"self_edge": 158, "strict_cycle": 26}
    assert summary["center_pair_intersection_histogram"] == (
        EXPECTED_CENTER_PAIR_INTERSECTION_HISTOGRAM
    )
    assert summary["witness_pair_frequency_histogram"] == (
        EXPECTED_WITNESS_PAIR_FREQUENCY_HISTOGRAM
    )
    assert summary["selected_indegree_value_histogram"] == (
        EXPECTED_SELECTED_INDEGREE_VALUE_HISTOGRAM
    )
    assert summary["assignment_witness_pair_profiles"] == (
        EXPECTED_ASSIGNMENT_WITNESS_PAIR_PROFILES
    )
    assert summary["example_errors"] == []
    assert "stored 184 frontier assignments" in payload["claim_scope"]
    assert "does not prove frontier coverage" in payload["claim_scope"]
    assert "counterexample" in payload["claim_scope"]


def test_frontier_assignment_audit_rejects_appended_claim_scope_overclaim() -> None:
    payload = frontier_assignment_audit_payload()
    payload["claim_scope"] = f"{CLAIM_SCOPE} This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_frontier_assignment_audit(payload)


def test_frontier_assignment_audit_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_frontier_assignment_audit.py",
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
    summary = parsed["frontier_assignment_audit"]
    assert parsed["validation_status"] == "passed"
    assert summary["center_pair_intersection_histogram"] == {
        "0": 72,
        "1": 3168,
        "2": 3384,
    }
    assert summary["witness_pair_frequency_histogram"] == {
        "0": 72,
        "1": 3168,
        "2": 3384,
    }
    assert summary["selected_indegree_value_histogram"] == {"4": 1656}
    assert summary["two_overlap_crossing_violations"] == 0
    assert summary["witness_pair_cap_violations"] == 0
    assert summary["selected_indegree_cap_violations"] == 0
