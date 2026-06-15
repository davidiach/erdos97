from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_target_sparse_full_cone_misses import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_SUPPORT_CONE,
    GATE_STATUS,
    PROBE_STATUS,
    assert_expected_target_sparse_full_cone_misses,
    build_target_sparse_full_cone_misses_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_support_cone() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_SUPPORT_CONE)


def test_target_sparse_full_cone_misses_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_target_sparse_full_cone_misses(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_151_6_LABEL4_TARGET_SPARSE_FULL_CONE_MISSES_"
        "DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "three source-151 row-6 label-4 assignment-0 endpoint rows",
        "HiGHS reports both screens infeasible",
        "stores no exact dual infeasibility certificate",
        "solver diagnostic only",
        "does not prove that no current-row-family certificate exists",
        "does not prove assignments 0 and 11 are impossible",
        "does not prove support existence",
        "does not prove center migration",
        "does not prove row forcing",
        "does not prove endpoint-8 forcing",
        "does not prove that pair [3,5] is impossible",
        "does not prove n=9",
        "does not prove the bootstrap bridge",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_target_sparse_full_cone_misses_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["source_support_cone_gate_status"] == (
        "NOT_READY_SUPPORT_CONE_PARTIAL_ENDPOINT_COVERAGE"
    )
    assert summary["source_support_cone_probe_status"] == (
        "TARGET_SPARSE_SUPPORT_CONE_BOUND_2_PARTIAL_ENDPOINT_ONLY"
    )
    assert summary["strict_row_count"] == 255
    assert summary["source_endpoint_augmented_probe_count"] == 30
    assert summary["source_endpoint_augmented_bounded_certificate_count"] == 27
    assert summary["source_endpoint_augmented_probe_without_certificate_count"] == 3
    assert summary["full_cone_probe_count"] == 3
    assert summary["zero_sum_equalities_feasible_count"] == 0
    assert summary["nonpositive_inequalities_feasible_count"] == 0
    assert summary["full_cone_solver_certificate_found_count"] == 0
    assert summary["all_full_cone_lp_screens_report_infeasible"] is True
    assert summary["all_misses_are_assignment0_source_pair0"] is True
    assert summary["uncovered_endpoint_rows"] == [
        [0, 1, 4, 6],
        [0, 2, 4, 6],
        [0, 4, 6, 7],
    ]
    assert summary["exact_infeasibility_certificates_stored"] is False
    assert summary["current_evidence_forces_target_sparse_obstruction"] is False
    assert summary["gate_status"] == GATE_STATUS
    assert summary["probe_status"] == PROBE_STATUS


def test_target_sparse_full_cone_misses_records_pin_lp_screens() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = payload["full_cone_probe_records"]

    assert len(records) == 3
    assert sorted(record["endpoint_row_witnesses"] for record in records) == [
        [0, 1, 4, 6],
        [0, 2, 4, 6],
        [0, 4, 6, 7],
    ]
    for record in records:
        assert record["assignment_index"] == 0
        assert record["source_pair_row_index"] == 0
        assert record["source_core_index"] == 1
        assert record["row_center"] == 2
        assert record["row_witnesses"] == [0, 3, 4, 8]
        assert record["endpoint_center"] == 8
        assert record["endpoint_row_key"] == ",".join(
            str(label) for label in record["endpoint_row_witnesses"]
        )
        assert record["centered_class_count"] == 4
        assert record["distance_class_count"] == 28
        assert record["strict_row_count"] == 255
        assert record["full_cone_solver_certificate_found"] is False
        assert record["exact_infeasibility_certificate_stored"] is False
        for screen_key in (
            "zero_sum_equalities_screen",
            "nonpositive_inequalities_screen",
        ):
            screen = record[screen_key]
            assert screen["solver"] == "scipy.optimize.linprog(method=highs)"
            assert screen["normalization"] == "sum_weights_equals_1"
            assert screen["feasible"] is False
            assert screen["scipy_status_code"] == 2
            assert screen["normalized_status"] == "infeasible_reported_by_highs"
            assert screen["exact_certificate_stored"] is False
            assert screen["solver_result_is_not_exact_certificate"] is True


def test_target_sparse_full_cone_misses_artifact_matches_generator(
    source_support_cone: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_target_sparse_full_cone_misses_payload(
        source_support_cone
    )


def test_target_sparse_full_cone_misses_rejects_overclaim_flags() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["current_evidence_forces_target_sparse_obstruction"] = True
    bad["summary"]["exact_infeasibility_certificates_stored"] = True
    bad["decision"]["current_evidence_forces_target_sparse_obstruction"] = True
    bad["decision"]["exact_infeasibility_certificates_stored"] = True

    errors = validate_payload(bad, recompute=False)

    assert any(
        "current_evidence_forces_target_sparse_obstruction" in error
        for error in errors
    )
    assert any("exact_infeasibility_certificates_stored" in error for error in errors)


def test_target_sparse_full_cone_misses_rejects_tampered_lp_status() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["full_cone_probe_records"][0]["nonpositive_inequalities_screen"][
        "feasible"
    ] = True

    errors = validate_payload(bad, recompute=False)

    assert any("nonpositive_inequalities_screen must stay infeasible" in error for error in errors)


def test_target_sparse_full_cone_misses_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_target_sparse_full_cone_misses.py",
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
    assert payload["full_cone_probe_count"] == 3
    assert payload["zero_sum_equalities_feasible_count"] == 0
    assert payload["nonpositive_inequalities_feasible_count"] == 0
    assert payload["exact_infeasibility_certificates_stored"] is False
    assert payload["gate_status"] == GATE_STATUS
    assert payload["probe_status"] == PROBE_STATUS
