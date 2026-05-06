"""Regression tests for cataloged C19 fallback unit supports."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_c19_prefilter_catalog_unit_supports.py"
ARTIFACT = ROOT / "reports" / "c19_prefilter_catalog_unit_supports.json"


def run_script(*args: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_c19_prefilter_catalog_unit_support_artifact_summary() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["type"] == "c19_prefilter_catalog_unit_supports_v1"
    assert payload["trust"] == "EXACT_OBSTRUCTION"
    assert payload["aggregate"] == {
        "catalog_certified_count": 7,
        "catalog_certified_label_digest": (
            "03412b1e4da3c1de13345b052773aef2ae944f06028529f6c0f0d0a39e2a8ea6"
        ),
        "catalog_miss_count": 1,
        "catalog_support_count": 2,
        "catalog_support_digest": (
            "b4110d03ca090444ce9585c24d89ca8a71be87d1e7df55507cbc47ef41a5aee5"
        ),
        "fallback_child_count": 8,
        "fallback_label_digest": (
            "2dc4965b208144017b7aba73dba920c8c8f8f1eea93a2f84650eb4f5f484f0c8"
        ),
        "input_support_record_count": 7,
        "two_row_prefilter_miss_count": 8,
    }
    assert payload["histograms"]["catalog_usage"] == {
        "none": 1,
        "unit_support_000": 6,
        "unit_support_001": 1,
    }
    assert [row["catalog_id"] for row in payload["catalog"]] == [
        "unit_support_000",
        "unit_support_001",
    ]
    misses = [
        row["label"]
        for row in payload["fallback_records"]
        if not row["catalog_unit_support_found"]
    ]
    assert misses == ["c19_window_fifth_child_0430_0081_0011"]


def test_c19_prefilter_catalog_unit_support_replay_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload == artifact
