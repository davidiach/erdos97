from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_base_apex_audit_path import (
    EXPECTED_CLAIM_SCOPE,
    EXPECTED_SCHEMA,
    EXPECTED_TRUST,
    load_artifacts,
    resolve_artifact_paths,
    summary_payload,
    validate_audit_path,
)

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.artifact


def load_default_artifacts() -> tuple[dict[str, Path], dict[str, object]]:
    paths = resolve_artifact_paths(ROOT)
    artifacts, errors = load_artifacts(paths)
    assert errors == []
    return paths, artifacts


def test_base_apex_audit_path_default_stack_passes() -> None:
    paths, artifacts = load_default_artifacts()

    errors = validate_audit_path(artifacts)
    summary = summary_payload(ROOT, paths, artifacts, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["schema"] == EXPECTED_SCHEMA
    assert summary["trust"] == EXPECTED_TRUST
    assert summary["claim_scope"] == EXPECTED_CLAIM_SCOPE
    assert summary["base_apex"]["strict_unresolved_profile_ledger_count"] == 30
    assert summary["base_apex"]["strict_minimum_relevant_deficit_count_to_spoil"] == 3
    assert summary["base_apex"]["d3_representative_count"] == 88
    assert summary["base_apex"]["d3_common_dihedral_pair_class_count"] == 18088
    assert summary["base_apex"]["d3_realizability_state"] == "UNKNOWN"
    assert summary["base_apex"]["d3_incidence_state"] == "UNKNOWN"
    assert summary["selected_baseline_d3"]["assignment_count"] == 184
    assert summary["selected_baseline_d3"]["total_budget3_slot_choice_count"] == 15456
    assert summary["selected_baseline_d3"]["escaping_budget3_slot_choice_count"] == 1746
    assert summary["selected_baseline_d3"]["nonzero_crosswalk_cell_count"] == 36
    assert summary["vertex_circle_frontier"]["frontier_assignment_count"] == 184
    assert summary["vertex_circle_frontier"]["self_edge_count"] == 158
    assert summary["vertex_circle_frontier"]["strict_cycle_count"] == 26
    assert summary["vertex_circle_frontier"]["main_full_assignments"] == 0


def test_base_apex_audit_path_scope_is_nonclaiming() -> None:
    lowered = EXPECTED_CLAIM_SCOPE.lower()

    for phrase in (
        "not a proof",
        "not a counterexample",
        "not an incidence-completeness result",
        "not a geometric realizability test",
        "not a global status update",
    ):
        assert phrase in lowered


def test_base_apex_audit_path_rejects_selected_baseline_frontier_drift() -> None:
    _paths, artifacts = load_default_artifacts()
    payload = copy.deepcopy(artifacts)
    payload["selected_baseline_d3_crosswalk"]["assignment_count"] = 185

    errors = validate_audit_path(payload)

    assert any(
        "selected-baseline assignment count vs vertex frontier" in error
        for error in errors
    )


def test_base_apex_audit_path_rejects_vertex_frontier_drift() -> None:
    _paths, artifacts = load_default_artifacts()
    payload = copy.deepcopy(artifacts)
    payload["n9_vertex_circle_exhaustive"]["cross_check_without_vertex_circle_pruning"][
        "counts"
    ]["self_edge"] = 157

    errors = validate_audit_path(payload)

    assert any("n9_vertex_circle_exhaustive" in error for error in errors)
    assert any("vertex frontier self-edge count" in error for error in errors)


def test_base_apex_audit_path_rejects_claim_state_drift() -> None:
    _paths, artifacts = load_default_artifacts()
    payload = copy.deepcopy(artifacts)
    payload["d3_incidence_capacity_packet"]["realizability_state"] = "PROVED"

    errors = validate_audit_path(payload)

    assert any("realizability_state must be UNKNOWN" in error for error in errors)
    assert any("full packet realizability state" in error for error in errors)


def test_base_apex_audit_path_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_base_apex_audit_path.py",
            "--check",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["base_apex"]["d3_common_dihedral_pair_class_count"] == 18088
    assert payload["selected_baseline_d3"]["assignment_count"] == 184
