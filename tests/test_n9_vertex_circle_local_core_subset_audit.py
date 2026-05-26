from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_n9_vertex_circle_local_core_subset_audit import (
    CLAIM_SCOPE,
    DEFAULT_LOCAL_CORE_PACKET,
    DEFAULT_MOTIF_FAMILIES,
    assert_expected_local_core_subset_audit,
    local_core_subset_audit_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_local_core_subset_audit_counts_and_scope() -> None:
    payload = local_core_subset_audit_payload()

    assert_expected_local_core_subset_audit(payload)
    summary = payload["local_core_subset_audit"]
    assert payload["validation_status"] == "passed"
    assert summary["family_count"] == 16
    assert summary["computed_status_counts"] == {"self_edge": 13, "strict_cycle": 3}
    assert summary["subset_mismatches"] == 0
    assert summary["unobstructed_core_count"] == 0
    assert "does not prove frontier coverage" in payload["claim_scope"]
    assert "counterexample" in payload["claim_scope"]


def test_local_core_subset_audit_rejects_appended_claim_scope_overclaim() -> None:
    payload = local_core_subset_audit_payload()
    payload["claim_scope"] = f"{CLAIM_SCOPE} This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_local_core_subset_audit(payload)


def test_local_core_subset_audit_rejects_row_outside_full_family(
    tmp_path: Path,
) -> None:
    local_core = json.loads(DEFAULT_LOCAL_CORE_PACKET.read_text(encoding="utf-8"))
    local_core["certificates"][0]["compact_selected_rows"][0] = [0, 1, 2, 4, 8]
    local_core_path = tmp_path / "local_core.json"
    local_core_path.write_text(json.dumps(local_core), encoding="utf-8")

    payload = local_core_subset_audit_payload(local_core_path=local_core_path)

    assert payload["validation_status"] == "failed"
    assert any("compact rows are not full-row subsets" in error for error in payload["validation_errors"])


def test_local_core_subset_audit_rejects_bad_status(
    tmp_path: Path,
) -> None:
    local_core = json.loads(DEFAULT_LOCAL_CORE_PACKET.read_text(encoding="utf-8"))
    local_core["certificates"][0]["status"] = "strict_cycle"
    local_core_path = tmp_path / "local_core.json"
    local_core_path.write_text(json.dumps(local_core), encoding="utf-8")

    payload = local_core_subset_audit_payload(local_core_path=local_core_path)

    assert payload["validation_status"] == "failed"
    assert any("status mismatch" in error for error in payload["validation_errors"])


def test_local_core_subset_audit_rejects_bad_orbit_size(
    tmp_path: Path,
) -> None:
    local_core = json.loads(DEFAULT_LOCAL_CORE_PACKET.read_text(encoding="utf-8"))
    local_core["certificates"][0]["orbit_size"] = 17
    local_core_path = tmp_path / "local_core.json"
    local_core_path.write_text(json.dumps(local_core), encoding="utf-8")

    payload = local_core_subset_audit_payload(local_core_path=local_core_path)

    assert payload["validation_status"] == "failed"
    assert any("orbit_size mismatch" in error for error in payload["validation_errors"])


def test_local_core_subset_audit_rejects_motif_family_drift(
    tmp_path: Path,
) -> None:
    motif = json.loads(DEFAULT_MOTIF_FAMILIES.read_text(encoding="utf-8"))
    motif["dihedral_incidence_families"]["families"][0]["representative_selected_rows"][
        0
    ] = [1, 2, 4, 8]
    motif_path = tmp_path / "motif.json"
    motif_path.write_text(json.dumps(motif), encoding="utf-8")

    payload = local_core_subset_audit_payload(motif_path=motif_path)

    assert payload["validation_status"] == "failed"
    assert any("compact rows are not full-row subsets" in error for error in payload["validation_errors"])


def test_local_core_subset_audit_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_local_core_subset_audit.py",
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
    assert payload["local_core_subset_audit"]["family_count"] == 16
