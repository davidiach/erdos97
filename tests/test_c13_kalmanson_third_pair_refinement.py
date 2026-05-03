"""Regression tests for the C13 third-pair Kalmanson refinement."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "refine_c13_kalmanson_third_pair.py"
ARTIFACT = ROOT / "data" / "certificates" / "c13_kalmanson_third_pair_refinement.json"


def run_script(*args: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_c13_third_pair_refinement_artifact_summary() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    accounting = payload["branch_accounting"]
    assert accounting["two_pair_unclosed_parent_count"] == 832
    assert accounting["scanned_parent_count"] == 832
    assert accounting["child_extensions_per_parent"] == 56
    assert accounting["third_pair_child_branch_count"] == 46592
    assert accounting["third_pair_child_certified_count"] == 46567
    assert accounting["unclosed_child_branch_count"] == 25
    assert accounting["exhaustive_refinement_of_two_pair_frontier"] is True
    assert accounting["exhaustive_all_orders"] is False
    assert payload["forced_row_count_histogram"] == {"490": 46592}
    assert (
        payload["child_label_digest"]
        == "4dfb8111a92c9c8d429fa349acd109d413a586dc6876848ea7a04cd1fd9f8c32"
    )

    unclosed = payload["unclosed_child_branches"]
    assert isinstance(unclosed, list)
    assert len(unclosed) == 25
    assert unclosed[0]["label"] == "third_pair_child_07723"
    assert unclosed[0]["parent_label"] == "partial_branch_1244"
    assert unclosed[-1]["label"] == "third_pair_child_42595"
    assert unclosed[-1]["parent_label"] == "partial_branch_5284"


def test_c13_third_pair_refinement_small_replay() -> None:
    payload = run_script(
        "--max-parents",
        "2",
        "--closed-example-count",
        "3",
        "--json",
    )

    accounting = payload["branch_accounting"]
    assert accounting["two_pair_unclosed_parent_count"] == 832
    assert accounting["scanned_parent_count"] == 2
    assert accounting["third_pair_child_branch_count"] == 112
    assert accounting["third_pair_child_certified_count"] == 112
    assert accounting["unclosed_child_branch_count"] == 0
    assert accounting["exhaustive_refinement_of_two_pair_frontier"] is False
    assert accounting["exhaustive_all_orders"] is False
    assert payload["forced_row_count_histogram"] == {"490": 112}

    examples = payload["closed_certificate_examples"]
    assert isinstance(examples, list)
    assert len(examples) == 3
    for example in examples:
        assert isinstance(example, dict)
        summary = example["certificate_summary"]
        assert isinstance(summary, dict)
        assert summary["zero_sum_verified"] is True
        assert summary["positive_inequalities"] > 0


@pytest.mark.artifact
@pytest.mark.slow
def test_c13_third_pair_refinement_full_replay_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert artifact["branch_accounting"] == payload["branch_accounting"]
    assert artifact["forced_row_count_histogram"] == payload["forced_row_count_histogram"]
    assert artifact["child_label_digest"] == payload["child_label_digest"]
    assert artifact["unclosed_child_branches"] == payload["unclosed_child_branches"]
    assert (
        sum(payload["closed_support_size_histogram"].values())
        == payload["branch_accounting"]["third_pair_child_certified_count"]
    )
