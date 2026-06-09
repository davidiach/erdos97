from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_support_hypothesis_ledger import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_COMPONENTS,
    DEFAULT_SOURCE_FEASIBILITY,
    DEFAULT_SOURCE_OBLIGATIONS,
    LEDGER_STATUS,
    assert_expected_support_hypothesis_ledger,
    build_support_hypothesis_ledger_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_components() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_COMPONENTS)


@pytest.fixture(scope="module")
def source_obligations() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_OBLIGATIONS)


@pytest.fixture(scope="module")
def source_feasibility() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_FEASIBILITY)


def test_label4_support_hypothesis_ledger_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_support_hypothesis_ledger(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_151_6_LABEL4_SUPPORT_HYPOTHESIS_LEDGER_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "does not discharge those support hypotheses",
        "does not prove outside-pair support existence",
        "does not prove row forcing",
        "does not prove pair [3,5] impossible",
        "does not prove endpoint-8 forcing",
        "does not prove n=9",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_label4_support_hypothesis_ledger_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["source_length_component_count"] == 6
    assert summary["source_feasible_component_count"] == 6
    assert summary["support_need_record_count"] == 6
    assert summary["unique_centered_support_requirement_count"] == 7
    assert summary["component_count_by_required_support_center_count"] == {
        "1": 5,
        "2": 1,
    }
    assert summary["component_incidence_count_by_required_center"] == {
        "5": 4,
        "6": 1,
        "7": 2,
    }
    assert summary["unique_support_requirement_count_by_role"] == {
        "row5_label4_spoke_swap": 3,
        "row5_label4_to_target_center_step": 1,
        "row6_target_connector_step": 1,
        "row7_label4_spoke_swap": 2,
    }
    assert summary["components_requiring_row6_target_connector_count"] == 1
    assert summary["components_requiring_exact_private_support_pair_count"] == 0
    assert summary["unique_requirements_with_exact_private_support_pair_count"] == 0
    assert summary["components_requiring_label4_witness_count"] == 6
    assert summary["components_requiring_label8_witness_count"] == 0
    assert summary["component_count_by_access_mode"] == {
        "direct_cycle_edge": 4,
        "quotient_equality_only": 2,
    }
    assert summary["positive_transfer_signature_count_by_access_mode"] == {
        "direct_cycle_edge": 6,
        "quotient_equality_only": 2,
    }
    assert summary["cascade_component_key"] == "D[0,6]=D[4,5]=D[5,6]"
    assert summary["cascade_required_support_centers"] == [5, 6]
    assert summary["cascade_required_witness_pairs"] == [[4, 6], [0, 5]]
    assert summary["cascade_auxiliary_center_pair_occurrence_counts"] == {"5,8": 4}
    assert summary["ledger_status"] == LEDGER_STATUS


def test_label4_support_hypothesis_ledger_records() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    support_needs = payload["support_need_records"]
    requirements = payload["support_requirement_records"]

    assert len(support_needs) == 6
    assert len(requirements) == 7
    assert {
        record["component_key"]
        for record in support_needs
        if record["requires_row6_target_connector"]
    } == {"D[0,6]=D[4,5]=D[5,6]"}
    assert not any(
        record["requires_exact_private_support_pair"] for record in support_needs
    )
    assert not any(
        record["witness_pair_equals_private_support_pair"]
        for record in requirements
    )

    cascade = next(
        record
        for record in support_needs
        if record["component_key"] == "D[0,6]=D[4,5]=D[5,6]"
    )
    assert cascade["required_support_centers"] == [5, 6]
    assert cascade["required_witness_pairs"] == [[4, 6], [0, 5]]
    assert cascade["requires_private_target_class_witness_subset"] is True
    assert cascade["requires_target_center_as_auxiliary_witness"] is True
    assert cascade["requires_label8_witness"] is False
    assert cascade["component_alone_witness_modulus"] == 13
    assert cascade["auxiliary_center_pair_signature_counts"] == {"5,8": 3}


def test_label4_support_hypothesis_ledger_artifact_matches_generator(
    source_components: dict[str, object],
    source_obligations: dict[str, object],
    source_feasibility: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_support_hypothesis_ledger_payload(
        source_components,
        source_obligations,
        source_feasibility,
    )


def test_label4_support_hypothesis_ledger_rejects_private_pair_claim() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["summary"]["components_requiring_exact_private_support_pair_count"] = 1

    errors = validate_payload(payload, recompute=False)

    assert any("exact_private_support_pair" in error for error in errors)


def test_label4_support_hypothesis_ledger_rejects_tampered_requirement() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["support_requirement_records"][0][
        "witness_pair_equals_private_support_pair"
    ] = True

    errors = validate_payload(payload, recompute=False)

    assert any("private pair" in error or "[3,5]" in error for error in errors)


def test_label4_support_hypothesis_ledger_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_support_hypothesis_ledger.py",
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
    assert payload["support_need_record_count"] == 6
    assert payload["unique_centered_support_requirement_count"] == 7
    assert payload["components_requiring_row6_target_connector_count"] == 1
    assert payload["components_requiring_exact_private_support_pair_count"] == 0
    assert payload["cascade_component_key"] == "D[0,6]=D[4,5]=D[5,6]"
