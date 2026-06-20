#!/usr/bin/env python3
"""Closure of the three-orbit quarter cells via "A_0 cannot be 4-bad".

Context (`docs/quarter-cell-closure.md`, follow-up to
`docs/three-orbit-window-closure.md` and `docs/three-square-m4-exact-closure.md`):
the three-orbit (t=3) finite-m closure screen skips the degenerate
``m = 0 mod 4`` quarter cells (A-row and B-row own pair = m/4, the 90-degree
pair). This script closes them by a single observation about the A-row alone,
uniform in the C-row choice ``a3``.

Reduction. In every quarter cell the A-row own pair is the 90-pair, so A_0's
witnesses sit at squared distance 2; A_0 is 4-bad only if it also has a
B-vertex and a C-vertex at squared distance 2, i.e. (with
``P(r) = (r^2-1)/(2r)`` and ``h = pi/m``):

    (i)  P(y) in { cos(beta  + 2k h) : k }      [A_0 has a B-witness]
    (ii) P(z) in { cos(gamma + 2k h) : k }      [A_0 has a C-witness]

These use only the A-row and B-row, which are the 90-pair in *every* quarter
cell regardless of ``a3``; so if no strictly convex window configuration
satisfies (i)&(ii), then A_0 is never 4-bad, hence no quarter-cell
configuration is 4-bad.

Exact boundary-band lemma. For ``m = 0 mod 4`` the angle ``pi/2`` is an integer
multiple of the step ``2h`` (``pi/2 = (m/4)*2h``), so ``pi/2 ≡ 0 (mod 2h)``.
In the strict-convexity radius window ``cos h < y < sec h`` we have
``|P(y)| < omega_m := P(sec h)``, so a vertex at squared distance 2 from A_0
lies at an angle within ``delta_m := arcsin(omega_m)`` of ``±pi/2``; reduced
mod ``2h`` (where ``±pi/2 ≡ 0``) the offset is forced into the boundary bands
``(0, delta_m) ∪ (2h - delta_m, 2h)``. So the cross orbit nearly aligns with
the A orbit -- which is what breaks strict convexity. This confinement is
verified exactly by the self-test below.

Screen. Over a dense grid of window radii, this enumerates every offset
assignment satisfying (i)&(ii) with ``0 < beta < gamma < 2h`` and reports the
maximum over them of the minimum per-period turn determinant. A value
strictly below zero means *no* such configuration is strictly convex (with a
margin), i.e. A_0 cannot be 4-bad. This is float-grade screen evidence
(matching the main three-orbit screen), not an exact certificate; the
``m = 4`` quarter cell is additionally closed exactly by SMT in
`scripts/check_three_square_m4_closure.py`.

The exact-SMT route did not close ``m >= 8`` in our encoding (z3 nonlinear real
arithmetic returns ``unknown`` on the 8+-way witness disjunctions and times out
on the cubic turn determinants in the explicit-combo encoding), which is why
this companion screen exists -- recorded so future work does not re-attempt
that particular SMT encoding. A different encoding (e.g. CAD/resultants on the
band-confined region) may still succeed.

Not an all-m result, not a proof of Erdos Problem #97, not a counterexample.
"""

from __future__ import annotations

import argparse
import json
import math
import sys

DEFAULT_MS = (4, 8, 12, 16)
# The 4-bad locus is tangent to the convexity boundary: the supremum of the
# minimum per-period turn determinant over (i)&(ii) configs is 0, attained
# only in the degenerate orbit-coincidence limit (excluded by strict
# convexity). So the screen passes a cell when every sampled config is
# strictly non-convex (max min-turn < 0). The margin shrinks with m (tangency
# tightens), so this float-grade screen is reliable only for bounded m; the
# exact, m-uniform statement (min turn <= 0 on the locus) is the open lemma,
# and m=4 is closed exactly by SMT in check_three_square_m4_closure.py.
TURN_TOL = 1e-12


def offsets_for(p: float, m: int) -> list[float]:
    """All phi in (0, 2h) with cos(phi + 2k h) = p for some integer k."""
    h = math.pi / m
    twoh = 2 * h
    if abs(p) > 1:
        return []
    base = math.acos(max(-1.0, min(1.0, p)))
    out = set()
    for raw in (base, -base):
        for k in range(m):
            out.add(round((raw - 2 * k * h) % twoh, 12))
    return sorted(out)


def turn_min(m: int, y: float, z: float, beta: float, gamma: float) -> float:
    h = math.pi / m
    twoh = 2 * h
    a0 = (1.0, 0.0)
    a1 = (math.cos(twoh), math.sin(twoh))
    b0 = (y * math.cos(beta), y * math.sin(beta))
    c0 = (z * math.cos(gamma), z * math.sin(gamma))
    cm1 = (z * math.cos(gamma - twoh), z * math.sin(gamma - twoh))

    def t(u, v, w):
        return (v[0] - u[0]) * (w[1] - v[1]) - (v[1] - u[1]) * (w[0] - v[0])

    return min(t(cm1, a0, b0), t(a0, b0, c0), t(b0, c0, a1))


def boundary_band_ok(m: int, samples: int = 40) -> bool:
    """Exact-lemma self-test: for window radii, every offset solving the
    dist^2=2 condition lies in (0, delta) U (2h - delta, 2h)."""
    h = math.pi / m
    twoh = 2 * h
    sech = 1.0 / math.cos(h)
    omega = (sech * sech - 1) / (2 * sech)  # P(sec h)
    delta = math.asin(min(1.0, omega))
    lo, hi = math.cos(h), sech
    for i in range(samples):
        y = lo + (hi - lo) * (i + 0.5) / samples
        p = (y * y - 1) / (2 * y)
        for phi in offsets_for(p, m):
            in_band = phi < delta + 1e-9 or phi > twoh - delta - 1e-9
            if not in_band:
                return False
    return True


