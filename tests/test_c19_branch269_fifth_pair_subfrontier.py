"""Regression tests for the C19 branch-269 fifth-pair sub-frontier."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_c19_branch269_fifth_pair_subfrontier.py"
ARTIFACT = ROOT / "reports" / "c19_branch269_fifth_pair_subfrontier.json"


def run_script(*args: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_c19_branch269_fifth_pair_subfrontier_artifact() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["trust"] == "EXACT_CERTIFICATE_DIAGNOSTIC"
    assert payload["frontier_artifact"] == "reports/c19_fourth_pair_frontier_classifier.json"
    assert (
        payload["source_sweep_artifact"]
        == "data/certificates/c19_kalmanson_prefix_window_sweep_128_287.json"
    )

    source_window = payload["source_window"]
    assert source_window["start_index"] == 256
    assert source_window["end_index"] == 287
    assert source_window["fifth_pair_child_branch_count"] == 4950
    assert source_window["fifth_pair_child_certified_count"] == 4950
    assert source_window["unclosed_fifth_pair_child_branch_count"] == 0

    focus = payload["focus_parent"]
    assert focus["label"] == "c19_prefix_branch_0269"
    assert focus["boundary_left"] == [1, 3, 11]
    assert focus["boundary_right_reflection_side"] == [2, 5, 15]
    assert focus["fourth_pair_survivor_count"] == 9
    assert focus["fifth_pair_child_count"] == 810
    assert (
        focus["fifth_pair_child_label_digest"]
        == "65690f03459851d0f3dafc19d2d0a4a1a6797d4e033f455e39b17810d2e2cf08"
    )

    assert [row["fifth_pair_child_count"] for row in payload["per_fourth_pair_parent"]] == [
        90,
        90,
        90,
        90,
        90,
        90,
        90,
        90,
        90,
    ]
    assert payload["histograms"]["fifth_child_count_by_fourth_added_pair"] == {
        "8,4": 90,
        "8,7": 90,
        "9,7": 90,
        "9,13": 90,
        "10,7": 90,
        "10,9": 90,
        "10,13": 90,
        "17,4": 90,
        "17,18": 90,
    }


def test_c19_branch269_fifth_pair_subfrontier_replay_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload == artifact
