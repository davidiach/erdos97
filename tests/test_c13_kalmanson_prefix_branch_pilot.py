"""Regression tests for the bounded C13 Kalmanson prefix branch pilot."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "branch_c13_kalmanson_prefix_pilot.py"
ARTIFACT = ROOT / "data" / "certificates" / "c13_kalmanson_prefix_branch_pilot.json"


def test_c13_kalmanson_prefix_branch_pilot_matches_artifact() -> None:
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

    assert artifact == payload
    accounting = payload["branch_accounting"]
    assert accounting["canonical_boundary_state_count"] == 5940
    assert accounting["prefix_pruned_extension_count"] == 66
    assert accounting["closed_by_kalmanson_certificate_count"] == 12
    assert accounting["exhaustive_all_orders"] is False

    for case in payload["cases"]:
        assert case["status"] == "EXACT_KALMANSON_CERTIFICATE_FOUND"
        assert case["certificate_summary"]["zero_sum_verified"] is True
