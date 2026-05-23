from __future__ import annotations

import pytest

from scripts.check_n9_vertex_circle_frontier_coverage_crosswalk import (
    EXPECTED_ASSIGNMENT_COUNT,
    EXPECTED_SEQUENCE_ROWS_SHA256,
    EXPECTED_SORTED_ROWS_SHA256,
    assert_expected_frontier_coverage_crosswalk,
    frontier_coverage_crosswalk_payload,
)

pytestmark = pytest.mark.slow


def test_frontier_coverage_crosswalk_payload_scope_and_counts() -> None:
    payload = frontier_coverage_crosswalk_payload()

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
