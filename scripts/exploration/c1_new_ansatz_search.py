"""C1 lane: GLOBAL free-form numerical search with a NEW ansatz for Erdos #97.

Trust label for everything produced here: NUMERICAL_EVIDENCE / HEURISTIC.
This file contains NO proof of the general problem and claims NO counterexample.
A numerical near-equality is NOT a counterexample (see docs/exactification-plan.md,
README.md "Numerical near-misses", docs/failed-ideas.md).

Why this ansatz is genuinely DIFFERENT from the forbidden ones
--------------------------------------------------------------
Forbidden / already-killed structures we deliberately do NOT use:
  * #7  B12_3x4_danzer_lift  -- a *fixed* 3x4 selected pattern + Danzer lift,
        searched in polar (radius/angle) coordinates.  We use neither that
        fixed pattern nor a polar parameterization.
  * #17 / two-orbit-radius-propagation -- two concentric half-step-offset
        regular m-gons with a fixed quarter-turn selected pattern.  We do NOT
        place points on concentric circles and we do NOT fix the selected
        pattern.
  * #20 Fishburn--Reeds cut-matrix nearest-fourth homotopy -- a 20-point
        FR k=3 decimal scaffold continued to a 4-witness system.  We use no
        FR table and no homotopy continuation.

Also avoided: full coordinate symmetry / circulant patterns (#6), common-radius
reduction (#15).

What this search DOES (the new ansatz)
--------------------------------------
1. Free Cartesian coordinates: x in R^{2n}, points p_i = (x[2i], x[2i+1]).
   No symmetry imposed; no circle/orbit imposed; no fixed selected pattern.
2. Per-center FREE radius: implicit.  For each center i we look at the squared
   distances d_ij = |p_i - p_j|^2 to all other vertices and DYNAMICALLY pick the
   4 of them that are closest together (the 4-subset minimizing their variance).
   The "radius^2" of center i is then the mean of those 4 selected values --
   it is whatever the configuration wants, independent per center.  This is the
   exact local objective the problem asks for, with NO pattern prescribed.
3. Soft-selection for gradient-friendliness: instead of the hard argmin-4-set,
   the per-center penalty is a softmin over 4-subsets of their variance.  As the
   softmin temperature -> 0 this recovers the true min-over-4-subsets.  We anneal
   the temperature down during refinement, then report HARD (true argmin) metrics.
4. Strict convexity: enforced as a barrier on signed turns.  In the cyclic
   vertex order 0,1,...,n-1 every consecutive turn determinant
       cross(p_{i+1}-p_i, p_{i+2}-p_{i+1})
   must be >= margin (all same sign).  We additionally report the stronger
   full one-sided check orient(p_i,p_{i+1},p_j) > 0 for all edges and vertices
   on the best hard configuration, which is the real strict-convexity witness.
5. Asymmetric multistart / basin-hopping over the raw coordinates with SLSQP /
   L-BFGS-B local polishes and random kicks.  No structure is reused between
   restarts except the running best.

Total objective minimized:
    F(x) = sum_i softmin_{4-subset S}( var(d_ij : j in S) )
           + w_conv * sum_i barrier(turn_i)
           + w_scale * (scale-normalization term)
where barrier(t) = max(0, margin - t)^2 pushes every consecutive turn to be
>= margin with the SAME sign (we fix the sign to positive by a one-time global
orientation flip).

Reported metrics are computed on the HARD selection (true argmin 4-subset per
center) so no softmin slack leaks into the trust-bearing numbers.

CLI
---
    python scripts/exploration/c1_new_ansatz_search.py --n 12 --seconds 60
    python scripts/exploration/c1_new_ansatz_search.py --n 10 12 16 --seconds 60 \
        --out data/runs/c1_new_ansatz_2026-06-14
"""
from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass, asdict
from itertools import combinations
from time import monotonic

import numpy as np
from scipy.optimize import minimize


# --------------------------------------------------------------------------- #
# Geometry helpers (all squared distances; no sqrt in the objective)          #
# --------------------------------------------------------------------------- #
def points_of(x: np.ndarray, n: int) -> np.ndarray:
    return x.reshape(n, 2)


