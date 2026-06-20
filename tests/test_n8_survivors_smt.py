"""Tests for the independent SMT cross-check of the n=8 survivor classes."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

SPEC = importlib.util.spec_from_file_location(
    "check_n8_survivors_smt",
    pathlib.Path(__file__).resolve().parents[1]
    / "scripts"
    / "check_n8_survivors_smt.py",
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def _rows(cid):
    root = MOD.repo_root()
    for rec in MOD.load_survivors(root):
        if int(rec["id"]) == cid:
            return rec["rows"]
    raise AssertionError(f"class {cid} not found")


def test_loads_fifteen_survivors():
    assert len(MOD.load_survivors(MOD.repo_root())) == 15


def test_groebner_dependent_classes_unsat():
    """The four Groebner-dependent classes (the gap in the SymPy-free recheck)
    have no strictly convex realization under the independent z3 decision
    procedure (order-free strict convex position is UNSAT)."""
    pytest.importorskip("z3")
    for cid in (3, 4, 5, 14):
        d = MOD.decide_class(_rows(cid), 60000)
        assert d["strict_convex"] == "unsat", (cid, d)
        assert d["equations"] == 64


def test_class14_needs_convexity_others_orderfree():
    """Class 14 is SAT without convexity (its bare ED+PB system has solutions)
    but UNSAT under strict convex position; a sample of other classes is
    already UNSAT with no convexity assumption (order-independent)."""
    pytest.importorskip("z3")
    d14 = MOD.decide_class(_rows(14), 60000)
    assert d14["without_convexity"] == "sat", d14
    assert d14["strict_convex"] == "unsat", d14
    for cid in (0, 3, 5):
        d = MOD.decide_class(_rows(cid), 60000)
        assert d["without_convexity"] == "unsat", (cid, d)


def test_each_center_has_four_witnesses():
    """Sanity: every survivor row selects exactly four witnesses (4-bad)."""
    for rec in MOD.load_survivors(MOD.repo_root()):
        rows = rec["rows"]
        for i in range(MOD.N):
            assert len(MOD.witnesses(rows, i)) == 4, (rec["id"], i)


def test_compare_artifact_replay_detects_stale_payload(tmp_path):
    payload = {
        "schema": "erdos97.n8_survivors_smt.v1",
        "status": "EXACT_OBSTRUCTION_SMT",
        "trust": "EXACT_OBSTRUCTION",
        "clear": True,
        "classes_total": 15,
        "not_strictly_convex_unsat_failures": [],
        "order_independent_unsat_classes": list(range(14)),
        "records": [{"class": 0, "strict_convex": "unsat"}],
    }
    artifact = tmp_path / "n8_survivors_smt.json"
    artifact.write_text(
        json.dumps({**payload, "clear": False}, sort_keys=True),
        encoding="utf-8",
    )

    errors = MOD.compare_artifact_replay(payload, str(artifact))

    assert errors == [
        f"stored artifact replay mismatch: {artifact}",
        "field 'clear' differs",
    ]


@pytest.mark.slow
def test_all_fifteen_unsat():
    pytest.importorskip("z3")
    for rec in MOD.load_survivors(MOD.repo_root()):
        d = MOD.decide_class(rec["rows"], 60000)
        assert d["strict_convex"] == "unsat", (rec["id"], d)
