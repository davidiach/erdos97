"""Regression tests for the merged round-two Kalmanson certificates."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_kalmanson_certificate.py"
C19 = ROOT / "data" / "certificates" / "round2" / "c19_kalmanson_known_order_unsat.json"
C17_TRANSLATION = ROOT / "data" / "certificates" / "round2" / "c17_skew_kalmanson_from_ptolemy_method_note.json"


def load_module():
    spec = importlib.util.spec_from_file_location("check_kalmanson_certificate", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_c19_kalmanson_certificate_cli() -> None:
    result = subprocess.run([sys.executable, str(SCRIPT), str(C19)], check=True, text=True, capture_output=True)
    assert "certificate OK" in result.stdout
    assert "pattern=C19_skew n=19" in result.stdout
    assert "positive inequalities=94" in result.stdout
    assert "distance classes after selected equalities=114" in result.stdout
    assert "max weight=334665404" in result.stdout


def test_c19_kalmanson_certificate_exact_summary() -> None:
    module = load_module()
    summary = module.check_certificate_file(C19)
    assert summary.pattern == "C19_skew"
    assert summary.n == 19
    assert summary.positive_inequalities == 94
    assert summary.distance_classes_after_selected_equalities == 114
    assert summary.weight_sum == 6283316065
    assert summary.zero_sum_verified is True


def test_c17_ptolemy_translation_is_valid_kalmanson_certificate() -> None:
    module = load_module()
    summary = module.check_certificate_file(C17_TRANSLATION)
    assert summary.pattern == "C17_skew"
    assert summary.positive_inequalities == 17
    assert summary.max_weight == 1
    assert summary.distance_classes_after_selected_equalities == 85


def test_kalmanson_checker_rejects_wrong_weight_sum() -> None:
    module = load_module()
    cert = json.loads(C19.read_text(encoding="utf-8"))
    cert["weight_sum"] += 1
    try:
        module.check_certificate_dict(cert)
    except ValueError as exc:
        assert "weight_sum" in str(exc)
    else:
        raise AssertionError("expected bad weight_sum to be rejected")
