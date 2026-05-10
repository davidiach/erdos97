from __future__ import annotations

import copy

import pytest

from erdos97.bootstrap_t12_row_pressure import (
    assert_expected_payload,
    build_t12_row_pressure_payload,
)


def test_bootstrap_t12_row_pressure_expected_payload() -> None:
    payload = build_t12_row_pressure_payload()

    assert_expected_payload(payload)
    summary = payload["summary"]
    assert summary["row_gap_record_count"] == 6
    assert summary["activation_deficit_counts"] == {"0": 2, "1": 3, "2": 1}
    assert summary["forcing_target_status"] == "OPEN_TARGET_NOT_PROVED"


def test_bootstrap_t12_row_pressure_classifies_rows() -> None:
    payload = build_t12_row_pressure_payload()
    by_key = {
        (record["source_record_id"], record["row_center"]): record
        for record in payload["row_records"]
    }

    assert by_key[(81, 3)]["pressure_class"] == "ALREADY_PRESENT_IN_A_DELETION_CLOSURE"
    assert by_key[(151, 7)]["pressure_class"] == "ALREADY_PRESENT_IN_A_DELETION_CLOSURE"
    assert by_key[(151, 6)]["pressure_class"] == "NEEDS_OUTSIDE_PAIR_AND_PRIVATE_CENTER"
    assert by_key[(151, 6)]["ledger_private_pair_support_hit_count"] == 2


def test_bootstrap_t12_row_pressure_private_center_rows() -> None:
    payload = build_t12_row_pressure_payload()
    by_key = {
        (record["source_record_id"], record["row_center"]): record
        for record in payload["row_records"]
    }

    assert by_key[(81, 8)]["row_center_private_in_all_deletion_closures"]
    assert by_key[(151, 5)]["row_center_private_in_all_deletion_closures"]
    assert by_key[(151, 6)]["row_center_private_in_all_deletion_closures"]
    assert by_key[(151, 8)]["row_center_private_in_all_deletion_closures"]
    assert not by_key[(81, 3)]["row_center_private_in_all_deletion_closures"]
    assert not by_key[(151, 7)]["row_center_private_in_all_deletion_closures"]


def test_bootstrap_t12_row_pressure_expected_payload_rejects_drift() -> None:
    payload = build_t12_row_pressure_payload()
    bad = copy.deepcopy(payload)
    bad["summary"]["pressure_class_counts"] = {"NEEDS_OUTSIDE_PAIR_AND_PRIVATE_CENTER": 6}

    with pytest.raises(AssertionError, match="pressure_class_counts"):
        assert_expected_payload(bad)
