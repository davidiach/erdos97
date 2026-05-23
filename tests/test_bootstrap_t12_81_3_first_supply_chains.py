from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_81_3_first_supply_chains import (
    DEFAULT_ARTIFACT,
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_81_3_first_supply_chains_payload,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_81_3_first_supply_chains_payload()


def test_81_3_first_supply_chains_counts_and_scope(
    payload: dict[str, object],
) -> None:
    assert_expected_payload(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_81_3_FIRST_SUPPLY_CHAINS_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "First-step prefix CSP" in claim_scope
    assert "three first-step prefix survivors" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope


def test_81_3_first_supply_chains_summary(payload: dict[str, object]) -> None:
    summary = payload["summary"]

    assert summary["target_row_key"] == "81:3"
    assert summary["source_record_ids"] == [81]
    assert summary["deletion_seed"] == [0, 1, 4]
    assert summary["connector_pair"] == [0, 1]
    assert summary["target_center"] == 3
    assert summary["eventual_supply_label"] == 6
    assert summary["first_step_centers"] == [2, 5, 6, 7, 8]
    assert summary["first_step_support_count"] == 155
    assert summary["center_3_connector_avoiding_support_count"] == 30
    assert summary["fixed_prefix_support_pair_count"] == 4650
    assert summary["implicit_selected_assignment_space_size"] == 4983670464500000000
    assert summary["search_node_count"] == 8852
    assert summary["empty_domain_count"] == 5339
    assert summary["initial_auxiliary_support_pair_incompatible_count"] == 3958
    assert summary["initial_auxiliary_support_pair_searched_count"] == 692
    assert summary["detected_solution_count"] == 3
    assert summary["surviving_prefix_pair_count"] == 3
    assert summary["surviving_prefix_first_step_centers"] == [8]
    assert summary["immediate_label_6_extension_candidate_count"] == 228
    assert summary["immediate_label_6_extension_detected_solution_count"] == 0
    assert summary["surviving_immediate_label_6_extension_count"] == 0
    assert summary["scan_status"] == SCAN_STATUS


def test_81_3_first_supply_chains_generation(payload: dict[str, object]) -> None:
    generation = payload["support_generation"]

    assert generation["first_step_support_count_by_center"] == {
        "2": 31,
        "5": 31,
        "6": 31,
        "7": 31,
        "8": 31,
    }
    assert generation["first_step_support_size_histogram"] == {
        "4": 25,
        "5": 50,
        "6": 50,
        "7": 25,
        "8": 5,
    }
    assert generation["first_step_total_selected_row_choices_over_supports"] == 2275
    assert generation["center_3_total_selected_row_choices_over_supports"] == 266


def test_81_3_first_supply_chains_survivors(
    payload: dict[str, object],
) -> None:
    survivors = payload["survivors"]

    assert len(survivors) == 3
    assert {record["first_step_center"] for record in survivors} == {8}
    assert {
        tuple(record["first_step_support"]) for record in survivors
    } == {(0, 1, 4, 5), (0, 1, 4, 7)}
    assert all(record["detected_solution_count"] == 1 for record in survivors)

    extension = payload["immediate_label_6_extension_scan"]
    assert extension["aggregate"]["extension_candidate_count"] == 228
    assert extension["aggregate"]["detected_solution_count"] == 0
    assert extension["survivors"] == []


def test_81_3_first_supply_chains_artifact_matches_generator(
    payload: dict[str, object],
) -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == payload


def test_81_3_first_supply_chains_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_first_supply_chains.py",
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
    assert payload["summary"]["surviving_prefix_pair_count"] == 3


def test_81_3_first_supply_chains_expected_payload_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["surviving_prefix_pair_count"] = 0

    with pytest.raises(AssertionError, match="surviving_prefix_pair_count"):
        assert_expected_payload(bad)
