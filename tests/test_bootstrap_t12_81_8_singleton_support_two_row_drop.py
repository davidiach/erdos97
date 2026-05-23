from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_81_8_singleton_support_audit import (
    _base_selected_rows,
    _rejection_data,
    _target_row_candidates,
)
from erdos97.bootstrap_t12_81_8_singleton_support_two_row_drop import (
    DEFAULT_ARTIFACT,
    EXPECTED_PER_DROPPED_PAIR_REJECTION_COUNTS,
    EXPECTED_REJECTION_COUNTS,
    SCAN_STATUS,
    TARGET_ROW_CENTER,
    _row_mask,
    _scan_candidate_category,
    assert_expected_payload,
    build_t12_81_8_singleton_support_two_row_drop_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_81_8_singleton_support_two_row_drop_payload()


def test_81_8_two_row_drop_counts_and_scope(payload: dict[str, object]) -> None:
    assert_expected_payload(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_81_8_SINGLETON_SUPPORT_TWO_ROW_DROP_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "Two-row-drop" in claim_scope
    assert "only 28 survivors" in claim_scope
    assert "does not prove singleton support existence" in claim_scope
    assert "Erdos Problem #97" in claim_scope
    assert "not a counterexample" in claim_scope


def test_81_8_two_row_drop_summary(payload: dict[str, object]) -> None:
    summary = payload["summary"]

    assert summary["target_row_key"] == "81:8"
    assert summary["source_record_ids"] == [81]
    assert summary["target_center"] == 8
    assert summary["bootstrap_core_witnesses"] == [0, 2]
    assert summary["singleton_support_labels"] == [5, 6]
    assert summary["original_target_center_class"] == [0, 2, 5, 6]
    assert summary["target_center_candidate_count"] == 9
    assert summary["two_row_drop_centers"] == list(range(8))
    assert summary["dropped_pair_count"] == 28
    assert summary["dropped_row_replacement_count_per_center"] == 70
    assert summary["candidate_count"] == 1234800
    assert summary["surviving_candidate_count"] == 28
    assert summary["two_row_drop_non_original_survivor_count"] == 0
    assert summary["two_row_drop_survivors_all_original_rows"] is True
    assert summary["rejection_category_counts"] == EXPECTED_REJECTION_COUNTS
    assert summary["scan_status"] == SCAN_STATUS


def test_81_8_two_row_drop_per_pair_counts(payload: dict[str, object]) -> None:
    per_dropped = payload["per_dropped_pair"]

    assert len(per_dropped) == 28
    for record in per_dropped:
        key = ",".join(str(center) for center in record["dropped_centers"])
        assert record["replacement_row_count_per_center"] == 70
        assert record["candidate_count"] == 44100
        assert record["surviving_candidate_count"] == 1
        assert (
            record["rejection_category_counts"]
            == EXPECTED_PER_DROPPED_PAIR_REJECTION_COUNTS[key]
        )


def test_81_8_two_row_drop_survivors_are_original(
    payload: dict[str, object],
) -> None:
    survivors = payload["survivors"]

    assert len(survivors) == 28
    assert {
        tuple(survivor["dropped_centers"]) for survivor in survivors
    } == set(__import__("itertools").combinations(range(8), 2))
    assert all(
        survivor["target_center_class"] == [0, 2, 5, 6]
        and survivor["target_center_class_is_original"]
        and survivor["dropped_center_classes_are_original"]
        for survivor in survivors
    )


def test_81_8_two_row_drop_fast_filter_matches_reference_fixed_scan() -> None:
    base_rows = _base_selected_rows()

    for target_row in _target_row_candidates():
        rows = [list(row) for row in base_rows]
        rows[TARGET_ROW_CENTER] = list(target_row)
        category = _scan_candidate_category([_row_mask(row) for row in rows])
        reference = _rejection_data(rows)["rejection_category"]
        assert category == reference


def test_81_8_two_row_drop_artifact_matches_generator(
    payload: dict[str, object],
) -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == payload


def test_81_8_two_row_drop_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_8_singleton_support_two_row_drop.py",
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


def test_81_8_two_row_drop_expected_payload_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["two_row_drop_non_original_survivor_count"] = 1

    with pytest.raises(AssertionError, match="non_original_survivor_count"):
        assert_expected_payload(bad)
