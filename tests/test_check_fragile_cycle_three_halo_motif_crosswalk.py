from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from erdos97.json_io import load_json
from scripts.check_fragile_cycle_three_halo_motif_crosswalk import (
    summary_json_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_fragile_cycle_three_halo_motif_crosswalk.py"
ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "fragile_cycle_three_halo_motif_crosswalk.json"
)


def test_cli_help() -> None:
    checked = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
    )
    assert "--assert-expected" in checked.stdout


def test_stored_artifact_has_compact_summary() -> None:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)
    summary = summary_json_payload(payload)
    assert summary["summary"]["source_states_checked"] == 13
    assert summary["summary"]["equilateral_hinge_states"] == 11
    assert summary["summary"]["hinge_free_splice_states"] == 2
