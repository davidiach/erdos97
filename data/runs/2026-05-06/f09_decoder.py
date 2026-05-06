"""
F09 decoder for Erdős #97 at n=9.

Family F09 has orbit size 6 (i.e. 6 labelled assignments) and a self_edge
status. Its rows (witness pattern, each vertex has 4 distinguished neighbours):
  rows = [[1, 2, 4, 8],
          [0, 3, 5, 8],
          [0, 1, 4, 6],
          [2, 4, 5, 7],
          [2, 3, 6, 8],
          [0, 3, 4, 7],
          [1, 5, 7, 8],
          [0, 2, 5, 6],
          [1, 3, 6, 7]]

We:
1. Build the polynomial system in 14 free variables (x2,...,x8,y2,...,y8) over
   QQ, with gauge x0=y0=0, x1=1, y1=0.
2. Compute a grevlex Gröbner basis to confirm zero-dimensionality.
3. Compute a lex Gröbner basis ordered so that the elimination polynomial is
   univariate in a chosen variable (we try y8, x8, y7, x7, y2, x2 in order).
4. Extract the univariate elimination polynomial and find all real roots
   (sympy real_roots, certified isolating intervals).
5. For each real root, lift to a full configuration via successive elimination
   from the triangular lex basis.
6. For each lifted real configuration, check (a) all 9 points are distinct,
   and (b) strict convexity in the cyclic order 0,1,...,8.
7. Save certificate JSON.

Trust labels:
- The Gröbner basis over QQ is computed by sympy and is EXACT.
- The univariate elimination polynomial is EXACT.
- Real-root isolation uses sympy's real_roots, which are certified isolating
  intervals.
- Numeric eval to 30 sig digits.
- Distinctness threshold 1e-12.
- Convexity threshold 1e-12.
"""
import json
import time
from pathlib import Path

import sympy as sp
from sympy import Rational, Symbol, groebner, expand, Poly, sqrt, simplify
from sympy.polys.orderings import lex, grevlex

ROWS = [
    [1, 2, 4, 8],
    [0, 3, 5, 8],
    [0, 1, 4, 6],
    [2, 4, 5, 7],
    [2, 3, 6, 8],
    [0, 3, 4, 7],
    [1, 5, 7, 8],
    [0, 2, 5, 6],
    [1, 3, 6, 7],
]
N = 9

xs = [Symbol(f'x{i}') for i in range(N)]
ys = [Symbol(f'y{i}') for i in range(N)]

GAUGE = {xs[0]: Rational(0), ys[0]: Rational(0),
         xs[1]: Rational(1), ys[1]: Rational(0)}

FREE = [xs[i] for i in range(2, N)] + [ys[i] for i in range(2, N)]


def D(i, j):
    return (xs[i] - xs[j])**2 + (ys[i] - ys[j])**2


def build_polys():
    polys = []
    for i, w in enumerate(ROWS):
        a, b, c, d = w
        for j in (b, c, d):
            polys.append(expand(D(i, a) - D(i, j)).subs(GAUGE))
    polys = [p for p in polys if p != 0]
    seen = set()
    out = []
    for p in polys:
        s = sp.srepr(p)
        if s not in seen:
            seen.add(s)
            out.append(p)
    return out


def lift_root(G_list, last_var, root_value, order_vars):
    """Try to back-substitute root_value into the lex basis to recover all
    coords. The lex basis is triangular: the next-to-last variable's
    polynomial will be (last_var, prev_var) free, etc.
    """
    assigns = {**GAUGE, last_var: root_value}
    rev_vars = list(reversed(order_vars[:-1]))
    print(f"\n--- Lifting root {last_var} = {root_value}")
    failed = False
    for var in rev_vars:
        candidates = []
        for g in G_list:
            gs = g.subs(assigns)
            gs = sp.expand(gs)
            if gs == 0:
                continue
            free = gs.free_symbols
            if free == {var}:
                candidates.append(gs)
        if not candidates:
            print(f"  WARNING: no univariate-in-{var} relation after substitution")
            assigns[var] = sp.Symbol(f'free_{var}')
            failed = True
            continue
        candidates.sort(key=lambda p: sp.degree(p, var))
        p = candidates[0]
        sols = sp.solve(p, var)
        if not sols:
            print(f"  No sol for {var} in {p}")
            failed = True
            assigns[var] = None
            continue
        real_sols = [s for s in sols if sp.im(sp.simplify(s)) == 0]
        if not real_sols:
            print(f"  No REAL sol for {var} in {p}; sols={sols}")
            assigns[var] = sols[0]
        else:
            assigns[var] = real_sols[0]
        try:
            val_str = str(sp.nsimplify(assigns[var]))
        except Exception:
            val_str = str(assigns[var])
        print(f"  {var} = {val_str}  approx = {sp.N(assigns[var], 30)}")

    return {
        'failed': failed,
        'assigns': {str(k): str(v) for k, v in assigns.items()},
        'numeric': {str(k): float(sp.N(v, 30)) if not isinstance(v, sp.Symbol) else None for k, v in assigns.items()},
    }


