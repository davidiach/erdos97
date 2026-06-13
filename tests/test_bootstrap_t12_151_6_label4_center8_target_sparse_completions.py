from __future__ import annotations

from collections import Counter
import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_center8_target_sparse_completions import (
    COMPLETION_STATUS,
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    GATE_STATUS,
    assert_expected_target_sparse_completions,
    build_target_sparse_completions_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_full_neighborhood() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_FULL_NEIGHBORHOOD)


@pytest.fixture(scope="module")
def source_residual_target_rows() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS)


def test_target_sparse_completions_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_target_sparse_completions(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_TARGET_SPARSE_COMPLETIONS_"
        "DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "assignments 0 and 11",
        "All 12 one-row completions fail basic filters",
        "does not prove support existence",
        "does not prove row forcing",
        "does not prove center migration",
        "does not prove endpoint-8 forcing",
        "does not prove that assignments 0 and 11 are impossible",
        "does not prove that pair [3,5] is impossible",
        "does not prove n=9",
        "does not prove the bootstrap bridge",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_target_sparse_completions_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["conditional_center8_target_center"] == 8
    assert summary["conditional_center8_triple"] == [0, 4, 6]
    assert summary["source_residual_gate_status"] == (
        "NOT_READY_RESIDUAL_TARGET_ROWS_DO_NOT_FORCE_CENTER8"
    )
    assert summary["target_sparse_assignment_indices"] == [0, 11]
    assert summary["target_sparse_pair_row_count"] == 6
    assert summary["completion_attempt_count"] == 12
    assert summary["generated_valid_completion_count"] == 12
    assert summary["basic_filter_surviving_completion_count"] == 0
    assert summary["vertex_circle_checked_completion_count"] == 0
    assert summary["completion_assignment_counts"] == {"0": 2, "11": 10}
    assert summary["completion_row_center_counts"] == {"2": 4, "3": 2, "7": 6}
    assert summary["completion_missing_target_counts"] == {"0": 2, "4": 6, "6": 4}
    assert summary["completion_exact_row_counts"] == {
        "0,1,4,6": 4,
        "0,2,4,6": 1,
        "0,3,4,6": 1,
        "0,4,5,6": 1,
        "0,4,6,7": 1,
        "0,4,6,8": 4,
    }
    assert summary["endpoint_exact_row_allowed_completion_count"] == 8
    assert summary["endpoint_exact_row_disallowed_completion_count"] == 4
    assert summary["failure_attempt_reason_counts"] == {
        "crossing": 12,
        "witness_pair_cap": 12,
    }
    assert summary["failure_detail_counts"] == {
        "crossing": 29,
        "witness_pair_cap": 13,
    }
    assert summary["one_row_completions_survive_basic_filters"] is False
    assert summary["current_evidence_forces_target_sparse_obstruction"] is False
    assert summary["gate_status"] == GATE_STATUS
    assert summary["completion_status"] == COMPLETION_STATUS


def test_target_sparse_completions_records() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = payload["completion_records"]

    assert len(records) == 12
    assert Counter(record["assignment_index"] for record in records) == {
        0: 2,
        11: 10,
    }
    assert [record["row_center"] for record in records] == [
        2,
        2,
        3,
        3,
        2,
        2,
        7,
        7,
        7,
        7,
        7,
        7,
    ]
    assert all(record["completion_valid_4set"] is True for record in records)
    assert all(record["basic_filter_ok"] is False for record in records)
    assert all(record["vertex_circle_status"] is None for record in records)
    assert all(
        set(record["failure_reason_types"]) == {"crossing", "witness_pair_cap"}
        for record in records
    )
    assert all(
        {0, 4, 6} <= set(record["completion_row_witnesses"])
        for record in records
    )
    assert Counter(
        record["completion_endpoint_exact_row_allowed"] for record in records
    ) == {
        True: 8,
        False: 4,
    }


def test_target_sparse_completions_artifact_matches_generator(
    source_full_neighborhood: dict[str, object],
    source_residual_target_rows: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_target_sparse_completions_payload(
        source_full_neighborhood,
        source_residual_target_rows,
    )


def test_target_sparse_completions_rejects_overclaim_flags() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["one_row_completions_survive_basic_filters"] = True
    bad["summary"]["current_evidence_forces_target_sparse_obstruction"] = True
    bad["decision"]["one_row_completions_survive_basic_filters"] = True
    bad["decision"]["current_evidence_forces_target_sparse_obstruction"] = True

    errors = validate_payload(bad, recompute=False)

    assert any("one_row_completions_survive_basic_filters" in error for error in errors)
    assert any(
        "current_evidence_forces_target_sparse_obstruction" in error
        for error in errors
    )


def test_target_sparse_completions_rejects_tampered_survivor_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["basic_filter_surviving_completion_count"] = 1

    errors = validate_payload(bad, recompute=False)

    assert any("basic_filter_surviving_completion_count" in error for error in errors)


def test_target_sparse_completions_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_center8_target_sparse_completions.py",
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
    assert payload["target_sparse_assignment_indices"] == [0, 11]
    assert payload["completion_attempt_count"] == 12
    assert payload["basic_filter_surviving_completion_count"] == 0
    assert payload["failure_attempt_reason_counts"] == {
        "crossing": 12,
        "witness_pair_cap": 12,
    }
    assert payload["gate_status"] == GATE_STATUS
