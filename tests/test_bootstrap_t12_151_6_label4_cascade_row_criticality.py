from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_cascade_row_criticality import (
    CRITICALITY_STATUS,
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_RESIDUAL_TARGETS,
    DEFAULT_SOURCE_SUPPORT_LEDGER,
    REQUIRED_CORE_CENTERS,
    assert_expected_cascade_row_criticality,
    build_cascade_row_criticality_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_residual_targets() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_RESIDUAL_TARGETS)


@pytest.fixture(scope="module")
def source_support_ledger() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_SUPPORT_LEDGER)


def test_label4_cascade_row_criticality_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_cascade_row_criticality(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_151_6_LABEL4_CASCADE_ROW_CRITICALITY_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "Every nonempty proper row truncation is quotient-clean",
        "does not prove support existence",
        "does not prove row forcing",
        "does not prove pair [3,5] impossible",
        "does not prove endpoint-8 forcing",
        "does not prove n=9",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_label4_cascade_row_criticality_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["cascade_component_key"] == "D[0,6]=D[4,5]=D[5,6]"
    assert summary["cascade_auxiliary_center_pair"] == "5,8"
    assert summary["cascade_required_support_centers"] == [5, 6]
    assert summary["cascade_required_witness_pairs"] == [[4, 6], [0, 5]]
    assert summary["required_core_centers"] == REQUIRED_CORE_CENTERS
    assert summary["cascade_signature_indices"] == [7, 8, 9]
    assert summary["cascade_signature_count"] == 3
    assert summary["cascade_occurrence_count"] == 4
    assert summary["cascade_full_core_status_counts"] == {"strict_cycle": 3}
    assert summary["cascade_full_core_occurrence_status_counts"] == {
        "strict_cycle": 4
    }
    assert summary["cascade_full_core_cycle_length_signature_counts"] == {
        "2": 1,
        "3": 2,
    }
    assert summary["proper_truncation_record_count"] == 18
    assert summary["proper_truncation_occurrence_count"] == 24
    assert summary["proper_truncation_status_counts"] == {"ok": 18}
    assert summary["row_subset_status_counts_by_size"] == {
        "1": {"ok": 9},
        "2": {"ok": 9},
        "3": {"strict_cycle": 3},
    }
    assert summary["clean_deletion_signature_counts_by_deleted_center"] == {
        "5": 3,
        "6": 3,
        "8": 3,
    }
    assert summary["full_core_cycle_edge_row_pair_signature_counts"] == {"5,8": 3}
    assert summary["criticality_status"] == CRITICALITY_STATUS


def test_label4_cascade_row_criticality_records() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = payload["cascade_signature_records"]

    assert [record["signature_index"] for record in records] == [7, 8, 9]
    assert [record["multiplicity"] for record in records] == [1, 1, 2]
    for record in records:
        assert record["auxiliary_center_pair"] == "5,8"
        assert record["full_core_centers"] == [5, 6, 8]
        assert record["full_core_status"] == "strict_cycle"
        assert record["full_core_strict_edge_count"] == 27
        assert record["full_core_cycle_edge_rows"] == [5, 8]
        assert record["all_proper_truncations_clean"] is True
        assert [
            item["centers"] for item in record["proper_truncation_records"]
        ] == [[5], [6], [8], [5, 6], [5, 8], [6, 8]]
        assert {
            item["status"] for item in record["proper_truncation_records"]
        } == {"ok"}
        assert not any(
            item["obstructed"] for item in record["proper_truncation_records"]
        )


def test_label4_cascade_row_criticality_artifact_matches_generator(
    source_residual_targets: dict[str, object],
    source_support_ledger: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_cascade_row_criticality_payload(
        source_residual_targets,
        source_support_ledger,
    )


def test_label4_cascade_row_criticality_rejects_obstructed_truncation() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["cascade_signature_records"][0]["proper_truncation_records"][0][
        "status"
    ] = "strict_cycle"

    errors = validate_payload(payload, recompute=False)

    assert any("truncation" in error for error in errors)


def test_label4_cascade_row_criticality_rejects_missing_row8_target() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["cascade_signature_records"][0]["full_core_cycle_edge_rows"] = [5]

    errors = validate_payload(payload, recompute=False)

    assert any("cycle rows mismatch" in error for error in errors)


def test_label4_cascade_row_criticality_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_cascade_row_criticality.py",
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
    assert payload["cascade_signature_count"] == 3
    assert payload["cascade_occurrence_count"] == 4
    assert payload["required_core_centers"] == [5, 6, 8]
    assert payload["proper_truncation_status_counts"] == {"ok": 18}
