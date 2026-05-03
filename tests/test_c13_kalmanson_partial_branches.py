"""Regression tests for C13 prefix-forced Kalmanson branch closures."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "certify_c13_kalmanson_partial_branches.py"
ARTIFACT = ROOT / "data" / "certificates" / "c13_kalmanson_partial_branch_closures.json"


def run_script(*args: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_c13_partial_branch_closures_match_artifact() -> None:
    payload = run_script("--assert-expected", "--json")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert artifact["branch_accounting"] == payload["branch_accounting"]
    assert artifact["forced_row_count_histogram"] == payload["forced_row_count_histogram"]
    assert (
        artifact["unclosed_branch_label_digest"]
        == payload["unclosed_branch_label_digest"]
    )
    assert (
        artifact["unclosed_branch_label_examples"]
        == payload["unclosed_branch_label_examples"]
    )
    accounting = payload["branch_accounting"]
    assert accounting["partial_branch_certified_count"] == 5108
    assert accounting["unclosed_branch_count"] == 832
    assert accounting["exhaustive_two_pair_boundary_scan"] is True
    assert accounting["exhaustive_all_orders"] is False
    assert payload["forced_row_count_histogram"] == {"170": 5940}
    assert (
        sum(payload["closed_support_size_histogram"].values())
        == accounting["partial_branch_certified_count"]
    )
    examples = payload["unclosed_branch_label_examples"]
    assert isinstance(examples, dict)
    assert examples["first"][0] == "partial_branch_0012"
    assert examples["last"][-1] == "partial_branch_5915"


def test_c13_partial_branch_full_certificate_examples_verify() -> None:
    payload = run_script(
        "--max-branches",
        "12",
        "--closed-example-count",
        "2",
        "--include-certificates",
        "--json",
    )

    examples = payload["closed_certificate_examples"]
    assert isinstance(examples, list)
    assert len(examples) == 2
    for example in examples:
        assert isinstance(example, dict)
        certificate = example["certificate"]
        assert isinstance(certificate, dict)
        assert certificate["status"] == "EXACT_OBSTRUCTION_FOR_PREFIX_BRANCH_COMPLETIONS"
        assert certificate["num_inequalities"] > 0
        assert certificate["forced_inequalities_available"] == 170
