from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.artifact


def test_independent_n8_artifact_audit_entrypoint() -> None:
    repo = Path(__file__).resolve().parents[1]
    script = repo / "scripts" / "independent_check_n8_artifacts.py"
    result = subprocess.run(
        [sys.executable, str(script), "--check", "--json"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    summary = json.loads(result.stdout)
    assert summary["verified"] is True
    assert (
        summary["overall_status"]
        == "n8_artifacts_verified_repo_local_pending_external_review"
    )
    assert "full independent regeneration" in summary["does_not_check"][0]
    assert summary["dependencies_imported"] == [
        "scripts/analyze_n8_exact_survivors.py",
        "scripts/independent_check_n8_incidence_json.py",
    ]
    assert summary["survivor_json"]["record_count"] == 15
    assert summary["completeness_artifact"]["canonical_class_count"] == 15
    exact = summary["exact_obstruction_artifacts"]
    assert exact["all_reconstructed_15_rejected"] is True
    assert exact["compatible_orders_artifact"]["verified"] is True
    assert exact["exact_analysis_artifact"]["verified"] is True
