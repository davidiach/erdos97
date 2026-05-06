#!/usr/bin/env python3
"""Q-L9 (quantitative L9) filter for 4-bad polygon candidates.

Implements the Q-L9 lemma from data/runs/2026-05-05/L9_sharpening.md:

    Every 4-bad strictly convex polygon P satisfies
        eps(P) >= delta_min(P) * sin theta_int(v) / 2

where:
- eps(P) is the Hausdorff-radial deviation of vertices from the best-fit circle,
- delta_min is the minimum pairwise vertex separation,
- theta_int is the angle between v's witness circle and the best-fit circle at
  their nominal intersection.

Under the generic transversality assumption sin theta_int >= 1/2 the lemma
collapses to the explicit lower bound

        eps(P) / delta_min(P) >= 1/4,

which is the filter threshold used here (rejecting candidates with ratio < 1/4
on the assumption they are 4-bad). The recommended floor in section 2.1 of the
write-up is "delta_min <= 4*eps", i.e. ratio >= 1/4. This script implements that
filter and applies it to all *.json artifacts in data/runs/ that carry vertex
coordinates.

Bonus: SLSQP optimisation with the Q-L9 floor as a soft inequality
constraint, demonstrated on the C13_sidon and B12 near-miss patterns.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.optimize import least_squares, minimize

ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Best-fit circle
# ---------------------------------------------------------------------------


def _circle_residuals(params: np.ndarray, V: np.ndarray) -> np.ndarray:
    cx, cy, rho = params
    return np.linalg.norm(V - np.array([cx, cy]), axis=1) - rho


def best_fit_circle(V: np.ndarray) -> tuple[np.ndarray, float, float]:
    """Return (centre, radius, eps) where eps = max_v ||v - C| - rho|."""
    centroid = V.mean(axis=0)
    rho0 = float(np.linalg.norm(V - centroid, axis=1).mean())
    res = least_squares(_circle_residuals, x0=[centroid[0], centroid[1], rho0], args=(V,))
    cx, cy, rho = res.x
    centre = np.array([cx, cy])
    eps = float(np.max(np.abs(np.linalg.norm(V - centre, axis=1) - rho)))
    return centre, float(rho), eps


def min_vertex_separation(V: np.ndarray) -> float:
    diffs = V[:, None, :] - V[None, :, :]
    sq = np.einsum("ijk,ijk->ij", diffs, diffs)
    n = V.shape[0]
    sq[np.arange(n), np.arange(n)] = np.inf
    return float(math.sqrt(sq.min()))


# ---------------------------------------------------------------------------
# Q-L9 core
# ---------------------------------------------------------------------------


def q_l9_check(coordinates: Iterable[Iterable[float]], threshold: float = 0.25) -> dict:
    """Apply the Q-L9 filter to a polygon's vertex coordinates.

    Parameters
    ----------
    coordinates : iterable of (x, y)
    threshold   : minimum ratio eps/delta_min for the filter to PASS
                  (default 0.25 corresponds to the 'delta_min <= 4*eps' floor;
                  the lemma admits this whenever sin theta_int >= 1/2).

    Returns
    -------
    dict with keys: eps, delta_min, ratio, passes_q_l9, centre, rho.
    """
    V = np.asarray(coordinates, dtype=float)
    if V.ndim != 2 or V.shape[1] != 2 or V.shape[0] < 3:
        raise ValueError(f"need an (n, 2) array with n >= 3; got {V.shape}")

    centre, rho, eps = best_fit_circle(V)
    delta_min = min_vertex_separation(V)
    ratio = eps / delta_min if delta_min > 0 else math.inf
    return {
        "eps": eps,
        "delta_min": delta_min,
        "ratio": ratio,
        "passes_q_l9": bool(ratio >= threshold),
        "threshold": threshold,
        "centre": centre.tolist(),
        "rho": rho,
    }


def witness_circle_angle(V: np.ndarray, v_idx: int, witnesses: list[int],
                         centre: np.ndarray, rho: float) -> float | None:
    """sin theta_int(v): angle between v's witness circle and best-fit circle.

    The two circles are circle(v, r_v) and circle(C, rho). For two circles with
    centre distance d the intersection angle phi satisfies
        cos phi = (r_v^2 + rho^2 - d^2) / (2 r_v rho)
    when |rho - r_v| <= d <= rho + r_v; otherwise no real intersection (returns
    None).
    """
    v = V[v_idx]
    dists = np.linalg.norm(V[witnesses] - v, axis=1)
    r_v = float(dists.mean())
    d = float(np.linalg.norm(v - centre))
    if d <= 0 or r_v <= 0 or rho <= 0:
        return None
    if d < abs(rho - r_v) - 1e-12 or d > rho + r_v + 1e-12:
        return None
    cos_phi = (r_v * r_v + rho * rho - d * d) / (2.0 * r_v * rho)
    cos_phi = max(-1.0, min(1.0, cos_phi))
    return math.sin(math.acos(cos_phi))


def q_l9_per_vertex(V: np.ndarray, S: list[list[int]], centre: np.ndarray,
                    rho: float, eps: float, delta_min: float) -> list[dict]:
    """For each vertex v with M(v) >= 4, compare eps with delta_min*sin(theta)/2."""
    out = []
    for v_idx, witnesses in enumerate(S):
        if len(witnesses) < 4:
            continue
        sin_theta = witness_circle_angle(V, v_idx, list(witnesses), centre, rho)
        if sin_theta is None:
            out.append({"v": v_idx, "sin_theta_int": None, "lower_bound": None,
                        "ratio_to_eps": None})
            continue
        lower = delta_min * sin_theta / 2.0
        out.append({
            "v": v_idx,
            "sin_theta_int": sin_theta,
            "lower_bound": lower,
            "ratio_to_eps": eps / lower if lower > 0 else math.inf,
        })
    return out


# ---------------------------------------------------------------------------
# Apply filter to every coordinate-bearing artifact
# ---------------------------------------------------------------------------


def _coords_from_artifact(d: dict) -> np.ndarray | None:
    if not isinstance(d, dict) or "coordinates" not in d:
        return None
    coords = d["coordinates"]
    try:
        arr = np.asarray(coords, dtype=float)
    except (TypeError, ValueError):
        return None
    if arr.ndim != 2 or arr.shape[1] != 2:
        return None
    return arr


def scan_runs(runs_dir: Path, threshold: float = 0.25) -> list[dict]:
    rows = []
    for path in sorted(runs_dir.glob("*.json")):
        try:
            d = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        V = _coords_from_artifact(d)
        if V is None:
            continue
        try:
            base = q_l9_check(V, threshold=threshold)
        except ValueError:
            continue
        S = d.get("S")
        per_vertex = []
        if isinstance(S, list) and len(S) == V.shape[0]:
            try:
                centre = np.asarray(base["centre"])
                per_vertex = q_l9_per_vertex(V, S, centre, base["rho"],
                                             base["eps"], base["delta_min"])
            except Exception:
                per_vertex = []
        rows.append({
            "file": str(path.relative_to(ROOT)),
            "pattern_name": d.get("pattern_name"),
            "n": d.get("n"),
            "loss": d.get("loss"),
            "min_pair_distance": d.get("min_pair_distance"),
            **base,
            "per_vertex_q_l9": per_vertex,
        })
    return rows


# ---------------------------------------------------------------------------
# SLSQP optimisation with Q-L9 constraint (bonus task)
# ---------------------------------------------------------------------------


def _polar_to_xy(theta: np.ndarray, r: np.ndarray) -> np.ndarray:
    return np.column_stack([r * np.cos(theta), r * np.sin(theta)])


def _polygon_loss(theta: np.ndarray, r: np.ndarray, S: list[list[int]]) -> float:
    V = _polar_to_xy(theta, r)
    total = 0.0
    for i, witnesses in enumerate(S):
        d2 = np.sum((V[witnesses] - V[i]) ** 2, axis=1)
        total += float(np.var(d2))
    return total


def _q_l9_ratio_for_xy(V: np.ndarray) -> float:
    centre, rho, eps = best_fit_circle(V)
    delta = min_vertex_separation(V)
    if delta <= 0:
        return math.inf
    return eps / delta


def slsqp_with_q_l9(coords0: np.ndarray, S: list[list[int]],
                    floor: float = 0.5, max_iter: int = 200,
                    use_q_l9: bool = True) -> dict:
    """Run a simple SLSQP refinement starting from coords0 with optional
    Q-L9 lower-bound constraint  eps/delta_min >= floor."""
    n = coords0.shape[0]
    theta0 = np.arctan2(coords0[:, 1], coords0[:, 0])
    r0 = np.linalg.norm(coords0, axis=1)
    x0 = np.concatenate([theta0, r0])

    def unpack(x):
        return x[:n], x[n:]

    def obj(x):
        theta, r = unpack(x)
        return _polygon_loss(theta, r, S)

    constraints = []
    if use_q_l9:
        def ratio_cons(x):
            theta, r = unpack(x)
            V = _polar_to_xy(theta, r)
            return _q_l9_ratio_for_xy(V) - floor
        constraints.append({"type": "ineq", "fun": ratio_cons})

    res = minimize(obj, x0, method="SLSQP", constraints=constraints,
                   options={"maxiter": max_iter, "ftol": 1e-9})
    theta, r = unpack(res.x)
    V = _polar_to_xy(theta, r)
    return {
        "success": bool(res.success),
        "message": str(res.message),
        "loss_initial": float(_polygon_loss(theta0, r0, S)),
        "loss_final": float(res.fun),
        "ratio_initial": float(_q_l9_ratio_for_xy(coords0)),
        "ratio_final": float(_q_l9_ratio_for_xy(V)),
        "delta_min_initial": float(min_vertex_separation(coords0)),
        "delta_min_final": float(min_vertex_separation(V)),
        "use_q_l9": use_q_l9,
        "floor": floor,
        "n_iter": int(res.nit) if hasattr(res, "nit") else None,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir",
                        default=str(ROOT / "data" / "runs"),
                        help="directory of *.json artifacts to scan")
    parser.add_argument("--threshold", type=float, default=0.25,
                        help="ratio threshold; reject if eps/delta_min < threshold")
    parser.add_argument("--demo-slsqp", action="store_true",
                        help="run SLSQP with Q-L9 constraint on B12 and C13 sidon")
    parser.add_argument("--write",
                        default=str(ROOT / "data" / "certificates" / "2026-05-06"
                                    / "q_l9_filter_results.json"),
                        help="output JSON path")
    args = parser.parse_args(argv)

    rows = scan_runs(Path(args.runs_dir), threshold=args.threshold)

    summary = {
        "threshold": args.threshold,
        "n_artifacts": len(rows),
        "n_pass_filter": sum(1 for r in rows if r["passes_q_l9"]),
        "n_blocked":     sum(1 for r in rows if not r["passes_q_l9"]),
    }

    print(f"# Q-L9 filter (threshold ratio = {args.threshold})")
    print(f"Scanned {summary['n_artifacts']} coordinate-bearing artifacts")
    print(f"Passes:  {summary['n_pass_filter']}")
    print(f"Blocked: {summary['n_blocked']}")
    print()
    print(f"{'pattern':<55} {'n':>3} {'eps':>10} {'delta_min':>11} {'ratio':>9} {'verdict':>9}")
    for r in rows:
        verdict = "PASS" if r["passes_q_l9"] else "BLOCKED"
        print(f"{(r.get('pattern_name') or r['file'])[:55]:<55} "
              f"{(r.get('n') or 0):>3} "
              f"{r['eps']:>10.3e} {r['delta_min']:>11.3e} "
              f"{r['ratio']:>9.3e} {verdict:>9}")

    slsqp_demos = []
    if args.demo_slsqp:
        for stem, label in [("best_B12_slsqp_m1e-6", "B12"),
                            ("C13_sidon_m1e-6", "C13_sidon_m1e-6")]:
            path = ROOT / "data" / "runs" / f"{stem}.json"
            if not path.exists():
                continue
            d = json.loads(path.read_text())
            V = np.asarray(d["coordinates"], dtype=float)
            S = d["S"]
            try:
                with_constraint = slsqp_with_q_l9(V, S, floor=0.5,
                                                  max_iter=300, use_q_l9=True)
                without_constraint = slsqp_with_q_l9(V, S, floor=0.5,
                                                     max_iter=300, use_q_l9=False)
            except Exception as e:
                slsqp_demos.append({"pattern": label, "error": repr(e)})
                continue
            slsqp_demos.append({
                "pattern": label,
                "with_q_l9_constraint": with_constraint,
                "without_constraint": without_constraint,
            })
            print()
            print(f"# SLSQP demo on {label}")
            print(f"  initial loss              {with_constraint['loss_initial']:.3e}")
            print(f"  final loss (no Q-L9)      {without_constraint['loss_final']:.3e}")
            print(f"  final loss (with Q-L9)    {with_constraint['loss_final']:.3e}")
            print(f"  ratio initial             {with_constraint['ratio_initial']:.3e}")
            print(f"  ratio final  (no Q-L9)    {without_constraint['ratio_final']:.3e}")
            print(f"  ratio final  (with Q-L9)  {with_constraint['ratio_final']:.3e}")

    out_path = Path(args.write)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "summary": summary,
        "rows": rows,
        "slsqp_demos": slsqp_demos,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\nWrote {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
