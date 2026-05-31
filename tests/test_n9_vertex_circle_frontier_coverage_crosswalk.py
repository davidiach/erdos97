from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_frontier_coverage_crosswalk import (
    CLAIM_SCOPE,
    EXPECTED_ASSIGNMENT_COUNT,
    EXPECTED_SEQUENCE_ROWS_SHA256,
    EXPECTED_SORTED_ROWS_SHA256,
    assert_expected_frontier_coverage_crosswalk,
    frontier_coverage_crosswalk_payload,
    summary_json_payload,
)

pytestmark = pytest.mark.slow
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return frontier_coverage_crosswalk_payload()


def test_frontier_coverage_crosswalk_payload_scope_and_counts(
    payload: dict[str, object],
) -> None:
    assert_expected_frontier_coverage_crosswalk(payload)
    assert payload["validation_status"] == "passed"
    summary = payload["frontier_coverage_crosswalk"]
    assert summary["generated_assignment_count"] == EXPECTED_ASSIGNMENT_COUNT
    assert summary["stored_assignment_count"] == EXPECTED_ASSIGNMENT_COUNT
    assert summary["sequence_matches"] is True
    assert summary["set_matches"] is True
    assert summary["status_mismatches"] == 0
    assert summary["generated_sorted_rows_sha256"] == EXPECTED_SORTED_ROWS_SHA256
    assert summary["stored_sequence_rows_sha256"] == EXPECTED_SEQUENCE_ROWS_SHA256
    assert summary["example_mismatches"] == []
    assert "does not prove filter soundness" in payload["claim_scope"]
    assert "counterexample" in payload["claim_scope"]


def test_frontier_coverage_crosswalk_rejects_top_level_claim_scope_append(
    payload: dict[str, object],
) -> None:
    tampered = dict(payload)
    tampered["claim_scope"] = CLAIM_SCOPE + " This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_frontier_coverage_crosswalk(tampered)


def test_frontier_coverage_crosswalk_summary_json_payload(
    payload: dict[str, object],
) -> None:
    summary = summary_json_payload(payload)

    assert "frontier_coverage_crosswalk" not in summary
    assert summary["schema"] == payload["schema"]
    assert summary["claim_scope"] == payload["claim_scope"]
    crosswalk = summary["frontier_coverage_crosswalk_summary"]
    assert crosswalk["generated_assignment_count"] == EXPECTED_ASSIGNMENT_COUNT
    assert crosswalk["stored_assignment_count"] == EXPECTED_ASSIGNMENT_COUNT
    assert crosswalk["sequence_matches"] is True
    assert crosswalk["generated_sorted_rows_sha256"] == EXPECTED_SORTED_ROWS_SHA256
    assert crosswalk["generated_sequence_rows_sha256"] == EXPECTED_SEQUENCE_ROWS_SHA256
    assert "example_mismatches" not in crosswalk


def test_frontier_coverage_crosswalk_cli_summary_json(
    payload: dict[str, object],
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py",
            "--check",
            "--assert-expected",
            "--summary-json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout) == summary_json_payload(payload)
