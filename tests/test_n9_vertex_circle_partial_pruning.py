from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_partial_pruning import (
    EXPECTED_MIN_OBSTRUCTION_SIZE_COUNTS,
    EXPECTED_PREFIX_STATUS_COUNTS,
    EXPECTED_SUBSET_STATUS_COUNTS,
    assert_expected_partial_pruning,
    partial_pruning_payload,
)

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.slow


def test_partial_pruning_payload_scope_and_counts() -> None:
    payload = partial_pruning_payload()

    assert_expected_partial_pruning(payload)
    assert payload["validation_status"] == "passed"
    summary = payload["frontier_subset_audit"]
    assert summary["assignment_count"] == 184
    assert summary["subset_count"] == 94_024
    assert summary["subset_status_counts"] == EXPECTED_SUBSET_STATUS_COUNTS
    assert summary["min_obstruction_size_counts"] == EXPECTED_MIN_OBSTRUCTION_SIZE_COUNTS
    assert summary["stored_row_order_prefix_status_counts"] == EXPECTED_PREFIX_STATUS_COUNTS
    assert summary["extension_violations"] == 0
    assert summary["checker_replay_status_mismatches"] == 0
    assert "stored frontier assignment subsets" in payload["claim_scope"]
    assert "does not prove frontier coverage" in payload["claim_scope"]
    assert "counterexample" in payload["claim_scope"]


def test_partial_pruning_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_partial_pruning.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    parsed = json.loads(result.stdout)
    summary = parsed["frontier_subset_audit"]
    assert parsed["validation_status"] == "passed"
    assert summary["subset_status_counts"] == {
        "ok": 35418,
        "self_edge": 24890,
        "strict_cycle": 33716,
    }
    assert summary["min_obstruction_size_counts"] == {"3": 182, "4": 2}
    assert summary["extension_violations"] == 0
    assert summary["checker_replay_status_mismatches"] == 0
