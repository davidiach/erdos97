from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from erdos97.json_io import load_json
from scripts.check_fragile_cycle_three_halo_kalmanson_endgame import (
    summary_json_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "scripts" / "check_fragile_cycle_three_halo_kalmanson_endgame.py"
)
ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "fragile_cycle_three_halo_kalmanson_endgame.json"
)


def test_cli_help() -> None:
    checked = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "PYTHONPATH": str(ROOT / "src")},
    )
    assert "--assert-expected" in checked.stdout


def test_stored_artifact_has_compact_summary() -> None:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)
    summary = summary_json_payload(payload)
    assert summary["summary"]["deep_states_checked"] == 13
    assert summary["summary"]["states_killed_by_one_strict_self_edge"] == 11
    assert summary["summary"]["states_killed_by_two_strict_inverse_pair"] == 2
