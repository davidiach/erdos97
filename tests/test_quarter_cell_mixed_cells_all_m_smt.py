"""Tests for the all-m SMT closure of the mixed-derivative quarter-cell cells."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

SPEC = importlib.util.spec_from_file_location(
    "check_quarter_cell_mixed_cells_all_m_smt",
    REPO_ROOT / "scripts" / "check_quarter_cell_mixed_cells_all_m_smt.py",
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

ARTIFACT = (
    REPO_ROOT / "data" / "certificates" / "quarter_cell_mixed_cells_all_m_smt.json"
)


def test_cells_match_stored_derivative_certificate():
    """The three cells are exactly the mixed-derivative (proof rule
    F(d,0)=F(0,e)=0 and F_de<0) cells of the finite-m interval certificate,
    with the same killer turns and radius signs."""
    stored = json.loads(
        (
            REPO_ROOT
            / "data"
            / "certificates"
            / "quarter_cell_derivative_certificate.json"
        ).read_text(encoding="utf-8")
    )
    mixed = {
        c["cell"]: c
        for c in stored["results"][0]["cells"]
        if c["certified_component"] == "de"
    }
    ours = {c["cell"]: c for c in MOD.MIXED_CELLS}
    assert set(mixed) == set(ours)
    turn_name = {1: "tau_A", 2: "tau_B", 3: "tau_C"}
    for cell_id, ours_cell in ours.items():
        assert mixed[cell_id]["killer_turn"] == turn_name[ours_cell["killer_turn"]]
        assert mixed[cell_id]["y_radius_sign"] == ours_cell["y_sign"]
        assert mixed[cell_id]["z_radius_sign"] == ours_cell["z_sign"]


def test_boundary_identities_exact():
    """F(0,e) == 0 and F(d,0) == 0 hold symbolically for all three cells."""
    pytest.importorskip("sympy")
    for cell in MOD.MIXED_CELLS:
        assert MOD.boundary_identities_hold(cell), cell["cell"]


def test_embedding_spot_check():
    """Quarter-cell instances m = 0 mod 4, m in [8, 200] land in the
    relaxation region."""
    res = MOD.embedding_spot_check(200)
    assert res["ok"]
    assert res["instances_checked"] == len(range(8, 201, 4))


def test_finite_difference_agreement_one_cell():
    """The cleared numerator matches finite differences of the raw geometric
    turn for the first cell (sign agreement, positive ratio)."""
    pytest.importorskip("sympy")
    _, _, _, _, poly_syms = MOD._symbols()
    cell = MOD.MIXED_CELLS[0]
    numer, _terms = MOD.mixed_numerator(cell)
    res = MOD.finite_difference_agreement(cell, numer, poly_syms, grid=4)
    assert res["ok"]


def test_z3_decisions_replay_one_cell():
    """The three z3 decisions replay for the first cell: mixed-derivative
    nonnegativity UNSAT over the all-T relaxation, with the two SAT
    non-vacuity controls."""
    pytest.importorskip("sympy")
    pytest.importorskip("z3")
    _, _, _, _, poly_syms = MOD._symbols()
    cell = MOD.MIXED_CELLS[0]
    numer, _terms = MOD.mixed_numerator(cell)
    decisions = MOD.decide_cell(cell, numer, poly_syms, timeout_ms=120000)
    assert decisions == MOD.EXPECTED_DECISIONS


def test_stored_artifact_fields():
    """The checked-in certificate has the expected schema, trust, per-cell
    certification, and clear flag."""
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["schema"] == "erdos97.quarter_cell_mixed_cells_all_m_smt.v1"
    assert payload["trust"] == "EXACT_OBSTRUCTION"
    assert payload["status"] == "EXACT_MIXED_CELLS_ALL_M_SMT"
    assert payload["clear"] is True
    assert [c["cell"] for c in payload["cells"]] == [
        "LL_y-_z+",
        "LH_y+_z+",
        "HH_y+_z-",
    ]
    for cell in payload["cells"]:
        assert cell["certified"] is True
        assert cell["boundary_identities_exact"] is True
        assert cell["decisions"] == MOD.EXPECTED_DECISIONS
        assert cell["finite_difference_agreement"]["ok"] is True


def test_compare_artifact_replay_detects_stale_payload(tmp_path):
    """The replay comparator flags a mismatching stored artifact."""
    stale = tmp_path / "stale.json"
    stale.write_text(json.dumps({"schema": "wrong"}), encoding="utf-8")
    assert MOD.compare_artifact_replay({"schema": "right"}, str(stale))


@pytest.mark.artifact
def test_full_artifact_replay():
    """Full deterministic payload replay against the checked-in certificate
    (needs sympy and z3; exercised by the artifact tier)."""
    pytest.importorskip("sympy")
    pytest.importorskip("z3")

    class Args:
        timeout_ms = 120000
        max_m = 120

    payload = MOD.build_payload(Args())
    assert MOD.compare_artifact_replay(payload, str(ARTIFACT)) == []
