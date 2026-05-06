"""
Erdős #97 — F13 (n=9) Gröbner-basis decoder.

For family F13 (orbit 2, status self_edge), we:
  1. Build the polynomial system from the witness pattern.
  2. Compute the lex Gröbner basis (lex order so the elimination ideal is exposed).
  3. Extract the univariate elimination polynomial in the smallest-eliminated variable.
  4. Compute all real roots of that polynomial.
  5. Lift each real root to all coordinates by solving the triangular system.
  6. Test for distinctness of the 9 points and strict convexity (sorted by polar angle around the centroid, alternation of cross-product signs).
  7. Emit a JSON certificate.

Gauge: x_0 = y_0 = 0, y_1 = 0, x_1 = 1.
"""
import json
import time
import math
import sys
sys.path.insert(0, '/home/user/erdos97/data/runs/2026-05-05')

import sympy as sp
from sympy import Rational, Symbol, groebner, expand, Poly, sqrt, nroots, simplify
from sympy.polys.orderings import lex, grevlex

# --- F13 pattern --------------------------------------------------------------

F13_ROWS = [
    [1, 2, 5, 7],
    [2, 3, 6, 8],
    [0, 3, 4, 7],
    [1, 4, 5, 8],
    [0, 2, 5, 6],
    [1, 3, 6, 7],
    [2, 4, 7, 8],
    [0, 3, 5, 8],
    [0, 1, 4, 6],
]
N = 9


def build_system(rows, n):
    xs = [Symbol(f'x{i}') for i in range(n)]
    ys = [Symbol(f'y{i}') for i in range(n)]
    subs = {xs[0]: Rational(0), ys[0]: Rational(0),
            ys[1]: Rational(0), xs[1]: Rational(1)}
    free = [xs[i] for i in range(2, n)] + [ys[i] for i in range(2, n)]

    def D(i, j):
        return (xs[i] - xs[j]) ** 2 + (ys[i] - ys[j]) ** 2

    polys = []
    for i, w in enumerate(rows):
        a, b, c, d = w
        for j in (b, c, d):
            polys.append(expand(D(i, a) - D(i, j)).subs(subs))
    polys = [p for p in polys if p != 0]
    seen = set()
    polys_unique = []
    for p in polys:
        s = sp.srepr(p)
        if s not in seen:
            seen.add(s)
            polys_unique.append(p)
    return free, polys_unique, xs, ys, subs


