"""Regression tests for the C19 Kalmanson sweep cost diagnostic."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_c19_kalmanson_sweep_costs.py"
ARTIFACT = ROOT / "reports" / "c19_kalmanson_sweep_cost_diagnostic.json"


def run_script(*args: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_c19_sweep_cost_diagnostic_artifact() -> None:
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
    assert aggregate["window_count"] == 5
    assert aggregate["prefix_branch_count"] == 160
    assert aggregate["prefix_branches_closed_after_chain"] == 160
    assert aggregate["prefix_branches_remaining_after_chain"] == 0
    assert aggregate["total_branch_attempt_count"] == 14416
    assert aggregate["direct_prefix_attempt_count"] == 160
    assert aggregate["fourth_pair_child_attempt_count"] == 6336
    assert aggregate["fifth_pair_child_attempt_count"] == 7920
    assert aggregate["direct_survivor_count"] == 48
    assert aggregate["direct_survivors_requiring_fifth_pair_count"] == 33
    assert aggregate["direct_survivors_closed_by_fourth_pair_only_count"] == 15

    assert payload["histograms"]["fifth_pair_child_attempts_per_direct_survivor"] == {
        "0": 15,
        "90": 13,
        "180": 7,
        "270": 3,
        "360": 4,
        "450": 4,
        "630": 1,
        "810": 1,
    }

    max_window = payload["maxima"]["max_window_by_total_branch_attempts"]
    assert max_window["start_index"] == 256
    assert max_window["end_index"] == 287
    assert max_window["total_branch_attempt_count"] == 7226

    max_prefix = payload["maxima"]["max_prefix_by_fifth_pair_child_attempts"]
    assert max_prefix["label"] == "c19_prefix_branch_0269"
    assert max_prefix["fourth_pair_child_survivor_count"] == 9
    assert max_prefix["fifth_pair_child_attempt_count"] == 810


def test_c19_sweep_cost_diagnostic_replay_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload == artifact
