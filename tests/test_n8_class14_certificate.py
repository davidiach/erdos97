from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.artifact


def run_class14_script(repo: Path) -> dict:
    script = repo / "scripts" / "check_n8_class14_certificate.py"
    result = subprocess.run(
        [sys.executable, str(script), "--check", "--json"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return json.loads(result.stdout)


def test_n8_class14_certificate_audit() -> None:
    repo = Path(__file__).resolve().parents[1]
    summary = run_class14_script(repo)

    assert summary["verified"] is True
    assert summary["class_id"] == 14
    assert summary["equation_counts"] == {
        "phi_edges": 20,
        "perpendicular_bisector_equations": 40,
        "equal_distance_equations": 24,
        "total_equations": 64,
    }
    assert summary["groebner"] == {
        "basis_polynomial_count": 12,
        "artifact_basis_matches_computed_basis": True,
        "artifact_basis_reduces_all_pb_ed_equations": True,
        "computed_basis_is_zero_dimensional": True,
    }
    assert summary["branches"]["artifact_branch_count"] == 4
    assert summary["branches"]["derived_branch_count"] == 4
    assert summary["branches"]["derived_branches_match_artifact"] is True
    assert summary["branches"]["all_derived_branches_solve_pb_ed"] is True
    assert summary["branches"]["all_derived_branches_satisfy_artifact_basis"] is True
    assert summary["branches"]["all_derived_branches_have_four_hull_vertices"] is True
    assert summary["branches"]["all_remaining_labels_are_strict_interior"] is True

    hulls = [record["convexity"]["hull_labels"] for record in summary["branches"]["records"]]
    assert hulls == [[3, 2, 6, 7], [3, 7, 6, 2], [0, 1, 5, 4], [0, 1, 5, 4]]
