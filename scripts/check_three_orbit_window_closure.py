#!/usr/bin/env python3
"""Finite-m closure screen for the three-orbit (t=3) C_m family.

Claim being screened (`docs/three-orbit-window-closure.md`, follow-up to the
review-pending reduction `docs/half-step-matching-reduction.md`): a strictly
convex polygon whose vertex set is three concentric regular ``m``-gons
(radii ``1, y, z``, relative rotations ``0, beta, gamma``) cannot be 4-bad,
i.e. cannot have, at every vertex, four other vertices on a circle centered
at that vertex.

Normalization: rotate so the first orbit has phase 0, scale its radius to 1,
shift orbit indices so ``beta, gamma in (0, 2h)`` with ``h = pi/m``, and
relabel the second/third orbits so ``beta < gamma``.  With ``m >= 3`` the
common center is interior, so strict convexity is equivalent to the three
per-period turn inequalities of the angular-order polygon
``..., C_{-1}, A_0, B_0, C_0, A_1, ...``; they also force the necessary
radius window ``cos h < y, z < 1/cos h``.  Offset 0 is excluded by the open
range, and inside ``0 < beta < gamma < 2h`` at most one of
``beta, gamma, gamma - beta`` can equal the half-step ``h``.  The search
therefore splits into four exhaustive branches:

- ``G``  : no half-step offset (all cross-orbit witnesses are singles);
- ``AB`` : ``beta = h`` (A-B cross pairs exist);
- ``AC`` : ``gamma = h`` (A-C cross pairs exist);
- ``BC`` : ``gamma - beta = h`` (B-C cross pairs exist).

In every branch each witness row decomposes into equidistance atoms (own
pairs, the own antipode for even ``m``, cross pairs and the cross pole on
the unique half-step pair, and cross singles).  Equating atom distances
gives, per discrete choice, equations linear in the cosine/sine of one
unknown offset; pairing the two equations that hit the same offset
eliminates the angle and pins the radii by univariate polynomials, after
which the offsets are recovered in closed form.  The screen enumerates all
discrete choices, runs this deterministic solution path in float64 inside
the necessary window, and emits every near-feasible joint configuration as
a candidate.  Each candidate is re-derived along the same path with
60-digit mpmath arithmetic: an equality residual above ``1e-20`` refutes
it, below ``1e-45`` it counts as satisfied, and anything between is
reported as unresolved (and blocks ``--assert-clear``).  Strict-inequality
margins inside ``1e-30`` of zero are re-checked at 240 digits; exact
boundary hits are excluded by strictness but reported.  Any candidate that
survives with strict margins is confirmed against the direct 4-bad
definition and reported loudly as a potential counterexample configuration
-- never silently accepted.

This checker is a float64-screened, escalation-audited finite-``m`` closure
*screen* with a built-in random-configuration audit of its atom catalogue.
It is not an all-``m`` lemma, it is not a proof of Erdos Problem #97, and
it does not produce or certify any counterexample.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from dataclasses import dataclass, field

import numpy as np

JOIN_BAND = 1e-7
WINDOW_PAD = 1e-9
EQ_ACCEPT = "1e-45"
EQ_REJECT = "1e-20"
MARGIN_BAND = "1e-30"
SEED = 20260612


class EscalationInconclusive(RuntimeError):
    """High-precision re-derivation could not be completed soundly."""


# ---------------------------------------------------------------------------
# Math backends: the same deterministic solution path runs in float64 for
# the screen and in 60-digit mpmath for escalation.
# ---------------------------------------------------------------------------


class FloatBackend:
    name = "float64"
    band = JOIN_BAND

    pi = math.pi

    @staticmethod
    def num(x):
        return float(x)

    cos = staticmethod(math.cos)
    sin = staticmethod(math.sin)
    atan2 = staticmethod(math.atan2)

    @staticmethod
    def sqrt(v):
        return math.sqrt(max(0.0, v))

    @staticmethod
    def real_roots(coeffs, lo, hi, pad):
        arr = np.asarray(coeffs, dtype=float)
        scale = np.max(np.abs(arr)) if arr.size else 0.0
        if scale == 0.0:
            return []
        # trim leading coefficients that are zero up to float noise; they
        # are exact zeros of the underlying algebraic coefficients and
        # would otherwise inject spurious huge roots
        keep = np.abs(arr) > 1e-12 * scale
        first = int(np.argmax(keep)) if keep.any() else arr.size
        arr = arr[first:]
        if arr.size <= 1:
            return []
        out = []
        for r in np.roots(arr):
            # multiplicity-k roots split into clusters with imaginary parts
            # of order eps**(1/k); accept generously, the residual bands and
            # the escalation re-derivation filter spurious accepts
            if abs(r.imag) < 1e-5 * max(1.0, abs(r.real)) and (
                lo - pad < r.real < hi + pad
            ):
                out.append(float(r.real))
        return out

    @staticmethod
    def is_zero(v):
        return abs(v) < JOIN_BAND

    @staticmethod
    def abs(v):
        return abs(v)


class MPBackend:
    name = "mp60"

    def __init__(self, dps: int = 60):
        import mpmath as mp

        self.mp = mp
        self.dps = dps
        self.band = mp.mpf("1e-30")
        self.pi = None  # set per-use to honor dps

    def _ctx(self):
        self.mp.mp.dps = self.dps
        return self.mp

    def num(self, x):
        return self._ctx().mpf(x)

    def cos(self, v):
        return self._ctx().cos(v)

    def sin(self, v):
        return self._ctx().sin(v)

    def sqrt(self, v):
        mp = self._ctx()
        if v < 0 and -v < mp.mpf(EQ_ACCEPT):
            return mp.mpf(0)
        return mp.sqrt(v)

    def atan2(self, a, b):
        return self._ctx().atan2(a, b)

    @property
    def PI(self):
        return self._ctx().pi

    def real_roots(self, coeffs, lo, hi, pad):
        mp = self._ctx()
        arr = [mp.mpf(c) for c in coeffs]
        scale = max((abs(c) for c in arr), default=mp.mpf(0))
        if scale == 0:
            return []
        thresh = scale * mp.mpf(10) ** (-(self.dps - 8))
        while arr and abs(arr[0]) < thresh:
            arr.pop(0)
        if len(arr) <= 1:
            return []
        try:
            roots = mp.polyroots(arr, maxsteps=5000, extraprec=2 * self.dps)
        except Exception as exc:
            # a root-finding failure must escalate, never silently read as
            # "no roots" (which downstream would become a refuted verdict)
            raise EscalationInconclusive(
                f"mp.polyroots failed at dps={self.dps}: {exc}"
            ) from exc
        imag_tol = mp.mpf(10) ** (-(self.dps // 3))
        out = []
        for r in roots:
            if abs(mp.im(r)) < imag_tol * max(1, abs(mp.re(r))) and (
                lo - pad < mp.re(r) < hi + pad
            ):
                out.append(mp.re(r))
        return out

    def is_zero(self, v):
        return abs(v) < self.band

    def abs(self, v):
        return abs(v)


FLOAT = FloatBackend()


def be_pi(be):
    return be.PI if isinstance(be, MPBackend) else math.pi


# ---------------------------------------------------------------------------
# Shared structure
# ---------------------------------------------------------------------------


def own_pair_avals(m: int) -> list[int]:
    """Own-pair half-offsets a with {X_a, X_{m-a}} a genuine 2-point pair."""

    return list(range(1, (m + 1) // 2 if m % 2 else m // 2))


def odd_offsets(m: int) -> list[int]:
    """Odd multiples o of h with {o, 2m-o} a genuine cross pair (o < m)."""

    return list(range(1, m, 2))


@dataclass
class Solution:
    """One solved configuration with its residuals and strict margins."""

    y: object
    z: object
    beta: object
    gamma: object
    equalities: list = field(default_factory=list)
    margins: list = field(default_factory=list)


def turn_margins(be, m: int, y, z, beta, gamma) -> list:
    """Signed per-period turn determinants of the angular-order polygon."""

    h = be_pi(be) / m
    one = be.num(1)
    a0 = (one, be.num(0))
    a1 = (be.cos(2 * h), be.sin(2 * h))
    b0 = (y * be.cos(beta), y * be.sin(beta))
    c0 = (z * be.cos(gamma), z * be.sin(gamma))
    cm1 = (z * be.cos(gamma - 2 * h), z * be.sin(gamma - 2 * h))

    def turn(u, v, w):
        return (v[0] - u[0]) * (w[1] - v[1]) - (v[1] - u[1]) * (w[0] - v[0])

    return [turn(cm1, a0, b0), turn(a0, b0, c0), turn(b0, c0, a1)]


def base_margins(be, m: int, sol: Solution) -> list:
    """All strict constraints: turns, offset ranges, positive radii."""

    h = be_pi(be) / m
    return turn_margins(be, m, sol.y, sol.z, sol.beta, sol.gamma) + [
        sol.beta,
        sol.gamma - sol.beta,
        2 * h - sol.gamma,
        sol.y,
        sol.z,
    ]


def window(be, m: int):
    h = be_pi(be) / m
    c = be.cos(h)
    return c, 1 / c


def solve_offset_pair(be, w1, phi1, w2, phi2):
    """Solve cos(t + phi1) = w1, cos(t + phi2) = w2 for (cos t, sin t).

    Returns a list of ((ct, st), unit_residual); the unit residual is the
    deviation of the solved pair from the unit circle (an equality of the
    system in the nonsingular case, where the linear solve is exact and the
    circle condition is the pinning constraint already enforced upstream).
    """

    det = be.sin(phi1 - phi2)
    if be.abs(det) > 1e-9:
        ct = (-w1 * be.sin(phi2) + w2 * be.sin(phi1)) / det
        st = (-w1 * be.cos(phi2) + w2 * be.cos(phi1)) / det
        return [((ct, st), ct * ct + st * st - 1)]
    # parallel constraints: consistent iff w1 = cos(phi1 - phi2) * w2
    sign = be.cos(phi1 - phi2)
    out = []
    mism = w1 - sign * w2
    if be.abs(w1) <= 1 + be.num(1e-9):
        w = w1
        st_abs = be.sqrt(1 - w * w)
        for s in (1, -1):
            t = be.atan2(s * st_abs, w) - phi1
            out.append(((be.cos(t), be.sin(t)), mism))
    return out


def recover_offset(be, u1, u2, delta, period):
    """Offsets theta2 mod period with cos(theta2)=u2, cos(theta2+delta)=u1.

    Returns (theta2, consistency_residual) pairs; the residual restates the
    pinning polynomial and vanishes exactly at exact solutions.
    """

    if be.abs(u1) > 1 + 1e-9 or be.abs(u2) > 1 + 1e-9:
        return []
    sd = be.sin(delta)
    cd = be.cos(delta)
    out = []
    if be.abs(sd) > 1e-9:
        st2 = (u2 * cd - u1) / sd
        resid = st2 * st2 + u2 * u2 - 1
        theta = be.atan2(st2, u2)
        out.append((theta % period, resid))
    else:
        st2 = be.sqrt(1 - u2 * u2)
        resid = cd * u2 - u1
        for s in (1, -1):
            theta = be.atan2(s * st2, u2)
            out.append((theta % period, resid))
    return out


# ---------------------------------------------------------------------------
# Branch G: no half-step offset.  Every row is own pair + two cross singles.
#
# Equations (center representative, h = pi/m, t_a = 4 sin^2(a h)):
#   A-row, a1:  cos(beta + 2 k1 h) = u_ab(y) ; cos(gamma + 2 j1 h) = u_ac(z)
#       with 2 y u_ab = 1 + y^2 - t_{a1}, 2 z u_ac = 1 + z^2 - t_{a1}
#   B-row, a2:  cos(beta - 2 k2 h) = v_ab(y),  2 y v_ab = 1 + y^2 - t_{a2} y^2
#               cos((gamma-beta) + 2 j2 h) = (y^2 + z^2 - t_{a2} y^2)/(2 y z)
#   C-row, a3:  cos(gamma - 2 k3 h) = v_ac(z),  2 z v_ac = 1 + z^2 - t_{a3} z^2
#               cos((gamma-beta) - 2 j3 h) = (y^2 + z^2 - t_{a3} z^2)/(2 y z)
# Pairing the two beta equations (angle gap 2 s h, s = k1 + k2 mod m)
# eliminates beta and pins y; likewise for gamma/z.  j2, j3 are then
# discrete equality scans on the recovered configuration.
# ---------------------------------------------------------------------------


def is_quarter_cell(m: int, a_shared: int, a_other: int, s: int) -> bool:
    """Degenerate identity cell of the branch-G side reduction.

    The pinning polynomial vanishes identically iff sin(2 s h) = 0 with
    cos(2 s h) = -1 and t_{a_shared} = t_{a_other} = 2, i.e. iff
    m = 0 mod 4, a_shared = a_other = m/4 and s = m/2 (then the two row
    equations coincide and leave a one-parameter family).  These cells are
    skipped by the point screen and reported as named open sub-cases.
    """

    return (
        m % 4 == 0
        and a_shared == m // 4
        and a_other == m // 4
        and s == m // 2
    )


def g_pin_poly(be, m: int, a_shared: int, a_other: int, s: int):
    """Pinning polynomial coefficients for one side system of branch G."""

    h = be_pi(be) / m
    t1 = 4 * be.sin(a_shared * h) ** 2
    t2 = 4 * be.sin(a_other * h) ** 2
    cd = be.cos(2 * s * h)
    sd = be.sin(2 * s * h)
    one = be.num(1)
    # N1 = r^2 + (1 - t1); N2 = (1 - t2) r^2 + 1; both equal 2 r u.
    # P = (cd N2 - N1)^2 - (4 r^2 - N2^2) sd^2, descending coefficients.
    n1 = [one, be.num(0), 1 - t1]
    n2 = [1 - t2, be.num(0), one]

    def polymul(p, q):
        out = [be.num(0)] * (len(p) + len(q) - 1)
        for i, pi_ in enumerate(p):
            for j, qj in enumerate(q):
                out[i + j] = out[i + j] + pi_ * qj
        return out

    def polysub(p, q):
        n = max(len(p), len(q))
        p = [be.num(0)] * (n - len(p)) + list(p)
        q = [be.num(0)] * (n - len(q)) + list(q)
        return [a - b for a, b in zip(p, q)]

    lin = polysub([cd * c for c in n2], n1)
    if be.abs(sd) < 1e-9:
        # singular gap (delta = 0 or pi): P is the exact square of the
        # linear factor; use the factor itself to avoid double roots
        return lin
    four_r2 = [be.num(4), be.num(0), be.num(0)]
    return polysub(
        polymul(lin, lin),
        [sd * sd * c for c in polysub(four_r2, polymul(n2, n2))],
    )


def g_side_solutions(be, m: int, sysd: dict) -> list[tuple]:
    """(radius, offset, residual) tuples for one branch-G side system."""

    if is_quarter_cell(m, sysd["a_shared"], sysd["a_other"], sysd["s"]):
        raise ValueError(f"degenerate quarter cell m={m} {sysd}")
    h = be_pi(be) / m
    lo, hi = window(be, m)
    t1 = 4 * be.sin(sysd["a_shared"] * h) ** 2
    t2 = 4 * be.sin(sysd["a_other"] * h) ** 2
    delta = 2 * sysd["s"] * h
    poly = g_pin_poly(be, m, sysd["a_shared"], sysd["a_other"], sysd["s"])
    scale = max(be.abs(c) for c in poly)
    if scale < 1e-12:
        raise RuntimeError(
            f"unexpected identically-zero pinning polynomial m={m} {sysd}"
        )
    out = []
    for r in be.real_roots(poly, lo, hi, be.num(WINDOW_PAD)):
        if r <= 0:
            continue
        u1 = (1 + r * r - t1) / (2 * r)
        u2 = (1 + r * r - t2 * r * r) / (2 * r)
        for theta, resid in recover_offset(be, u1, u2, delta, 2 * h):
            out.append((r, theta, resid))
    return out


def g_join(be, m: int, side_y: tuple, side_z: tuple, a2: int, a3: int) -> Solution | None:
    """Join two side solutions and scan the d-equations; None if no scan hit."""

    h = be_pi(be) / m
    y, beta, res_y = side_y
    z, gamma, res_z = side_z
    if not (0 < beta < gamma < 2 * h):
        return None
    t2 = 4 * be.sin(a2 * h) ** 2
    t3 = 4 * be.sin(a3 * h) ** 2
    d = gamma - beta
    v1 = (y * y + z * z - t2 * y * y) / (2 * y * z)
    v2 = (y * y + z * z - t3 * z * z) / (2 * y * z)
    best1 = min(
        (be.abs(be.cos(d + 2 * j * h) - v1) for j in range(m)),
    )
    best2 = min(
        (be.abs(be.cos(d - 2 * j * h) - v2) for j in range(m)),
    )
    sol = Solution(y=y, z=z, beta=beta, gamma=gamma)
    sol.equalities = [res_y, res_z, best1, best2]
    sol.margins = base_margins(be, m, sol)
    return sol


def screen_generic(m: int) -> tuple[int, list[dict], int]:
    be = FLOAT
    avals = own_pair_avals(m)
    side_cache: dict[tuple, list[tuple]] = {}
    systems = 0
    quarter_cells = 0
    for a1 in avals:
        for ao in avals:
            for s in range(m):
                if is_quarter_cell(m, a1, ao, s):
                    quarter_cells += 1
                    continue
                systems += 1
                sysd = {"a_shared": a1, "a_other": ao, "s": s}
                sols = g_side_solutions(be, m, sysd)
                if sols:
                    side_cache[(a1, ao, s)] = sols
    candidates = []
    for (a1, a2, s_ab), ylist in side_cache.items():
        for (a1c, a3, s_ac), zlist in side_cache.items():
            if a1c != a1:
                continue
            for sy, sz in itertools.product(ylist, zlist):
                sol = g_join(be, m, sy, sz, a2, a3)
                if sol is None:
                    continue
                if max(map(abs, sol.equalities)) < JOIN_BAND and min(
                    sol.margins
                ) > -JOIN_BAND:
                    candidates.append(
                        {
                            "branch": "G",
                            "m": m,
                            "desc": {
                                "a1": a1,
                                "a2": a2,
                                "a3": a3,
                                "s_ab": s_ab,
                                "s_ac": s_ac,
                            },
                            "point": [sol.y, sol.z, sol.beta, sol.gamma],
                        }
                    )
    return systems, candidates, quarter_cells


def g_cell_solutions(be, m: int, desc: dict) -> list[Solution]:
    """All joined branch-G solutions of one candidate's cell."""

    ylist = g_side_solutions(
        be, m, {"a_shared": desc["a1"], "a_other": desc["a2"], "s": desc["s_ab"]}
    )
    zlist = g_side_solutions(
        be, m, {"a_shared": desc["a1"], "a_other": desc["a3"], "s": desc["s_ac"]}
    )
    out = []
    for sy, sz in itertools.product(ylist, zlist):
        sol = g_join(be, m, sy, sz, desc["a2"], desc["a3"])
        if sol is not None:
            out.append(sol)
    return out


