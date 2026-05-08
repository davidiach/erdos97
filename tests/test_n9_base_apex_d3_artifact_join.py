from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from erdos97.n9_base_apex_d3_artifact_join import (
    EXPECTED_CLAIM_SCOPE,
    cloned_artifacts,
    load_artifacts,
    resolve_artifact_paths,
    summary_payload,
    validate_artifact_stack,
)

ROOT = Path(__file__).resolve().parents[1]


def load_default_stack() -> tuple[dict[str, Path], dict[str, Any]]:
    paths = resolve_artifact_paths(ROOT)
    artifacts, errors = load_artifacts(paths)
    assert errors == []
    return paths, artifacts


def test_d3_artifact_join_default_stack_passes() -> None:
    paths, artifacts = load_default_stack()

    errors = validate_artifact_stack(artifacts)
    summary = summary_payload(ROOT, paths, artifacts, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert summary["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert summary["claim_scope"] == EXPECTED_CLAIM_SCOPE
    assert summary["d3_slice"]["labelled_profile_sequence_count"] == 3003
    assert summary["d3_slice"]["labelled_escape_placement_count"] == 108
    assert summary["d3_slice"]["common_dihedral_pair_class_count"] == 18088
    assert summary["d3_packet_representative_count"] == 88
    assert summary["d3_crosswalk_row_count"] == 88
    assert summary["d3_crosswalk_common_dihedral_pair_class_count"] == 18088
    assert summary["full_packet_row_count"] == 88
    assert summary["p19_pilot_row_count"] == 8


def test_d3_artifact_join_scope_is_nonclaiming() -> None:
    lowered = EXPECTED_CLAIM_SCOPE.lower()

    assert "cross-artifact consistency checker" in lowered
    assert "n=9 base-apex d=3 bookkeeping artifacts" in lowered
    for phrase in (
        "not a proof",
        "not a counterexample",
        "not an incidence-completeness result",
        "not a geometric realizability test",
        "not a global status update",
    ):
        assert phrase in lowered


def test_d3_artifact_join_rejects_slice_orbit_arithmetic_drift() -> None:
    _paths, artifacts = load_default_stack()
    payload = cloned_artifacts(artifacts)
    payload["d3_escape_slice"]["coupled_slice"][
        "labelled_profile_escape_pair_count"
    ] += 1

    errors = validate_artifact_stack(payload)

    assert any("orbit arithmetic" in error for error in errors)
    assert any("3003*108" in error for error in errors)


def test_d3_artifact_join_rejects_crosswalk_pair_count_drift() -> None:
    _paths, artifacts = load_default_stack()
    payload = cloned_artifacts(artifacts)
    for row in payload["low_excess_escape_crosswalk"]["crosswalk_rows"]:
        if row["total_profile_excess"] == 6 and row["capacity_deficit"] == 3:
            row["labelled_profile_escape_pair_count"] += 1
            break

    errors = validate_artifact_stack(payload)

    assert any("profile*escape count" in error for error in errors)


def test_d3_artifact_join_rejects_packet_crosswalk_join_drift() -> None:
    _paths, artifacts = load_default_stack()
    payload = cloned_artifacts(artifacts)
    payload["d3_escape_frontier_packet"]["representatives"][0][
        "common_dihedral_pair_class_count"
    ] += 1

    errors = validate_artifact_stack(payload)

    assert any(
        "does not match crosswalk.common_dihedral_pair_class_count" in error
        for error in errors
    )


def test_d3_artifact_join_rejects_full_packet_source_drift() -> None:
    _paths, artifacts = load_default_stack()
    payload = cloned_artifacts(artifacts)
    payload["d3_incidence_capacity_packet"]["rows"][0]["escape_class_id"] = "X99"

    errors = validate_artifact_stack(payload)

    assert any("does not match d3 packet.escape_class_id" in error for error in errors)
    assert any("rows must be P19..P29 x X00..X07" in error for error in errors)


def test_d3_artifact_join_rejects_p19_pilot_full_packet_drift() -> None:
    _paths, artifacts = load_default_stack()
    payload = cloned_artifacts(artifacts)
    payload["d3_p19_incidence_capacity_pilot"]["rows"][0][
        "target_capacity_totals_by_cyclic_length"
    ]["2"] += 1

    errors = validate_artifact_stack(payload)

    assert any("does not match full packet R000" in error for error in errors)
    assert any("must sum to 60" in error for error in errors)


def test_d3_artifact_join_rejects_p19_pilot_missing_projection_fields() -> None:
    _paths, artifacts = load_default_stack()
    payload = cloned_artifacts(artifacts)
    for row in payload["d3_p19_incidence_capacity_pilot"]["rows"]:
        del row["profile_ledger_id"]

    errors = validate_artifact_stack(payload)

    assert any(
        "d3_p19_incidence_capacity_pilot.rows[0] keys do not match "
        "full packet R000 projection" in error
        for error in errors
    )
    assert any("profile_ledger_id" in error for error in errors)


def test_d3_artifact_join_rejects_state_and_capacity_drift() -> None:
    _paths, artifacts = load_default_stack()
    payload = cloned_artifacts(artifacts)
    payload["d3_incidence_capacity_packet"]["rows"][0]["target_capacity_total"] = 59
    payload["d3_p19_incidence_capacity_pilot"]["realizability_state"] = "PROVED"

    errors = validate_artifact_stack(payload)

    assert any("target_capacity_total must be 60" in error for error in errors)
    assert any("realizability_state must be UNKNOWN" in error for error in errors)


def test_d3_artifact_join_rejects_non_object_rows() -> None:
    _paths, artifacts = load_default_stack()
    payload = cloned_artifacts(artifacts)
    payload["d3_p19_incidence_capacity_pilot"]["rows"] = [None] * 8

    errors = validate_artifact_stack(payload)

    assert any(
        "d3_p19_incidence_capacity_pilot.rows[0] must be an object" in error
        for error in errors
    )
    assert any("object row count must be 8" in error for error in errors)


def test_d3_artifact_join_rejects_artifact_contract_drift() -> None:
    _paths, artifacts = load_default_stack()
    payload = cloned_artifacts(artifacts)
    payload["d3_incidence_capacity_packet"]["source_artifacts"][
        "d3_escape_frontier_packet"
    ] = "data/certificates/other.json"
    payload["d3_escape_frontier_packet"]["schema"] = "wrong"

    errors = validate_artifact_stack(payload)

    assert any("d3_incidence_capacity_packet.source_artifacts mismatch" in error for error in errors)
    assert any("d3_escape_frontier_packet.schema mismatch" in error for error in errors)


def test_d3_artifact_join_rejects_missing_profile_ids() -> None:
    _paths, artifacts = load_default_stack()
    payload = cloned_artifacts(artifacts)
    for row in payload["low_excess_escape_crosswalk"]["crosswalk_rows"]:
        if row["total_profile_excess"] == 6 and row["capacity_deficit"] == 3:
            del row["profile_ledger_id"]

    errors = validate_artifact_stack(payload)

    assert any("profile_ledger_id must be a string" in error for error in errors)
    assert any(
        "low_excess_escape_crosswalk D=3 rows must be P19..P29 x X00..X07"
        in error
        for error in errors
    )


def test_d3_artifact_join_reports_invalid_utf8(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_bytes(b"\xff")

    artifacts, errors = load_artifacts({"d3_escape_slice": bad})

    assert artifacts == {}
    assert any("artifact is not valid UTF-8" in error for error in errors)


def test_d3_artifact_join_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_base_apex_d3_artifact_join.py",
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
    assert payload["claim_scope"] == EXPECTED_CLAIM_SCOPE
    assert payload["d3_crosswalk_row_count"] == 88
    assert payload["d3_crosswalk_common_dihedral_pair_class_count"] == 18088
