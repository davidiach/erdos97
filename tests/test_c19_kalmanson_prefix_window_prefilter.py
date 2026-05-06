"""Regression tests for C19 prefix windows using the fifth-pair prefilter."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "certify_c19_kalmanson_prefix_window_prefilter.py"
WINDOW_288_ARTIFACT = (
    ROOT / "data" / "certificates" / "c19_kalmanson_prefix_window_288_319_prefilter.json"
)
WINDOW_320_ARTIFACT = (
    ROOT / "data" / "certificates" / "c19_kalmanson_prefix_window_320_351_prefilter.json"
)
WINDOW_352_ARTIFACT = (
    ROOT / "data" / "certificates" / "c19_kalmanson_prefix_window_352_383_prefilter.json"
)
WINDOW_384_ARTIFACT = (
    ROOT / "data" / "certificates" / "c19_kalmanson_prefix_window_384_415_prefilter.json"
)
WINDOW_416_ARTIFACT = (
    ROOT / "data" / "certificates" / "c19_kalmanson_prefix_window_416_447_prefilter.json"
)
WINDOW_448_ARTIFACT = (
    ROOT / "data" / "certificates" / "c19_kalmanson_prefix_window_448_479_prefilter.json"
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


def test_c19_prefilter_window_288_319_artifact_summary() -> None:
    payload = json.loads(WINDOW_288_ARTIFACT.read_text(encoding="utf-8"))

    assert payload["type"] == "c19_kalmanson_prefix_window_prefilter_chain_v1"
    assert payload["trust"] == "EXACT_OBSTRUCTION"
    accounting = payload["branch_accounting"]
    assert accounting["prefix_branch_count"] == 32
    assert accounting["direct_prefix_certified_count"] == 32
    assert accounting["prefix_branches_closed_after_chain"] == 32
    assert accounting["prefix_branches_remaining_after_chain"] == 0
    assert accounting["fourth_pair_child_branch_count"] == 0
    assert accounting["fifth_pair_child_branch_count"] == 0
    assert accounting["exhaustive_all_orders"] is False
    assert payload["direct_unclosed_prefixes"] == []

    assert payload["label_digests"] == {
        "prefix": "cc83bf55e54627845ea5a3bb9d7588cbe6442d9bf6bdaae0c26ab356beb2dfef",
        "fourth_pair_children": (
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ),
        "fifth_pair_children": (
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ),
    }


def test_c19_prefilter_window_288_319_replay_matches_artifact() -> None:
    payload = run_script(
        "--start-index",
        "288",
        "--window-size",
        "32",
        "--assert-expected",
        "--json",
    )
    artifact = json.loads(WINDOW_288_ARTIFACT.read_text(encoding="utf-8"))

    assert payload == artifact


def test_c19_prefilter_window_320_351_artifact_summary() -> None:
    payload = json.loads(WINDOW_320_ARTIFACT.read_text(encoding="utf-8"))

    assert payload["type"] == "c19_kalmanson_prefix_window_prefilter_chain_v1"
    assert payload["trust"] == "EXACT_OBSTRUCTION"
    accounting = payload["branch_accounting"]
    assert accounting["prefix_branch_count"] == 32
    assert accounting["direct_prefix_certified_count"] == 26
    assert accounting["direct_prefix_unclosed_count"] == 6
    assert accounting["fourth_pair_child_branch_count"] == 792
    assert accounting["fourth_pair_child_certified_count"] == 786
    assert accounting["unclosed_fourth_pair_child_branch_count"] == 6
    assert accounting["fifth_pair_child_branch_count"] == 540
    assert accounting["fifth_pair_child_certified_count"] == 540
    assert accounting["fifth_pair_prefilter_certified_count"] == 540
    assert accounting["fifth_pair_farkas_fallback_attempt_count"] == 0
    assert accounting["unclosed_fifth_pair_child_branch_count"] == 0
    assert accounting["prefix_branches_closed_after_chain"] == 32
    assert accounting["prefix_branches_remaining_after_chain"] == 0

    assert payload["closed_support_size_histograms"]["fifth_pair_prefilter"] == {"2": 540}
    assert payload["closed_support_size_histograms"]["fifth_pair_farkas_fallback"] == {}
    assert [row["label"] for row in payload["direct_unclosed_prefixes"]] == [
        "c19_prefix_branch_0338",
        "c19_prefix_branch_0343",
        "c19_prefix_branch_0344",
        "c19_prefix_branch_0348",
        "c19_prefix_branch_0349",
        "c19_prefix_branch_0350",
    ]
    assert [row["label"] for row in payload["unclosed_fourth_pair_child_branches"]] == [
        "c19_window_fourth_child_0338_0063",
        "c19_window_fourth_child_0338_0065",
        "c19_window_fourth_child_0348_0066",
        "c19_window_fourth_child_0348_0073",
        "c19_window_fourth_child_0348_0076",
        "c19_window_fourth_child_0350_0075",
    ]


def test_c19_prefilter_window_320_351_replay_matches_artifact() -> None:
    payload = run_script(
        "--start-index",
        "320",
        "--window-size",
        "32",
        "--assert-expected",
        "--json",
    )
    artifact = json.loads(WINDOW_320_ARTIFACT.read_text(encoding="utf-8"))

    assert payload == artifact


def test_c19_prefilter_window_352_383_artifact_summary() -> None:
    payload = json.loads(WINDOW_352_ARTIFACT.read_text(encoding="utf-8"))

    assert payload["type"] == "c19_kalmanson_prefix_window_prefilter_chain_v1"
    assert payload["trust"] == "EXACT_OBSTRUCTION"
    accounting = payload["branch_accounting"]
    assert accounting["prefix_branch_count"] == 32
    assert accounting["direct_prefix_certified_count"] == 23
    assert accounting["direct_prefix_unclosed_count"] == 9
    assert accounting["fourth_pair_child_branch_count"] == 1188
    assert accounting["fourth_pair_child_certified_count"] == 1180
    assert accounting["unclosed_fourth_pair_child_branch_count"] == 8
    assert accounting["fifth_pair_child_branch_count"] == 720
    assert accounting["fifth_pair_child_certified_count"] == 720
    assert accounting["fifth_pair_prefilter_certified_count"] == 720
    assert accounting["fifth_pair_farkas_fallback_attempt_count"] == 0
    assert accounting["unclosed_fifth_pair_child_branch_count"] == 0
    assert accounting["prefix_branches_closed_after_chain"] == 32
    assert accounting["prefix_branches_remaining_after_chain"] == 0

    assert payload["closed_support_size_histograms"]["fifth_pair_prefilter"] == {"2": 720}
    assert payload["closed_support_size_histograms"]["fifth_pair_farkas_fallback"] == {}
    assert [row["label"] for row in payload["direct_unclosed_prefixes"]] == [
        "c19_prefix_branch_0352",
        "c19_prefix_branch_0357",
        "c19_prefix_branch_0362",
        "c19_prefix_branch_0363",
        "c19_prefix_branch_0364",
        "c19_prefix_branch_0368",
        "c19_prefix_branch_0369",
        "c19_prefix_branch_0374",
        "c19_prefix_branch_0376",
    ]


def test_c19_prefilter_window_352_383_replay_matches_artifact() -> None:
    payload = run_script(
        "--start-index",
        "352",
        "--window-size",
        "32",
        "--assert-expected",
        "--json",
    )
    artifact = json.loads(WINDOW_352_ARTIFACT.read_text(encoding="utf-8"))

    assert payload == artifact


def test_c19_prefilter_window_384_415_artifact_summary() -> None:
    payload = json.loads(WINDOW_384_ARTIFACT.read_text(encoding="utf-8"))

    assert payload["type"] == "c19_kalmanson_prefix_window_prefilter_chain_v1"
    assert payload["trust"] == "EXACT_OBSTRUCTION"
    accounting = payload["branch_accounting"]
    assert accounting["prefix_branch_count"] == 32
    assert accounting["direct_prefix_certified_count"] == 20
    assert accounting["direct_prefix_unclosed_count"] == 12
    assert accounting["fourth_pair_child_branch_count"] == 1584
    assert accounting["fourth_pair_child_certified_count"] == 1569
    assert accounting["unclosed_fourth_pair_child_branch_count"] == 15
    assert accounting["fifth_pair_child_branch_count"] == 1350
    assert accounting["fifth_pair_child_certified_count"] == 1350
    assert accounting["fifth_pair_prefilter_certified_count"] == 1350
    assert accounting["fifth_pair_farkas_fallback_attempt_count"] == 0
    assert accounting["unclosed_fifth_pair_child_branch_count"] == 0
    assert accounting["prefix_branches_closed_after_chain"] == 32
    assert accounting["prefix_branches_remaining_after_chain"] == 0

    assert payload["closed_support_size_histograms"]["fifth_pair_prefilter"] == {"2": 1350}
    assert payload["closed_support_size_histograms"]["fifth_pair_farkas_fallback"] == {}
    assert [row["label"] for row in payload["direct_unclosed_prefixes"]] == [
        "c19_prefix_branch_0391",
        "c19_prefix_branch_0393",
        "c19_prefix_branch_0395",
        "c19_prefix_branch_0396",
        "c19_prefix_branch_0397",
        "c19_prefix_branch_0403",
        "c19_prefix_branch_0404",
        "c19_prefix_branch_0405",
        "c19_prefix_branch_0406",
        "c19_prefix_branch_0407",
        "c19_prefix_branch_0408",
        "c19_prefix_branch_0412",
    ]


def test_c19_prefilter_window_384_415_replay_matches_artifact() -> None:
    payload = run_script(
        "--start-index",
        "384",
        "--window-size",
        "32",
        "--assert-expected",
        "--json",
    )
    artifact = json.loads(WINDOW_384_ARTIFACT.read_text(encoding="utf-8"))

    assert payload == artifact


def test_c19_prefilter_window_416_447_artifact_summary() -> None:
    payload = json.loads(WINDOW_416_ARTIFACT.read_text(encoding="utf-8"))

    assert payload["type"] == "c19_kalmanson_prefix_window_prefilter_chain_v1"
    assert payload["trust"] == "EXACT_OBSTRUCTION"
    accounting = payload["branch_accounting"]
    assert accounting["prefix_branch_count"] == 32
    assert accounting["direct_prefix_certified_count"] == 19
    assert accounting["direct_prefix_unclosed_count"] == 13
    assert accounting["fourth_pair_child_branch_count"] == 1716
    assert accounting["fourth_pair_child_certified_count"] == 1669
    assert accounting["unclosed_fourth_pair_child_branch_count"] == 47
    assert accounting["fifth_pair_child_branch_count"] == 4230
    assert accounting["fifth_pair_child_certified_count"] == 4230
    assert accounting["fifth_pair_prefilter_certified_count"] == 4223
    assert accounting["fifth_pair_farkas_fallback_attempt_count"] == 7
    assert accounting["fifth_pair_farkas_fallback_certified_count"] == 7
    assert accounting["unclosed_fifth_pair_child_branch_count"] == 0
    assert accounting["prefix_branches_closed_after_chain"] == 32
    assert accounting["prefix_branches_remaining_after_chain"] == 0

    assert payload["closed_support_size_histograms"]["fifth_pair_prefilter"] == {"2": 4223}
    assert payload["closed_support_size_histograms"]["fifth_pair_farkas_fallback"] == {
        "7": 1,
        "8": 1,
        "19": 1,
        "47": 1,
        "52": 1,
        "54": 1,
        "58": 1,
    }
    assert [row["label"] for row in payload["fifth_pair_farkas_fallback_examples"]] == [
        "c19_window_fifth_child_0430_0081_0011",
        "c19_window_fifth_child_0434_0070_0021",
        "c19_window_fifth_child_0435_0078_0012",
        "c19_window_fifth_child_0435_0078_0085",
        "c19_window_fifth_child_0435_0083_0022",
        "c19_window_fifth_child_0436_0082_0022",
        "c19_window_fifth_child_0436_0083_0022",
    ]


def test_c19_prefilter_window_416_447_replay_matches_artifact() -> None:
    payload = run_script(
        "--start-index",
        "416",
        "--window-size",
        "32",
        "--assert-expected",
        "--json",
    )
    artifact = json.loads(WINDOW_416_ARTIFACT.read_text(encoding="utf-8"))

    assert payload == artifact


def test_c19_prefilter_window_448_479_artifact_summary() -> None:
    payload = json.loads(WINDOW_448_ARTIFACT.read_text(encoding="utf-8"))

    assert payload["type"] == "c19_kalmanson_prefix_window_prefilter_chain_v1"
    assert payload["trust"] == "EXACT_OBSTRUCTION"
    accounting = payload["branch_accounting"]
    assert accounting["prefix_branch_count"] == 32
    assert accounting["direct_prefix_certified_count"] == 16
    assert accounting["direct_prefix_unclosed_count"] == 16
    assert accounting["fourth_pair_child_branch_count"] == 2112
    assert accounting["fourth_pair_child_certified_count"] == 2073
    assert accounting["unclosed_fourth_pair_child_branch_count"] == 39
    assert accounting["fifth_pair_child_branch_count"] == 3510
    assert accounting["fifth_pair_child_certified_count"] == 3510
    assert accounting["fifth_pair_prefilter_certified_count"] == 3509
    assert accounting["fifth_pair_farkas_fallback_attempt_count"] == 1
    assert accounting["fifth_pair_farkas_fallback_certified_count"] == 1
    assert accounting["unclosed_fifth_pair_child_branch_count"] == 0
    assert accounting["prefix_branches_closed_after_chain"] == 32
    assert accounting["prefix_branches_remaining_after_chain"] == 0

    assert payload["closed_support_size_histograms"]["fifth_pair_prefilter"] == {"2": 3509}
    assert payload["closed_support_size_histograms"]["fifth_pair_farkas_fallback"] == {
        "50": 1
    }
    assert [row["label"] for row in payload["fifth_pair_farkas_fallback_examples"]] == [
        "c19_window_fifth_child_0456_0059_0041"
    ]


def test_c19_prefilter_window_448_479_replay_matches_artifact() -> None:
    payload = run_script(
        "--start-index",
        "448",
        "--window-size",
        "32",
        "--assert-expected",
        "--json",
    )
    artifact = json.loads(WINDOW_448_ARTIFACT.read_text(encoding="utf-8"))

    assert payload == artifact
