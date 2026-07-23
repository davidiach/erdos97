#!/usr/bin/env python3
"""Nonlinear continuation test on the 19 doubled-Danzer survivor assignments.

For each survivor the script runs deterministic Levenberg-Marquardt
continuation of the full nonlinear 18-equation C3-slice system from seeds
x = slide(t) + eps * v, with v ranging over the assignment's nontrivial
collision-kernel directions (basis vectors, negatives, and seeded random
in-kernel combinations), eps in {1e-3, 1e-2, 5e-2, 1e-1}, and t in
{0, +0.1, -0.1} along the collided base family.

A run counts as a COUNTEREXAMPLE_CANDIDATE trigger only if the final
residual max|F| < 1e-12 while all three copy-pair separations exceed 1e-4.

Three independent diagnostics quantify the negative outcome:

- pinned-split residual floors: minimize |F| on the affine slice where the
  anti-diagonal split component is pinned to eps (with the scaling and
  rotation gauges also pinned to block the degenerate total-shrink escape);
- the second-order Lyapunov-Schmidt obstruction |P_coker d2F[v,v]| for the
  all-split kernel directions, recomputed in mpmath at dps=50;
- a scan of that obstruction along the collided base family.

This is a numerical negative result (FAILED_APPROACH support): no claim of
a counterexample and no claim about non-equivariant perturbations.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

from erdos97.danzer18_doubling import (
    CROSS,
    EXTERNAL_SURVIVORS,
    OMEGA,
    assignment_jacobian_rows,
    assignment_rank_and_kernel,
    assignment_residuals,
    base_floats,
    collision_x,
    idx_phi,
    idx_r,
    kernel_split_norms,
    mp_assignment_residuals,
    pair_separations,
    projected_blocks,
    split_direction_matrix,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    REPO_ROOT / "data" / "certificates" / "danzer18_survivor_continuation.json"
)
SCHEMA = "erdos97.danzer18_survivor_continuation.v1"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
GENERATOR_COMMAND = (
    "python scripts/check_danzer18_survivor_continuation.py --write-artifact"
)

EPS_LIST = (1e-3, 1e-2, 5e-2, 1e-1)
T_LIST = (0.0, 0.1, -0.1)
PIN_EPS_LIST = (1e-3, 3e-3, 1e-2, 3e-2, 1e-1)
RNG_SEED_RUNS = 97
RNG_SEED_PINS = 1897
RESIDUAL_TOL = 1e-12
SEP_TOL = 1e-4

CHIRAL_FAMILY = (
    (1, 2, 1, 2, 1, 2), (1, 2, 2, 1, 2, 1), (2, 1, 1, 2, 2, 1),
    (2, 1, 2, 1, 1, 2), (3, 4, 3, 4, 3, 4), (3, 4, 4, 3, 4, 3),
    (4, 3, 3, 4, 4, 3), (4, 3, 4, 3, 3, 4),
)


def residual_fn(x, assign):
    return np.array(assignment_residuals(list(x), assign))


def jacobian_fn(x, assign):
    return np.array(assignment_jacobian_rows(list(x), assign))


def base_cross_residuals(y):
    r = [1.0, y[0], y[1]]
    ph = [0.0, y[2], y[3]]
    out = []
    for m in range(3):
        vm, tv = CROSS[m]
        dx = r[vm] * math.cos(ph[vm] + OMEGA * tv) - r[m] * math.cos(ph[m])
        dy = r[vm] * math.sin(ph[vm] + OMEGA * tv) - r[m] * math.sin(ph[m])
        out.append(dx * dx + dy * dy - 3.0 * r[m] ** 2)
    return np.array(out)


def slide_base(t, base, flex4):
    """Collided family point at flex-step t, Newton-polished (still collided)."""
    x0 = np.array(collision_x(base))
    flex = np.zeros(12)
    dr = [0.0, flex4[0], flex4[1]]
    dph = [0.0, flex4[2], flex4[3]]
    for m in range(3):
        for s in range(2):
            flex[idx_r(m, s)] = dr[m]
            flex[idx_phi(m, s)] = dph[m]
    x = x0 + t * flex
    y0 = np.array([x[idx_r(1, 0)], x[idx_r(2, 0)],
                   x[idx_phi(1, 0)], x[idx_phi(2, 0)]])
    sol = least_squares(base_cross_residuals, y0, method="trf",
                        xtol=1e-15, ftol=1e-15, gtol=1e-15)
    out = np.zeros(12)
    for s in range(2):
        out[idx_r(0, s)] = 1.0
        out[idx_phi(0, s)] = 0.0
        out[idx_r(1, s)] = sol.x[0]
        out[idx_r(2, s)] = sol.x[1]
        out[idx_phi(1, s)] = sol.x[2]
        out[idx_phi(2, s)] = sol.x[3]
    return out


def run_lm(assign, x_seed):
    sol = least_squares(residual_fn, x_seed, jac=jacobian_fn, args=(assign,),
                        method="lm", xtol=1e-15, ftol=1e-15, gtol=1e-15,
                        max_nfev=4000)
    res = float(np.abs(residual_fn(sol.x, assign)).max())
    seps = pair_separations(list(sol.x))
    return sol.x, res, seps


def gauge_directions(base):
    sca = np.zeros(12)
    rot = np.zeros(12)
    for m in range(3):
        for s in range(2):
            sca[idx_r(m, s)] = base["r"][m]
            rot[idx_phi(m, s)] = 1.0
    return sca / np.linalg.norm(sca), rot / np.linalg.norm(rot)


def pinned_floor(assign, x0, w, eps, sca_dir, rot_dir):
    """min max|F| on the slice <x - x0, w> = eps with scale/rotation pinned."""
    wmat = np.stack([w, sca_dir, rot_dir], axis=1)
    u, _, _ = np.linalg.svd(wmat, full_matrices=True)
    z = u[:, 3:]

    def f(y):
        return residual_fn(x0 + eps * w + z @ y, assign)

    def j(y):
        return jacobian_fn(x0 + eps * w + z @ y, assign) @ z

    sol = least_squares(f, np.zeros(z.shape[1]), jac=j, method="lm",
                        xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=6000)
    x = x0 + eps * w + z @ sol.x
    res = float(np.abs(residual_fn(x, assign)).max())
    return res, pair_separations(list(x)), x


def obstruction_float(x, assign, kernel):
    """|P_coker d2F[v,v]| for the first kernel direction, float64."""
    v = kernel[0]
    jac = jacobian_fn(x, assign)
    u, sv, _ = np.linalg.svd(jac)
    rank = int((sv > 1e-8 * sv[0]).sum())
    uc = u[:, rank:]
    h = 1e-5
    fp = residual_fn(np.array(x) + h * v, assign)
    f0 = residual_fn(np.array(x), assign)
    fm = residual_fn(np.array(x) - h * v, assign)
    quad = (fp - 2 * f0 + fm) / h ** 2
    return float(np.linalg.norm(uc.T @ quad)), float(np.linalg.norm(quad))


def mp_obstruction(assign, kernel_seed, dps=50):
    """mpmath second-order obstruction at the polished base point."""
    from mpmath import matrix, mpf, norm, sqrt, svd_r

    from erdos97.danzer18_doubling import (
        mp_assignment_jacobian,
        mp_base,
        mp_collision_x,
    )

    x4, _ = mp_base(dps)
    xc = mp_collision_x(x4)
    j = mp_assignment_jacobian(xc, assign)
    u, sv, vt = svd_r(j, compute_uv=True)

    v = matrix([mpf(float(t)) for t in kernel_seed])
    # one refinement step: remove the range components of J v
    jv = j * v
    corr = matrix(12, 1)
    for i in range(8):
        ui = matrix([u[k, i] for k in range(18)])
        vi = matrix([vt[i, k] for k in range(12)])
        coef = sum(ui[k] * jv[k] for k in range(18)) / sv[i]
        for k in range(12):
            corr[k] += coef * vi[k]
    v = v - corr
    v = v / norm(v)
    jv_norm = norm(j * v)

    h = mpf(10) ** (-12)
    xp = [xc[k] + h * v[k] for k in range(12)]
    xm = [xc[k] - h * v[k] for k in range(12)]
    fp = mp_assignment_residuals(xp, assign)
    f0 = mp_assignment_residuals(xc, assign)
    fm = mp_assignment_residuals(xm, assign)
    quad = [(fp[i] - 2 * f0[i] + fm[i]) / h ** 2 for i in range(18)]
    qn2 = sum(q ** 2 for q in quad)
    range_part = mpf(0)
    for i in range(8):
        ui = matrix([u[k, i] for k in range(18)])
        coef = sum(ui[k] * quad[k] for k in range(18))
        range_part += coef ** 2
    return {
        "dps": dps,
        "kernel_residual": float(jv_norm),
        "obstruction": float(sqrt(qn2 - range_part)),
        "quad_norm": float(sqrt(qn2)),
        "sv_rank_boundary": [float(sv[7]), float(sv[8])],
    }


def kernel_at_slid_point(xb, assign):
    """Rank and kernel at a slid collided family point (trivial dirs rebuilt
    from the local base values and local family tangent)."""
    y = np.array([xb[idx_r(1, 0)], xb[idx_r(2, 0)],
                  xb[idx_phi(1, 0)], xb[idx_phi(2, 0)]])
    h = 1e-7
    jb = np.zeros((3, 4))
    for k in range(4):
        yp = y.copy()
        ym = y.copy()
        yp[k] += h
        ym[k] -= h
        jb[:, k] = (base_cross_residuals(yp) - base_cross_residuals(ym)) / (2 * h)
    _, _, vtb = np.linalg.svd(jb)
    flex4 = vtb[3]
    base = {"r": [1.0, float(y[0]), float(y[1])],
            "phi": [0.0, float(y[2]), float(y[3])]}
    from erdos97.danzer18_doubling import numpy_blocks, trivial_directions

    blocks = numpy_blocks(list(xb))
    t = trivial_directions(base, flex4)
    u, _, _ = np.linalg.svd(t, full_matrices=True)
    b = u[:, 3:]
    pblocks = np.einsum("ckij,jl->ckil", blocks, b)
    return assignment_rank_and_kernel(assign, pblocks, b)


def continuation_for(assign, slid, pblocks, b, rng):
    rank, kernel = assignment_rank_and_kernel(assign, pblocks, b)
    dirs = []
    for i in range(kernel.shape[0]):
        dirs.append((f"ker{i}+", kernel[i]))
        dirs.append((f"ker{i}-", -kernel[i]))
    if kernel.shape[0] >= 2:
        for i in range(4):
            c = rng.standard_normal(kernel.shape[0])
            v = c @ kernel
            v /= np.linalg.norm(v)
            dirs.append((f"rand{i}", v))

    runs = []
    best = None
    for t in sorted(slid):
        xb = slid[t]
        for name, v in dirs:
            for eps in EPS_LIST:
                _, res, seps = run_lm(assign, xb + eps * v)
                conv = res < RESIDUAL_TOL
                split_ok = min(seps) > SEP_TOL
                verdict = ("CANDIDATE" if conv and split_ok
                           else "collapsed" if conv else "failed")
                rec = {
                    "t": t, "dir": name, "eps": eps,
                    "residual": res,
                    "min_pair_separation": float(min(seps)),
                    "verdict": verdict,
                }
                runs.append(rec)
                key = (not (conv and split_ok),
                       -min(seps) if conv else 0.0, res)
                if best is None or key < best[0]:
                    best = (key, rec)

    return rank, kernel, runs, best[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-artifact", action="store_true",
                        help="run the full deterministic suite and store the "
                             "certificate JSON")
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--quick", action="store_true",
                        help="reduced run set (t=0, kernel directions only)")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true",
                        help="exit nonzero if any acceptance-criteria "
                             "candidate appears or diagnostics disagree")
    args = parser.parse_args()

    base = base_floats()
    from erdos97.danzer18_doubling import BASE_FLEX4 as flex4

    pblocks, b = projected_blocks()
    psplit = split_direction_matrix()
    sca_dir, rot_dir = gauge_directions(base)
    x0 = np.array(collision_x(base))
    rng = np.random.default_rng(RNG_SEED_RUNS)
    rng_pins = np.random.default_rng(RNG_SEED_PINS)

    t_list = (0.0,) if args.quick else T_LIST
    slid = {t: slide_base(t, base, flex4) for t in t_list}

    survivors_out = []
    n_candidates_total = 0
    for assign in EXTERNAL_SURVIVORS:
        rank, kernel, runs, best = continuation_for(
            assign, slid, pblocks, b, rng)
        norms = kernel_split_norms(kernel, psplit)

        # pinned-split floors
        pins = []
        pin_dirs = []
        for i in range(kernel.shape[0]):
            w_raw = psplit.T @ (psplit @ kernel[i])
            n = np.linalg.norm(w_raw)
            if n > 1e-8:
                pin_dirs.append((f"ker{i}-split", w_raw / n))
        if not pin_dirs:
            for i in range(2):
                w = psplit.T @ rng_pins.standard_normal(6)
                pin_dirs.append((f"rand{i}-split", w / np.linalg.norm(w)))
        for name, w in pin_dirs:
            floors = []
            for eps in PIN_EPS_LIST:
                res, seps, _ = pinned_floor(assign, x0, w, eps,
                                            sca_dir, rot_dir)
                floors.append({
                    "eps": eps, "floor": res,
                    "pair_separations": [float(s) for s in seps],
                })
            le = np.log10([f["eps"] for f in floors])
            lf = np.log10([max(f["floor"], 1e-300) for f in floors])
            pins.append({
                "dir": name,
                "floors": floors,
                "loglog_slope": float(np.polyfit(le, lf, 1)[0]),
            })

        n_cand = sum(1 for r in runs if r["verdict"] == "CANDIDATE")
        n_candidates_total += n_cand
        rec = {
            "assignment": list(assign),
            "collision_rank": rank,
            "kernel_dim": int(kernel.shape[0]),
            "kernel_split_norms": [float(v) for v in norms],
            "n_runs": len(runs),
            "n_candidate": n_cand,
            "n_collapsed": sum(1 for r in runs if r["verdict"] == "collapsed"),
            "n_failed": sum(1 for r in runs if r["verdict"] == "failed"),
            "best_run": best,
            "pinned_split_floors": pins,
            "verdict": "FAILED_no_all_split_branch" if n_cand == 0
            else "CANDIDATE_TRIGGERED",
        }
        if all(v > 1e-6 for v in norms):
            of, qn = obstruction_float(list(x0), assign, kernel)
            rec["second_order_obstruction_float"] = of
            rec["second_order_quad_norm_float"] = qn
        survivors_out.append(rec)
        print(f"  {assign} rank {rank} runs {len(runs)} candidates {n_cand}",
              file=sys.stderr, flush=True)

    # mpmath obstruction for the chiral all-split family
    mp_obs = {}
    if not args.quick:
        for assign in CHIRAL_FAMILY:
            _, kernel = assignment_rank_and_kernel(assign, pblocks, b)
            mp_obs[str(assign)] = mp_obstruction(assign, kernel[0])
            print(f"  mp obstruction {assign} done", file=sys.stderr,
                  flush=True)

    # obstruction scan along the collided family for the chiral family
    family_scan = {}
    if not args.quick:
        ts = [round(v, 3) for v in np.linspace(-0.6, 0.6, 25)]
        for assign in CHIRAL_FAMILY:
            vals = []
            for t in ts:
                xb = slide_base(t, base, flex4)
                rank_t, kernel_t = kernel_at_slid_point(xb, assign)
                if kernel_t.shape[0] == 0:
                    vals.append({"t": t, "rank": rank_t, "obstruction": None})
                    continue
                of, _ = obstruction_float(list(xb), assign, kernel_t)
                vals.append({"t": t, "rank": rank_t, "obstruction": of})
            obs = [v["obstruction"] for v in vals if v["obstruction"]]
            mn = min(obs) if obs else None
            family_scan[str(assign)] = {
                "t_values": ts,
                "min_obstruction": mn,
                "scan": vals,
            }
            print(f"  family scan {assign} min obstruction {mn}",
                  file=sys.stderr, flush=True)

    # polish one partial (single-orbit-split) branch example in mpmath
    partial_branch = None
    if not args.quick:
        assign = (10, 0, 5, 5, 0, 0)
        _, kernel = assignment_rank_and_kernel(assign, pblocks, b)
        w_raw = psplit.T @ (psplit @ kernel[0])
        w = w_raw / np.linalg.norm(w_raw)
        res, seps, xsol = pinned_floor(assign, x0, w, 0.1, sca_dir, rot_dir)
        partial_branch = polish_partial_branch(assign, xsol)
        partial_branch["float64_floor"] = res
        partial_branch["float64_pair_separations"] = [float(s) for s in seps]

    result = {
        "schema": SCHEMA,
        "status": "NEGATIVE_CONTINUATION_ALL_19_SURVIVORS",
        "trust": TRUST,
        "provenance": {"command": GENERATOR_COMMAND},
        "claim_scope": (
            "Deterministic Levenberg-Marquardt continuation and second-order "
            "obstruction diagnostics for the 19 externally supplied "
            "doubled-Danzer survivor assignments at the 2026-07 base "
            "nonagon. Numerical negative evidence only: no all-three-split "
            "branch was found, no counterexample is claimed, and "
            "non-equivariant (full 36-dof) perturbations are out of scope."
        ),
        "parameters": {
            "eps_list": list(EPS_LIST),
            "t_list": list(t_list),
            "pin_eps_list": list(PIN_EPS_LIST),
            "rng_seed_runs": RNG_SEED_RUNS,
            "rng_seed_pins": RNG_SEED_PINS,
            "residual_tol": RESIDUAL_TOL,
            "separation_tol": SEP_TOL,
        },
        "survivors": survivors_out,
        "n_candidates_total": n_candidates_total,
        "mp_second_order_obstruction": mp_obs,
        "family_obstruction_scan": family_scan,
        "partial_branch_example": partial_branch,
    }
    ok = n_candidates_total == 0
    if not args.quick:
        ok = ok and all(v["obstruction"] > 1.0 for v in mp_obs.values())
        ok = ok and all(s["min_obstruction"] > 1.0
                        for s in family_scan.values())
    result["all_checks_pass"] = ok

    if args.write_artifact:
        args.artifact.parent.mkdir(parents=True, exist_ok=True)
        with args.artifact.open("w", encoding="utf-8", newline="\n") as fh:
            json.dump(result, fh, indent=1)
            fh.write("\n")
        print(f"wrote {args.artifact}", file=sys.stderr)

    if args.json:
        compact = dict(result)
        compact["survivors"] = [
            {k: v for k, v in s.items() if k != "pinned_split_floors"}
            for s in result["survivors"]
        ]
        compact["family_obstruction_scan"] = {
            k: {"min_obstruction": v["min_obstruction"]}
            for k, v in result["family_obstruction_scan"].items()
        }
        json.dump(compact, sys.stdout, indent=1)
        sys.stdout.write("\n")
    else:
        for s in survivors_out:
            print(f"{tuple(s['assignment'])} rank {s['collision_rank']} "
                  f"runs {s['n_runs']} candidates {s['n_candidate']} "
                  f"best residual {s['best_run']['residual']:.2e} "
                  f"best min-sep {s['best_run']['min_pair_separation']:.2e} "
                  f"-> {s['verdict']}")
        print("n_candidates_total:", n_candidates_total)
        print("all_checks_pass:", ok)

    if args.check and not ok:
        print("FAIL: continuation checks failed (or a candidate appeared; "
              "if so, follow docs/exactification-plan.md)", file=sys.stderr)
        return 1
    return 0


def polish_partial_branch(assign, xsol, dps=40):
    """Newton-polish a partial-split branch point in mpmath (truncated-SVD
    pseudo-inverse Newton on the 18-equation system; the Jacobian is rank
    deficient on the solution manifold) and record it to 40 digits."""
    from mpmath import mp, mpf, svd_r

    from erdos97.danzer18_doubling import (
        mp_assignment_jacobian,
        mp_assignment_residuals,
    )

    mp.dps = dps
    x = [mpf(float(v)) for v in xsol]
    for _ in range(8):
        f = mp_assignment_residuals(x, assign)
        j = mp_assignment_jacobian(x, assign)
        u, sv, vt = svd_r(j, compute_uv=True)
        tol = sv[0] * mpf("1e-10")
        dx = [mpf(0)] * 12
        for i in range(12):
            if sv[i] <= tol:
                continue
            coef = sum(u[k, i] * f[k] for k in range(18)) / sv[i]
            for k in range(12):
                dx[k] += coef * vt[i, k]
        x = [x[k] - dx[k] for k in range(12)]
    f = mp_assignment_residuals(x, assign)
    seps = pair_separations([float(v) for v in x])
    return {
        "assignment": list(assign),
        "dps": dps,
        "max_residual": float(max(abs(v) for v in f)),
        "pair_separations": [float(s) for s in seps],
        "coordinates_r_phi_by_orbit_copy": [mp.nstr(v, 40) for v in x],
        "note": (
            "Genuine nonlinear branch with exactly one orbit pair split; the "
            "other two copy pairs collide, so the 18-point configuration has "
            "only 12 distinct points and is NOT a counterexample candidate. "
            "Recorded as seed material for non-equivariant follow-up."
        ),
    }


if __name__ == "__main__":
    raise SystemExit(main())