# ---------------------------------------------------------------------------
# Half-step branches AB (beta = h) and AC (gamma = h).
#
# The pinned orbit pair exchanges cross pairs at odd multiples o h (plus a
# pole when m is odd); its two centers' rows pin the pinned radius by
# univariate polynomials.  Row options for a pinned center (own distances
# scaled by r^2 for the non-unit center, cross distances 1 + r^2 - 2 r
# cos(o h) either way):
#   {own pair a, cross pair o}                  poly only
#   {own pair a, cross pole, free single}       m odd, poly + leftover
#   {own antipode, cross pair o, free single}   m even, poly + leftover
# ({cross pair, cross pole, single} needs cos(o h) = -1, impossible for
# o <= m - 1; {own pair, own antipode} forces a = m/2; {own pair, two free
# singles} forces the free offset into {0, h}, excluded by the open branch
# ranges -- all auto-killed and intentionally not enumerated.)
#
# The free-orbit center row is own pair + one single to each pinned orbit;
# its two equations are linear in (cos, sin) of the free offset, and the
# unit-circle condition pins the free radius by a quartic.
# ---------------------------------------------------------------------------


def pinned_row_options(be, m: int, scale_own: bool) -> list[dict]:
    h = be_pi(be) / m
    options = []
    for a in own_pair_avals(m):
        t = 4 * be.sin(a * h) ** 2
        for o in odd_offsets(m):
            c = be.cos(o * h)
            poly = (
                [t - 1, 2 * c, be.num(-1)]
                if scale_own
                else [be.num(1), -2 * c, 1 - t]
            )
            options.append({"poly": poly, "leftover": "", "a": a, "o": o})
        if m % 2 == 1:
            poly = (
                [t - 1, be.num(-2), be.num(-1)]
                if scale_own
                else [be.num(1), be.num(2), 1 - t]
            )
            options.append({"poly": poly, "leftover": "pole", "a": a})
    if m % 2 == 0:
        for o in odd_offsets(m):
            c = be.cos(o * h)
            poly = (
                [be.num(3), 2 * c, be.num(-1)]
                if scale_own
                else [be.num(1), -2 * c, be.num(-3)]
            )
            options.append({"poly": poly, "leftover": "antipode", "o": o})
    return options


