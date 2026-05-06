"""Regression tests for the sampled C19 fourth-pair Kalmanson refinement."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

from c19_replay_helpers import assert_c19_replay_matches_artifact

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "refine_c19_kalmanson_sampled_fourth_pair.py"
ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "c19_kalmanson_sampled_fourth_pair_refinement.json"
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


def test_c19_sampled_fourth_pair_refinement_artifact_summary() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    accounting = payload["branch_accounting"]
    assert accounting["sampled_prefix_frontier_parent_count"] == 28
    assert accounting["scanned_parent_count"] == 28
    assert accounting["fourth_pair_children_per_parent"] == 132
    assert accounting["fourth_pair_child_branch_count"] == 3696
    assert accounting["fourth_pair_child_certified_count"] == 3643
    assert accounting["unclosed_fourth_pair_child_branch_count"] == 53
    assert accounting["sampled_prefix_parents_closed_by_fourth_refinement"] == 13
    assert accounting["sampled_prefix_parents_still_unclosed_after_fourth_refinement"] == 15
    assert accounting["exhaustive_refinement_of_sampled_prefix_frontier"] is True
    assert accounting["exhaustive_all_orders"] is False

    combined = payload["combined_sample_accounting"]
    assert combined["sampled_prefix_branches_in_prior_pilot"] == 128
    assert combined["sampled_prefix_branches_closed_directly_by_prior_pilot"] == 100
    assert combined["sampled_prefix_branches_refined_here"] == 28
    assert combined["sampled_prefix_branches_closed_by_fourth_pair_subdivision"] == 13
    assert combined["sampled_prefix_branches_remaining_unclosed_after_fourth_pair"] == 15

    assert payload["forced_row_count_histogram"] == {"1932": 3696}
    assert (
        payload["fourth_child_label_digest"]
        == "8a6276f5a27044b79b6ac2bb0d4b88612051d07738633d56a0c966409a923a90"
    )

    unclosed = payload["unclosed_fourth_pair_child_branches"]
    assert isinstance(unclosed, list)
    assert len(unclosed) == 53
    assert unclosed[0]["label"] == "c19_fourth_pair_child_0044"
    assert unclosed[0]["sampled_parent_label"] == "c19_prefix_branch_0013"
    assert unclosed[-1]["label"] == "c19_fourth_pair_child_3266"
    assert unclosed[-1]["sampled_parent_label"] == "c19_prefix_branch_0101"

    examples = payload["closed_certificate_examples"]
    assert isinstance(examples, list)
    assert len(examples) == 12
    first = examples[0]
    assert first["label"] == "c19_fourth_pair_child_0000"
    assert first["sampled_parent_label"] == "c19_prefix_branch_0013"
    assert first["certificate_summary"]["zero_sum_verified"] is True
    assert first["certificate_summary"]["forced_inequalities_available"] == 1932


def test_c19_sampled_fourth_pair_refinement_small_replay() -> None:
    payload = run_script(
        "--max-parents",
        "1",
        "--closed-example-count",
        "3",
        "--json",
    )

    accounting = payload["branch_accounting"]
    assert accounting["sampled_prefix_frontier_parent_count"] == 28
    assert accounting["scanned_parent_count"] == 1
    assert accounting["fourth_pair_child_branch_count"] == 132
    assert accounting["fourth_pair_child_certified_count"] == 126
    assert accounting["unclosed_fourth_pair_child_branch_count"] == 6
    assert accounting["sampled_prefix_parents_closed_by_fourth_refinement"] == 0
    assert accounting["sampled_prefix_parents_still_unclosed_after_fourth_refinement"] == 1
    assert accounting["exhaustive_refinement_of_sampled_prefix_frontier"] is False
    assert accounting["exhaustive_all_orders"] is False
    assert payload["forced_row_count_histogram"] == {"1932": 132}
    assert (
        payload["fourth_child_label_digest"]
        == "9c213bf55cd674abfa5a4acede16b559127fd4b2a035228e51334ffcd21d40bf"
    )

    unclosed = payload["unclosed_fourth_pair_child_branches"]
    assert isinstance(unclosed, list)
    assert [row["label"] for row in unclosed] == [
        "c19_fourth_pair_child_0044",
        "c19_fourth_pair_child_0054",
        "c19_fourth_pair_child_0058",
        "c19_fourth_pair_child_0065",
        "c19_fourth_pair_child_0113",
        "c19_fourth_pair_child_0120",
    ]

    examples = payload["closed_certificate_examples"]
    assert isinstance(examples, list)
    assert len(examples) == 3
    for example in examples:
        summary = example["certificate_summary"]
        assert isinstance(summary, dict)
        assert summary["zero_sum_verified"] is True
        assert summary["forced_inequalities_available"] == 1932
        assert summary["positive_inequalities"] > 0


@pytest.mark.artifact
@pytest.mark.slow
def test_c19_sampled_fourth_pair_refinement_full_replay_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert_c19_replay_matches_artifact(payload, artifact)
