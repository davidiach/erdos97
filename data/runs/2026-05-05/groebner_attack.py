"""
Erdős #97 Gröbner basis attack.

For a witness-incidence pattern (each vertex i has 4 distinguished neighbors
{a, b, c, d} such that |i-a| = |i-b| = |i-c| = |i-d|), set up the polynomial
system in 2n vertex coordinates and compute a Gröbner basis with sympy over QQ.
A trivial basis {1} proves the system is over-determined / unrealizable.

Symmetry fixings used (gauge):
  x_0 = 0, y_0 = 0    (translation)
  y_1 = 0             (rotation)
  x_1 = 1             (scale)
"""
import json
import time
import sympy as sp
from sympy import Rational, Symbol, groebner, expand
from sympy.polys.orderings import lex, grevlex


def build_system(rows, n, monomial_order='grevlex'):
    """rows[i] is list of 4 indices = witnesses of vertex i.
    Returns (variable_list, polynomial_list, free_vars).
    """
    # Variables x_0..x_{n-1}, y_0..y_{n-1} as sympy symbols
    xs = [Symbol(f'x{i}') for i in range(n)]
    ys = [Symbol(f'y{i}') for i in range(n)]

    # Gauge fixings
    subs = {xs[0]: Rational(0), ys[0]: Rational(0),
            ys[1]: Rational(0), xs[1]: Rational(1)}

    # Free variables (in the order we want to feed into Gröbner)
    free = [xs[i] for i in range(2, n)] + [ys[i] for i in range(2, n)]

    # Distance squared: D(i,j) = (x_i - x_j)^2 + (y_i - y_j)^2
    def D(i, j):
        return (xs[i] - xs[j])**2 + (ys[i] - ys[j])**2

    polys = []
    for i, w in enumerate(rows):
        if len(w) != 4:
            raise ValueError(f"row {i} has {len(w)} witnesses, expected 4")
        a, b, c, d = w
        # Three equality constraints: D(i,a)=D(i,b), D(i,a)=D(i,c), D(i,a)=D(i,d)
        for j in (b, c, d):
            polys.append(expand(D(i, a) - D(i, j)).subs(subs))

    polys = [p for p in polys if p != 0]
    return free, polys


def try_groebner(rows, n, time_budget_sec=180, monomial_order='grevlex',
                 use_lex_after=False, lex_budget_sec=120):
    """Compute Gröbner basis of the system with a soft time check."""
    free, polys = build_system(rows, n)
    info = {'n': n, 'num_polys': len(polys), 'num_vars': len(free),
            'order': monomial_order}
    # Eliminate trivial duplicates (some constraints might coincide)
    polys_unique = []
    seen = set()
    for p in polys:
        s = sp.srepr(p)
        if s not in seen:
            seen.add(s)
            polys_unique.append(p)
    info['num_polys_unique'] = len(polys_unique)

    order = grevlex if monomial_order == 'grevlex' else lex
    t0 = time.time()
    try:
        G = groebner(polys_unique, *free, order=order, domain='QQ')
        t1 = time.time()
        info['groebner_time'] = t1 - t0
        info['basis_size'] = len(G)
        info['is_trivial_one'] = (len(G) == 1 and G[0] == 1)
        info['basis_repr'] = [str(p) for p in list(G)[:8]]
    except Exception as e:
        info['error'] = f"{type(e).__name__}: {e}"
        info['groebner_time'] = time.time() - t0
    return info


if __name__ == '__main__':
    # Demo: load survivor 0
    with open('/home/user/erdos97/data/incidence/n8_reconstructed_15_survivors.json') as f:
        survivors = json.load(f)
    s = survivors[0]
    rows = [[j for j, v in enumerate(r) if v == 1] for r in s['rows']]
    print('Survivor 0 rows:', rows)
    info = try_groebner(rows, n=8)
    print(json.dumps(info, indent=2))
