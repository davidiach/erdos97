from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_block6_reversed_block_clean_kalmanson import (
    EXPECTED_CLEAN_INDICES,
    OUT,
    assert_expected,
    check_artifact,
    payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_reversed_block_clean_kalmanson_partial_discovery() -> None:
    data = payload(indices=[13, 157])

    assert data["summary"]["source_clean_order_count"] == 2
    assert data["summary"]["obstructed_clean_order_count"] == 2
    assert data["summary"]["clean_order_indices"] == [13, 157]
    assert data["summary"]["strict_rows_total"] == 37
    assert data["summary"]["weight_sum_total"] == 1240


def test_reversed_block_clean_kalmanson_artifact_replays() -> None:
    data = check_artifact()

    assert_expected(data)
    assert data["summary"]["clean_order_indices"] == EXPECTED_CLEAN_INDICES
    assert data["summary"]["obstructed_clean_order_count"] == 16
    assert "not a counterexample" in data["claim_scope"]


def test_reversed_block_clean_kalmanson_artifact_has_stored_certificates() -> None:
    data = json.loads(OUT.read_text(encoding="utf-8"))

    assert len(data["certificate_records"]) == 16
    assert data["certificate_records"][11]["index"] == 157
    assert data["certificate_records"][11]["strict_rows"] == 7
    assert data["certificate_records"][11]["weight_sum"] == 8


def test_reversed_block_clean_kalmanson_cli_check() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_reversed_block_clean_kalmanson.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
