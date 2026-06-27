from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_center8_migration_support_crosswalk import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    DEFAULT_SOURCE_SUPPORT_LEDGER,
    MIGRATION_STATUS,
    assert_expected_center8_migration_support_crosswalk,
    build_center8_migration_support_crosswalk_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_residual_target_rows() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS)


@pytest.fixture(scope="module")
def source_support_ledger() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_SUPPORT_LEDGER)


def test_center8_migration_support_crosswalk_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_center8_migration_support_crosswalk(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_MIGRATION_SUPPORT_CROSSWALK_"
        "DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "does not prove center migration",
        "does not prove support existence",
        "does not prove row forcing",
        "does not prove endpoint-8 forcing",
        "does not prove assignments 0 and 11 impossible",
        "does not prove that pair [3,5] is impossible",
        "does not prove n=9",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_center8_migration_support_crosswalk_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["conditional_center8_target_center"] == 8
    assert summary["conditional_center8_triple"] == [0, 4, 6]
    assert summary["residual_assignment_indices"] == [0, 5, 7, 9, 10, 11]
    assert summary["off_center_target_row_occurrence_count"] == 5
    assert summary["off_center_target_assignment_indices"] == [5, 7, 9, 10]
    assert summary["target_sparse_assignment_indices"] == [0, 11]
    assert summary["support_requirement_centers"] == [5, 6, 7]
    assert summary["support_requirement_center8_count"] == 0
    assert summary["off_center_row_centers"] == [2, 5, 7]
    assert summary["off_center_rows_at_unsupported_center_count"] == 2
    assert summary["off_center_assignments_at_unsupported_center_indices"] == [9]
    assert summary["off_center_rows_with_same_center_support_count"] == 3
    assert summary["off_center_assignments_with_same_center_support_indices"] == [
        5,
        7,
        10,
    ]
    assert summary["same_center_support_requirement_match_count"] == 5
    assert summary["same_center_support_match_count_by_row_center"] == {
        "5": 3,
        "7": 2,
    }
    assert summary["same_center_support_endpoint_triple_pairs"] == [[0, 4], [4, 6]]
    assert summary["endpoint_triple_pairs_missing_from_same_center_support"] == [
        [0, 6]
    ]
    assert summary["off_center_rows_with_cascade_row5_support_count"] == 1
    assert summary["cascade_row5_support_assignment_indices"] == [5]
    assert summary["off_center_rows_with_row6_cascade_support_count"] == 0
    assert summary["cascade_row6_support_assignment_indices"] == []
    assert summary["support_backing_supplies_center8_target"] is False
    assert summary["current_evidence_proves_center_migration"] is False
    assert summary["current_evidence_obstructs_target_sparse_assignments"] is False
    assert summary["migration_status"] == MIGRATION_STATUS


def test_center8_migration_support_crosswalk_records() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = payload["off_center_alignment_records"]

    by_assignment = {
        (record["assignment_index"], record["core_index"]): record
        for record in records
    }
    assignment5 = by_assignment[(5, 0)]
    assert assignment5["row_center"] == 5
    assert assignment5["same_center_support_requirement_keys"] == [
        "row5:[4,5]=[0,5]",
        "row5:[4,5]=[2,5]",
        "row5:[4,5]=[5,6]",
    ]
    assert assignment5["same_center_support_witness_pairs"] == [
        [0, 4],
        [2, 4],
        [4, 6],
    ]
    assert assignment5["has_cascade_row5_support"] is True
    assert assignment5["has_row6_cascade_support"] is False

    assignment7 = by_assignment[(7, 1)]
    assert assignment7["same_center_support_requirement_keys"] == [
        "row7:[4,7]=[1,7]"
    ]
    assignment10 = by_assignment[(10, 3)]
    assert assignment10["same_center_support_requirement_keys"] == [
        "row7:[4,7]=[2,7]"
    ]
    assignment9 = [
        record
        for record in records
        if record["assignment_index"] == 9
    ]
    assert len(assignment9) == 2
    assert all(not record["has_same_center_support"] for record in assignment9)
    assert all(
        record["same_center_support_supplies_center8_target"] is False
        for record in records
    )

    sparse = payload["target_sparse_gap_records"]
    assert [record["assignment_index"] for record in sparse] == [0, 11]
    assert all(record["requires_separate_obstruction"] is True for record in sparse)


def test_center8_migration_support_crosswalk_artifact_matches_generator(
    source_residual_target_rows: dict[str, object],
    source_support_ledger: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_center8_migration_support_crosswalk_payload(
        source_residual_target_rows,
        source_support_ledger,
    )


def test_center8_migration_support_crosswalk_rejects_migration_overclaim() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["support_backing_supplies_center8_target"] = True
    bad["decision"]["support_backing_supplies_center8_target"] = True

    errors = validate_payload(bad, recompute=False)

    assert any("support_backing_supplies_center8_target" in error for error in errors)


def test_center8_migration_support_crosswalk_rejects_row6_cascade_promotion() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["off_center_alignment_records"][0]["has_row6_cascade_support"] = True

    errors = validate_payload(bad, recompute=False)

    assert any("row-6 cascade support" in error for error in errors)


def test_center8_migration_support_crosswalk_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/"
            "check_bootstrap_t12_151_6_label4_center8_migration_support_crosswalk.py",
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
    assert payload["off_center_target_row_occurrence_count"] == 5
    assert payload["off_center_rows_with_same_center_support_count"] == 3
    assert payload["off_center_rows_with_cascade_row5_support_count"] == 1
    assert payload["support_requirement_center8_count"] == 0
    assert payload["target_sparse_assignment_indices"] == [0, 11]
    assert payload["migration_status"] == MIGRATION_STATUS
