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
C19_TWO = ROOT / "data" / "certificates" / "round2" / "c19_kalmanson_known_order_two_unsat.json"
C17_TRANSLATION = ROOT / "data" / "certificates" / "round2" / "c17_skew_kalmanson_from_ptolemy_method_note.json"
C13 = ROOT / "data" / "certificates" / "c13_sidon_order_survivor_kalmanson_unsat.json"
C13_TWO = ROOT / "data" / "certificates" / "c13_sidon_order_survivor_kalmanson_two_unsat.json"
C29 = ROOT / "data" / "certificates" / "c29_sidon_fixed_order_kalmanson_165_unsat.json"


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


def test_c19_compact_two_inequality_kalmanson_certificate() -> None:
    module = load_module()
    summary = module.check_certificate_file(C19_TWO)
    assert summary.pattern == "C19_skew"
    assert summary.n == 19
    assert summary.positive_inequalities == 2
    assert summary.distance_classes_after_selected_equalities == 114
    assert summary.weight_sum == 2
    assert summary.max_weight == 1
    assert summary.zero_sum_verified is True


def test_c17_ptolemy_translation_is_valid_kalmanson_certificate() -> None:
    module = load_module()
    summary = module.check_certificate_file(C17_TRANSLATION)
    assert summary.pattern == "C17_skew"
    assert summary.positive_inequalities == 17
    assert summary.max_weight == 1
    assert summary.distance_classes_after_selected_equalities == 85


def test_c13_sidon_survivor_kalmanson_certificate() -> None:
    module = load_module()
    summary = module.check_certificate_file(C13)
    assert summary.pattern == "C13_sidon_1_2_4_10"
    assert summary.positive_inequalities == 34
    assert summary.distance_classes_after_selected_equalities == 39
    assert summary.weight_sum == 17463
    assert summary.max_weight == 1322


def test_c13_compact_two_inequality_kalmanson_certificate() -> None:
    module = load_module()
    summary = module.check_certificate_file(C13_TWO)
    assert summary.pattern == "C13_sidon_1_2_4_10"
    assert summary.positive_inequalities == 2
    assert summary.distance_classes_after_selected_equalities == 39
    assert summary.weight_sum == 2
    assert summary.max_weight == 1


def test_c29_fixed_order_kalmanson_certificate() -> None:
    module = load_module()
    summary = module.check_certificate_file(C29)
    assert summary.pattern == "C29_sidon_1_3_7_15"
    assert summary.n == 29
    assert summary.positive_inequalities == 165
    assert summary.distance_classes_after_selected_equalities == 319
    assert summary.weight_sum == 504300794
    assert summary.max_weight == 15835921
    assert summary.zero_sum_verified is True


def test_find_kalmanson_certificate_reproduces_c13_summary() -> None:
    finder = ROOT / "scripts" / "find_kalmanson_certificate.py"
    result = subprocess.run(
        [
            sys.executable,
            str(finder),
            "--name",
            "C13_sidon_1_2_4_10",
            "--n",
            "13",
            "--offsets",
            "1,2,4,10",
            "--order",
            "5,0,10,8,9,7,4,6,2,11,12,3,1",
            "--assert-found",
            "--summary-json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    summary = json.loads(result.stdout)
    assert summary["pattern"] == "C13_sidon_1_2_4_10"
    assert summary["positive_inequalities"] == 34
    assert summary["zero_sum_verified"] is True


def test_find_kalmanson_two_certificate_reproduces_c19_summary() -> None:
    finder = ROOT / "scripts" / "find_kalmanson_two_certificate.py"
    result = subprocess.run(
        [
            sys.executable,
            str(finder),
            "--name",
            "C19_skew",
            "--n",
            "19",
            "--offsets=-8,-3,5,9",
            "--order",
            "18,10,7,17,6,3,5,9,14,11,2,13,4,16,12,15,0,8,1",
            "--assert-found",
            "--summary-json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    summary = json.loads(result.stdout)
    assert summary["pattern"] == "C19_skew"
    assert summary["positive_inequalities"] == 2
    assert summary["max_weight"] == 1
    assert summary["inverse_pair_candidates"] >= 1
    assert summary["zero_sum_verified"] is True


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
