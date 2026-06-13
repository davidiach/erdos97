from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_center8_source_crosswalk import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
    DEFAULT_SOURCE_CENTER8_PREFLIGHT,
    DEFAULT_SOURCE_ONE_OUTSIDE,
    DEFAULT_SOURCE_SINGLETON_AUDIT,
    GATE_STATUS,
    assert_expected_center8_source_crosswalk,
    build_center8_source_crosswalk_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_center8_preflight() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_CENTER8_PREFLIGHT)


@pytest.fixture(scope="module")
def source_singleton_audit() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_SINGLETON_AUDIT)


@pytest.fixture(scope="module")
def source_one_outside() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_ONE_OUTSIDE)


@pytest.fixture(scope="module")
def source_cascade_endpoint8_targets() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS)


def test_center8_source_crosswalk_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_center8_source_crosswalk(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_SOURCE_CROSSWALK_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "existing source-151 named center-8 singleton/one-outside evidence",
        "center-8 rich class containing [0,4,6]",
        "bootstrap core [1,2]",
        "singleton supports [5,7]",
        "at most one label from [0,4,6]",
        "does not prove support existence",
        "does not prove row forcing",
        "does not prove endpoint-8 forcing",
        "does not prove that pair [3,5] is impossible",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_center8_source_crosswalk_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["cascade_source_record_id"] == 151
    assert summary["conditional_center8_target_center"] == 8
    assert summary["conditional_center8_triple"] == [0, 4, 6]
    assert summary["conditional_center8_preflight_gate_status"] == (
        "NOT_READY_NO_CENTER8_RICH_TRIPLE_SOURCE"
    )
    assert summary["source151_named_center8_target_row_key"] == "151:8"
    assert summary["source151_named_center8_bootstrap_core_witnesses"] == [1, 2]
    assert summary["source151_named_center8_singleton_support_labels"] == [5, 7]
    assert summary["source151_named_center8_original_row"] == [1, 2, 5, 7]
    assert summary["source151_named_center8_candidate_count"] == 9
    assert summary["source151_named_center8_candidate_overlap_histogram"] == {
        "0": 3,
        "1": 6,
    }
    assert summary["source151_named_center8_candidate_rows_with_any_target_label_count"] == 6
    assert summary["source151_named_center8_candidate_rows_with_target_pair_count"] == 0
    assert summary["source151_named_center8_candidate_rows_with_full_target_triple_count"] == 0
    assert summary["source151_named_center8_max_target_triple_overlap"] == 1
    assert summary["source151_one_outside_support_option_count"] == 2
    assert summary["source151_one_outside_activation_overlap_histogram"] == {"0": 2}
    assert summary["source151_one_outside_activation_rows_with_any_target_label_count"] == 0
    assert summary["source151_one_outside_activation_rows_with_full_target_triple_count"] == 0
    assert summary["same_center_as_conditional_target"] is True
    assert summary["same_source_record_as_cascade"] is True
    assert (
        summary["current_source151_named_center8_evidence_supplies_cascade_triple"]
        is False
    )
    assert summary["gate_status"] == GATE_STATUS


def test_center8_source_crosswalk_records() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = {
        record["source_name"]: record for record in payload["source_crosswalk_records"]
    }

    singleton = records["source-151 row-8 singleton activation candidates"]
    assert singleton["target_row_key"] == "151:8"
    assert singleton["row_center"] == 8
    assert singleton["bootstrap_core_witnesses"] == [1, 2]
    assert singleton["singleton_support_labels"] == [5, 7]
    assert singleton["candidate_rows_with_target_pair_count"] == 0
    assert singleton["candidate_rows_with_full_target_triple_count"] == 0
    assert singleton["max_target_triple_overlap"] == 1
    assert singleton["supplies_cascade_triple"] is False
    assert all(
        profile["target_pair_overlap"] == []
        and profile["contains_full_target_triple"] is False
        for profile in singleton["candidate_profiles"]
    )

    one_outside = records["source-151 row-8 one-outside support activations"]
    assert one_outside["support_labels"] == [5, 7]
    assert one_outside["support_option_count"] == 2
    assert one_outside["target_label_overlap_histogram"] == {"0": 2}
    assert one_outside["supplies_cascade_triple"] is False


def test_center8_source_crosswalk_artifact_matches_generator(
    source_center8_preflight: dict[str, object],
    source_singleton_audit: dict[str, object],
    source_one_outside: dict[str, object],
    source_cascade_endpoint8_targets: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_center8_source_crosswalk_payload(
        source_center8_preflight,
        source_singleton_audit,
        source_one_outside,
        source_cascade_endpoint8_targets,
    )


def test_center8_source_crosswalk_rejects_forcing_overclaim() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["current_source151_named_center8_evidence_supplies_cascade_triple"] = True
    bad["decision"]["current_source151_named_center8_evidence_supplies_cascade_triple"] = True
    bad["source_crosswalk_records"][0]["supplies_cascade_triple"] = True

    errors = validate_payload(bad, recompute=False)

    assert any("supplies_cascade_triple" in error for error in errors)


def test_center8_source_crosswalk_rejects_tampered_pair_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["source151_named_center8_candidate_rows_with_target_pair_count"] = 1
    bad["source_crosswalk_records"][0]["candidate_rows_with_target_pair_count"] = 1

    errors = validate_payload(bad, recompute=False)

    assert any("target_pair_count" in error or "target pairs" in error for error in errors)


def test_center8_source_crosswalk_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_center8_source_crosswalk.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["target_row_key"] == "151:6"
    assert payload["conditional_center8_triple"] == [0, 4, 6]
    assert payload["source151_named_center8_target_row_key"] == "151:8"
    assert payload["source151_named_center8_max_target_triple_overlap"] == 1
    assert payload["source151_named_center8_candidate_rows_with_target_pair_count"] == 0
    assert (
        payload["source151_named_center8_candidate_rows_with_full_target_triple_count"]
        == 0
    )
    assert payload["gate_status"] == GATE_STATUS
