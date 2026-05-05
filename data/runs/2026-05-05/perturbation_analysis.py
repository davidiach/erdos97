"""
First-order perturbation analysis for Erdős Problem #97.

Goal: investigate whether perturbations of a regular n-gon can produce a
strictly convex polygon where every vertex has 4 others at one common distance.

Approach:
  (A) Linearise the equality constraints d(i,a) = d(i,b) at the regular n-gon.
      Compute rank, kernel dimension modulo rigid motions, consistency.
  (B) Run a Newton solver on the full nonlinear system from the regular n-gon.
  (C) Restrict to d_m-symmetric interlaced 2m-gons (two concentric regular m-gons,
      offset by π/m + phi) and search for parameters (r_b, phi) where every
      vertex has multiplicity >= 4 AND the polygon is strictly convex.

Output: /tmp/perturbation_results.json
"""
import json
import numpy as np
from itertools import combinations
from scipy.optimize import fsolve, root
from collections import Counter


# --------------------- helpers ---------------------
def regular_ngon(n):
    return np.array([[np.cos(2*np.pi*i/n), np.sin(2*np.pi*i/n)] for i in range(n)])


def chord_length_sq(n, k):
    return 2 - 2*np.cos(2*np.pi*k/n)


def linearize_eq(p, i, a, b, n):
    """
    Linearise constraint  d^2(i,a) = d^2(i,b) at perturbation 0.
    Returns (row of length 2n, rhs).
    """
    row = np.zeros(2*n)
    pia = p[i] - p[a]
    pib = p[i] - p[b]
    row[2*i:2*i+2] += 2*pia - 2*pib
    row[2*a:2*a+2] += -2*pia
    row[2*b:2*b+2] += +2*pib
    rhs = np.dot(pib, pib) - np.dot(pia, pia)
    return row, rhs


def linear_constraint_system(n, k1, k2):
    """
    Build the linearised system that, for every vertex i,
        d(i, i+k1) = d(i, i+k2)
        d(i, i-k1) = d(i, i-k2)
    Returns A, b such that the linearised system A delta = b describes
    perturbations realising the merge to first order.
    """
    p = regular_ngon(n)
    rows, rhss = [], []
    for i in range(n):
        for offs1, offs2 in [(k1, k2), (-k1, -k2)]:
            a = (i + offs1) % n
            b = (i + offs2) % n
            if a == b:
                continue
            r, c = linearize_eq(p, i, a, b, n)
            rows.append(r); rhss.append(c)
    return np.array(rows), np.array(rhss)


# --------------------- analyses ---------------------
def linearised_rank_analysis(n, k1, k2):
    A, b = linear_constraint_system(n, k1, k2)
    r_A = int(np.linalg.matrix_rank(A, tol=1e-9))
    r_Ab = int(np.linalg.matrix_rank(np.column_stack([A, b]), tol=1e-9))
    consistent = (r_A == r_Ab)
    kernel = 2*n - r_A
    return {
        'n': n, 'k1': k1, 'k2': k2,
        'rank_A': r_A, 'rank_Ab': r_Ab,
        'kernel_dim': kernel,
        'kernel_mod_rigid': kernel - 3,
        'consistent': bool(consistent),
        'rhs_norm': float(np.linalg.norm(b)),
    }


def newton_solve_full(n, k1, k2, p0=None, max_iter=200):
    """Solve the full nonlinear distance-equality system via Newton."""
    if p0 is None:
        p0 = regular_ngon(n).flatten()

    def res_only(P_flat):
        P = P_flat.reshape(n, 2)
        R = np.zeros(2*n)
        for i in range(n):
            a = (i+k1) % n; b = (i+k2) % n
            R[i] = np.linalg.norm(P[i]-P[a]) - np.linalg.norm(P[i]-P[b])
        for i in range(n):
            a = (i-k1) % n; b = (i-k2) % n
            R[n+i] = np.linalg.norm(P[i]-P[a]) - np.linalg.norm(P[i]-P[b])
        return R

    sol = root(res_only, p0, method='lm', options={'maxiter': max_iter})
    P = sol.x.reshape(n, 2)
    return P, sol