def free_row_solutions(be, m: int, r_pin, a3: int, k3: int, j3: int) -> list[tuple]:
    """Solve the free-center row; returns (r_free, (ct, st), residual)."""

    h = be_pi(be) / m
    lo, hi = window(be, m)
    t3 = 4 * be.sin(a3 * h) ** 2
    phi1 = -2 * k3 * h
    phi2 = -(2 * j3 + 1) * h
    det = be.sin(phi1 - phi2)
    out = []
    if be.abs(det) < 1e-9:
        sign = be.cos(phi1 - phi2)
        c2 = (1 - t3) * (r_pin - sign)
        c0 = r_pin - sign * r_pin * r_pin
        roots = be.real_roots([c2, be.num(0), c0], lo, hi, be.num(WINDOW_PAD))
    else:
        s1, s2 = be.sin(phi1), be.sin(phi2)
        c1, c2_ = be.cos(phi1), be.cos(phi2)
        n1 = [1 - t3, be.num(0), be.num(1)]
        n2 = [1 - t3, be.num(0), r_pin * r_pin]
        num_c = [s1 * x / r_pin - s2 * w for x, w in zip(n2, n1)]
        num_s = [c1 * x / r_pin - c2_ * w for x, w in zip(n2, n1)]

        def polymul(p, q):
            res = [be.num(0)] * (len(p) + len(q) - 1)
            for i, pi_ in enumerate(p):
                for j, qj in enumerate(q):
                    res[i + j] = res[i + j] + pi_ * qj
            return res

        quart = polymul(num_c, num_c)
        for i, v in enumerate(polymul(num_s, num_s)):
            quart[i] = quart[i] + v
        d2 = (2 * det) ** 2
        # subtract d2 * r^2  (degree-4 list, r^2 coefficient at index 2)
        quart[2] = quart[2] - d2
        roots = be.real_roots(quart, lo, hi, be.num(WINDOW_PAD))
    for r in roots:
        if r <= 0:
            continue
        w1 = (1 + r * r - t3 * r * r) / (2 * r)
        w2 = (r_pin * r_pin + r * r - t3 * r * r) / (2 * r_pin * r)
        for (ct, st), resid in solve_offset_pair(be, w1, phi1, w2, phi2):
            out.append((r, (ct, st), resid))
    return out


