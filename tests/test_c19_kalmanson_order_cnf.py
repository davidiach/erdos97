from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.export_c19_kalmanson_order_cnf import (
    DEFAULT_ARTIFACT,
    assert_expected,
    before_literal,
    check_cnf,
    check_artifact,
    diagnostic_payload,
    dimacs_from_certificate,
    dimacs_text,
    pair_variable,
    source_clauses,
)


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


def test_c19_kalmanson_order_cnf_summary_matches_artifact() -> None:
    payload = diagnostic_payload()

    assert_expected(payload)
    check_artifact(DEFAULT_ARTIFACT, payload)
    assert payload["source_certificate"]["pattern"] == {
        "circulant_offsets": [-8, -3, 5, 9],
        "n": 19,
        "name": "C19_skew",
    }
    assert payload["encoding"]["variable_count"] == 171
    assert payload["encoding"]["clause_count"] == 13813
    assert payload["encoding"]["transitivity_clause_count"] == 5814
    assert payload["validation"]["dimacs_header"] == "p cnf 171 13813"
    assert payload["validation"]["dimacs_sha256"] == (
        "dd4b8f429fea232bf09ff878342d7a28f4e9b6e743c99cd1b48f681d0f9ec450"
    )


def test_c19_kalmanson_order_cnf_literal_mapping() -> None:
    assert pair_variable(0, 1, 19) == 1
    assert pair_variable(0, 18, 19) == 18
    assert pair_variable(1, 2, 19) == 19
    assert before_literal(0, 18, 19) == 18
    assert before_literal(18, 0, 19) == -18


def test_c19_kalmanson_order_cnf_dimacs_shape() -> None:
    certificate_path = ROOT / "data/certificates/c19_skew_all_orders_kalmanson_z3.json"
    certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
    _, clauses = source_clauses(certificate)
    dimacs = dimacs_from_certificate(certificate_path)
    lines = dimacs.splitlines()

    assert dimacs == dimacs_text(19, clauses)
    assert lines[3] == "p cnf 171 13813"
    assert lines[4] == "1 0"
    assert lines[21] == "18 0"
    assert len(lines) == 13817


def test_c19_kalmanson_order_cnf_roundtrip_file(tmp_path: Path) -> None:
    certificate = ROOT / "data/certificates/c19_skew_all_orders_kalmanson_z3.json"
    cnf_path = tmp_path / "c19.cnf"
    cnf_path.write_text(dimacs_from_certificate(certificate), encoding="utf-8", newline="\n")

    check_cnf(cnf_path, dimacs_from_certificate(certificate))


def test_c19_kalmanson_order_cnf_rejects_tampered_cnf(tmp_path: Path) -> None:
    cnf_path = tmp_path / "bad.cnf"
    cnf_path.write_text("p cnf 1 0\n", encoding="utf-8", newline="\n")

    try:
        check_cnf(cnf_path, "p cnf 1 1\n1 0\n")
    except AssertionError as exc:
        assert "does not match generated DIMACS" in str(exc)
    else:  # pragma: no cover - defensive assertion shape
        raise AssertionError("tampered CNF unexpectedly passed")


def test_c19_kalmanson_order_cnf_rejects_tampering() -> None:
    payload = diagnostic_payload()
    payload["validation"]["dimacs_sha256"] = "0" * 64

    try:
        assert_expected(payload)
    except AssertionError as exc:
        assert "dimacs_sha256" in str(exc)
    else:  # pragma: no cover - defensive assertion shape
        raise AssertionError("tampered CNF summary unexpectedly passed")


def test_c19_kalmanson_order_cnf_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/export_c19_kalmanson_order_cnf.py",
            "--assert-expected",
            "--check-artifact",
            "reports/c19_kalmanson_order_cnf_summary.json",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["status"] == "C19_ORDER_CNF_EXPORT_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "EXACT_CERTIFICATE_DIAGNOSTIC"


def test_c19_kalmanson_order_cnf_cli_write_and_check_cnf(tmp_path: Path) -> None:
    cnf_path = tmp_path / "c19.cnf"

    write_result = subprocess.run(
        [
            sys.executable,
            "scripts/export_c19_kalmanson_order_cnf.py",
            "--write-cnf",
            str(cnf_path),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert write_result.returncode == 0
    assert write_result.stderr == ""
    assert cnf_path.exists()

    check_result = subprocess.run(
        [
            sys.executable,
            "scripts/export_c19_kalmanson_order_cnf.py",
            "--check-cnf",
            str(cnf_path),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert check_result.returncode == 0
    assert check_result.stderr == ""
    assert "matches generated DIMACS" in check_result.stdout
