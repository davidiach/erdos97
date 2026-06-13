from __future__ import annotations

from collections import Counter
import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_center8_target_sparse_two_row_repairs import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_COMPLETIONS,
    DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    GATE_STATUS,
    REPAIR_STATUS,
    assert_expected_target_sparse_two_row_repairs,
    build_target_sparse_two_row_repairs_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_full_neighborhood() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_FULL_NEIGHBORHOOD)


@pytest.fixture(scope="module")
def source_completions() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_COMPLETIONS)


def test_target_sparse_two_row_repairs_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_target_sparse_two_row_repairs(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_TARGET_SPARSE_TWO_ROW_REPAIRS_"
        "DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "assignments 0 and 11",
        "All 6624 one-completion plus one-repair candidates fail",
        "does not prove assignments 0 and 11 are impossible",
        "does not prove center migration",
        "does not prove support existence",
        "does not prove row forcing",
        "does not prove endpoint-8 forcing",
        "does not prove that pair [3,5] is impossible",
        "does not prove n=9",
        "does not prove the bootstrap bridge",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_target_sparse_two_row_repairs_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["source_completion_gate_status"] == (
        "NOT_READY_TARGET_SPARSE_ONE_ROW_COMPLETIONS_FAIL_BASIC_FILTERS"
    )
    assert summary["target_sparse_assignment_indices"] == [0, 11]
    assert summary["source_completion_attempt_count"] == 12
    assert summary["repair_centers_per_completion"] == 8
    assert summary["candidate_rows_per_repair_center"] == 69
    assert summary["repair_candidate_count"] == 6624
    assert summary["repair_basic_filter_surviving_candidate_count"] == 0
    assert summary["vertex_circle_checked_repair_candidate_count"] == 0
    assert summary["repair_records_with_basic_filter_survivor_count"] == 0
    assert summary["assignment_repair_candidate_counts"] == {"0": 1104, "11": 5520}
    assert summary["repair_center_counts"] == {
        "0": 828,
        "1": 828,
        "2": 552,
        "3": 690,
        "4": 828,
        "5": 828,
        "6": 828,
        "7": 414,
        "8": 828,
    }
    assert summary["completion_row_repair_candidate_counts"] == {
        "0,1,4,6": 2208,
        "0,2,4,6": 552,
        "0,3,4,6": 552,
        "0,4,5,6": 552,
        "0,4,6,7": 552,
        "0,4,6,8": 2208,
    }
    assert summary["missing_target_repair_candidate_counts"] == {
        "0": 1104,
        "4": 3312,
        "6": 2208,
    }
    assert summary["endpoint_exact_row_allowed_repair_candidate_count"] == 4416
    assert summary["endpoint_exact_row_disallowed_repair_candidate_count"] == 2208
    assert summary["failure_attempt_reason_counts"] == {
        "crossing": 6624,
        "selected_indegree_cap": 1260,
        "witness_pair_cap": 6582,
    }
    assert summary["failure_detail_counts"] == {
        "crossing": 36962,
        "selected_indegree_cap": 1260,
        "witness_pair_cap": 19141,
    }
    assert summary["one_completion_one_repair_survives_basic_filters"] is False
    assert summary["current_evidence_forces_target_sparse_obstruction"] is False
    assert summary["gate_status"] == GATE_STATUS
    assert summary["repair_status"] == REPAIR_STATUS


def test_target_sparse_two_row_repairs_records() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = payload["repair_records"]

    assert len(records) == 12
    assert [record["source_completion_index"] for record in records] == list(range(12))
    assert Counter(record["assignment_index"] for record in records) == {0: 2, 11: 10}
    assert all(record["repair_candidate_count"] == 552 for record in records)
    assert all(
        record["basic_filter_surviving_candidate_count"] == 0
        for record in records
    )
    assert all(
        record["vertex_circle_checked_candidate_count"] == 0
        for record in records
    )
    assert all(record["all_repair_candidates_fail_basic_filters"] is True for record in records)
    assert all(
        record["failure_attempt_reason_counts"]["crossing"] == 552
        for record in records
    )
    assert records[0]["repair_center_counts"] == {
        "0": 69,
        "1": 69,
        "3": 69,
        "4": 69,
        "5": 69,
        "6": 69,
        "7": 69,
        "8": 69,
    }
    assert records[2]["repair_center_counts"] == {
        "0": 69,
        "1": 69,
        "2": 69,
        "4": 69,
        "5": 69,
        "6": 69,
        "7": 69,
        "8": 69,
    }


def test_target_sparse_two_row_repairs_artifact_matches_generator(
    source_full_neighborhood: dict[str, object],
    source_completions: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_target_sparse_two_row_repairs_payload(
        source_full_neighborhood,
        source_completions,
    )


def test_target_sparse_two_row_repairs_rejects_overclaim_flags() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["one_completion_one_repair_survives_basic_filters"] = True
    bad["summary"]["current_evidence_forces_target_sparse_obstruction"] = True
    bad["decision"]["one_completion_one_repair_survives_basic_filters"] = True
    bad["decision"]["current_evidence_forces_target_sparse_obstruction"] = True

    errors = validate_payload(bad, recompute=False)

    assert any(
        "one_completion_one_repair_survives_basic_filters" in error
        for error in errors
    )
    assert any(
        "current_evidence_forces_target_sparse_obstruction" in error
        for error in errors
    )


def test_target_sparse_two_row_repairs_rejects_tampered_survivor_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["repair_basic_filter_surviving_candidate_count"] = 1

    errors = validate_payload(bad, recompute=False)

    assert any(
        "repair_basic_filter_surviving_candidate_count" in error for error in errors
    )


def test_target_sparse_two_row_repairs_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_center8_target_sparse_two_row_repairs.py",
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
    assert payload["target_sparse_assignment_indices"] == [0, 11]
    assert payload["source_completion_attempt_count"] == 12
    assert payload["repair_candidate_count"] == 6624
    assert payload["repair_basic_filter_surviving_candidate_count"] == 0
    assert payload["failure_attempt_reason_counts"] == {
        "crossing": 6624,
        "selected_indegree_cap": 1260,
        "witness_pair_cap": 6582,
    }
    assert payload["gate_status"] == GATE_STATUS
