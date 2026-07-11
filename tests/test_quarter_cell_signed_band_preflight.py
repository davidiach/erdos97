"""Tests for the quarter-cell signed-band turn preflight."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_quarter_cell_signed_band_preflight",
    ROOT / "scripts" / "check_quarter_cell_signed_band_preflight.py",
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def test_signed_case_table_has_all_cells() -> None:
    payload = MOD.build_payload((8, 12, 16), grid=18)

    assert payload["schema"] == MOD.SCHEMA
    assert payload["signed_case_count"] == 12
    assert payload["leading_killer_case_count"] == 12
    assert payload["leading_sign_ok_for_sample_ms"] is True
    assert payload["sampled_fixed_killer_all_negative"] is True
    assert {case["band_case"] for case in payload["signed_cases"]} == {"LL", "LH", "HH"}
    assert {case["killer_turn"] for case in payload["signed_cases"]} == {1, 2, 3}


def test_payload_keeps_open_cells_open() -> None:
    payload = MOD.build_payload((8,), grid=12)

    assert payload["preflight_only_not_certified_m_values"] == [8, 12, 16]
    assert payload["superseded_for_m_values_by"]["m_values"] == [8, 12, 16]
    assert (
        payload["superseded_for_m_values_by"]["artifact"]
        == "data/certificates/quarter_cell_derivative_certificate.json"
    )
    assert "preflight artifact closes m=8,12,16 quarter cells" in payload["does_not_claim"]
    assert "all-m three-orbit obstruction" in payload["does_not_claim"]
    assert "general proof of Erdos Problem #97" in payload["does_not_claim"]
    assert "counterexample to Erdos Problem #97" in payload["does_not_claim"]


def test_payload_rejects_vacuous_sampling_inputs() -> None:
    with pytest.raises(ValueError, match="at least one m-value"):
        MOD.build_payload((), grid=12)
    with pytest.raises(ValueError, match="m >= 8"):
        MOD.build_payload((4,), grid=12)
    with pytest.raises(ValueError, match="m = 0 mod 4"):
        MOD.build_payload((9,), grid=12)
    with pytest.raises(ValueError, match="grid must be at least 2"):
        MOD.build_payload((8,), grid=1)


def test_cli_write_check_roundtrip(tmp_path: pathlib.Path) -> None:
    artifact = tmp_path / "signed_band.json"

    write = subprocess.run(
        [
            sys.executable,
            "scripts/check_quarter_cell_signed_band_preflight.py",
            "--artifact",
            str(artifact),
            "--ms",
            "8",
            "12",
            "--grid",
            "12",
            "--write",
            "--assert-expected",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert write.returncode == 0, write.stderr
    stored = json.loads(artifact.read_text(encoding="utf-8"))
    assert stored["signed_case_count"] == 12

    check = subprocess.run(
        [
            sys.executable,
            "scripts/check_quarter_cell_signed_band_preflight.py",
            "--artifact",
            str(artifact),
            "--ms",
            "8",
            "12",
            "--grid",
            "12",
            "--check",
            "--assert-expected",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert check.returncode == 0, check.stderr


def test_portable_comparison_accepts_libm_tail_drift_only() -> None:
    current = MOD.build_payload((8,), grid=12)
    stored = json.loads(json.dumps(current))
    stored["sample_records"][0]["case_records"][0]["max_killer_turn"] += 8e-18

    MOD._assert_portable_payload_equal(stored, current)


def test_portable_comparison_rejects_semantic_and_material_changes() -> None:
    current = MOD.build_payload((8,), grid=12)

    changed_decision = json.loads(json.dumps(current))
    changed_decision["sampled_fixed_killer_all_negative"] = False
    with pytest.raises(AssertionError, match="exact value mismatch"):
        MOD._assert_portable_payload_equal(changed_decision, current)

    changed_sign = json.loads(json.dumps(current))
    value = changed_sign["sample_records"][0]["case_records"][0]["max_killer_turn"]
    changed_sign["sample_records"][0]["case_records"][0]["max_killer_turn"] = -value
    with pytest.raises(AssertionError, match="sign/zero mismatch"):
        MOD._assert_portable_payload_equal(changed_sign, current)

    changed_float = json.loads(json.dumps(current))
    changed_float["sample_records"][0]["case_records"][0]["max_killer_turn"] *= 1.01
    with pytest.raises(AssertionError, match="material float mismatch"):
        MOD._assert_portable_payload_equal(changed_float, current)


def test_assert_expected_rejects_changes_under_python_optimized_mode() -> None:
    code = """
import importlib.util
import sys
from pathlib import Path

path = Path('scripts/check_quarter_cell_signed_band_preflight.py')
spec = importlib.util.spec_from_file_location('optimized_quarter_cell_check', path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
payload = module.build_payload((8,), grid=12)
payload['status'] = 'INVALID_STATUS'
try:
    module.assert_expected(payload)
except AssertionError:
    raise SystemExit(0)
raise SystemExit(1)
"""
    result = subprocess.run(
        [sys.executable, "-O", "-c", code],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr


def test_cli_default_artifact_check_is_cross_platform_reproducible() -> None:
    check = subprocess.run(
        [
            sys.executable,
            "scripts/check_quarter_cell_signed_band_preflight.py",
            "--check",
            "--assert-expected",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert check.returncode == 0, check.stderr