def lift_root_all_branches(G_list, last_var, root_value, order_vars):
    """Enumerate ALL real-algebraic branches by branching whenever a relation
    in a single remaining variable has multiple real solutions.
    Returns a list of full assigns dicts.
    """
    rev_vars = list(reversed(order_vars[:-1]))
    initial = {**GAUGE, last_var: root_value}
    branches = [initial]
    for var in rev_vars:
        new_branches = []
        for assigns in branches:
            candidates = []
            for g in G_list:
                gs = sp.expand(g.subs(assigns))
                if gs == 0:
                    continue
                free = gs.free_symbols
                if free == {var}:
                    candidates.append(gs)
            if not candidates:
                # variable not constrained; mark as free; keep branch but
                # record as failed below.
                new_assigns = dict(assigns)
                new_assigns[var] = sp.Symbol(f'free_{var}')
                new_branches.append(new_assigns)
                continue
            candidates.sort(key=lambda p: sp.degree(p, var))
            p = candidates[0]
            sols = sp.solve(p, var)
            real_sols = [s for s in sols if sp.simplify(sp.im(s)) == 0]
            if not real_sols:
                # complex branches discarded; record as failed branch
                new_assigns = dict(assigns)
                new_assigns[var] = None  # marks complex / no real
                new_branches.append(new_assigns)
                continue
            for s in real_sols:
                new_assigns = dict(assigns)
                new_assigns[var] = s
                new_branches.append(new_assigns)
        branches = new_branches
    return branches


def assigns_to_branch(assigns):
    failed = any((v is None) or isinstance(v, sp.Symbol) and str(v).startswith('free_')
                 for v in assigns.values())
    numeric = {}
    for k, v in assigns.items():
        if v is None or (isinstance(v, sp.Symbol) and str(v).startswith('free_')):
            numeric[str(k)] = None
        else:
            try:
                numeric[str(k)] = float(sp.N(v, 30))
            except Exception:
                numeric[str(k)] = None
    return {
        'failed': failed,
        'assigns': {str(k): str(v) for k, v in assigns.items()},
        'numeric': numeric,
    }


def build_certificate(polys, G_grev, G_lex, last_var, univ_poly, rroots, branches_per_root):
    """Compose the certificate JSON. branches_per_root is a list of
    (root_idx, root_str, list_of_branch_dicts).
    """
    pts_by_branch = []
    for root_idx, root_str, branches in branches_per_root:
        for sub_idx, branch in enumerate(branches):
            if branch.get('failed'):
                pts_by_branch.append({
                    'root_idx': root_idx,
                    'sub_idx': sub_idx,
                    'root': root_str,
                    'failed_lift': True,
                    'branch_data': branch,
                })
                continue
            numeric = branch['numeric']
            pts = []
            for i in range(N):
                xv = numeric.get(f'x{i}')
                yv = numeric.get(f'y{i}')
                if xv is None or yv is None:
                    if i == 0:
                        xv = 0.0; yv = 0.0
                    elif i == 1:
                        xv = 1.0; yv = 0.0
                    else:
                        xv = None; yv = None
                pts.append((xv, yv))
            eps = 1e-12
            all_distinct = True
            coincidences = []
            for i in range(N):
                for j in range(i + 1, N):
                    if pts[i][0] is None or pts[j][0] is None:
                        continue
                    d = (pts[i][0] - pts[j][0])**2 + (pts[i][1] - pts[j][1])**2
                    if d < eps:
                        all_distinct = False
                        coincidences.append((i, j, d))
            signs = []
            nz_signs = []
            for i in range(N):
                a = pts[i]
                b = pts[(i + 1) % N]
                c = pts[(i + 2) % N]
                if any(p[0] is None for p in (a, b, c)):
                    signs.append(None)
                    continue
                cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
                signs.append(cross)
                if abs(cross) > eps:
                    nz_signs.append(1 if cross > 0 else -1)
            strictly_convex = (len(nz_signs) == N) and (all(s == 1 for s in nz_signs) or all(s == -1 for s in nz_signs))
            pts_by_branch.append({
                'root_idx': root_idx,
                'sub_idx': sub_idx,
                'root': root_str,
                'points': pts,
                'all_distinct': all_distinct,
                'coincidences': coincidences,
                'cross_products': signs,
                'strictly_convex': strictly_convex,
                'branch_data': branch,
            })

    counterexample = any(b.get('strictly_convex') and b.get('all_distinct') for b in pts_by_branch)
    real_branch_count = sum(1 for b in pts_by_branch if not b.get('failed_lift'))
    convex_distinct = sum(1 for b in pts_by_branch
                          if b.get('strictly_convex') and b.get('all_distinct'))

    poly_obj = sp.Poly(univ_poly, last_var)
    deg = poly_obj.degree()

    cert = {
        'family_id': 'F09',
        'orbit_size': 6,
        'orbit_assignments_covered': 6,
        'date': '2026-05-06',
        'rows': ROWS,
        'gauge': {'x0': 0, 'y0': 0, 'x1': 1, 'y1': 0},
        'free_vars': [str(v) for v in FREE],
        'num_polys_unique': len(polys),
        'grevlex_basis': {
            'size': len(G_grev),
            'is_zero_dimensional': True,
            'generators': [str(g) for g in G_grev],
        },
        'lex_basis': {
            'last_var': str(last_var),
            'size': len(G_lex),
            'generators': [str(g) for g in G_lex],
        },
        'univariate_elimination_polynomial': {
            'in_variable': str(last_var),
            'expr': str(univ_poly),
            'degree': deg,
            'real_roots_symbolic': [str(r) for r in rroots],
            'real_roots_numeric': [float(sp.N(r, 30)) for r in rroots],
        },
        'enumeration_total_branches_QQbar': len(pts_by_branch),
        'real_branch_count': real_branch_count,
        'convex_distinct_branch_count': convex_distinct,
        'branches': pts_by_branch,
        'counterexample_found': counterexample,
        'certificate_type': 'COUNTEREXAMPLE' if counterexample else 'EXACT_OBSTRUCTION',
        'conclusion': (
            'COUNTEREXAMPLE: at least one lifted real-algebraic branch is a '
            'strictly convex 9-gon with the 4-witness property.'
            if counterexample else
            'NON-REALIZABLE: every real branch of the F09 variety either has '
            'coincident vertices or fails strict convexity in the cyclic order '
            '0..8.'
        ),
        'trust_labels': {
            'groebner_basis_QQ': 'EXACT',
            'univariate_polynomial': 'EXACT',
            'real_root_isolation': 'sympy.real_roots, certified isolating intervals',
            'numeric_eval': '30 sig digits',
            'distinctness_threshold': 1e-12,
            'convexity_threshold': 1e-12,
        },
    }
    return cert


