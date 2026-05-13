from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_81_8_singleton_support_audit import (
    DEFAULT_ARTIFACT,
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_81_8_singleton_support_audit_payload,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_81_8_singleton_support_audit_payload()


def test_81_8_singleton_support_audit_counts_and_scope(
    payload: dict[str, object],
) -> None:
    assert_expected_payload(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_81_8_SINGLETON_SUPPORT_AUDIT_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "singleton-support audit" in claim_scope
    assert "does not prove singleton support existence" in claim_scope
    assert "does not prove n=9" in claim_scope
    assert "counterexample" in claim_scope


def test_81_8_singleton_support_audit_summary(
    payload: dict[str, object],
) -> None:
    summary = payload["summary"]

    assert summary["target_row_key"] == "81:8"
    assert summary["source_record_ids"] == [81]
    assert summary["target_center"] == 8
    assert summary["bootstrap_core_witnesses"] == [0, 2]
    assert summary["singleton_support_labels"] == [5, 6]
    assert summary["original_target_center_class"] == [0, 2, 5, 6]
    assert summary["target_center_candidate_count"] == 9
    assert summary["fixed_neighborhood_candidate_count"] == 9
    assert summary["fixed_neighborhood_surviving_candidate_count"] == 1
    assert summary["fixed_neighborhood_non_original_survivor_count"] == 0
    assert summary["one_row_drop_candidate_count"] == 5040
    assert summary["one_row_drop_surviving_candidate_count"] == 8
    assert summary["one_row_drop_non_original_row8_survivor_count"] == 0
    assert summary["one_row_drop_survivors_all_original_rows"] is True
    assert summary["scan_status"] == SCAN_STATUS


def test_81_8_singleton_support_candidate_generation(
    payload: dict[str, object],
) -> None:
    generation = payload["candidate_generation"]

    assert generation["target_center_candidate_classes"] == [
        [0, 1, 2, 5],
        [0, 1, 2, 6],
        [0, 2, 3, 5],
        [0, 2, 3, 6],
        [0, 2, 4, 5],
        [0, 2, 4, 6],
        [0, 2, 5, 6],
        [0, 2, 5, 7],
        [0, 2, 6, 7],
    ]


def test_81_8_singleton_support_fixed_scan(
    payload: dict[str, object],
) -> None:
    summary = payload["summary"]
    fixed = payload["fixed_neighborhood_candidates"]

    assert summary["fixed_neighborhood_rejection_category_counts"] == {
        "row_pair+witness_pair+crossing": 6,
        "survive": 1,
        "witness_pair+crossing": 2,
    }
    survivors = [
        record
        for record in fixed
        if record["passes_basic_incidence_crossing_filters"]
    ]
    assert len(survivors) == 1
    assert survivors[0]["target_center_class"] == [0, 2, 5, 6]
    assert survivors[0]["is_original_row"] is True


def test_81_8_singleton_support_one_row_drop_scan(
    payload: dict[str, object],
) -> None:
    summary = payload["summary"]
    one_row_drop = payload["one_row_drop"]

    assert summary["one_row_drop_rejection_category_counts"] == {
        "crossing": 47,
        "row_pair+crossing": 11,
        "row_pair+witness_pair": 36,
        "row_pair+witness_pair+crossing": 4692,
        "survive": 8,
        "witness_pair+crossing": 246,
    }
    survivors = one_row_drop["survivors"]
    assert len(survivors) == 8
    assert {survivor["dropped_center"] for survivor in survivors} == set(range(8))
    assert all(
        survivor["target_center_class"] == [0, 2, 5, 6]
        and survivor["target_center_class_is_original"]
        and survivor["dropped_center_class_is_original"]
        for survivor in survivors
    )


def test_81_8_singleton_support_artifact_matches_generator(
    payload: dict[str, object],
) -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == payload


def test_81_8_singleton_support_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_8_singleton_support_audit.py",
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
    assert payload["summary"]["one_row_drop_non_original_row8_survivor_count"] == 0


def test_81_8_singleton_support_expected_payload_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["one_row_drop_non_original_row8_survivor_count"] = 1

    with pytest.raises(AssertionError, match="non_original_row8_survivor_count"):
        assert_expected_payload(bad)