def leftover_residual(be, m: int, which: str, y, z, beta, gamma, kind: str, center: str):
    """Distance-match residual for a pole/antipode row's free-orbit single."""

    h = be_pi(be) / m
    if which == "AB":
        if center == "unit":
            target = (1 + y) ** 2 if kind == "pole" else be.num(4)
            pool = [
                1 + z * z - 2 * z * be.cos(gamma + 2 * k * h) for k in range(m)
            ]
        else:
            target = (1 + y) ** 2 if kind == "pole" else 4 * y * y
            pool = [
                y * y + z * z - 2 * y * z * be.cos((gamma - beta) + 2 * k * h)
                for k in range(m)
            ]
    else:
        if center == "unit":
            target = (1 + z) ** 2 if kind == "pole" else be.num(4)
            pool = [1 + y * y - 2 * y * be.cos(beta + 2 * k * h) for k in range(m)]
        else:
            target = (1 + z) ** 2 if kind == "pole" else 4 * z * z
            pool = [
                y * y + z * z - 2 * y * z * be.cos((gamma - beta) - 2 * k * h)
                for k in range(m)
            ]
    return min(be.abs(target - d) for d in pool)


def halfstep_solutions(
    be, m: int, which: str, opt_u: dict, opt_s: dict, a3: int, k3: int, j3: int
) -> list[Solution]:
    """Solve one full half-step system (AB or AC) at backend precision."""

    h = be_pi(be) / m
    lo, hi = window(be, m)
    roots_u = be.real_roots(opt_u["poly"], lo, hi, be.num(WINDOW_PAD))
    roots_s = be.real_roots(opt_s["poly"], lo, hi, be.num(WINDOW_PAD))
    out: list[Solution] = []
    for ru in roots_u:
        for rs in roots_s:
            if ru <= 0 or rs <= 0:
                continue
            pin_resid = ru - rs
            if be.abs(pin_resid) > 1e-4:
                continue
            r_pin = (ru + rs) / 2
            for r_free, (ct, st), circ_resid in free_row_solutions(
                be, m, r_pin, a3, k3, j3
            ):
                theta = be.atan2(st, ct) % (2 * h)
                if which == "AB":
                    y, z = r_pin, r_free
                    beta, gamma = h, theta
                    range_ok = h < gamma < 2 * h
                else:
                    y, z = r_free, r_pin
                    beta, gamma = theta, h
                    range_ok = 0 < beta < h
                if not range_ok:
                    continue
                sol = Solution(y=y, z=z, beta=beta, gamma=gamma)
                sol.equalities = [pin_resid, circ_resid]
                for opt, center in ((opt_u, "unit"), (opt_s, "scaled")):
                    if opt["leftover"]:
                        sol.equalities.append(
                            leftover_residual(
                                be, m, which, y, z, beta, gamma,
                                opt["leftover"], center,
                            )
                        )
                sol.margins = base_margins(be, m, sol)
                out.append(sol)
    return out


