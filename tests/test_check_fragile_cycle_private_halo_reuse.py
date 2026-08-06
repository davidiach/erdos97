from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_fragile_cycle_private_halo_reuse.py"
SUBPROCESS_ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def test_cli_write_then_check(tmp_path: Path) -> None:
    artifact = tmp_path / "private_halo_reuse.json"
    write = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPT),
            "--write",
            "--assert-expected",
            "--out",
            str(artifact),
            "--summary-json",
        ],
        cwd=ROOT,
        env=SUBPROCESS_ENV,
        check=True,
        capture_output=True,
        text=True,
    )
    written = json.loads(write.stdout)
    assert written["pair_budget_lemma"]["four_halos_maximum_selected_private"] == 2
    assert written["pair_budget_lemma"]["five_halos_minimum_reused"] == 2

    checked = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPT),
            "--check",
            "--assert-expected",
            "--artifact",
            str(artifact),
            "--summary-json",
        ],
        cwd=ROOT,
        env=SUBPROCESS_ENV,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(checked.stdout)
    assert payload["guardrails"][0]["selected_private_halos"] == [8]
    assert payload["guardrails"][1]["selected_private_halos"] == [9, 10]


def test_cli_rejects_modified_artifact(tmp_path: Path) -> None:
    artifact = tmp_path / "private_halo_reuse.json"
    subprocess.run(
        [sys.executable, "-B", str(SCRIPT), "--write", "--out", str(artifact)],
        cwd=ROOT,
        env=SUBPROCESS_ENV,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    payload["pair_budget_lemma"]["five_halos_maximum_selected_private"] = 4
    artifact.write_text(json.dumps(payload), encoding="utf-8")

    checked = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPT),
            "--check",
            "--artifact",
            str(artifact),
        ],
        cwd=ROOT,
        env=SUBPROCESS_ENV,
        check=False,
        capture_output=True,
        text=True,
    )
    assert checked.returncode != 0
    assert "private-halo reuse packet changed" in checked.stderr
