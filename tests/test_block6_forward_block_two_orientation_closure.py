from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_block6_forward_block_two_orientation_closure import (
    OUT,
    assert_expected,
    check_artifact,
    payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_two_orientation_payload_counts() -> None:
    data = payload()

    assert data["summary"]["total_family_order_count"] == 924
    assert data["summary"]["forward_second_block_closed_order_count"] == 462
    assert data["summary"]["reversed_second_block_closed_order_count"] == 462
    assert data["summary"]["vertex_circle_closed_order_count"] == 908
    assert data["summary"]["kalmanson_after_vertex_circle_escape_count"] == 16
    assert data["summary"]["combined_closure_complete"] is True


def test_two_orientation_artifact_replays() -> None:
    data = check_artifact()

    assert_expected(data)
    assert "does not include first-block-reversed" in data["claim_scope"]
    assert "proof of Erdos Problem #97" in data["claim_scope"]


def test_two_orientation_artifact_is_compact() -> None:
    data = json.loads(OUT.read_text(encoding="utf-8"))

    assert len(data["family_crosswalk"]) == 2
    assert "sample_records" not in data
    assert "clean_order_crosswalk" not in data
    assert data["family_crosswalk"][0]["closure_methods"] == {
        "vertex_circle_quotient": 462
    }
    assert data["family_crosswalk"][1]["closure_methods"] == {
        "vertex_circle_quotient": 446,
        "kalmanson_after_vertex_circle_escape": 16,
    }


def test_two_orientation_cli_check() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_forward_block_two_orientation_closure.py",
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
