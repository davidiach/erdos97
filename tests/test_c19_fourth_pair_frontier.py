"""Regression tests for the C19 fourth-pair frontier classifier."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_c19_fourth_pair_frontier.py"
ARTIFACT = ROOT / "reports" / "c19_fourth_pair_frontier_classifier.json"


def run_script(*args: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_c19_fourth_pair_frontier_classifier_artifact() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["trust"] == "EXACT_CERTIFICATE_DIAGNOSTIC"
    assert (
        payload["source_artifact"]
        == "data/certificates/c19_kalmanson_prefix_window_sweep_128_287.json"
    )
    assert (
        payload["source_prefix_label_digest"]
        == "b18984a2ebd95ffcd6eb2af48fd13c6710b29d9234af18e5966895fa23667879"
    )

    aggregate = payload["aggregate"]
    assert aggregate["direct_survivor_parent_count"] == 48
    assert aggregate["fourth_pair_child_attempt_count"] == 6336
    assert aggregate["fourth_pair_survivor_count"] == 88
    assert aggregate["fourth_pair_children_closed_by_fourth_pair_count"] == 6248
    assert aggregate["parents_requiring_fifth_pair_count"] == 33
    assert aggregate["parents_closed_by_fourth_pair_only_count"] == 15
    assert (
        aggregate["all_fourth_pair_child_label_digest"]
        == "63c4cfe44978752598f66ba946f747e4509c3d3fa85b2ffb662317126ebacc0a"
    )
    assert (
        aggregate["fourth_pair_survivor_label_digest"]
        == "0c6073d4ef3cc32705263a3bbc0bcaa98c1d644fe81a6e067864a8e4a618be8c"
    )

    focus = payload["focus_parent"]
    assert focus["label"] == "c19_prefix_branch_0269"
    assert focus["fourth_pair_survivor_count"] == 9
    assert focus["fifth_pair_child_attempt_count"] == 810
    assert [
        (row["added_left"], row["added_right_reflection_side"])
        for row in focus["survivor_pairs"]
    ] == [
        (8, 4),
        (8, 7),
        (9, 7),
        (9, 13),
        (10, 7),
        (10, 9),
        (10, 13),
        (17, 4),
        (17, 18),
    ]

    top_parent_labels = [row["label"] for row in payload["top_parents_by_fourth_pair_survivor_count"][:3]]
    assert top_parent_labels == [
        "c19_prefix_branch_0269",
        "c19_prefix_branch_0278",
        "c19_prefix_branch_0260",
    ]


def test_c19_fourth_pair_frontier_replay_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload == artifact
