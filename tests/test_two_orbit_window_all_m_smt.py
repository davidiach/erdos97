"""Tests for the all-m SMT certificate of the two-orbit window-root exclusion."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

SPEC = importlib.util.spec_from_file_location(
    "check_two_orbit_window_all_m_smt",
    REPO_ROOT / "scripts" / "check_two_orbit_window_all_m_smt.py",
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

LEGACY_SPEC = importlib.util.spec_from_file_location(
    "check_two_orbit_dynamic_window_lemma",
    REPO_ROOT / "scripts" / "check_two_orbit_dynamic_window_lemma.py",
)
LEGACY = importlib.util.module_from_spec(LEGACY_SPEC)
sys.modules[LEGACY_SPEC.name] = LEGACY
LEGACY_SPEC.loader.exec_module(LEGACY)

ARTIFACT = REPO_ROOT / "data" / "certificates" / "two_orbit_window_all_m_smt.json"


def test_exact_rational_self_checks():
    """The m=3 corner point, its E_A boundary-root identification, and the
    pinned no-gap witness all verify in exact rational arithmetic."""
    assert MOD.corner_point_exact_check()
    assert MOD.corner_is_m3_boundary_root()
    assert MOD.no_gap_witness_exact_check()


def test_valid_pairs_match_legacy_screen():
    """The (a, p) instance ranges agree with the finite float screen this
    certificate supersedes, for every m up to 60."""
    for m in range(3, 61):
        assert MOD.valid_pairs(m) == LEGACY.valid_pairs(m), m


def test_embedding_spot_check_small():
    """Every integer instance with m <= 48 maps into the relaxed region."""
    res = MOD.embedding_spot_check(48)
    assert res["ok"]
    assert res["pairs_checked"] == sum(
        len(MOD.valid_pairs(m)) for m in range(3, 49)
    )


def test_formulation_agreement_small():
    """Root-location and T-form window tests agree for m <= 30, with the
    single boundary-band pair being the m=3 corner."""
    res = MOD.formulation_agreement_check(30)
    assert res["mismatches"] == 0
    assert res["boundary_band_hits"] == 1


def test_stored_artifact_fields():
    """The checked-in certificate has the expected schema, trust, decisions,
    and clear flag."""
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["schema"] == "erdos97.two_orbit_window_all_m_smt.v1"
    assert payload["trust"] == "EXACT_OBSTRUCTION"
    assert payload["status"] == "EXACT_STEP5_ALL_M_SMT"
    assert payload["clear"] is True
    assert payload["decisions"] == MOD.EXPECTED_DECISIONS
    assert payload["exact_checks"] == {
        "corner_point_verified": True,
        "corner_is_m3_boundary_root_x2": True,
        "no_gap_witness_verified": True,
    }


def test_z3_decisions_replay():
    """The five z3 decisions replay: main strict system UNSAT (the all-m
    certificate), non-strict variant SAT only at the pinned m=3 corner, and
    the no-gap control SAT."""
    pytest.importorskip("z3")
    assert MOD.decide_all(timeout_ms=60000) == MOD.EXPECTED_DECISIONS


def test_compare_artifact_replay_detects_stale_payload(tmp_path):
    """The replay comparator flags a mismatching stored artifact."""
    stale = tmp_path / "stale.json"
    stale.write_text(json.dumps({"schema": "wrong"}), encoding="utf-8")
    errors = MOD.compare_artifact_replay({"schema": "right"}, str(stale))
    assert errors


@pytest.mark.artifact
def test_full_artifact_replay():
    """Full deterministic payload replay against the checked-in certificate
    (needs z3; exercised by the artifact tier)."""
    pytest.importorskip("z3")

    class Args:
        timeout_ms = 60000
        max_m = 120
        agreement_max_m = 40

    payload = MOD.build_payload(Args())
    assert MOD.compare_artifact_replay(payload, str(ARTIFACT)) == []
