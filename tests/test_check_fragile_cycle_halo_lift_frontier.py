from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_fragile_cycle_halo_lift_frontier.py"
ARTIFACT = ROOT / "data" / "certificates" / "fragile_cycle_halo_lift_frontier.json"


def test_cli_checks_stored_artifact() -> None:
    checked = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--check",
            "--assert-expected",
            "--summary-json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(checked.stdout)
    assert payload["two_halos"]["extendable_partial_cover_count"] == 6


def test_cli_rejects_modified_artifact(tmp_path: Path) -> None:
    artifact = tmp_path / "halo_lift.json"
    shutil.copyfile(ARTIFACT, artifact)
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    payload["summary"]["two_halo_extendable_partial_cover_count"] = 7
    artifact.write_text(json.dumps(payload), encoding="utf-8")

    checked = subprocess.run(
        [sys.executable, str(SCRIPT), "--check", "--artifact", str(artifact)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert checked.returncode != 0
    assert "summary.two_halo_extendable_partial_cover_count" in checked.stderr
