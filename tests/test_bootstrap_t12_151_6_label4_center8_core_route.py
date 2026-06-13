from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_151_6_label4_center8_core_route import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
    DEFAULT_SOURCE_STRICT_CORE_SPLIT,
    GATE_STATUS,
    assert_expected_center8_core_route,
    build_center8_core_route_payload,
    load_artifact,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_strict_core_split() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_STRICT_CORE_SPLIT)


@pytest.fixture(scope="module")
def source_cascade_endpoint8_targets() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS)


def test_center8_core_route_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_center8_core_route(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_CORE_ROUTE_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    for phrase in (
        "center-8 row with witnesses [0,4,6]",
        "8 of 9 center-8 cores are target-compatible",
        "only 4 of the 32 label-8-visible cores",
        "label-8 visibility alone is not enough",
        "does not prove support existence",
        "does not prove row forcing",
        "does not prove endpoint-8 forcing",
        "does not prove that pair [3,5] is impossible",
        "does not prove n=9",
        "not a counterexample",
    ):
        assert phrase in claim_scope


def test_center8_core_route_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["target_center"] == 6
    assert summary["private_target_center_class"] == [0, 3, 5, 7]
    assert summary["private_support_pair"] == [3, 5]
    assert summary["source_private_lane_assignment_count"] == 12
    assert summary["source_row6_three_row_strict_core_count"] == 44
    assert summary["source_label8_visible_core_count"] == 32
    assert summary["source_label8_free_core_count"] == 12
    assert summary["source_center8_core_count"] == 9
    assert summary["conditional_center8_target_center"] == 8
    assert summary["conditional_center8_triple"] == [0, 4, 6]
    assert summary["center8_core_count"] == 9
    assert summary["center8_target_compatible_core_count"] == 8
    assert summary["center8_target_incompatible_core_count"] == 1
    assert summary["label8_visible_center8_core_count"] == 5
    assert summary["label8_free_center8_core_count"] == 4
    assert summary["label8_visible_center8_target_core_count"] == 4
    assert summary["label8_free_center8_target_core_count"] == 4
    assert summary["label8_visible_non_center8_core_count"] == 27
    assert summary["assignments_with_center8_core"] == 7
    assert summary["assignments_with_center8_target_core"] == 6
    assert summary["assignments_with_label8_visible_center8_target_core"] == 4
    assert summary["assignments_with_label8_free_center8_target_core"] == 4
    assert summary["assignments_with_label8_visible_core_but_no_center8_target_core"] == 6
    assert summary["assignments_without_center8_target_core"] == 6
    assert summary["center8_target_exact_row_counts"] == {
        "0,1,4,6": 4,
        "0,2,4,6": 2,
        "0,4,6,7": 2,
    }
    assert summary["label8_visible_center8_target_exact_row_counts"] == {
        "0,1,4,6": 2,
        "0,2,4,6": 1,
        "0,4,6,7": 1,
    }
    assert summary["covered_endpoint_exact_four_rows"] == [
        [0, 1, 4, 6],
        [0, 2, 4, 6],
        [0, 4, 6, 7],
    ]
    assert summary["missing_endpoint_exact_four_rows"] == [
        [0, 3, 4, 6],
        [0, 4, 5, 6],
    ]
    assert summary["current_evidence_forces_center8_target_core"] is False
    assert summary["label8_visibility_alone_supplies_center8_target"] is False
    assert summary["gate_status"] == GATE_STATUS


def test_center8_core_route_records() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    records = payload["center8_core_records"]

    target_records = [
        record for record in records if record["center8_target_compatible"]
    ]
    non_target_records = [
        record for record in records if not record["center8_target_compatible"]
    ]

    assert len(target_records) == 8
    assert len(non_target_records) == 1
    assert all({0, 4, 6} <= set(record["center8_row_witnesses"]) for record in target_records)
    assert non_target_records[0]["assignment_index"] == 11
    assert non_target_records[0]["center8_row_witnesses"] == [1, 2, 5, 7]
    assert non_target_records[0]["label8_visible"] is True

    assignments = {
        record["assignment_index"]: record
        for record in payload["assignment_route_records"]
    }
    assert assignments[0]["has_label8_visible_core_but_no_center8_target_core"] is True
    assert assignments[3]["label8_free_center8_target_core_count"] == 1
    assert assignments[3]["label8_visible_center8_target_core_count"] == 1
    assert assignments[8]["has_label8_visible_center8_target_core"] is False
    assert assignments[8]["label8_free_center8_target_core_count"] == 1
    assert assignments[11]["non_target_center8_rows"] == [[1, 2, 5, 7]]


def test_center8_core_route_artifact_matches_generator(
    source_strict_core_split: dict[str, object],
    source_cascade_endpoint8_targets: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_center8_core_route_payload(
        source_strict_core_split,
        source_cascade_endpoint8_targets,
    )


def test_center8_core_route_rejects_forcing_overclaim() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["current_evidence_forces_center8_target_core"] = True
    bad["decision"]["current_evidence_forces_center8_target_core"] = True

    errors = validate_payload(bad, recompute=False)

    assert any("current_evidence_forces_center8_target_core" in error for error in errors)


def test_center8_core_route_rejects_tampered_target_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    bad = copy.deepcopy(payload)
    bad["summary"]["center8_target_compatible_core_count"] = 9
    bad["center8_core_records"][-1]["center8_target_compatible"] = True

    errors = validate_payload(bad, recompute=False)

    assert any("target-compatible" in error or "target_count" in error for error in errors)


def test_center8_core_route_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_label4_center8_core_route.py",
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
    assert payload["center8_core_count"] == 9
    assert payload["center8_target_compatible_core_count"] == 8
    assert payload["label8_visible_center8_target_core_count"] == 4
    assert payload["assignments_without_center8_target_core"] == 6
    assert payload["gate_status"] == GATE_STATUS
