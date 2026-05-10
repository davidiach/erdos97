from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from erdos97.quotient_cone import check_quotient_cone_certificate
from scripts.check_block6_survivor_kalmanson_certificate import CERTIFICATE, audit


ROOT = Path(__file__).resolve().parents[1]


def test_block6_survivor_kalmanson_certificate_replays() -> None:
    result = check_quotient_cone_certificate(CERTIFICATE)

    assert result.pattern == "block6_two_block_survivor_extension_3"
    assert result.strict_rows == 31
    assert result.distance_classes == 33
    assert result.weight_sum == 4294
    assert result.max_weight == 402
    assert result.zero_sum_verified is True
    assert result.nonpositive_sum_verified is True
    assert result.combined_nonzero_coefficient_count == 0


def test_block6_survivor_kalmanson_audit_summary() -> None:
    payload = audit()

    assert payload["status"] == "EXACT_OBSTRUCTION_FOR_FIXED_SURVIVOR_AND_FIXED_CYCLIC_ORDER"
    assert payload["strict_rows"] == 31
    assert payload["distance_classes"] == 33
    assert payload["weight_sum"] == 4294
    assert payload["zero_sum_verified"] is True
    assert payload["certificate"]["num_inequalities"] == 31


def test_block6_survivor_kalmanson_certificate_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_survivor_kalmanson_certificate.py",
            "--assert-expected",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "strict rows: 31" in result.stdout
    assert "distance classes: 33" in result.stdout
    assert "OK: expected Kalmanson certificate verified" in result.stdout
