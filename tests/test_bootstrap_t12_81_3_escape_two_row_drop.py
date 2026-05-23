from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_81_3_escape_candidates import (
    _base_selected_rows,
    _candidate_records,
)
from erdos97.bootstrap_t12_81_3_escape_two_row_drop import (
    DEFAULT_ARTIFACT,
    EXPECTED_PER_DROPPED_PAIR_REJECTION_COUNTS,
    EXPECTED_REJECTION_COUNTS,
    SCAN_STATUS,
    SUPPLY_CENTER,
    TARGET_ROW_CENTER,
    _row_mask,
    _scan_candidate_category,
    assert_expected_payload,
    build_t12_81_3_escape_two_row_drop_payload,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return build_t12_81_3_escape_two_row_drop_payload()


def test_81_3_two_row_drop_counts_and_scope(payload: dict[str, object]) -> None:
    assert_expected_payload(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_81_3_ESCAPE_TWO_ROW_DROP_SCAN_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "Two-row-drop" in claim_scope
    assert "All 4,116,000 candidates fail" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope


def test_81_3_two_row_drop_summary(payload: dict[str, object]) -> None:
    summary = payload["summary"]

    assert summary["target_row_key"] == "81:3"
    assert summary["source_record_ids"] == [81]
    assert summary["deletion_seed"] == [0, 1, 4]
    assert summary["connector_pair"] == [0, 1]
    assert summary["supply_center"] == 6
    assert summary["target_center"] == 3
    assert summary["two_row_drop_centers"] == [0, 1, 2, 4, 5, 7, 8]
    assert summary["also_replaced_row_centers"] == [3, 6]
    assert summary["center_6_supply_class_count"] == 5
    assert summary["center_3_connector_avoiding_class_count"] == 8
    assert summary["dropped_pair_count"] == 21
    assert summary["dropped_row_replacement_count_per_center"] == 70
    assert summary["candidate_count"] == 4116000
    assert summary["surviving_candidate_count"] == 0
    assert summary["rejection_category_counts"] == EXPECTED_REJECTION_COUNTS
    assert summary["scan_status"] == SCAN_STATUS


def test_81_3_two_row_drop_per_pair_counts(payload: dict[str, object]) -> None:
    per_dropped = payload["per_dropped_pair"]

    assert len(per_dropped) == 21
    for record in per_dropped:
        key = ",".join(str(center) for center in record["dropped_centers"])
        assert record["replacement_row_count_per_center"] == 70
        assert record["candidate_count"] == 196000
        assert record["surviving_candidate_count"] == 0
        assert (
            record["rejection_category_counts"]
            == EXPECTED_PER_DROPPED_PAIR_REJECTION_COUNTS[key]
        )


def test_81_3_two_row_drop_fast_filter_matches_reference_one_row_scan() -> None:
    base_rows = _base_selected_rows()
    records = _candidate_records(base_rows)

    for record in records:
        rows = [list(row) for row in base_rows]
        rows[SUPPLY_CENTER] = record["supply_class"]
        rows[TARGET_ROW_CENTER] = record["target_center_class"]
        category = _scan_candidate_category([_row_mask(row) for row in rows])
        assert category == record["rejection_category"]


def test_81_3_two_row_drop_artifact_matches_generator(
    payload: dict[str, object],
) -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == payload


def test_81_3_two_row_drop_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_escape_two_row_drop.py",
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
    assert payload["summary"]["surviving_candidate_count"] == 0


def test_81_3_two_row_drop_expected_payload_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["summary"]["surviving_candidate_count"] = 1

    with pytest.raises(AssertionError, match="surviving_candidate_count"):
        assert_expected_payload(bad)
