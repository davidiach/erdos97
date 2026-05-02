"""Regression tests for the merged round-two Ptolemy-log method note."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_ptolemy_log_filter.py"
CERT = ROOT / "data" / "certificates" / "round2" / "c17_skew_ptolemy_log_certificate.json"


def load_module():
    spec = importlib.util.spec_from_file_location("check_ptolemy_log_filter", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_c17_ptolemy_log_certificate_verifies() -> None:
    module = load_module()
    cert = module.build_c17_skew_certificate()
    summary = module.verify_certificate_object(cert)
    assert summary["verified_zero_sum"] is True
    assert summary["n"] == 17
    assert summary["distance_class_count"] == 85
    assert summary["ptolemy_log_inequality_count"] == 34
    assert summary["certificate_support_size"] == 17
    assert summary["max_abs_certificate_sum"] == 0
    assert summary["offset_selected_sets_match"] is True


def test_stored_c17_ptolemy_log_certificate_verifies() -> None:
    module = load_module()
    cert = json.loads(CERT.read_text(encoding="utf-8"))
    summary = module.verify_certificate_object(cert)
    assert summary["verified_zero_sum"] is True
    assert summary["pattern"] == "C17_skew"
    assert summary["role"] == "METHOD_NOTE_REGRESSION"
    assert summary["offset_selected_sets_match"] is True


def test_ptolemy_cli_accepts_normalized_data_path() -> None:
    result = subprocess.run([sys.executable, str(SCRIPT), "--certificate", str(CERT), "--summary-json"], check=True, text=True, capture_output=True)
    payload = json.loads(result.stdout)
    assert payload["pattern"] == "C17_skew"
    assert payload["verified_zero_sum"] is True


def test_ptolemy_checker_rejects_offset_selected_set_mismatch() -> None:
    module = load_module()
    cert = json.loads(CERT.read_text(encoding="utf-8"))
    cert["selected_witness_sets"]["0"] = [1, 2, 3, 4]
    try:
        module.verify_certificate_object(cert)
    except ValueError as exc:
        assert "do not match offsets" in str(exc)
    else:
        raise AssertionError("expected offset/selected_witness_sets mismatch to be rejected")
