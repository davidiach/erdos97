from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.artifact


def test_independent_n8_incidence_json_checker_verifies_survivors() -> None:
    repo = Path(__file__).resolve().parents[1]
    script = repo / "scripts" / "independent_check_n8_incidence_json.py"
    result = subprocess.run(
        [sys.executable, str(script), "--json"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    summary = json.loads(result.stdout)
    assert summary["verified"] is True
    assert summary["record_count"] == 15
    assert summary["canonical_class_count"] == 15
    assert summary["errors"] == []
    assert summary["status"] == "survivor_json_independent_consistency_check_not_completeness_proof"
