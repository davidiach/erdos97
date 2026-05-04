from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from erdos97.path_display import display_path

ROOT = Path(__file__).resolve().parents[1]


def test_display_path_prefers_repo_relative_inside_root(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    out = root / "data" / "artifact.json"

    assert display_path(out, root) == "data/artifact.json"


def test_display_path_allows_outputs_outside_root(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    out = tmp_path / "elsewhere" / "artifact.json"

    assert display_path(out, root) == str(out.resolve())


def test_write_cli_reports_outside_repo_path_without_crashing(tmp_path: Path) -> None:
    out = tmp_path / "phi4_frontier_scan.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_phi4_frontier_scan.py",
            "--no-builtins",
            "--no-sparse-orders",
            "--write",
            "--out",
            str(out),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert out.exists()
    assert f"wrote {out.resolve()}" in result.stdout
