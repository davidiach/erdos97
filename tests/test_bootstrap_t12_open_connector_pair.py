from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from erdos97.bootstrap_t12_open_connector_pair import (
    DEFAULT_ARTIFACT,
    GAP_SINGLETON_SPLIT_PAIR,
    assert_expected_payload,
    build_t12_open_connector_pair_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def _records(payload: dict[str, object]) -> dict[tuple[int, int], dict[str, object]]:
    return {
        (int(record["source_record_id"]), int(record["row_center"])): record
        for record in payload["records"]
    }


def test_open_connector_counts_and_scope() -> None:
    payload = build_t12_open_connector_pair_payload()
    assert_expected_payload(payload)
    assert payload["status"] == "BOOTSTRAP_T12_OPEN_CONNECTOR_PAIR_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "does not prove that the missing row or connector endpoints are forced" in claim_scope
    assert "does not prove n=9" in claim_scope
    assert payload["summary"]["open_connector_row_count"] == 1
    assert payload["summary"]["open_connector_requirement_ids"] == [
        "151:5:connector:1:0"
    ]


def test_open_connector_singleton_supports_split_pair() -> None:
    payload = build_t12_open_connector_pair_payload()
    row_5 = _records(payload)[(151, 5)]
    assert row_5["open_connector_gap_type"] == GAP_SINGLETON_SPLIT_PAIR
    assert row_5["required_witnesses"] == [7, 8]
    assert row_5["non_required_row_witnesses"] == [2, 4]
    assert row_5["missing_from_bootstrap_core"] == [7, 8]
    support_missing = {
        tuple(item["support"]): item["missing_required_witnesses"]
        for item in row_5["support_evaluations"]
    }
    assert support_missing == {(7,): [8], (8,): [7]}
    assert row_5["support_sufficient_count"] == 0
    assert row_5["partial_support_count"] == 2


def test_open_connector_partial_closure_negative_control() -> None:
    payload = build_t12_open_connector_pair_payload()
    row_5 = _records(payload)[(151, 5)]
    assert row_5["closure_sufficient_count"] == 0
    assert row_5["partial_closure_count"] == 1
    partial = row_5["partial_closures"][0]
    assert partial["core_vertex"] == 2
    assert partial["available_required_witnesses"] == [7]
    assert partial["missing_required_witnesses"] == [8]
    assert not partial["row_center_in_closure"]
    assert not partial["activation_ready_in_closure"]


def test_open_connector_support_packet_summary() -> None:
    payload = build_t12_open_connector_pair_payload()
    row_5 = _records(payload)[(151, 5)]
    assert row_5["support_packet_summary"] == {
        "ledger_private_pair_support_hit_count": 0,
        "private_halo_containment_counts": [3, 4],
        "support_label_modes": [
            "INTERNAL_TO_ONE_DELETION_CLOSURE",
            "PRIVATE_IN_ALL_DELETION_HALOS",
        ],
        "support_labels": [7, 8],
        "support_packet": "bootstrap_t12_one_outside",
    }


def test_open_connector_artifact_matches_generator() -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == build_t12_open_connector_pair_payload()


def test_open_connector_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_open_connector_pair.py",
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
    assert payload["summary"]["open_connector_requirement_ids"] == [
        "151:5:connector:1:0",
    ]


def test_open_connector_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "bootstrap_t12_open_connector_pair.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_open_connector_pair.py",
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
            "scripts/check_bootstrap_t12_open_connector_pair.py",
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
