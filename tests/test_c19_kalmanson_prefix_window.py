"""Regression tests for the C19 prefix-window Kalmanson chain."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

from c19_replay_helpers import assert_c19_replay_matches_artifact

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "certify_c19_kalmanson_prefix_window.py"
ARTIFACT = ROOT / "data" / "certificates" / "c19_kalmanson_prefix_window_128_159.json"
WINDOW_160_ARTIFACT = (
    ROOT / "data" / "certificates" / "c19_kalmanson_prefix_window_160_191.json"
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


def test_c19_prefix_window_artifact_summary() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    accounting = payload["branch_accounting"]
    assert accounting["prefix_branch_count"] == 32
    assert accounting["direct_prefix_certified_count"] == 31
    assert accounting["direct_prefix_unclosed_count"] == 1
    assert accounting["fourth_pair_child_branch_count"] == 132
    assert accounting["fourth_pair_child_certified_count"] == 130
    assert accounting["unclosed_fourth_pair_child_branch_count"] == 2
    assert accounting["fifth_pair_child_branch_count"] == 180
    assert accounting["fifth_pair_child_certified_count"] == 180
    assert accounting["unclosed_fifth_pair_child_branch_count"] == 0
    assert accounting["prefix_branches_closed_after_chain"] == 32
    assert accounting["prefix_branches_remaining_after_chain"] == 0
    assert accounting["exhaustive_window_scan"] is True
    assert accounting["exhaustive_all_orders"] is False

    assert payload["forced_row_count_histograms"] == {
        "direct_prefix": {"910": 32},
        "fourth_pair": {"1932": 132},
        "fifth_pair": {"3300": 180},
    }
    assert payload["label_digests"] == {
        "prefix": "9741d59833d730db662ad850c052d53fc880a6599db363e82175ca318729f3e9",
        "fourth_pair_children": (
            "e2fe7d93069dab13d15fe076e4d114db09c0d75420208f89241fccf26bca1225"
        ),
        "fifth_pair_children": (
            "75db70d03330d51835ff7974ec1999eeb8307e3fb5347a8416ee37f7467b51b8"
        ),
    }

    direct_unclosed = payload["direct_unclosed_prefixes"]
    assert isinstance(direct_unclosed, list)
    assert len(direct_unclosed) == 1
    assert direct_unclosed[0]["label"] == "c19_prefix_branch_0156"

    fourth_unclosed = payload["unclosed_fourth_pair_child_branches"]
    assert isinstance(fourth_unclosed, list)
    assert [row["label"] for row in fourth_unclosed] == [
        "c19_window_fourth_child_0156_0063",
        "c19_window_fourth_child_0156_0065",
    ]
    assert payload["unclosed_fifth_pair_child_branches"] == []

    first_direct = payload["direct_closed_examples"][0]
    assert first_direct["label"] == "c19_prefix_branch_0128"
    assert first_direct["certificate_summary"]["zero_sum_verified"] is True
    first_fifth = payload["fifth_pair_closed_examples"][0]
    assert first_fifth["label"] == "c19_window_fifth_child_0156_0063_0000"
    assert first_fifth["certificate_summary"]["forced_inequalities_available"] == 3300


def test_c19_prefix_window_replay_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert_c19_replay_matches_artifact(payload, artifact)


def test_c19_prefix_window_160_191_artifact_summary() -> None:
    payload = json.loads(WINDOW_160_ARTIFACT.read_text(encoding="utf-8"))

    accounting = payload["branch_accounting"]
    assert accounting["prefix_branch_count"] == 32
    assert accounting["direct_prefix_certified_count"] == 23
    assert accounting["direct_prefix_unclosed_count"] == 9
    assert accounting["fourth_pair_child_branch_count"] == 1188
    assert accounting["fourth_pair_child_certified_count"] == 1181
    assert accounting["unclosed_fourth_pair_child_branch_count"] == 7
    assert accounting["fifth_pair_child_branch_count"] == 630
    assert accounting["fifth_pair_child_certified_count"] == 630
    assert accounting["unclosed_fifth_pair_child_branch_count"] == 0
    assert accounting["prefix_parents_closed_by_fourth_refinement"] == 4
    assert accounting["prefix_parents_closed_by_fifth_refinement"] == 5
    assert accounting["prefix_branches_closed_after_chain"] == 32
    assert accounting["prefix_branches_remaining_after_chain"] == 0
    assert accounting["exhaustive_window_scan"] is True
    assert accounting["exhaustive_all_orders"] is False

    assert payload["forced_row_count_histograms"] == {
        "direct_prefix": {"910": 32},
        "fourth_pair": {"1932": 1188},
        "fifth_pair": {"3300": 630},
    }
    assert payload["label_digests"] == {
        "prefix": "92c942e3ff7724cdfa51af73618e70f8d0a268a3256954bd77e8c00d8b68be69",
        "fourth_pair_children": (
            "ee4c5b53f6976fe6453363552d9404f101c881141e56208454c6bd484068160e"
        ),
        "fifth_pair_children": (
            "004b096bc414999a8288790c66e93b76aeac1b879a3f66c2ad43848a016b4106"
        ),
    }

    assert [row["label"] for row in payload["direct_unclosed_prefixes"]] == [
        "c19_prefix_branch_0161",
        "c19_prefix_branch_0162",
        "c19_prefix_branch_0164",
        "c19_prefix_branch_0166",
        "c19_prefix_branch_0167",
        "c19_prefix_branch_0168",
        "c19_prefix_branch_0182",
        "c19_prefix_branch_0186",
        "c19_prefix_branch_0187",
    ]
    assert [row["label"] for row in payload["unclosed_fourth_pair_child_branches"]] == [
        "c19_window_fourth_child_0164_0074",
        "c19_window_fourth_child_0164_0076",
        "c19_window_fourth_child_0166_0076",
        "c19_window_fourth_child_0168_0075",
        "c19_window_fourth_child_0186_0114",
        "c19_window_fourth_child_0186_0119",
        "c19_window_fourth_child_0187_0114",
    ]
    assert payload["unclosed_fifth_pair_child_branches"] == []


def test_c19_prefix_window_160_191_replay_matches_artifact() -> None:
    payload = run_script(
        "--start-index",
        "160",
        "--window-size",
        "32",
        "--json",
    )
    artifact = json.loads(WINDOW_160_ARTIFACT.read_text(encoding="utf-8"))

    assert_c19_replay_matches_artifact(payload, artifact)
