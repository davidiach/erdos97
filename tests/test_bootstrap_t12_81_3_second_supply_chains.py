from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_81_3_second_supply_chains import (
    DEFAULT_ARTIFACT,
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_81_3_second_supply_chains_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_81_3_second_supply_chains_payload()


def test_81_3_second_supply_chains_counts_and_scope(
    payload: dict[str, object],
) -> None:
    assert_expected_payload(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_81_3_SECOND_SUPPLY_CHAINS_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "Second-step prefix CSP" in claim_scope
    assert "one second-step prefix survivor" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope


def test_81_3_second_supply_chains_summary(payload: dict[str, object]) -> None:
    summary = payload["summary"]

    assert summary["target_row_key"] == "81:3"
    assert summary["source_record_ids"] == [81]
    assert summary["deletion_seed"] == [0, 1, 4]
    assert summary["connector_pair"] == [0, 1]
    assert summary["target_center"] == 3
    assert summary["eventual_supply_label"] == 6
    assert summary["first_step_survivor_count"] == 3
    assert summary["second_step_centers_per_prefix"] == [2, 5, 7]
    assert summary["second_step_support_count_per_prefix_center"] == 76
    assert summary["fixed_second_step_prefix_count"] == 684
    assert summary["implicit_selected_assignment_space_size"] == 3617000856000000
    assert summary["search_node_count"] == 303
    assert summary["empty_domain_count"] == 135
    assert summary["initial_auxiliary_support_catalogue_incompatible_count"] == 678
    assert summary["initial_auxiliary_support_catalogue_searched_count"] == 6
    assert summary["detected_solution_count"] == 1
    assert summary["surviving_second_step_prefix_count"] == 1
    assert summary["surviving_second_step_prefix_indices"] == [1]
    assert summary["surviving_second_step_centers"] == [2]
    assert summary["immediate_label_6_extension_candidate_count"] == 118
    assert summary[
        "immediate_label_6_extension_implicit_selected_assignment_space_size"
    ] == 14386792000000
    assert summary["immediate_label_6_extension_detected_solution_count"] == 0
    assert summary["surviving_immediate_label_6_extension_count"] == 0
    assert summary["scan_status"] == SCAN_STATUS


def test_81_3_second_supply_chains_generation(payload: dict[str, object]) -> None:
    generation = payload["support_generation"]

    assert generation["first_step_prefix_survivor_count"] == 3
    assert generation["second_step_centers_by_prefix"] == {
        "0": [2, 5, 7],
        "1": [2, 5, 7],
        "2": [2, 5, 7],
    }
    assert generation["second_step_support_count_by_prefix_center"] == {
        "0:2": 76,
        "0:5": 76,
        "0:7": 76,
        "1:2": 76,
        "1:5": 76,
        "1:7": 76,
        "2:2": 76,
        "2:5": 76,
        "2:7": 76,
    }
    assert generation["second_step_total_selected_row_choices_over_supports"] == 7686
    extension_generation = generation[
        "immediate_label_6_extension_support_generation"
    ]
    assert len(extension_generation) == 1
    assert extension_generation[0]["label_6_supply_support_count"] == 118
    assert extension_generation[0][
        "label_6_supply_total_selected_row_choices_over_supports"
    ] == 1070


def test_81_3_second_supply_chains_survivor(
    payload: dict[str, object],
) -> None:
    survivors = payload["survivors"]

    assert len(survivors) == 1
    survivor = survivors[0]
    assert survivor["prefix_survivor_index"] == 1
    assert survivor["first_step_center"] == 8
    assert survivor["first_step_support"] == [0, 1, 4, 7]
    assert survivor["auxiliary_target_support"] == [0, 2, 4, 6]
    assert survivor["second_step_center"] == 2
    assert survivor["second_step_support"] == [1, 3, 4, 8]
    assert survivor["detected_solution_count"] == 1
    assert survivor["solution_search_status"] == "STOPPED_AFTER_FIRST_SOLUTION"

    extension = payload["immediate_label_6_extension_scan"]
    assert extension["aggregate"]["candidate_count"] == 118
    assert extension["aggregate"]["detected_solution_count"] == 0
    assert extension["survivors"] == []


def test_81_3_second_supply_chains_artifact_matches_generator(
    payload: dict[str, object],
) -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == payload


def test_81_3_second_supply_chains_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_second_supply_chains.py",
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
    assert payload["summary"]["surviving_second_step_prefix_count"] == 1


def test_81_3_second_supply_chains_expected_payload_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["surviving_second_step_prefix_count"] = 0

    with pytest.raises(AssertionError, match="surviving_second_step_prefix_count"):
        assert_expected_payload(bad)