def screen_halfstep(m: int, which: str) -> tuple[int, list[dict]]:
    be = FLOAT
    opts_u = pinned_row_options(be, m, scale_own=False)
    opts_s = pinned_row_options(be, m, scale_own=True)
    systems = 0
    candidates = []
    avals = own_pair_avals(m)
    for iu, opt_u in enumerate(opts_u):
        ru = be.real_roots(opt_u["poly"], *window(be, m), be.num(WINDOW_PAD))
        if not ru:
            systems += len(opts_s)
            continue
        for is_, opt_s in enumerate(opts_s):
            systems += 1
            rs = be.real_roots(opt_s["poly"], *window(be, m), be.num(WINDOW_PAD))
            if not rs or min(
                abs(a - b) for a in ru for b in rs
            ) > JOIN_BAND:
                continue
            for a3 in avals:
                for k3 in range(m):
                    for j3 in range(m):
                        for sol in halfstep_solutions(
                            be, m, which, opt_u, opt_s, a3, k3, j3
                        ):
                            if max(map(abs, sol.equalities)) < JOIN_BAND and min(
                                sol.margins
                            ) > -JOIN_BAND:
                                candidates.append(
                                    {
                                        "branch": which,
                                        "m": m,
                                        "desc": {
                                            "iu": iu,
                                            "is": is_,
                                            "a3": a3,
                                            "k3": k3,
                                            "j3": j3,
                                        },
                                        "point": [
                                            sol.y,
                                            sol.z,
                                            sol.beta,
                                            sol.gamma,
                                        ],
                                    }
                                )
    return systems, candidates


def halfstep_cell_solutions(be, m: int, which: str, desc: dict) -> list[Solution]:
    opts_u = pinned_row_options(be, m, scale_own=False)
    opts_s = pinned_row_options(be, m, scale_own=True)
    return halfstep_solutions(
        be,
        m,
        which,
        opts_u[desc["iu"]],
        opts_s[desc["is"]],
        desc["a3"],
        desc["k3"],
        desc["j3"],
    )


# ---------------------------------------------------------------------------
# Branch BC (gamma = beta + h, beta in (0, h)).
#
# B-C cross distances are homogeneous in (y, z), so each B- or C-center row
# pins the ratio rho = z/y to an algebraic constant:
#   {own pair a, cross pair o}:    z^2 - 2 cos(o h) y z + (1 - t_a) y^2 = 0
#   {own pair a, cross pole}:      (y + z)^2 = t_a y^2 (m odd) + A-single
#   {own antipode, cross pair o}:  z^2 - 2 cos(o h) y z - 3 y^2 = 0 (m even)
#                                  + A-single
# (C-center rows are the same with y and z swapped.)  Consistency of the two
# ratios is an exact algebraic condition; the A-row (own pair + B-single +
# C-single) then pins y by the unit-circle quartic exactly as in the other
# branches.
# ---------------------------------------------------------------------------


RHO_FLOOR = 1e-9


def bc_ratio_options(be, m: int, center_is_b: bool) -> list[dict]:
    """Ratio options for BC-branch pinned rows, keyed by content.

    Options with ratio (or discriminant) within ``RHO_FLOOR`` of zero are
    excluded deterministically in every backend: an exactly-zero ratio is a
    rounding-noise sign away from inclusion otherwise, and any ratio below
    the floor is window-killed regardless (z/y < 1e-9 cannot keep both
    radii inside ``(cos h, sec h)``), so the exclusion loses no solutions
    while keeping float64 and high-precision option lists aligned.
    """

    h = be_pi(be) / m
    out = []
    for a in own_pair_avals(m):
        t = 4 * be.sin(a * h) ** 2
        for o in odd_offsets(m):
            c = be.cos(o * h)
            disc = c * c - 1 + t
            if disc < RHO_FLOOR * RHO_FLOOR:
                if disc > -RHO_FLOOR * RHO_FLOOR:
                    disc = be.num(0)
                else:
                    continue
            root = be.sqrt(disc)
            for sgn in (1, -1):
                rho = c + sgn * root
                if rho <= RHO_FLOOR:
                    continue
                ratio = rho if center_is_b else 1 / rho
                out.append(
                    {"ratio": ratio, "leftover": "", "a": a, "o": o, "sgn": sgn}
                )
        if m % 2 == 1:
            rho = 2 * be.sin(a * h) - 1
            if rho > RHO_FLOOR:
                ratio = rho if center_is_b else 1 / rho
                out.append({"ratio": ratio, "leftover": "pole", "a": a})
    if m % 2 == 0:
        for o in odd_offsets(m):
            c = be.cos(o * h)
            root = be.sqrt(c * c + 3)
            for sgn in (1, -1):
                rho = c + sgn * root
                if rho <= RHO_FLOOR:
                    continue
                ratio = rho if center_is_b else 1 / rho
                out.append(
                    {
                        "ratio": ratio,
                        "leftover": "antipode",
                        "o": o,
                        "sgn": sgn,
                    }
                )
    return out


def bc_option_from_meta(be, m: int, meta: dict, center_is_b: bool) -> dict | None:
    """Rebuild one BC ratio option from its content key at backend precision."""

    for opt in bc_ratio_options(be, m, center_is_b):
        if (
            opt["leftover"] == meta["leftover"]
            and opt.get("a") == meta.get("a")
            and opt.get("o") == meta.get("o")
            and opt.get("sgn") == meta.get("sgn")
        ):
            return opt
    return None


