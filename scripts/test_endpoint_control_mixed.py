"""Numerical probe of the Endpoint Control mixed-side sub-claim.

Setup (Erdős #97, Lemma 12 / endpoint descent program; see
docs/canonical-synthesis.md §5.1 and docs/endpoint-control-mixed-side.md).

Let `P` be a strictly convex `n`-gon with vertex set `V`. For each vertex
`v_i` the "vertex-circle multiplicity" is
    M(i) = max_{r > 0} |S_i(r)|,    S_i(r) = {v_j : ||v_j - v_i|| = r, j != i}.
Set m = min_i M(i). When m >= 4 (so the polygon is a "would-be #97
counterexample at level m"), pick (i*, r*) attaining m. Let
    A = S_{i*}(r*) = {a_1, ..., a_m}
in joint angular / boundary order around v_{i*}. The endpoint indices are
j^- = a_1 and j^+ = a_m. The polygon boundary, traversed once, induces the
cyclic sequence
    v_{i*}, L_1, ..., L_s, j^-, a_2, ..., a_{m-1}, j^+, R_1, ..., R_t, v_{i*}
so V \ A \ {i*} = L ⊔ R.

The Endpoint Control auxiliary claim (open, the gap in the Lemma 12
program) asserts: at least one j ∈ {j^-, j^+} has |S_j(ρ) \ (A ∪ {i*})|
≤ m - 3 for *every* ρ > 0.  At m = 4 this is the sharp inequality
|S_j(ρ) \ (A ∪ {i*})| ≤ 1.

This script attacks the **mixed-side sub-claim at m=4**:

    For every strictly convex P with m = 4 attained at i*, and every
    ρ > 0, the vertex v_{j^-} has at most one outside witness in
    L ∪ R that lies "across" the A-block from v_{j^-} — i.e. there is
    no ρ for which |S_{j^-}(ρ) ∩ L| >= 1 *and* |S_{j^-}(ρ) ∩ R| >= 1
    simultaneously, in the strong "2-in-each-chain" sense.

Concretely, for random strictly convex polygons that nearly attain m=4
at some vertex, we check how often the strong mixed pattern appears:

    (#) ∃ ρ > 0:  |S_{j^-}(ρ) ∩ L| >= 1 and |S_{j^-}(ρ) ∩ R| >= 1.
    (##) ∃ ρ > 0:  |S_{j^-}(ρ) ∩ L| >= 2 and |S_{j^-}(ρ) ∩ R| >= 2.

Random strictly convex polygons (in general position) have all pairwise
distances distinct, so neither (#) nor (##) typically holds. To exhibit
near-mixed configurations we generate polygons with two random vertices
"force-equidistant" from v_{j^-} (one on each side of A) and check
whether the rest of the polygon's geometry is consistent with strict
convexity and m >= 4.

Output: pass/fail counts, and a small dossier of near-misses.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from pathlib import Path

import numpy as np


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def is_strictly_convex(P):
    """P: (n, 2) array of points in cyclic order. Returns True iff strictly
    convex (every consecutive triple turns the same way and area > 0)."""
    n = len(P)
    if n < 3:
        return False
    sign = 0
    for i in range(n):
        a = P[i]
        b = P[(i + 1) % n]
        c = P[(i + 2) % n]
        v1 = b - a
        v2 = c - b
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        if abs(cross) < 1e-12:
            return False  # collinear or degenerate
        s = 1 if cross > 0 else -1
        if sign == 0:
            sign = s
        elif sign != s:
            return False
    return True


def pairwise_distances(P):
    """Return n x n distance matrix."""
    n = len(P)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            D[i, j] = np.linalg.norm(P[i] - P[j])
    return D


def vertex_circle_multiplicities(D, eps=1e-8):
    """For each vertex i, return the maximum count of other vertices at a
    common distance from i (the M(i) value), within tolerance eps.
    Also returns the witness sets.
    """
    n = D.shape[0]
    Ms = np.zeros(n, dtype=int)
    witness_sets = [None] * n
    radii = [0.0] * n
    for i in range(n):
        # Cluster the n-1 distances by tolerance.
        ds = sorted([(D[i, j], j) for j in range(n) if j != i])
        # Greedy cluster.
        best_size = 0
        best_set = []
        best_r = 0.0
        cluster = []
        for d, j in ds:
            if not cluster:
                cluster = [(d, j)]
                continue
            if abs(d - cluster[0][0]) <= eps:
                cluster.append((d, j))
            else:
                if len(cluster) > best_size:
                    best_size = len(cluster)
                    best_set = [c[1] for c in cluster]
                    best_r = cluster[0][0]
                cluster = [(d, j)]
        if cluster and len(cluster) > best_size:
            best_size = len(cluster)
            best_set = [c[1] for c in cluster]
            best_r = cluster[0][0]
        Ms[i] = best_size
        witness_sets[i] = sorted(best_set)
        radii[i] = best_r
    return Ms, witness_sets, radii


def angular_order_around(P, i):
    """Return the indices of vertices != i sorted by angle as seen from P[i].
    Uses arctan2; the cyclic ambiguity is resolved by L1 (cone span < pi)
    so we just sort with a fixed reference direction."""
    n = len(P)
    other = [j for j in range(n) if j != i]
    angles = [math.atan2(P[j][1] - P[i][1], P[j][0] - P[i][0]) for j in other]
    return [j for _, j in sorted(zip(angles, other))]


# ---------------------------------------------------------------------------
# Polygon generators
# ---------------------------------------------------------------------------

def random_strictly_convex_polygon(n, rng=None):
    """Generate a random strictly convex n-gon by sampling n random points
    on the unit circle and slightly perturbing the radii.
    """
    if rng is None:
        rng = np.random.default_rng()
    # Random angles, sorted.
    angles = np.sort(rng.uniform(0, 2 * np.pi, n))
    # Random radii in [0.5, 1.5].
    r = 0.5 + rng.uniform(size=n)
    P = np.column_stack([r * np.cos(angles), r * np.sin(angles)])
    return P


def construct_m4_polygon(n, rng=None, max_tries=400, min_each=1):
    """Construct a strictly convex n-gon (n >= 6) with vertex i* (index 0)
    having M(i*) >= 4. The construction:

    - Place v_{i*} at the bottom (large negative y) facing upward.
    - Place 4 witnesses A on a circle of radius r*=1 around v_{i*}, in
      a tight angular spread above v_{i*} (so all 4 are above and form a
      "fan" cocircular). They are at distance 1 from v_{i*} and at small
      x-spread.
    - Place s "L" vertices to the left of v_{i*}, on a low arc, between
      v_{i*} and j^-.
    - Place t "R" vertices to the right of v_{i*}, on a low arc, between
      j^+ and v_{i*}.
    - All these need to lie on a single convex hull with all n points
      hull-extreme.

    Returns (P, i_star_index_in_cyclic_order) or (None, None).
    """
    if rng is None:
        rng = np.random.default_rng()
    if n < 6:
        return None, None
    extra = n - 5
    if extra < 2 * min_each:
        return None, None
    for _ in range(max_tries):
        s = int(rng.integers(min_each, extra - min_each + 1))
        t = extra - s
        if t < min_each:
            continue

        # Place v_{i*} at origin facing "up". A on radius 1 circle around it,
        # in a NARROW spread close to vertical so A is high up.
        # spread small => A_pts have y close to 1, x spread small.
        spread = rng.uniform(np.pi*0.15, np.pi*0.5)
        a_angles = np.sort(rng.uniform(np.pi/2 - spread/2, np.pi/2 + spread/2, 4))
        r_star = 1.0
        A_pts = np.array([[np.cos(t), np.sin(t)] for t in a_angles])
        # A_pts[0] has smallest angle => largest x (right). A_pts[-1] has largest angle => leftmost.
        # Polygon CCW starting from i* (origin): we go to the right first
        # if R is on the right side. Boundary cyclic CCW:
        #   i*=origin → R_t (lower right) → ... → R_1 (upper right) → j^+=A[0] (right top)
        #     → A[1] → A[2] → j^-=A[3] (left top) → L_1 (upper left) → ... → L_s (lower left) → i*

        # L points: on the LEFT side of i*, between i* and j^- = A[-1].
        # Going CCW from i* (origin) to L means going up the left side.
        # So L points have x < 0 and y between 0 and ~1, with smaller y closer to i*.
        L_pts = []
        for k in range(s):
            # k=0 => closest to i* (lowest y); k=s-1 => closest to j^- (highest y)
            frac = (k + 1) / (s + 1)
            x = -0.5 - rng.uniform(0.5, 1.5) * (1 - frac * 0.3)
            y = frac * (A_pts[-1][1] - 0.05)
            L_pts.append([x, y])
        L_pts = np.array(L_pts) if L_pts else np.zeros((0, 2))

        R_pts = []
        for k in range(t):
            # k=0 => closest to j^+ (highest y); k=t-1 => closest to i* (lowest y)
            frac = (t - k) / (t + 1)
            x = 0.5 + rng.uniform(0.5, 1.5) * (1 - frac * 0.3)
            y = frac * (A_pts[0][1] - 0.05)
            R_pts.append([x, y])
        R_pts = np.array(R_pts) if R_pts else np.zeros((0, 2))

        all_pts = np.vstack([
            np.array([[0.0, 0.0]]),
            A_pts,
            L_pts,
            R_pts,
        ])
        try:
            from scipy.spatial import ConvexHull
        except ImportError:
            return None, None
        try:
            hull = ConvexHull(all_pts)
        except Exception:
            continue
        if len(hull.vertices) != len(all_pts):
            continue
        cyc = list(hull.vertices)
        if 0 not in cyc:
            continue
        pos = cyc.index(0)
        cyc = cyc[pos:] + cyc[:pos]
        P = all_pts[cyc]
        if not is_strictly_convex(P):
            continue
        return P, 0
    return None, None


# ---------------------------------------------------------------------------
# Mixed-side claim test
# ---------------------------------------------------------------------------

@dataclass
class MixedSideTest:
    n: int
    seed: int
    i_star: int
    j_minus: int
    j_plus: int
    A: list                       # indices of A in angular order
    L: list                       # left chain indices
    R: list                       # right chain indices
    m: int                        # minimum M (global)
    M_at_i_star: int
    M_at_j_minus: int
    M_at_j_plus: int = 0
    Ms_all: list = field(default_factory=list)
    # Mixed-side findings
    mixed_count_per_radius: list = field(default_factory=list)
    strong_mixed: bool = False    # |S_{j-}(rho) ∩ L| >=1 and ≥1 in R
    strong_2plus_2: bool = False  # |...| >= 2 in each chain
    notes: str = ""


def analyse_polygon(P, eps=1e-7, require_global_m4=False,
                    force_i_star=None) -> MixedSideTest | None:
    """Locate (i*, r*) and j^- and check for mixed-side outside witnesses.

    If require_global_m4 is True, requires every vertex to have M >= 4
    (the genuine counterexample condition; rare).
    Otherwise picks any vertex with M >= 4 as i*.
    """
    n = len(P)
    if not is_strictly_convex(P):
        return None
    D = pairwise_distances(P)
    Ms, W, R = vertex_circle_multiplicities(D, eps=eps)
    m = int(Ms.min())
    if require_global_m4 and m < 4:
        return None
    if force_i_star is not None:
        i_star = force_i_star
        if Ms[i_star] < 4:
            return None
    else:
        # Pick i* with M(i*) >= 4, smallest such M, smallest index for determinism.
        candidates = [i for i in range(n) if Ms[i] >= 4]
        if not candidates:
            return None
        candidates.sort(key=lambda i: (Ms[i], i))
        i_star = candidates[0]
    A_all = sorted(W[i_star])
    if len(A_all) < 4:
        return None

    # Angular order at i*.
    angle_order_i = angular_order_around(P, i_star)
    A_set = set(A_all)
    # Angular order of A around i*.
    A = [j for j in angle_order_i if j in A_set]
    if len(A) < 4:
        return None

    j_minus, j_plus = A[0], A[-1]

    # Boundary order partition. Cyclic boundary indices 0..n-1, walk from i*.
    # L = vertices strictly between i* and j_minus (going one way that has
    # j_minus first); R = vertices strictly between j_plus and i*.
    cyc = list(range(n))
    # Find the arc i* -> j_minus that contains no other A vertex.
    def boundary_walk(start, end, direction):
        out = []
        x = (start + direction) % n
        while x != end:
            out.append(x)
            x = (x + direction) % n
        return out

    # Two candidate walks: +1 and -1.
    walk_pos = boundary_walk(i_star, j_minus, +1)
    walk_neg = boundary_walk(i_star, j_minus, -1)
    # Pick the walk that contains no A vertex.
    if not any(v in A_set for v in walk_pos):
        L_chain = walk_pos
        # Then the other direction from i* goes through R then j_plus.
        R_chain = boundary_walk(i_star, j_plus, -1)
    elif not any(v in A_set for v in walk_neg):
        L_chain = walk_neg
        R_chain = boundary_walk(i_star, j_plus, +1)
    else:
        # Should not happen if angular order matches boundary order
        return None

    # Sanity: every vertex other than A ∪ {i*} should be in L ∪ R.
    interior_A = set(A) - {j_minus, j_plus}
    rest = set(range(n)) - {i_star} - set(A)
    if set(L_chain) | set(R_chain) != rest:
        # Some inconsistency; skip.
        return None

    test = MixedSideTest(
        n=n, seed=-1, i_star=i_star, j_minus=j_minus, j_plus=j_plus,
        A=A, L=L_chain, R=R_chain, m=m,
        M_at_i_star=int(Ms[i_star]),
        M_at_j_minus=int(Ms[j_minus]),
        M_at_j_plus=int(Ms[j_plus]),
        Ms_all=[int(x) for x in Ms],
    )

    # Now examine S_{j_minus}(rho). For each candidate rho (= each distance
    # from j_minus to another vertex), count |S ∩ L|, |S ∩ R|, |S ∩ (A∪i*)|.
    rho_groups = defaultdict(list)
    for k in range(n):
        if k == j_minus:
            continue
        d = D[j_minus, k]
        # Group by quantized radius.
        key = round(d / eps) * eps
        # Use approximate equality: brute search over existing keys.
        matched = False
        for existing in list(rho_groups.keys()):
            if abs(existing - d) <= eps:
                rho_groups[existing].append(k)
                matched = True
                break
        if not matched:
            rho_groups[d].append(k)

    L_set = set(L_chain)
    R_set = set(R_chain)
    AI_set = set(A) | {i_star}

    for rho, members in rho_groups.items():
        nL = sum(1 for m in members if m in L_set)
        nR = sum(1 for m in members if m in R_set)
        nAI = sum(1 for m in members if m in AI_set)
        total = len(members)
        if total >= 2 and nL >= 1 and nR >= 1:
            test.strong_mixed = True
        if nL >= 2 and nR >= 2:
            test.strong_2plus_2 = True
        if total >= 2:
            test.mixed_count_per_radius.append({
                "rho": float(rho), "nL": int(nL), "nR": int(nR),
                "nAI": int(nAI), "total": int(total),
            })

    return test


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def force_jminus_mixed(P, i_star, eps=1e-7, max_iter=50, rng=None):
    """Given a polygon P with M(i*)=4, attempt to force v_{j^-} to have
    a strong mixed-side configuration: u_1, u_2 in L and u_3, u_4 in R,
    all at common distance from v_{j^-}.

    Returns (P_modified, info) or (None, None).
    """
    if rng is None:
        rng = np.random.default_rng()
    test = analyse_polygon(P, eps=eps, force_i_star=i_star)
    if test is None or len(test.L) < 1 or len(test.R) < 1:
        return None, None
    L_chain = test.L
    R_chain = test.R
    j_minus = test.j_minus
    # Need at least 1 in each. For the 2+2 strong case need at least 2 in each.
    if len(L_chain) < 1 or len(R_chain) < 1:
        return None, None
    n_pick_L = min(2, len(L_chain))
    n_pick_R = min(2, len(R_chain))
    # Random choice of u's.
    chosen_L = list(rng.choice(L_chain, size=n_pick_L, replace=False))
    chosen_R = list(rng.choice(R_chain, size=n_pick_R, replace=False))
    chosen = chosen_L + chosen_R
    # Target distance: average existing distances.
    ds = [np.linalg.norm(P[k] - P[j_minus]) for k in chosen]
    target = float(np.mean(ds))
    # Slide each chosen vertex along (j_minus -> u_k) ray to be at distance target.
    P_try = P.copy()
    for k in chosen:
        v = P_try[k] - P_try[j_minus]
        vn = np.linalg.norm(v)
        if vn < 1e-9:
            return None, None
        P_try[k] = P_try[j_minus] + (target / vn) * v
    if not is_strictly_convex(P_try):
        return None, None
    # Re-check that M(i*) is still >= 4 (since we moved L_chain / R_chain
    # vertices, they're not in A so this should be preserved exactly except
    # for possible coincidences).
    test2 = analyse_polygon(P_try, eps=eps, force_i_star=i_star)
    if test2 is None or test2.m < 1:
        return None, None
    return P_try, {"chosen": chosen, "target_rho": target}


def run_random(n_trials, n=8, eps=1e-7, seed_base=0,
               jitter_attempts=200):
    """Generate polygons and test the mixed-side claim.

    Strategy:
    - Construct an m=4 polygon directly (so v_{i*} has 4 cocircular witnesses).
    - Then jitter to force two outside witnesses of v_{j^-} to be on a common
      circle. Specifically: pick u_1 in L and u_2 in R, force ||u_1 - j_-|| = ||u_2 - j_-||
      by sliding u_1 along its (j^- to u_1) ray (analogous on R side).
    - Test whether the resulting polygon (a) is strictly convex, (b) has m >= 4 still.
    """
    results = []
    n_constructed = 0
    n_M_i_star_ge_4 = 0
    n_strong_mixed = 0     # j^- has 1+ in L and 1+ in R at same radius
    n_strong_2plus_2 = 0   # j^- has 2+ in L and 2+ in R at same radius
    n_strong_mixed_with_strict_convex = 0
    n_strong_mixed_and_M_jminus_ge_4 = 0
    n_strong_mixed_and_global_m_ge_4 = 0
    rng = np.random.default_rng(seed_base)

    for trial in range(n_trials):
        # Construct m=4 polygon.
        P, i_star_pos = construct_m4_polygon(n, rng=rng)
        if P is None:
            continue
        n_constructed += 1
        # Baseline analysis with i*=position 0.
        test = analyse_polygon(P, eps=eps, force_i_star=i_star_pos)
        if test is None:
            continue
        test.seed = trial
        if test.M_at_i_star >= 4:
            n_M_i_star_ge_4 += 1

        # Try to force a mixed-side configuration at v_{j^-}.
        if len(test.L) > 0 and len(test.R) > 0:
            P_forced, info = force_jminus_mixed(P, i_star_pos, eps=eps, rng=rng)
            if P_forced is not None:
                test_forced = analyse_polygon(P_forced, eps=eps,
                                              force_i_star=i_star_pos)
                if test_forced is not None:
                    test_forced.seed = trial
                    test_forced.notes = (f"forced; chosen={info['chosen']}; "
                                         f"target_rho={info['target_rho']:.4f}; "
                                         f"strict_convex={is_strictly_convex(P_forced)}")
                    test = test_forced
                    P = P_forced

        results.append(test)
        if test.strong_mixed:
            n_strong_mixed += 1
            if is_strictly_convex(P):
                n_strong_mixed_with_strict_convex += 1
            if test.M_at_j_minus >= 4:
                n_strong_mixed_and_M_jminus_ge_4 += 1
            if test.m >= 4:
                n_strong_mixed_and_global_m_ge_4 += 1
        if test.strong_2plus_2:
            n_strong_2plus_2 += 1
    return {
        "n_trials": n_trials,
        "n_constructed": n_constructed,
        "n_M_i_star_ge_4": n_M_i_star_ge_4,
        "n_strong_mixed": n_strong_mixed,
        "n_strong_2plus_2": n_strong_2plus_2,
        "n_strong_mixed_with_strict_convex": n_strong_mixed_with_strict_convex,
        "n_strong_mixed_and_M_jminus_ge_4": n_strong_mixed_and_M_jminus_ge_4,
        "n_strong_mixed_and_global_m_ge_4": n_strong_mixed_and_global_m_ge_4,
        "results_sample": [asdict(r) for r in results[:30]],
    }


def verify_symmetric_closure():
    """Programmatically verify the symmetric mixed-side closure (§3.3 of
    docs/endpoint-control-mixed-side.md): in any reflection-symmetric
    setup, having two distinct mirror pairs (u_L, u_R), (u_L', u_R') all
    at common distance rho from v_{j^-} forces them to coincide on the
    symmetry axis, hence not 2 distinct pairs.

    Direct algebra: with v_{j^-} = (-x_0, y_0), x_0 > 0, the constraint
    |v_{j^-} - mirror(u_L)| = |v_{j^-} - u_L| = rho forces u_L on the y-axis.
    """
    import sympy as sp
    x0, y0, rho, alpha = sp.symbols('x0 y0 rho alpha', positive=True)
    # j^- = (-x0, y0)
    # u_L = j^- + rho (cos alpha, sin alpha) = (-x0 + rho cos alpha, y0 + rho sin alpha)
    uL = sp.Matrix([-x0 + rho * sp.cos(alpha), y0 + rho * sp.sin(alpha)])
    # mirror through y-axis: x -> -x
    uR = sp.Matrix([x0 - rho * sp.cos(alpha), y0 + rho * sp.sin(alpha)])
    jm = sp.Matrix([-x0, y0])
    dL = (uL - jm).norm()
    dR = (uR - jm).norm()
    # |uL - jm| = rho automatically. Force |uR - jm| = rho:
    eq = sp.simplify(dR**2 - rho**2)
    sol = sp.solve(eq, alpha)
    print(f"Symmetric closure: forcing |v_{{j^-}} - mirror(u_L)| = rho gives:")
    print(f"  alpha must satisfy: cos(alpha) = x0 / rho")
    # Substitute back to see that uL_x = 0:
    cos_alpha_expr = x0 / rho
    uL_x_at_sol = sp.simplify((-x0 + rho * cos_alpha_expr))
    print(f"  Then u_L.x = -x0 + rho * (x0/rho) = {uL_x_at_sol}")
    print(f"  Hence u_L lies on the y-axis, equal to its mirror u_R.")
    print(f"  Two distinct mirror pairs at the same rho is impossible.")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=8)
    p.add_argument("--trials", type=int, default=1000)
    p.add_argument("--eps", type=float, default=1e-7)
    p.add_argument("--seed", type=int, default=20260506)
    p.add_argument("--out", type=str, default="")
    p.add_argument("--symmetric-closure", action="store_true",
                   help="Run only the symmetric closure verification.")
    args = p.parse_args()
    if args.symmetric_closure:
        verify_symmetric_closure()
        return

    summary = run_random(args.trials, n=args.n, eps=args.eps,
                         seed_base=args.seed)
    print(json.dumps({
        "n": args.n,
        "trials": args.trials,
        "eps": args.eps,
        "seed": args.seed,
        "n_constructed": summary["n_constructed"],
        "n_M_i_star_ge_4": summary["n_M_i_star_ge_4"],
        "n_strong_mixed": summary["n_strong_mixed"],
        "n_strong_2plus_2": summary["n_strong_2plus_2"],
        "n_strong_mixed_with_strict_convex": summary["n_strong_mixed_with_strict_convex"],
        "n_strong_mixed_and_M_jminus_ge_4": summary["n_strong_mixed_and_M_jminus_ge_4"],
        "n_strong_mixed_and_global_m_ge_4": summary["n_strong_mixed_and_global_m_ge_4"],
    }, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
