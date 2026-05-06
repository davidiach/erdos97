"""Regression tests for the C19 fifth-pair two-row prefilter."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

from c19_replay_helpers import assert_c19_replay_matches_artifact

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_c19_fifth_pair_two_row_prefilter.py"
ARTIFACT = ROOT / "reports" / "c19_fifth_pair_two_row_prefilter.json"


def run_script(*args: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_c19_fifth_pair_two_row_prefilter_artifact() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["trust"] == "EXACT_OBSTRUCTION"
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
    assert aggregate["prefilter_certified_count"] == 7917
    assert aggregate["prefilter_miss_count"] == 3
    assert aggregate["fallback_exactified_count"] == 3
    assert aggregate["final_certified_count"] == 7920
    assert aggregate["final_unclosed_count"] == 0
    assert aggregate["certified_by_zero_row_count"] == 0
    assert aggregate["certified_by_two_row_count"] == 7917
    assert (
        aggregate["two_row_prefilter_certificate_digest"]
        == "61476c4922821c55986b182a4720280730f97bf78a3b7f1cfb29658331e64b98"
    )
    assert (
        aggregate["fallback_certificate_digest"]
        == "1c09e3b2b7b147172f3d703bb2968a5ed66a84f550b65fc27cd55d9dc173e7ee"
    )

    assert payload["histograms"]["forced_row_count"] == {"3300": 7920}
    assert payload["histograms"]["certificate_row_count"] == {"2": 7917}
    assert payload["histograms"]["fallback_support_size"] == {"50": 1, "56": 1, "59": 1}
    assert [row["prefilter_miss_count"] for row in payload["per_window"]] == [
        0,
        0,
        1,
        0,
        2,
    ]
    assert [row["final_unclosed_count"] for row in payload["per_window"]] == [
        0,
        0,
        0,
        0,
        0,
    ]

    fallback_labels = [row["label"] for row in payload["fallback_certificates"]]
    assert fallback_labels == [
        "c19_window_fifth_child_0212_0023_0000",
        "c19_window_fifth_child_0261_0059_0041",
        "c19_window_fifth_child_0274_0059_0041",
    ]


def test_c19_fifth_pair_two_row_prefilter_replay_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert_c19_replay_matches_artifact(payload, artifact)
