"""Regression tests for the bounded C13 Kalmanson order pilot."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "pilot_c13_kalmanson_orders.py"
ARTIFACT = ROOT / "data" / "certificates" / "c13_kalmanson_bounded_order_pilot.json"


def test_c13_kalmanson_bounded_order_pilot_replays_stable_closures() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--assert-expected",
            "--summary-only",
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
    accounting = payload["branch_accounting"]
    assert accounting["canonical_unique_order_count"] == 7
    assert accounting["closed_by_kalmanson_certificate_count"] == 7
    assert accounting["exhaustive_all_orders"] is False

    by_label = {case["label"]: case for case in payload["cases"]}
    artifact_by_label = {case["label"]: case for case in artifact["cases"]}
    assert set(by_label) == set(artifact_by_label)
    for case in payload["cases"]:
        artifact_case = artifact_by_label[case["label"]]
        assert case["canonical_order"] == artifact_case["canonical_order"]
        assert case["status"] == "EXACT_KALMANSON_CERTIFICATE_FOUND"
        assert case["certificate_summary"]["zero_sum_verified"] is True
        assert case["certificate_summary"]["positive_inequalities"] > 0
        assert (
            case["certificate_summary"]["distance_classes_after_selected_equalities"]
            == 39
        )
