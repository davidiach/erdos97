from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_81_3_second_step_chains import (
    DEFAULT_ARTIFACT,
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_81_3_second_step_chains_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_81_3_second_step_chains_payload()


def test_81_3_second_step_chains_counts_and_scope(
    payload: dict[str, object],
) -> None:
    assert_expected_payload(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_81_3_SECOND_STEP_CHAINS_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "Distinct-intermediate continuation CSP" in claim_scope
    assert "no surviving chain" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope


def test_81_3_second_step_chains_summary(payload: dict[str, object]) -> None:
    summary = payload["summary"]

    assert summary["target_row_key"] == "81:3"
    assert summary["source_record_ids"] == [81]
    assert summary["deletion_seed"] == [0, 1, 4]
    assert summary["connector_pair"] == [0, 1]
    assert summary["target_center"] == 3
    assert summary["first_step_center"] == 8
    assert summary["eventual_supply_label"] == 6
    assert summary["source_prefix_survivor_count"] == 3
    assert summary["intermediate_centers_after_center8"] == [2, 5, 7]
    assert summary["max_distinct_intermediate_chain_length"] == 3
    assert summary["support_prefix_pruned_count"] == 4112
    assert summary["label_6_supply_candidate_count"] == 9528
    assert summary["initial_auxiliary_catalogue_incompatible_count"] == 9470
    assert summary["initial_auxiliary_catalogue_searched_count"] == 58
    assert summary["search_node_count"] == 223
    assert summary["empty_domain_count"] == 85
    assert summary["detected_solution_count"] == 0
    assert summary["surviving_chain_count"] == 0
    assert summary["scan_status"] == SCAN_STATUS


def test_81_3_second_step_chains_by_length(payload: dict[str, object]) -> None:
    chain_scan = payload["chain_scan"]
    per_length = chain_scan["per_chain_length"]

    assert per_length["0"]["label_6_supply_candidate_count"] == 228
    assert per_length["0"]["initial_auxiliary_catalogue_searched_count"] == 0
    assert per_length["1"]["label_6_supply_candidate_count"] == 708
    assert per_length["1"]["initial_auxiliary_catalogue_searched_count"] == 14
    assert per_length["2"]["label_6_supply_candidate_count"] == 2072
    assert per_length["2"]["initial_auxiliary_catalogue_searched_count"] == 20
    assert per_length["3"]["label_6_supply_candidate_count"] == 6520
    assert per_length["3"]["initial_auxiliary_catalogue_searched_count"] == 24
    assert all(record["detected_solution_count"] == 0 for record in per_length.values())


def test_81_3_second_step_chains_source_prefixes(
    payload: dict[str, object],
) -> None:
    source_prefixes = payload["source_prefix_survivors"]

    assert len(source_prefixes) == 3
    assert {record["first_step_center"] for record in source_prefixes} == {8}
    assert {
        tuple(record["first_step_support"]) for record in source_prefixes
    } == {(0, 1, 4, 5), (0, 1, 4, 7)}
    assert {
        tuple(record["auxiliary_target_support"]) for record in source_prefixes
    } == {(1, 4, 6, 8), (0, 2, 4, 6), (1, 2, 4, 6)}

    chain_scan = payload["chain_scan"]
    assert chain_scan["survivors"] == []


def test_81_3_second_step_chains_artifact_matches_generator(
    payload: dict[str, object],
) -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == payload


def test_81_3_second_step_chains_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_second_step_chains.py",
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
    assert payload["summary"]["surviving_chain_count"] == 0


def test_81_3_second_step_chains_expected_payload_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["surviving_chain_count"] = 1

    with pytest.raises(AssertionError, match="surviving_chain_count"):
        assert_expected_payload(bad)
