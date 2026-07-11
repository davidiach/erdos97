from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_lean_toolchain_and_ci_are_pinned() -> None:
    assert (ROOT / "lean-toolchain").read_text(encoding="utf-8") == (
        "leanprover/lean4:v4.31.0\n"
    )
    workflow = (ROOT / ".github/workflows/lean.yml").read_text(encoding="utf-8")
    assert "leanprover/lean-action@38fbc41a8c28c4cbaec22d7f7de508ec2e7c0dd9" in workflow
    assert "python scripts/check_lean_files.py --require-lean" in workflow


def test_python_312_ci_uses_the_checked_dependency_snapshot() -> None:
    tests_workflow = (ROOT / ".github/workflows/tests.yml").read_text(encoding="utf-8")
    artifact_workflow = (ROOT / ".github/workflows/artifact-audit.yml").read_text(
        encoding="utf-8"
    )
    assert "python -m pip install -r requirements-lock.txt" in tests_workflow
    assert "python -m pip install --no-deps -e ." in tests_workflow
    assert artifact_workflow.count("python -m pip install -r requirements-lock.txt") == 3
    assert artifact_workflow.count("python -m pip install --no-deps -e .") == 3
