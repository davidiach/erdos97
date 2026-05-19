from __future__ import annotations

import subprocess
import sys
from fractions import Fraction
from pathlib import Path

from scripts.check_k4e_kalmanson_stretch_audit import (
    PATTERNS,
    QSqrt3,
    audit_pattern,
    class_name,
)


ROOT = Path(__file__).resolve().parents[1]


def test_qsqrt3_signs_are_exact() -> None:
    assert QSqrt3(Fraction(-1), Fraction(1)).sign() == 1
    assert QSqrt3(Fraction(2), Fraction(-1)).sign() == 1
    assert QSqrt3(Fraction(1), Fraction(-1)).sign() == -1
    assert QSqrt3(Fraction(-2), Fraction(1)).sign() == -1


def test_n10_frontier_k4e_kalmanson_certificate() -> None:
    n, rows = PATTERNS["n10_frontier"]
    audit = audit_pattern("n10_frontier", n, rows)

    assert len(audit.k4_obstructions) == 0
    assert len(audit.codegree_obstructions) == 0
    assert len(audit.k4e_relations) == 2
    assert len(audit.stretch_certificates) == 3

    first = audit.stretch_certificates[0]
    assert first.kind == "K1"
    assert first.quad == (0, 1, 4, 6)
    assert class_name(first.rel.source) == "Q02"
    assert class_name(first.rel.target) == "Q26"
    assert first.diff[first.rel.source] == QSqrt3(Fraction(-1), Fraction(1))


def test_case2_diagnostic_k4e_kalmanson_counts() -> None:
    n, rows = PATTERNS["case2_diagnostic"]
    audit = audit_pattern("case2_diagnostic", n, rows)

    assert len(audit.k4_obstructions) == 0
    assert len(audit.codegree_obstructions) == 0
    assert len(audit.k4e_relations) == 3
    assert len(audit.stretch_certificates) == 24


def test_k4e_kalmanson_stretch_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_k4e_kalmanson_stretch_audit.py",
            "--pattern",
            "n10_frontier",
            "--assert-expected",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "K4-e relations extracted: 2" in result.stdout
    assert "K4-e/Kalmanson stretch contradictions: 3" in result.stdout
    assert "OK: expected K4-e/Kalmanson stretch audit verified" in result.stdout
