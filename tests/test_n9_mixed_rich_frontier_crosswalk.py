from __future__ import annotations

import pytest

from scripts.check_n9_mixed_rich_frontier_crosswalk import (
    CLAIM_SCOPE,
    EXPECTED_SUMMARY,
    assert_expected_payload,
    mixed_frontier_crosswalk_payload,
)

pytestmark = pytest.mark.slow


def test_n9_mixed_rich_frontier_crosswalk_payload() -> None:
    payload = mixed_frontier_crosswalk_payload()

    assert_expected_payload(payload)
    assert payload["validation_status"] == "passed"
    summary = payload["mixed_rich_frontier_crosswalk"]
    assert summary["set_matches"] is True
    assert summary["sequence_matches"] is False
    assert summary["sequence_mismatch_count"] == 6
    assert summary["matched_frontier_status_counts"] == {
        "self_edge": 158,
        "strict_cycle": 26,
    }
    assert summary["mixed_sorted_rows_sha256"] == EXPECTED_SUMMARY[
        "mixed_sorted_rows_sha256"
    ]
    assert summary["frontier_sorted_rows_sha256"] == EXPECTED_SUMMARY[
        "frontier_sorted_rows_sha256"
    ]
    assert "does not prove the exact-four vertex-circle exhaustive checker" in payload[
        "claim_scope"
    ]
    assert "counterexample" in payload["claim_scope"]


def test_n9_mixed_rich_frontier_crosswalk_rejects_appended_claim_scope_overclaim() -> None:
    payload = mixed_frontier_crosswalk_payload()
    payload["claim_scope"] = f"{CLAIM_SCOPE} This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_payload(payload)
