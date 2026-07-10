"""Tests for the all-m dominance closure of the first-derivative quarter cells."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

SPEC = importlib.util.spec_from_file_location(
    "check_quarter_cell_first_derivative_all_m_dominance",
    REPO_ROOT / "scripts" / "check_quarter_cell_first_derivative_all_m_dominance.py",
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "quarter_cell_first_derivative_all_m_dominance.json"
)


def test_cells_match_stored_derivative_certificate():
    """The nine cells are exactly the non-mixed cells of the finite-m
    interval certificate, with matching killer turns, components, signs,
    and vanishing boundaries."""
    stored = json.loads(
        (
            REPO_ROOT
            / "data"
            / "certificates"
            / "quarter_cell_derivative_certificate.json"
        ).read_text(encoding="utf-8")
    )
    first = {
        c["cell"]: c
        for c in stored["results"][0]["cells"]
        if c["certified_component"] != "de"
    }
    ours = {c["cell"]: c for c in MOD.FIRST_DERIVATIVE_CELLS}
    assert set(first) == set(ours)
    turn_name = {1: "tau_A", 2: "tau_B", 3: "tau_C"}
    for cell_id, ours_cell in ours.items():
        assert first[cell_id]["killer_turn"] == turn_name[ours_cell["killer_turn"]]
        assert first[cell_id]["certified_component"] == ours_cell["component"]
        assert first[cell_id]["required_sign"] == ours_cell["required_sign"]
        assert first[cell_id]["y_radius_sign"] == ours_cell["y_sign"]
        assert first[cell_id]["z_radius_sign"] == ours_cell["z_sign"]
        rule = first[cell_id]["proof_rule"]
        expected_boundary = {
            "d0": "F(0,e)=0",
            "e0": "F(d,0)=0",
            "diag": "F(d,d)=0",
        }[ours_cell["vanishing_boundary"]]
        assert rule.startswith(expected_boundary), (cell_id, rule)


def test_exact_rational_checks():
    """A's factorization, the band-inside-box bound, and the dominance
    clearing-identity sample all verify."""
    pytest.importorskip("sympy")
    assert MOD.a_factorization_holds()
    assert MOD.band_inside_box_exact()
    assert MOD.dominance_chain_exact()


def test_symbolic_identities_one_edge_one_diagonal_cell():
    """Corner and vanishing-boundary identities verify for one edge cell
    and one diagonal cell (the full set is exercised by the artifact tier)."""
    pytest.importorskip("sympy")
    for idx in (0, 2):  # LL_y+_z+ (edge) and LL_y-_z- (diagonal)
        res = MOD.symbolic_identities_hold(MOD.FIRST_DERIVATIVE_CELLS[idx])
        assert res == {"corner_identity": True, "boundary_identity": True}


def test_z3_band_and_dominance_decisions():
    """The five shared z3 decisions replay, including the M=6 SAT control."""
    pytest.importorskip("z3")
    assert (
        MOD.decide_band_and_dominance(timeout_ms=120000)
        == MOD.EXPECTED_Z3_DECISIONS
    )


def test_interval_lipschitz_one_cell():
    """The certified interval Lipschitz bound holds for the worst edge cell
    at a coarse subdivision."""
    pytest.importorskip("sympy")
    res = MOD.certified_lipschitz_bound(
        MOD.FIRST_DERIVATIVE_CELLS[1], n_t=12, n_de=3
    )
    assert res["certified_le_m"], res


def test_embedding_spot_check():
    res = MOD.embedding_spot_check(200)
    assert res["ok"]
    assert res["instances_checked"] == len(range(8, 201, 4))


def test_stored_artifact_fields():
    """The checked-in certificate has the expected schema, trust, per-cell
    certification, and clear flag."""
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert (
        payload["schema"]
        == "erdos97.quarter_cell_first_derivative_all_m_dominance.v1"
    )
    assert payload["trust"] == "EXACT_OBSTRUCTION"
    assert payload["status"] == "EXACT_FIRST_DERIVATIVE_CELLS_ALL_M_DOMINANCE"
    assert payload["clear"] is True
    assert payload["m_lipschitz"] == 4
    assert payload["z3_decisions"] == MOD.EXPECTED_Z3_DECISIONS
    assert len(payload["cells"]) == 9
    for cell in payload["cells"]:
        assert cell["certified"] is True
        assert cell["symbolic_identities"] == {
            "corner_identity": True,
            "boundary_identity": True,
        }
        assert cell["lipschitz"]["certified_le_m"] is True
        assert cell["lipschitz"]["sum_upper"] <= 4
        assert cell["finite_difference_agreement"]["ok"] is True


def test_compare_artifact_replay_detects_stale_payload(tmp_path):
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
        interval_t_slices = 24
        interval_de_slices = 4

    payload = MOD.build_payload(Args())
    assert MOD.compare_artifact_replay(payload, str(ARTIFACT)) == []
