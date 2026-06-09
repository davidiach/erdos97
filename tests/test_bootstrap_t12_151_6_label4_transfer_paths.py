from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_transfer_paths import (
    DEFAULT_ARTIFACT,
    DEFAULT_LABEL4_QUOTIENT_ROLES,
    DEFAULT_SOURCE_RESIDUAL_TARGETS,
    TRANSFER_STATUS,
    assert_expected_label4_transfer_paths,
    build_label4_transfer_paths_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_residual_targets() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_RESIDUAL_TARGETS)


@pytest.fixture(scope="module")
def source_label4_quotient_roles() -> dict[str, object]:
    return load_artifact(DEFAULT_LABEL4_QUOTIENT_ROLES)


def test_label4_transfer_paths_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_label4_transfer_paths(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_151_6_LABEL4_TRANSFER_PATHS_DIAGNOSTIC_ONLY"
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


def test_label4_transfer_paths_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["label4_transfer_path_class_signature_incidence_count"] == 19
    assert summary["label4_transfer_path_class_occurrence_incidence_count"] == 23
    assert summary["direct_endpoint_transfer_class_signature_incidence_count"] == 11
    assert summary["direct_endpoint_transfer_class_occurrence_incidence_count"] == 14
    assert summary["one_equality_edge_transfer_class_signature_incidence_count"] == 5
    assert summary["one_equality_edge_transfer_class_occurrence_incidence_count"] == 5
    assert summary["two_equality_edge_transfer_class_signature_incidence_count"] == 3
    assert summary["two_equality_edge_transfer_class_occurrence_incidence_count"] == 4
    assert summary["signatures_with_positive_transfer_class"] == 8
    assert summary["occurrences_with_positive_transfer_class"] == 9
    assert summary["transfer_edge_count_signature_counts"] == {"0": 11, "1": 5, "2": 3}
    assert summary["transfer_edge_count_occurrence_counts"] == {"0": 14, "1": 5, "2": 4}
    assert summary["positive_transfer_path_edge_signature_counts_by_row"] == {
        "5": 6,
        "6": 3,
        "7": 2,
    }
    assert summary["positive_transfer_path_edge_occurrence_counts_by_row"] == {
        "5": 7,
        "6": 4,
        "7": 2,
    }
    assert summary["transfer_status"] == TRANSFER_STATUS


def test_label4_transfer_path_records_are_consistent() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = payload["transfer_path_records"]

    assert len(records) == 19
    mode_counts: dict[str, int] = {}
    equality_only_records = []
    for index, record in enumerate(records):
        assert record["transfer_record_index"] == index
        assert all(4 in pair for pair in record["label4_pair_members"])
        assert record["chosen_label4_pair"] in record["label4_pair_members"]
        assert record["chosen_cycle_endpoint_pair"] in record["cycle_endpoint_pairs"]
        assert record["transfer_edge_count"] == len(record["transfer_path"])
        mode_counts[record["transfer_mode"]] = mode_counts.get(record["transfer_mode"], 0) + 1
        if record["transfer_edge_count"] == 0:
            assert record["chosen_label4_pair"] == record["chosen_cycle_endpoint_pair"]
            assert record["transfer_mode"] == "direct_endpoint"
        else:
            path = record["transfer_path"]
            assert path[0]["from_pair"] == record["chosen_label4_pair"]
            assert path[-1]["to_pair"] == record["chosen_cycle_endpoint_pair"]
            for previous, current in zip(path, path[1:], strict=False):
                assert previous["to_pair"] == current["from_pair"]
        if record["access_mode"] == "quotient_equality_only":
            equality_only_records.append(record)

    assert mode_counts == {
        "direct_endpoint": 11,
        "one_equality_edge": 5,
        "two_equality_edges": 3,
    }
    assert len(equality_only_records) == 2
    assert {record["transfer_edge_count"] for record in equality_only_records} == {1}
    assert {record["transfer_path"][0]["row"] for record in equality_only_records} == {5}


def test_label4_transfer_paths_artifact_matches_generator(
    source_residual_targets: dict[str, object],
    source_label4_quotient_roles: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_label4_transfer_paths_payload(
        source_residual_targets,
        source_label4_quotient_roles,
    )


def test_label4_transfer_paths_rejects_tampered_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["summary"]["direct_endpoint_transfer_class_signature_incidence_count"] = 10

    errors = validate_payload(payload, recompute=False)

    assert any(
        "direct_endpoint_transfer_class_signature_incidence_count" in error
        for error in errors
    )


def test_label4_transfer_paths_rejects_broken_path_chain() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    positive = next(
        record for record in payload["transfer_path_records"] if record["transfer_path"]
    )
    positive["transfer_path"][0]["from_pair"] = [0, 1]

    errors = validate_payload(payload, recompute=False)

    assert any("path start mismatch" in error for error in errors)


def test_label4_transfer_paths_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_transfer_paths.py",
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
    assert payload["label4_transfer_path_class_signature_incidence_count"] == 19
    assert payload["direct_endpoint_transfer_class_signature_incidence_count"] == 11
    assert payload["one_equality_edge_transfer_class_signature_incidence_count"] == 5
    assert payload["two_equality_edge_transfer_class_signature_incidence_count"] == 3
