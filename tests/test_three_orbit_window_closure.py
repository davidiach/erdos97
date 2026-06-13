"""Tests for the three-orbit (t=3) finite-m closure screen.

The planted-solution tests validate the reduction independently: they solve
the raw distance-equality systems numerically (no reduction) and assert that
the screen's pinning polynomials vanish and its solution lists contain the
planted points.  The identity tests validate each row-option family against
direct coordinate geometry.
"""

from __future__ import annotations

import importlib.util
import math
import pathlib
import sys

import numpy as np
import pytest
from scipy.optimize import fsolve

SPEC = importlib.util.spec_from_file_location(
    "check_three_orbit_window_closure",
    pathlib.Path(__file__).resolve().parents[1]
    / "scripts"
    / "check_three_orbit_window_closure.py",
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

RNG = np.random.default_rng(20260612)


def rel_close(a, b, tol=1e-7):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def circ_close(a, b, period, tol=1e-6):
    d = abs((a - b) % period)
    return min(d, period - d) < tol


def orbit_points(m, y, z, beta, gamma):
    h = math.pi / m
    ang = 2 * h * np.arange(m)
    return {
        "A": np.stack([np.cos(ang), np.sin(ang)], 1),
        "B": y * np.stack([np.cos(beta + ang), np.sin(beta + ang)], 1),
        "C": z * np.stack([np.cos(gamma + ang), np.sin(gamma + ang)], 1),
    }


def test_self_audit_atom_catalogue():
    rng = np.random.default_rng(7)
    for m in (3, 4, 5, 6, 9, 12):
        MOD.self_audit(m, 30, rng)


def test_pinned_row_polynomials_match_geometry():
    """Each pinned-row option's polynomial restates a true distance equality."""

    for m in (3, 4, 5, 6, 7, 8):
        h = math.pi / m
        for scale_own in (False, True):
            for opt in MOD.pinned_row_options(MOD.FLOAT, m, scale_own):
                roots = np.roots(np.array(opt["poly"], dtype=float))
                for r in roots:
                    if abs(r.imag) > 1e-10 or not (1e-6 < r.real < 1e3):
                        continue
                    y = float(r.real)
                    pts = orbit_points(m, y, 1.0, h, 1.5 * h)
                    center = pts["A"][0] if not scale_own else pts["B"][0]
                    own = pts["A"] if not scale_own else pts["B"]
                    cross = pts["B"] if not scale_own else pts["A"]
                    if opt["leftover"] == "":
                        a, o = opt["a"], opt["o"]
                        own_d = ((center - own[a]) ** 2).sum()
                        k = (o - 1) // 2 if not scale_own else None
                        if not scale_own:
                            cross_d = ((center - cross[k]) ** 2).sum()
                        else:
                            # B-to-A odd multiples: |B_0 - A_k|, 2k-1 = o
                            k = ((o + 1) // 2) % m
                            cross_d = ((center - cross[k]) ** 2).sum()
                        assert rel_close(own_d, cross_d), (m, scale_own, opt)
                    elif opt["leftover"] == "pole":
                        a = opt["a"]
                        own_d = ((center - own[a]) ** 2).sum()
                        assert rel_close(own_d, (1.0 + y) ** 2), (m, opt)
                    else:
                        o = opt["o"]
                        anti = own[m // 2]
                        own_d = ((center - anti) ** 2).sum()
                        if not scale_own:
                            k = (o - 1) // 2
                        else:
                            k = ((o + 1) // 2) % m
                        cross_d = ((center - cross[k]) ** 2).sum()
                        assert rel_close(own_d, cross_d), (m, scale_own, opt)


def test_bc_ratio_options_match_geometry():
    """Each BC ratio option satisfies its defining homogeneous equation."""

    for m in (3, 4, 5, 6, 7, 8):
        h = math.pi / m
        y = 1.1
        for center_is_b in (True, False):
            for opt in MOD.bc_ratio_options(MOD.FLOAT, m, center_is_b):
                rho = opt["ratio"]
                z = rho * y
                beta = 0.4 * h
                gamma = beta + h
                pts = orbit_points(m, y, z, beta, gamma)
                center = pts["B"][0] if center_is_b else pts["C"][0]
                own = pts["B"] if center_is_b else pts["C"]
                cross = pts["C"] if center_is_b else pts["B"]
                if opt["leftover"] == "":
                    a, o = opt["a"], opt["o"]
                    own_d = ((center - own[a]) ** 2).sum()
                    if center_is_b:
                        k = (o - 1) // 2  # |B_0 - C_k|: angle (2k+1) h
                    else:
                        k = ((o + 1) // 2) % m  # |C_0 - B_k|: angle (2k-1) h
                    cross_d = ((center - cross[k]) ** 2).sum()
                    assert rel_close(own_d, cross_d), (m, center_is_b, opt)
                elif opt["leftover"] == "pole":
                    a = opt["a"]
                    own_d = ((center - own[a]) ** 2).sum()
                    assert rel_close(own_d, (y + z) ** 2), (m, opt)
                else:
                    o = opt["o"]
                    anti = own[m // 2]
                    own_d = ((center - anti) ** 2).sum()
                    if center_is_b:
                        k = (o - 1) // 2
                    else:
                        k = ((o + 1) // 2) % m
                    cross_d = ((center - cross[k]) ** 2).sum()
                    assert rel_close(own_d, cross_d), (m, center_is_b, opt)


def _raw_side_system(m, a_shared, a_other, k1, k2):
    """The two raw branch-G equations pairing one offset, as residuals."""

    h = math.pi / m
    t1 = 4 * math.sin(a_shared * h) ** 2
    t2 = 4 * math.sin(a_other * h) ** 2

    def eqs(vars_):
        r, theta = vars_  # theta = offset
        e1 = 1 + r * r - 2 * r * math.cos(theta + 2 * k1 * h) - t1
        e2 = 1 + r * r - 2 * r * math.cos(theta - 2 * k2 * h) - t2 * r * r
        return [e1, e2]

    return eqs


def test_planted_generic_side_solutions():
    """fsolve the raw equation pairs and check the reduction recovers them."""

    found = 0
    for _ in range(300):
        m = int(RNG.integers(3, 10))
        h = math.pi / m
        avals = MOD.own_pair_avals(m)
        a1 = int(RNG.choice(avals))
        a2 = int(RNG.choice(avals))
        k1 = int(RNG.integers(0, m))
        k2 = int(RNG.integers(0, m))
        if MOD.is_quarter_cell(m, a1, a2, (k1 + k2) % m):
            continue
        eqs = _raw_side_system(m, a1, a2, k1, k2)
        guess = [RNG.uniform(0.3, 2.5), RNG.uniform(0, 2 * math.pi)]
        sol, info, ier, _ = fsolve(eqs, guess, full_output=True)
        if ier != 1 or max(abs(v) for v in eqs(sol)) > 1e-10:
            continue
        r, theta = float(sol[0]), float(sol[1])
        if r <= 1e-3:
            continue
        found += 1
        s = (k1 + k2) % m
        # the pinning polynomial must vanish at the planted radius
        poly = MOD.g_pin_poly(MOD.FLOAT, m, a1, a2, s)
        val = np.polyval(np.array(poly, dtype=float), r)
        scale = max(1.0, max(abs(c) for c in poly))
        assert abs(val) < 1e-6 * scale, (m, a1, a2, k1, k2, r, val)
        # and the side-solution list must contain (r, beta) with
        # beta = theta + 2 k1 h mod 2h ... the offset convention of the
        # screen is beta with cos(beta + 2 k1 h) = u1: theta IS beta here.
        orig_window = MOD.window
        MOD.window = lambda be, mm: (1e-3, 1e3)
        try:
            sols = MOD.g_side_solutions(
                MOD.FLOAT, m, {"a_shared": a1, "a_other": a2, "s": s}
            )
        finally:
            MOD.window = orig_window
        beta_expected = theta % (2 * h)
        hit = any(
            abs(rr - r) < 1e-6 and circ_close(bb, beta_expected, 2 * h)
            for rr, bb, _resid in sols
        )
        assert hit, (m, a1, a2, k1, k2, r, beta_expected, sols)
    assert found >= 30, f"too few planted side systems converged ({found})"


def test_planted_full_generic_join():
    """Plant a full branch-G solution (4 side equations) and require that the
    screen's join path reports it when the d-scan equalities also hold."""

    planted = 0
    for _ in range(1000):
        m = int(RNG.integers(3, 9))
        h = math.pi / m
        avals = MOD.own_pair_avals(m)
        a1 = int(RNG.choice(avals))
        a2 = int(RNG.choice(avals))
        a3 = int(RNG.choice(avals))
        k1, k2, k3, j1 = (int(RNG.integers(0, m)) for _ in range(4))
        if MOD.is_quarter_cell(m, a1, a2, (k1 + k2) % m) or MOD.is_quarter_cell(
            m, a1, a3, (j1 + k3) % m
        ):
            continue

        def eqs(v):
            y, beta, z, gamma = v
            t1 = 4 * math.sin(a1 * h) ** 2
            t2 = 4 * math.sin(a2 * h) ** 2
            t3 = 4 * math.sin(a3 * h) ** 2
            return [
                1 + y * y - 2 * y * math.cos(beta + 2 * k1 * h) - t1,
                1 + y * y - 2 * y * math.cos(beta - 2 * k2 * h) - t2 * y * y,
                1 + z * z - 2 * z * math.cos(gamma + 2 * j1 * h) - t1,
                1 + z * z - 2 * z * math.cos(gamma - 2 * k3 * h) - t3 * z * z,
            ]

        guess = [
            RNG.uniform(0.5, 2.0),
            RNG.uniform(0, 2 * h),
            RNG.uniform(0.5, 2.0),
            RNG.uniform(0, 2 * h),
        ]
        sol, info, ier, _ = fsolve(eqs, guess, full_output=True)
        if ier != 1 or max(abs(v) for v in eqs(sol)) > 1e-10:
            continue
        y, beta, z, gamma = (float(v) for v in sol)
        beta %= 2 * h
        gamma %= 2 * h
        edge = 1e-5
        if y <= 1e-3 or z <= 1e-3 or not (
            edge < beta and beta < gamma - edge and gamma < 2 * h - edge
        ):
            continue
        planted += 1
        orig_window = MOD.window
        MOD.window = lambda be, mm: (1e-3, 1e3)
        try:
            ylist = MOD.g_side_solutions(
                MOD.FLOAT,
                m,
                {"a_shared": a1, "a_other": a2, "s": (k1 + k2) % m},
            )
            zlist = MOD.g_side_solutions(
                MOD.FLOAT,
                m,
                {"a_shared": a1, "a_other": a3, "s": (j1 + k3) % m},
            )
            hit_y = [
                t
                for t in ylist
                if abs(t[0] - y) < 1e-6 and circ_close(t[1], beta, 2 * h)
            ]
            hit_z = [
                t
                for t in zlist
                if abs(t[0] - z) < 1e-6 and circ_close(t[1], gamma, 2 * h)
            ]
            assert hit_y, (m, a1, a2, k1, k2, y, beta)
            assert hit_z, (m, a1, a3, j1, k3, z, gamma)
            joined = MOD.g_join(MOD.FLOAT, m, hit_y[0], hit_z[0], a2, a3)
        finally:
            MOD.window = orig_window
        assert joined is not None
        # the first two equalities (side recoveries) must be tiny; the
        # d-scan residuals are whatever they are -- planted points need not
        # satisfy E4/E6, so only consistency of the join machinery is
        # asserted here.
        assert abs(joined.equalities[0]) < 1e-6
        assert abs(joined.equalities[1]) < 1e-6
    assert planted >= 15, f"too few full planted systems converged ({planted})"


@pytest.mark.slow
def test_screen_small_m_clear():
    rng = np.random.default_rng(1)
    for m in (3, 4, 5):
        rec = MOD.check_m(m, 10, rng)
        assert not rec["feasible_survivors"], rec
        assert not rec["unresolved"], rec