def main():
    print("=== F13 Gröbner decoder (n=9) ===")
    free, polys, xs, ys, subs = build_system(F13_ROWS, N)
    print(f"Variables (free): {[str(v) for v in free]}")
    print(f"Number of polynomials (unique): {len(polys)}")

    # --- 1) grevlex GB (cheap; for sanity / cross-check) ---------------------
    t0 = time.time()
    G_grevlex = groebner(polys, *free, order=grevlex, domain='QQ')
    t_grevlex = time.time() - t0
    print(f"\n[grevlex] basis size = {len(G_grevlex)} time = {t_grevlex:.2f}s")
    print(f"[grevlex] is_zero_dim = {G_grevlex.is_zero_dimensional}")
    print(f"[grevlex] first 8 generators:")
    for p in list(G_grevlex)[:8]:
        print(f"  {p}")

    # --- 2) lex GB. Use lex order with an ordering chosen to bring a single
    # variable to the bottom for elimination. We'll try y8 last (so y8 is the
    # leading variable to eliminate, leaving univariate y8). -----------------
    # In sympy lex with vars [v1,v2,...,vk], the LAST variable is the smallest
    # under lex ⇒ the elimination ideal in vk is what we want; basis contains a
    # univariate polynomial in vk if zero-dimensional.
    # Reorder to put y8 last:
    ordered = [v for v in free if v != Symbol('y8')] + [Symbol('y8')]
    print(f"\n[lex] ordering puts 'y8' last (small): {[str(v) for v in ordered]}")
    t0 = time.time()
    G_lex = groebner(polys, *ordered, order=lex, domain='QQ')
    t_lex = time.time() - t0
    print(f"[lex] basis size = {len(G_lex)} time = {t_lex:.2f}s")
    print(f"[lex] is_zero_dim = {G_lex.is_zero_dimensional}")

    # Find the univariate polynomial in y8 (last var):
    y8 = Symbol('y8')
    univariate = None
    for p in list(G_lex):
        free_syms = p.free_symbols
        if free_syms == {y8}:
            univariate = p
            break
    if univariate is None:
        # Try any single-var polynomial
        for p in list(G_lex):
            fs = p.free_symbols
            if len(fs) == 1:
                univariate = p
                print(f"[lex] (note) univariate found in {list(fs)[0]} not y8")
                break

    print(f"\n[univariate] polynomial: {univariate}")
    if univariate is None:
        print("FATAL: no univariate elimination polynomial found")
        return

    poly = Poly(univariate, list(univariate.free_symbols)[0])
    print(f"[univariate] degree = {poly.degree()}")
    print(f"[univariate] coefficients = {poly.all_coeffs()}")

    # --- 3) Real roots ------------------------------------------------------
    # All real roots over QQ-bar (algebraic):
    real_roots = sp.real_roots(poly)
    print(f"\n[real roots] count = {len(real_roots)}")
    for r in real_roots:
        print(f"  {r} ≈ {float(r):.10f}")

    # --- 4) Lift each real root via lex GB ----------------------------------
    # The lex GB has a univariate polynomial in y8, then polynomials in
    # (y8, prev_var), etc. For each real root r of the univariate polynomial,
    # substitute y8 = r and recursively solve the remaining triangular system.
    # We use sympy.solve on the substituted system to get all (in general
    # algebraic) values of remaining variables.
    print("\n[lift] solving triangular system per real root")
    full_solutions = []
    var_smb = list(univariate.free_symbols)[0]
    for idx, r in enumerate(real_roots):
        print(f"\n--- root #{idx}: {var_smb} = {r} ≈ {float(r):.6f} ---")
        # Substitute the root:
        subs_root = {var_smb: r}
        subbed = [sp.simplify(g.subs(subs_root)) for g in list(G_lex)]
        subbed = [s for s in subbed if s != 0]
        # Remaining variables:
        rem_vars = [v for v in ordered if v != var_smb]
        sols = sp.solve(subbed, rem_vars, dict=True)
        print(f"   sympy.solve returned {len(sols)} solution dicts")
        for si, sol in enumerate(sols):
            full = dict(sol)
            full[var_smb] = r
            full_solutions.append(full)

    print(f"\n[lift] total solution dicts: {len(full_solutions)}")

    # --- 5) Distinctness + strict convexity test for each lifted solution ---
    def to_points(sol_dict):
        # Build full coordinate list (x0,y0,...,x8,y8)
        full_subs = dict(subs)
        for k, v in sol_dict.items():
            full_subs[k] = v
        pts = []
        for i in range(N):
            xi = xs[i].subs(full_subs)
            yi = ys[i].subs(full_subs)
            try:
                xv = float(sp.N(xi, 30))
                yv = float(sp.N(yi, 30))
            except Exception:
                return None
            pts.append((xv, yv))
        return pts

    def distinctness(pts, tol=1e-9):
        n = len(pts)
        for i in range(n):
            for j in range(i + 1, n):
                if (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2 < tol ** 2:
                    return False, (i, j)
        return True, None

    def strict_convexity(pts):
        """Sort by polar angle around centroid, then check sign of all 9 cross
        products is the same (and nonzero)."""
        n = len(pts)
        cx = sum(p[0] for p in pts) / n
        cy = sum(p[1] for p in pts) / n
        sorted_pts = sorted(pts, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
        signs = []
        for i in range(n):
            a = sorted_pts[i]
            b = sorted_pts[(i + 1) % n]
            c = sorted_pts[(i + 2) % n]
            cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            signs.append(cross)
        positive = all(s > 1e-9 for s in signs)
        negative = all(s < -1e-9 for s in signs)
        return (positive or negative), signs

    decode_results = []
    for idx, sol in enumerate(full_solutions):
        pts = to_points(sol)
        if pts is None:
            decode_results.append({'idx': idx, 'error': 'non-real coordinate'})
            continue
        ok_distinct, dup = distinctness(pts)
        ok_convex, signs = strict_convexity(pts) if ok_distinct else (False, None)
        decode_results.append({
            'idx': idx,
            'sol_repr': {str(k): str(v) for k, v in sol.items()},
            'points': [[p[0], p[1]] for p in pts],
            'distinct': ok_distinct,
            'duplicate_pair': dup,
            'strictly_convex': ok_convex,
            'cross_signs': signs,
        })
        print(f"\n  Lift #{idx}: distinct={ok_distinct}, strictly_convex={ok_convex}")
        if not ok_distinct:
            print(f"    duplicate pair (i,j) = {dup}")
        if signs:
            print(f"    cross signs: {[f'{s:.4f}' for s in signs]}")

    # --- 6) Conclusion ------------------------------------------------------
    counterexample_found = any(r.get('distinct') and r.get('strictly_convex') for r in decode_results)
    print(f"\n=== CONCLUSION ===")
    print(f"Counterexample found: {counterexample_found}")

    cert = {
        'family_id': 'F13',
        'orbit_size': 2,
        'pattern': F13_ROWS,
        'n': N,
        'gauge': 'x0=y0=0, y1=0, x1=1',
        'gb': {
            'grevlex_size': len(G_grevlex),
            'grevlex_zero_dim': bool(G_grevlex.is_zero_dimensional),
            'grevlex_time_sec': t_grevlex,
            'lex_size': len(G_lex),
            'lex_zero_dim': bool(G_lex.is_zero_dimensional),
            'lex_time_sec': t_lex,
            'lex_basis_repr': [str(p) for p in list(G_lex)],
        },
        'univariate_polynomial': {
            'expr': str(univariate),
            'variable': str(var_smb),
            'degree': poly.degree(),
            'coefficients_descending': [str(c) for c in poly.all_coeffs()],
        },
        'real_roots': [
            {'symbolic': str(r), 'numeric': float(r)} for r in real_roots
        ],
        'lift_results': decode_results,
        'counterexample_found': counterexample_found,
        'conclusion': (
            'COUNTEREXAMPLE: at least one lifted real root is a strictly convex 9-gon with the 4-witness property.'
            if counterexample_found else
            'NON-REALIZABLE: every lifted real root either has duplicate vertices or fails strict convexity.'
        ),
    }
    out_path = '/home/user/erdos97/data/certificates/2026-05-06/n9_f13_decoder.json'
    with open(out_path, 'w') as f:
        json.dump(cert, f, indent=2, default=str)
    print(f"\n[wrote certificate] {out_path}")


if __name__ == '__main__':
    main()
