from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_center8_migration_preflight import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
    DEFAULT_SOURCE_CENTER8_PREFLIGHT,
    DEFAULT_SOURCE_CENTER8_SOURCE_CROSSWALK,
    DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    GATE_STATUS,
    assert_expected_center8_migration_preflight,
    build_center8_migration_preflight_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_residual_target_rows() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS)


@pytest.fixture(scope="module")
def source_center8_preflight() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_CENTER8_PREFLIGHT)


@pytest.fixture(scope="module")
def source_center8_source_crosswalk() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_CENTER8_SOURCE_CROSSWALK)


@pytest.fixture(scope="module")
def source_cascade_endpoint8_targets() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS)


def test_center8_migration_preflight_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_center8_migration_preflight(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_MIGRATION_PREFLIGHT_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "off-center strict-core rows at centers 2, 5, or 7",
        "does not prove center migration",
        "does not prove support existence",
        "does not prove row forcing",
        "does not prove endpoint-8 forcing",
        "does not prove that assignments 0 and 11 are impossible",
        "does not prove that pair [3,5] is impossible",
        "does not prove n=9",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_center8_migration_preflight_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["conditional_center8_triple"] == [0, 4, 6]
    assert summary["source_residual_gate_status"] == (
        "NOT_READY_RESIDUAL_TARGET_ROWS_DO_NOT_FORCE_CENTER8"
    )
    assert summary["source_center8_preflight_gate_status"] == (
        "NOT_READY_NO_CENTER8_RICH_TRIPLE_SOURCE"
    )
    assert summary["source_center8_source_crosswalk_gate_status"] == (
        "NOT_READY_EXISTING_SOURCE151_CENTER8_SINGLETON_DOES_NOT_SUPPLY_CASCADE_TRIPLE"
    )
    assert summary["off_center_residual_assignment_count"] == 4
    assert summary["off_center_residual_assignment_indices"] == [5, 7, 9, 10]
    assert summary["target_sparse_assignment_indices"] == [0, 11]
    assert summary["migration_candidate_count"] == 5
    assert summary["migration_candidate_distinct_exact_row_count"] == 3
    assert summary["migration_candidate_source_centers"] == [2, 5, 7]
    assert summary["migration_candidate_source_center_counts"] == {
        "2": 2,
        "5": 1,
        "7": 2,
    }
    assert summary["migration_candidate_exact_row_counts"] == {
        "0,1,4,6": 1,
        "0,2,4,6": 2,
        "0,3,4,6": 2,
    }
    assert summary["migration_candidate_center8_exact_rows"] == [
        [0, 1, 4, 6],
        [0, 2, 4, 6],
        [0, 3, 4, 6],
    ]
    assert summary["endpoint_exact_rows_not_seen_off_center"] == [
        [0, 4, 5, 6],
        [0, 4, 6, 7],
    ]
    assert summary["support_requirement_center8_count"] == 0
    assert summary["source151_named_center8_max_target_triple_overlap"] == 1
    assert summary["source151_named_center8_candidate_rows_with_target_pair_count"] == 0
    assert summary["current_evidence_proves_center_migration"] is False
    assert summary["off_center_rows_migrate_to_center8_under_current_evidence"] is False
    assert summary["gate_status"] == GATE_STATUS


def test_center8_migration_preflight_records() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = payload["migration_candidate_records"]

    assert [record["assignment_index"] for record in records] == [5, 7, 9, 9, 10]
    assert [record["source_row_center"] for record in records] == [5, 7, 2, 2, 7]
    assert [record["candidate_center8_row_center"] for record in records] == [8] * 5
    assert all(record["candidate_center8_exact_row_allowed"] is True for record in records)
    assert all(record["candidate_center8_obstructed_if_forced"] is True for record in records)
    assert all(record["current_evidence_migrates_this_row"] is False for record in records)
    assert all({0, 4, 6} <= set(record["source_row_witnesses"]) for record in records)

    assignments = {
        record["assignment_index"]: record
        for record in payload["assignment_migration_records"]
    }
    assert assignments[5]["migration_candidate_exact_rows"] == [[0, 2, 4, 6]]
    assert assignments[9]["off_center_target_row_count"] == 2
    assert assignments[9]["migration_candidate_source_centers"] == [2]
    assert assignments[10]["required_migration_target"] == {
        "candidate_exact_rows": [[0, 2, 4, 6]],
        "center": 8,
        "witness_triple": [0, 4, 6],
    }

    sparse = payload["target_sparse_assignment_records"]
    assert [record["assignment_index"] for record in sparse] == [0, 11]
    assert all(record["current_evidence_migrates_assignment"] is False for record in sparse)


def test_center8_migration_preflight_artifact_matches_generator(
    source_residual_target_rows: dict[str, object],
    source_center8_preflight: dict[str, object],
    source_center8_source_crosswalk: dict[str, object],
    source_cascade_endpoint8_targets: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_center8_migration_preflight_payload(
        source_residual_target_rows,
        source_center8_preflight,
        source_center8_source_crosswalk,
        source_cascade_endpoint8_targets,
    )


def test_center8_migration_preflight_rejects_migration_overclaim() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["current_evidence_proves_center_migration"] = True
    bad["decision"]["current_evidence_proves_center_migration"] = True
    bad["migration_candidate_records"][0]["current_evidence_migrates_this_row"] = True

    errors = validate_payload(bad, recompute=False)

    assert any("current_evidence_proves_center_migration" in error for error in errors)
    assert any("current_evidence_migrates_this_row" in error for error in errors)


def test_center8_migration_preflight_rejects_tampered_source_center() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["migration_candidate_source_centers"] = [5, 7]
    bad["migration_candidate_records"][0]["source_row_center"] = 8

    errors = validate_payload(bad, recompute=False)

    assert any("migration_candidate_source_centers" in error for error in errors)
    assert any("must start off-center" in error for error in errors)


def test_center8_migration_preflight_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_center8_migration_preflight.py",
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
    assert payload["off_center_residual_assignment_indices"] == [5, 7, 9, 10]
    assert payload["target_sparse_assignment_indices"] == [0, 11]
    assert payload["migration_candidate_count"] == 5
    assert payload["migration_candidate_source_centers"] == [2, 5, 7]
    assert payload["current_evidence_proves_center_migration"] is False
    assert payload["gate_status"] == GATE_STATUS
