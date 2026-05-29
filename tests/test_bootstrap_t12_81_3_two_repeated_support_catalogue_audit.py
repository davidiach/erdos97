from __future__ import annotations

import copy
import json

import pytest

from erdos97.bootstrap_t12_81_3_two_repeated_support_catalogue_audit import (
    DEFAULT_ARTIFACT,
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_81_3_two_repeated_support_catalogue_audit_payload,
)


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_81_3_two_repeated_support_catalogue_audit_payload()


def test_bootstrap_t12_81_3_two_repeated_support_expected_payload(
    payload: dict[str, object],
) -> None:
    assert_expected_payload(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_81_3_TWO_REPEATED_SUPPORT_CATALOGUE_AUDIT_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "two-repeated-support layer" in claim_scope
    assert "not a proof of support existence" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope

    summary = payload["summary"]
    assert summary["scan_status"] == SCAN_STATUS
    assert summary["source_prefix_survivor_count"] == 4
    assert summary["source_one_repeated_candidate_count"] == 5
    assert summary["ordered_two_repeated_generation_path_count"] == 2
    assert summary["two_repeated_support_catalogue_count"] == 1
    assert summary["supply_extension_candidate_count"] == 118
    assert summary["supply_extension_initially_compatible_count"] == 0
    assert summary["supply_extension_survivor_count"] == 0


def test_bootstrap_t12_81_3_two_repeated_support_shapes(
    payload: dict[str, object],
) -> None:
    scan = payload["two_repeated_support_catalogue_scan"]
    records = scan["records"]
    assert len(records) == 1
    record = records[0]
    assert record["prefix_survivor_index"] == 1
    assert record["repeated_supports"] == [
        {"center": 2, "support": [0, 5, 6, 7], "support_size": 4},
        {"center": 8, "support": [2, 3, 5, 6], "support_size": 4},
    ]
    assert record["ordered_generation_path_count"] == 2
    assert record["initial_status"] == "INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE"
    assert record["detected_solution_count"] == 0
    assert scan["survivors"] == []

    supply_scan = payload["supply_extension_scan"]
    assert supply_scan["aggregate"]["initial_status:INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE"] == 118
    assert supply_scan["initially_compatible_catalogues"] == []
    assert supply_scan["survivors"] == []


def test_bootstrap_t12_81_3_two_repeated_support_artifact_matches_generator(
    payload: dict[str, object],
) -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == payload


def test_bootstrap_t12_81_3_two_repeated_support_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["supply_extension_survivor_count"] = 1

    with pytest.raises(AssertionError, match="supply_extension_survivor_count"):
        assert_expected_payload(bad)
