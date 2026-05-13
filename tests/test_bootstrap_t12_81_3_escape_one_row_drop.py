from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_81_3_escape_one_row_drop import (
    DEFAULT_ARTIFACT,
    EXPECTED_PER_DROPPED_REJECTION_COUNTS,
    EXPECTED_REJECTION_COUNTS,
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_81_3_escape_one_row_drop_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_81_3_one_row_drop_counts_and_scope() -> None:
    payload = build_t12_81_3_escape_one_row_drop_payload()

    assert_expected_payload(payload)
    assert payload["status"] == (
        "BOOTSTRAP_T12_81_3_ESCAPE_ONE_ROW_DROP_SCAN_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "one row" in claim_scope
    assert "All 19,600 candidates fail" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope


def test_81_3_one_row_drop_summary() -> None:
    payload = build_t12_81_3_escape_one_row_drop_payload()
    summary = payload["summary"]

    assert summary["target_row_key"] == "81:3"
    assert summary["source_record_ids"] == [81]
    assert summary["deletion_seed"] == [0, 1, 4]
    assert summary["connector_pair"] == [0, 1]
    assert summary["supply_center"] == 6
    assert summary["target_center"] == 3
    assert summary["one_row_drop_centers"] == [0, 1, 2, 4, 5, 7, 8]
    assert summary["also_replaced_row_centers"] == [3, 6]
    assert summary["center_6_supply_class_count"] == 5
    assert summary["center_3_connector_avoiding_class_count"] == 8
    assert summary["dropped_row_replacement_count_per_center"] == 70
    assert summary["dropped_center_count"] == 7
    assert summary["candidate_count"] == 19600
    assert summary["surviving_candidate_count"] == 0
    assert summary["rejection_category_counts"] == EXPECTED_REJECTION_COUNTS
    assert summary["scan_status"] == SCAN_STATUS


def test_81_3_one_row_drop_per_center_counts() -> None:
    payload = build_t12_81_3_escape_one_row_drop_payload()
    per_dropped = payload["per_dropped_center"]

    assert len(per_dropped) == 7
    for record in per_dropped:
        center = record["dropped_center"]
        assert record["replacement_row_count"] == 70
        assert record["candidate_count"] == 2800
        assert record["surviving_candidate_count"] == 0
        assert (
            record["rejection_category_counts"]
            == EXPECTED_PER_DROPPED_REJECTION_COUNTS[center]
        )


def test_81_3_one_row_drop_generation_space() -> None:
    payload = build_t12_81_3_escape_one_row_drop_payload()
    generation = payload["candidate_generation"]

    assert generation["center_6_supply_classes"] == [
        [0, 1, 2, 4],
        [0, 1, 3, 4],
        [0, 1, 4, 5],
        [0, 1, 4, 7],
        [0, 1, 4, 8],
    ]
    assert generation["dropped_row_choice_count_per_center"] == {
        "0": 70,
        "1": 70,
        "2": 70,
        "4": 70,
        "5": 70,
        "7": 70,
        "8": 70,
    }


def test_81_3_one_row_drop_artifact_matches_generator() -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == build_t12_81_3_escape_one_row_drop_payload()


def test_81_3_one_row_drop_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_escape_one_row_drop.py",
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


def test_81_3_one_row_drop_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "bootstrap_t12_81_3_escape_one_row_drop.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_escape_one_row_drop.py",
            "--write",
            "--assert-expected",
            "--artifact",
            str(out),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_escape_one_row_drop.py",
            "--check",
            "--assert-expected",
            "--artifact",
            str(out),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )


def test_81_3_one_row_drop_expected_payload_rejects_drift() -> None:
    payload = build_t12_81_3_escape_one_row_drop_payload()
    bad = copy.deepcopy(payload)
    bad["summary"]["surviving_candidate_count"] = 1

    with pytest.raises(AssertionError, match="surviving_candidate_count"):
        assert_expected_payload(bad)
