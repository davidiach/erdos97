from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_transfer_obligations import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_TRANSFER_PATHS,
    OBLIGATION_STATUS,
    assert_expected_label4_transfer_obligations,
    build_label4_transfer_obligations_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_transfer_paths() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_TRANSFER_PATHS)


def test_label4_transfer_obligations_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_label4_transfer_obligations(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_151_6_LABEL4_TRANSFER_OBLIGATIONS_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "does not prove outside-pair support existence",
        "does not prove row forcing",
        "does not prove pair [3,5] impossible",
        "does not prove endpoint-8 forcing",
        "does not prove n=9",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_label4_transfer_obligations_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["source_label4_transfer_path_class_signature_incidence_count"] == 19
    assert summary["source_positive_transfer_class_signature_incidence_count"] == 8
    assert summary["source_positive_transfer_class_occurrence_incidence_count"] == 9
    assert summary["row_local_transfer_obligation_record_count"] == 8
    assert summary["row_local_transfer_obligation_occurrence_count"] == 9
    assert summary["row_local_transfer_edge_signature_count"] == 11
    assert summary["row_local_transfer_edge_occurrence_count"] == 13
    assert summary["unique_path_motif_count"] == 6
    assert summary["unique_edge_obligation_count"] == 7
    assert summary["label4_spoke_swap_edge_signature_count"] == 8
    assert summary["label4_spoke_swap_edge_occurrence_count"] == 9
    assert summary["target_center_touching_edge_signature_count"] == 6
    assert summary["target_center_touching_edge_occurrence_count"] == 8
    assert summary["row6_connector_step_signature_count"] == 3
    assert summary["row6_connector_step_occurrence_count"] == 4
    assert summary["path_shape_signature_counts"] == {
        "one_edge_row5_label4_spoke_swap": 3,
        "one_edge_row7_label4_spoke_swap": 2,
        "two_edge_row5_row6_connector_cascade": 3,
    }
    assert summary["obligation_status"] == OBLIGATION_STATUS


def test_label4_transfer_obligation_records_are_consistent() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = payload["transfer_obligation_records"]
    edge_records = payload["unique_edge_obligation_records"]
    motif_records = payload["path_motif_records"]

    assert len(records) == 8
    assert len(edge_records) == 7
    assert len(motif_records) == 6
    assert {
        record["path_shape"] for record in motif_records
    } == {
        "one_edge_row5_label4_spoke_swap",
        "one_edge_row7_label4_spoke_swap",
        "two_edge_row5_row6_connector_cascade",
    }

    all_rows: set[int] = set()
    row6_steps = 0
    for record in records:
        assert record["transfer_edge_count"] == len(record["row_obligations"])
        assert record["row_obligations"]
        if record["access_mode"] == "quotient_equality_only":
            assert record["transfer_edge_count"] == 1
            assert record["row_obligations"][0]["row"] == 5
        for obligation in record["row_obligations"]:
            all_rows.add(obligation["row"])
            if obligation["row"] in {5, 7}:
                assert obligation["label4_spoke_swap"] is True
            if obligation["row"] == 6:
                row6_steps += 1
                assert obligation["row6_connector_step"] is True
                assert obligation["obligation_key"] == "row6:[5,6]=[0,6]"

    assert all_rows == {5, 6, 7}
    assert row6_steps == 3


def test_label4_transfer_obligations_artifact_matches_generator(
    source_transfer_paths: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_label4_transfer_obligations_payload(
        source_transfer_paths,
    )


def test_label4_transfer_obligations_rejects_tampered_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["summary"]["unique_edge_obligation_count"] = 6

    errors = validate_payload(payload, recompute=False)

    assert any("unique_edge_obligation_count" in error for error in errors)


def test_label4_transfer_obligations_rejects_broken_path_shape() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["transfer_obligation_records"][0]["path_shape"] = "wrong_shape"

    errors = validate_payload(payload, recompute=False)

    assert any("path shape mismatch" in error for error in errors)


def test_label4_transfer_obligations_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_transfer_obligations.py",
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
    assert payload["row_local_transfer_obligation_record_count"] == 8
    assert payload["unique_edge_obligation_count"] == 7
    assert payload["unique_path_motif_count"] == 6
    assert payload["row6_connector_step_signature_count"] == 3
