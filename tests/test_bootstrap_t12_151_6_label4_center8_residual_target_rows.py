from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_center8_residual_target_rows import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_CENTER8_CORE_ROUTE,
    DEFAULT_SOURCE_STRICT_CORE_SPLIT,
    GATE_STATUS,
    assert_expected_center8_residual_target_rows,
    build_center8_residual_target_rows_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_strict_core_split() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_STRICT_CORE_SPLIT)


@pytest.fixture(scope="module")
def source_center8_core_route() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_CENTER8_CORE_ROUTE)


def test_center8_residual_target_rows_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_center8_residual_target_rows(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_RESIDUAL_TARGET_ROWS_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "off-center row with witnesses [0,4,6]",
        "assignments 0 and 11",
        "does not prove center migration",
        "does not prove support existence",
        "does not prove row forcing",
        "does not prove endpoint-8 forcing",
        "does not prove that pair [3,5] is impossible",
        "does not prove n=9",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_center8_residual_target_rows_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["conditional_center8_target_center"] == 8
    assert summary["conditional_center8_triple"] == [0, 4, 6]
    assert summary["source_private_lane_assignment_count"] == 12
    assert summary["source_center8_target_assignment_count"] == 6
    assert summary["residual_assignment_count"] == 6
    assert summary["residual_assignment_indices"] == [0, 5, 7, 9, 10, 11]
    assert summary["residual_core_count"] == 19
    assert summary["residual_label8_visible_core_count"] == 15
    assert summary["residual_label8_free_core_count"] == 4
    assert summary["residual_center8_core_count"] == 1
    assert summary["residual_center8_target_core_count"] == 0
    assert summary["residual_assignments_with_off_center_target_row"] == 4
    assert summary["residual_assignments_with_off_center_target_row_indices"] == [
        5,
        7,
        9,
        10,
    ]
    assert summary["residual_assignments_without_any_target_row"] == 2
    assert summary["target_sparse_assignment_indices"] == [0, 11]
    assert summary["off_center_target_row_occurrence_count"] == 5
    assert summary["off_center_target_core_count"] == 5
    assert summary["off_center_target_label8_visible_core_count"] == 1
    assert summary["off_center_target_label8_free_core_count"] == 4
    assert summary["off_center_target_row_center_counts"] == {"2": 2, "5": 1, "7": 2}
    assert summary["off_center_target_exact_row_counts"] == {
        "0,1,4,6": 1,
        "0,2,4,6": 2,
        "0,3,4,6": 2,
    }
    assert summary["off_center_target_auxiliary_center_pair_counts"] == {
        "2,5": 1,
        "2,7": 2,
        "3,5": 1,
        "3,7": 1,
    }
    assert summary["target_sparse_max_target_overlap"] == 2
    assert summary["target_sparse_pair_row_occurrence_count"] == 6
    assert summary["target_sparse_pair_overlap_counts"] == {
        "0,4": 2,
        "0,6": 3,
        "4,6": 1,
    }
    assert summary["current_evidence_forces_center8_target_core"] is False
    assert summary["off_center_target_rows_supply_center8_target"] is False
    assert summary["gate_status"] == GATE_STATUS


def test_center8_residual_target_rows_records() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    off_center = payload["off_center_target_row_records"]

    assert [record["assignment_index"] for record in off_center] == [5, 7, 9, 9, 10]
    assert [record["row_center"] for record in off_center] == [5, 7, 2, 2, 7]
    assert all(record["row_center_equals_endpoint_center"] is False for record in off_center)
    assert all(record["exact_endpoint_row_allowed"] is True for record in off_center)
    assert sum(1 for record in off_center if record["label8_visible"]) == 1
    assert all({0, 4, 6} <= set(record["row_witnesses"]) for record in off_center)

    assignments = {
        record["assignment_index"]: record
        for record in payload["assignment_residual_records"]
    }
    assert assignments[0]["residual_class"] == "target_sparse"
    assert assignments[0]["target_pair_row_count"] == 1
    assert assignments[5]["off_center_target_rows"] == [
        {
            "core_index": 0,
            "label8_visible": False,
            "row_center": 5,
            "row_witnesses": [0, 2, 4, 6],
        }
    ]
    assert assignments[9]["off_center_target_core_indices"] == [1, 2]
    assert assignments[11]["center8_rows"] == [[1, 2, 5, 7]]
    assert assignments[11]["target_pair_row_count"] == 5


def test_center8_residual_target_rows_artifact_matches_generator(
    source_strict_core_split: dict[str, object],
    source_center8_core_route: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_center8_residual_target_rows_payload(
        source_strict_core_split,
        source_center8_core_route,
    )


def test_center8_residual_target_rows_rejects_center8_supply_overclaim() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["off_center_target_rows_supply_center8_target"] = True
    bad["decision"]["off_center_target_rows_supply_center8_target"] = True

    errors = validate_payload(bad, recompute=False)

    assert any("off_center_target_rows_supply_center8_target" in error for error in errors)


def test_center8_residual_target_rows_rejects_tampered_sparse_indices() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["target_sparse_assignment_indices"] = [0]
    bad["target_sparse_assignment_records"] = bad["target_sparse_assignment_records"][:1]

    errors = validate_payload(bad, recompute=False)

    assert any("target_sparse" in error for error in errors)


def test_center8_residual_target_rows_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_center8_residual_target_rows.py",
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
    assert payload["residual_assignment_count"] == 6
    assert payload["residual_assignment_indices"] == [0, 5, 7, 9, 10, 11]
    assert payload["off_center_target_row_occurrence_count"] == 5
    assert payload["target_sparse_assignment_indices"] == [0, 11]
    assert payload["gate_status"] == GATE_STATUS
