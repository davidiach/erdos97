from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from erdos97.fragile_cycle_three_halo_vertex_circle import assert_expected_payload
from erdos97.json_io import load_json
from scripts.check_fragile_cycle_three_halo_vertex_circle import (
    summary_json_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_fragile_cycle_three_halo_vertex_circle.py"
ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "fragile_cycle_three_halo_vertex_circle.json"
)


def test_cli_help() -> None:
    checked = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--assert-expected" in checked.stdout


def test_stored_artifact_has_expected_compact_summary() -> None:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)
    assert_expected_payload(payload)
    summary = summary_json_payload(payload)
    assert summary["placement_count"] == 84
    assert summary["aggregate"]["full_vertex_circle_survivor_count"] == 0
