from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_block6_reversed_block_two_stage_closure import (
    OUT,
    assert_expected,
    check_artifact,
    payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_reversed_block_two_stage_payload_counts() -> None:
    data = payload()

    assert data["summary"]["family_order_count"] == 462
    assert data["summary"]["vertex_circle_closed_order_count"] == 446
    assert data["summary"]["kalmanson_obstructed_clean_order_count"] == 16
    assert data["summary"]["combined_closed_order_count"] == 462
    assert data["summary"]["combined_closure_complete"] is True


def test_reversed_block_two_stage_artifact_replays() -> None:
    data = check_artifact()

    assert_expected(data)
    assert "not a counterexample" in data["claim_scope"]
    assert data["summary"]["source_clean_indices_match"] is True


def test_reversed_block_two_stage_artifact_is_compact() -> None:
    data = json.loads(OUT.read_text(encoding="utf-8"))

    assert len(data["clean_order_crosswalk"]) == 16
    assert "certificate_records" not in data
    assert data["clean_order_crosswalk"][11]["index"] == 157
    assert data["clean_order_crosswalk"][11]["strict_rows"] == 7


def test_reversed_block_two_stage_cli_check() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_block6_reversed_block_two_stage_closure.py",
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
