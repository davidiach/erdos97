from __future__ import annotations

from erdos97.bootstrap_t12_151_singleton_two_row_drop import (
    DEFAULT_ARTIFACT,
    SCAN_STATUS,
    assert_expected_payload,
    load_artifact,
)


def test_source151_two_row_drop_artifact_matches_expected_counts() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_payload(payload)
    summary = payload["summary"]
    assert summary["scan_status"] == SCAN_STATUS
    assert summary["two_row_drop_candidate_count"] == 2_469_600
    assert summary["two_row_drop_surviving_candidate_count"] == 56
    assert summary["two_row_drop_non_original_survivor_count"] == 0


def test_source151_two_row_drop_target_counts() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    by_key = {
        record["target_row_key"]: record
        for record in payload["target_audits"]
    }

    assert by_key["151:5"]["two_row_drop_candidate_count"] == 1_234_800
    assert by_key["151:8"]["two_row_drop_candidate_count"] == 1_234_800
    assert by_key["151:5"]["two_row_drop_surviving_candidate_count"] == 28
    assert by_key["151:8"]["two_row_drop_surviving_candidate_count"] == 28
    assert by_key["151:5"]["two_row_drop_survivors_all_original_rows"] is True
    assert by_key["151:8"]["two_row_drop_survivors_all_original_rows"] is True
