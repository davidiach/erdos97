#!/usr/bin/env python3
"""Scan the Danzer-type nonagon base family for pool-enlarging coincidences.

The doubled-Danzer witness pools would enlarge at a family point where some
additional base vertex v satisfies d^2(center_m, v) = 3 r_m^2 exactly (the
recorded near-coincidence is d^2(v0, v4) = 2.99778 at the base point).  This
scan slides along the 1-parameter collided family (flex-step parameter t,
Newton-reprojected) and records:

- the strict-convexity margin and minimum vertex distance along the family;
- sign changes of all 15 candidate coincidence functions
  d^2(center (m,0), vertex (mv,jv)) - 3 r_m^2 on the scan window;
- the degenerate family endpoint near t ~ 0.3944 where the polished family
  point collapses onto a triply covered equilateral triangle
  (r -> (1,1,1), phi -> (0, 2pi/3, 0)) and every coincidence trivializes.

Outcome at this base family: the scan detects no nondegenerate sign-changing
coincidence root, and the near-coincidence d^2(v0, v4) - 3 is negative at the
eight reported profile samples.  The finite grid can miss tangential roots,
and flex-seeded reprojection is not a certified parameterization of the full
family branch.  This is numerical scan evidence only, not a nonexistence proof
and not a counterexample claim.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from erdos97.danzer18_doubling import CROSS, OMEGA, base_floats

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    REPO_ROOT / "data" / "certificates" /
    "danzer18_family_coincidence_scan.json"
)
SCHEMA = "erdos97.danzer18_family_coincidence_scan.v1"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
GENERATOR_COMMAND = (
    "python scripts/check_danzer18_family_coincidences.py --write-artifact"
)

T_WINDOW = (-0.8, 0.8)
T_SAMPLES = 161
PROFILE_TS = (0.0, 0.1, 0.2, 0.3, 0.35, 0.38, 0.39, 0.394)


def base_params(t):
    from scipy.optimize import least_squares

    from erdos97.danzer18_doubling import BASE_FLEX4 as flex4

    base = base_floats()
    y0 = np.array([
        base["r"][1] + t * flex4[0],
        base["r"][2] + t * flex4[1],
        base["phi"][1] + t * flex4[2],
        base["phi"][2] + t * flex4[3],
    ])

    def res(y):
        r = [1.0, y[0], y[1]]
        ph = [0.0, y[2], y[3]]
        out = []
        for m in range(3):
            vm, tv = CROSS[m]
            dx = (r[vm] * math.cos(ph[vm] + OMEGA * tv)
                  - r[m] * math.cos(ph[m]))
            dy = (r[vm] * math.sin(ph[vm] + OMEGA * tv)
                  - r[m] * math.sin(ph[m]))
            out.append(dx * dx + dy * dy - 3.0 * r[m] ** 2)
        return np.array(out)

    sol = least_squares(res, y0, method="trf", xtol=1e-15, ftol=1e-15,
                        gtol=1e-15)
    r = [1.0, float(sol.x[0]), float(sol.x[1])]
    ph = [0.0, float(sol.x[2]), float(sol.x[3])]
    return r, ph


def vertex(r, ph, m, j):
    a = ph[m] + OMEGA * j
    return (r[m] * math.cos(a), r[m] * math.sin(a))


def coincidence_val(t, m, mv, jv):
    r, ph = base_params(t)
    c = vertex(r, ph, m, 0)
    w = vertex(r, ph, mv, jv)
    return (c[0] - w[0]) ** 2 + (c[1] - w[1]) ** 2 - 3.0 * r[m] ** 2


def convexity_margin(t):
    r, ph = base_params(t)
    pts = [vertex(r, ph, m, j) for m in range(3) for j in range(3)]
    ang = [math.atan2(p[1], p[0]) % (2 * math.pi) for p in pts]
    order = sorted(range(9), key=lambda v: ang[v])
    turns = []
    for i in range(9):
        a = pts[order[(i - 1) % 9]]
        b = pts[order[i]]
        c = pts[order[(i + 1) % 9]]
        ux, uy = b[0] - a[0], b[1] - a[1]
        vx, vy = c[0] - b[0], c[1] - b[1]
        turns.append(math.atan2(ux * vy - uy * vx, ux * vx + uy * vy))
    return min(turns)


def min_pair_distance(t):
    r, ph = base_params(t)
    pts = [vertex(r, ph, m, j) for m in range(3) for j in range(3)]
    return min(
        math.hypot(pts[a][0] - pts[b][0], pts[a][1] - pts[b][1])
        for a in range(9)
        for b in range(a + 1, 9)
    )


def candidates():
    out = []
    for m in range(3):
        vm, tv = CROSS[m]
        excluded = {(m, 0), (m, 1), (m, 2), (vm, tv)}
        for mv in range(3):
            for jv in range(3):
                if (mv, jv) not in excluded:
                    out.append((m, mv, jv))
    return out


def run() -> dict:
    ts = np.linspace(T_WINDOW[0], T_WINDOW[1], T_SAMPLES)

    profile = []
    for t in PROFILE_TS:
        profile.append({
            "t": t,
            "min_pair_distance": min_pair_distance(t),
            "convexity_margin": convexity_margin(t),
            "d2_v0_v4_minus_3": coincidence_val(t, 0, 1, 1),
        })

    roots = []
    for (m, mv, jv) in candidates():
        vals = [coincidence_val(t, m, mv, jv) for t in ts]
        for i in range(len(ts) - 1):
            if vals[i] == 0 or vals[i] * vals[i + 1] < 0:
                t0 = brentq(coincidence_val, ts[i], ts[i + 1],
                            args=(m, mv, jv), xtol=1e-13)
                roots.append({
                    "t": float(t0),
                    "center_orbit": m,
                    "gained_vertex": 3 * mv + jv,
                    "min_pair_distance_at_root": min_pair_distance(t0),
                })

    # the degenerate endpoint: polished family point near t = 0.3944
    r_end, ph_end = base_params(0.3944042146)
    endpoint = {
        "t_approx": 0.3944042146,
        "r": r_end,
        "phi": ph_end,
        "min_pair_distance": min_pair_distance(0.3944042146),
        "is_triple_triangle": bool(
            abs(r_end[1] - 1.0) < 1e-8
            and abs(r_end[2] - 1.0) < 1e-8
            and abs(ph_end[1] - 2 * math.pi / 3) < 1e-8
            and abs(ph_end[2]) < 1e-8
        ),
    }

    all_detected_roots_degenerate = all(
        r["min_pair_distance_at_root"] < 1e-6 for r in roots
    )
    near_coincidence_negative_on_profile = all(
        p["d2_v0_v4_minus_3"] < 0 for p in profile
    )

    return {
        "schema": SCHEMA,
        "status": "NO_NONDEGENERATE_SIGN_CHANGE_ROOT_DETECTED",
        "trust": TRUST,
        "provenance": {"command": GENERATOR_COMMAND},
        "claim_scope": (
            "Float64 sign-change scan of flex-seeded, Newton-reprojected "
            "samples in [-0.8, 0.8] for pool-enlarging distance coincidences "
            "on the Danzer-type nonagon base family. Every detected "
            "sign-changing root lies at the degenerate triple-triangle "
            "endpoint, and d^2(v0,v4)-3 is negative at eight recorded profile "
            "samples. The finite grid can miss tangential roots and is not a "
            "certified parameterization of the full branch, so this does not "
            "prove that a nondegenerate enlarged-pool point is absent. Not a "
            "counterexample claim for Erdos Problem #97."
        ),
        "window": list(T_WINDOW),
        "samples": T_SAMPLES,
        "collapse_profile": profile,
        "detected_sign_change_roots": roots,
        "degenerate_endpoint": endpoint,
        "all_detected_sign_change_roots_at_degenerate_endpoint":
            all_detected_roots_degenerate,
        "near_coincidence_negative_on_profile":
            near_coincidence_negative_on_profile,
        "scan_limitations": [
            "finite sign-change grid can miss tangential or even-multiplicity roots",
            "flex-seeded reprojection is not a certified full-branch parameterization",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-artifact", action="store_true")
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = run()
    ok = (
        result["all_detected_sign_change_roots_at_degenerate_endpoint"]
        and result["near_coincidence_negative_on_profile"]
        and result["degenerate_endpoint"]["is_triple_triangle"]
    )
    result["all_checks_pass"] = ok

    if args.write_artifact:
        args.artifact.parent.mkdir(parents=True, exist_ok=True)
        with args.artifact.open("w", encoding="utf-8", newline="\n") as fh:
            json.dump(result, fh, indent=1)
            fh.write("\n")
        print(f"wrote {args.artifact}", file=sys.stderr)

    if args.json:
        json.dump(result, sys.stdout, indent=1)
        sys.stdout.write("\n")
    else:
        for p in result["collapse_profile"]:
            print(f"t={p['t']:.3f} min-pair {p['min_pair_distance']:.6f} "
                  f"margin {p['convexity_margin']:+.4f} "
                  f"d2(v0,v4)-3 {p['d2_v0_v4_minus_3']:+.3e}")
        print("detected sign-change roots:", len(result["detected_sign_change_roots"]),
              " all at degenerate endpoint:",
              result["all_detected_sign_change_roots_at_degenerate_endpoint"])
        print("degenerate endpoint is triple triangle:",
              result["degenerate_endpoint"]["is_triple_triangle"])
        print("all_checks_pass:", ok)

    if args.check and not ok:
        print("FAIL: family coincidence scan checks failed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