def bc_solutions(
    be, m: int, opt_b: dict, opt_c: dict, a1: int, k1: int, j1: int
) -> list[Solution]:
    h = be_pi(be) / m
    lo, hi = window(be, m)
    ratio_resid = opt_b["ratio"] - opt_c["ratio"]
    rho = (opt_b["ratio"] + opt_c["ratio"]) / 2
    t1 = 4 * be.sin(a1 * h) ** 2
    phi1 = 2 * k1 * h
    phi2 = (2 * j1 + 1) * h
    det = be.sin(phi1 - phi2)
    out: list[Solution] = []
    if be.abs(det) < 1e-9:
        sign = be.cos(phi1 - phi2)
        # rho * N1(y) = sign * N2(y): N1 = y^2 + (1-t1), N2 = rho^2 y^2 + (1-t1)
        c2 = rho - sign * rho * rho
        c0 = (1 - t1) * (rho - sign)
        roots = be.real_roots([c2, be.num(0), c0], lo, hi, be.num(WINDOW_PAD))
    else:
        s1, s2 = be.sin(phi1), be.sin(phi2)
        c1, c2_ = be.cos(phi1), be.cos(phi2)
        n1 = [be.num(1), be.num(0), 1 - t1]
        n2 = [rho * rho, be.num(0), 1 - t1]
        num_c = [s1 * x / rho - s2 * w for x, w in zip(n2, n1)]
        num_s = [c1 * x / rho - c2_ * w for x, w in zip(n2, n1)]

        def polymul(p, q):
            res = [be.num(0)] * (len(p) + len(q) - 1)
            for i, pi_ in enumerate(p):
                for j, qj in enumerate(q):
                    res[i + j] = res[i + j] + pi_ * qj
            return res

        quart = polymul(num_c, num_c)
        for i, v in enumerate(polymul(num_s, num_s)):
            quart[i] = quart[i] + v
        quart[2] = quart[2] - (2 * det) ** 2
        roots = be.real_roots(quart, lo, hi, be.num(WINDOW_PAD))
    for y in roots:
        if y <= 0:
            continue
        z = rho * y
        lo_f, hi_f = window(be, m)
        if not (lo_f - WINDOW_PAD < z < hi_f + WINDOW_PAD):
            continue
        w1 = (1 + y * y - t1) / (2 * y)
        w2 = (1 + z * z - t1) / (2 * z)
        for (cb, sb), circ_resid in solve_offset_pair(be, w1, phi1, w2, phi2):
            beta = be.atan2(sb, cb) % (2 * h)
            if not (0 < beta < h):
                continue
            gamma = beta + h
            sol = Solution(y=y, z=z, beta=beta, gamma=gamma)
            sol.equalities = [ratio_resid, circ_resid]
            for opt, center in ((opt_b, "B"), (opt_c, "C")):
                if opt["leftover"]:
                    sol.equalities.append(
                        bc_leftover_residual(
                            be, m, y, z, beta, gamma, opt["leftover"], center
                        )
                    )
            sol.margins = base_margins(be, m, sol)
            out.append(sol)
    return out


def bc_leftover_residual(be, m: int, y, z, beta, gamma, kind: str, center: str):
    h = be_pi(be) / m
    if center == "B":
        target = (y + z) ** 2 if kind == "pole" else 4 * y * y
        pool = [1 + y * y - 2 * y * be.cos(beta - 2 * k * h) for k in range(m)]
    else:
        target = (y + z) ** 2 if kind == "pole" else 4 * z * z
        pool = [1 + z * z - 2 * z * be.cos(gamma - 2 * k * h) for k in range(m)]
    return min(be.abs(target - d) for d in pool)


def screen_bc(m: int) -> tuple[int, list[dict]]:
    be = FLOAT
    b_opts = bc_ratio_options(be, m, center_is_b=True)
    c_opts = bc_ratio_options(be, m, center_is_b=False)
    avals = own_pair_avals(m)
    systems = 0
    candidates = []
    def content_key(opt: dict) -> dict:
        return {
            k: opt[k] for k in ("leftover", "a", "o", "sgn") if k in opt
        }

    for opt_b in b_opts:
        for opt_c in c_opts:
            systems += 1
            if abs(opt_b["ratio"] - opt_c["ratio"]) > JOIN_BAND * max(
                1.0, abs(opt_b["ratio"])
            ):
                continue
            for a1 in avals:
                for k1 in range(m):
                    for j1 in range(m):
                        for sol in bc_solutions(
                            be, m, opt_b, opt_c, a1, k1, j1
                        ):
                            if max(map(abs, sol.equalities)) < JOIN_BAND and min(
                                sol.margins
                            ) > -JOIN_BAND:
                                candidates.append(
                                    {
                                        "branch": "BC",
                                        "m": m,
                                        "desc": {
                                            "opt_b": content_key(opt_b),
                                            "opt_c": content_key(opt_c),
                                            "a1": a1,
                                            "k1": k1,
                                            "j1": j1,
                                        },
                                        "point": [
                                            sol.y,
                                            sol.z,
                                            sol.beta,
                                            sol.gamma,
                                        ],
                                    }
                                )
    return systems, candidates


def bc_cell_solutions(be, m: int, desc: dict) -> list[Solution]:
    opt_b = bc_option_from_meta(be, m, desc["opt_b"], center_is_b=True)
    opt_c = bc_option_from_meta(be, m, desc["opt_c"], center_is_b=False)
    if opt_b is None or opt_c is None:
        raise EscalationInconclusive(
            f"BC option content key not reproducible at {be.name}: {desc}"
        )
    return bc_solutions(
        be,
        m,
        opt_b,
        opt_c,
        desc["a1"],
        desc["k1"],
        desc["j1"],
    )


# ---------------------------------------------------------------------------
# Escalation and confirmation
# ---------------------------------------------------------------------------


def brute_force_min_spread(be, m: int, y, z, beta, gamma):
    """Per-center minimum 4-window spread of squared distances (direct test).

    Vanishes exactly at a 4-bad configuration; used as the final independent
    confirmation for any candidate that survives escalation.
    """

    h = be_pi(be) / m
    orbits = [
        (be.num(1), be.num(0)),
        (y, beta),
        (z, gamma),
    ]
    pts = [
        [
            (r * be.cos(ph + 2 * k * h), r * be.sin(ph + 2 * k * h))
            for k in range(m)
        ]
        for r, ph in orbits
    ]
    spreads = []
    for oi in range(3):
        cx, cy = pts[oi][0]
        dists = sorted(
            (px - cx) ** 2 + (py - cy) ** 2
            for oj in range(3)
            for k, (px, py) in enumerate(pts[oj])
            if not (oi == oj and k == 0)
        )
        spreads.append(
            min(dists[i + 3] - dists[i] for i in range(len(dists) - 3))
        )
    return max(spreads)