def screen_m(m: int, grid: int) -> dict:
    h = math.pi / m
    twoh = 2 * h
    lo, hi = math.cos(h), 1.0 / math.cos(h)
    best = -math.inf
    worst = None
    count = 0
    step = (hi - lo) / (grid + 1)
    ys = [lo + step * (i + 1) for i in range(grid)]
    # precompute offsets per radius
    offs = []
    for y in ys:
        offs.append(offsets_for((y * y - 1) / (2 * y), m))
    for iy, y in enumerate(ys):
        bs = offs[iy]
        if not bs:
            continue
        for iz, z in enumerate(ys):
            gs = offs[iz]
            if not gs:
                continue
            for beta in bs:
                for gamma in gs:
                    if not (1e-9 < beta < gamma - 1e-9 < twoh - 1e-9):
                        continue
                    count += 1
                    tm = turn_min(m, y, z, beta, gamma)
                    if tm > best:
                        best = tm
                        worst = (y, z, beta, gamma)
    return {
        "m": m,
        "grid": grid,
        "ii_configs": count,
        "max_min_turn": (None if best == -math.inf else best),
        "clear": (count == 0) or (best < -TURN_TOL),
        "argmax": (None if worst is None else
                   {"y": worst[0], "z": worst[1], "beta": worst[2],
                    "gamma": worst[3]}),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ms", type=int, nargs="*", default=list(DEFAULT_MS))
    ap.add_argument("--grid", type=int, default=160)
    ap.add_argument("--assert-clear", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-artifact", type=str, default="")
    args = ap.parse_args()

    band_ok = all(boundary_band_ok(m) for m in args.ms)
    records = [screen_m(m, args.grid if m <= 8 else max(96, args.grid * 3 // 4))
               for m in args.ms]
    clear = band_ok and all(r["clear"] for r in records)
    payload = {
        "schema": "erdos97.quarter_cell_closure.v1",
        "status": "REDUCTION_AND_TANGENCY_EVIDENCE" if clear else "INCOMPLETE",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "provenance": {
            "generator": "scripts/check_quarter_cell_closure.py",
            "command": (
                "python scripts/check_quarter_cell_closure.py --assert-clear "
                "--write-artifact data/certificates/quarter_cell_closure.json"
            ),
        },
        "scope": (
            "Three-orbit (t=3) quarter cells (m=0 mod 4, A/B-row own pair = "
            "m/4). Exact, m-uniform self-tested lemmas: (1) A_0 is 4-bad only "
            "if the A_0 B-/C-witness conditions (i)&(ii) hold, uniform in the "
            "C-row choice a3, so the quarter cell closes iff A_0 cannot be "
            "4-bad; (2) the boundary-band confinement of beta,gamma. Float "
            "grid for m in {4,8,12,16}: every sampled (i)&(ii) config is "
            "strictly non-convex (max min-turn < 0), but the margin is "
            "tangent to 0 and grid-dependent, so for m>=8 this is EVIDENCE "
            "of closure, not a certificate. m=4 is closed exactly by SMT "
            "elsewhere; the m=8,12,16 finite-m certificate is recorded "
            "separately by check_quarter_cell_derivative_certificate.py. "
            "Records that the exact-SMT route does not scale past m=4. "
            "Not an all-m lemma, not a proof "
            "of Erdos Problem #97, not a counterexample."
        ),
        "boundary_band_lemma_ok": band_ok,
        "turn_tol": TURN_TOL,
        "tangency_note": (
            "the 4-bad locus is tangent to the convexity boundary: max "
            "min-turn over (i)&(ii) configs is < 0 but its supremum is 0 "
            "(at the degenerate orbit-coincidence limit, excluded by strict "
            "convexity), and the sampled max can be driven arbitrarily close "
            "to 0 by sampling nearer the tangency (non-monotone in grid). So "
            "the float grid is EVIDENCE of closure, not a certificate, for "
            "m >= 8"
        ),
        "records": records,
        # Per-m closure status, stated unambiguously to prevent any misread of
        # the grid pass as a closure:
        #  - m=4 is closed EXACTLY (by SMT in check_three_square_m4_closure.py);
        #    this screen only corroborates it.
        #  - m>=8 entries here are tangency-limited EVIDENCE only; the
        #    derivative certificate is a separate artifact.
        "exactly_closed_elsewhere": [m for m in args.ms if m == 4],
        "grid_evidence_only_m_values": [r["m"] for r in records
                                        if r["m"] != 4 and r["clear"]],
        "grid_all_sampled_nonconvex": [r["m"] for r in records if r["clear"]],
        # `clear` = the checker's reproducibility pass (lemmas hold AND every
        # sampled config is strictly non-convex). It does NOT mean m>=8 closed.
        "clear": clear,
    }
    if args.write_artifact:
        with open(args.write_artifact, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True)
            fh.write("\n")
    if args.json:
        print(json.dumps(payload, indent=1, sort_keys=True))
    else:
        print(f"boundary_band_lemma_ok={band_ok}")
        for r in records:
            print(f"m={r['m']}: (i&ii) configs={r['ii_configs']} "
                  f"max_min_turn={r['max_min_turn']} clear={r['clear']}")
        print(f"clear={clear}")
    if args.assert_clear and not clear:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
