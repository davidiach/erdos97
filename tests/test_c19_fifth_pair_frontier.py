"""Regression tests for the full C19 fifth-pair frontier classifier."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_c19_fifth_pair_frontier.py"
ARTIFACT = ROOT / "reports" / "c19_fifth_pair_frontier_classifier.json"


def run_script(*args: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_c19_fifth_pair_frontier_classifier_artifact() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["trust"] == "EXACT_CERTIFICATE_DIAGNOSTIC"
    assert payload["frontier_artifact"] == "reports/c19_fourth_pair_frontier_classifier.json"
    assert (
        payload["source_sweep_artifact"]
        == "data/certificates/c19_kalmanson_prefix_window_sweep_128_287.json"
    )

    aggregate = payload["aggregate"]
    assert aggregate["fourth_pair_survivor_parent_count"] == 88
    assert aggregate["fifth_pair_child_count"] == 7920
    assert aggregate["source_fifth_pair_child_count"] == 7920
    assert aggregate["source_unclosed_fifth_pair_child_count"] == 0
    assert aggregate["prefix_parent_count_requiring_fifth_pair"] == 33
    assert (
        aggregate["fifth_pair_child_label_digest"]
        == "33ec807edc96dbd4e529899b34d61f4e57a43798b6d63f31cbac40bd7a3b8033"
    )

    assert [row["fifth_pair_child_count"] for row in payload["per_window"]] == [
        180,
        630,
        1350,
        810,
        4950,
    ]
    assert [row["source_unclosed_fifth_pair_child_count"] for row in payload["per_window"]] == [
        0,
        0,
        0,
        0,
        0,
    ]
    assert payload["top_prefix_parents_by_fifth_pair_child_count"][:3] == [
        {"prefix_parent_label": "c19_prefix_branch_0269", "fifth_pair_child_count": 810},
        {"prefix_parent_label": "c19_prefix_branch_0278", "fifth_pair_child_count": 630},
        {"prefix_parent_label": "c19_prefix_branch_0260", "fifth_pair_child_count": 450},
    ]


def test_c19_fifth_pair_frontier_replay_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload == artifact
