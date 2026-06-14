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

    assert payload["open_quarter_cells_still_open"] == [8, 12, 16]
    assert "m=8,12,16 quarter cells closed" in payload["does_not_claim"]
    assert "all-m three-orbit obstruction" in payload["does_not_claim"]
    assert "general proof of Erdos Problem #97" in payload["does_not_claim"]
    assert "counterexample to Erdos Problem #97" in payload["does_not_claim"]


def test_payload_rejects_vacuous_sampling_inputs() -> None:
    with pytest.raises(ValueError, match="at least one m-value"):
        MOD.build_payload((), grid=12)
    with pytest.raises(ValueError, match="m >= 8"):
        MOD.build_payload((4,), grid=12)
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