def all_sq_dists(pts: np.ndarray) -> np.ndarray:
    """Return the n x n matrix of squared distances |p_i - p_j|^2."""
    diff = pts[:, None, :] - pts[None, :, :]
    return np.einsum("ijk,ijk->ij", diff, diff)


# Precompute, for n-1 candidate distances per center, all C(n-1,4) 4-subsets as
# an index array of shape (num_subsets, 4).  These index into the sorted list of
# OTHER vertices for a center, but we build subsets over a generic (n-1) list.
def four_subsets(m: int) -> np.ndarray:
    return np.array(list(combinations(range(m), 4)), dtype=np.int64)


def variance4(vals: np.ndarray) -> np.ndarray:
    """Population variance of the last axis (length 4)."""
    mean = vals.mean(axis=-1, keepdims=True)
    return ((vals - mean) ** 2).mean(axis=-1)


# --------------------------------------------------------------------------- #
# Objective                                                                   #
# --------------------------------------------------------------------------- #
@dataclass
class SearchConfig:
    n: int
    margin: float = 1e-3
    w_conv: float = 50.0
    softmin_beta: float = 200.0  # higher = closer to hard argmin
    seed: int = 0


def _per_center_softmin_var(
    dmat: np.ndarray,
    n: int,
    subsets: np.ndarray,
    beta: float,
) -> float:
    """Sum over centers of softmin_{4-subset} var(selected squared distances).

    For center i, take the n-1 squared distances to other vertices, form the
    variance of every 4-subset, and softmin them: -1/beta * logsumexp(-beta*var).
    """
    total = 0.0
    for i in range(n):
        others = dmat[i, np.arange(n) != i]  # length n-1
        sub_vals = others[subsets]  # (num_subsets, 4)
        var = variance4(sub_vals)  # (num_subsets,)
        # numerically-stable softmin
        z = -beta * var
        m = z.max()
        sm = -(m + math.log(np.exp(z - m).sum())) / beta
        total += sm
    return total


def _convexity_barrier(pts: np.ndarray, n: int, margin: float) -> tuple[float, float]:
    """Return (barrier_penalty, min_signed_turn) for the cyclic order.

    Signed turn at vertex i: cross(p_{i+1}-p_i, p_{i+2}-p_{i+1}).  We orient so
    the polygon is counter-clockwise by checking the signed area sign and, if
    needed, the caller flips; here we just push every turn >= margin (positive).
    """
    turns = np.empty(n)
    for i in range(n):
        a = pts[(i + 1) % n] - pts[i]
        b = pts[(i + 2) % n] - pts[(i + 1) % n]
        turns[i] = a[0] * b[1] - a[1] * b[0]
    deficit = np.maximum(0.0, margin - turns)
    return float((deficit ** 2).sum()), float(turns.min())


