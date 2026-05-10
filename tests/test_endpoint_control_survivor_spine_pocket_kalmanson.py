from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from erdos97.quotient_cone import check_quotient_cone_certificate
from scripts.check_endpoint_control_survivor_spine_pocket_kalmanson import (
    EXPECTED_MAX_WEIGHTS,
    EXPECTED_STRICT_ROWS,
    EXPECTED_WEIGHT_SUMS,
    assert_expected,
    audit,
    certificate_for_order,
)


ROOT = Path(__file__).resolve().parents[1]


def test_endpoint_control_survivor_spine_pocket_each_certificate_replays() -> None:
    for index in range(5):
        result = check_quotient_cone_certificate(certificate_for_order(index))

        assert result.strict_rows == EXPECTED_STRICT_ROWS[index]
        assert result.weight_sum == EXPECTED_WEIGHT_SUMS[index]
        assert result.max_weight == EXPECTED_MAX_WEIGHTS[index]
        assert result.distance_classes == 25
        assert result.zero_sum_verified is True
        assert result.combined_nonzero_coefficient_count == 0


def test_endpoint_control_survivor_spine_pocket_kalmanson_audit() -> None:
    payload = audit()

    assert payload["crossing_frontier"]["order_count"] == 5
    assert payload["obstructed_order_count"] == 5
    assert [
        summary["strict_rows"] for summary in payload["order_summaries"]
    ] == EXPECTED_STRICT_ROWS
    assert [
        summary["weight_sum"] for summary in payload["order_summaries"]
    ] == EXPECTED_WEIGHT_SUMS
    assert_expected(payload)


def test_endpoint_control_survivor_spine_pocket_kalmanson_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_endpoint_control_survivor_spine_pocket_kalmanson.py",
            "--assert-expected",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "crossing-compatible orders: 5" in result.stdout
    assert "obstructed orders: 5" in result.stdout
    assert "order 0: rows=23 weight_sum=541 zero_sum=True" in result.stdout
    assert "OK: expected spine-pocket Kalmanson certificates verified" in result.stdout
