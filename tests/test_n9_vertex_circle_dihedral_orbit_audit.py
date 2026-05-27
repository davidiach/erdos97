from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_dihedral_orbit_audit import (
    CLAIM_SCOPE,
    DEFAULT_FRONTIER_CLASSIFICATION,
    DEFAULT_MOTIF_FAMILIES,
    EXPECTED_ASSIGNMENT_COUNT,
    EXPECTED_ROWS_SHA256,
    assert_expected_dihedral_orbit_audit,
    dihedral_orbit_audit_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_dihedral_orbit_audit_payload_counts_and_scope() -> None:
    payload = dihedral_orbit_audit_payload()

    assert_expected_dihedral_orbit_audit(payload)
    summary = payload["dihedral_orbit_audit"]
    assert payload["validation_status"] == "passed"
    assert summary["family_count"] == 16
    assert summary["classification_assignment_count"] == EXPECTED_ASSIGNMENT_COUNT
    assert summary["orbit_union_row_count"] == EXPECTED_ASSIGNMENT_COUNT
    assert summary["canonical_rep_mismatches"] == 0
    assert summary["canonical_label_map_mismatches"] == 0
    assert summary["orbit_union_rows_sha256"] == EXPECTED_ROWS_SHA256
    assert "does not prove frontier coverage" in payload["claim_scope"]
    assert "counterexample" in payload["claim_scope"]


def test_dihedral_orbit_audit_rejects_appended_claim_scope_overclaim() -> None:
    payload = dihedral_orbit_audit_payload()
    payload["claim_scope"] = f"{CLAIM_SCOPE} This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_dihedral_orbit_audit(payload)


def test_dihedral_orbit_audit_rejects_bad_orbit_size(tmp_path: Path) -> None:
    motif = json.loads(DEFAULT_MOTIF_FAMILIES.read_text(encoding="utf-8"))
    motif["dihedral_incidence_families"]["families"][0]["orbit_size"] = 17
    motif_path = tmp_path / "motif.json"
    motif_path.write_text(json.dumps(motif), encoding="utf-8")

    payload = dihedral_orbit_audit_payload(motif_path=motif_path)

    assert payload["validation_status"] == "failed"
    assert any("orbit_size" in error for error in payload["validation_errors"])


def test_dihedral_orbit_audit_rejects_bad_canonical_label_map(
    tmp_path: Path,
) -> None:
    classification = json.loads(
        DEFAULT_FRONTIER_CLASSIFICATION.read_text(encoding="utf-8")
    )
    # A001 is stored in canonical position, so this nontrivial rotation cannot
    # be its stable canonicalizing map.
    classification["assignments"][0]["to_canonical_label_map"] = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    classification_path = tmp_path / "classification.json"
    classification_path.write_text(json.dumps(classification), encoding="utf-8")

    payload = dihedral_orbit_audit_payload(classification_path=classification_path)

    assert payload["validation_status"] == "failed"
    assert any("canonical_label_map" in error for error in payload["validation_errors"])


def test_dihedral_orbit_audit_rejects_duplicate_classification_row(
    tmp_path: Path,
) -> None:
    classification = json.loads(
        DEFAULT_FRONTIER_CLASSIFICATION.read_text(encoding="utf-8")
    )
    classification["assignments"][1]["selected_rows"] = copy.deepcopy(
        classification["assignments"][0]["selected_rows"]
    )
    classification_path = tmp_path / "classification.json"
    classification_path.write_text(json.dumps(classification), encoding="utf-8")

    payload = dihedral_orbit_audit_payload(classification_path=classification_path)

    assert payload["validation_status"] == "failed"
    assert any("classification_duplicate_rows" in error for error in payload["validation_errors"])


def test_dihedral_orbit_audit_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_dihedral_orbit_audit.py",
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
    assert payload["dihedral_orbit_audit"]["orbit_union_row_count"] == 184
