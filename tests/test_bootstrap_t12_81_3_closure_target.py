from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.bootstrap_t12_81_3_closure_target import (
    DEFAULT_ARTIFACT,
    ROW_FORCING_GAP,
    assert_expected_payload,
    build_t12_81_3_closure_target_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_81_3_closure_target_counts_and_scope() -> None:
    payload = build_t12_81_3_closure_target_payload()

    assert_expected_payload(payload)
    assert payload["status"] == "BOOTSTRAP_T12_81_3_CLOSURE_TARGET_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    claim_scope = str(payload["claim_scope"])
    assert "does not prove the row is forced" in claim_scope
    assert "does not prove n=9" in claim_scope
    assert "does not claim a counterexample" in claim_scope
    assert payload["summary"]["full_row_closure_relation_sufficient_targets"] == [
        "81:3"
    ]


def test_81_3_closure_target_isolates_full_row_exposure() -> None:
    payload = build_t12_81_3_closure_target_payload()
    target = payload["target_record"]

    assert target["target_row_key"] == "81:3"
    assert target["row_center"] == 3
    assert target["witnesses"] == [0, 1, 4, 6]
    assert target["deletion_seed"] == [0, 1, 4]
    assert target["exposed_core_vertex"] == 2
    assert target["closure_labels"] == [0, 1, 3, 4, 6]
    assert target["row_center_in_closure"]
    assert target["full_row_contained_in_exposure_closure"]
    assert target["witnesses_in_closure"] == [0, 1, 4, 6]
    assert target["outside_witnesses_in_closure"] == [6]
    assert target["outside_witnesses_private"] == []
    assert target["row_forcing_gap_type"] == ROW_FORCING_GAP


def test_81_3_closure_target_relation_requirement() -> None:
    payload = build_t12_81_3_closure_target_payload()
    requirement = payload["target_record"]["relation_requirement"]

    assert requirement["requirement_id"] == "81:3:connector:2:0"
    assert requirement["kind"] == "equality_connector_pair"
    assert requirement["required_witnesses"] == [0, 1]
    assert requirement["relation_state"] == "BOOTSTRAP_CORE_SUFFICIENT"
    assert requirement["bootstrap_core_status"] == "SUFFICIENT"
    assert requirement["closure_sufficient_count"] == 1
    assert requirement["support_sufficient_count"] == 0
    assert requirement["missing_from_bootstrap_core"] == []


def test_81_3_closure_target_t12_role_is_conditional() -> None:
    payload = build_t12_81_3_closure_target_payload()
    role = payload["target_record"]["t12_strict_cycle_role"]

    assert role["template_id"] == "T12"
    assert role["family_id"] == "F16"
    assert role["assignment_id"] == "A082"
    assert role["cycle_step"] == 2
    assert role["selected_row"] == [3, 0, 1, 4, 6]
    assert role["equality_step"] == {
        "row": 3,
        "left_pair": [1, 3],
        "right_pair": [0, 3],
    }
    assert role["connector_pair_chain"] == [[1, 3], [0, 3]]
    strict = role["strict_inequality_before_connector"]
    assert strict["row"] == 0
    assert strict["outer_pair"] == [1, 7]
    assert strict["inner_pair"] == [1, 3]
    assert "Conditional: if a future bridge proves" in role["conditional_use"]


def test_81_3_closure_target_artifact_matches_generator() -> None:
    checked_in = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
    assert checked_in == build_t12_81_3_closure_target_payload()


def test_81_3_closure_target_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_closure_target.py",
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
    assert payload["summary"]["target_row_key"] == "81:3"
    assert payload["summary"]["row_forcing_gap_type"] == ROW_FORCING_GAP


def test_81_3_closure_target_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "bootstrap_t12_81_3_closure_target.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/check_bootstrap_t12_81_3_closure_target.py",
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
            "scripts/check_bootstrap_t12_81_3_closure_target.py",
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


def test_81_3_closure_target_expected_payload_rejects_drift() -> None:
    payload = build_t12_81_3_closure_target_payload()
    bad = copy.deepcopy(payload)
    bad["summary"]["target_row_key"] = "81:8"

    with pytest.raises(AssertionError, match="target_row_key"):
        assert_expected_payload(bad)
