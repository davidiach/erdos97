from __future__ import annotations

import copy

import pytest

from erdos97.bootstrap_t12_outside_pair import (
    LEDGER_HIT_MODE,
    PRIVATE_HALO_ONLY_MODE,
    assert_expected_payload,
    build_t12_outside_pair_payload,
)


def test_bootstrap_t12_outside_pair_expected_payload() -> None:
    payload = build_t12_outside_pair_payload()

    assert_expected_payload(payload)
    summary = payload["summary"]
    assert summary["outside_pair_row_record_count"] == 1
    assert summary["support_pair_option_count"] == 3
    assert summary["forcing_target_status"] == "OPEN_TARGET_NOT_PROVED"


def test_bootstrap_t12_outside_pair_isolates_expected_row() -> None:
    payload = build_t12_outside_pair_payload()
    record = payload["records"][0]

    assert record["source_record_id"] == 151
    assert record["classification_assignment_id"] == "A152"
    assert record["row_center"] == 6
    assert record["roles"] == ["equality_connector_row"]
    assert record["witnesses"] == [0, 3, 5, 8]
    assert record["bootstrap_core_witnesses"] == [0]
    assert record["outside_witnesses"] == [3, 5, 8]
    assert record["row_center_private_in_all_deletion_closures"]


def test_bootstrap_t12_outside_pair_support_modes() -> None:
    payload = build_t12_outside_pair_payload()
    record = payload["records"][0]
    actual = [
        (option["support_pair"], option["support_pair_mode"])
        for option in record["support_pair_options"]
    ]

    assert actual == [
        ([3, 5], PRIVATE_HALO_ONLY_MODE),
        ([3, 8], LEDGER_HIT_MODE),
        ([5, 8], LEDGER_HIT_MODE),
    ]


def test_bootstrap_t12_outside_pair_support_activation_and_privacy() -> None:
    payload = build_t12_outside_pair_payload()
    record = payload["records"][0]

    for option in record["support_pair_options"]:
        assert option["activation_ready_with_pair"]
        assert option["activation_witness_count"] == 3
        assert option["pair_private_in_all_deletion_halos"]
        assert option["private_halo_containment_count"] == 4


def test_bootstrap_t12_outside_pair_ledger_hits_are_partial() -> None:
    payload = build_t12_outside_pair_payload()
    record = payload["records"][0]
    by_key = {
        option["support_pair_key"]: option
        for option in record["support_pair_options"]
    }

    assert not by_key["3-5"]["ledger_private_pair_hit"]
    assert by_key["3-8"]["ledger_private_pair_core_vertices"] == [0]
    assert by_key["5-8"]["ledger_private_pair_core_vertices"] == [2]


def test_bootstrap_t12_outside_pair_expected_payload_rejects_drift() -> None:
    payload = build_t12_outside_pair_payload()
    bad = copy.deepcopy(payload)
    bad["summary"]["ledger_private_pair_support_hit_count"] = 3

    with pytest.raises(AssertionError, match="ledger_private_pair_support_hit_count"):
        assert_expected_payload(bad)
