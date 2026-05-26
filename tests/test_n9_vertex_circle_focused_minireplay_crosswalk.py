from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_focused_minireplay_crosswalk import (
    CLAIM_SCOPE,
    DEFAULT_MINIREPLAY_PATHS,
    assert_expected_focused_minireplay_crosswalk,
    focused_minireplay_crosswalk_payload,
    load_json,
)

ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_focused_minireplay_crosswalk_counts_and_scope() -> None:
    payload = focused_minireplay_crosswalk_payload()

    assert_expected_focused_minireplay_crosswalk(payload)
    summary = payload["focused_minireplay_crosswalk"]
    assert payload["validation_status"] == "passed"
    assert payload["status"] == "REVIEW_PENDING_FOCUSED_MINIREPLAY_CROSSWALK"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "bookkeeping only" in payload["interpretation"]
    assert "does not prove mini-replay soundness" in payload["claim_scope"]
    assert "counterexample" in payload["claim_scope"]
    assert "official/global status update" in payload["claim_scope"]
    assert summary["template_ids"] == [f"T{index:02d}" for index in range(1, 13)]
    assert summary["status_counts"] == {"self_edge": 9, "strict_cycle": 3}
    assert summary["status_assignment_counts"] == {"self_edge": 158, "strict_cycle": 26}
    assert summary["source_assignment_count"] == 184
    assert summary["source_family_count"] == 16
    assert summary["obstruction_flagged_count"] == 12
    assert summary["assignment_count_repeated_total"] == 184
    assert summary["assignment_count_source_only_total"] == 0


def test_focused_minireplay_crosswalk_rejects_top_level_claim_scope_append() -> None:
    payload = focused_minireplay_crosswalk_payload()
    payload["claim_scope"] = CLAIM_SCOPE + " This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_focused_minireplay_crosswalk(payload)


def test_focused_minireplay_crosswalk_rejects_source_packet_drift(
    tmp_path: Path,
) -> None:
    t09_path = tmp_path / "t09_minireplay.json"
    t09_minireplay = load_json(DEFAULT_MINIREPLAY_PATHS["T09"])
    t09_minireplay["source_packet"] = (
        "data/certificates/n9_vertex_circle_t08_self_edge_lemma_packet.json"
    )
    _write_json(t09_path, t09_minireplay)
    minireplay_paths = dict(DEFAULT_MINIREPLAY_PATHS)
    minireplay_paths["T09"] = t09_path

    payload = focused_minireplay_crosswalk_payload(minireplay_paths=minireplay_paths)

    assert payload["validation_status"] == "failed"
    assert "T09: mini-replay source_packet mismatch" in payload["validation_errors"]
    summary = payload["focused_minireplay_crosswalk"]
    assert summary["source_packet_mismatch_count"] == 1


def test_focused_minireplay_crosswalk_rejects_family_drift(
    tmp_path: Path,
) -> None:
    t02_path = tmp_path / "t02_minireplay.json"
    t02_minireplay = load_json(DEFAULT_MINIREPLAY_PATHS["T02"])
    t02_minireplay["replay"]["family_ids"] = ["F01", "F04", "F08"]
    _write_json(t02_path, t02_minireplay)
    minireplay_paths = dict(DEFAULT_MINIREPLAY_PATHS)
    minireplay_paths["T02"] = t02_path

    payload = focused_minireplay_crosswalk_payload(minireplay_paths=minireplay_paths)

    assert payload["validation_status"] == "failed"
    assert "T02: mini-replay family ids mismatch" in payload["validation_errors"]
    summary = payload["focused_minireplay_crosswalk"]
    assert summary["family_mismatch_count"] == 1


def test_focused_minireplay_crosswalk_rejects_obstruction_flag_drift(
    tmp_path: Path,
) -> None:
    t10_path = tmp_path / "t10_minireplay.json"
    t10_minireplay = load_json(DEFAULT_MINIREPLAY_PATHS["T10"])
    t10_minireplay["replay"]["strict_cycle_contradiction"] = False
    _write_json(t10_path, t10_minireplay)
    minireplay_paths = dict(DEFAULT_MINIREPLAY_PATHS)
    minireplay_paths["T10"] = t10_path

    payload = focused_minireplay_crosswalk_payload(minireplay_paths=minireplay_paths)

    assert payload["validation_status"] == "failed"
    assert "T10: mini-replay obstruction flag mismatch" in payload["validation_errors"]
    summary = payload["focused_minireplay_crosswalk"]
    assert summary["obstruction_flag_mismatch_count"] == 1


def test_focused_minireplay_crosswalk_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    parsed = json.loads(result.stdout)
    assert parsed["validation_status"] == "passed"
    summary = parsed["focused_minireplay_crosswalk"]
    assert summary["source_assignment_count"] == 184
    assert summary["obstruction_flagged_count"] == 12
