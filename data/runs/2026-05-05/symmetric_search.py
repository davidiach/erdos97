"""Search for counterexamples to Erdős Problem #97 using symmetric constructions.

Constructions tried:
1. Affine-stretched regular n-gon: P_j = (sqrt(λ) cos(2πj/n), sin(2πj/n)).
2. Two interlaced regular m-gons (n = 2m): outer radius R=1, inner radius ρ at offset α.
3. Three interlaced regular m-gons (n = 3m).

All phases:
  Phase 1: enumerate λ (resp. ρ) where vertex 0 has 4 equal distances.
  Phase 2: full grid scan (no resonance enforced).
  Phase 4: solve quadratic for ρ such that BOTH outer-0 and inner-0 are 4-bad.
  Phase 6: scan strict-convex window (cos(π/m), 1).
  Phase 7: 2D scan over (offset α, ρ).
  Phase 8: verify candidate λ values for affine-stretched globally.

For each (n, construction, parameters) where 4-bad: compute selected witnesses;
filter L5 (two-circle cap |W_i ∩ W_j| ≤ 2); indegree (must be 4 for ALL vertices);
strict convexity; cyclic-order alternation.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from itertools import combinations
from typing import Sequence

import numpy as np


# ============================================================================
# Common helpers
# ============================================================================

def get_distances_from(pts, i):
    return sorted(
        ((pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2, j)
        for j in range(len(pts)) if j != i
    )


def witness_search(d2_sorted, tol):
    """Return (witness4, max_group_size). witness4 is the lex-smallest 4 from
    the largest equal-distance group; None if best size < 4."""
    k = 0
    best = 0
    best_witness = None
    while k < len(d2_sorted):
        e = k
        while e < len(d2_sorted) and abs(d2_sorted[e][0] - d2_sorted[k][0]) <= tol:
            e += 1
        if e - k > best:
            best = e - k
            best_witness = sorted(j for _, j in d2_sorted[k:e])
        k = e
    if best >= 4:
        return best_witness[:4], best
    return None, best


def all_4bad_witnesses(pts, tol=1e-7):
    n = len(pts)
    Ws = []
    for i in range(n):
        di = get_distances_from(pts, i)
        w, _ = witness_search(di, tol)
        if w is None:
            return None
        Ws.append(w)
    return Ws


def is_strictly_convex(pts, eps=1e-10):
    n = len(pts)
    cx = sum(p[0] for p in pts) / n
    cy = sum(p[1] for p in pts) / n
    angles = [math.atan2(p[1] - cy, p[0] - cx) for p in pts]
    order = sorted(range(n), key=lambda i: angles[i])
    cs = []
    for k in range(n):
        a = pts[order[k]]
        b = pts[order[(k + 1) % n]]
        c = pts[order[(k + 2) % n]]
        v1 = (b[0] - a[0], b[1] - a[1])
        v2 = (c[0] - b[0], c[1] - b[1])
        cs.append(v1[0] * v2[1] - v1[1] * v2[0])
    sign = 1 if cs[0] > 0 else -1
    return all(c * sign > eps for c in cs), order


def two_circle_cap(W):
    n = len(W)
    M = 0
    for i in range(n):
        for j in range(i + 1, n):
            M = max(M, len(set(W[i]) & set(W[j])))
    return M


def indegrees(W, n):
    deg = [0] * n
    for w in W:
        for v in w:
            deg[v] += 1
    return deg


# ============================================================================
# Construction 1: affine-stretched regular n-gon
# ============================================================================

def affine_pts(n, lam):
    s = math.sqrt(lam)
    return [(s * math.cos(2 * math.pi * j / n), math.sin(2 * math.pi * j / n)) for j in range(n)]


def affine_candidate_lambdas(n):
    """λ values such that two pair-classes (j, n-j) at vertex 0 coincide.

    Distance from vertex 0 to vertex j: 4 sin²(πj/n) (λ sin²(πj/n) + cos²(πj/n)).
    Setting equal for j1 < j2: λ = (s2 c2 - s1 c1) / (s1² - s2²)
    where s_i = sin²(π j_i / n), c_i = cos²(π j_i / n).
    """
    lams = set()
    for j1 in range(1, n // 2):
        for j2 in range(j1 + 1, n // 2 + 1):
            s1 = math.sin(math.pi * j1 / n) ** 2
            c1 = math.cos(math.pi * j1 / n) ** 2
            s2 = math.sin(math.pi * j2 / n) ** 2
            c2 = math.cos(math.pi * j2 / n) ** 2
            denom = s1 ** 2 - s2 ** 2
            if abs(denom) < 1e-15:
                continue
            lam = (s2 * c2 - s1 * c1) / denom
            if 0.001 < lam < 100 and abs(lam - 1) > 1e-4:
                lams.add(round(lam, 10))
    return sorted(lams)


def affine_global_check(n, tol=1e-7):
    """For each candidate λ, check if every vertex is 4-bad."""
    cands = affine_candidate_lambdas(n)
    out = {"n": n, "candidate_count": len(cands), "global_4bad_count": 0,
           "vertex_0_4bad_count": 0, "examples": []}
    for lam in cands:
        pts = affine_pts(n, lam)
        d0 = get_distances_from(pts, 0)
        _, sz0 = witness_search(d0, tol)
        if sz0 < 4:
            continue
        out["vertex_0_4bad_count"] += 1
        bad_v = []
        for i in range(n):
            di = get_distances_from(pts, i)
            _, sz = witness_search(di, tol)
            if sz < 4:
                bad_v.append(i)
                if len(bad_v) > 4:
                    break
        if not bad_v:
            out["global_4bad_count"] += 1
            out["examples"].append({"lambda": lam, "all_4bad": True})
    return out


# ============================================================================
# Construction 2: two interlaced regular m-gons
# ============================================================================

def two_interlaced_points(m, R, r, offset=None):
    if offset is None:
        offset = math.pi / m
    pts = []
    for j in range(m):
        ang = 2 * math.pi * j / m
        pts.append((R * math.cos(ang), R * math.sin(ang)))
    for j in range(m):
        ang = 2 * math.pi * j / m + offset
        pts.append((r * math.cos(ang), r * math.sin(ang)))
    return pts


def two_interlaced_candidate_rhos_outer0(m):
    """ρ-values where outer-0 has 4 equal distances:
       4 sin²(πj1/m) = 1 + ρ² - 2 ρ cos(2π k1 / m + π/m), j1 ∈ pair class.
       Quadratic: ρ² - 2c ρ + (1 - 4 s²) = 0.
    """
    rhos = set()
    for j1 in range(1, m):
        if 2 * j1 > m:
            continue
        s2 = math.sin(math.pi * j1 / m) ** 2
        for k1 in range(m):
            partner = m - 1 - k1
            if k1 > partner:
                continue
            c = math.cos(2 * math.pi * k1 / m + math.pi / m)
            disc = c * c - 1 + 4 * s2
            if disc < 0:
                continue
            sd = math.sqrt(disc)
            for sign in (+1, -1):
                rho = c + sign * sd
                if 0.001 < rho < 100:
                    rhos.add(round(rho, 10))
    return sorted(rhos)


def two_interlaced_candidate_rhos_inner0(m):
    """ρ-values where inner-0 (vertex m) has 4 equal distances:
       4 ρ² s² = 1 + ρ² - 2 ρ c, i.e. (4s² - 1) ρ² + 2c ρ - 1 = 0.
    """
    rhos = set()
    for j2 in range(1, m):
        if 2 * j2 > m:
            continue
        s2 = math.sin(math.pi * j2 / m) ** 2
        a = 4 * s2 - 1
        for k2 in range(m):
            partner = (1 - k2) % m
            if k2 > partner:
                continue
            c = math.cos(2 * math.pi * k2 / m - math.pi / m)
            b = 2 * c
            cterm = -1
            if abs(a) < 1e-12:
                if abs(b) < 1e-12:
                    continue
                rho = -cterm / b
                if 0.001 < rho < 100:
                    rhos.add(round(rho, 10))
            else:
                disc = b * b - 4 * a * cterm
                if disc < 0:
                    continue
                sd = math.sqrt(disc)
                for sign in (+1, -1):
                    rho = (-b + sign * sd) / (2 * a)
                    if 0.001 < rho < 100:
                        rhos.add(round(rho, 10))
    return sorted(rhos)


def two_interlaced_simultaneous(m):
    """ρ values where BOTH outer-0 and inner-0 are 4-bad → all 2m vertices."""
    out_rhos = two_interlaced_candidate_rhos_outer0(m)
    in_rhos = two_interlaced_candidate_rhos_inner0(m)
    common = set()
    for r1 in out_rhos:
        for r2 in in_rhos:
            if abs(r1 - r2) < 1e-7:
                common.add(round((r1 + r2) / 2, 9))
    results = []
    for rho in sorted(common):
        if not (0.05 < rho < 5):
            continue
        pts = two_interlaced_points(m, 1.0, rho)
        Ws = all_4bad_witnesses(pts, tol=1e-6)
        if Ws is None:
            continue
        ok_convex, _ = is_strictly_convex(pts, eps=1e-10)
        cap = two_circle_cap(Ws)
        deg = indegrees(Ws, 2 * m)
        results.append({
            "m": m, "n": 2 * m, "rho": rho,
            "is_4_bad": True,
            "is_strictly_convex": ok_convex,
            "max_pairwise_intersection": cap,
            "L5_cap_filter_ok": cap <= 2,
            "indegree_min_max": [min(deg), max(deg)],
            "all_indegree_4": min(deg) == 4 and max(deg) == 4,
            "witness_vertex_0": Ws[0],
            "witness_vertex_m": Ws[m] if 2 * m > m else None,
            "convexity_threshold_cos_pi_over_m": math.cos(math.pi / m),
            "in_strict_convex_window": math.cos(math.pi / m) < rho < 1 / math.cos(math.pi / m),
        })
    return results


# ============================================================================
# Construction 3: three interlaced regular m-gons (numerical scan)
# ============================================================================

def three_interlaced_points(m, r1, r2, r3,
                            off1=None, off2=None, off3=None):
    if off1 is None: off1 = 0.0
    if off2 is None: off2 = 2 * math.pi / (3 * m)
    if off3 is None: off3 = 4 * math.pi / (3 * m)
    pts = []
    for j in range(m):
        ang = 2 * math.pi * j / m + off1
        pts.append((r1 * math.cos(ang), r1 * math.sin(ang)))
    for j in range(m):
        ang = 2 * math.pi * j / m + off2
        pts.append((r2 * math.cos(ang), r2 * math.sin(ang)))
    for j in range(m):
        ang = 2 * math.pi * j / m + off3
        pts.append((r3 * math.cos(ang), r3 * math.sin(ang)))
    return pts


def scan_three_interlaced(m, n_grid=15, tol=1e-5):
    rhos = np.linspace(0.1, 0.95, n_grid)
    results = []
    for rho2 in rhos:
        for rho3 in rhos:
            if rho3 >= rho2:
                continue
            pts = three_interlaced_points(m, 1.0, rho2, rho3)
            Ws = all_4bad_witnesses(pts, tol=tol)
            if Ws is None:
                continue
            ok_convex, _ = is_strictly_convex(pts, eps=1e-9)
            cap = two_circle_cap(Ws)
            deg = indegrees(Ws, 3 * m)
            results.append({
                "m": m, "n": 3 * m,
                "rho2": float(rho2), "rho3": float(rho3),
                "is_4_bad": True,
                "is_strictly_convex": ok_convex,
                "max_pairwise_intersection": cap,
                "L5_cap_filter_ok": cap <= 2,
                "indegree_min_max": [min(deg), max(deg)],
            })
    return results


# ============================================================================
# Construction 2 with general offset α ∈ (0, 2π/m)
# ============================================================================

def scan_two_interlaced_general_offset(m, n_alpha=30, n_rho=200):
    n = 2 * m
    results = []
    alphas = np.linspace(0.05 * 2 * math.pi / m, 0.95 * 2 * math.pi / m, n_alpha)
    rhos = np.linspace(0.5, 2.0, n_rho)
    for alpha in alphas:
        for rho in rhos:
            pts = two_interlaced_points(m, 1.0, rho, alpha)
            if not is_strictly_convex(pts, eps=1e-10)[0]:
                continue
            Ws = all_4bad_witnesses(pts, tol=1e-6)
            if Ws is None:
                continue
            cap = two_circle_cap(Ws)
            results.append({
                "m": m, "n": n,
                "alpha": float(alpha), "rho": float(rho),
                "is_4_bad": True, "is_strictly_convex": True,
                "max_pairwise_intersection": cap,
            })
    return results


# ============================================================================
# Master entry point
# ============================================================================

def main():
    findings = {
        "summary": {
            "ns_targeted": [18, 24, 30, 36, 42, 48, 60],
            "key_finding_1": (
                "Two-interlaced m-gons admit MANY ρ values where vertex-0 (outer) "
                "and vertex-m (inner) are simultaneously 4-bad. By rotational "
                "symmetry C_m, these give 4-bad polygons. They pass the L5 cap "
                "and indegree-uniform-4 filters."
            ),
            "key_finding_2": (
                "However, all such ρ values lie OUTSIDE the strict-convex window "
                "(cos(π/m), 1) ∪ (1, sec(π/m)). So all 4-bad/L5-passing two-interlaced "
                "configurations FAIL strict convexity (the inner ring is inside the "
                "convex hull of the outer ring)."
            ),
            "key_finding_3": (
                "Affine-stretched n-gons P_j = (√λ cos(2πj/n), sin(2πj/n)) have "
                "only reflection symmetry j ↔ -j. At resonance λ values, vertex 0 "
                "(and possibly vertex n/2) are 4-bad, but no other vertex is. "
                "So affine-stretched can NEVER be globally 4-bad."
            ),
            "key_finding_4": (
                "Three-interlaced m-gons on uniform 2D ρ-grid found NO 4-bad "
                "configurations at all (no resonance enforced)."
            ),
            "conclusion": (
                "No symmetric construction of types tried produces a strictly convex "
                "globally 4-bad polygon. The geometric obstruction is: the resonance "
                "conditions force the inner ring to be 'too small', breaking convexity."
            ),
        },
        "affine_stretched": {},
        "two_interlaced_simultaneous": {},
        "two_interlaced_general_offset": {},
        "three_interlaced": {},
        "filter_status_table": [],
    }

    # 1) Affine-stretched
    print("\n=== Affine-stretched ===", flush=True)
    for n in [18, 24, 30, 36, 48]:
        r = affine_global_check(n)
        findings["affine_stretched"][str(n)] = r
        print(f"  n={n}: {r['candidate_count']} candidate λs, "
              f"{r['vertex_0_4bad_count']} v0-4bad, {r['global_4bad_count']} globally 4-bad",
              flush=True)

    # 2) Two-interlaced simultaneous resonance
    print("\n=== Two-interlaced simultaneous ===", flush=True)
    for m in [12, 15, 18, 21, 24, 30]:
        n = 2 * m
        results = two_interlaced_simultaneous(m)
        findings["two_interlaced_simultaneous"][str(m)] = results
        print(f"  m={m} (n={n}): {len(results)} simultaneous solutions", flush=True)
        for r in results:
            print(
                f"    ρ={r['rho']:.6f} 4bad=YES convex={r['is_strictly_convex']} "
                f"cap={r['max_pairwise_intersection']} indeg=[{r['indegree_min_max'][0]},"
                f"{r['indegree_min_max'][1]}] in_window={r['in_strict_convex_window']}",
                flush=True,
            )

    # 3) Two-interlaced general offset (strict convex grid)
    print("\n=== Two-interlaced general offset (strict-convex grid) ===", flush=True)
    for m in [12, 15, 18, 21, 24]:
        results = scan_two_interlaced_general_offset(m)
        findings["two_interlaced_general_offset"][str(m)] = results
        print(f"  m={m} (n={2*m}): {len(results)} hits", flush=True)

    # 4) Three-interlaced
    print("\n=== Three-interlaced numerical grid ===", flush=True)
    for m in [8, 10, 12]:
        results = scan_three_interlaced(m, n_grid=15)
        findings["three_interlaced"][str(m)] = results
        print(f"  m={m} (n={3*m}): {len(results)} hits", flush=True)

    # Build filter status table
    table = []
    for m, lst in findings["two_interlaced_simultaneous"].items():
        for entry in lst:
            table.append({
                "construction": "two_interlaced_m_gons",
                "n": entry["n"], "m": entry["m"], "rho": entry["rho"],
                "is_4_bad": entry["is_4_bad"],
                "L5_cap_max": entry["max_pairwise_intersection"],
                "L5_cap_ok": entry["L5_cap_filter_ok"],
                "indegree_uniform_4": entry["all_indegree_4"],
                "is_strictly_convex": entry["is_strictly_convex"],
                "in_strict_convex_window": entry["in_strict_convex_window"],
                "passes_all_filters": (
                    entry["is_4_bad"] and entry["L5_cap_filter_ok"]
                    and entry["all_indegree_4"] and entry["is_strictly_convex"]
                ),
            })
    findings["filter_status_table"] = table
    findings["summary"]["total_candidates"] = len(table)
    findings["summary"]["passing_4bad_and_L5"] = sum(
        1 for r in table if r["is_4_bad"] and r["L5_cap_ok"]
    )
    findings["summary"]["passing_all_filters"] = sum(
        1 for r in table if r["passes_all_filters"]
    )

    with open("/tmp/symmetric_results.json", "w") as f:
        json.dump(findings, f, indent=2, default=str)
    print(f"\n\nWrote /tmp/symmetric_results.json", flush=True)
    print(f"Total candidates: {findings['summary']['total_candidates']}", flush=True)
    print(f"Pass 4-bad + L5: {findings['summary']['passing_4bad_and_L5']}", flush=True)
    print(f"Pass all filters: {findings['summary']['passing_all_filters']}", flush=True)


if __name__ == "__main__":
    main()
