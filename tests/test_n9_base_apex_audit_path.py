from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_base_apex_audit_path import (
    EXPECTED_CLAIM_SCOPE,
    EXPECTED_HANDOFF_NAMES,
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
    assert [check["name"] for check in summary["handoff_checks"]] == EXPECTED_HANDOFF_NAMES
    assert all(check["ok"] is True for check in summary["handoff_checks"])
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
    paths, artifacts = load_default_artifacts()
    payload = copy.deepcopy(artifacts)
    payload["selected_baseline_d3_crosswalk"]["assignment_count"] = 185

    errors = validate_audit_path(payload)
    summary = summary_payload(ROOT, paths, payload, errors)
    handoffs = {check["name"]: check for check in summary["handoff_checks"]}

    assert any(
        "selected-baseline assignment count vs vertex frontier" in error
        for error in errors
    )
    assert handoffs["selected_baseline_to_vertex_frontier"]["ok"] is False
    assert any(
        "selected-baseline assignment count" in error
        for error in handoffs["selected_baseline_to_vertex_frontier"]["errors"]
    )


def test_base_apex_audit_path_rejects_low_excess_escape_budget_drift() -> None:
    paths, artifacts = load_default_artifacts()
    payload = copy.deepcopy(artifacts)
    payload["escape_budget"]["strict_positive_threshold"][
        "minimum_relevant_deficit_count_to_spoil"
    ] = 4

    errors = validate_audit_path(payload)
    summary = summary_payload(ROOT, paths, payload, errors)
    handoffs = {check["name"]: check for check in summary["handoff_checks"]}

    assert any("escape_budget" in error for error in errors)
    assert handoffs["escape_budget_to_ladder"]["ok"] is False
    assert any(
        "minimum relevant deficit" in error
        for error in handoffs["escape_budget_to_ladder"]["errors"]
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
    assert [check["name"] for check in payload["handoff_checks"]] == EXPECTED_HANDOFF_NAMES
    assert all(check["ok"] is True for check in payload["handoff_checks"])
    assert payload["base_apex"]["d3_common_dihedral_pair_class_count"] == 18088
    assert payload["selected_baseline_d3"]["assignment_count"] == 184


def test_base_apex_audit_path_checker_cli_summary_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_base_apex_audit_path.py",
            "--check",
            "--summary-json",
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
    assert [check["name"] for check in payload["handoff_checks"]] == EXPECTED_HANDOFF_NAMES
    assert payload["claim_scope"] == EXPECTED_CLAIM_SCOPE
