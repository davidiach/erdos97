from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from erdos97.bootstrap_t12_bridge_target_map import (
    DEFAULT_ARTIFACT,
    RELATION_HARD_STRICT,
    RELATION_OPEN_CONNECTOR,
    assert_expected_payload,
    build_t12_bridge_target_map_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def _records(payload: dict[str, object]) -> dict[tuple[int, int], dict[str, object]]:
    return {
        (int(record["source_record_id"]), int(record["row_center"])): record
        for record in payload["records"]
    }


def test_bridge_target_map_counts_and_scope() -> None:
    payload = build_t12_bridge_target_map_payload()
    assert_expected_payload(payload)
    assert payload["status"] == "BOOTSTRAP_T12_BRIDGE_TARGET_MAP_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "does not prove that the missing rows are forced" in claim_scope
    assert "does not prove n=9" in claim_scope
    assert payload["summary"]["row_target_count"] == 6
    assert payload["summary"]["requirement_count"] == 7


def test_bridge_target_map_marks_negative_controls() -> None:
    payload = build_t12_bridge_target_map_payload()
    records = _records(payload)
    assert records[(151, 7)]["row_target_status"] == (
        "CLOSURE_EXPOSED_HARD_STRICT_ENDPOINT"
    )
    assert records[(151, 7)]["support_packet_summary"]["witnesses_in_closure"] == [
        0,
        1,
        4,
    ]
    assert RELATION_HARD_STRICT in records[(151, 7)]["relation_state_counts"]
    assert records[(151, 8)]["row_target_status"] == (
        "MIXED_SINGLETON_CONNECTOR_AND_HARD_STRICT"
    )
    assert RELATION_HARD_STRICT in records[(151, 8)]["relation_state_counts"]


def test_bridge_target_map_separates_relation_status_from_row_activation() -> None:
    payload = build_t12_bridge_target_map_payload()
    records = _records(payload)
    assert records[(81, 8)]["row_target_status"] == (
        "CORE_CONNECTOR_WITH_SINGLETON_ROW_ACTIVATION"
    )
    assert records[(81, 8)]["relation_state_counts"] == {
        "BOOTSTRAP_CORE_SUFFICIENT": 1
    }
    assert records[(151, 5)]["row_target_status"] == (
        "SINGLETON_ROW_OPEN_CONNECTOR_PAIR"
    )
    assert RELATION_OPEN_CONNECTOR in records[(151, 5)]["relation_state_counts"]


def test_bridge_target_map_artifact_matches_generator() -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == build_t12_bridge_target_map_payload()


def test_bridge_target_map_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_bridge_target_map.py",
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
    assert payload["summary"]["bridge_target_status"] == "OPEN_TARGET_NOT_PROVED"


def test_bridge_target_map_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "bootstrap_t12_bridge_target_map.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_bridge_target_map.py",
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
            "scripts/check_bootstrap_t12_bridge_target_map.py",
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
