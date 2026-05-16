from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _make_target_commands(target: str) -> list[str]:
    lines = (ROOT / "Makefile").read_text(encoding="utf-8").splitlines()
    header = f"{target}:"
    start = lines.index(header) + 1
    commands: list[str] = []
    for line in lines[start:]:
        if line and not line.startswith("\t"):
            break
        if line.startswith("\t"):
            commands.append(line.strip().replace("$(PYTHON)", "python"))
    return commands


def test_verify_n9_review_includes_documented_frontier_audits() -> None:
    commands = _make_target_commands("verify-n9-review")
    expected_chain = [
        "python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json",
        (
            "python scripts/analyze_n9_vertex_circle_obstruction_shapes.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/analyze_n9_vertex_circle_motif_families.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_turn_inequality_frontier.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_input_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_incidence_filters.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_branch_options.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_dynamic_mro_choices.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_mro_branching_replay.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_strict_edge_geometry.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_local_core_packet.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_local_core_subset_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_core_templates.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_frontier_motif_classification.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_dihedral_orbit_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_motif_obstruction_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/compare_n9_vertex_circle_frontier.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_frontier_assignment_audit.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_quotient_soundness.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_partial_pruning.py "
            "--check --assert-expected --json"
        ),
        (
            "python scripts/check_n9_vertex_circle_self_edge_path_join.py "
            "--check --assert-expected --json"
        ),
    ]

    for command in expected_chain:
        assert command in commands

    positions = [commands.index(command) for command in expected_chain]
    assert positions == sorted(positions)
