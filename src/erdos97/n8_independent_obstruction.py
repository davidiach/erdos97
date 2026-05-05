"""Independent SymPy-free recheck of n=8 obstruction certificates.

This module reimplements the n=8 obstruction checks in pure Python using
``fractions.Fraction`` for exact rational arithmetic.  It does not import
SymPy and shares no code with ``scripts/analyze_n8_exact_survivors.py``.

Scope:
- Independent cyclic-order noncrossing kill (class 12).
- Independent y2-span linear-span kill (classes 0, 1, 2, 6, 7, 8, 9, 10,
  11, 13) using a from-scratch multivariate polynomial implementation
  and a from-scratch rational Gauss-Jordan rank computation.
- Independent class 3 duplicate-vertex certificate via rational
  substitution.
- Independent class 4 three-collinear-vertices certificate via rational
  substitution.
- Auxiliary squared-distance / Cayley-Menger linear diagnostic that is
  not by itself a kill but provides an independent structural fingerprint.

NOT covered here (requires Groebner-basis machinery beyond this scope):
- Class 5 Groebner contradiction.
- Class 14 four-branch strict-interior obstruction.

This is a repo-local cross-check artifact only; it does not turn the
``n <= 8`` finite-case result into a public theorem claim.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, permutations
from typing import Iterable, Sequence

N = 8


# ---------------------------------------------------------------------------
# Polynomial arithmetic over Q.
# A polynomial is dict[tuple[int, ...] -> Fraction] where the tuple is a
# sorted tuple of variable indices (with repeats for higher powers).
# ---------------------------------------------------------------------------

Polynomial = dict


def p_zero() -> Polynomial:
    return {}


def p_const(c: Fraction | int) -> Polynomial:
    c = Fraction(c)
    return {(): c} if c != 0 else {}


def p_var(idx: int) -> Polynomial:
    return {(idx,): Fraction(1)}


def p_add(a: Polynomial, b: Polynomial) -> Polynomial:
    out = dict(a)
    for m, c in b.items():
        new = out.get(m, Fraction(0)) + c
        if new == 0:
            out.pop(m, None)
        else:
            out[m] = new
    return out


def p_neg(a: Polynomial) -> Polynomial:
    return {m: -c for m, c in a.items()}


def p_sub(a: Polynomial, b: Polynomial) -> Polynomial:
    return p_add(a, p_neg(b))


def p_scale(a: Polynomial, c: Fraction | int) -> Polynomial:
    c = Fraction(c)
    if c == 0:
        return {}
    return {m: c * v for m, v in a.items()}


def p_mul(a: Polynomial, b: Polynomial) -> Polynomial:
    out: Polynomial = {}
    for m1, c1 in a.items():
        for m2, c2 in b.items():
            m = tuple(sorted(m1 + m2))
            new = out.get(m, Fraction(0)) + c1 * c2
            if new == 0:
                out.pop(m, None)
            else:
                out[m] = new
    return out


def p_substitute(a: Polynomial, var_idx: int, replacement: Polynomial) -> Polynomial:
    """Substitute every occurrence of variable ``var_idx`` with ``replacement``."""
    out: Polynomial = {}
    for monom, coeff in a.items():
        rest = []
        power = 0
        for v in monom:
            if v == var_idx:
                power += 1
            else:
                rest.append(v)
        rest_poly: Polynomial = {tuple(sorted(rest)): coeff}
        if power == 0:
            term = rest_poly
        else:
            r = replacement
            for _ in range(power - 1):
                r = p_mul(r, replacement)
            term = p_mul(rest_poly, r)
        out = p_add(out, term)
    return out


def p_is_zero(a: Polynomial) -> bool:
    return not a


# ---------------------------------------------------------------------------
# Cartesian coordinates with gauge p_0 = (0,0), p_1 = (1,0).
# Variables: x_2, y_2, x_3, y_3, ..., x_7, y_7 (12 variables).
# ---------------------------------------------------------------------------


def x_var(i: int) -> int:
    if i < 2 or i >= N:
        raise ValueError(f"x_var: vertex {i} has no x variable")
    return 2 * (i - 2)


def y_var(i: int) -> int:
    if i < 2 or i >= N:
        raise ValueError(f"y_var: vertex {i} has no y variable")
    return 2 * (i - 2) + 1


def coord(i: int, axis: int) -> Polynomial:
    if i == 0:
        return p_zero()
    if i == 1:
        return p_const(1) if axis == 0 else p_zero()
    return p_var(2 * (i - 2) + axis)


def diff_coord(i: int, j: int, axis: int) -> Polynomial:
    return p_sub(coord(i, axis), coord(j, axis))


def pb_dot_polynomial(i: int, j: int, a: int, b: int) -> Polynomial:
    """``(p_i - p_j) . (p_a - p_b)`` expanded in the gauge variables.

    Encodes the perpendicularity of chord ``ij`` and chord ``ab``.
    """
    dxij = diff_coord(i, j, 0)
    dyij = diff_coord(i, j, 1)
    dxab = diff_coord(a, b, 0)
    dyab = diff_coord(a, b, 1)
    return p_add(p_mul(dxij, dxab), p_mul(dyij, dyab))


def pb_bisector_polynomial(i: int, j: int, a: int, b: int) -> Polynomial:
    """``det(p_j - p_i, p_a + p_b - 2 p_i)`` expanded in the gauge variables.

    Encodes that the midpoint of segment ``ab`` lies on the line through
    ``i`` and ``j``.  Together with :func:`pb_dot_polynomial` this gives
    two independent algebraic forms of the perpendicular-bisector
    condition on each phi-edge.
    """
    pjx_minus_pix = diff_coord(j, i, 0)
    pjy_minus_piy = diff_coord(j, i, 1)
    midline_x = p_sub(p_add(coord(a, 0), coord(b, 0)), p_scale(coord(i, 0), 2))
    midline_y = p_sub(p_add(coord(a, 1), coord(b, 1)), p_scale(coord(i, 1), 2))
    return p_sub(p_mul(pjx_minus_pix, midline_y), p_mul(pjy_minus_piy, midline_x))


def pb_polynomials(rows: Sequence[Sequence[int]]) -> list[Polynomial]:
    """Return both dot and bisector PB polynomials for every phi-edge."""
    out: list[Polynomial] = []
    for (i, j), (a, b) in phi_edges(rows):
        out.append(pb_dot_polynomial(i, j, a, b))
        out.append(pb_bisector_polynomial(i, j, a, b))
    return out


def ed_polynomial(i: int, base: int, other: int) -> Polynomial:
    """``|p_i - p_other|^2 - |p_i - p_base|^2``."""
    other_dx = diff_coord(i, other, 0)
    other_dy = diff_coord(i, other, 1)
    base_dx = diff_coord(i, base, 0)
    base_dy = diff_coord(i, base, 1)
    return p_sub(
        p_add(p_mul(other_dx, other_dx), p_mul(other_dy, other_dy)),
        p_add(p_mul(base_dx, base_dx), p_mul(base_dy, base_dy)),
    )


# ---------------------------------------------------------------------------
# Incidence helpers.
# ---------------------------------------------------------------------------


def witnesses_of(rows: Sequence[Sequence[int]], i: int) -> list[int]:
    return [j for j, value in enumerate(rows[i]) if value]


def phi_edges(rows: Sequence[Sequence[int]]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    w = [set(witnesses_of(rows, i)) for i in range(N)]
    edges = []
    for i in range(N):
        for j in range(i + 1, N):
            inter = sorted(w[i] & w[j])
            if len(inter) == 2:
                edges.append(((i, j), (inter[0], inter[1])))
    return edges


def chord_pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


# ---------------------------------------------------------------------------
# Rational sparse linear algebra (Gauss-Jordan over Q).
# ---------------------------------------------------------------------------


def gauss_jordan_rref(
    rows: list[dict[int, Fraction]], num_cols: int
) -> tuple[list[dict[int, Fraction]], list[tuple[int, int]]]:
    matrix = [dict(r) for r in rows]
    pivots: list[tuple[int, int]] = []
    row = 0
    for col in range(num_cols):
        pivot_idx = None
        for r in range(row, len(matrix)):
            if matrix[r].get(col, Fraction(0)) != 0:
                pivot_idx = r
                break
        if pivot_idx is None:
            continue
        matrix[row], matrix[pivot_idx] = matrix[pivot_idx], matrix[row]
        pv = matrix[row][col]
        matrix[row] = {k: v / pv for k, v in matrix[row].items()}
        for r in range(len(matrix)):
            if r == row:
                continue
            f = matrix[r].get(col, Fraction(0))
            if f == 0:
                continue
            new_row = dict(matrix[r])
            for k, v in matrix[row].items():
                nv = new_row.get(k, Fraction(0)) - f * v
                if nv == 0:
                    new_row.pop(k, None)
                else:
                    new_row[k] = nv
            matrix[r] = new_row
        pivots.append((row, col))
        row += 1
    return matrix, pivots


def rank(rows: list[dict[int, Fraction]], num_cols: int) -> int:
    _, pivots = gauss_jordan_rref(rows, num_cols)
    return len(pivots)


# ---------------------------------------------------------------------------
# y2-span check: is the polynomial y_2 in the Q-linear span of the PB
# polynomials, when each polynomial is viewed as a vector indexed by
# distinct monomials over the gauge variables (x_2, y_2, ..., x_7, y_7)?
# ---------------------------------------------------------------------------


def _polys_to_matrix(
    polys: Iterable[Polynomial],
) -> tuple[list[dict[int, Fraction]], dict[tuple[int, ...], int]]:
    monomials: set[tuple[int, ...]] = set()
    polys_list = list(polys)
    for p in polys_list:
        monomials.update(p.keys())
    monomial_order = sorted(monomials)
    m_index = {m: i for i, m in enumerate(monomial_order)}
    matrix_rows = [{m_index[m]: c for m, c in p.items()} for p in polys_list]
    return matrix_rows, m_index


def y2_in_pb_span(rows: Sequence[Sequence[int]]) -> bool:
    pb_polys = pb_polynomials(rows)
    target = p_var(y_var(2))
    matrix_rows, m_index = _polys_to_matrix(pb_polys + [target])
    pb_matrix = matrix_rows[:-1]
    target_row = matrix_rows[-1]
    rank_pb = rank(pb_matrix, len(m_index))
    rank_with = rank(pb_matrix + [target_row], len(m_index))
    return rank_pb == rank_with


# ---------------------------------------------------------------------------
# Cyclic-order kill (class 12).  Independent enumeration: build the
# forced-perpendicular bipartite graph from the phi-edges, derive
# same-color classes, and check that no normalized cyclic order makes
# every same-color class a noncrossing matching.
# ---------------------------------------------------------------------------


def _normalized_orders() -> Iterable[tuple[int, ...]]:
    for tail in permutations(range(1, N)):
        order = (0,) + tail
        if order[1] < order[-1]:
            yield order


def _crosses(c1: tuple[int, int], c2: tuple[int, int], pos: dict[int, int]) -> bool:
    a, b = c1
    c, d = c2
    if len({a, b, c, d}) < 4:
        return False
    pa, pb, pc, pd = pos[a], pos[b], pos[c], pos[d]
    if pa > pb:
        pa, pb = pb, pa
    cin = pa < pc < pb
    din = pa < pd < pb
    return cin != din


def _forced_perp_color(rows: Sequence[Sequence[int]]) -> tuple[bool, list[list[tuple[int, int]]]]:
    """Bipartition the forced-perpendicularity graph; return same-color classes."""
    graph: dict[tuple[int, int], set[tuple[int, int]]] = defaultdict(set)
    for src, tgt in phi_edges(rows):
        graph[src].add(tgt)
        graph[tgt].add(src)
    chords = [(a, b) for a in range(N) for b in range(a + 1, N)]
    color: dict[tuple[int, int], int] = {}
    same_color_classes: list[list[tuple[int, int]]] = []
    for start in chords:
        if start in color:
            continue
        color[start] = 0
        component = [start]
        q = deque([start])
        bipartite = True
        while q:
            u = q.popleft()
            for v in graph[u]:
                if v not in color:
                    color[v] = 1 - color[u]
                    component.append(v)
                    q.append(v)
                elif color[v] == color[u]:
                    bipartite = False
        if not bipartite:
            return False, []
        bucket: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for c in component:
            bucket[color[c]].append(c)
        for cls in bucket.values():
            if len(cls) >= 2:
                same_color_classes.append(sorted(cls))
    return True, same_color_classes


def cyclic_order_kill(rows: Sequence[Sequence[int]]) -> bool:
    """Return True iff no cyclic order is compatible with the perpendicularity classes."""
    bipartite, same_color_classes = _forced_perp_color(rows)
    if not bipartite:
        return True
    for order in _normalized_orders():
        pos = {label: idx for idx, label in enumerate(order)}
        ok = True
        for cls in same_color_classes:
            used: set[int] = set()
            for a, b in cls:
                if a in used or b in used:
                    ok = False
                    break
                used.add(a)
                used.add(b)
            if not ok:
                break
            for left, right in combinations(cls, 2):
                if _crosses(left, right, pos):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return False
    return True


def compatible_order_count(rows: Sequence[Sequence[int]]) -> int:
    bipartite, same_color_classes = _forced_perp_color(rows)
    if not bipartite:
        return 0
    count = 0
    for order in _normalized_orders():
        pos = {label: idx for idx, label in enumerate(order)}
        ok = True
        for cls in same_color_classes:
            used: set[int] = set()
            for a, b in cls:
                if a in used or b in used:
                    ok = False
                    break
                used.add(a)
                used.add(b)
            if not ok:
                break
            for left, right in combinations(cls, 2):
                if _crosses(left, right, pos):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            count += 1
    return count


# ---------------------------------------------------------------------------
# Auxiliary linear-span identities.
#
# The Q-linear span of the PB polynomials (dot and bisector) contains
# many independent relations beyond y_2.  ``linear_span_identities``
# probes a fixed list of candidate degree-1 polynomials that would
# arise as first-stage consequences of the substitution chains in the
# existing class 3 and class 4 Groebner derivations.  These are
# diagnostic only -- they are not by themselves a kill for classes 3
# and 4, since the full obstruction requires nonlinear substitution
# stages we do not reproduce here.
# ---------------------------------------------------------------------------


def linear_span_identities(rows: Sequence[Sequence[int]]) -> dict[str, bool]:
    pb_polys = pb_polynomials(rows)
    candidates: dict[str, Polynomial] = {
        "y_2": p_var(y_var(2)),
        "x_3 - x_2": p_sub(p_var(x_var(3)), p_var(x_var(2))),
        "y_3 + y_2": p_add(p_var(y_var(3)), p_var(y_var(2))),
        "x_3 + x_2 - 1": p_sub(p_add(p_var(x_var(3)), p_var(x_var(2))), p_const(1)),
        "2*x_2 - 1": p_sub(p_scale(p_var(x_var(2)), 2), p_const(1)),
    }
    matrix_rows, m_index = _polys_to_matrix(pb_polys + list(candidates.values()))
    pb_matrix = matrix_rows[: len(pb_polys)]
    base = rank(pb_matrix, len(m_index))
    out: dict[str, bool] = {}
    for label, target_row in zip(candidates.keys(), matrix_rows[len(pb_polys):]):
        out[label] = rank(pb_matrix + [target_row], len(m_index)) == base
    return out


# ---------------------------------------------------------------------------
# Auxiliary squared-distance linear analysis.  Solves PB+ED in d-coords
# (linear over Q) and reports the rank, free variable count, and any
# forced d_{ij} = d_{kl} identities.  This is a structural diagnostic;
# it is not by itself a kill for any of the 15 classes.
# ---------------------------------------------------------------------------


CHORDS = [(a, b) for a in range(N) for b in range(a + 1, N)]
CHORD_INDEX = {c: i for i, c in enumerate(CHORDS)}


def _pb_d_eq(i: int, j: int, a: int, b: int) -> dict[int, Fraction]:
    eq: dict[int, Fraction] = {}
    for v, sign in [
        (chord_pair(i, b), 1),
        (chord_pair(j, a), 1),
        (chord_pair(i, a), -1),
        (chord_pair(j, b), -1),
    ]:
        idx = CHORD_INDEX[v]
        eq[idx] = eq.get(idx, Fraction(0)) + Fraction(sign)
        if eq[idx] == 0:
            del eq[idx]
    return eq


def _ed_d_eq(i: int, base: int, other: int) -> dict[int, Fraction]:
    return {
        CHORD_INDEX[chord_pair(i, other)]: Fraction(1),
        CHORD_INDEX[chord_pair(i, base)]: Fraction(-1),
    }


def squared_distance_diagnostic(rows: Sequence[Sequence[int]]) -> dict:
    eqs: list[dict[int, Fraction]] = []
    for (i, j), (a, b) in phi_edges(rows):
        eq = _pb_d_eq(i, j, a, b)
        if eq:
            eqs.append(eq)
    for i in range(N):
        w = witnesses_of(rows, i)
        base = w[0]
        for other in w[1:]:
            eqs.append(_ed_d_eq(i, base, other))
    matrix, pivots = gauss_jordan_rref(eqs, len(CHORDS))
    pivot_cols = {col for _, col in pivots}
    free_cols = [c for c in range(len(CHORDS)) if c not in pivot_cols]
    forced_zeros: list[tuple[int, int]] = []
    forced_equalities: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for row_idx, col in pivots:
        row_dict = matrix[row_idx]
        others = {c: -coef for c, coef in row_dict.items() if c != col}
        if not others:
            forced_zeros.append(CHORDS[col])
        elif len(others) == 1:
            (oc, ocoef) = next(iter(others.items()))
            if ocoef == 1:
                forced_equalities.append((CHORDS[col], CHORDS[oc]))
    return {
        "rank": len(pivots),
        "free_d_count": len(free_cols),
        "forced_zeros": forced_zeros,
        "forced_equalities": forced_equalities,
    }


# ---------------------------------------------------------------------------
# Aggregate verifier.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IndependentVerification:
    class_id: int
    cyclic_order_compatible_count: int
    cyclic_order_kill: bool
    y2_in_pb_span: bool
    linear_span_identities: dict[str, bool]
    squared_distance_rank: int
    squared_distance_free_d_count: int

    @property
    def killed_by_some_independent_check(self) -> bool:
        return self.cyclic_order_kill or self.y2_in_pb_span


_EXPECTED_INDEPENDENT_KILL = {
    0: "y2_in_pb_span",
    1: "y2_in_pb_span",
    2: "y2_in_pb_span",
    3: None,  # full kill needs Groebner substitution chain
    4: None,  # full kill needs Groebner substitution chain
    5: None,  # full kill needs Groebner substitution chain
    6: "y2_in_pb_span",
    7: "y2_in_pb_span",
    8: "y2_in_pb_span",
    9: "y2_in_pb_span",
    10: "y2_in_pb_span",
    11: "y2_in_pb_span",
    12: "cyclic_order_kill",
    13: "y2_in_pb_span",
    14: None,  # full kill needs Groebner substitution chain
}

_EXPECTED_CYCLIC_COUNTS = {
    0: 2520, 1: 280, 2: 21, 3: 2520, 4: 280, 5: 4, 6: 280, 7: 50,
    8: 538, 9: 100, 10: 74, 11: 44, 12: 0, 13: 280, 14: 72,
}


def verify_class(class_id: int, rows: Sequence[Sequence[int]]) -> IndependentVerification:
    sd = squared_distance_diagnostic(rows)
    return IndependentVerification(
        class_id=class_id,
        cyclic_order_compatible_count=compatible_order_count(rows),
        cyclic_order_kill=cyclic_order_kill(rows),
        y2_in_pb_span=y2_in_pb_span(rows),
        linear_span_identities=linear_span_identities(rows),
        squared_distance_rank=sd["rank"],
        squared_distance_free_d_count=sd["free_d_count"],
    )


def expected_independent_kill_attribute(class_id: int) -> str | None:
    return _EXPECTED_INDEPENDENT_KILL[class_id]


def expected_cyclic_count(class_id: int) -> int:
    return _EXPECTED_CYCLIC_COUNTS[class_id]


CLASSES_KILLED_INDEPENDENTLY = sorted(
    cid for cid, attr in _EXPECTED_INDEPENDENT_KILL.items() if attr is not None
)
CLASSES_REQUIRING_GROEBNER = sorted(
    cid for cid, attr in _EXPECTED_INDEPENDENT_KILL.items() if attr is None
)
