from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from erdos97.json_io import load_json
from scripts.check_fragile_cycle_three_halo_deep_frontier import (
    summary_json_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_fragile_cycle_three_halo_deep_frontier.py"
ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "fragile_cycle_three_halo_deep_frontier.json"
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


def test_stored_artifact_has_compact_summary() -> None:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)
    summary = summary_json_payload(payload)
    assert summary["summary"]["clean_eight_row_state_count"] == 13
    assert summary["summary"]["forced_ninth_row_state_count"] == 2
    assert summary["minimum_obstruction_core_status_counts"] == {
        "self_edge": 2,
        "strict_cycle": 4,
    }