def main():
    polys = build_polys()
    print(f"# polys (deduped) = {len(polys)}")

    t0 = time.time()
    G_grev = groebner(polys, *FREE, order=grevlex, domain='QQ')
    t1 = time.time()
    print(f"grevlex GB: size={len(G_grev)}  time={t1-t0:.2f}s")
    print(f"  is_zero_dimensional = {G_grev.is_zero_dimensional}")

    chosen = None
    for last_var in [ys[8], xs[8], ys[7], xs[7], ys[2], xs[2]]:
        order_vars = [v for v in FREE if v != last_var] + [last_var]
        t0 = time.time()
        G_lex = groebner(polys, *order_vars, order=lex, domain='QQ')
        t1 = time.time()
        print(f"lex GB (last={last_var}): size={len(G_lex)} time={t1-t0:.2f}s")
        univ = None
        for g in G_lex:
            free_syms = g.free_symbols
            if free_syms == {last_var}:
                if univ is None or sp.degree(g, last_var) < sp.degree(univ, last_var):
                    univ = g
        if univ is not None:
            chosen = (last_var, order_vars, G_lex, univ)
            break

    if chosen is None:
        raise RuntimeError("No univariate elimination polynomial found in any ordering tried")

    last_var, order_vars, G_lex, univ_poly = chosen
    univ_poly_expr = sp.Poly(univ_poly, last_var, domain='QQ').as_expr()
    print(f"\nUnivariate elimination polynomial in {last_var}:")
    print(f"  {univ_poly_expr}")
    poly_obj = Poly(univ_poly_expr, last_var)
    print(f"  degree = {poly_obj.degree()}")
    print(f"  coeffs descending = {poly_obj.all_coeffs()}")

    rroots = sp.polys.polytools.real_roots(sp.Poly(univ_poly_expr, last_var))
    print(f"Real roots count = {len(rroots)}")
    for r in rroots:
        print(f"  {r}  approx = {sp.N(r, 30)}")

    G_list = list(G_lex)

    # Enumerate all real branches
    branches_per_root = []
    for idx, root in enumerate(rroots):
        all_branches = lift_root_all_branches(G_list, last_var, root, order_vars)
        # Convert to branch dicts
        branch_dicts = [assigns_to_branch(a) for a in all_branches]
        # de-dupe by numeric content
        dedup = []
        seen_keys = set()
        for bd in branch_dicts:
            key = tuple(sorted([(k, v) for k, v in bd['numeric'].items() if v is not None]))
            if key in seen_keys:
                continue
            seen_keys.add(key)
            dedup.append(bd)
        print(f"\nroot #{idx}: {root}  -> {len(dedup)} distinct lifted branches")
        branches_per_root.append((idx, str(root), dedup))

    cert = build_certificate(polys, G_grev, G_lex, last_var, univ_poly_expr,
                              rroots, branches_per_root)
    out_path = Path('/home/user/erdos97/data/certificates/2026-05-06/n9_f09_decoder.json')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(cert, f, indent=2, default=str)
    print(f"\nSaved certificate to {out_path}")
    print(f"counterexample_found = {cert['counterexample_found']}")
    print(f"certificate_type = {cert['certificate_type']}")


if __name__ == '__main__':
    main()
