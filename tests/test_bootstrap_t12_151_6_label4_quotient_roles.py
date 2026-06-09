from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_quotient_roles import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_RESIDUAL_TARGETS,
    ROLE_STATUS,
    assert_expected_label4_quotient_roles,
    build_label4_quotient_roles_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_residual_targets() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_RESIDUAL_TARGETS)


def test_label4_quotient_roles_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_label4_quotient_roles(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_151_6_LABEL4_QUOTIENT_ROLES_DIAGNOSTIC_ONLY"
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


def test_label4_quotient_roles_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["label8_free_distinct_exact_signature_count"] == 10
    assert summary["label8_free_occurrence_count"] == 12
    assert summary["signatures_with_label4_cycle_quotient_class"] == 10
    assert summary["occurrences_with_label4_cycle_quotient_class"] == 12
    assert summary["direct_cycle_edge_label4_signature_count"] == 8
    assert summary["direct_cycle_edge_label4_occurrence_count"] == 10
    assert summary["quotient_equality_only_label4_signature_count"] == 2
    assert summary["quotient_equality_only_label4_occurrence_count"] == 2
    assert summary["label4_cycle_quotient_class_signature_incidence_count"] == 19
    assert summary["label4_cycle_quotient_class_occurrence_incidence_count"] == 23
    assert summary["role_status"] == ROLE_STATUS


def test_label4_quotient_role_records_are_consistent() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = payload["quotient_role_records"]

    assert len(records) == 10
    direct = 0
    equality_only = 0
    for index, record in enumerate(records):
        assert record["signature_index"] == index
        assert record["label4_cycle_quotient_class_count"] == len(
            record["label4_cycle_quotient_classes"]
        )
        assert record["label4_cycle_quotient_classes"]
        for class_record in record["label4_cycle_quotient_classes"]:
            assert class_record["label4_pair_members"]
            assert all(4 in pair for pair in class_record["label4_pair_members"])
        if record["access_mode"] == "direct_cycle_edge":
            direct += 1
            assert record["direct_label4_cycle_edges"]
        else:
            equality_only += 1
            assert record["access_mode"] == "quotient_equality_only"
            assert record["direct_label4_cycle_edges"] == []

    assert direct == 8
    assert equality_only == 2


def test_label4_quotient_roles_artifact_matches_generator(
    source_residual_targets: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_label4_quotient_roles_payload(
        source_residual_targets,
    )


def test_label4_quotient_roles_rejects_tampered_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["summary"]["signatures_with_label4_cycle_quotient_class"] = 9

    errors = validate_payload(payload, recompute=False)

    assert any("signatures_with_label4_cycle_quotient_class" in error for error in errors)


def test_label4_quotient_roles_rejects_missing_label4_class() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["quotient_role_records"][0]["label4_cycle_quotient_classes"] = []

    errors = validate_payload(payload, recompute=False)

    assert any("must have label-4 cycle classes" in error for error in errors)


def test_label4_quotient_roles_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_quotient_roles.py",
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
    assert payload["signatures_with_label4_cycle_quotient_class"] == 10
    assert payload["direct_cycle_edge_label4_signature_count"] == 8
    assert payload["quotient_equality_only_label4_signature_count"] == 2
