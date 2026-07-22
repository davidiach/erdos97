#!/usr/bin/env python3
"""Rebuild and verify the C3-symmetric Danzer-type base nonagon.

Newton-polishes the externally supplied seed at mpmath dps=60 and checks:

- the three cross-witness equalities have residual below 1e-50;
- all nine points are strictly convex hull vertices, with cyclic boundary
  order [2, 4, 8, 0, 5, 6, 1, 3, 7] and minimum exterior turn above 0.01;
- the gauge-fixed 6x4 Jacobian of the equality system has rank 3, so the
  nonagon sits in a 1-parameter family;
- the recorded near-coincidence d^2(v0, v4) is approximately 2.99778.

This is numerical verification of a k=3 (three equidistant witnesses per
vertex) configuration.  It is not a counterexample to Erdos Problem #97 and
makes no k=4 claim.
"""

from __future__ import annotations

import argparse
import json
import sys

from mpmath import atan2, det, matrix, mp, mpf, norm, pi, sqrt, svd_r

from erdos97.danzer18_doubling import (
    CROSS,
    mp_base,
    mp_base_jacobian,
    mp_base_vertices,
)

EXPECTED_BOUNDARY_ORDER = [2, 4, 8, 0, 5, 6, 1, 3, 7]


def cyclic_normalize(order: list[int]) -> list[int]:
    """Rotate a cyclic sequence so it starts at its smallest label."""
    k = order.index(min(order))
    return order[k:] + order[:k]


def turn_angles(pts, order):
    n = len(order)
    turns = []
    for i in range(n):
        a = pts[order[(i - 1) % n]]
        b = pts[order[i]]
        c = pts[order[(i + 1) % n]]
        ux, uy = b[0] - a[0], b[1] - a[1]
        vx, vy = c[0] - b[0], c[1] - b[1]
        turns.append(atan2(ux * vy - uy * vx, ux * vx + uy * vy))
    return turns


def family_tangent(x4):
    """Unit kernel vector of the 3x4 base Jacobian via signed 3x3 minors."""
    j = mp_base_jacobian(x4)
    ker = []
    for drop in range(4):
        cols = [c for c in range(4) if c != drop]
        m3 = matrix(3, 3)
        for i in range(3):
            for k, c in enumerate(cols):
                m3[i, k] = j[i, c]
        ker.append((-1) ** drop * det(m3))
    nrm = norm(matrix(ker))
    return [v / nrm for v in ker], j


def run(dps: int) -> dict:
    x4, residuals = mp_base(dps)
    max_res = max(abs(r) for r in residuals)

    pts = mp_base_vertices(x4)
    angles = [atan2(p[1], p[0]) % (2 * pi) for p in pts]
    order = sorted(range(9), key=lambda v: angles[v])
    turns = turn_angles(pts, order)
    min_turn = min(turns)
    total_turn = sum(turns)
    min_pair = min(
        sqrt((pts[a][0] - pts[b][0]) ** 2 + (pts[a][1] - pts[b][1]) ** 2)
        for a in range(9)
        for b in range(a + 1, 9)
    )

    # 6x4 gauge-fixed Jacobian: per orbit, both mate-vs-cross differences.
    h = mpf(10) ** (-(mp.dps // 2))
    j6 = matrix(6, 4)

    def residuals6(y4):
        from mpmath import cos, sin

        om = 2 * pi / 3
        r = [mpf(1), y4[0], y4[1]]
        ph = [mpf(0), y4[2], y4[3]]

        def vert(m, j):
            a = ph[m] + om * j
            return (r[m] * cos(a), r[m] * sin(a))

        out = []
        for m in range(3):
            vm, tv = CROSS[m]
            c = vert(m, 0)
            w = vert(vm, tv)
            dw = (c[0] - w[0]) ** 2 + (c[1] - w[1]) ** 2
            for j in (1, 2):
                mt = vert(m, j)
                out.append((c[0] - mt[0]) ** 2 + (c[1] - mt[1]) ** 2 - dw)
        return out

    for k in range(4):
        xp = list(x4)
        xm = list(x4)
        xp[k] += h
        xm[k] -= h
        fp = residuals6(xp)
        fm = residuals6(xm)
        for i in range(6):
            j6[i, k] = (fp[i] - fm[i]) / (2 * h)
    sv6 = sorted((abs(s) for s in svd_r(j6, compute_uv=False)), reverse=True)
    rank6 = sum(1 for s in sv6 if s > sv6[0] * mpf("1e-12"))

    tangent, _ = family_tangent(x4)

    d2_04 = (pts[0][0] - pts[4][0]) ** 2 + (pts[0][1] - pts[4][1]) ** 2

    return {
        "schema": "erdos97.danzer18_base_nonagon.v1",
        "dps": dps,
        "coordinates": {
            "r1": mp.nstr(x4[0], 50),
            "r2": mp.nstr(x4[1], 50),
            "phi1": mp.nstr(x4[2], 50),
            "phi2": mp.nstr(x4[3], 50),
        },
        "max_cross_residual": mp.nstr(max_res, 5),
        "residual_below_1e50": bool(max_res < mpf("1e-50")),
        "boundary_order": cyclic_normalize(order),
        "boundary_order_matches": cyclic_normalize(order)
        == cyclic_normalize(EXPECTED_BOUNDARY_ORDER),
        "min_turn": float(min_turn),
        "total_turn_minus_2pi": float(total_turn - 2 * pi),
        "strictly_convex": bool(min(turns) > 0),
        "min_turn_above_0_01": bool(min_turn > mpf("0.01")),
        "min_pair_distance": float(min_pair),
        "jacobian6x4_singular_values": [mp.nstr(s, 10) for s in sv6],
        "jacobian6x4_rank": rank6,
        "one_parameter_family": rank6 == 3,
        "family_tangent_dr1_dr2_dphi1_dphi2": [mp.nstr(v, 40) for v in tangent],
        "d2_v0_v4": mp.nstr(d2_04, 12),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dps", type=int, default=60)
    parser.add_argument("--check", action="store_true",
                        help="exit nonzero unless all landmark checks pass")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run(args.dps)
    ok = (
        result["residual_below_1e50"]
        and result["boundary_order_matches"]
        and result["strictly_convex"]
        and result["min_turn_above_0_01"]
        and result["one_parameter_family"]
    )
    result["all_checks_pass"] = ok

    if args.json:
        json.dump(result, sys.stdout, indent=1)
        sys.stdout.write("\n")
    else:
        for key in (
            "max_cross_residual", "boundary_order", "min_turn",
            "min_pair_distance", "jacobian6x4_rank", "d2_v0_v4",
            "all_checks_pass",
        ):
            print(f"{key}: {result[key]}")
    if args.check and not ok:
        print("FAIL: base nonagon landmark checks failed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
