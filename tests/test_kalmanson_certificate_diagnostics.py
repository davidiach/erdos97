"""Regression tests for Kalmanson certificate support diagnostics."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_kalmanson_certificates.py"
ARTIFACT = ROOT / "reports" / "kalmanson_certificate_diagnostics.json"


def test_kalmanson_certificate_diagnostics_match_artifact() -> None:
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
    by_pattern = {row["pattern"]: row for row in payload["certificates"]}
    c13 = by_pattern["C13_sidon_1_2_4_10"]
    c19 = by_pattern["C19_skew"]

    assert c13["positive_inequalities"] == 34
    assert c13["distance_classes_after_selected_equalities"] == 39
    assert c13["support_nullity_mod_primes"] == {
        "1000003": 1,
        "1000033": 1,
        "1000037": 1,
    }
    assert c19["positive_inequalities"] == 94
    assert c19["distance_classes_after_selected_equalities"] == 114
    assert c19["max_abs_weighted_sum_coefficient"] == 0
