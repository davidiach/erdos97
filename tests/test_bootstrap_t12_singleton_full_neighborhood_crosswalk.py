from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_bootstrap_t12_singleton_full_neighborhood_crosswalk import (
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_151,
    DEFAULT_SOURCE_81_8,
    assert_expected_singleton_full_neighborhood_crosswalk,
    build_singleton_full_neighborhood_crosswalk_payload,
    load_artifact,
    summary_payload,
    validate_payload,
)

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def source_81_8() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_81_8)


@pytest.fixture(scope="module")
def source_151() -> dict[str, object]:
    return load_artifact(DEFAULT_SOURCE_151)


def test_singleton_full_neighborhood_crosswalk_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_singleton_full_neighborhood_crosswalk(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_SINGLETON_FULL_NEIGHBORHOOD_CROSSWALK_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert payload["summary"] == {
        "basic_filter_complete_assignment_count": 84,
        "basic_filter_non_original_assignment_count": 63,
        "empty_domain_count": 20395,
        "free_row_replacement_count_per_center": 70,
        "implicit_assignment_space_size": 15564962700000000,
        "non_original_vertex_circle_surviving_assignment_count": 0,
        "remaining_gap": (
            "The crosswalk does not prove singleton support existence, does not "
            "prove the target rows are forced by minimal or rich-class geometry, "
            "does not model additional auxiliary rich supports, and does not "
            "promote the review-pending n=9 checker."
        ),
        "scan_status": "FULL_NEIGHBORHOOD_BASIC_SURVIVORS_ALL_VERTEX_CIRCLE_OBSTRUCTED",
        "search_node_count": 38719,
        "source_record_ids": [81, 151],
        "target_center_candidate_count": 27,
        "target_count": 3,
        "target_row_keys": ["81:8", "151:5", "151:8"],
        "vertex_circle_status_counts": {"self_edge": 64, "strict_cycle": 20},
        "vertex_circle_surviving_assignment_count": 0,
    }
    for phrase in (
        "not singleton-support existence",
        "not row forcing",
        "not a proof of n=9",
        "not a proof of the bridge",
        "not a counterexample",
        "not a global status update",
    ):
        assert phrase in payload["claim_scope"]


def test_singleton_full_neighborhood_target_records() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    by_key = {record["target_row_key"]: record for record in payload["target_crosswalk"]}

    assert by_key["81:8"] == {
        "basic_filter_complete_assignment_count": 34,
        "bootstrap_core_witnesses": [0, 2],
        "empty_domain_count": 8436,
        "free_row_replacement_count_per_center": 70,
        "implicit_assignment_space_size": 5188320900000000,
        "non_original_basic_assignment_count": 27,
        "search_node_count": 16010,
        "source_artifact_id": "bootstrap_t12_81_8_full_neighborhood_vertex_circle",
        "source_record_id": 81,
        "target_center": 8,
        "target_center_candidate_count": 9,
        "target_row_key": "81:8",
        "vertex_circle_status_counts": {"self_edge": 27, "strict_cycle": 7},
        "vertex_circle_surviving_assignment_count": 0,
    }
    assert by_key["151:5"]["bootstrap_core_witnesses"] == [2, 4]
    assert by_key["151:5"]["basic_filter_complete_assignment_count"] == 34
    assert by_key["151:5"]["non_original_basic_assignment_count"] == 27
    assert by_key["151:5"]["vertex_circle_status_counts"] == {
        "self_edge": 27,
        "strict_cycle": 7,
    }
    assert by_key["151:8"]["bootstrap_core_witnesses"] == [1, 2]
    assert by_key["151:8"]["basic_filter_complete_assignment_count"] == 16
    assert by_key["151:8"]["non_original_basic_assignment_count"] == 9
    assert by_key["151:8"]["vertex_circle_status_counts"] == {
        "self_edge": 10,
        "strict_cycle": 6,
    }


def test_singleton_full_neighborhood_rejects_tampered_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["summary"]["basic_filter_complete_assignment_count"] = 83

    errors = validate_payload(payload, recompute=False)

    assert any("summary.basic_filter_complete_assignment_count" in error for error in errors)


def test_singleton_full_neighborhood_rejects_tampered_target_status_sum() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["target_crosswalk"][0]["vertex_circle_status_counts"]["self_edge"] = 26

    errors = validate_payload(payload, recompute=False)

    assert any("status counts do not sum" in error for error in errors)


def test_singleton_full_neighborhood_rejects_source_status_drift(
    source_81_8: dict[str, object],
    source_151: dict[str, object],
) -> None:
    tampered = json.loads(json.dumps(source_151))
    tampered["summary"]["vertex_circle_surviving_assignment_count"] = 1

    with pytest.raises(AssertionError, match="vertex_circle_surviving_assignment_count"):
        build_singleton_full_neighborhood_crosswalk_payload(source_81_8, tampered)


@pytest.mark.exhaustive
def test_singleton_full_neighborhood_artifact_matches_generator(
    source_81_8: dict[str, object],
    source_151: dict[str, object],
) -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == build_singleton_full_neighborhood_crosswalk_payload(
        source_81_8,
        source_151,
    )


@pytest.mark.exhaustive
def test_singleton_full_neighborhood_checker_passes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["target_count"] == 3
    assert summary["basic_filter_complete_assignment_count"] == 84


@pytest.mark.exhaustive
def test_singleton_full_neighborhood_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_singleton_full_neighborhood_crosswalk.py",
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
    assert payload["target_count"] == 3
