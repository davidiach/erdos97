from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_81_3_post8_supply_chains import (
    DEFAULT_ARTIFACT,
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_81_3_post8_supply_chains_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_81_3_post8_supply_chains_payload()


def test_81_3_post8_supply_chains_counts_and_scope(
    payload: dict[str, object],
) -> None:
    assert_expected_payload(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_81_3_POST8_SUPPLY_CHAINS_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "Post-center-8 supply-chain CSP" in claim_scope
    assert "No selected-row survivor is found" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope


def test_81_3_post8_supply_chains_summary(payload: dict[str, object]) -> None:
    summary = payload["summary"]

    assert summary["target_row_key"] == "81:3"
    assert summary["source_record_ids"] == [81]
    assert summary["deletion_seed"] == [0, 1, 4]
    assert summary["first_step_center"] == 8
    assert summary["post_first_step_closure"] == [0, 1, 4, 8]
    assert summary["eventual_supply_center"] == 6
    assert summary["target_center"] == 3
    assert summary["intermediate_center_universe"] == [2, 5, 7]
    assert summary["source_first_supply_survivor_count"] == 3
    assert summary["source_first_supply_survivor_centers"] == [8]
    assert summary["total_support_catalogue_candidate_count"] == 3_918_164_268
    assert summary["total_initially_compatible_support_catalogue_count"] == 58
    assert summary["total_selected_search_node_count"] == 223
    assert summary["total_selected_empty_domain_count"] == 85
    assert summary["total_selected_detected_solution_count"] == 0
    assert summary["scan_status"] == SCAN_STATUS


def test_81_3_post8_supply_chains_by_length(payload: dict[str, object]) -> None:
    summary = payload["summary"]

    assert summary["support_catalogue_candidate_count_by_length"] == {
        "0": 228,
        "1": 80_712,
        "2": 23_890_752,
        "3": 3_894_192_576,
    }
    assert summary["initially_compatible_support_catalogue_count_by_length"] == {
        "0": 0,
        "1": 14,
        "2": 20,
        "3": 24,
    }
    assert summary["selected_search_node_count_by_length"] == {
        "0": 0,
        "1": 86,
        "2": 94,
        "3": 43,
    }
    assert summary["selected_detected_solution_count_by_length"] == {
        "0": 0,
        "1": 0,
        "2": 0,
        "3": 0,
    }


def test_81_3_post8_supply_chains_source_crosswalk(
    payload: dict[str, object],
) -> None:
    source_first = payload["source_first_supply_chains"]
    source_second = payload["source_second_step_chains"]

    assert source_first["scan_status"] == (
        "PREFIX_SURVIVORS_FOUND_BUT_NO_IMMEDIATE_LABEL6_SUPPLY_EXTENSION"
    )
    assert source_second["scan_status"] == (
        "NO_DISTINCT_INTERMEDIATE_CENTER8_TO_LABEL6_CHAINS"
    )
    records = payload["initially_compatible_catalogues"]
    assert len(records) == 58
    assert {tuple(record["intermediate_order"]) for record in records} == {
        (2,),
        (2, 5),
        (2, 7),
        (2, 5, 7),
    }
    assert all(record["detected_solution_count"] == 0 for record in records)


def test_81_3_post8_supply_chains_artifact_matches_generator(
    payload: dict[str, object],
) -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == payload


def test_81_3_post8_supply_chains_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_post8_supply_chains.py",
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
    assert payload["summary"]["total_selected_detected_solution_count"] == 0


def test_81_3_post8_supply_chains_expected_payload_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["total_selected_detected_solution_count"] = 1

    with pytest.raises(AssertionError, match="total_selected_detected_solution_count"):
        assert_expected_payload(bad)
