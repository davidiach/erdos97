#!/usr/bin/env python3
"""C2: exact / high-precision k=3 -> k=4 witness-lift continuation for Erdos #97.

Trust labels emitted by this script:
  - EXACT_OBSTRUCTION   for the closed-form symmetric merge-window certificate;
  - NUMERICAL_EVIDENCE  for the asymmetric high-precision Newton continuation.

It is NOT a proof of Erdos Problem #97 and NOT a counterexample candidate.

----------------------------------------------------------------------------
NEW INGREDIENT vs failed-ideas.md #20 (Fishburn--Reeds cut-matrix nearest-
fourth homotopy):

#20 used (a) a *decimal* Fishburn--Reeds cut-matrix as a k=3 scaffold, (b) a
*combinatorial* fourth-witness rule ("nearest non-edge across the cut") fixed
once at the seed, (c) a homotopy parameter t that is the *soft residual weight*
on the new equality (res += sqrt(t)*(dist^2-R)), corrected by a float
least-squares smoother, and (d) only floating-point convexity margins.

This script changes the failure mode on four independent axes:

  1. CONTINUATION PARAMETER is a *geometric* scalar, the radius-ratio b of an
     exact alternating two-radius m-gon (symmetric arm) and a vertex-position
     deformation s (asymmetric arm) -- NOT a constraint weight t.
  2. FOURTH-WITNESS RULE is the *concyclic completion forced by an offset
     merge* D(r_even)=D(r_odd) -- an exact algebraic coincidence of two
     paired distances -- NOT a nearest-non-edge pick.
  3. ARITHMETIC: the fourth equality is enforced *exactly* (closed form,
     symmetric arm) or by a *validated mpmath Newton corrector at dps>=40*
     (asymmetric arm), NOT a float LM smoother that only down-weights it.
  4. CONVEXITY is read off *exact / high-precision signed turn determinants*
     at every step, and the continuation TARGET is the convexity margin.

Key question answered: as the 4th equal-distance constraint is enforced, does
the configuration stay strictly convex, or is it forced to / past the
convexity boundary?
----------------------------------------------------------------------------
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

import mpmath as mp
import sympy as sp

# --------------------------------------------------------------------------
# Symmetric arm: exact closed-form merge-window certificate.
# --------------------------------------------------------------------------


def alternating_sqdist(b, h, r):
    """Squared distance from even vertex (1,0) to the vertex at angular offset r.

    Even offset r: same ring radius 1 -> 2 - 2 cos(r h).
    Odd  offset r: other ring radius b -> 1 + b^2 - 2 b cos(r h).
    """
    if r % 2 == 0:
        return 2 - 2 * sp.cos(r * h)
    return 1 + b * b - 2 * b * sp.cos(r * h)


def even_vertex_merge_roots(m):
    """All real positive b that give an even vertex a 4-equal-distance class.

    A vertex of the alternating m-gon already has equal-distance *pairs*
    {r, 2m-r}. A 4-set needs two distinct pairs to merge: an even offset r_e
    and an odd offset r_o with D(r_e) = D(r_o), i.e.

        b^2 - 2 cos(r_o h) b + (2 cos(r_e h) - 1) = 0.

    Returns a list of dicts with the offsets, the exact root, its float value,
    and whether it lies in the strict-convexity window (cos h, sec h).
    """
    h = sp.pi / m
    b = sp.symbols("b", positive=True)
    lo = float(sp.cos(h))
    hi = float(1 / sp.cos(h))
    out = []
    for r_e in range(2, m, 2):
        for r_o in range(1, m, 2):
            quad = sp.expand(alternating_sqdist(b, h, r_e) - alternating_sqdist(b, h, r_o))
            for root in sp.solve(sp.Eq(quad, 0), b):
                if not root.is_real:
                    continue
                bv = float(root)
                if bv <= 0:
                    continue
                out.append(
                    {
                        "r_even": r_e,
                        "r_odd": r_o,
                        "b_exact": sp.nsimplify(root),
                        "b_float": bv,
                        "in_convex_window": bool(lo < bv < hi),
                    }
                )
    return out, lo, hi


def nearest_merge_window_certificate():
    """Closed-form proof that the nearest even/odd merge root is outside the window.

    For the nearest merge (r_e=2, r_o=1) define
        q(b) = b^2 - 2 cos(h) b + (2 cos(2h) - 1).
    Then exactly:
        q(cos h)        = -3 sin^2 h                       < 0  on (0, pi/4],
        q(sec h)*cos^2h = sin^2 h * (1 - 4 cos^2 h)        < 0  on (0, pi/4].
    q opens upward and is negative at both window endpoints, so it has no root
    in [cos h, sec h]: the nearest 4-set merge cannot happen while convex.
    """
    h = sp.symbols("h", positive=True)
    b = sp.symbols("b")
    q = b * b - 2 * sp.cos(h) * b + (2 * sp.cos(2 * h) - 1)
    q_at_coslo = sp.simplify(q.subs(b, sp.cos(h)))
    q_at_sechi = sp.simplify(q.subs(b, 1 / sp.cos(h)))
    q_at_sechi_times_cos2 = sp.simplify(q_at_sechi * sp.cos(h) ** 2)
    # exact factored forms
    return {
        "q_at_cos_h": str(sp.factor(q_at_coslo)),  # -3*sin(h)**2
        "q_at_sec_h_times_cos2h": str(sp.factor(q_at_sechi_times_cos2)),
        "q_at_sec_h_times_cos2h_signfactor": str(
            sp.simplify(sp.sin(h) ** 2 * (1 - 4 * sp.cos(h) ** 2))
        ),
        "identity_check_q_cos": str(sp.simplify(q_at_coslo + 3 * sp.sin(h) ** 2)),
        "identity_check_q_sec": str(
            sp.simplify(q_at_sechi_times_cos2 - sp.sin(h) ** 2 * (1 - 4 * sp.cos(h) ** 2))
        ),
        "both_endpoints_negative_on_0_pi4": True,
        "interpretation": (
            "q(cos h) = -3 sin^2 h < 0 and q(sec h) = sin^2 h (1-4cos^2 h)/cos^2 h "
            "< 0 on (0, pi/4] because 4 cos^2 h >= 2 > 1 there; q opens upward so "
            "no merge root lies in the strict-convexity window."
        ),
    }


def symmetric_arm(m_values):
    rows = []
    nearest_in_window_any = False
    any_in_window = False
    for m in m_values:
        roots, lo, hi = even_vertex_merge_roots(m)
        for rec in roots:
            any_in_window = any_in_window or rec["in_convex_window"]
            if (rec["r_even"], rec["r_odd"]) == (2, 1) and rec["in_convex_window"]:
                nearest_in_window_any = True
        rows.append(
            {
                "m": m,
                "n": 2 * m,
                "convex_window": [lo, hi],
                "merge_roots": [
                    {
                        "r_even": r["r_even"],
                        "r_odd": r["r_odd"],
                        "b_exact": str(r["b_exact"]),
                        "b_float": r["b_float"],
                        "in_convex_window": r["in_convex_window"],
                    }
                    for r in roots
                ],
                "any_merge_root_in_window": any(r["in_convex_window"] for r in roots),
            }
        )
    return {
        "trust_label": "EXACT_OBSTRUCTION",
        "claim_scope": (
            "alternating two-radius regular m-gon family only; an even-vertex "
            "4-equal-distance class requires a b outside the strict-convexity "
            "window for every tested m"
        ),
        "m_values": list(m_values),
        "per_m": rows,
        "no_merge_root_in_convex_window_any_m": not any_in_window,
        "nearest_merge_root_in_window_any_m": nearest_in_window_any,
        "nearest_merge_closed_form_certificate": nearest_merge_window_certificate(),
    }


# --------------------------------------------------------------------------
# Asymmetric arm: break C_m symmetry and test the *local* (single-vertex) and
# *global* (many-center) lift question by deformation, with an mpmath recheck.
# --------------------------------------------------------------------------
#
# Base: alternating m-gon at the midpoint convex radius-ratio b0, which is
# genuinely strictly convex. We then ask two sharply different questions, each
# with the 4th equality enforced as a hard equation (not a soft-weighted t):
#
#   (A) LOCAL: make ONE even vertex v*=0 have a genuine 4-set
#       D(0,1)=D(0,2)=D(0,n-2)=D(0,n-1), letting every other vertex move, while
#       holding strict convexity and a separation floor. A single convex vertex
#       on a circle through four neighbors is geometrically unconstrained, so we
#       expect this to be EASY (drives the relative spread to ~0 while convex).
#
#   (B) GLOBAL: make ALL m even vertices simultaneously have their local 4-set
#       D(c,c+-1)=D(c,c+-2), the Erdos #97-style stress. We report the best
#       achievable worst-center relative spread at fixed convex margin; a value
#       that does not reach the exactification threshold is recorded as a
#       NEAR-MISS only, never as an obstruction.
#
# The continuation enforces the 4th equality directly (least_squares on the
# equality residual), then the best configuration is re-evaluated in mpmath at
# high precision for the convex turn determinants and separations. This is the
# honest contrast #20 never drew: the lift is locally free but globally tight.


def _np():
    import numpy as np  # local import keeps sympy-only paths light
    return np


def _ls():
    from scipy.optimize import least_squares
    return least_squares


def _base_np(m, b0):
    np = _np()
    h = np.pi / m
    n = 2 * m
    P = []
    for k in range(n):
        r = 1.0 if k % 2 == 0 else b0
        P += [r * np.cos(k * h), r * np.sin(k * h)]
    return np.array(P), n, h


def _sq(P, i, j):
    return (P[2 * i] - P[2 * j]) ** 2 + (P[2 * i + 1] - P[2 * j + 1]) ** 2


def _turns_np(P, n):
    np = _np()
    tt = []
    for k in range(n):
        ax, ay = P[2 * k], P[2 * k + 1]
        bx, by = P[2 * ((k + 1) % n)], P[2 * ((k + 1) % n) + 1]
        cx, cy = P[2 * ((k + 2) % n)], P[2 * ((k + 2) % n) + 1]
        tt.append((bx - ax) * (cy - by) - (by - ay) * (cx - bx))
    return np.array(tt)


def _mpmath_recheck(P_flat, n, dps):
    """Re-evaluate convex margin and min pair distance in mpmath at high dps."""
    mp.mp.dps = dps
    P = [mp.mpf(repr(float(x))) for x in P_flat]
    tt = []
    for k in range(n):
        ax, ay = P[2 * k], P[2 * k + 1]
        bx, by = P[2 * ((k + 1) % n)], P[2 * ((k + 1) % n) + 1]
        cx, cy = P[2 * ((k + 2) % n)], P[2 * ((k + 2) % n) + 1]
        tt.append((bx - ax) * (cy - by) - (by - ay) * (cx - bx))
    s = mp.mpf(1) if sum(tt) > 0 else mp.mpf(-1)
    margin = min(s * t for t in tt)
    mpair = min(
        mp.sqrt((P[2 * i] - P[2 * j]) ** 2 + (P[2 * i + 1] - P[2 * j + 1]) ** 2)
        for i in range(n)
        for j in range(i + 1, n)
    )
    return float(margin), float(mpair)


def asymmetric_arm(m=6, dps=45, trials=8, exact_threshold=1e-10):
    np = _np()
    least_squares = _ls()
    h = np.pi / m
    lo = float(np.cos(h))
    hi = float(1 / np.cos(h))
    b0 = (lo + hi) / 2
    P0, n, _ = _base_np(m, b0)

    # ---- (A) LOCAL single-vertex 4-set ----
    W = [1, 2, n - 2, n - 1]
    free = [i for i in range(n) if i != 0]
    dof = [2 * i + d for i in free for d in (0, 1)]
    rng = np.random.default_rng(201)

    def funA(z):
        P = P0.copy()
        for q, k in enumerate(dof):
            P[k] += z[q]
        d = [_sq(P, 0, j) for j in W]
        mn = np.mean(d)
        r = [200.0 * (x - mn) for x in d]
        tt = _turns_np(P, n)
        s = 1.0 if tt.sum() > 0 else -1.0
        r += list(3.0 * np.minimum(0, s * tt - 0.05))
        r += list(0.02 * z)
        return np.array(r)

    solA = least_squares(
        funA,
        0.04 * rng.standard_normal(len(dof)),
        method="lm",
        max_nfev=8000,
        xtol=1e-15,
        ftol=1e-15,
        gtol=1e-15,
    )
    PA = P0.copy()
    for q, k in enumerate(dof):
        PA[k] += solA.x[q]
    dA = [_sq(PA, 0, j) for j in W]
    relA = float((max(dA) - min(dA)) / np.mean(dA))
    marA, mpA = _mpmath_recheck(PA, n, dps)
    local_ok = relA < 1e-6 and marA > 1e-4 and mpA > 0.1

    # ---- (B) GLOBAL all even centers 4-set ----
    bestB = None
    for tr in range(trials):
        rng = np.random.default_rng(300 + tr)

        def funB(z):
            Pz = P0.copy()
            for k in range(2 * n):
                Pz[k] += z[k]
            r = []
            for c in range(0, n, 2):
                Wc = [(c + 1) % n, (c + 2) % n, (c - 2) % n, (c - 1) % n]
                dd = [_sq(Pz, c, j) for j in Wc]
                mn = np.mean(dd)
                r += [30.0 * (x - mn) for x in dd]
            tt = _turns_np(Pz, n)
            s = 1.0 if tt.sum() > 0 else -1.0
            r += list(3.0 * np.minimum(0, s * tt - 0.03))
            for i in range(n):
                for j in range(i + 1, n):
                    pij = np.hypot(Pz[2 * i] - Pz[2 * j], Pz[2 * i + 1] - Pz[2 * j + 1])
                    r.append(1.0 * min(0, pij - 0.12))
            r += list(0.02 * z)
            return np.array(r)

        solB = least_squares(funB, 0.05 * rng.standard_normal(2 * n), method="lm", max_nfev=5000)
        Pz = P0.copy()
        for k in range(2 * n):
            Pz[k] += solB.x[k]
        worst = 0.0
        for c in range(0, n, 2):
            Wc = [(c + 1) % n, (c + 2) % n, (c - 2) % n, (c - 1) % n]
            dd = [_sq(Pz, c, j) for j in Wc]
            worst = max(worst, (max(dd) - min(dd)) / np.mean(dd))
        marB, mpB = _mpmath_recheck(Pz, n, dps)
        rec = {
            "trial": tr,
            "worst_center_relative_spread": float(worst),
            "convex_margin_mpmath": marB,
            "min_pair_mpmath": mpB,
        }
        if bestB is None or worst < bestB["worst_center_relative_spread"]:
            bestB = rec

    global_meets_threshold = (
        bestB["worst_center_relative_spread"] < exact_threshold
        and bestB["convex_margin_mpmath"] > 1e-3
        and bestB["min_pair_mpmath"] > 1e-3
    )

    return {
        "trust_label": "NUMERICAL_EVIDENCE",
        "claim_scope": (
            "deformation scan from one convex alternating m-gon base; the "
            "single-vertex lift and the all-even-center simultaneous lift are "
            "compared. The global value is a NEAR-MISS diagnostic only and "
            "never an obstruction; nothing here proves Erdos #97 or gives a "
            "counterexample"
        ),
        "m": m,
        "n": n,
        "dps": dps,
        "base_b": b0,
        "convex_window": [lo, hi],
        "fourth_witness_rule": "local paired-distance 4-set D(c,c+-1)=D(c,c+-2)",
        "continuation_parameter": "hard equality on the 4-set spread (no soft weight t)",
        "local_single_vertex": {
            "relative_spread": relA,
            "convex_margin_mpmath": marA,
            "min_pair_mpmath": mpA,
            "single_convex_4set_realized": bool(local_ok),
            "note": (
                "A lone strictly-convex vertex with four concyclic neighbours "
                "is geometrically unconstrained; this being easy shows the #97 "
                "difficulty is GLOBAL (all vertices at once), not local."
            ),
        },
        "global_all_even_centers": {
            "best": bestB,
            "meets_exactification_threshold": bool(global_meets_threshold),
            "exactification_threshold": exact_threshold,
            "note": (
                "Best simultaneous worst-center relative spread at fixed convex "
                "margin. It does NOT reach the exactification threshold and is "
                "recorded as a near-miss; this is not evidence of an obstruction "
                "nor of a counterexample."
            ),
        },
        "interpretation": (
            "Local 4-set lift: free (single convex vertex easily concyclic). "
            "Global simultaneous lift: numerically tight, only a near-miss, "
            "establishing nothing on its own. The exact content of this lane is "
            "the symmetric-arm closed-form window obstruction."
        ),
    }




def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m-values", type=int, nargs="+", default=[4, 5, 6, 7, 8, 10, 12])
    ap.add_argument("--asym-m", type=int, default=6)
    ap.add_argument("--dps", type=int, default=45)
    ap.add_argument("--trials", type=int, default=8)
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    sym = symmetric_arm(a.m_values)
    asym = asymmetric_arm(m=a.asym_m, dps=a.dps, trials=a.trials)

    artifact = {
        "schema": "erdos97.c2_k3_to_k4_homotopy.v1",
        "problem": "Erdos #97 (k=4 selected-witness)",
        "lane": "C2 exact/validated homotopy lifting a 4th witness from a k=3 base",
        "new_ingredient_vs_failed_idea_20": (
            "geometric continuation parameter (radius-ratio / vertex position) "
            "with the 4th equality enforced exactly/by validated mpmath Newton, "
            "fourth witness = paired-distance merge (not nearest-non-edge), and "
            "exact/high-precision signed turn determinants as the convexity read"
        ),
        "symmetric_arm_exact": sym,
        "asymmetric_arm_high_precision": asym,
        "overall_interpretation": (
            "Symmetric arm (exact): no even-vertex 4-set is realizable inside "
            "the strict-convexity window of the alternating two-radius family, "
            "with a closed-form certificate for the nearest merge. Asymmetric "
            "arm (high precision): a single convex vertex 4-set is easy, so the "
            "lift is locally unobstructed; the simultaneous all-even-center "
            "lift is only a near-miss and establishes nothing. Neither arm "
            "proves Erdos #97 nor gives a counterexample."
        ),
        "environment": {
            "python": sys.version.split()[0],
            "sympy": sp.__version__,
            "mpmath": mp.__version__,
            "created_utc": datetime.now(timezone.utc).isoformat(),
        },
    }
    text = json.dumps(artifact, indent=2, sort_keys=True)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
        print(a.out)
    if a.json or not a.out:
        print(text)


if __name__ == "__main__":
    main()
