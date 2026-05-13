from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_151_singleton_support_audit import (
    DEFAULT_ARTIFACT,
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_151_singleton_support_audit_payload,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_151_singleton_support_audit_payload()


def test_151_singleton_support_audit_counts_and_scope(
    payload: dict[str, object],
) -> None:
    assert_expected_payload(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_151_SINGLETON_SUPPORT_AUDIT_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "singleton-support audit" in claim_scope
    assert "does not prove singleton support existence" in claim_scope
    assert "does not prove n=9" in claim_scope
    assert "counterexample" in claim_scope


def test_151_singleton_support_audit_summary(payload: dict[str, object]) -> None:
    summary = payload["summary"]

    assert summary["source_record_ids"] == [151]
    assert summary["target_row_keys"] == ["151:5", "151:8"]
    assert summary["target_centers"] == [5, 8]
    assert summary["target_count"] == 2
    assert summary["target_center_candidate_count_by_key"] == {
        "151:5": 9,
        "151:8": 9,
    }
    assert summary["fixed_neighborhood_candidate_count"] == 18
    assert summary["fixed_neighborhood_surviving_candidate_count"] == 2
    assert summary["fixed_neighborhood_non_original_survivor_count"] == 0
    assert summary["one_row_drop_candidate_count"] == 10080
    assert summary["one_row_drop_surviving_candidate_count"] == 16
    assert summary["one_row_drop_non_original_target_row_survivor_count"] == 0
    assert summary["one_row_drop_survivors_all_original_rows"] is True
    assert summary["scan_status"] == SCAN_STATUS


def test_151_singleton_support_audit_target_details(
    payload: dict[str, object],
) -> None:
    records = {
        record["target_row_key"]: record for record in payload["target_audits"]
    }

    assert records["151:5"]["bootstrap_core_witnesses"] == [2, 4]
    assert records["151:5"]["singleton_support_labels"] == [7, 8]
    assert records["151:5"]["original_target_center_class"] == [2, 4, 7, 8]
    assert records["151:5"]["target_center_candidate_classes"] == [
        [0, 2, 4, 7],
        [0, 2, 4, 8],
        [1, 2, 4, 7],
        [1, 2, 4, 8],
        [2, 3, 4, 7],
        [2, 3, 4, 8],
        [2, 4, 6, 7],
        [2, 4, 6, 8],
        [2, 4, 7, 8],
    ]

    assert records["151:8"]["bootstrap_core_witnesses"] == [1, 2]
    assert records["151:8"]["singleton_support_labels"] == [5, 7]
    assert records["151:8"]["original_target_center_class"] == [1, 2, 5, 7]
    assert records["151:8"]["target_center_candidate_classes"] == [
        [0, 1, 2, 5],
        [0, 1, 2, 7],
        [1, 2, 3, 5],
        [1, 2, 3, 7],
        [1, 2, 4, 5],
        [1, 2, 4, 7],
        [1, 2, 5, 6],
        [1, 2, 5, 7],
        [1, 2, 6, 7],
    ]


def test_151_singleton_support_audit_rejection_counts(
    payload: dict[str, object],
) -> None:
    records = {
        record["target_row_key"]: record for record in payload["target_audits"]
    }

    assert records["151:5"]["fixed_neighborhood_rejection_category_counts"] == {
        "row_pair+witness_pair+crossing": 6,
        "survive": 1,
        "witness_pair+crossing": 2,
    }
    assert records["151:5"]["one_row_drop_rejection_category_counts"] == {
        "crossing": 47,
        "row_pair+crossing": 11,
        "row_pair+witness_pair": 36,
        "row_pair+witness_pair+crossing": 4692,
        "survive": 8,
        "witness_pair+crossing": 246,
    }

    assert records["151:8"]["fixed_neighborhood_rejection_category_counts"] == {
        "crossing": 2,
        "row_pair+witness_pair+crossing": 6,
        "survive": 1,
    }
    assert records["151:8"]["one_row_drop_rejection_category_counts"] == {
        "crossing": 105,
        "row_pair+crossing": 11,
        "row_pair+witness_pair": 32,
        "row_pair+witness_pair+crossing": 4704,
        "survive": 8,
        "witness_pair+crossing": 180,
    }


def test_151_singleton_support_audit_survivors_are_original(
    payload: dict[str, object],
) -> None:
    for record in payload["target_audits"]:
        fixed_survivors = [
            candidate
            for candidate in record["fixed_neighborhood_candidates"]
            if candidate["passes_basic_incidence_crossing_filters"]
        ]
        assert len(fixed_survivors) == 1
        assert fixed_survivors[0]["is_original_row"] is True

        survivors = record["one_row_drop"]["survivors"]
        assert len(survivors) == 8
        assert all(
            survivor["target_center_class_is_original"]
            and survivor["dropped_center_class_is_original"]
            for survivor in survivors
        )


def test_151_singleton_support_artifact_matches_generator(
    payload: dict[str, object],
) -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == payload


def test_151_singleton_support_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_singleton_support_audit.py",
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
    assert (
        payload["summary"]["one_row_drop_non_original_target_row_survivor_count"]
        == 0
    )


def test_151_singleton_support_expected_payload_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["one_row_drop_non_original_target_row_survivor_count"] = 1

    with pytest.raises(
        AssertionError,
        match="one_row_drop_non_original_target_row_survivor_count",
    ):
        assert_expected_payload(bad)
