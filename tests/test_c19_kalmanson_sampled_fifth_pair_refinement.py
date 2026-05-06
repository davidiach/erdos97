"""Regression tests for the sampled C19 fifth-pair Kalmanson refinement."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

from c19_replay_helpers import assert_c19_replay_matches_artifact

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "refine_c19_kalmanson_sampled_fifth_pair.py"
ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "c19_kalmanson_sampled_fifth_pair_refinement.json"
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


def test_c19_sampled_fifth_pair_refinement_artifact_summary() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    accounting = payload["branch_accounting"]
    assert accounting["sampled_fourth_pair_frontier_parent_count"] == 53
    assert accounting["scanned_parent_count"] == 53
    assert accounting["fifth_pair_children_per_parent"] == 90
    assert accounting["fifth_pair_child_branch_count"] == 4770
    assert accounting["fifth_pair_child_certified_count"] == 4770
    assert accounting["unclosed_fifth_pair_child_branch_count"] == 0
    assert accounting["fourth_pair_parents_closed_by_fifth_refinement"] == 53
    assert accounting["fourth_pair_parents_still_unclosed_after_fifth_refinement"] == 0
    assert accounting["sampled_prefix_parents_closed_by_fifth_refinement"] == 15
    assert accounting["exhaustive_refinement_of_sampled_fourth_pair_frontier"] is True
    assert accounting["exhaustive_all_orders"] is False

    combined = payload["combined_sample_accounting"]
    assert combined["sampled_prefix_branches_in_prior_pilot"] == 128
    assert combined["sampled_prefix_branches_closed_directly_by_prior_pilot"] == 100
    assert combined["sampled_prefix_branches_closed_by_fourth_pair_subdivision"] == 13
    assert combined["sampled_prefix_branches_closed_by_fifth_pair_subdivision"] == 15
    assert combined["sampled_prefix_branches_closed_after_fifth_pair"] == 128
    assert combined["sampled_prefix_branches_remaining_after_fifth_pair"] == 0
    assert combined["sampled_fourth_pair_children_refined_here"] == 53
    assert combined["sampled_fourth_pair_children_closed_by_fifth_pair_subdivision"] == 53
    assert combined["sampled_fourth_pair_children_remaining_after_fifth_pair"] == 0

    assert payload["forced_row_count_histogram"] == {"3300": 4770}
    assert (
        payload["fifth_child_label_digest"]
        == "94c4657efb0253fe566cc7fad12c2401658f0fcdc9f1cdca7b44c3d40d497f0b"
    )
    assert payload["unclosed_fifth_pair_child_branches"] == []

    examples = payload["closed_certificate_examples"]
    assert isinstance(examples, list)
    assert len(examples) == 12
    first = examples[0]
    assert first["label"] == "c19_fifth_pair_child_00000"
    assert first["fourth_pair_parent_label"] == "c19_fourth_pair_child_0044"
    assert first["sampled_parent_label"] == "c19_prefix_branch_0013"
    assert first["certificate_summary"]["zero_sum_verified"] is True
    assert first["certificate_summary"]["forced_inequalities_available"] == 3300


def test_c19_sampled_fifth_pair_refinement_small_replay() -> None:
    payload = run_script(
        "--max-parents",
        "1",
        "--closed-example-count",
        "1",
        "--json",
    )

    accounting = payload["branch_accounting"]
    assert accounting["sampled_fourth_pair_frontier_parent_count"] == 53
    assert accounting["scanned_parent_count"] == 1
    assert accounting["fifth_pair_child_branch_count"] == 90
    assert accounting["fifth_pair_child_certified_count"] == 90
    assert accounting["unclosed_fifth_pair_child_branch_count"] == 0
    assert accounting["fourth_pair_parents_closed_by_fifth_refinement"] == 1
    assert accounting["fourth_pair_parents_still_unclosed_after_fifth_refinement"] == 0
    assert accounting["sampled_prefix_parents_closed_by_fifth_refinement"] is None
    assert accounting["exhaustive_refinement_of_sampled_fourth_pair_frontier"] is False
    assert accounting["exhaustive_all_orders"] is False
    assert payload["forced_row_count_histogram"] == {"3300": 90}
    assert (
        payload["fifth_child_label_digest"]
        == "0e31fbb70f268612792c5b70f6fd180f83077bc24464de7fefab1175ccda0dbd"
    )
    assert payload["unclosed_fifth_pair_child_branches"] == []

    examples = payload["closed_certificate_examples"]
    assert isinstance(examples, list)
    assert len(examples) == 1
    summary = examples[0]["certificate_summary"]
    assert summary["zero_sum_verified"] is True
    assert summary["forced_inequalities_available"] == 3300
    assert summary["positive_inequalities"] > 0


@pytest.mark.artifact
@pytest.mark.slow
def test_c19_sampled_fifth_pair_refinement_full_replay_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert_c19_replay_matches_artifact(payload, artifact)
