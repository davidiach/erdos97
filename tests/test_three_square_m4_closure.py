"""Tests for the m=4 three-square exact SMT closure checker."""

from __future__ import annotations

import importlib.util
import math
import pathlib
import sys

import pytest

SPEC = importlib.util.spec_from_file_location(
    "check_three_square_m4_closure",
    pathlib.Path(__file__).resolve().parents[1]
    / "scripts"
    / "check_three_square_m4_closure.py",
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def test_faithfulness_guard():
    """The constructive faithfulness self-test passes: solving the witness
    distance equation yields P(r) equal to the modelled witness-angle value."""
    assert MOD.faithfulness_ok()


def test_reduction_matches_raw_4bad():
    """On constructed configs, conditions (i,ii,iii) agree with the raw
    geometric branch-G 4-bad definition (own 90-pair + one witness per orbit)."""
    from collections import Counter

    h = math.pi / 4
    m = 4

    def raw(y, z, beta, gamma):
        ang = [2 * h * k for k in range(m)]
        P = {
            "A": [(math.cos(a), math.sin(a)) for a in ang],
            "B": [(y * math.cos(beta + a), y * math.sin(beta + a)) for a in ang],
            "C": [(z * math.cos(gamma + a), z * math.sin(gamma + a)) for a in ang],
        }
        for orb in "ABC":
            c = P[orb][0]
            ds = [
                round((c[0] - q[0]) ** 2 + (c[1] - q[1]) ** 2, 9)
                for nm in "ABC"
                for j, q in enumerate(P[nm])
                if not (nm == orb and j == 0)
            ]
            if max(Counter(ds).values()) < 4:
                return False
        return True

    def conds(y, z, beta, gamma, tol=1e-7):
        cb, sb = math.cos(beta), math.sin(beta)
        cg, sg = math.cos(gamma), math.sin(gamma)

        def Pf(r):
            return (r * r - 1) / (2 * r)

        def near(v, opts):
            return any(abs(v - o) < tol for o in opts)

        Q = (z * z - y * y) / (2 * y * z)
        return (
            near(Pf(y), [cb, -cb, sb, -sb])
            and near(Pf(z), [cg, -cg, sg, -sg])
            and near(Q, [math.cos(gamma - beta), -math.cos(gamma - beta),
                         math.sin(gamma - beta), -math.sin(gamma - beta)])
        )

    # construct configs hitting the witness distance for various branches
    import numpy as np

    rng = np.random.default_rng(3)
    checked = 0
    for _ in range(3000):
        beta = rng.uniform(0.06, math.pi / 2 - 0.06)
        gamma = rng.uniform(0.06, math.pi / 2 - 0.06)
        if (abs(beta - gamma) < 0.05 or abs(beta - h) < 0.03
                or abs(gamma - h) < 0.03 or abs(abs(gamma - beta) - h) < 0.03):
            continue
        if beta > gamma:
            beta, gamma = gamma, beta
        cb, sb = math.cos(beta), math.sin(beta)
        cg, sg = math.cos(gamma), math.sin(gamma)
        for pv in (cb, -cb, sb, -sb):
            y = pv + math.sqrt(pv * pv + 1)
            for qv in (cg, -cg, sg, -sg):
                z = qv + math.sqrt(qv * qv + 1)
                assert raw(y, z, beta, gamma) == conds(y, z, beta, gamma)
                checked += 1
    assert checked > 1000


@pytest.mark.slow
def test_spot_combos_unsat():
    """A few representative combos decide UNSAT in-window (needs z3)."""
    z3 = pytest.importorskip("z3")
    combos = [
        ("+cb", "+cg", "+cgb"),
        ("+sb", "-sg", "+sgb"),
        ("-cb", "+sg", "-cgb"),
    ]
    for c in combos:
        s = MOD._solver_for(c, window=True, convex=False, timeout_ms=60000)
        assert s.check() == z3.unsat, c


@pytest.mark.slow
def test_full_decision_clear():
    """Full 64-combo in-window decision is clear (all UNSAT). Needs z3."""
    pytest.importorskip("z3")
    res = MOD.decide_all(window=True, convex=False, timeout_ms=30000)
    assert res["counts"]["sat"] == 0
    assert res["counts"]["unknown"] == 0
    assert res["counts"]["unsat"] == 64
