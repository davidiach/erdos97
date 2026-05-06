"""Regression tests for the compact C19 prefix-window sweep artifact."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sweep_c19_kalmanson_prefix_windows.py"
ARTIFACT = (
    ROOT / "data" / "certificates" / "c19_kalmanson_prefix_window_sweep_128_287.json"
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


def test_c19_prefix_window_sweep_artifact_summary() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    aggregate = payload["aggregate_accounting"]
    assert aggregate["prefix_branch_count"] == 160
    assert aggregate["prefix_branches_closed_after_chain"] == 160
    assert aggregate["prefix_branches_remaining_after_chain"] == 0
    assert aggregate["direct_prefix_certified_count"] == 112
    assert aggregate["direct_prefix_unclosed_count"] == 48
    assert aggregate["fourth_pair_child_branch_count"] == 6336
    assert aggregate["fourth_pair_child_certified_count"] == 6248
    assert aggregate["unclosed_fourth_pair_child_branch_count"] == 88
    assert aggregate["fifth_pair_child_branch_count"] == 7920
    assert aggregate["fifth_pair_child_certified_count"] == 7920
    assert aggregate["unclosed_fifth_pair_child_branch_count"] == 0
    assert aggregate["exhaustive_window_sweep"] is True
    assert aggregate["exhaustive_all_orders"] is False
    assert (
        payload["prefix_label_digest"]
        == "b18984a2ebd95ffcd6eb2af48fd13c6710b29d9234af18e5966895fa23667879"
    )

    windows = payload["windows"]
    assert isinstance(windows, list)
    assert [(row["start_index"], row["end_index"]) for row in windows] == [
        (128, 159),
        (160, 191),
        (192, 223),
        (224, 255),
        (256, 287),
    ]
    assert [row["branch_accounting"]["prefix_branches_remaining_after_chain"] for row in windows] == [
        0,
        0,
        0,
        0,
        0,
    ]
    assert [len(row["direct_survivor_labels"]) for row in windows] == [1, 9, 13, 8, 17]
    assert [len(row["fourth_pair_survivor_labels"]) for row in windows] == [2, 7, 15, 9, 55]
    assert [len(row["fifth_pair_survivor_labels"]) for row in windows] == [0, 0, 0, 0, 0]


def test_c19_prefix_window_sweep_small_replay() -> None:
    payload = run_script("--window-count", "1", "--json")

    aggregate = payload["aggregate_accounting"]
    assert aggregate["prefix_branch_count"] == 32
    assert aggregate["prefix_branches_closed_after_chain"] == 32
    assert aggregate["prefix_branches_remaining_after_chain"] == 0
    assert aggregate["direct_prefix_certified_count"] == 31
    assert aggregate["direct_prefix_unclosed_count"] == 1
    assert aggregate["fourth_pair_child_branch_count"] == 132
    assert aggregate["fourth_pair_child_certified_count"] == 130
    assert aggregate["fifth_pair_child_branch_count"] == 180
    assert aggregate["fifth_pair_child_certified_count"] == 180

    windows = payload["windows"]
    assert len(windows) == 1
    assert windows[0]["start_index"] == 128
    assert windows[0]["end_index"] == 159
    assert windows[0]["direct_survivor_labels"] == ["c19_prefix_branch_0156"]
    assert windows[0]["fifth_pair_survivor_labels"] == []


@pytest.mark.artifact
@pytest.mark.slow
def test_c19_prefix_window_sweep_full_replay_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert artifact == payload
