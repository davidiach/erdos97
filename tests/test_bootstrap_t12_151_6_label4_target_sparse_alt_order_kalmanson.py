from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_bootstrap_t12_151_6_label4_target_sparse_alt_order_kalmanson import (
    ALT_ORDER,
    build_payload,
    validate_payload,
)


def test_alt_order_kalmanson_check() -> None:
    root = Path(__file__).resolve().parents[1]
    script = (
        root
        / "scripts"
        / "check_bootstrap_t12_151_6_label4_target_sparse_alt_order_kalmanson.py"
    )
    result = subprocess.run(
        [sys.executable, str(script), "--check", "--assert-expected", "--json"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["fixed_cyclic_order"] == list(ALT_ORDER)
    assert payload["source_miss_count"] == 3
    assert payload["certificate_count"] == 3
    assert payload["available_fixed_order_strict_row_count_each"] == [255]
    assert payload["certificate_row_count_each"] == [10, 10, 9]
    assert payload["certificate_weight_sum_each"] == [10, 11, 10]
    assert payload["all_exact_zero_sum_verified"] is True
    assert payload["all_order_obstruction_proved"] is False
    assert payload["solves_n9"] is False
    assert payload["solves_erdos97"] is False


def test_alt_order_kalmanson_artifact_is_deterministic() -> None:
    root = Path(__file__).resolve().parents[1]
    artifact = (
        root
        / "data"
        / "certificates"
        / "bootstrap_t12_151_6_label4_target_sparse_alt_order_kalmanson.json"
    )
    stored = json.loads(artifact.read_text(encoding="utf-8"))
    assert stored == build_payload()
    assert validate_payload(stored) == []


def test_alt_order_kalmanson_rejects_tampered_weight() -> None:
    payload = build_payload()
    payload["certificate_records"][0]["certificate_rows"][0]["weight"] = 2
    errors = validate_payload(payload)
    assert "stored payload differs from deterministic regeneration" in errors
