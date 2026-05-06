"""Regression tests for the C19 prefilter fallback support diagnostic."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

from c19_replay_helpers import assert_c19_replay_matches_artifact

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_c19_prefilter_fallback_supports.py"
ARTIFACT = ROOT / "reports" / "c19_prefilter_fallback_supports.json"


def run_script(*args: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_c19_prefilter_fallback_support_artifact_summary() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["type"] == "c19_prefilter_fallback_support_diagnostic_v1"
    assert payload["trust"] == "EXACT_OBSTRUCTION"
    aggregate = payload["aggregate"]
    assert aggregate == {
        "exact_farkas_certified_count": 8,
        "fallback_certificate_digest": (
            "1570b3fa915c0c4a734518008c0121d3b40c6913927d0cc45064a40777969952"
        ),
        "fallback_child_count": 8,
        "fallback_label_digest": (
            "2dc4965b208144017b7aba73dba920c8c8f8f1eea93a2f84650eb4f5f484f0c8"
        ),
        "final_unclosed_count": 0,
        "forced_row_count": 3300,
        "two_row_prefilter_miss_count": 8,
    }
    assert payload["histograms"]["support_size"] == {
        "7": 1,
        "8": 1,
        "19": 1,
        "47": 1,
        "50": 1,
        "52": 1,
        "54": 1,
        "58": 1,
    }
    assert [row["label"] for row in payload["fallback_records"]] == [
        "c19_window_fifth_child_0430_0081_0011",
        "c19_window_fifth_child_0434_0070_0021",
        "c19_window_fifth_child_0435_0078_0012",
        "c19_window_fifth_child_0435_0078_0085",
        "c19_window_fifth_child_0435_0083_0022",
        "c19_window_fifth_child_0436_0082_0022",
        "c19_window_fifth_child_0436_0083_0022",
        "c19_window_fifth_child_0456_0059_0041",
    ]
    assert all(
        row["two_row_prefilter_certificate_found"] is False
        for row in payload["fallback_records"]
    )


def test_c19_prefilter_fallback_support_replay_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert_c19_replay_matches_artifact(payload, artifact)
