from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle import (
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_151_6_outside_pair_full_neighborhood_vertex_circle_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_151_6_outside_pair_full_neighborhood_vertex_circle_payload()


def test_151_6_outside_pair_full_neighborhood_counts_and_scope(
    payload: dict[str, object],
) -> None:
    assert_expected_payload(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_151_6_OUTSIDE_PAIR_FULL_NEIGHBORHOOD_VERTEX_CIRCLE_"
        "DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "non-original row 6" in claim_scope
    assert "not a proof of outside-pair support existence" in claim_scope
    assert "not a proof of row forcing" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope


def test_151_6_outside_pair_full_neighborhood_summary(
    payload: dict[str, object],
) -> None:
    summary = payload["summary"]

    assert summary["target_row_key"] == "151:6"
    assert summary["source_record_ids"] == [151]
    assert summary["target_center"] == 6
    assert summary["bootstrap_core_witnesses"] == [0]
    assert summary["outside_support_pairs"] == [[3, 5], [3, 8], [5, 8]]
    assert summary["original_target_center_class"] == [0, 3, 5, 8]
    assert summary["target_center_candidate_count"] == 13
    assert summary["free_row_centers"] == [0, 1, 2, 3, 4, 5, 7, 8]
    assert summary["free_row_replacement_count_per_center"] == 70
    assert summary["implicit_assignment_space_size"] == 7_494_241_300_000_000
    assert summary["search_node_count"] == 13_439
    assert summary["empty_domain_count"] == 7_097
    assert summary["basic_filter_complete_assignment_count"] == 28
    assert summary["basic_filter_non_original_row6_assignment_count"] == 21
    assert summary["vertex_circle_status_counts"] == {
        "self_edge": 20,
        "strict_cycle": 8,
    }
    assert summary["vertex_circle_surviving_assignment_count"] == 0
    assert summary["non_original_vertex_circle_surviving_assignment_count"] == 0
    assert summary["scan_status"] == SCAN_STATUS


def test_151_6_outside_pair_full_neighborhood_target_breakdown(
    payload: dict[str, object],
) -> None:
    by_row = {
        tuple(record["target_center_class"]): record
        for record in payload["per_target_center_class"]
        if isinstance(record, dict)
    }

    assert by_row[(0, 3, 5, 7)]["basic_filter_complete_assignment_count"] == 12
    assert by_row[(0, 3, 5, 7)]["vertex_circle_status_counts"] == {
        "self_edge": 10,
        "strict_cycle": 2,
    }
    assert by_row[(0, 3, 5, 8)]["target_center_class_is_original"] is True
    assert by_row[(0, 3, 5, 8)]["basic_filter_complete_assignment_count"] == 7
    assert by_row[(0, 3, 5, 8)]["vertex_circle_status_counts"] == {
        "self_edge": 3,
        "strict_cycle": 4,
    }
    assert by_row[(0, 5, 7, 8)]["basic_filter_complete_assignment_count"] == 3
    assert by_row[(0, 5, 7, 8)]["vertex_circle_status_counts"] == {
        "self_edge": 3
    }


def test_151_6_outside_pair_full_neighborhood_survivors_are_obstructed(
    payload: dict[str, object],
) -> None:
    survivors = payload["basic_filter_survivors"]

    assert len(survivors) == 28
    assert sum(
        1 for survivor in survivors if not survivor["target_center_class_is_original"]
    ) == 21
    assert {survivor["vertex_circle_status"] for survivor in survivors} == {
        "self_edge",
        "strict_cycle",
    }
    for survivor in survivors:
        selected_rows = survivor["selected_rows"]
        assert set(selected_rows) == {str(center) for center in range(9)}
        assert all(len(row) == 4 for row in selected_rows.values())


def test_151_6_outside_pair_full_neighborhood_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.py",
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
    assert payload["summary"]["basic_filter_non_original_row6_assignment_count"] == 21
    assert payload["summary"]["vertex_circle_surviving_assignment_count"] == 0


def test_151_6_outside_pair_full_neighborhood_expected_payload_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["vertex_circle_surviving_assignment_count"] = 1

    with pytest.raises(AssertionError, match="vertex_circle_surviving_assignment_count"):
        assert_expected_payload(bad)