def cell_solutions(be, cand: dict) -> list[Solution]:
    m, branch = cand["m"], cand["branch"]
    if branch == "G":
        return g_cell_solutions(be, m, cand["desc"])
    if branch in ("AB", "AC"):
        return halfstep_cell_solutions(be, m, branch, cand["desc"])
    return bc_cell_solutions(be, m, cand["desc"])


def _match_solution(sols: list[Solution], ref: Solution, ball: float):
    for sol in sols:
        dist = (
            abs(float(sol.y) - float(ref.y))
            + abs(float(sol.z) - float(ref.z))
            + abs(float(sol.beta) - float(ref.beta))
            + abs(float(sol.gamma) - float(ref.gamma))
        )
        if dist < ball:
            return sol
    return None


VERDICT_RANK = {"refuted": 0, "boundary": 1, "unresolved": 2, "feasible": 3}


def _classify_solution(cand: dict, sol: Solution, sols240: dict) -> dict:
    """Classify one 60-digit cell solution by the strict-first ladder.

    Margins decide first: configurations outside or on the boundary of the
    open region (strict turns, open offset ranges, positive radii) are
    excluded by strictness regardless of how well the equalities hold;
    boundary-grazing margins and multiplicity-degraded equality residuals
    re-derive the whole cell at 240 digits and match this solution there
    (a solution that evaporates at 240 digits was a 60-digit artifact).
    A feasible verdict additionally requires the direct 4-bad
    minimum-spread confirmation.
    """

    be = MPBackend(60)

    def at240() -> Solution | None:
        if "sols" not in sols240:
            sols240["sols"] = cell_solutions(MPBackend(240), cand)
        return _match_solution(sols240["sols"], sol, 1e-10)

    min_margin = min(sol.margins)
    eq_max = max(be.abs(e) for e in sol.equalities)
    used240 = False
    if min_margin < -be.num(MARGIN_BAND):
        return {"verdict": "refuted", "min_margin": float(min_margin)}
    if be.abs(min_margin) <= be.num(MARGIN_BAND):
        sol240 = at240()
        if sol240 is None:
            return {"verdict": "refuted", "reason": "60-digit margin artifact"}
        used240 = True
        min_margin = min(sol240.margins)
        if min_margin < -MPBackend(240).num("1e-100"):
            return {"verdict": "refuted", "min_margin": float(min_margin)}
        if abs(min_margin) < MPBackend(240).num("1e-100"):
            return {"verdict": "boundary", "margin": float(min_margin)}
        sol = sol240
        eq_max = max(abs(e) for e in sol.equalities)
    accept = MPBackend(240).num("1e-100") if used240 else be.num(EQ_ACCEPT)
    if eq_max < accept:
        pass
    elif not used240 and eq_max > be.num(EQ_REJECT):
        return {"verdict": "refuted", "equality_residual": float(eq_max)}
    else:
        if not used240:
            sol240 = at240()
            if sol240 is None:
                return {
                    "verdict": "refuted",
                    "reason": "60-digit equality artifact",
                }
            min_margin = min(sol240.margins)
            if min_margin < 0:
                return {"verdict": "refuted", "min_margin": float(min_margin)}
            sol = sol240
            eq_max = max(abs(e) for e in sol.equalities)
        if eq_max > MPBackend(240).num("1e-100"):
            return {"verdict": "refuted", "equality_residual": float(eq_max)}
    mp_conf = MPBackend(60)
    spread = brute_force_min_spread(
        mp_conf, cand["m"], sol.y, sol.z, sol.beta, sol.gamma
    )
    if spread > mp_conf.num("1e-40"):
        return {
            "verdict": "unresolved",
            "equality_residual": float(eq_max),
            "direct_4bad_spread": float(spread),
            "reason": "equalities accepted but direct 4-bad spread is nonzero",
        }
    return {
        "verdict": "feasible",
        "equality_residual": float(eq_max),
        "min_margin": float(min_margin),
        "direct_4bad_spread": float(spread),
        "point": [float(sol.y), float(sol.z), float(sol.beta), float(sol.gamma)],
    }


def escalate(cand: dict) -> dict:
    """Classify a candidate by re-deriving its whole cell at 60 digits.

    Every solution of the cell is classified (not only the one nearest the
    float point), and the worst-case verdict is returned, so no true
    solution sharing a cell with a spurious one can be shadowed.
    """

    be = MPBackend(60)
    try:
        sols = cell_solutions(be, cand)
        if not sols:
            return {
                "verdict": "refuted",
                "reason": "cell empty at high precision",
            }
        sols240: dict = {}
        results = [_classify_solution(cand, sol, sols240) for sol in sols]
    except EscalationInconclusive as exc:
        return {"verdict": "unresolved", "reason": str(exc)}
    return max(results, key=lambda r: VERDICT_RANK[r["verdict"]])


# ---------------------------------------------------------------------------
# Random-configuration audit of the atom catalogue
# ---------------------------------------------------------------------------


def self_audit(m: int, samples: int, rng: np.random.Generator) -> dict:
    """Verify on random configurations that every equidistance class of size
    >= 2 from each representative center is a catalogued atom: an own pair
    {k, m-k}, or on the half-step slice a cross pair of the pinned orbit
    pair (with its pole merging allowed for odd m)."""

    h = math.pi / m
    checked = 0
    for branch in ("G", "AB", "AC", "BC"):
        for _ in range(samples):
            y, z = rng.uniform(0.75, 1.3, 2)
            if branch == "G":
                beta, gamma = np.sort(rng.uniform(0.05 * h, 1.95 * h, 2))
                if (
                    min(
                        abs(beta - h),
                        abs(gamma - h),
                        abs(gamma - beta - h),
                        abs(gamma - beta),
                    )
                    < 0.02 * h
                ):
                    continue
            elif branch == "AB":
                beta, gamma = h, rng.uniform(1.05 * h, 1.95 * h)
            elif branch == "AC":
                beta, gamma = rng.uniform(0.05 * h, 0.95 * h), h
            else:
                beta = rng.uniform(0.05 * h, 0.95 * h)
                gamma = beta + h
            _audit_one(m, float(y), float(z), float(beta), float(gamma), branch)
            checked += 1
    return {"m": m, "configs_checked": checked}


