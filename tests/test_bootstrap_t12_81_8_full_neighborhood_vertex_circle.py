from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_81_8_full_neighborhood_vertex_circle import (
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_81_8_full_neighborhood_vertex_circle_payload,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_81_8_full_neighborhood_vertex_circle_payload()


def test_81_8_full_neighborhood_counts_and_scope(payload: dict[str, object]) -> None:
    assert_expected_payload(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_81_8_FULL_NEIGHBORHOOD_VERTEX_CIRCLE_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "non-original row 8" in claim_scope
    assert "not a proof of row forcing" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope


def test_81_8_full_neighborhood_summary(payload: dict[str, object]) -> None:
    summary = payload["summary"]

    assert summary["target_row_key"] == "81:8"
    assert summary["source_record_ids"] == [81]
    assert summary["target_center"] == 8
    assert summary["bootstrap_core_witnesses"] == [0, 2]
    assert summary["singleton_support_labels"] == [5, 6]
    assert summary["original_target_center_class"] == [0, 2, 5, 6]
    assert summary["target_center_candidate_count"] == 9
    assert summary["free_row_centers"] == list(range(8))
    assert summary["free_row_replacement_count_per_center"] == 70
    assert summary["implicit_assignment_space_size"] == 5_188_320_900_000_000
    assert summary["search_node_count"] == 16_010
    assert summary["empty_domain_count"] == 8_436
    assert summary["basic_filter_complete_assignment_count"] == 34
    assert summary["basic_filter_non_original_row8_assignment_count"] == 27
    assert summary["vertex_circle_status_counts"] == {
        "self_edge": 27,
        "strict_cycle": 7,
    }
    assert summary["vertex_circle_surviving_assignment_count"] == 0
    assert summary["non_original_vertex_circle_surviving_assignment_count"] == 0
    assert summary["scan_status"] == SCAN_STATUS


def test_81_8_full_neighborhood_per_target_boundary(
    payload: dict[str, object],
) -> None:
    per_target = payload["per_target_center_class"]
    by_target = {
        tuple(record["target_center_class"]): record for record in per_target
    }

    zero_basic_survivor_rows = {
        (0, 1, 2, 5),
        (0, 1, 2, 6),
        (0, 2, 3, 5),
        (0, 2, 3, 6),
        (0, 2, 4, 5),
    }
    for row in zero_basic_survivor_rows:
        assert by_target[row]["basic_filter_complete_assignment_count"] == 0
        assert by_target[row]["vertex_circle_status_counts"] == {}

    assert by_target[(0, 2, 4, 6)]["vertex_circle_status_counts"] == {
        "self_edge": 4,
        "strict_cycle": 1,
    }
    assert by_target[(0, 2, 5, 6)]["vertex_circle_status_counts"] == {
        "self_edge": 3,
        "strict_cycle": 4,
    }
    assert by_target[(0, 2, 5, 7)]["vertex_circle_status_counts"] == {
        "self_edge": 10,
        "strict_cycle": 2,
    }
    assert by_target[(0, 2, 6, 7)]["vertex_circle_status_counts"] == {
        "self_edge": 10,
    }


def test_81_8_full_neighborhood_survivors_are_obstructed(
    payload: dict[str, object],
) -> None:
    survivors = payload["basic_filter_survivors"]

    assert len(survivors) == 34
    assert sum(
        1 for survivor in survivors if not survivor["target_center_class_is_original"]
    ) == 27
    assert {survivor["vertex_circle_status"] for survivor in survivors} == {
        "self_edge",
        "strict_cycle",
    }
    for survivor in survivors:
        selected_rows = survivor["selected_rows"]
        assert set(selected_rows) == {str(center) for center in range(9)}
        assert all(len(row) == 4 for row in selected_rows.values())


def test_81_8_full_neighborhood_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_8_full_neighborhood_vertex_circle.py",
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
    assert payload["summary"]["basic_filter_non_original_row8_assignment_count"] == 27
    assert payload["summary"]["vertex_circle_surviving_assignment_count"] == 0


def test_81_8_full_neighborhood_expected_payload_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["vertex_circle_surviving_assignment_count"] = 1

    with pytest.raises(AssertionError, match="vertex_circle_surviving_assignment_count"):
        assert_expected_payload(bad)
