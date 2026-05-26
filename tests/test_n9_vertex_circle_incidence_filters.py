from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_incidence_filters import (
    CLAIM_SCOPE,
    EXPECTED_SELECTED_INDEGREE,
    EXPECTED_TWO_OVERLAP,
    EXPECTED_WITNESS_PAIR_CAP,
    assert_expected_incidence_filters,
    incidence_filter_payload,
    selected_indegree_cap_audit,
    two_overlap_crossing_audit,
    witness_pair_cap_audit,
)

ROOT = Path(__file__).resolve().parents[1]


def test_incidence_filter_sections_match_expected_counts() -> None:
    assert two_overlap_crossing_audit() == EXPECTED_TWO_OVERLAP
    assert witness_pair_cap_audit() == EXPECTED_WITNESS_PAIR_CAP
    assert selected_indegree_cap_audit() == EXPECTED_SELECTED_INDEGREE


def test_incidence_filter_payload_scope_and_validation() -> None:
    payload = incidence_filter_payload()

    assert_expected_incidence_filters(payload)
    assert payload["validation_status"] == "passed"
    assert "does not replay the brancher" in payload["claim_scope"]
    assert "strict-edge geometry" in payload["claim_scope"]
    assert "selected-distance quotient" in payload["claim_scope"]
    assert "counterexample" in payload["claim_scope"]


def test_incidence_filter_rejects_top_level_claim_scope_append() -> None:
    payload = incidence_filter_payload()
    payload["claim_scope"] = CLAIM_SCOPE + " This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_incidence_filters(payload)


def test_incidence_filter_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_incidence_filters.py",
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
    assert parsed["two_overlap_crossing"]["compatibility_errors"] == 0
    assert parsed["witness_pair_cap"]["witness_pair_frequency_histogram"] == {
        "21": 36
    }
    assert parsed["selected_indegree_cap"]["label_frequency_histogram"] == {
        "56": 9
    }