def _audit_one(m, y, z, beta, gamma, branch):
    h = math.pi / m
    ang = 2.0 * h * np.arange(m)
    pts = {
        "A": np.stack([np.cos(ang), np.sin(ang)], 1),
        "B": y * np.stack([np.cos(beta + ang), np.sin(beta + ang)], 1),
        "C": z * np.stack([np.cos(gamma + ang), np.sin(gamma + ang)], 1),
    }
    pinned = {"G": None, "AB": ("A", "B"), "AC": ("A", "C"), "BC": ("B", "C")}[branch]
    for orb in "ABC":
        center = pts[orb][0]
        items = sorted(
            (float(((center - pts[name][k]) ** 2).sum()), name, k)
            for name in "ABC"
            for k in range(m)
            if not (name == orb and k == 0)
        )
        groups = [[items[0]]]
        for it in items[1:]:
            if it[0] - groups[-1][-1][0] < 1e-9:
                groups[-1].append(it)
            else:
                groups.append([it])
        for g in groups:
            if len(g) == 1:
                continue
            names = {it[1] for it in g}
            if len(g) != 2:
                raise AssertionError(
                    f"unexpected class size {len(g)}: m={m} branch={branch} {g}"
                )
            if names == {orb}:
                ks = sorted(it[2] for it in g)
                if (ks[0] + ks[1]) % m != 0:
                    raise AssertionError(f"bad own pair {g} at m={m}")
            else:
                if pinned is None or orb not in pinned:
                    raise AssertionError(
                        f"unexpected cross class: m={m} branch={branch} "
                        f"center={orb} {g}"
                    )
                partner = pinned[0] if pinned[1] == orb else pinned[1]
                if names != {partner}:
                    raise AssertionError(
                        f"cross class with wrong orbit: m={m} branch={branch} "
                        f"center={orb} {g}"
                    )


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def check_m(m: int, audit_samples: int, rng: np.random.Generator) -> dict:
    sys_g, c_g, quarter_cells = screen_generic(m)
    sys_ab, c_ab = screen_halfstep(m, "AB")
    sys_ac, c_ac = screen_halfstep(m, "AC")
    sys_bc, c_bc = screen_bc(m)
    cands = c_g + c_ab + c_ac + c_bc
    audit = self_audit(m, audit_samples, rng) if audit_samples else None
    feasible, unresolved, boundary, refuted = [], [], 0, 0
    for cand in cands:
        rec = escalate(cand)
        if rec["verdict"] == "feasible":
            feasible.append({**cand, **rec, "point": rec["point"]})
        elif rec["verdict"] == "unresolved":
            unresolved.append({**cand, **rec})
        elif rec["verdict"] == "boundary":
            boundary += 1
        else:
            refuted += 1
    return {
        "m": m,
        "systems_screened": {"G": sys_g, "AB": sys_ab, "AC": sys_ac, "BC": sys_bc},
        "open_quarter_cells": quarter_cells,
        "screen_candidates": len(cands),
        "refuted": refuted,
        "boundary_exclusions": boundary,
        "unresolved": unresolved,
        "feasible_survivors": feasible,
        "self_audit": audit,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="three-orbit (t=3) finite-m closure screen"
    )
    parser.add_argument("--min-m", type=int, default=3)
    parser.add_argument("--max-m", type=int, default=12)
    parser.add_argument(
        "--audit-samples",
        type=int,
        default=40,
        help="random configurations per branch for the atom-catalogue audit",
    )
    parser.add_argument(
        "--assert-clear",
        action="store_true",
        help="exit nonzero on any feasible or unresolved survivor",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-artifact", type=str, default="")
    args = parser.parse_args()

    rng = np.random.default_rng(SEED)
    records = [
        check_m(m, args.audit_samples, rng)
        for m in range(args.min_m, args.max_m + 1)
    ]
    bad = [
        r for r in records if r["feasible_survivors"] or r["unresolved"]
    ]
    payload = {
        "schema": "erdos97.three_orbit_window_closure.v1",
        "status": "REVIEW_PENDING_SCREEN_ONLY",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "provenance": {
            "generator": "scripts/check_three_orbit_window_closure.py",
            "command": (
                "python scripts/check_three_orbit_window_closure.py "
                f"--min-m {args.min_m} --max-m {args.max_m} "
                f"--audit-samples {args.audit_samples} --write-artifact "
                "data/certificates/three_orbit_window_closure_m3_16.json"
            ),
        },
        "tool": "scripts/check_three_orbit_window_closure.py",
        "scope": (
            "three concentric regular m-gon orbits (t=3), all radii, all "
            "relative rotations, all selected-witness rows; float64 screen "
            "with 60-digit deterministic re-derivation of candidates and "
            "240-digit boundary rechecks; the m = 0 mod 4 quarter cells "
            "are skipped and recorded as named open sub-cases; not an "
            "all-m lemma, not an exact certificate for screened cells, "
            "not a proof of Erdos Problem #97, and not a counterexample "
            "claim"
        ),
        "min_m": args.min_m,
        "max_m": args.max_m,
        "join_band": JOIN_BAND,
        "eq_accept": EQ_ACCEPT,
        "eq_reject": EQ_REJECT,
        "margin_band": MARGIN_BAND,
        "records": records,
        "total_systems": {
            br: sum(r["systems_screened"][br] for r in records)
            for br in ("G", "AB", "AC", "BC")
        },
        "total_screen_candidates": sum(r["screen_candidates"] for r in records),
        "total_boundary_exclusions": sum(
            r["boundary_exclusions"] for r in records
        ),
        "ms_with_survivors": [r["m"] for r in bad],
        "ms_fully_screened": [
            r["m"]
            for r in records
            if not r["feasible_survivors"]
            and not r["unresolved"]
            and r["open_quarter_cells"] == 0
        ],
        "ms_with_open_quarter_cells": [
            r["m"] for r in records if r["open_quarter_cells"]
        ],
        "clear": not bad,
    }
    if args.write_artifact:
        with open(args.write_artifact, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True)
            fh.write("\n")
    if args.json:
        print(json.dumps(payload, indent=1, sort_keys=True))
    else:
        for r in records:
            print(
                f"m={r['m']}: systems={r['systems_screened']} "
                f"candidates={r['screen_candidates']} refuted={r['refuted']} "
                f"boundary={r['boundary_exclusions']} "
                f"unresolved={len(r['unresolved'])} "
                f"feasible={len(r['feasible_survivors'])} "
                f"open_quarter_cells={r['open_quarter_cells']}"
            )
        print(f"clear={not bad}")
    if args.assert_clear and bad:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
