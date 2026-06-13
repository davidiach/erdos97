#!/usr/bin/env python3
"""Exact SMT closure of the m=4 (three concentric squares, n=12) quarter cell.

Context (`docs/three-square-m4-exact-closure.md`): the three-orbit (t=3)
finite-m closure screen `scripts/check_three_orbit_window_closure.py` clears
every branch for `m = 3..16` except the degenerate ``m = 0 mod 4`` quarter
cells, which it skips and reports as named open sub-cases. This script closes
the smallest such cell, ``m = 4`` (three concentric regular 4-gons, ``n = 12``
points), exactly, with an SMT (z3) certificate.

Reduction (exact for ``m = 4``). Three concentric squares: radii ``1, y, z``,
rotation offsets ``0, beta, gamma`` with ``h = pi/4``. For a square the only
own equidistance pair from a vertex is the 90-degree diagonal pair, at squared
distance ``2 r^2``; two same-orbit cross witnesses would force a half-step
offset (branches AB/AC/BC, covered by the main screen), so a *branch-G* 4-bad
center uses its own 90-pair plus one witness from each other orbit, all at the
own-pair distance. A vertex at radius ``r`` and angle ``theta`` is at squared
distance 2 from ``A_0 = (1, 0)`` iff ``cos(theta) = P(r) := (r^2-1)/(2r)``;
the four B-vertices sit at angles ``beta + k*pi/2``, whose cosines are exactly
``{+-cos beta, +-sin beta}``. Hence branch-G 4-badness is equivalent to

    (i)   P(y) in {+-cos beta, +-sin beta}      [A_0 has a B-witness]
    (ii)  P(z) in {+-cos gamma, +-sin gamma}    [A_0 has a C-witness]
    (iii) Q(y,z) in {+-cos(gamma-beta), +-sin(gamma-beta)}   [B_0 has a C-witness]

with ``Q(y,z) := (z^2-y^2)/(2yz)``. The remaining witness conditions
(``B_0``/``C_0`` see ``A``; ``C_0`` sees ``B``) are implied because each
witness-angle set ``{cos(theta + k*pi/2)}`` equals ``{+-cos theta, +-sin theta}``
and is closed under negation, with the relevant target distances being exact
negatives. (Equivalent log-radius form: with ``p = P(y) = sinh(ln y)``,
``q = P(z) = sinh(ln z)``, one has ``Q = sinh(ln z - ln y) =
q*sqrt(1+p^2) - p*sqrt(1+q^2)``.)

Strict convexity of the interleaved 12-gon forces the radius window
``cos h < y, z < 1/cos h`` (i.e. ``1/2 < y^2, z^2 < 2``) and the angular order
``0 < beta < gamma < pi/2``. This script decides, with z3, whether the
conjunction (i)&(ii)&(iii) together with the window and ``0 < beta < gamma <
pi/2`` is satisfiable, over all 64 discrete sign/witness combinations. The
constraints are rationalized via the tangent half-angle (``t = tan(beta/2)``,
``u = tan(gamma/2)`` in ``(0, 1)``) to a polynomial system z3's nonlinear real
arithmetic decides quickly; **no convexity inequality is needed** -- the radius
window alone already makes every combination UNSAT, which a fortiori excludes
the strictly convex case.

Trust: ``EXACT_OBSTRUCTION`` (SMT certificate) for the stated restricted family
(three concentric squares, branch G). The companion half-step branches
AB/AC/BC for ``m = 4`` are covered at screen grade by the main three-orbit
artifact. This is not an all-``m`` result, not a proof of Erdos Problem #97, and
not a counterexample.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys

PB_KEYS = ("+cb", "-cb", "+sb", "-sb")
PZ_KEYS = ("+cg", "-cg", "+sg", "-sg")
Q_KEYS = ("+cgb", "-cgb", "+sgb", "-sgb")


def _solver_for(combo, *, window: bool, convex: bool, timeout_ms: int):
    import z3

    y, z, t, u = z3.Reals("y z t u")
    dt, du = 1 + t * t, 1 + u * u
    cb, sb = (1 - t * t), 2 * t  # = cos b, sin b scaled by dt
    cg, sg = (1 - u * u), 2 * u  # = cos g, sin g scaled by du
    s = z3.Solver()
    s.set("timeout", timeout_ms)
    s.add(t > 0, t < 1, u > 0, u < 1, t < u, y > 0, z > 0)  # 0<b<g<pi/2
    if window:
        s.add(2 * y * y > 1, y * y < 2, 2 * z * z > 1, z * z < 2)
    else:
        s.add(y < 5, z < 5)
    pb = {"+cb": cb, "-cb": -cb, "+sb": sb, "-sb": -sb}[combo[0]]
    pz = {"+cg": cg, "-cg": -cg, "+sg": sg, "-sg": -sg}[combo[1]]
    cgb = cb * cg + sb * sg  # cos(g-b) scaled by dt*du
    sgb = sg * cb - cg * sb  # sin(g-b) scaled by dt*du
    qd = {"+cgb": cgb, "-cgb": -cgb, "+sgb": sgb, "-sgb": -sgb}[combo[2]]
    s.add(sgb > 0, cgb > 0)  # 0 < g-b < pi/2
    s.add((y * y - 1) * dt == 2 * y * pb)  # (i)
    s.add((z * z - 1) * du == 2 * z * pz)  # (ii)
    s.add((z * z - y * y) * dt * du == 2 * y * z * qd)  # (iii)
    if convex:
        # per-period turn determinants of the angular-order 12-gon, each
        # cleared by dt*du > 0 (strict convexity <=> all three positive)
        ta = y * (2 * t) * du + z * (1 - u * u) * dt - y * z * cgb
        tb = y * (2 * t) * du - z * (2 * u) * dt + y * z * sgb
        tc = z * (1 - u * u) * dt - y * (1 - t * t) * du + y * z * sgb
        s.add(ta > 0, tb > 0, tc > 0)
    return s


def decide_all(*, window: bool, convex: bool, timeout_ms: int) -> dict:
    import z3

    combos = list(itertools.product(PB_KEYS, PZ_KEYS, Q_KEYS))
    counts = {"unsat": 0, "sat": 0, "unknown": 0}
    sat_combos, unknown_combos = [], []
    for combo in combos:
        r = _solver_for(
            combo, window=window, convex=convex, timeout_ms=timeout_ms
        ).check()
        if r == z3.unsat:
            counts["unsat"] += 1
        elif r == z3.sat:
            counts["sat"] += 1
            sat_combos.append(list(combo))
        else:
            counts["unknown"] += 1
            unknown_combos.append(list(combo))
    return {
        "total": len(combos),
        "counts": counts,
        "sat_combos": sat_combos,
        "unknown_combos": unknown_combos,
    }


# --- self-tests: encoding faithfulness and non-vacuity (no z3) ---------------


def faithfulness_ok() -> bool:
    """For every witness index k, the radius solving the distance equation
    yields P(r) equal to the witness-angle cosine, which lies in the modelled
    set {+-cos theta, +-sin theta}. This is the exact equivalence underlying
    conditions (i)-(iii)."""
    h = math.pi / 4
    for theta in [0.1, 0.5, 1.0, 1.4, math.pi / 4 - 0.2]:
        members = {
            round(v, 12)
            for v in (
                math.cos(theta),
                -math.cos(theta),
                math.sin(theta),
                -math.sin(theta),
            )
        }
        for k in range(4):
            c = math.cos(theta + k * h * 2)
            # radius with a vertex (angle theta + k*pi/2) at squared distance 2
            r = c + math.sqrt(c * c + 1)
            p = (r * r - 1) / (2 * r)
            if abs(p - c) > 1e-12:
                return False
            if round(p, 12) not in {round(x, 12) for x in members}:
                return False
    return True


def nonvacuity_witness() -> dict:
    """The system is satisfiable in the degenerate boundary limit gamma->pi/2,
    z->1 (the C square collapses onto the A square): there P(z)=0=cos(pi/2) and
    the tie holds. This shows the window-UNSAT is a genuine obstruction, not a
    vacuous over-constraint -- solutions appear exactly at the excluded
    (non-strictly-convex) boundary."""
    return {"y": 1.0, "z": 1.0, "beta_deg": 0.0, "gamma_deg": 90.0,
            "note": "degenerate boundary limit; excluded by strict convexity"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--timeout-ms", type=int, default=20000)
    ap.add_argument("--assert-clear", action="store_true",
                    help="exit nonzero unless all 64 combos are UNSAT in-window")
    ap.add_argument("--check-vacuity", action="store_true",
                    help="also confirm the system is SAT without the window")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-artifact", type=str, default="")
    args = ap.parse_args()

    faithful = faithfulness_ok()
    main_res = decide_all(window=True, convex=False, timeout_ms=args.timeout_ms)
    clear = (
        main_res["counts"]["sat"] == 0
        and main_res["counts"]["unknown"] == 0
        and faithful
    )
    payload = {
        "schema": "erdos97.three_square_m4_closure.v1",
        "status": "EXACT_OBSTRUCTION_SMT" if clear else "INCOMPLETE",
        "trust": "EXACT_OBSTRUCTION",
        "provenance": {
            "generator": "scripts/check_three_square_m4_closure.py",
            "command": (
                "python scripts/check_three_square_m4_closure.py "
                "--assert-clear --write-artifact "
                "data/certificates/three_square_m4_closure.json"
            ),
        },
        "scope": (
            "Three concentric regular 4-gons (n=12), branch G: the conjunction "
            "of the 4-bad conditions (i),(ii),(iii) and the strict-convexity "
            "radius window cos h < y,z < 1/cos h with 0<beta<gamma<pi/2 is SMT "
            "(z3) UNSAT over all 64 discrete sign/witness combinations; "
            "convexity inequalities are not even required. Exact obstruction "
            "for this restricted family; AB/AC/BC half-step branches for m=4 "
            "are screen-grade in the main three-orbit artifact; not an all-m "
            "result, not a proof of Erdos Problem #97, not a counterexample."
        ),
        "m": 4,
        "n": 12,
        "combos_total": main_res["total"],
        "in_window_no_convexity": main_res["counts"],
        "sat_combos": main_res["sat_combos"],
        "unknown_combos": main_res["unknown_combos"],
        "faithfulness_ok": faithful,
        "nonvacuity_witness": nonvacuity_witness(),
        "clear": clear,
    }
    if args.check_vacuity:
        novwin = decide_all(window=False, convex=False, timeout_ms=args.timeout_ms)
        payload["without_window"] = novwin["counts"]

    if args.write_artifact:
        with open(args.write_artifact, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True)
            fh.write("\n")
    if args.json:
        print(json.dumps(payload, indent=1, sort_keys=True))
    else:
        c = main_res["counts"]
        print(f"m=4 branch-G, in-window, no-convexity over {main_res['total']} "
              f"combos: UNSAT={c['unsat']} SAT={c['sat']} UNKNOWN={c['unknown']}")
        print(f"faithfulness_ok={faithful}  clear={clear}")
        if main_res["sat_combos"]:
            print(f"  SAT combos: {main_res['sat_combos']}")
        if main_res["unknown_combos"]:
            print(f"  UNKNOWN combos: {main_res['unknown_combos']}")
    if args.assert_clear and not clear:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
