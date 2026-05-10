from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from erdos97.quotient_cone import check_quotient_cone_certificate
from scripts.check_endpoint_control_survivor_kalmanson_certificate import (
    CERTIFICATE,
    audit,
)


ROOT = Path(__file__).resolve().parents[1]


def test_endpoint_control_survivor_kalmanson_certificate_replays() -> None:
    result = check_quotient_cone_certificate(CERTIFICATE)

    assert (
        result.status == "EXACT_OBSTRUCTION_FOR_FIXED_SURVIVOR_AND_FIXED_CYCLIC_ORDER"
    )
    assert result.strict_rows == 22
    assert result.distance_classes == 25
    assert result.weight_sum == 89
    assert result.max_weight == 11
    assert result.zero_sum_verified is True
    assert result.combined_nonzero_coefficient_count == 0


def test_endpoint_control_survivor_kalmanson_audit_summary() -> None:
    payload = audit()

    assert payload["strict_rows"] == 22
    assert payload["distance_classes"] == 25
    assert payload["weight_sum"] == 89
    assert payload["max_weight"] == 11
    assert payload["zero_sum_verified"] is True
    assert payload["combined_nonzero_coefficient_count"] == 0


def test_endpoint_control_survivor_kalmanson_certificate_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_endpoint_control_survivor_kalmanson_certificate.py",
            "--assert-expected",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "strict rows: 22" in result.stdout
    assert "distance classes: 25" in result.stdout
    assert "weight sum: 89" in result.stdout
    assert "zero sum verified: True" in result.stdout
    assert "OK: expected Kalmanson certificate verified" in result.stdout
