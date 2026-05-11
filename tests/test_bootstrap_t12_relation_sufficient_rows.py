from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from erdos97.bootstrap_t12_bridge_target_map import (
    RELATION_BOOTSTRAP_CORE,
    RELATION_SUPPORT,
)
from erdos97.bootstrap_t12_relation_sufficient_rows import (
    DEFAULT_ARTIFACT,
    GAP_FULL_ROW_CLOSURE,
    GAP_OUTSIDE_PAIR_SUPPORT,
    GAP_SINGLETON_ACTIVATION,
    assert_expected_payload,
    build_t12_relation_sufficient_rows_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def _records(payload: dict[str, object]) -> dict[tuple[int, int], dict[str, object]]:
    return {
        (int(record["source_record_id"]), int(record["row_center"])): record
        for record in payload["records"]
    }


def test_relation_sufficient_counts_and_scope() -> None:
    payload = build_t12_relation_sufficient_rows_payload()
    assert_expected_payload(payload)
    assert payload["status"] == "BOOTSTRAP_T12_RELATION_SUFFICIENT_ROWS_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "row/rich-class forcing remains an open bridge target" in claim_scope
    assert "does not prove that the missing rows are forced" in claim_scope
    assert "does not prove n=9" in claim_scope
    assert payload["summary"]["relation_sufficient_row_count"] == 3
    assert payload["summary"]["excluded_hard_or_open_rows"] == [
        "151:5",
        "151:7",
        "151:8",
    ]


def test_relation_sufficient_full_row_closure_gap() -> None:
    payload = build_t12_relation_sufficient_rows_payload()
    row_81_3 = _records(payload)[(81, 3)]
    assert row_81_3["row_forcing_gap_type"] == GAP_FULL_ROW_CLOSURE
    assert row_81_3["row_target_status"] == "CLOSURE_FULL_ROW_CONNECTOR"
    assert row_81_3["support_packet_summary"]["support_packet"] == (
        "bootstrap_t12_closure_exposed"
    )
    assert row_81_3["support_packet_summary"][
        "full_row_contained_in_exposure_closure"
    ]
    requirement = row_81_3["relation_sufficient_requirements"][0]
    assert requirement["requirement_id"] == "81:3:connector:2:0"
    assert requirement["relation_state"] == RELATION_BOOTSTRAP_CORE
    assert requirement["required_witnesses"] == [0, 1]
    assert requirement["closure_sufficient_count"] == 1


def test_relation_sufficient_singleton_activation_gap() -> None:
    payload = build_t12_relation_sufficient_rows_payload()
    row_81_8 = _records(payload)[(81, 8)]
    assert row_81_8["row_forcing_gap_type"] == GAP_SINGLETON_ACTIVATION
    assert row_81_8["row_target_status"] == (
        "CORE_CONNECTOR_WITH_SINGLETON_ROW_ACTIVATION"
    )
    assert row_81_8["row_center_private_in_all_deletion_closures"]
    assert row_81_8["support_packet_summary"]["support_labels"] == [5, 6]
    assert row_81_8["support_packet_summary"]["private_halo_containment_counts"] == [
        4,
        3,
    ]
    requirement = row_81_8["relation_sufficient_requirements"][0]
    assert requirement["requirement_id"] == "81:8:connector:0:0"
    assert requirement["relation_state"] == RELATION_BOOTSTRAP_CORE
    assert requirement["support_sufficient_count"] == 2
    assert requirement["missing_from_bootstrap_core"] == []


def test_relation_sufficient_outside_pair_support_gap() -> None:
    payload = build_t12_relation_sufficient_rows_payload()
    row_151_6 = _records(payload)[(151, 6)]
    assert row_151_6["row_forcing_gap_type"] == GAP_OUTSIDE_PAIR_SUPPORT
    assert row_151_6["row_target_status"] == "OUTSIDE_PAIR_CONNECTOR_PARTIAL_LEDGER"
    assert row_151_6["support_packet_summary"]["support_packet"] == (
        "bootstrap_t12_outside_pair"
    )
    assert row_151_6["support_packet_summary"]["ledger_hit_support_pairs"] == [
        [3, 8],
        [5, 8],
    ]
    assert row_151_6["support_packet_summary"]["ledger_miss_support_pairs"] == [
        [3, 5],
    ]
    requirement = row_151_6["relation_sufficient_requirements"][0]
    assert requirement["requirement_id"] == "151:6:connector:2:0"
    assert requirement["relation_state"] == RELATION_SUPPORT
    assert requirement["required_witnesses"] == [0, 8]
    assert requirement["missing_from_bootstrap_core"] == [8]
    assert requirement["support_sufficient_count"] == 2


def test_relation_sufficient_artifact_matches_generator() -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == build_t12_relation_sufficient_rows_payload()


def test_relation_sufficient_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_relation_sufficient_rows.py",
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
    assert payload["summary"]["relation_sufficient_requirement_ids"] == [
        "81:3:connector:2:0",
        "81:8:connector:0:0",
        "151:6:connector:2:0",
    ]


def test_relation_sufficient_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "bootstrap_t12_relation_sufficient_rows.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_relation_sufficient_rows.py",
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
            "scripts/check_bootstrap_t12_relation_sufficient_rows.py",
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
