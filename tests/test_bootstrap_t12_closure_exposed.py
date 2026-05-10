from __future__ import annotations

import copy

import pytest

from erdos97.bootstrap_t12_closure_exposed import (
    CORE_WITNESS_MODE,
    FULL_ROW_MODE,
    assert_expected_payload,
    build_t12_closure_exposed_payload,
)


def test_bootstrap_t12_closure_exposed_expected_payload() -> None:
    payload = build_t12_closure_exposed_payload()

    assert_expected_payload(payload)
    summary = payload["summary"]
    assert summary["closure_exposed_row_record_count"] == 2
    assert summary["forcing_target_status"] == "OPEN_TARGET_NOT_PROVED"


def test_bootstrap_t12_closure_exposed_isolates_expected_rows() -> None:
    payload = build_t12_closure_exposed_payload()
    by_key = {
        (record["source_record_id"], record["row_center"]): record
        for record in payload["records"]
    }

    assert set(by_key) == {(81, 3), (151, 7)}
    assert by_key[(81, 3)]["exposed_core_vertex"] == 2
    assert by_key[(151, 7)]["exposed_core_vertex"] == 2
    assert by_key[(81, 3)]["core_witnesses_in_closure"] == [0, 1, 4]
    assert by_key[(151, 7)]["core_witnesses_in_closure"] == [0, 1, 4]


def test_bootstrap_t12_closure_exposed_modes() -> None:
    payload = build_t12_closure_exposed_payload()
    by_key = {
        (record["source_record_id"], record["row_center"]): record
        for record in payload["records"]
    }

    assert by_key[(81, 3)]["closure_exposure_mode"] == FULL_ROW_MODE
    assert by_key[(81, 3)]["full_row_contained_in_exposure_closure"]
    assert by_key[(81, 3)]["outside_witnesses_in_closure"] == [6]
    assert by_key[(81, 3)]["outside_witnesses_private"] == []

    assert by_key[(151, 7)]["closure_exposure_mode"] == CORE_WITNESS_MODE
    assert not by_key[(151, 7)]["full_row_contained_in_exposure_closure"]
    assert by_key[(151, 7)]["outside_witnesses_in_closure"] == []
    assert by_key[(151, 7)]["outside_witnesses_private"] == [6]


def test_bootstrap_t12_closure_exposed_expected_payload_rejects_drift() -> None:
    payload = build_t12_closure_exposed_payload()
    bad = copy.deepcopy(payload)
    bad["summary"]["closure_exposed_row_record_count"] = 3

    with pytest.raises(AssertionError, match="closure_exposed_row_record_count"):
        assert_expected_payload(bad)
