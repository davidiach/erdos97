from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_81_3_escape_candidates import (
    DEFAULT_ARTIFACT,
    EXPECTED_REJECTION_COUNTS,
    SCAN_STATUS,
    assert_expected_payload,
    build_t12_81_3_escape_candidate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_81_3_escape_candidate_scan_counts_and_scope() -> None:
    payload = build_t12_81_3_escape_candidate_payload()

    assert_expected_payload(payload)
    assert (
        payload["status"]
        == "BOOTSTRAP_T12_81_3_ESCAPE_CANDIDATE_SCAN_DIAGNOSTIC_ONLY"
    )
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "preserving the seven source-81 rows" in claim_scope
    assert "not a proof of n=9" in claim_scope
    assert "not a counterexample" in claim_scope


def test_81_3_escape_candidate_scan_summary() -> None:
    payload = build_t12_81_3_escape_candidate_payload()
    summary = payload["summary"]

    assert summary["target_row_key"] == "81:3"
    assert summary["source_record_ids"] == [81]
    assert summary["deletion_seed"] == [0, 1, 4]
    assert summary["connector_pair"] == [0, 1]
    assert summary["supply_center"] == 6
    assert summary["target_center"] == 3
    assert summary["preserved_row_centers"] == [0, 1, 2, 4, 5, 7, 8]
    assert summary["replaced_row_centers"] == [3, 6]
    assert summary["center_6_supply_class_count"] == 5
    assert summary["center_3_connector_avoiding_class_count"] == 8
    assert summary["candidate_count"] == 40
    assert summary["surviving_candidate_count"] == 0
    assert summary["rejection_category_counts"] == EXPECTED_REJECTION_COUNTS
    assert summary["scan_status"] == SCAN_STATUS


def test_81_3_escape_candidate_generation_space() -> None:
    payload = build_t12_81_3_escape_candidate_payload()
    generation = payload["candidate_generation"]

    assert generation["center_6_supply_classes"] == [
        [0, 1, 2, 4],
        [0, 1, 3, 4],
        [0, 1, 4, 5],
        [0, 1, 4, 7],
        [0, 1, 4, 8],
    ]
    assert generation["center_3_connector_avoiding_classes"] == [
        {"activation_triple": [0, 4, 6], "fourth": 2, "rich_class": [0, 2, 4, 6]},
        {"activation_triple": [0, 4, 6], "fourth": 5, "rich_class": [0, 4, 5, 6]},
        {"activation_triple": [0, 4, 6], "fourth": 7, "rich_class": [0, 4, 6, 7]},
        {"activation_triple": [0, 4, 6], "fourth": 8, "rich_class": [0, 4, 6, 8]},
        {"activation_triple": [1, 4, 6], "fourth": 2, "rich_class": [1, 2, 4, 6]},
        {"activation_triple": [1, 4, 6], "fourth": 5, "rich_class": [1, 4, 5, 6]},
        {"activation_triple": [1, 4, 6], "fourth": 7, "rich_class": [1, 4, 6, 7]},
        {"activation_triple": [1, 4, 6], "fourth": 8, "rich_class": [1, 4, 6, 8]},
    ]


def test_81_3_escape_candidate_records_have_no_survivors() -> None:
    payload = build_t12_81_3_escape_candidate_payload()

    assert payload["survivors"] == []
    candidates = payload["candidates"]
    assert len(candidates) == 40
    assert all(not candidate["passes_basic_incidence_crossing_filters"] for candidate in candidates)
    assert all(candidate["crossing_violations"] for candidate in candidates)
    assert any(candidate["row_pair_cap_violations"] for candidate in candidates)
    assert any(candidate["witness_pair_cap_violations"] for candidate in candidates)


def test_81_3_escape_candidate_artifact_matches_generator() -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == build_t12_81_3_escape_candidate_payload()


def test_81_3_escape_candidate_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_escape_candidates.py",
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


def test_81_3_escape_candidate_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "bootstrap_t12_81_3_escape_candidates.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_escape_candidates.py",
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
            "scripts/check_bootstrap_t12_81_3_escape_candidates.py",
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


def test_81_3_escape_candidate_expected_payload_rejects_drift() -> None:
    payload = build_t12_81_3_escape_candidate_payload()
    bad = copy.deepcopy(payload)
    bad["summary"]["surviving_candidate_count"] = 1

    with pytest.raises(AssertionError, match="surviving_candidate_count"):
        assert_expected_payload(bad)
