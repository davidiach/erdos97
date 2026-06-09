from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label8_free_residual_targets import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_STRICT_CORE_SPLIT,
    TARGET_STATUS,
    assert_expected_label8_free_residual_targets,
    build_label8_free_residual_targets_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_strict_core_split() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_STRICT_CORE_SPLIT)


def test_label8_free_residual_targets_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_label8_free_residual_targets(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_151_6_LABEL8_FREE_RESIDUAL_TARGETS_DIAGNOSTIC_ONLY"
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


def test_label8_free_residual_targets_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["label8_free_distinct_exact_signature_count"] == 10
    assert summary["label8_free_occurrence_count"] == 12
    assert summary["signatures_with_any_label4_auxiliary_row"] == 10
    assert summary["signatures_with_all_auxiliary_rows_label4"] == 8
    assert summary["occurrences_with_all_auxiliary_rows_label4"] == 10
    assert summary["label4_auxiliary_row_signature_incidence_count"] == 18
    assert summary["label4_auxiliary_row_occurrence_count"] == 22
    assert summary["signatures_with_label4_free_strict_cycle_edges"] == 2
    assert summary["occurrences_with_label4_free_strict_cycle_edges"] == 2
    assert summary["signatures_with_center8_as_auxiliary_center"] == 3
    assert summary["occurrences_with_center8_as_auxiliary_center"] == 4
    assert summary["target_status"] == TARGET_STATUS


def test_label8_free_residual_target_records_are_consistent() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = payload["residual_signature_records"]

    assert len(records) == 10
    total_multiplicity = 0
    all_label4_count = 0
    label4_free_cycle_edge_count = 0
    center8_count = 0
    for index, record in enumerate(records):
        assert record["signature_index"] == index
        total_multiplicity += record["multiplicity"]
        assert len(record["centers"]) == 3
        assert 6 in record["centers"]
        assert all(8 not in row["witnesses"] for row in record["rows"])
        assert record["label4_in_any_auxiliary_row"] is True
        assert record["strict_edge_count"] == 27
        assert record["cycle_edge_count"] == len(record["cycle_edges"])
        assert record["cycle_edge_count"] > 0
        if record["label4_in_all_auxiliary_rows"]:
            all_label4_count += 1
        if record["label4_free_strict_cycle_edges"]:
            label4_free_cycle_edge_count += 1
            assert record["label4_touching_cycle_edge_count"] == 0
        if record["center8_as_auxiliary_center"]:
            center8_count += 1

    assert total_multiplicity == 12
    assert all_label4_count == 8
    assert label4_free_cycle_edge_count == 2
    assert center8_count == 3


def test_label8_free_residual_targets_artifact_matches_generator(
    source_strict_core_split: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_label8_free_residual_targets_payload(
        source_strict_core_split,
    )


def test_label8_free_residual_targets_rejects_tampered_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["summary"]["signatures_with_any_label4_auxiliary_row"] = 9

    errors = validate_payload(payload, recompute=False)

    assert any("signatures_with_any_label4_auxiliary_row" in error for error in errors)


def test_label8_free_residual_targets_rejects_label8_witness() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["residual_signature_records"][0]["rows"][0]["witnesses"][0] = 8

    errors = validate_payload(payload, recompute=False)

    assert any("contains witness label 8" in error for error in errors)


def test_label8_free_residual_targets_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label8_free_residual_targets.py",
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
    assert payload["label8_free_distinct_exact_signature_count"] == 10
    assert payload["label8_free_occurrence_count"] == 12
    assert payload["signatures_with_any_label4_auxiliary_row"] == 10
