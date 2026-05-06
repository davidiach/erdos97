"""Regression tests for the bounded C19 prefix-forced Kalmanson pilot."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

from c19_replay_helpers import assert_c19_replay_matches_artifact

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "pilot_c19_kalmanson_prefix_branches.py"
ARTIFACT = ROOT / "data" / "certificates" / "c19_kalmanson_prefix_branch_pilot.json"


def run_script(*args: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_c19_prefix_branch_pilot_matches_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert_c19_replay_matches_artifact(payload, artifact)
    accounting = payload["branch_accounting"]
    assert accounting["raw_boundary_state_count"] == 13366080
    assert accounting["canonical_boundary_state_count"] == 6683040
    assert accounting["sampled_branch_count"] == 128
    assert accounting["sampled_branch_certified_count"] == 100
    assert accounting["sampled_branch_unclosed_count"] == 28
    assert accounting["exhaustive_prefix_scan"] is False
    assert accounting["exhaustive_all_orders"] is False
    assert payload["forced_row_count_histogram"] == {"910": 128}
    assert (
        payload["sampled_branch_label_digest"]
        == "79fa7c236754647fd7ed844475896ee61ff1eef0ab66c14410221891773db37b"
    )
    support_histogram = payload["closed_support_size_histogram"]
    assert isinstance(support_histogram, dict)
    assert sum(support_histogram.values()) == 100

    closed = payload["closed_certificate_examples"]
    assert isinstance(closed, list)
    assert len(closed) == 12
    assert closed[0]["label"] == "c19_prefix_branch_0000"
    assert closed[0]["certificate_summary"]["zero_sum_verified"] is True
    assert closed[0]["certificate_summary"]["forced_inequalities_available"] == 910

    unclosed = payload["unclosed_branch_examples"]
    assert isinstance(unclosed, list)
    assert len(unclosed) == 12
    assert unclosed[0]["label"] == "c19_prefix_branch_0013"

    unclosed_all = payload["unclosed_sampled_branches"]
    assert isinstance(unclosed_all, list)
    assert len(unclosed_all) == 28
    assert unclosed_all[0]["label"] == "c19_prefix_branch_0013"
    assert unclosed_all[-1]["label"] == "c19_prefix_branch_0109"


def test_c19_prefix_branch_pilot_full_certificate_examples_verify() -> None:
    payload = run_script(
        "--max-branches",
        "16",
        "--closed-example-count",
        "2",
        "--include-certificates",
        "--json",
    )

    examples = payload["closed_certificate_examples"]
    assert isinstance(examples, list)
    assert len(examples) == 2
    for example in examples:
        certificate = example["certificate"]
        assert isinstance(certificate, dict)
        assert certificate["status"] == "EXACT_OBSTRUCTION_FOR_PREFIX_BRANCH_COMPLETIONS"
        assert certificate["num_inequalities"] > 0
        assert certificate["forced_inequalities_available"] == 910
        assert example["certificate_summary"]["zero_sum_verified"] is True
