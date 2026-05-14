from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_block6_terminal_crossing_vertex_circle_sample import (
    FULL_SWEEP_OUT,
    assert_expected,
    assert_expected_full_sweep,
    assert_expected_packet,
    audit,
    sample_packet_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_block6_terminal_crossing_vertex_circle_sample() -> None:
    payload = audit()

    assert_expected(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert "not a proof" in payload["claim_scope"]
    assert payload["summary"]["terminal_extensions_examined"] == 100
    assert payload["summary"]["total_crossing_orders"] == 440
    assert payload["summary"]["vertex_circle_order_status_counts"] == {
        "self_edge": 440,
    }
    assert payload["first_clean_extension_record"] is None


def test_block6_terminal_crossing_vertex_circle_sample_second_window() -> None:
    payload = audit(offset=100)

    assert_expected(payload)
    assert payload["terminal_extension_offset"] == 100
    assert payload["summary"]["terminal_extensions_examined"] == 100
    assert payload["summary"]["total_crossing_orders"] == 356
    assert payload["summary"]["vertex_circle_order_status_counts"] == {
        "self_edge": 356,
    }
    assert payload["first_clean_extension_record"] is None


def test_block6_terminal_crossing_vertex_circle_sample_packet() -> None:
    payload = sample_packet_payload()

    assert_expected_packet(payload)
    assert payload["summary"]["sample_window_count"] == 2
    assert payload["summary"]["terminal_extensions_examined"] == 200
    assert payload["summary"]["total_crossing_orders"] == 796
    assert payload["summary"]["vertex_circle_order_status_counts"] == {
        "self_edge": 796,
    }


def test_block6_terminal_crossing_vertex_circle_full_sweep_artifact() -> None:
    payload = json.loads(FULL_SWEEP_OUT.read_text(encoding="utf-8"))

    assert_expected_full_sweep(payload)
    assert payload["summary"]["terminal_extensions_examined"] == 105978
    assert payload["summary"]["total_crossing_orders"] == 385517
    assert payload["summary"]["vertex_circle_order_status_counts"] == {
        "self_edge": 384318,
        "strict_cycle": 1199,
    }


def test_block6_terminal_crossing_vertex_circle_sample_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_terminal_crossing_vertex_circle_sample.py",
            "--offset",
            "100",
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


def test_block6_terminal_crossing_vertex_circle_sample_packet_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_terminal_crossing_vertex_circle_sample.py",
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
