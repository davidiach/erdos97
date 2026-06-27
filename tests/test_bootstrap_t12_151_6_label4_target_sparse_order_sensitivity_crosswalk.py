from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_bootstrap_t12_151_6_label4_target_sparse_order_sensitivity_crosswalk import (
    ALT_ORDER,
    EXPECTED_ALT_CERTIFICATE_ROW_COUNTS,
    EXPECTED_POTENTIAL_WEIGHT_SUMS,
    build_payload,
    validate_payload,
)


def test_order_sensitivity_crosswalk_check() -> None:
    root = Path(__file__).resolve().parents[1]
    script = (
        root
        / "scripts"
        / "check_bootstrap_t12_151_6_label4_target_sparse_order_sensitivity_crosswalk.py"
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
    assert payload["target_row_key"] == "151:6"
    assert payload["source_miss_count"] == 3
    assert payload["natural_order_current_row_family_size_each"] == [255]
    assert payload["natural_order_potential_weight_sum_each"] == (
        EXPECTED_POTENTIAL_WEIGHT_SUMS
    )
    assert payload["alternate_order"] == ALT_ORDER
    assert payload["alternate_order_certificate_row_count_each"] == (
        EXPECTED_ALT_CERTIFICATE_ROW_COUNTS
    )
    assert payload["current_row_family_all_order_route_ready"] is False
    assert payload["all_order_obstruction_proved"] is False
    assert payload["solves_n9"] is False
    assert payload["solves_erdos97"] is False


def test_order_sensitivity_crosswalk_artifact_is_deterministic() -> None:
    root = Path(__file__).resolve().parents[1]
    artifact = (
        root
        / "data"
        / "certificates"
        / "bootstrap_t12_151_6_label4_target_sparse_order_sensitivity_crosswalk.json"
    )
    stored = json.loads(artifact.read_text(encoding="utf-8"))
    assert stored == build_payload()
    assert validate_payload(stored) == []


def test_order_sensitivity_crosswalk_rejects_route_overclaim() -> None:
    payload = build_payload()
    payload["summary"]["all_order_obstruction_proved"] = True
    errors = validate_payload(payload)
    assert "stored payload differs from deterministic regeneration" in errors
