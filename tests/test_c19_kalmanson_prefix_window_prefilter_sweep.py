"""Regression tests for the compact C19 prefilter-window sweep artifact."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

from c19_replay_helpers import assert_c19_replay_matches_artifact

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sweep_c19_kalmanson_prefix_windows_prefilter.py"
ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "c19_kalmanson_prefix_window_prefilter_sweep_288_479.json"
)


def run_script(*args: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_c19_prefilter_window_sweep_artifact_summary() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["type"] == "c19_kalmanson_prefix_window_prefilter_sweep_v1"
    assert payload["trust"] == "EXACT_OBSTRUCTION"
    aggregate = payload["aggregate_accounting"]
    assert aggregate["prefix_branch_count"] == 192
    assert aggregate["prefix_branches_closed_after_chain"] == 192
    assert aggregate["prefix_branches_remaining_after_chain"] == 0
    assert aggregate["direct_prefix_certified_count"] == 136
    assert aggregate["direct_prefix_unclosed_count"] == 56
    assert aggregate["fourth_pair_child_branch_count"] == 7392
    assert aggregate["fourth_pair_child_certified_count"] == 7277
    assert aggregate["unclosed_fourth_pair_child_branch_count"] == 115
    assert aggregate["fifth_pair_child_branch_count"] == 10350
    assert aggregate["fifth_pair_child_certified_count"] == 10350
    assert aggregate["fifth_pair_prefilter_certified_count"] == 10342
    assert aggregate["fifth_pair_farkas_fallback_attempt_count"] == 8
    assert aggregate["fifth_pair_farkas_fallback_certified_count"] == 8
    assert aggregate["unclosed_fifth_pair_child_branch_count"] == 0
    assert aggregate["exhaustive_all_orders"] is False
    assert (
        payload["prefix_label_digest"]
        == "a2dcbd0eb6d2513dd906346ab9a4e6a273bb7033d5bcd344cf4f52cd622e8648"
    )

    windows = payload["windows"]
    assert [(row["start_index"], row["end_index"]) for row in windows] == [
        (288, 319),
        (320, 351),
        (352, 383),
        (384, 415),
        (416, 447),
        (448, 479),
    ]
    assert [
        row["branch_accounting"]["fifth_pair_farkas_fallback_certified_count"]
        for row in windows
    ] == [0, 0, 0, 0, 7, 1]
    assert windows[-1]["fifth_pair_farkas_fallback_labels"] == [
        "c19_window_fifth_child_0456_0059_0041",
    ]


def test_c19_prefilter_window_sweep_small_replay() -> None:
    payload = run_script("--window-count", "1", "--json")

    aggregate = payload["aggregate_accounting"]
    assert aggregate["prefix_branch_count"] == 32
    assert aggregate["prefix_branches_closed_after_chain"] == 32
    assert aggregate["prefix_branches_remaining_after_chain"] == 0
    assert aggregate["direct_prefix_certified_count"] == 32
    assert aggregate["direct_prefix_unclosed_count"] == 0
    assert aggregate["fourth_pair_child_branch_count"] == 0
    assert aggregate["fifth_pair_child_branch_count"] == 0

    windows = payload["windows"]
    assert len(windows) == 1
    assert windows[0]["start_index"] == 288
    assert windows[0]["end_index"] == 319
    assert windows[0]["direct_survivor_labels"] == []
    assert windows[0]["fifth_pair_farkas_fallback_labels"] == []


@pytest.mark.artifact
@pytest.mark.slow
def test_c19_prefilter_window_sweep_full_replay_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert_c19_replay_matches_artifact(payload, artifact)
