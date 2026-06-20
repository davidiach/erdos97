from __future__ import annotations

import json
import copy
import subprocess
import sys
from pathlib import Path

from scripts.check_n10_fast_cpp_singleton_replay import validate_payload


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_n10_fast_cpp_singleton_replay.py"
ARTIFACT = ROOT / "data" / "certificates" / "n10_fast_cpp_singleton_replay.json"
PRIMARY_ARTIFACT = ROOT / "data" / "certificates" / "n10_vertex_circle_singleton_slices.json"
CPP_SOURCE = ROOT / "cpp" / "n_vertex_search_fast.cpp"
EXPECTED_ROW_DIGEST = "64ebe12406c8777bcc7d7e2c5f1db3adb7703cbdba3898bb069bf964091b2fbb"


def test_n10_fast_cpp_replay_check() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--check", "--json"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    payload = json.loads(result.stdout)

    assert payload["ok"] is True
    assert payload["n9_calibration_ok"] is True
    assert payload["n10_rows_match_primary_artifact"] is True
    assert payload["n10_row0_choices_covered"] == 126
    assert payload["n10_total_full"] == 0
    assert payload["n10_total_nodes"] == 4_142_738
    assert payload["n10_row_summaries_digest_sha256"] == EXPECTED_ROW_DIGEST
    assert payload["solves_n10"] is False
    assert payload["solves_erdos97"] is False


def test_n10_fast_cpp_replay_scope_guardrails() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    claim_scope = artifact["claim_scope"]

    assert "does not prove n=10" in claim_scope
    assert "does not prove Erdos Problem #97" in claim_scope
    assert "does not claim a counterexample" in claim_scope
    assert "does not update the official/global status" in claim_scope
    assert artifact["review_independence"]["language"] == "C++17"
    assert artifact["review_independence"]["uses_repo_python_search"] is False


def test_n10_fast_cpp_replay_rejects_contradictory_validation_status() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    primary = json.loads(PRIMARY_ARTIFACT.read_text(encoding="utf-8"))
    tampered = copy.deepcopy(artifact)
    tampered["validation_status"] = "failed"
    tampered["validation_errors"] = ["synthetic failure"]

    errors = validate_payload(
        tampered,
        primary=primary,
        primary_path=PRIMARY_ARTIFACT,
        cpp_source=CPP_SOURCE,
    )

    assert "validation_status mismatch: expected 'passed', got 'failed'" in errors
    assert "validation_errors mismatch: expected [], got ['synthetic failure']" in errors


def test_n10_fast_cpp_replay_rejects_false_summary_match_flag() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    primary = json.loads(PRIMARY_ARTIFACT.read_text(encoding="utf-8"))
    tampered = copy.deepcopy(artifact)
    tampered["summary"]["n10_rows_match_primary_artifact"] = False

    errors = validate_payload(
        tampered,
        primary=primary,
        primary_path=PRIMARY_ARTIFACT,
        cpp_source=CPP_SOURCE,
    )

    assert (
        "summary.n10_rows_match_primary_artifact mismatch: expected True, got False"
        in errors
    )
