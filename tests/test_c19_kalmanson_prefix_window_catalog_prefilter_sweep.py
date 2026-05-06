"""Regression tests for the compact C19 catalog-prefilter sweep artifact."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sweep_c19_kalmanson_prefix_windows_catalog_prefilter.py"
ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "c19_kalmanson_prefix_window_catalog_prefilter_sweep_288_479.json"
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


def test_c19_catalog_prefilter_window_sweep_artifact_summary() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["type"] == "c19_kalmanson_prefix_window_catalog_prefilter_sweep_v1"
    assert payload["trust"] == "EXACT_OBSTRUCTION"
    assert payload["parameters"]["fifth_pair_prefilter"] == (
        "two_row_then_cataloged_unit_support"
    )
    aggregate = payload["aggregate_accounting"]
    assert aggregate["prefix_branch_count"] == 192
    assert aggregate["prefix_branches_closed_after_chain"] == 192
    assert aggregate["prefix_branches_remaining_after_chain"] == 0
    assert aggregate["fifth_pair_child_branch_count"] == 10350
    assert aggregate["fifth_pair_child_certified_count"] == 10350
    assert aggregate["fifth_pair_prefilter_certified_count"] == 10350
    assert aggregate["fifth_pair_two_row_prefilter_certified_count"] == 10342
    assert aggregate["fifth_pair_catalog_prefilter_certified_count"] == 8
    assert aggregate["fifth_pair_farkas_fallback_attempt_count"] == 0
    assert aggregate["fifth_pair_farkas_fallback_certified_count"] == 0
    assert aggregate["unclosed_fifth_pair_child_branch_count"] == 0
    assert aggregate["exhaustive_all_orders"] is False

    windows = payload["windows"]
    assert [
        row["branch_accounting"]["fifth_pair_catalog_prefilter_certified_count"]
        for row in windows
    ] == [0, 0, 0, 0, 7, 1]
    assert [
        row["branch_accounting"]["fifth_pair_farkas_fallback_certified_count"]
        for row in windows
    ] == [0, 0, 0, 0, 0, 0]
    assert windows[4]["fifth_pair_farkas_fallback_labels"] == []
    assert windows[5]["fifth_pair_farkas_fallback_labels"] == []
    assert windows[4]["closed_support_size_histograms"]["fifth_pair_prefilter"] == {
        "2": 4223,
        "3": 6,
        "6": 1,
    }
    assert windows[5]["closed_support_size_histograms"]["fifth_pair_prefilter"] == {
        "2": 3509,
        "3": 1,
    }


def test_c19_catalog_prefilter_window_sweep_small_replay() -> None:
    payload = run_script("--window-count", "1", "--json")

    assert payload["type"] == "c19_kalmanson_prefix_window_catalog_prefilter_sweep_v1"
    aggregate = payload["aggregate_accounting"]
    assert aggregate["prefix_branch_count"] == 32
    assert aggregate["prefix_branches_closed_after_chain"] == 32
    assert aggregate["prefix_branches_remaining_after_chain"] == 0
    assert aggregate["direct_prefix_certified_count"] == 32
    assert aggregate["fifth_pair_child_branch_count"] == 0
    assert aggregate["fifth_pair_catalog_prefilter_certified_count"] == 0

    windows = payload["windows"]
    assert len(windows) == 1
    assert windows[0]["start_index"] == 288
    assert windows[0]["end_index"] == 319
    assert windows[0]["fifth_pair_farkas_fallback_labels"] == []


@pytest.mark.artifact
@pytest.mark.slow
def test_c19_catalog_prefilter_window_sweep_full_replay_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert artifact == payload
