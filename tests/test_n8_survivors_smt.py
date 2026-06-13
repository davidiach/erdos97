"""Tests for the independent SMT cross-check of the n=8 survivor classes."""

from __future__ import annotations

import importlib.util
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
    are UNSAT under the independent z3 decision procedure."""
    pytest.importorskip("z3")
    for cid in (3, 4, 5, 14):
        verdict, neqs = MOD.decide_class(_rows(cid), 60000)
        assert verdict == "unsat", (cid, verdict)
        assert neqs == 64


def test_each_center_has_four_witnesses():
    """Sanity: every survivor row selects exactly four witnesses (4-bad)."""
    for rec in MOD.load_survivors(MOD.repo_root()):
        rows = rec["rows"]
        for i in range(MOD.N):
            assert len(MOD.witnesses(rows, i)) == 4, (rec["id"], i)


@pytest.mark.slow
def test_all_fifteen_unsat():
    pytest.importorskip("z3")
    for rec in MOD.load_survivors(MOD.repo_root()):
        verdict, _ = MOD.decide_class(rec["rows"], 60000)
        assert verdict == "unsat", (rec["id"], verdict)
