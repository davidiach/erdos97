from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_target_sparse_support_cone import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_COMPLETIONS,
    DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    DEFAULT_SOURCE_SUPPORT_LEDGER,
    GATE_STATUS,
    PROBE_STATUS,
    assert_expected_target_sparse_support_cone,
    build_target_sparse_support_cone_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_residual_target_rows() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS)


@pytest.fixture(scope="module")
def source_completions() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_COMPLETIONS)


@pytest.fixture(scope="module")
def source_support_ledger() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_SUPPORT_LEDGER)


def test_target_sparse_support_cone_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_target_sparse_support_cone(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_151_6_LABEL4_TARGET_SPARSE_SUPPORT_CONE_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "assignments 0 and 11",
        "no bounded certificate",
        "27 of 30",
        "three assignment-0 endpoint rows uncovered",
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


def test_target_sparse_support_cone_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["conditional_center8_target_center"] == 8
    assert summary["conditional_center8_triple"] == [0, 4, 6]
    assert summary["cascade_support_requirements"] == [
        {"center": 5, "witness_pair": [4, 6]},
        {"center": 6, "witness_pair": [0, 5]},
    ]
    assert summary["target_sparse_assignment_indices"] == [0, 11]
    assert summary["strict_row_count"] == 255
    assert summary["max_certificate_row_count"] == 2
    assert summary["target_pair_probe_count"] == 6
    assert summary["target_pair_bounded_certificate_count"] == 0
    assert summary["completion_probe_count"] == 12
    assert summary["completion_bounded_certificate_count"] == 0
    assert summary["endpoint_augmented_probe_count"] == 30
    assert summary["endpoint_augmented_bounded_certificate_count"] == 27
    assert summary["endpoint_augmented_probe_without_certificate_count"] == 3
    assert summary["endpoint_augmented_assignment_certificate_counts"] == {
        "0": 2,
        "11": 25,
    }
    assert summary["endpoint_augmented_assignment_miss_counts"] == {"0": 3}
    assert summary["endpoint_augmented_exact_row_miss_counts"] == {
        "0,1,4,6": 1,
        "0,2,4,6": 1,
        "0,4,6,7": 1,
    }
    assert (
        summary["all_target_pair_and_completion_probes_have_no_bounded_certificate"]
        is True
    )
    assert (
        summary["all_assignment11_endpoint_augmented_probes_have_bounded_certificate"]
        is True
    )
    assert summary["assignment0_endpoint_augmented_probe_miss_count"] == 3
    assert summary["current_evidence_forces_target_sparse_obstruction"] is False
    assert summary["gate_status"] == GATE_STATUS
    assert summary["probe_status"] == PROBE_STATUS


def test_target_sparse_support_cone_records_pin_uncovered_rows() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]
    target_pair_records = payload["target_pair_probe_records"]
    completion_records = payload["completion_probe_records"]
    endpoint_records = payload["endpoint_augmented_probe_records"]

    assert len(target_pair_records) == 6
    assert all(
        record["bounded_certificate_found"] is False
        for record in target_pair_records
    )
    assert len(completion_records) == 12
    assert all(
        record["bounded_certificate_found"] is False
        for record in completion_records
    )

    misses = [
        record for record in endpoint_records if not record["bounded_certificate_found"]
    ]
    assert len(misses) == 3
    assert {record["assignment_index"] for record in misses} == {0}
    assert {record["source_pair_row_index"] for record in misses} == {0}
    assert sorted(record["endpoint_row_witnesses"] for record in misses) == [
        [0, 1, 4, 6],
        [0, 2, 4, 6],
        [0, 4, 6, 7],
    ]
    assert summary["endpoint_augmented_uncovered_assignment_rows"] == [
        {
            "assignment_index": 0,
            "source_pair_row_index": 0,
            "row_center": 2,
            "row_witnesses": [0, 3, 4, 8],
            "uncovered_endpoint_rows": [
                [0, 1, 4, 6],
                [0, 2, 4, 6],
                [0, 4, 6, 7],
            ],
        }
    ]

    hits = [
        record for record in endpoint_records if record["bounded_certificate_found"]
    ]
    assert len(hits) == 27
    assert all(record["first_bounded_certificate"] for record in hits)
    assert all(
        record["first_bounded_certificate"]["nonpositive_sum_verified"] is True
        for record in hits
    )


def test_target_sparse_support_cone_artifact_matches_generator(
    source_residual_target_rows: dict[str, object],
    source_completions: dict[str, object],
    source_support_ledger: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_target_sparse_support_cone_payload(
        source_residual_target_rows,
        source_completions,
        source_support_ledger,
    )


def test_target_sparse_support_cone_rejects_overclaim_flags() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["current_evidence_forces_target_sparse_obstruction"] = True
    bad["decision"]["current_evidence_forces_target_sparse_obstruction"] = True

    errors = validate_payload(bad, recompute=False)

    assert any(
        "current_evidence_forces_target_sparse_obstruction" in error
        for error in errors
    )


def test_target_sparse_support_cone_rejects_tampered_endpoint_miss_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["endpoint_augmented_probe_without_certificate_count"] = 0

    errors = validate_payload(bad, recompute=False)

    assert any(
        "endpoint_augmented_probe_without_certificate_count" in error
        for error in errors
    )


def test_target_sparse_support_cone_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_target_sparse_support_cone.py",
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
    assert payload["target_pair_probe_count"] == 6
    assert payload["target_pair_bounded_certificate_count"] == 0
    assert payload["completion_probe_count"] == 12
    assert payload["completion_bounded_certificate_count"] == 0
    assert payload["endpoint_augmented_probe_count"] == 30
    assert payload["endpoint_augmented_bounded_certificate_count"] == 27
    assert payload["endpoint_augmented_probe_without_certificate_count"] == 3
    assert payload["gate_status"] == GATE_STATUS
    assert payload["probe_status"] == PROBE_STATUS
