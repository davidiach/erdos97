"""Regression tests for the bounded C13 Kalmanson prefix branch pilot."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "branch_c13_kalmanson_prefix_pilot.py"
ARTIFACT = ROOT / "data" / "certificates" / "c13_kalmanson_prefix_branch_pilot.json"


def test_c13_kalmanson_prefix_branch_pilot_replays_stable_closures() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert artifact["branch_accounting"] == payload["branch_accounting"]
    assert artifact["parameters"] == payload["parameters"]
    accounting = payload["branch_accounting"]
    assert accounting["canonical_boundary_state_count"] == 5940
    assert accounting["prefix_pruned_extension_count"] == 66
    assert accounting["closed_by_kalmanson_certificate_count"] == 12
    assert accounting["exhaustive_all_orders"] is False

    for case, artifact_case in zip(payload["cases"], artifact["cases"]):
        assert case["label"] == artifact_case["label"]
        assert case["boundary_left"] == artifact_case["boundary_left"]
        assert (
            case["boundary_right_reflection_side"]
            == artifact_case["boundary_right_reflection_side"]
        )
        assert case["status"] == "EXACT_KALMANSON_CERTIFICATE_FOUND"
        assert case["certificate_summary"]["zero_sum_verified"] is True
        assert case["certificate_summary"]["positive_inequalities"] > 0
        assert (
            case["certificate_summary"]["distance_classes_after_selected_equalities"]
            == 39
        )
