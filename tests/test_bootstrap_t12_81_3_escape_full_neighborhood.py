from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_81_3_escape_full_neighborhood import (
    DEFAULT_ARTIFACT,
    IMPLICIT_ASSIGNMENT_SPACE_SIZE,
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_81_3_escape_full_neighborhood_payload,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_81_3_escape_full_neighborhood_payload()


def test_81_3_full_neighborhood_counts_and_scope(payload: dict[str, object]) -> None:
    assert_expected_payload(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_81_3_ESCAPE_FULL_NEIGHBORHOOD_CSP_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "Full-neighborhood CSP" in claim_scope
    assert "329,417,200,000,000 assignments" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope


def test_81_3_full_neighborhood_summary(payload: dict[str, object]) -> None:
    summary = payload["summary"]

    assert summary["target_row_key"] == "81:3"
    assert summary["source_record_ids"] == [81]
    assert summary["deletion_seed"] == [0, 1, 4]
    assert summary["connector_pair"] == [0, 1]
    assert summary["supply_center"] == 6
    assert summary["target_center"] == 3
    assert summary["free_row_centers"] == [0, 1, 2, 4, 5, 7, 8]
    assert summary["fixed_replacement_row_centers"] == [3, 6]
    assert summary["center_6_supply_class_count"] == 5
    assert summary["center_3_connector_avoiding_class_count"] == 8
    assert summary["fixed_replacement_pair_count"] == 40
    assert summary["free_row_replacement_count_per_center"] == 70
    assert summary["implicit_assignment_space_size"] == IMPLICIT_ASSIGNMENT_SPACE_SIZE
    assert summary["search_node_count"] == 1177
    assert summary["empty_domain_count"] == 684
    assert summary["initial_fixed_pair_incompatible_count"] == 8
    assert summary["initial_fixed_pair_searched_count"] == 32
    assert summary["complete_solution_count"] == 0
    assert summary["surviving_assignment_count"] == 0
    assert summary["scan_status"] == SCAN_STATUS


def test_81_3_full_neighborhood_fixed_pair_summaries(
    payload: dict[str, object],
) -> None:
    fixed_summaries = payload["fixed_pair_summaries"]

    assert len(fixed_summaries) == 40
    assert sum(record["complete_solution_count"] for record in fixed_summaries) == 0
    assert {
        record["initial_status"] for record in fixed_summaries
    } == {"INITIAL_FIXED_PAIR_INCOMPATIBLE", "SEARCH_EXHAUSTED"}
    assert sum(record["search_node_count"] for record in fixed_summaries) == 1177


def test_81_3_full_neighborhood_generation_space(payload: dict[str, object]) -> None:
    generation = payload["candidate_generation"]

    assert generation["center_6_supply_classes"] == [
        [0, 1, 2, 4],
        [0, 1, 3, 4],
        [0, 1, 4, 5],
        [0, 1, 4, 7],
        [0, 1, 4, 8],
    ]
    assert generation["free_row_choice_count_per_center"] == {
        "0": 70,
        "1": 70,
        "2": 70,
        "4": 70,
        "5": 70,
        "7": 70,
        "8": 70,
    }


def test_81_3_full_neighborhood_artifact_matches_generator(
    payload: dict[str, object],
) -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == payload


def test_81_3_full_neighborhood_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_escape_full_neighborhood.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    payload = json.loads(result.stdout)
    assert payload["summary"]["scan_status"] == SCAN_STATUS
    assert payload["summary"]["surviving_assignment_count"] == 0


def test_81_3_full_neighborhood_expected_payload_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["surviving_assignment_count"] = 1

    with pytest.raises(AssertionError, match="surviving_assignment_count"):
        assert_expected_payload(bad)
