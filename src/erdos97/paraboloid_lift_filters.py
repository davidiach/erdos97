"""Paraboloid-lift dual incidence filter (proof-of-concept).

Background (canonical-synthesis.md, Section 1.3, equivalence #4): lift each
vertex p_i = (x_i, y_i) to hat_p_i = (x_i, y_i, x_i^2 + y_i^2) on the paraboloid
z = x^2 + y^2. The condition that vertex i has 4 equidistant other vertices
is equivalent to the four lifted witnesses lying on a hyperplane H_i
PARALLEL to the tangent plane of the paraboloid at hat_p_i. The tangent plane
at hat_p_i has normal (2 x_i, 2 y_i, -1).

Concretely, hat_p_j lies on H_i iff
    x_j^2 + y_j^2 - 2 x_i x_j - 2 y_i y_j = c_i
for a constant c_i depending only on vertex i. Equivalently, every j in S_i
satisfies the linear equation
    2 x_i x_j + 2 y_i y_j + c_i = x_j^2 + y_j^2.

DUAL VIEWPOINT (this module). Fix a witness vertex j with indegree
    d_j = #{ i : j in S_i }.
Then the d_j affine equations on the unknown row (2 x_i, 2 y_i, c_i):
    [ 2 x_j ] [ 2 x_i ]                 [ x_j^2 + y_j^2 ]
    [ 2 y_j ] [ 2 y_i ] = (rhs constant) [               ]
    [   1   ] [  c_i  ]
share the SAME left-hand-side vector (2 x_j, 2 y_j, 1). In matrix form, stack
these incidences over all (i, j) into a single matrix A whose rows are
    A[(i, j)] = (2 x_j, 2 y_j, 1, 0, ..., 0, -2 x_i, -2 y_i, -1, 0, ..., 0,
                 -1 contribution at column c_i)
wait -- this is bilinear, not linear. We treat one side as known, the other
as the unknown.

The CONCRETE FILTER implemented here: for each witness vertex j with d_j >= 4,
the four (or more) center-side rows
    M_j[i, :] = (2 x_i, 2 y_i, c_i)         for i with j in S_i
must satisfy
    M_j @ (x_j, y_j, 1)^T = q_j * 1
i.e. there is a vector (x_j, y_j, 1) -- with last coordinate = 1 -- that maps
M_j to a constant vector. This is the rank-1 condition

    rank [ M_j  |  q_j * 1 - column ] <= rank M_j  (column-extension stays 0)

Equivalently, the augmented matrix
    [ 2 x_{i1}  2 y_{i1}  c_{i1}  q_j ]
    [ 2 x_{i2}  2 y_{i2}  c_{i2}  q_j ]
    [   ...                            ]
    [ 2 x_{id}  2 y_{id}  c_{id}  q_j ]
must satisfy: for any 4 rows, the 4x4 determinant vanishes (four rows in a
3-dim affine condition). For pure indegree d_j = 4 the constraint is one
single 4x4 minor vanishing, giving ONE polynomial identity per (j, choice of
4 incident i's). Stacking over all j with d_j >= 4 gives a polynomial system
naturally indexed by the column-incidence (the dual of the row incidence
used by groebner_attack).

NEW SUBSTANCE: this is the formal dual to the row-determinant system used in
affine_circuit_certificates.py. The row-determinant rule says "4 lifts on
plane H_i". The column-determinant rule says "1 lift on >=4 hyperplanes
H_{i1},...,H_{i4}". When d_j > 4 we get extra polynomial identities that
the existing rows-only formulation does not directly encode. We refer to the
column-determinant as the "dual paraboloid filter" or DPF.

We then run a SymPy Groebner basis over QQ, after applying a translation /
rotation / scaling gauge fixing identical to data/runs/2026-05-05/groebner_attack.py
so results are directly comparable.

If the DPF Groebner basis is {1}, the dual incidence pattern is unrealizable
in the plane (over the algebraic closure). The honest comparison: the original
row-based Groebner already kills all 15 n=8 survivors in <0.5s each. The DPF
version is studied here to see whether (a) it produces materially smaller GB
generators / faster proof, (b) it kills any pattern at n=10 / n=11 not yet
killed by the existing toolkit, or (c) merely reproduces the same answer.

NOTHING in this module proves Erdos #97. It only provides a fixed-pattern
filter test, exactly the same regime as the existing affine-circuit and
row-Groebner artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Iterable, Sequence
import time

import sympy as sp
from sympy import Rational, Symbol, expand, groebner
from sympy.polys.orderings import grevlex


Pattern = Sequence[Sequence[int]]


@dataclass
class GaugedSystem:
    """Polynomial system after translation/rotation/scaling gauge fix."""
    n: int
    free_variables: list[Symbol]
    polys: list[sp.Expr]
    gauge_substitution: dict
    polys_per_vertex_j: dict[int, list[sp.Expr]] = field(default_factory=dict)


def gauge_substitution(xs: Sequence[Symbol], ys: Sequence[Symbol]) -> dict:
    """Standard gauge fix: x0=0, y0=0, y1=0, x1=1.

    Identical to data/runs/2026-05-05/groebner_attack.py for direct
    comparability of GB outcomes.
    """
    return {xs[0]: Rational(0), ys[0]: Rational(0),
            ys[1]: Rational(0), xs[1]: Rational(1)}


def _row_witness_lists(rows: Pattern, n: int) -> list[list[int]]:
    """Accept either 0/1 row matrix or list-of-witness-lists; return lists."""
    out: list[list[int]] = []
    for i, r in enumerate(rows):
        r_list = list(r)
        if all(v in (0, 1) for v in r_list) and len(r_list) == n:
            witness = [j for j, v in enumerate(r_list) if v == 1]
        else:
            witness = sorted(int(v) for v in r_list)
        if len(witness) != 4:
            raise ValueError(
                f"row {i} must select 4 witnesses, got {len(witness)}: {witness}"
            )
        if i in witness:
            raise ValueError(f"row {i} includes itself as a witness: {witness}")
        out.append(witness)
    return out


def column_incidence(rows: Sequence[Sequence[int]], n: int) -> list[list[int]]:
    """Return list_j = sorted list of i such that j is a witness of row i.

    This is the dual incidence: for each vertex j, who selects j.
    """
    out: list[list[int]] = [[] for _ in range(n)]
    for i, witnesses in enumerate(rows):
        for j in witnesses:
            out[j].append(i)
    for j in range(n):
        out[j].sort()
    return out


def build_dual_paraboloid_system(
    rows: Pattern,
    n: int,
    gauge: bool = True,
) -> GaugedSystem:
    """Construct the dual paraboloid filter polynomial system for `rows`.

    Variables: xs[0..n-1], ys[0..n-1], cs[0..n-1] where c_i is the affine
    constant of the parallel-to-tangent plane H_i. Each row i contributes
    constraints
        x_j^2 + y_j^2 - 2 x_i x_j - 2 y_i y_j - c_i = 0    for j in S_i.
    Stacked over all (i, j) incidences, this is the lifted-plane incidence
    system. There are 4 * n such polynomials in 3n variables. After gauge
    fix, 3n - 4 free variables.

    Note the c_i variables are auxiliary: they could be eliminated by setting
    c_i := r_i^2 - x_i^2 - y_i^2 with r_i = ||v_a - v_i|| for a chosen
    a in S_i, recovering a system in the 2n vertex coordinates. We keep c_i
    explicit so the system is bilinear-quadratic and the column-determinant
    structure is visible.
    """
    witnesses = _row_witness_lists(rows, n)
    xs = [Symbol(f"x{i}") for i in range(n)]
    ys = [Symbol(f"y{i}") for i in range(n)]
    cs = [Symbol(f"c{i}") for i in range(n)]
    subs = gauge_substitution(xs, ys) if gauge else {}

    polys: list[sp.Expr] = []
    polys_by_j: dict[int, list[sp.Expr]] = {j: [] for j in range(n)}
    for i, S_i in enumerate(witnesses):
        for j in S_i:
            poly = expand(
                xs[j] ** 2 + ys[j] ** 2 - 2 * xs[i] * xs[j] - 2 * ys[i] * ys[j] - cs[i]
            )
            poly = poly.subs(subs)
            polys.append(poly)
            polys_by_j[j].append(poly)

    free = [v for v in (*xs[2:], *ys[2:], *cs)
            if v not in subs]

    return GaugedSystem(
        n=n,
        free_variables=free,
        polys=polys,
        gauge_substitution=subs,
        polys_per_vertex_j=polys_by_j,
    )


def column_determinant_polys(
    rows: Pattern,
    n: int,
    gauge: bool = True,
) -> list[tuple[int, tuple[int, ...], sp.Expr]]:
    """Return the explicit column-determinant Plucker relations.

    For each vertex j and each 4-subset {i_1,...,i_4} of incidences-to-j, the
    4x4 augmented matrix
        [ 2 x_{i_k}  2 y_{i_k}  c_{i_k}  q_j ]_{k=1..4},  with q_j = x_j^2 + y_j^2,
    has rank <= 3 (since (x_j, y_j, 1, -1) lies in the kernel after multiplying
    column 4 by -1). The 4x4 determinant being zero is one polynomial identity.

    We build these polynomials gauged exactly as in build_dual_paraboloid_system.
    Returns list of (j, (i1,i2,i3,i4), poly).
    """
    witnesses = _row_witness_lists(rows, n)
    col_inc = column_incidence(witnesses, n)
    xs = [Symbol(f"x{i}") for i in range(n)]
    ys = [Symbol(f"y{i}") for i in range(n)]
    cs = [Symbol(f"c{i}") for i in range(n)]
    subs = gauge_substitution(xs, ys) if gauge else {}

    out: list[tuple[int, tuple[int, ...], sp.Expr]] = []
    for j, incidents in enumerate(col_inc):
        if len(incidents) < 4:
            continue
        q_j = xs[j] ** 2 + ys[j] ** 2
        for combo in combinations(incidents, 4):
            row4 = [(2 * xs[k], 2 * ys[k], cs[k]) for k in combo]
            diffs = [
                tuple(row4[t][col] - row4[0][col] for col in range(3))
                for t in (1, 2, 3)
            ]
            det = expand(q_j * sp.Matrix(diffs).det()).subs(subs)
            if det == 0:
                continue
            out.append((j, tuple(combo), det))
    return out


def column_determinant_polys_eliminated(
    rows: Pattern,
    n: int,
    gauge: bool = True,
) -> list[tuple[int, tuple[int, ...], sp.Expr]]:
    """Return the column-Plucker identities AFTER eliminating c_i.

    Substituting c_i := x_a^2 + y_a^2 - 2 x_i x_a - 2 y_i y_a for any chosen
    a in S_i (we use the lex-minimum non-i element) into the 4x4 column
    determinant produces a polynomial in (x_*, y_*) only. THESE polynomials
    are formal consequences of the row equidistance equations -- by direct
    expansion the result is identically zero modulo the chosen row equation.
    They are recorded here only as a structural diagnostic; they do NOT add
    new constraints beyond the row equations (this is documented honestly in
    docs/paraboloid-lift-attack.md).
    """
    witnesses = _row_witness_lists(rows, n)
    col_inc = column_incidence(witnesses, n)
    xs = [Symbol(f"x{i}") for i in range(n)]
    ys = [Symbol(f"y{i}") for i in range(n)]
    subs = gauge_substitution(xs, ys) if gauge else {}

    def c_expr(i: int) -> sp.Expr:
        S_i = witnesses[i]
        a = min(j for j in S_i if j != i)
        # c_i = ||v_a - v_i||^2 - x_i^2 - y_i^2 + x_a^2 + y_a^2
        # using definition c_i = q_a - 2 x_i x_a - 2 y_i y_a
        return xs[a] ** 2 + ys[a] ** 2 - 2 * xs[i] * xs[a] - 2 * ys[i] * ys[a]

    out: list[tuple[int, tuple[int, ...], sp.Expr]] = []
    for j, incidents in enumerate(col_inc):
        if len(incidents) < 4:
            continue
        q_j = xs[j] ** 2 + ys[j] ** 2
        for combo in combinations(incidents, 4):
            # Reduce the 4x4 determinant with constant last column to
            # q_j * det of 3x3 differences of the first 3 columns. This is
            # algebraically equivalent and ~6x faster than full sp.Matrix.det
            # on the 4x4 symbolic matrix.
            row4 = [(2 * xs[k], 2 * ys[k], c_expr(k)) for k in combo]
            diffs = [
                tuple(row4[t][col] - row4[0][col] for col in range(3))
                for t in (1, 2, 3)
            ]
            small = sp.Matrix(diffs)
            det = expand(q_j * small.det()).subs(subs)
            if det == 0:
                continue
            out.append((j, tuple(combo), det))
    return out


def run_row_groebner_with_column_pucker_enrichment(
    rows: Pattern,
    n: int,
    use_column_pucker: bool = False,
    time_budget_sec: float | None = None,
) -> dict:
    """Direct row equidistance Groebner, with optional column-Plucker enrichment.

    Variables: 2n vertex coordinates only. Gauge fix x0=y0=0, x1=1, y1=0.
    Constraints: 3 per row, exactly as in data/runs/2026-05-05/groebner_attack.py.
    Optional enrichment: append column-Plucker polynomials (after c_i
    elimination). These should reduce to zero modulo the row equations; we
    log whether SymPy recognizes that or whether some survive into the basis.

    Returns dict with the same fields as run_dual_paraboloid_groebner.
    """
    witnesses = _row_witness_lists(rows, n)
    xs = [Symbol(f"x{i}") for i in range(n)]
    ys = [Symbol(f"y{i}") for i in range(n)]
    subs = gauge_substitution(xs, ys)
    free = [v for v in (*xs[2:], *ys[2:]) if v not in subs]

    def D(a: int, b: int) -> sp.Expr:
        return (xs[a] - xs[b]) ** 2 + (ys[a] - ys[b]) ** 2

    polys: list[sp.Expr] = []
    for i, S_i in enumerate(witnesses):
        a = S_i[0]
        for b in S_i[1:]:
            polys.append(expand(D(i, a) - D(i, b)).subs(subs))

    if use_column_pucker:
        for _, _, p in column_determinant_polys_eliminated(rows, n, gauge=True):
            polys.append(p)

    seen = set()
    polys_unique: list[sp.Expr] = []
    for p in polys:
        if p == 0:
            continue
        s = sp.srepr(p)
        if s in seen:
            continue
        seen.add(s)
        polys_unique.append(p)

    info: dict = {
        "n": n,
        "use_column_pucker": use_column_pucker,
        "num_polys": len(polys),
        "num_polys_unique": len(polys_unique),
        "num_free_vars": len(free),
    }
    t0 = time.time()
    try:
        G = groebner(polys_unique, *free, order=grevlex, domain="QQ")
        info["elapsed_sec"] = time.time() - t0
        info["basis_size"] = len(G)
        info["is_trivial_one"] = (len(G) == 1 and G[0] == 1)
        info["basis_repr"] = [str(p) for p in list(G)[:8]]
    except Exception as exc:  # pragma: no cover
        info["elapsed_sec"] = time.time() - t0
        info["error"] = f"{type(exc).__name__}: {exc}"
    return info


def run_column_pucker_only_groebner(
    rows: Pattern,
    n: int,
) -> dict:
    """Run Groebner on ONLY the column-Plucker (eliminated) polynomials.

    Without the row equations, this is a strict subsystem. If its Groebner
    basis is {1} the column-Plucker subsystem alone is unsolvable; this
    would be a NEW exact obstruction (since the row Groebner already kills
    these patterns, but at higher cost).

    HOWEVER: as documented in docs/paraboloid-lift-attack.md, after c_i
    elimination the column-Plucker polys are formal multiples of the row
    polys. We expect this Groebner to be NOT trivial: it has the full
    realisation locus as one of its components, plus the q_j=0 degenerate
    component.
    """
    xs = [Symbol(f"x{i}") for i in range(n)]
    ys = [Symbol(f"y{i}") for i in range(n)]
    subs = gauge_substitution(xs, ys)
    free = [v for v in (*xs[2:], *ys[2:]) if v not in subs]

    polys: list[sp.Expr] = [
        p for _, _, p in column_determinant_polys_eliminated(rows, n, gauge=True)
    ]
    seen = set()
    polys_unique: list[sp.Expr] = []
    for p in polys:
        if p == 0:
            continue
        s = sp.srepr(p)
        if s in seen:
            continue
        seen.add(s)
        polys_unique.append(p)

    info: dict = {
        "n": n,
        "num_polys": len(polys),
        "num_polys_unique": len(polys_unique),
        "num_free_vars": len(free),
    }
    t0 = time.time()
    try:
        G = groebner(polys_unique, *free, order=grevlex, domain="QQ")
        info["elapsed_sec"] = time.time() - t0
        info["basis_size"] = len(G)
        info["is_trivial_one"] = (len(G) == 1 and G[0] == 1)
        info["basis_repr"] = [str(p) for p in list(G)[:8]]
    except Exception as exc:  # pragma: no cover
        info["elapsed_sec"] = time.time() - t0
        info["error"] = f"{type(exc).__name__}: {exc}"
    return info


def column_determinant_rank_summary(
    rows: Pattern,
    n: int,
) -> dict:
    """Linear-algebraic summary of the column-determinant matrix of free
    polynomials evaluated symbolically.

    For each vertex j with d_j >= 4, count the number of 4-subsets of
    incidents and the unique polynomial identities they produce. Also report
    the total polynomial count and the witnessed support.
    """
    entries = column_determinant_polys(rows, n, gauge=True)
    by_j: dict[int, int] = {}
    for j, _, p in entries:
        if p == 0:
            continue
        by_j[j] = by_j.get(j, 0) + 1
    return {
        "total_nonzero_column_dets": len(entries),
        "per_vertex_j": by_j,
    }


def incidence_matrix_rank_diagnostics(rows: Pattern, n: int) -> dict:
    """Combinatorial-rank diagnostics for the incidence matrix B.

    B[i, j] = 1 if j is in S_i, else 0. Rank over QQ and over GF(2). These
    are NOT obstructions on their own; they are recorded as fingerprints
    that often correlate with realisability obstacles.

    Conjectural connection (paraboloid lift): if B has full row rank n over
    QQ, the incidence pattern is "generic" enough that the lifted-plane
    system, combined with paraboloid quadricity, often forces unrealisability
    -- but this is only a heuristic. Empirically we record the rank over
    the integers and the elementary divisors of B^T B.
    """
    witnesses = _row_witness_lists(rows, n)
    B = sp.zeros(n, n)
    for i, S_i in enumerate(witnesses):
        for j in S_i:
            B[i, j] = 1
    rank_q = int(B.rank())
    # Rank over GF(2)
    B_mod2 = sp.Matrix(n, n, lambda i, j: int(B[i, j]) % 2)
    # SymPy GF rank: compute via .rank(simplify=...) over QQ then mod 2 via
    # echelon form
    rref_mod2, _ = B_mod2.rref(simplify=lambda x: x % 2)
    rank_gf2 = sum(1 for i in range(n) if any(rref_mod2[i, j] % 2 != 0 for j in range(n)))
    btb = B.T * B
    elem_divs = btb.singular_values()
    return {
        "rank_QQ": rank_q,
        "rank_GF2": rank_gf2,
        "BtB_singular_values_str": [str(v) for v in elem_divs],
    }


def column_determinant_indegree(rows: Pattern, n: int) -> dict[int, int]:
    """Return d_j = |{ i : j in S_i }| for each vertex j."""
    witnesses = _row_witness_lists(rows, n)
    out = {j: 0 for j in range(n)}
    for S_i in witnesses:
        for j in S_i:
            out[j] += 1
    return out


def normalise_pattern(rows: Iterable, n: int) -> list[list[int]]:
    """Accept the project's two pattern shapes and return witness lists.

    * 0/1 incidence matrix (length n per row).
    * List of selected witness indices (length 4 per row).
    """
    return _row_witness_lists(list(rows), n)
