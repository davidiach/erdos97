"""Regression tests for Kalmanson certificate support diagnostics."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_kalmanson_certificates.py"
ARTIFACT = ROOT / "reports" / "kalmanson_certificate_diagnostics.json"
C19_COMPACT_VS_LEGACY = ROOT / "reports" / "c19_kalmanson_compact_vs_legacy.json"


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


def test_c19_compact_vs_legacy_diagnostic_matches_artifact() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--c19-compact-vs-legacy",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    artifact = json.loads(C19_COMPACT_VS_LEGACY.read_text(encoding="utf-8"))

    assert artifact == payload
    assert payload["trust"] == "EXACT_CERTIFICATE_DIAGNOSTIC"
    assert payload["status"] == "FIXED_ORDER_CERTIFICATE_COMPARISON_ONLY"
    for side in ("legacy", "compact"):
        assert payload[side]["pattern"] == "C19_skew"
        assert payload[side]["n"] == 19
        assert payload[side]["circulant_offsets"] == [-8, -3, 5, 9]
    assert payload["compact"]["positive_inequalities"] == 2
    assert payload["compact"]["weight_stats"]["sum"] == 2
    assert payload["compact"]["weight_stats"]["max"] == 1
    assert payload["compact"]["zero_sum_verified"] is True
    assert payload["legacy"]["positive_inequalities"] == 94
    assert payload["legacy"]["weight_stats"]["sum"] == 6_283_316_065
    assert payload["legacy"]["weight_stats"]["max"] == 334_665_404
    assert payload["legacy"]["zero_sum_verified"] is True
    assert payload["comparison"]["same_pattern"] is True
    assert payload["comparison"]["same_cyclic_order"] is True
    assert payload["comparison"]["support_signature_overlap_count"] == 0
    assert payload["comparison"]["compact_support_subset_of_legacy"] is False
