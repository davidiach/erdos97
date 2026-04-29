from __future__ import annotations

import importlib.util
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_p24_metric_linear_nonconvex.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_p24_metric_linear_nonconvex", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_p24_metric_linear_nonconvex_exact_facts() -> None:
    verifier = load_verifier()

    result = verifier.run_checks()

    assert result["equal_distance_rows"] is True
    assert result["max_support_intersection"] == 1
    assert result["even_turns"] == {verifier.Q3(Fraction(1, 2))}
    assert result["odd_turns"] == {verifier.Q3(Fraction(0), Fraction(-1, 2))}
    assert result["jacobian_shape"] == (72, 48)
    assert result["jacobian_rank"] == 44


def test_p24_metric_linear_nonconvex_cli_reports_negative_control() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT)],
        check=True,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )

    assert "Equal-distance rows: PASS" in completed.stdout
    assert "Linearity |S_i cap S_k| <= 1: PASS; max intersection = 1" in completed.stdout
    assert "Convexity failure by alternating turn signs: PASS" in completed.stdout
    assert "Exact Jacobian rank: 44" in completed.stdout
    assert "All checks passed." in completed.stdout
