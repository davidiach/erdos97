"""Regression tests for the C19 fallback small-unit support search."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_c19_prefilter_small_unit_supports.py"
ARTIFACT = ROOT / "reports" / "c19_prefilter_small_unit_support_search.json"


def run_script(*args: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_c19_prefilter_small_unit_support_artifact_summary() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["type"] == "c19_prefilter_small_unit_support_search_v1"
    assert payload["trust"] == "EXACT_OBSTRUCTION"
    assert payload["aggregate"] == {
        "exhaustive_unit_support_bound": 3,
        "fallback_child_count": 8,
        "fallback_label_digest": (
            "2dc4965b208144017b7aba73dba920c8c8f8f1eea93a2f84650eb4f5f484f0c8"
        ),
        "total_pair_sums_checked": 15428396,
        "two_row_prefilter_miss_count": 8,
        "unit_support_at_most_three_found_count": 7,
        "unit_support_at_most_three_missing_count": 1,
    }
    assert payload["histograms"]["unit_support_result"] == {"3": 7, "none": 1}
    missing = [
        row["label"]
        for row in payload["fallback_records"]
        if not row["unit_support_at_most_three_found"]
    ]
    assert missing == ["c19_window_fifth_child_0430_0081_0011"]
    assert all(
        len(row["unit_support"]) == 3
        for row in payload["fallback_records"]
        if row["unit_support_at_most_three_found"]
    )


def test_c19_prefilter_small_unit_support_replay_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload == artifact
