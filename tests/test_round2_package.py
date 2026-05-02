"""Smoke test for the merged handoff package entry point."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_round2_certificates.py"


def test_round2_package_checker() -> None:
    result = subprocess.run([sys.executable, str(SCRIPT)], check=True, text=True, capture_output=True)
    payload = json.loads(result.stdout)
    assert payload["c19_kalmanson_promoted"]["zero_sum_verified"] is True
    assert payload["c17_ptolemy_method_note"]["verified_zero_sum"] is True
    assert payload["c17_kalmanson_translation_regression"]["zero_sum_verified"] is True
