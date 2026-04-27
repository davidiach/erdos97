#!/usr/bin/env python3
"""Empirical sweep that calibrates the 3-fold cluster obstruction constants.

For a log-spaced grid of convexity-margin targets ``m`` in
``[1e-9, 1e-3]``, we run ``--restarts`` independent SLSQP-style restarts on
``B12_3x4_danzer_lift``.  Each restart:

* warm-starts from a hand-constructed 3-cluster polygon at a randomized
  curvature and intra-cluster spacing chosen so the initial convexity
  margin is comparable to ``m``;
* perturbs slightly to break symmetry;
* runs ``scipy.optimize.least_squares`` with a hard barrier ``max(0, m-ori)``
  on every consecutive edge orientation to keep ``gamma >= m`` and a
  squared-distance equality residual to drive ``r`` down.

Each surviving restart yields a ``(gamma, r, rho, theta)`` tuple, where:

* ``gamma`` is the realized strict convexity margin (positive in every
  accepted run);
* ``r`` is the RMS equality residual (``eq_rms``) per
  :func:`erdos97.search.independent_diagnostics`;
* ``rho`` is the minimum intra-cluster pairwise distance, taken over the
  canonical block-(3,4) cluster partition;
* ``theta`` is the mean cluster-tangent / radial-direction angle in radians.

Results are written to ``data/obstructions/three_fold_cluster_runs.json``.
A linear least-squares fit of ``log r`` vs ``log gamma`` (overall and per
orientation regime) is written to
``data/obstructions/three_fold_cluster_fit.json``.

The fit is the empirical witness used by
``docs/lemmas/no_3fold_cluster_obstruction.md`` to confirm the analytic
exponent.  The ``C1`` lower-bound coefficient stored in
:mod:`erdos97.obstructions` is set conservatively below the smallest
empirically observed ratio ``r / gamma^alpha`` across this sweep.

Usage::

    python scripts/empirical_obstruction_constants.py            # default sweep
    python scripts/empirical_obstruction_constants.py --quick    # fast smoke
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from erdos97.obstructions import (
    cluster_orientation_angle,
    cluster_partition,
    min_intra_cluster_distance,
)
from erdos97.search import (
    built_in_patterns,
    independent_diagnostics,
    inverse_polar_x,
    orient_margins,
    pairwise_sqdist,
    polygon_from_x,
)
from scipy.optimize import least_squares


def _make_3cluster(rho: float, kappa: float, theta_off: float) -> np.ndarray:
    """Hand-built 3-cluster polygon at vertices of an equilateral triangle.

    ``theta_off`` controls cluster orientation: ``pi/2`` means the cluster
    tangent is perpendicular to the radial direction (generic regime);
    ``0`` means tangent parallel to radial (degenerate, non-strictly-convex
    in the limit).  ``rho`` is the spacing of consecutive intra-cluster
    points along the tangent.  ``kappa`` is the inward parabolic curvature.
    """
    pts: List[np.ndarray] = []
    s_vals = [-1.5, -0.5, 0.5, 1.5]
    for a in range(3):
        ang = 2.0 * math.pi * a / 3.0
        Va = np.array([math.cos(ang), math.sin(ang)])
        u = Va / np.linalg.norm(Va)
        t_perp = np.array([-math.sin(ang), math.cos(ang)])
        tt = math.sin(theta_off) * t_perp + math.cos(theta_off) * u
        nn = -u
        for s in s_vals:
            sp = s * rho
            pts.append(Va + sp * tt + (kappa / 2.0) * sp * sp * nn)
    return np.asarray(pts, dtype=float)


def _custom_residual(x: np.ndarray, n: int, S, m: float) -> np.ndarray:
    """Equality residuals plus a hard one-sided barrier ``max(0, m - ori)``.

    Unlike :func:`erdos97.search.residual_vector`, this barrier is exactly
    zero when every consecutive orientation already exceeds ``m``, so the
    optimizer can make ``r`` arbitrarily small as long as it preserves
    ``ori >= m`` everywhere.
    """
    P = polygon_from_x(x, n, "polar")
    D2 = pairwise_sqdist(P)
    rows: List[np.ndarray] = []
    for i, Si in enumerate(S):
        vals = np.array([D2[i, j] for j in Si], dtype=float)
        rows.append(vals - vals.mean())
    eq = np.concatenate(rows) if rows else np.zeros(0)
    ori = orient_margins(P)
    barrier = np.maximum(0.0, m - ori)
    # Convexity barrier weight: large enough that the optimizer respects
    # the floor, but the floor binds only when ori < m so it does not
    # interfere with the equality term in the cluster basin.
    return np.concatenate([eq, 1000.0 * barrier])


def _run_one_restart(
    pat,
    rho_init: float,
    kappa: float,
    theta_off: float,
    margin_floor: float,
    seed: int,
    max_nfev: int,
) -> Dict[str, float]:
    rng = np.random.default_rng(seed)
    P0 = _make_3cluster(rho_init, kappa=kappa, theta_off=theta_off)
    P0 = P0 + (0.05 * rho_init) * rng.normal(size=P0.shape)
    try:
        x0 = inverse_polar_x(P0)
    except Exception:  # pragma: no cover - sanity belt
        return {}

    def fun(x):
        return _custom_residual(x, pat.n, pat.S, margin_floor)

    try:
        sol = least_squares(
            fun,
            x0,
            method="trf",
            max_nfev=max_nfev,
            x_scale="jac",
            ftol=1e-13,
            xtol=1e-13,
            gtol=1e-13,
        )
    except Exception:  # pragma: no cover
        return {}
    P = polygon_from_x(sol.x, pat.n, "polar")
    diag = independent_diagnostics(P, pat.S)
    gamma = float(diag["convexity_margin"])
    r = float(diag["eq_rms"])
    if not math.isfinite(gamma) or not math.isfinite(r) or gamma <= 0.0 or r <= 0.0:
        return {}
    clusters = cluster_partition(pat.name, pat.n)
    rho = float(min_intra_cluster_distance(P, clusters))
    theta = float(cluster_orientation_angle(P, clusters))
    return {
        "seed": int(seed),
        "convex_margin_target": float(margin_floor),
        "rho_init": float(rho_init),
        "kappa_init": float(kappa),
        "theta_init": float(theta_off),
        "gamma": gamma,
        "r": r,
        "rho": rho,
        "theta": theta,
        "cost": float(np.sum(sol.fun ** 2)),
    }


def _classify_regime(theta: float) -> str:
    """Bucket cluster orientation: ``orthogonal`` if tangent within 20 deg
    of radial, ``generic`` otherwise.  ``theta`` is in ``[0, pi/2]``."""
    return "orthogonal" if theta < math.radians(20.0) else "generic"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="small fast sweep")
    ap.add_argument("--restarts", type=int, default=10)
    ap.add_argument("--num-tols", type=int, default=30)
    ap.add_argument("--max-nfev", type=int, default=400)
    ap.add_argument("--gamma-min", type=float, default=1e-9)
    ap.add_argument("--gamma-max", type=float, default=1e-3)
    ap.add_argument(
        "--out-runs",
        default="data/obstructions/three_fold_cluster_runs.json",
    )
    ap.add_argument(
        "--out-fit",
        default="data/obstructions/three_fold_cluster_fit.json",
    )
    ap.add_argument("--seed-base", type=int, default=20260427)
    args = ap.parse_args()

    if args.quick:
        args.num_tols = 6
        args.restarts = 3
        args.max_nfev = 600

    pat = built_in_patterns()["B12_3x4_danzer_lift"]
    tols = np.geomspace(args.gamma_max, args.gamma_min, args.num_tols)

    out_runs = ROOT / args.out_runs
    out_fit = ROOT / args.out_fit
    out_runs.parent.mkdir(parents=True, exist_ok=True)

    runs: List[Dict[str, float]] = []
    t0 = time.time()
    seed = int(args.seed_base)
    rng = np.random.default_rng(seed)
    for m in tols:
        # gamma ~ kappa * rho^3 in the parabolic family; pick rho_init from
        # the target margin and let the optimizer fine-tune.
        rho_target = float(m) ** (1.0 / 3.0)
        for k in range(args.restarts):
            kappa = float(np.clip(rng.lognormal(mean=0.0, sigma=0.4), 0.3, 3.0))
            rho_init = float(rho_target * np.clip(rng.lognormal(mean=0.0, sigma=0.2), 0.7, 1.5))
            rec = _run_one_restart(
                pat,
                rho_init=rho_init,
                kappa=kappa,
                theta_off=math.pi / 2.0,
                margin_floor=float(m),
                seed=seed,
                max_nfev=int(args.max_nfev),
            )
            seed += 1
            if rec:
                runs.append(rec)
        elapsed = time.time() - t0
        print(
            f"  tol {m:.1e}: {len(runs)} cumulative successes after {elapsed:.1f}s",
            flush=True,
        )

    if not runs:
        print("ERROR: no successful restarts", file=sys.stderr)
        return 1

    payload = {
        "pattern_id": "B12_3x4_danzer_lift",
        "n_runs": len(runs),
        "convex_margin_grid": [float(t) for t in tols],
        "restarts_per_tol": int(args.restarts),
        "runs": runs,
    }
    with open(out_runs, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"wrote {out_runs} ({len(runs)} runs)")

    log_g_all = np.array([math.log(r["gamma"]) for r in runs])
    log_r_all = np.array([math.log(r["r"]) for r in runs])

    def linfit(xs: np.ndarray, ys: np.ndarray) -> Dict[str, float]:
        if len(xs) < 2:
            return {"n_points": int(len(xs))}
        slope, intercept = np.polyfit(xs, ys, 1)
        yhat = slope * xs + intercept
        ss_res = float(np.sum((ys - yhat) ** 2))
        ss_tot = float(np.sum((ys - ys.mean()) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0.0 else 1.0
        return {
            "n_points": int(len(xs)),
            "slope": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r2),
            "alpha_estimate": float(slope),
            "C1_estimate": float(math.exp(intercept)),
        }

    overall = linfit(log_g_all, log_r_all)

    by_regime: Dict[str, Dict[str, float]] = {}
    for regime in ("generic", "orthogonal"):
        sel = [(math.log(rec["gamma"]), math.log(rec["r"])) for rec in runs
               if _classify_regime(rec["theta"]) == regime]
        if sel:
            xs = np.array([s[0] for s in sel])
            ys = np.array([s[1] for s in sel])
            by_regime[regime] = linfit(xs, ys)
        else:
            by_regime[regime] = {"n_points": 0}

    alpha = overall["slope"]
    ratios = np.exp(log_r_all - alpha * log_g_all)
    min_ratio = float(np.min(ratios))
    median_ratio = float(np.median(ratios))

    fit_payload = {
        "pattern_id": "B12_3x4_danzer_lift",
        "input": str(out_runs.relative_to(ROOT)),
        "n_runs": len(runs),
        "overall_fit": overall,
        "fit_by_regime": by_regime,
        "min_observed_ratio": min_ratio,
        "median_observed_ratio": median_ratio,
        "decision_rule": {
            "analytic_alpha_options": [1.0 / 3.0, 2.0 / 3.0],
            "tolerance": 0.05,
            "verdict": _verdict(overall["slope"]),
        },
    }
    with open(out_fit, "w", encoding="utf-8") as f:
        json.dump(fit_payload, f, indent=2)
    print(f"wrote {out_fit}")
    print(f"overall fit: alpha={overall['slope']:.4f}, "
          f"C1_fit={math.exp(overall['intercept']):.4g}, R^2={overall['r_squared']:.4f}")
    print(f"min observed r/gamma^alpha = {min_ratio:.4g}")
    elapsed = time.time() - t0
    print(f"sweep complete in {elapsed:.1f}s")
    return 0


def _verdict(alpha: float) -> str:
    if abs(alpha - 1.0 / 3.0) <= 0.05:
        return "alpha consistent with analytic 1/3 (generic regime)"
    if abs(alpha - 2.0 / 3.0) <= 0.05:
        return "alpha consistent with analytic 2/3 (orthogonal regime)"
    return ("alpha disagrees with both analytic options by more than 0.05; "
            "downgrade lemma to NUMERICAL_EVIDENCE + CONJECTURE")


if __name__ == "__main__":
    raise SystemExit(main())