def value_and_grad(x: np.ndarray, cfg: SearchConfig,
                   subsets: np.ndarray) -> tuple[float, np.ndarray]:
    """Analytic value and gradient of the full objective.

    Vectorized over centers (axis 0) and over 4-subsets.  This is the speed
    path that makes large-n basin-hopping feasible: scipy finite-difference
    gradients cost O(n) extra objective evals per step, which is prohibitive
    for n=16 with C(15,4)=1365 subsets.
    """
    n = cfg.n
    beta = cfg.softmin_beta
    pts = x.reshape(n, 2)

    # ---- squared distances and their gradients wrt the two endpoints ----
    diff = pts[:, None, :] - pts[None, :, :]          # (n,n,2)  p_i - p_j
    dmat = np.einsum("ijk,ijk->ij", diff, diff)        # (n,n)

    # other-index map: for each center i, the n-1 columns j != i, in order.
    other_idx = np.empty((n, n - 1), dtype=np.int64)
    for i in range(n):
        other_idx[i] = [j for j in range(n) if j != i]

    grad_pts = np.zeros((n, 2))
    eq_total = 0.0

    # weight (sensitivity) of each squared distance d_ij accumulated here, so we
    # can apply the chain rule d(d_ij)/d(p) = 2(p_i-p_j) on i and -2(...) on j.
    wd = np.zeros((n, n))  # wd[i,j] = dF_eq/d(d_ij), only j!=i used per center

    for i in range(n):
        cols = other_idx[i]                  # (n-1,)
        vals = dmat[i, cols]                 # (n-1,)
        sub = vals[subsets]                  # (S,4)
        mean = sub.mean(axis=1, keepdims=True)
        cen = sub - mean                     # (S,4)
        var = (cen ** 2).mean(axis=1)        # (S,)
        z = -beta * var
        mmax = z.max()
        ez = np.exp(z - mmax)
        denom = ez.sum()
        sm = -(mmax + math.log(denom)) / beta
        eq_total += sm
        # softmin weights w_S = softmax(-beta*var) ; d(sm)/d(var_S) = w_S
        w = ez / denom                       # (S,)
        # d(var_S)/d(vals_k) for k in subset = (2/4)*(vals_k - mean_S) = cen/2
        dvar_dsub = cen * 0.5                 # (S,4)
        contrib = (w[:, None] * dvar_dsub)    # (S,4)
        # scatter back to the n-1 distance slots
        slot = np.zeros(n - 1)
        np.add.at(slot, subsets.ravel(), contrib.ravel())
        wd[i, cols] = slot

    # chain rule: d(d_ij) = 2*(p_i - p_j) on p_i and the negative on p_j.
    # For center i, only the "i" endpoint participates in d_ij here (j ranges
    # over others), but d_ij is symmetric, so the witness point j also moves.
    for i in range(n):
        for jj, j in enumerate(other_idx[i]):
            wij = wd[i, j]
            if wij == 0.0:
                continue
            g = 2.0 * wij * (pts[i] - pts[j])
            grad_pts[i] += g
            grad_pts[j] -= g

    # ---- convexity barrier ----
    bar = 0.0
    margin = cfg.margin
    for i in range(n):
        ip1 = (i + 1) % n
        ip2 = (i + 2) % n
        a = pts[ip1] - pts[i]
        b = pts[ip2] - pts[ip1]
        t = a[0] * b[1] - a[1] * b[0]
        deficit = margin - t
        if deficit > 0:
            bar += deficit * deficit
            # d(bar_i)/d(t) = -2*deficit ; multiply by w_conv
            coef = cfg.w_conv * (-2.0 * deficit)
            # t = ax*by - ay*bx, with a=p_{i+1}-p_i, b=p_{i+2}-p_{i+1}
            # gradients wrt the three involved points:
            # dt/dp_i      = (-by,  bx)
            # dt/dp_{i+1}  = ( by - ay? ) -- compute directly below
            # Use explicit partials.
            ax, ay = a
            bx, by = b
            # dt/dax=by, dt/day=-bx, dt/dbx=-ay, dt/dby=ax
            # a depends on p_{i+1}(+1), p_i(-1); b depends on p_{i+2}(+1), p_{i+1}(-1)
            dpi = np.array([-by, bx])                    # from a: -d/dp_i
            dpi1 = np.array([by, -bx]) * 1.0             # +a part
            dpi1 = dpi1 + np.array([ay, -ax])            # -b part: -(-ay,ax)? see below
            # Recompute carefully:
            #   dt/dp_i    = -(by, -bx) = (-by, bx)
            #   dt/dp_{i+1}=  (by, -bx) - (-ay, ax) = (by + ay, -bx - ax)
            #   dt/dp_{i+2}=  (-ay, ax)
            dpi = np.array([-by, bx])
            dpi1 = np.array([by + ay, -bx - ax])
            dpi2 = np.array([-ay, ax])
            grad_pts[i] += coef * dpi
            grad_pts[ip1] += coef * dpi1
            grad_pts[ip2] += coef * dpi2
    bar *= cfg.w_conv

    # ---- scale anchor: 0.5*(std - 1)^2 ----
    mu = pts.mean(axis=0)
    cen = pts - mu
    var_all = (cen ** 2).mean()
    std = math.sqrt(var_all) if var_all > 0 else 0.0
    scale_pen = 0.5 * (std - 1.0) ** 2
    if std > 0:
        # d(std)/d(p_k) = cen_k / (n * std) ; d(scale_pen)/d std = (std-1)
        coef_s = (std - 1.0) / (n * std)
        grad_pts += coef_s * cen

    total = eq_total + bar + scale_pen
    return total, grad_pts.reshape(-1)


