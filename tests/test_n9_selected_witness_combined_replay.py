from __future__ import annotations

import pytest

from scripts.check_n9_selected_witness_combined_replay import (
    CLAIM_SCOPE,
    EXPECTED_CERTIFICATE_DIGEST,
    EXPECTED_FRONTIER_ASSIGNMENTS,
    assert_expected_certificates,
    assert_expected_summary,
    generate_replay,
)


@pytest.mark.artifact
def test_combined_replay_expected_payload_and_certificates() -> None:
    result = generate_replay()

    assert_expected_summary(result.summary)
    assert_expected_certificates(result.certificates_payload)
    assert result.summary["certificate_count"] == EXPECTED_FRONTIER_ASSIGNMENTS
    assert result.summary["certificate_digest_sha256"] == EXPECTED_CERTIFICATE_DIGEST
    assert result.summary["brancher"]["obstruction_counts"] == {
        "self_edge": 158,
        "strict_cycle": 26,
    }
    assert result.summary["brancher"]["clean_assignments"] == 0


@pytest.mark.artifact
def test_combined_replay_rejects_appended_claim_scope_overclaim() -> None:
    result = generate_replay()
    result.summary["claim_scope"] = f"{CLAIM_SCOPE} This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_summary(result.summary)
