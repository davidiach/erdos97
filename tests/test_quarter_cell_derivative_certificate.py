"""Tests for the quarter-cell interval-derivative certificate."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_quarter_cell_derivative_certificate",
    ROOT / "scripts" / "check_quarter_cell_derivative_certificate.py",
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def test_payload_certifies_expected_quarter_cells() -> None:
    payload = MOD.build_payload((8, 12, 16), dps=80)

    assert payload["schema"] == MOD.SCHEMA
    assert payload["status"] == MOD.STATUS
    assert payload["m_values"] == [8, 12, 16]
    assert payload["certified_quarter_cell_m_values"] == [8, 12, 16]
    assert payload["signed_cell_count_per_m"] == 12
    assert payload["certified_cell_count"] == 36
    assert payload["all_certified"] is True
    assert {record["m"] for record in payload["results"]} == {8, 12, 16}
    assert all(record["all_cells_certified"] for record in payload["results"])


def test_payload_keeps_global_nonclaims_explicit() -> None:
    payload = MOD.build_payload((8,), dps=80)

    assert "general proof of Erdos Problem #97" in payload["does_not_claim"]
    assert "counterexample to Erdos Problem #97" in payload["does_not_claim"]
    assert "all-m three-orbit obstruction" in payload["does_not_claim"]
    assert "formal proof-assistant certificate" in payload["does_not_claim"]
    assert "official/global status update" in payload["does_not_claim"]


def test_cli_write_check_roundtrip(tmp_path: pathlib.Path) -> None:
    artifact = tmp_path / "quarter_cell_derivative_certificate.json"

    write = subprocess.run(
        [
            sys.executable,
            "scripts/check_quarter_cell_derivative_certificate.py",
            "--m-values",
            "8,12,16",
            "--artifact",
            str(artifact),
            "--write",
            str(artifact),
            "--assert-expected",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert write.returncode == 0, write.stderr
    stored = json.loads(artifact.read_text(encoding="utf-8"))
    assert stored["certified_cell_count"] == 36

    check = subprocess.run(
        [
            sys.executable,
            "scripts/check_quarter_cell_derivative_certificate.py",
            "--m-values",
            "8,12,16",
            "--artifact",
            str(artifact),
            "--check",
            "--assert-expected",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert check.returncode == 0, check.stderr