def cyclic_convex(P):
    n = len(P)
    for i in range(n):
        a = P[i]; b = P[(i+1) % n]; c = P[(i+2) % n]
        cross = (b[0]-a[0])*(c[1]-b[1]) - (b[1]-a[1])*(c[0]-b[0])
        if cross <= 1e-10:
            return False
    return True


def max_mult(P, tol=1e-5):
    n = len(P)
    out = []
    for i in range(n):
        ds = sorted(np.linalg.norm(P[i]-P[j]) for j in range(n) if j != i)
        clusters = [[ds[0]]]
        for d in ds[1:]:
            if d - clusters[-1][-1] < tol:
                clusters[-1].append(d)
            else:
                clusters.append([d])
        out.append(max(len(c) for c in clusters))
    return out


# --------------------- d_m-symmetric interlace ---------------------
def f_system_dm(rb_phi, m, k1A, k1B, k2A, k2B, ra=1.0):
    """
    Two equations: vertex 0 has merge (k1A,k1B), vertex 1 has merge (k2A,k2B).
    """
    r_b, phi = rb_phi
    dA1 = 2*ra**2 * (1 - np.cos(2*np.pi*k1A/m))
    dB1 = ra**2 + r_b**2 - 2*ra*r_b*np.cos(2*np.pi*k1B/m + np.pi/m + phi)
    dA2 = 2*r_b**2 * (1 - np.cos(2*np.pi*k2A/m))
    dB2 = r_b**2 + ra**2 - 2*r_b*ra*np.cos(2*np.pi*k2B/m - np.pi/m - phi)
    return [dA1 - dB1, dA2 - dB2]


def build_dm_polygon(m, r_b, phi, ra=1.0):
    pts = []
    for i in range(m):
        pts.append([ra*np.cos(2*np.pi*i/m), ra*np.sin(2*np.pi*i/m)])
        pts.append([r_b*np.cos(2*np.pi*i/m + np.pi/m + phi),
                    r_b*np.sin(2*np.pi*i/m + np.pi/m + phi)])
    return np.array(pts)