def make_objective(cfg: SearchConfig, subsets: np.ndarray):
    """Return F(x) (value only) for diagnostics; the optimizer uses jac."""

    def F(x: np.ndarray) -> float:
        return value_and_grad(x, cfg, subsets)[0]

    return F


# --------------------------------------------------------------------------- #
# Hard (trust-bearing) metrics on the true argmin 4-subset per center         #
# --------------------------------------------------------------------------- #
@dataclass
class HardMetrics:
    n: int
    eq_rms: float           # RMS over centers of (selected-distance spread)
    max_spread: float       # max over centers of (max-min) of selected sq dists
    max_rel_spread: float   # max over centers of spread / mean(selected)
    convexity_margin: float  # min signed consecutive turn (after orientation)
    strict_convex: bool      # full one-sided orient() check passes
    min_edge_length: float
    min_pair_distance: float
    selected_sets: list      # per center, the chosen 4 OTHER-vertex indices

    def to_json(self) -> dict:
        d = asdict(self)
        return d


def _orient(o: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def hard_metrics(x: np.ndarray, n: int) -> HardMetrics:
    pts = points_of(x, n).copy()
    # Orient counter-clockwise so "positive turn" is the convex convention.
    area2 = 0.0
    for i in range(n):
        j = (i + 1) % n
        area2 += pts[i, 0] * pts[j, 1] - pts[j, 0] * pts[i, 1]
    if area2 < 0:
        pts = pts[::-1].copy()

    dmat = all_sq_dists(pts)
    spreads = []
    rel_spreads = []
    selected = []
    for i in range(n):
        order = [j for j in range(n) if j != i]
        vals = dmat[i, order]
        best = None
        best_combo = None
        for combo in combinations(range(n - 1), 4):
            sub = vals[list(combo)]
            v = sub.max() - sub.min()
            if best is None or v < best:
                best = v
                best_combo = combo
        chosen_vals = vals[list(best_combo)]
        spreads.append(best)
        mean = chosen_vals.mean()
        rel_spreads.append(best / mean if mean > 0 else float("inf"))
        selected.append([order[k] for k in best_combo])

    spreads = np.array(spreads)
    eq_rms = float(np.sqrt((spreads ** 2).mean()))
    max_spread = float(spreads.max())
    max_rel_spread = float(max(rel_spreads))

    # consecutive turns (signed) after CCW orientation
    turns = np.empty(n)
    for i in range(n):
        a = pts[(i + 1) % n] - pts[i]
        b = pts[(i + 2) % n] - pts[(i + 1) % n]
        turns[i] = a[0] * b[1] - a[1] * b[0]
    conv_margin = float(turns.min())

    # full strict-convexity witness: every edge (i,i+1) has all other vertices
    # strictly on the left (orient > 0).
    strict = True
    min_orient = float("inf")
    for i in range(n):
        o = pts[i]
        a = pts[(i + 1) % n]
        for j in range(n):
            if j == i or j == (i + 1) % n:
                continue
            val = _orient(o, a, pts[j])
            min_orient = min(min_orient, val)
            if val <= 0:
                strict = False
    strict_convex = bool(strict and conv_margin > 0)

    # edge lengths and min pair distance (true distances, sqrt)
    edge_len = min(
        float(np.linalg.norm(pts[(i + 1) % n] - pts[i])) for i in range(n)
    )
    dmat_off = dmat + np.eye(n) * 1e18
    min_pair = float(np.sqrt(dmat_off.min()))

    return HardMetrics(
        n=n,
        eq_rms=eq_rms,
        max_spread=max_spread,
        max_rel_spread=max_rel_spread,
        convexity_margin=conv_margin,
        strict_convex=strict_convex,
        min_edge_length=edge_len,
        min_pair_distance=min_pair,
        selected_sets=selected,
    )


# --------------------------------------------------------------------------- #
# Initialization: convex starts that are NOT regular / NOT two-orbit          #
# --------------------------------------------------------------------------- #
def random_convex_start(n: int, rng: np.random.Generator) -> np.ndarray:
    """A random strictly convex polygon: random radii on jittered, sorted angles.

    This is a generic convex seed, deliberately aperiodic (random per-vertex
    radius and random angular gaps) so it is not a regular polygon, not a
    concentric two-orbit, and carries no fixed selected pattern.
    """
    gaps = rng.uniform(0.3, 1.0, size=n)
    angles = np.cumsum(gaps)
    angles = angles / angles[-1] * 2 * math.pi
    radii = rng.uniform(0.7, 1.4, size=n)
    pts = np.column_stack([radii * np.cos(angles), radii * np.sin(angles)])
    pts -= pts.mean(axis=0)
    pts /= pts.std()
    return pts.reshape(-1)


def perturb(x: np.ndarray, rng: np.random.Generator, scale: float) -> np.ndarray:
    return x + rng.normal(0.0, scale, size=x.shape)


# --------------------------------------------------------------------------- #
# Basin-hopping driver                                                        #
# --------------------------------------------------------------------------- #
def polish(x0: np.ndarray, cfg: SearchConfig, subsets: np.ndarray,
           schedule=((40.0, 30.0), (150.0, 150.0), (500.0, 600.0),
                     (1200.0, 2500.0), (3000.0, 8000.0)),
           maxiter=400) -> np.ndarray:
    """Anneal softmin temperature (beta) and convexity weight (w_conv) jointly.

    Each stage uses the analytic gradient (jac=True) with L-BFGS-B.  Annealing
    beta sharpens the dynamic 4-subset selection toward the true argmin, while
    annealing w_conv pushes the configuration into the strictly convex region.

    A final convexity-repair stage minimizes the barrier alone with a slightly
    enlarged target margin so that the reported configuration sits strictly
    inside the convex region (positive turns), not on its boundary.  This keeps
    the trust-bearing residuals honest: they describe an actually strictly
    convex polygon, not a degenerate one.
    """
    x = x0.copy()
    for beta, wc in schedule:
        local = SearchConfig(n=cfg.n, margin=cfg.margin, w_conv=wc,
                             softmin_beta=beta, seed=cfg.seed)
        res = minimize(
            value_and_grad, x, args=(local, subsets), method="L-BFGS-B",
            jac=True,
            options={"maxiter": maxiter, "ftol": 1e-13, "gtol": 1e-11},
        )
        x = res.x

    # convexity repair: if the consecutive turns are not comfortably positive,
    # take a few steps minimizing the barrier with a larger target margin while
    # the high-beta equal-distance term keeps the witnesses aligned.
    _, min_turn = _convexity_barrier(x.reshape(cfg.n, 2), cfg.n, cfg.margin)
    if min_turn < cfg.margin:
        repair = SearchConfig(n=cfg.n, margin=2.0 * cfg.margin,
                              w_conv=2.0e4, softmin_beta=3000.0, seed=cfg.seed)
        res = minimize(
            value_and_grad, x, args=(repair, subsets), method="L-BFGS-B",
            jac=True,
            options={"maxiter": 300, "ftol": 1e-13, "gtol": 1e-11},
        )
        x = res.x
    return x


def search_n(n: int, seconds: float, seed: int = 0,
             margin: float = 1e-3) -> dict:
    rng = np.random.default_rng(seed)
    cfg = SearchConfig(n=n, margin=margin, seed=seed)
    subsets = four_subsets(n - 1)
    F_eval = make_objective(SearchConfig(n=n, margin=margin, softmin_beta=600.0),
                            subsets)

    # Two trust-distinct records:
    #   best_strict  -- lowest eq_rms among configurations that pass the FULL
    #                   strict-convexity witness.  This is the trust-bearing
    #                   number: residual of an actually strictly convex polygon.
    #   best_any     -- lowest eq_rms ignoring convexity (typically a boundary
    #                   degeneration).  This is the #7-style diagnostic; a small
    #                   value here with a collapsing convexity margin is the
    #                   known failure mode, NOT a candidate.
    best_strict_x = None
    best_strict = None
    best_any_x = None
    best_any = None
    restarts = 0
    t0 = monotonic()

    # current incumbent for basin hopping
    incumbent = None
    incumbent_loss = math.inf
    stall = 0

    while monotonic() - t0 < seconds:
        restarts += 1
        if incumbent is None or stall >= 6:
            x0 = random_convex_start(n, rng)
            stall = 0
        else:
            kick = 0.05 * (1.0 + 0.5 * rng.standard_normal())
            x0 = perturb(incumbent, rng, abs(kick))

        x = polish(x0, cfg, subsets)
        loss = F_eval(x)
        hm = hard_metrics(x, n)

        # basin-hopping accept: prefer lower combined loss
        if loss < incumbent_loss - 1e-9:
            incumbent = x
            incumbent_loss = loss
            stall = 0
        else:
            stall += 1

        if best_any is None or hm.eq_rms < best_any.eq_rms:
            best_any = hm
            best_any_x = x.copy()
        if hm.strict_convex and (best_strict is None
                                 or hm.eq_rms < best_strict.eq_rms):
            best_strict = hm
            best_strict_x = x.copy()

        if monotonic() - t0 >= seconds:
            break

    elapsed = monotonic() - t0
    out = {
        "n": n,
        "ansatz": "free-cartesian + per-center free radius + dynamic 4-subset "
                  "selection (softmin-annealed) + convexity barrier + "
                  "asymmetric basin-hopping",
        "trust_label": "NUMERICAL_EVIDENCE",
        "seconds_budget": seconds,
        "elapsed_sec": elapsed,
        "restarts": restarts,
        "seed": seed,
        "margin": margin,
        "best_strict_convex": best_strict.to_json() if best_strict else None,
        "best_strict_convex_x": (best_strict_x.tolist()
                                 if best_strict_x is not None else None),
        "best_any_residual": best_any.to_json() if best_any else None,
        "best_any_residual_x": (best_any_x.tolist()
                                if best_any_x is not None else None),
    }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, nargs="+", default=[10, 12, 16])
    ap.add_argument("--seconds", type=float, default=60.0,
                    help="time budget PER n")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--margin", type=float, default=1e-3)
    ap.add_argument("--out", type=str, default=None,
                    help="optional directory to write per-n JSON runs")
    args = ap.parse_args()

    results = []
    for n in args.n:
        res = search_n(n, args.seconds, seed=args.seed, margin=args.margin)
        results.append(res)
        s = res["best_strict_convex"]
        a = res["best_any_residual"]
        if s is not None:
            print(f"n={n:3d} STRICT  restarts={res['restarts']:4d}  "
                  f"eq_rms={s['eq_rms']:.3e}  max_spread={s['max_spread']:.3e}  "
                  f"rel_spread={s['max_rel_spread']:.3e}  "
                  f"conv_margin={s['convexity_margin']:.3e}  "
                  f"min_edge={s['min_edge_length']:.3e}")
        else:
            print(f"n={n:3d} STRICT  restarts={res['restarts']:4d}  "
                  f"(no strictly convex configuration found)")
        if a is not None:
            print(f"n={n:3d} ANY     "
                  f"eq_rms={a['eq_rms']:.3e}  max_spread={a['max_spread']:.3e}  "
                  f"conv_margin={a['convexity_margin']:.3e}  "
                  f"strict_convex={a['strict_convex']}  "
                  f"(diagnostic; small here + collapsing margin = #7 mode)")
        if args.out:
            os.makedirs(args.out, exist_ok=True)
            path = os.path.join(args.out, f"c1_n{n}.json")
            with open(path, "w") as fh:
                json.dump(res, fh, indent=2)
            print(f"        wrote {path}")

    # flag any STRICTLY CONVEX candidate meeting the exactification trigger.
    # A small residual that is NOT strictly convex is the known #7 failure mode,
    # not a candidate.
    for res in results:
        s = res["best_strict_convex"]
        if s is None:
            continue
        if (s["max_spread"] < 1e-10 and s["convexity_margin"] > 1e-3
                and s["min_edge_length"] > 1e-3 and s["strict_convex"]):
            print(f"\n*** EXACTIFICATION-TRIGGER candidate at n={res['n']} "
                  f"(max_spread {s['max_spread']:.2e}). NOT a counterexample; "
                  f"route to docs/exactification-plan.md and save coords. ***")


if __name__ == "__main__":
    main()
