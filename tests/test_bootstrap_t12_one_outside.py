from __future__ import annotations

import copy

import pytest

from erdos97.bootstrap_t12_one_outside import (
    CLOSURE_INTERNAL_MODE,
    PRIVATE_ALL_MODE,
    assert_expected_payload,
    build_t12_one_outside_payload,
)


def test_bootstrap_t12_one_outside_expected_payload() -> None:
    payload = build_t12_one_outside_payload()

    assert_expected_payload(payload)
    summary = payload["summary"]
    assert summary["one_outside_row_record_count"] == 3
    assert summary["support_option_count"] == 6
    assert summary["forcing_target_status"] == "OPEN_TARGET_NOT_PROVED"


def test_bootstrap_t12_one_outside_isolates_expected_rows() -> None:
    payload = build_t12_one_outside_payload()
    by_key = {
        (record["source_record_id"], record["row_center"]): record
        for record in payload["records"]
    }

    assert set(by_key) == {(81, 8), (151, 5), (151, 8)}
    assert by_key[(81, 8)]["bootstrap_core_witnesses"] == [0, 2]
    assert by_key[(151, 5)]["bootstrap_core_witnesses"] == [2, 4]
    assert by_key[(151, 8)]["bootstrap_core_witnesses"] == [1, 2]
    assert all(record["row_center_private_in_all_deletion_closures"] for record in by_key.values())


def test_bootstrap_t12_one_outside_support_modes() -> None:
    payload = build_t12_one_outside_payload()
    by_key = {
        (record["source_record_id"], record["row_center"]): record
        for record in payload["records"]
    }

    expected = {
        (81, 8): [(5, PRIVATE_ALL_MODE), (6, CLOSURE_INTERNAL_MODE)],
        (151, 5): [(7, CLOSURE_INTERNAL_MODE), (8, PRIVATE_ALL_MODE)],
        (151, 8): [(5, PRIVATE_ALL_MODE), (7, CLOSURE_INTERNAL_MODE)],
    }
    for key, expected_options in expected.items():
        actual = [
            (option["support_label"], option["support_label_mode"])
            for option in by_key[key]["support_options"]
        ]
        assert actual == expected_options


def test_bootstrap_t12_one_outside_support_activation_and_ledger() -> None:
    payload = build_t12_one_outside_payload()
    for record in payload["records"]:
        for option in record["support_options"]:
            assert option["activation_ready_with_support"]
            assert option["activation_witness_count"] == 3
            assert not option["ledger_private_pair_hit"]


def test_bootstrap_t12_one_outside_expected_payload_rejects_drift() -> None:
    payload = build_t12_one_outside_payload()
    bad = copy.deepcopy(payload)
    bad["summary"]["support_label_counts"] = {"5": 6}

    with pytest.raises(AssertionError, match="support_label_counts"):
        assert_expected_payload(bad)
