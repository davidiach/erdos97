from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_151_singleton_full_neighborhood_vertex_circle import (
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_151_singleton_full_neighborhood_vertex_circle_payload,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_151_singleton_full_neighborhood_vertex_circle_payload()


def test_source151_full_neighborhood_counts_and_scope(
    payload: dict[str, object],
) -> None:
    assert_expected_payload(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_151_SINGLETON_FULL_NEIGHBORHOOD_VERTEX_CIRCLE_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "non-original target rows" in claim_scope
    assert "not a proof of row forcing" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope


def test_source151_full_neighborhood_summary(payload: dict[str, object]) -> None:
    summary = payload["summary"]

    assert summary["target_row_keys"] == ["151:5", "151:8"]
    assert summary["source_record_ids"] == [151]
    assert summary["target_centers"] == [5, 8]
    assert summary["target_center_candidate_count_by_key"] == {"151:5": 9, "151:8": 9}
    assert summary["free_row_replacement_count_per_center"] == 70
    assert summary["implicit_assignment_space_size_per_target"] == 5_188_320_900_000_000
    assert summary["implicit_assignment_space_size"] == 10_376_641_800_000_000
    assert summary["search_node_count"] == 22_709
    assert summary["empty_domain_count"] == 11_959
    assert summary["basic_filter_complete_assignment_count"] == 50
    assert summary["basic_filter_non_original_target_assignment_count"] == 36
    assert summary["vertex_circle_status_counts"] == {
        "self_edge": 37,
        "strict_cycle": 13,
    }
    assert summary["vertex_circle_surviving_assignment_count"] == 0
    assert summary["non_original_vertex_circle_surviving_assignment_count"] == 0
    assert summary["scan_status"] == SCAN_STATUS


def test_source151_full_neighborhood_target_breakdown(
    payload: dict[str, object],
) -> None:
    by_key = {
        record["target_row_key"]: record
        for record in payload["target_audits"]
        if isinstance(record, dict)
    }

    assert by_key["151:5"]["search_node_count"] == 15_674
    assert by_key["151:5"]["basic_filter_complete_assignment_count"] == 34
    assert by_key["151:5"]["non_original_target_basic_assignment_count"] == 27
    assert by_key["151:5"]["vertex_circle_status_counts"] == {
        "self_edge": 27,
        "strict_cycle": 7,
    }

    assert by_key["151:8"]["search_node_count"] == 7_035
    assert by_key["151:8"]["basic_filter_complete_assignment_count"] == 16
    assert by_key["151:8"]["non_original_target_basic_assignment_count"] == 9
    assert by_key["151:8"]["vertex_circle_status_counts"] == {
        "self_edge": 10,
        "strict_cycle": 6,
    }


def test_source151_full_neighborhood_survivors_are_obstructed(
    payload: dict[str, object],
) -> None:
    survivors = [
        survivor
        for record in payload["target_audits"]
        if isinstance(record, dict)
        for survivor in record["basic_filter_survivors"]
    ]

    assert len(survivors) == 50
    assert sum(
        1 for survivor in survivors if not survivor["target_center_class_is_original"]
    ) == 36
    assert {survivor["vertex_circle_status"] for survivor in survivors} == {
        "self_edge",
        "strict_cycle",
    }
    for survivor in survivors:
        selected_rows = survivor["selected_rows"]
        assert set(selected_rows) == {str(center) for center in range(9)}
        assert all(len(row) == 4 for row in selected_rows.values())


def test_source151_full_neighborhood_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.py",
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
    assert payload["summary"]["basic_filter_non_original_target_assignment_count"] == 36
    assert payload["summary"]["vertex_circle_surviving_assignment_count"] == 0


def test_source151_full_neighborhood_expected_payload_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["vertex_circle_surviving_assignment_count"] = 1

    with pytest.raises(AssertionError, match="vertex_circle_surviving_assignment_count"):
        assert_expected_payload(bad)
