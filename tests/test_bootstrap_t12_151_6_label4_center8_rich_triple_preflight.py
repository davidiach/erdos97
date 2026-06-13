from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_center8_rich_triple_preflight import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
    DEFAULT_SOURCE_ENDPOINT8_FORCING_PREFLIGHT,
    DEFAULT_SOURCE_SUPPORT_LEDGER,
    GATE_STATUS,
    assert_expected_center8_rich_triple_preflight,
    build_center8_rich_triple_preflight_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_support_ledger() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_SUPPORT_LEDGER)


@pytest.fixture(scope="module")
def source_cascade_endpoint8_targets() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS)


@pytest.fixture(scope="module")
def source_endpoint8_forcing_preflight() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_ENDPOINT8_FORCING_PREFLIGHT)


def test_center8_rich_triple_preflight_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_center8_rich_triple_preflight(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_RICH_TRIPLE_PREFLIGHT_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "current checked evidence already supplies the new center-8 rich-class target [0,4,6]",
        "not forced by the current support ledger",
        "no centered support requirement at center 8",
        "does not prove support existence",
        "does not prove row forcing",
        "does not prove endpoint-8 forcing",
        "does not prove that pair [3,5] is impossible",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_center8_rich_triple_preflight_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_support_pair"] == [3, 5]
    assert summary["cascade_component_key"] == "D[0,6]=D[4,5]=D[5,6]"
    assert summary["cascade_required_support_centers"] == [5, 6]
    assert summary["cascade_required_witness_pairs"] == [[4, 6], [0, 5]]
    assert summary["required_core_centers"] == [5, 6, 8]
    assert summary["conditional_center8_target_center"] == 8
    assert summary["conditional_center8_triple"] == [0, 4, 6]
    assert summary["conditional_target_status"] == (
        "ENDPOINT8_RICH_TRIPLE_SUFFICES_CONDITIONALLY"
    )
    assert summary["conditional_rich_superset_signature_record_count"] == 93
    assert summary["conditional_rich_superset_obstructed_count"] == 93
    assert summary["support_requirement_centers"] == [5, 6, 7]
    assert summary["support_requirement_center8_count"] == 0
    assert summary["support_requirements_with_label8_witness_count"] == 0
    assert summary["center8_requirement_with_full_triple_count"] == 0
    assert summary["endpoint_triple_pair_requirements_any_center"] == [
        [0, 4],
        [4, 6],
    ]
    assert summary["endpoint_triple_pair_requirements_at_center8"] == []
    assert summary["endpoint_triple_pair_requirements_missing_any_center"] == [[0, 6]]
    assert summary["components_with_center8_auxiliary_center_count"] == 1
    assert summary["center8_auxiliary_pair_is_not_center8_support_requirement"] is True
    assert summary["outside_pair_endpoint8_preflight_target_center"] == 6
    assert summary["outside_pair_endpoint8_support_pairs"] == [[3, 8], [5, 8]]
    assert summary["current_evidence_forces_center8_rich_triple"] is False
    assert summary["gate_status"] == GATE_STATUS


def test_center8_rich_triple_preflight_records() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    support_audit = payload["support_requirement_audit"]
    distinction = payload["endpoint8_distinction_records"]

    assert len(support_audit) == 4
    assert support_audit[0]["answer"] is False
    assert support_audit[0]["matching_requirement_count"] == 0
    assert support_audit[2]["answer"] == "partial_pair_coverage_only"
    assert support_audit[2]["covered_pairs_any_center"] == [[0, 4], [4, 6]]
    assert support_audit[2]["covered_pairs_at_center8"] == []
    assert support_audit[2]["missing_pairs_any_center"] == [[0, 6]]
    assert [record["target_name"] for record in distinction] == [
        "endpoint-8 outside-pair support",
        "center-8 rich-triple row target",
    ]
    assert distinction[0]["row_center"] == 6
    assert distinction[1]["row_center"] == 8
    assert all(record["forced_by_current_evidence"] is False for record in distinction)


def test_center8_rich_triple_preflight_artifact_matches_generator(
    source_support_ledger: dict[str, object],
    source_cascade_endpoint8_targets: dict[str, object],
    source_endpoint8_forcing_preflight: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_center8_rich_triple_preflight_payload(
        source_support_ledger,
        source_cascade_endpoint8_targets,
        source_endpoint8_forcing_preflight,
    )


def test_center8_rich_triple_preflight_rejects_forcing_overclaim() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["summary"]["current_evidence_forces_center8_rich_triple"] = True
    payload["decision"]["current_evidence_forces_center8_rich_triple"] = True

    errors = validate_payload(payload, recompute=False)

    assert any("current_evidence_forces_center8_rich_triple" in error for error in errors)


def test_center8_rich_triple_preflight_rejects_tampered_center8_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["summary"]["support_requirement_center8_count"] = 1

    errors = validate_payload(payload, recompute=False)

    assert any("support_requirement_center8_count" in error for error in errors)


def test_center8_rich_triple_preflight_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_center8_rich_triple_preflight.py",
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
    assert payload["conditional_center8_target_center"] == 8
    assert payload["conditional_center8_triple"] == [0, 4, 6]
    assert payload["support_requirement_center8_count"] == 0
    assert payload["gate_status"] == GATE_STATUS
