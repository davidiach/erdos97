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
    assert "  lint:\n" in tests_workflow
    assert "  pytest-shard:\n" in tests_workflow
    assert "        shard: [0, 1]\n" in tests_workflow
    assert "make verify-lint" in tests_workflow
    assert "--durations 20 --durations-min 1.0" in tests_workflow
    assert '--shard-count 2 --shard-index ${{ matrix.shard }}' in tests_workflow
    assert "    name: pytest (3.12)\n" in tests_workflow
    assert "    needs: [lint, pytest-shard]\n" in tests_workflow
    assert artifact_workflow.count("python -m pip install -r requirements-lock.txt") == 2
    assert artifact_workflow.count("python -m pip install --no-deps -e .") == 2
    assert "slow-exhaustive-pytest:" not in artifact_workflow
    assert '-m "artifact and not exhaustive"' in artifact_workflow
    pr_artifact_step = artifact_workflow.split(
        "- name: Run PR artifact pytest shard", maxsplit=1
    )[1].split("- name: Run full artifact pytest shard", maxsplit=1)[0]
    assert "-n auto --dist worksteal" in pr_artifact_step
    assert "--durations 20 --durations-min 1.0" in pr_artifact_step


def test_compatibility_lanes_do_not_run_floating_lint() -> None:
    workflow = (ROOT / ".github/workflows/tests.yml").read_text(encoding="utf-8")
    compatibility = workflow.split("  compatibility:\n", maxsplit=1)[1]

    assert "python-version: ['3.10', '3.11']" in compatibility
    assert 'if [ "${{ matrix.python-version }}" = "3.10" ]; then' in compatibility
    assert "python -m pip install --no-deps -e ." in compatibility
    assert "python -m pytest -q" in compatibility
    assert "make verify-fast" not in compatibility
