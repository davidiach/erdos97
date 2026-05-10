from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from erdos97.bootstrap_t12_hard_strict_endpoints import (
    DEFAULT_ARTIFACT,
    GAP_CLOSURE_MISSING_OUTSIDE,
    GAP_SPLIT_SINGLETON,
    assert_expected_payload,
    build_t12_hard_strict_endpoints_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def _records(payload: dict[str, object]) -> dict[tuple[int, int], dict[str, object]]:
    return {
        (int(record["source_record_id"]), int(record["row_center"])): record
        for record in payload["records"]
    }


def test_hard_strict_counts_and_scope() -> None:
    payload = build_t12_hard_strict_endpoints_payload()
    assert_expected_payload(payload)
    assert payload["status"] == "BOOTSTRAP_T12_HARD_STRICT_ENDPOINTS_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "does not prove that the missing rows or endpoints are forced" in claim_scope
    assert "does not prove n=9" in claim_scope
    assert payload["summary"]["hard_strict_row_count"] == 2


def test_hard_strict_closure_exposed_negative_control() -> None:
    payload = build_t12_hard_strict_endpoints_payload()
    row_7 = _records(payload)[(151, 7)]
    assert row_7["hard_strict_gap_type"] == GAP_CLOSURE_MISSING_OUTSIDE
    assert row_7["required_witnesses"] == [0, 1, 6]
    assert row_7["non_required_row_witnesses"] == [4]
    assert row_7["missing_from_bootstrap_core"] == [6]
    exposed = row_7["exposed_closure_evaluations"]
    assert len(exposed) == 1
    assert exposed[0]["available_required_witnesses"] == [0, 1]
    assert exposed[0]["missing_required_witnesses"] == [6]


def test_hard_strict_singleton_supports_split_endpoints() -> None:
    payload = build_t12_hard_strict_endpoints_payload()
    row_8 = _records(payload)[(151, 8)]
    assert row_8["hard_strict_gap_type"] == GAP_SPLIT_SINGLETON
    assert row_8["required_witnesses"] == [1, 5, 7]
    support_missing = {
        tuple(item["support"]): item["missing_required_witnesses"]
        for item in row_8["support_evaluations"]
    }
    assert support_missing == {(5,): [7], (7,): [5]}
    assert row_8["other_row_requirements"] == [
        {
            "requirement_id": "151:8:connector:1:1",
            "kind": "equality_connector_pair",
            "required_witnesses": [2, 5],
            "relation_state": "SUPPORT_SUFFICIENT",
            "missing_from_bootstrap_core": [5],
        }
    ]


def test_hard_strict_artifact_matches_generator() -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == build_t12_hard_strict_endpoints_payload()


def test_hard_strict_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_hard_strict_endpoints.py",
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
    assert payload["summary"]["hard_strict_requirement_ids"] == [
        "151:7:strict:0",
        "151:8:strict:1",
    ]


def test_hard_strict_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "bootstrap_t12_hard_strict_endpoints.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_hard_strict_endpoints.py",
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
            "scripts/check_bootstrap_t12_hard_strict_endpoints.py",
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