def search_dm_interlace(m):
    """
    Sweep merge tuples (k1A, k1B, k2A, k2B) and solve for (r_b, phi).
    Filter for: r_b in convex window (cos(π/m), 1/cos(π/m)), strict convexity,
    distinct points, all vertex multiplicities >= 4.
    """
    n = 2*m
    cm = np.cos(np.pi/m); cM = 1/cm
    seen = set()
    candidates = []
    for k1A in range(1, m//2 + 1):
        for k1B in range(m):
            for k2A in range(1, m//2 + 1):
                for k2B in range(m):
                    try:
                        x, _, ier, _ = fsolve(
                            f_system_dm, [1.02, 0.05],
                            args=(m, k1A, k1B, k2A, k2B),
                            full_output=True, xtol=1e-12)
                        if ier != 1:
                            continue
                        r_b, phi = x
                        if not (cm < r_b < cM):
                            continue
                        if abs(phi) > np.pi/m:
                            continue
                        resid = np.linalg.norm(
                            f_system_dm([r_b, phi], m, k1A, k1B, k2A, k2B))
                        if resid > 1e-9:
                            continue
                        key = (round(r_b, 5), round(phi, 5))
                        if key in seen:
                            continue
                        seen.add(key)
                        pts = build_dm_polygon(m, r_b, phi)
                        dmin = min(np.linalg.norm(pts[i]-pts[j])
                                   for i in range(n) for j in range(i+1, n))
                        if dmin < 1e-4:
                            continue
                        if not cyclic_convex(pts):
                            continue
                        mults0_1 = []
                        for vi in [0, 1]:
                            ds = sorted(round(np.linalg.norm(pts[vi]-pts[j]), 5)
                                        for j in range(n) if j != vi)
                            mults0_1.append(max(Counter(ds).values()))
                        if min(mults0_1) >= 4:
                            candidates.append({
                                'm': m, 'n': n,
                                'r_b': float(r_b), 'phi': float(phi),
                                'merge1': (k1A, k1B), 'merge2': (k2A, k2B),
                                'mults_v0_v1': mults0_1,
                            })
                    except Exception:
                        pass
    return candidates


# --------------------- main ---------------------
def main():
    all_results = {}

    # Linearised analysis: exhaust (k1, k2) pairs for each n
    print("="*68)
    print("Linearised constraint analysis")
    print("="*68)
    consistent_pairs = []
    for n in [12, 14, 16, 18, 20, 24]:
        per_n = []
        half = n // 2
        for k1, k2 in combinations(range(1, half+1), 2):
            if 2*k1 == n or 2*k2 == n:
                continue  # skip diametric (i+k = i-k)
            r = linearised_rank_analysis(n, k1, k2)
            per_n.append(r)
            if r['consistent'] and r['kernel_mod_rigid'] > 0:
                consistent_pairs.append(r)
        all_results[f'linearised_n{n}'] = per_n
        # find best (largest kernel_mod_rigid) for this n
        best = max(per_n, key=lambda x: x['kernel_mod_rigid'])
        print(f"n={n}: best (k1,k2)=({best['k1']},{best['k2']}): "
              f"kernel_mod_rigid={best['kernel_mod_rigid']}, consistent={best['consistent']}")

    # Newton on full nonlinear system
    print()
    print("="*68)
    print("Full Newton from regular n-gon")
    print("="*68)
    newton_results = []
    for (n, k1, k2) in [
        (12, 1, 5), (16, 1, 5), (16, 2, 6),
        (18, 1, 7), (18, 2, 8), (18, 3, 6),
        (24, 3, 9), (24, 2, 10), (24, 4, 8)]:
        P, sol = newton_solve_full(n, k1, k2)
        residual = float(np.linalg.norm(sol.fun)) if hasattr(sol, 'fun') else \
                   float(np.linalg.norm(sol.x))
        sc = cyclic_convex(P)
        distinct = all(np.linalg.norm(P[i]-P[j]) > 1e-4
                       for i in range(n) for j in range(i+1, n))
        mults = max_mult(P, tol=1e-4) if distinct else None
        result = {
            'n': n, 'k1': k1, 'k2': k2,
            'residual': residual,
            'cyclic_convex_orig_order': bool(sc),
            'distinct': bool(distinct),
            'min_mult': int(min(mults)) if mults else None,
            'mults': mults,
        }
        newton_results.append(result)
        print(f"  n={n}, ({k1},{k2}): residual={residual:.2e}, convex={sc}, "
              f"distinct={distinct}, "
              f"min_mult={result['min_mult']}")
    all_results['newton'] = newton_results

    # d_m-symmetric search
    print()
    print("="*68)
    print("d_m-symmetric interlaced 2m-gons")
    print("="*68)
    dm_results = {}
    for m in [6, 7, 8, 9, 10, 12]:
        cm = np.cos(np.pi/m); cM = 1/cm
        cands = search_dm_interlace(m)
        dm_results[f'm={m}'] = {
            'convex_window': [float(cm), float(cM)],
            'candidates': cands,
        }
        print(f"m={m} (n={2*m}), convex window [{cm:.4f}, {cM:.4f}]: "
              f"{len(cands)} 4-bad convex candidates.")
    all_results['dm_interlace'] = dm_results

    # Save
    def serialise(o):
        if isinstance(o, dict):
            return {k: serialise(v) for k, v in o.items()}
        if isinstance(o, list):
            return [serialise(v) for v in o]
        if isinstance(o, tuple):
            return [serialise(v) for v in o]
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, (bool, int, float, str)) or o is None:
            return o
        return str(o)

    with open('/tmp/perturbation_results.json', 'w') as f:
        json.dump(serialise(all_results), f, indent=2)
    print()
    print("Results saved to /tmp/perturbation_results.json")


if __name__ == "__main__":
    main()
