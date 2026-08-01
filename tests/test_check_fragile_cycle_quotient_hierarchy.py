from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_fragile_cycle_quotient_hierarchy.py"


def test_cli_write_then_check(tmp_path: Path) -> None:
    artifact = tmp_path / "hierarchy.json"
    write = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--write",
            "--assert-expected",
            "--out",
            str(artifact),
            "--summary-json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    written = json.loads(write.stdout)
    assert written["summary"]["strict_support_levels"] == [1, 2, 4]

    checked = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--check",
            "--assert-expected",
            "--artifact",
            str(artifact),
            "--summary-json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(checked.stdout)
    assert payload["summary"]["all_quotient_certificates_zero_sum"] is True


def test_cli_rejects_modified_artifact(tmp_path: Path) -> None:
    artifact = tmp_path / "hierarchy.json"
    subprocess.run(
        [sys.executable, str(SCRIPT), "--write", "--out", str(artifact)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    payload["summary"]["admissible_partition_count"] = 6
    artifact.write_text(json.dumps(payload), encoding="utf-8")

    checked = subprocess.run(
        [sys.executable, str(SCRIPT), "--check", "--artifact", str(artifact)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert checked.returncode != 0
    assert "admissible_partition_count" in checked.stderr
