from __future__ import annotations

import copy

import pytest

from erdos97.bootstrap_t12_forcing_targets import (
    assert_expected_payload,
    build_t12_forcing_targets_payload,
)


def test_bootstrap_t12_forcing_targets_expected_payload() -> None:
    payload = build_t12_forcing_targets_payload()

    assert_expected_payload(payload)
    summary = payload["summary"]
    assert summary["source_record_ids"] == [81, 151]
    assert summary["template_counts"] == {"T12": 2}
    assert summary["row_gap_counts_by_source_id"] == {"81": 2, "151": 4}
    assert summary["forcing_target_status"] == "OPEN_TARGET_NOT_PROVED"


def test_bootstrap_t12_forcing_targets_private_pair_gap() -> None:
    payload = build_t12_forcing_targets_payload()
    by_source = {record["source_record_id"]: record for record in payload["records"]}

    assert by_source[81]["private_pair_hit_pairs"] == []
    assert by_source[81]["diagnosis"]["private_pair_only_target_status"] == "NO_DIRECT_HITS"
    assert by_source[151]["private_pair_hit_pairs"] == [[5, 8], [6, 8]]
    assert (
        by_source[151]["diagnosis"]["private_pair_only_target_status"]
        == "PARTIAL_DIRECT_HITS_ONLY"
    )


def test_bootstrap_t12_forcing_targets_row_center_gaps() -> None:
    payload = build_t12_forcing_targets_payload()
    by_source = {record["source_record_id"]: record for record in payload["records"]}

    assert by_source[81]["row_gap_centers"] == [3, 8]
    assert by_source[81]["row_gap_role_counts"] == {"equality_connector_row": 2}
    assert by_source[151]["row_gap_centers"] == [5, 6, 7, 8]
    assert by_source[151]["row_gap_role_counts"] == {
        "equality_connector_row": 3,
        "strict_edge_row": 2,
    }


def test_bootstrap_t12_forcing_targets_expected_payload_rejects_drift() -> None:
    payload = build_t12_forcing_targets_payload()
    bad = copy.deepcopy(payload)
    bad["summary"]["row_gap_counts_by_source_id"] = {"81": 0, "151": 0}

    with pytest.raises(AssertionError, match="row_gap_counts_by_source_id"):
        assert_expected_payload(bad)
