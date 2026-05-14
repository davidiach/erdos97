from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.artifact


def run_residual_script(repo: Path) -> dict:
    script = repo / "scripts" / "check_n8_residual_certificates.py"
    result = subprocess.run(
        [sys.executable, str(script), "--check", "--json"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return json.loads(result.stdout)


def test_n8_residual_certificate_audit() -> None:
    repo = Path(__file__).resolve().parents[1]
    summary = run_residual_script(repo)

    assert summary["verified"] is True
    assert summary["class_ids"] == [3, 4, 5]

    by_class = {record["class_id"]: record for record in summary["classes"]}
    assert by_class[3]["mechanism"] == "duplicate_vertex"
    assert by_class[3]["first_stage"]["all_expected_relations_hold"] is True
    assert by_class[3]["third_stage"]["forces_p7_equals_p0"] is True

    assert by_class[4]["mechanism"] == "collinear_vertices"
    assert by_class[4]["first_stage"]["all_expected_relations_hold"] is True
    assert by_class[4]["collinearity_stage"]["contains_collinearity_determinant"] is True
    assert by_class[4]["collinearity_stage"]["collinear_labels"] == [2, 3, 4]

    assert by_class[5]["mechanism"] == "groebner_contains_y2_after_substitution"
    assert by_class[5]["groebner"]["basis_polynomial_count"] == 8
    assert by_class[5]["groebner"]["artifact_generating_set_equivalent"] is True
    assert by_class[5]["groebner"]["contains_y2"] is True
    assert by_class[5]["groebner"]["artifact_contains_y2"] is True
