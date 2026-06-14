from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_verify_candidate_cli_rejects_invalid_candidate(tmp_path: Path) -> None:
    candidate = tmp_path / "bad.json"
    candidate.write_text(
        json.dumps(
            {
                "coordinates": [[0.0, 0.0], [1.0, 0.0]],
                "S": [[1, 1, 1, 1], [0, 0, 0, 0]],
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "scripts/verify_candidate.py", str(candidate)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 1
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["ok_at_tol"] is False
    assert payload["validation_errors"]


def test_search_module_verify_cli_rejects_invalid_candidate(tmp_path: Path) -> None:
    candidate = tmp_path / "bad.json"
    candidate.write_text(
        json.dumps(
            {
                "coordinates": [[0.0, 0.0], [1.0, 0.0]],
                "S": [[1, 1, 1, 1], [0, 0, 0, 0]],
            }
        ),
        encoding="utf-8",
    )

    env = dict(os.environ)
    src_path = str(ROOT / "src")
    env["PYTHONPATH"] = (
        src_path
        if not env.get("PYTHONPATH")
        else os.pathsep.join([src_path, env["PYTHONPATH"]])
    )
    result = subprocess.run(
        [sys.executable, "-m", "erdos97.search", "--verify", str(candidate)],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 1
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["ok_at_tol"] is False
    assert payload["validation_errors"]
