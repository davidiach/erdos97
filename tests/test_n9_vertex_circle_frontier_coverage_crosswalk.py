from __future__ import annotations

import pytest

from scripts.check_n9_vertex_circle_frontier_coverage_crosswalk import (
    CLAIM_SCOPE,
    EXPECTED_ASSIGNMENT_COUNT,
    EXPECTED_SEQUENCE_ROWS_SHA256,
    EXPECTED_SORTED_ROWS_SHA256,
    assert_expected_frontier_coverage_crosswalk,
    frontier_coverage_crosswalk_payload,
)

pytestmark = pytest.mark.slow


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
