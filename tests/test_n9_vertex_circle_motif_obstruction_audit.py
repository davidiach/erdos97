from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_motif_obstruction_audit import (
    CLAIM_SCOPE,
    DEFAULT_MOTIF_FAMILIES,
    assert_expected_motif_obstruction_audit,
    motif_obstruction_audit_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_motif_obstruction_audit_payload_counts_and_scope() -> None:
    payload = motif_obstruction_audit_payload()

    assert_expected_motif_obstruction_audit(payload)
    summary = payload["motif_obstruction_audit"]
    assert payload["validation_status"] == "passed"
    assert summary["family_count"] == 16
    assert summary["computed_status_counts"] == {"self_edge": 13, "strict_cycle": 3}
    assert summary["stored_status_mismatches"] == 0
    assert summary["equality_path_mismatches"] == 0
    assert summary["strict_cycle_edge_mismatches"] == 0
    assert "does not prove frontier coverage" in payload["claim_scope"]
    assert "counterexample" in payload["claim_scope"]


def test_motif_obstruction_audit_rejects_appended_claim_scope_overclaim() -> None:
    payload = motif_obstruction_audit_payload()
    payload["claim_scope"] = f"{CLAIM_SCOPE} This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_motif_obstruction_audit(payload)


def test_motif_obstruction_audit_rejects_bad_self_edge_conflict(
    tmp_path: Path,
) -> None:
    motif = json.loads(DEFAULT_MOTIF_FAMILIES.read_text(encoding="utf-8"))
    motif["dihedral_incidence_families"]["families"][0]["representative_obstruction"][
        "conflict"
    ]["outer_pair"] = [0, 4]
    motif_path = tmp_path / "motif.json"
    motif_path.write_text(json.dumps(motif), encoding="utf-8")

    payload = motif_obstruction_audit_payload(motif_path=motif_path)

    assert payload["validation_status"] == "failed"
    assert any("bad stored self-edge conflict" in error for error in payload["validation_errors"])


def test_motif_obstruction_audit_rejects_bad_self_edge_path(
    tmp_path: Path,
) -> None:
    motif = json.loads(DEFAULT_MOTIF_FAMILIES.read_text(encoding="utf-8"))
    motif["dihedral_incidence_families"]["families"][0]["representative_obstruction"][
        "distance_equality_path"
    ][0]["next_pair"] = [0, 2]
    motif_path = tmp_path / "motif.json"
    motif_path.write_text(json.dumps(motif), encoding="utf-8")

    payload = motif_obstruction_audit_payload(motif_path=motif_path)

    assert payload["validation_status"] == "failed"
    assert any("bad self-edge equality path" in error for error in payload["validation_errors"])


def test_motif_obstruction_audit_rejects_bad_strict_cycle_edge(
    tmp_path: Path,
) -> None:
    motif = json.loads(DEFAULT_MOTIF_FAMILIES.read_text(encoding="utf-8"))
    family = next(
        family
        for family in motif["dihedral_incidence_families"]["families"]
        if family["status"] == "strict_cycle"
    )
    family["representative_obstruction"]["cycle_edges"][0]["inner_class"] = [0, 1]
    motif_path = tmp_path / "motif.json"
    motif_path.write_text(json.dumps(motif), encoding="utf-8")

    payload = motif_obstruction_audit_payload(motif_path=motif_path)

    assert payload["validation_status"] == "failed"
    assert any("bad strict-cycle edge" in error for error in payload["validation_errors"])


def test_motif_obstruction_audit_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_motif_obstruction_audit.py",
            "--check",
            "--assert-expected",
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
    assert payload["validation_status"] == "passed"
    assert payload["motif_obstruction_audit"]["family_count"] == 16
