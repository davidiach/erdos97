from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_151_6_outside_pair_two_row_drop import (
    DEFAULT_ARTIFACT,
    EXPECTED_REJECTION_COUNTS,
    SCAN_STATUS,
    assert_expected_payload,
    load_artifact,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return load_artifact(DEFAULT_ARTIFACT)


def test_151_6_outside_pair_two_row_drop_counts_and_scope(
    payload: dict[str, object],
) -> None:
    assert_expected_payload(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_151_6_OUTSIDE_PAIR_TWO_ROW_DROP_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "outside-pair stress test" in claim_scope
    assert "does not prove outside-pair support existence" in claim_scope
    assert "row forcing" in claim_scope
    assert "counterexample" in claim_scope


def test_151_6_outside_pair_two_row_drop_summary(
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
    assert summary["two_row_drop_centers"] == [0, 1, 2, 3, 4, 5, 7, 8]
    assert summary["two_row_drop_dropped_center_pair_count"] == 28
    assert summary["two_row_drop_replacement_count_per_center"] == 70
    assert summary["two_row_drop_candidate_count"] == 1_783_600
    assert summary["two_row_drop_surviving_candidate_count"] == 28
    assert summary["two_row_drop_non_original_survivor_count"] == 0
    assert summary["two_row_drop_survivors_all_original_rows"] is True
    assert summary["two_row_drop_rejection_category_counts"] == EXPECTED_REJECTION_COUNTS
    assert summary["scan_status"] == SCAN_STATUS


def test_151_6_outside_pair_two_row_drop_survivors_are_trivial(
    payload: dict[str, object],
) -> None:
    target_audit = payload["target_audit"]
    survivors = target_audit["two_row_drop_survivors"]

    assert len(survivors) == 28
    assert {
        tuple(survivor["dropped_centers"]) for survivor in survivors
    } == {
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        (0, 5),
        (0, 7),
        (0, 8),
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (1, 7),
        (1, 8),
        (2, 3),
        (2, 4),
        (2, 5),
        (2, 7),
        (2, 8),
        (3, 4),
        (3, 5),
        (3, 7),
        (3, 8),
        (4, 5),
        (4, 7),
        (4, 8),
        (5, 7),
        (5, 8),
        (7, 8),
    }
    assert all(
        survivor["target_center_class"] == [0, 3, 5, 8]
        and survivor["target_center_class_is_original"]
        and survivor["dropped_center_classes_are_original"] == [True, True]
        for survivor in survivors
    )


def test_151_6_outside_pair_two_row_drop_per_pair_table(
    payload: dict[str, object],
) -> None:
    target_audit = payload["target_audit"]
    per_pair = target_audit["two_row_drop_per_dropped_center_pair"]

    assert len(per_pair) == 28
    assert all(row["candidate_count"] == 63_700 for row in per_pair)
    assert all(row["surviving_candidate_count"] == 1 for row in per_pair)


def test_151_6_outside_pair_two_row_drop_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_151_6_outside_pair_two_row_drop.py",
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
    assert payload["summary"]["two_row_drop_non_original_survivor_count"] == 0


def test_151_6_outside_pair_two_row_drop_expected_payload_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["two_row_drop_non_original_survivor_count"] = 1

    with pytest.raises(AssertionError, match="non_original_survivor_count"):
        assert_expected_payload(bad)
