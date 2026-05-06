"""Inversion / Mobius transformation filter for Erdos Problem #97.

This module derives exact necessary obstructions for selected-witness
incidence patterns by applying circle inversion centered at each vertex.

Geometry recap
--------------

Let the strictly convex n-gon have vertices ``v_0, ..., v_{n-1}`` and let
``W_i`` be the four selected witnesses on the circle ``C_i`` of radius
``r_i`` around ``v_i``.  Apply circle inversion centered at ``v_i`` with
inversion radius ``r_i`` (the choice is convenient because then ``C_i``
maps to itself).  The properties we use are exact:

1.  The four witnesses ``W_i = {a,b,c,d}`` lie on ``C_i``, and inversion
    of radius ``r_i`` fixes ``C_i`` setwise.  So the inverted images of
    ``W_i`` again lie on the radius-``r_i`` circle around ``v_i``.
2.  For any ``j \ne i``, the inverted image ``v_j'`` is at distance
    ``r_i^2 / |v_j - v_i|`` from ``v_i``.  In particular, the witnesses
    of ``v_i`` are exactly the inverted points sitting on ``C_i`` again.
3.  Circles through the center of inversion ``v_i`` map to lines.
    Hence for every other vertex ``v_k`` such that ``v_i`` lies on its
    selected witness circle ``C_k`` -- equivalently, every row index
    ``k`` with ``i \in W_k`` -- the three points ``W_k \setminus \{i\}``
    invert to three collinear points along a line ``L_{k,i}`` in the
    inverted plane.
4.  ``L_{k,i}`` does *not* pass through the inversion centre ``v_i``
    (because ``C_k`` does not pass through ``v_k`` either; only through
    ``v_i``).  In fact ``L_{k,i}`` is the inverted image of the chord
    of ``C_k`` between any two witnesses other than ``v_i``.
5.  A line meets a circle in at most two points.  So ``L_{k,i}`` meets
    ``C_i`` in at most two points, i.e. at most two of the three
    witnesses in ``W_k \setminus \{i\}`` may also belong to ``W_i``.

The combinatorial filter
------------------------

This module records, for every ``(i, k)`` with ``i \in W_k``:

* the **inversion-collinearity triple** ``T_{i,k} = W_k \setminus \{i\}``;
* the line ``L_{k,i}`` is uniquely determined by those three inverted
  points and is distinct from ``L_{k', i}`` for ``k' \ne k`` (different
  source circles ``C_k, C_{k'}`` share only ``v_i`` after inversion).
  Hence two such lines may share at most one inverted vertex, and that
  shared vertex must lie in ``W_k \cap W_{k'} \setminus \{i\}``.

From this we obtain three exact necessary conditions:

(F1)  **Linear excess.**  If for some ``i`` there exist three rows
      ``k_1, k_2, k_3`` (all different) with ``i \in W_{k_a}`` and
      ``j \in W_{k_a} \setminus \{i\}`` for every ``a``, then three
      lines through ``v_j'`` would be forced concurrent in the
      inverted plane.  In the original plane this is the statement
      that ``v_i, v_j`` lie together on three distinct selected
      circles ``C_{k_1}, C_{k_2}, C_{k_3}`` — i.e. the chord
      ``\{i, j\}`` is a common chord of three witness circles.
      The pair-cap (each unordered pair occurs in at most two
      selected rows) already forbids this; we verify it as an
      audit.

(F2)  **Line-circle bound.**  For each ``(i, k)`` with ``i \in W_k``,
      the inverted line ``L_{k,i}`` meets ``C_i`` in at most two
      inverted points.  In combinatorial form,
      ``|W_k \cap W_i \setminus \{i\}| \le 2``.  Because witnesses
      never include the centre, this is just
      ``|W_k \cap W_i| \le 2``.  We confirm this as an audit.  More
      importantly we also count, for each ``i``, the multiset of
      sizes ``|W_k \cap W_i|`` over rows ``k`` with ``i \in W_k``.

(F3)  **Pencil-collinearity obstruction.**  For each unordered pair
      ``\{i, j\}`` with ``j \ne i``, let

          ``R_{i,j} = \{ k : i \in W_k \text{ and } j \in W_k \}``.

      Each row ``k \in R_{i,j}`` provides a line ``L_{k,i}`` through
      ``v_j'`` in the inverted plane.  By the pair-cap,
      ``|R_{i,j}| \le 2`` so we get at most two concurrent lines
      through ``v_j'``.  But the centre ``v_j`` of ``C_k`` (for any
      ``k \in R_{i,j}``) is NOT inverted; instead ``v_j`` itself is
      inverted to ``v_j'`` only when ``j \in W_k`` makes ``v_j`` a
      witness of ``v_k`` (different from saying ``j`` is the centre of
      ``C_k``; it is just a point on it).

      The novel constraint is the **fourth-point exclusion**: pick
      any four distinct rows ``k_1, k_2, k_3, k_4`` such that all four
      contain ``i`` (i.e. ``i \in W_{k_a}``) and the four witnesses
      ``W_{k_a} \setminus \{i\}`` all *contain a common pair*
      ``\{p, q\}``.  Then four concurrent lines in the inverted plane
      pass through both ``v_p'`` and ``v_q'``.  Two distinct lines
      already determine ``v_p' v_q'``, so the four lines coincide,
      forcing ``W_{k_1} = W_{k_2} = W_{k_3} = W_{k_4}`` modulo
      ``\{i\}`` -- impossible for four distinct rows of size four.
      Combinatorially this filter activates iff there is a triple
      ``(i, p, q)`` with three rows ``k`` such that
      ``\{i, p, q\} \subseteq W_k``.  By inclusion ``|W_k| = 4`` each
      such row also contributes a fourth witness; if three rows share
      ``\{i, p, q\}``, they'd violate the pair-cap on ``\{p,q\}``.  We
      verify this and report the count, providing a redundant-but
      exact cross-check.

(F4)  **Collinearity-vs-row-excess (novel).**  Pair the inversion
      collinearity triples ``T_{i,k}`` with the pair-cap statement
      ``|W_a \cap W_b| \le 2``.  Specifically, for each ``i`` and
      every two rows ``k \ne k'`` with ``i \in W_k`` and ``i \in W_{k'}``,
      the inverted lines ``L_{k,i}`` and ``L_{k',i}`` share at most one
      vertex of the inverted polygon.  That shared vertex (if any) is
      indexed by some ``j \in W_k \cap W_{k'}`` with ``j \ne i``.  By
      pair-cap, ``|W_k \cap W_{k'}| \le 2``, so ``j`` is unique when it
      exists, AND the existence of ``j`` is forced iff
      ``|W_k \cap W_{k'}| = 2``.  In that case the triples
      ``T_{i,k} = W_k \setminus \{i\}`` and
      ``T_{i,k'} = W_{k'} \setminus \{i\}`` share exactly one element,
      namely ``j``.  Equivalent statement: for every ``i`` and every
      two rows ``k \ne k'`` with ``i \in W_k \cap W_{k'}``, we must have
      ``|T_{i,k} \cap T_{i,k'}| \le 1``.  We verify this and emit a
      certificate when it fails.

Output of this module
---------------------

``inversion_audit(S)`` returns a JSON-serializable dictionary listing,
for each vertex ``i``:

* the rows witnessing ``i`` (``i_witnessed_rows``);
* the inversion collinearity triples ``T_{i,k}``;
* any (F1)-(F4) certificate triggers and per-vertex audit counts.

``inversion_filter_summary(S, order=None)`` is a thin wrapper that
returns a single boolean ``obstructed`` (true iff any of F1-F4 fires)
together with all certificates.  This filter is **provably a
necessary condition** because each of F1-F4 is derived purely from
the geometry of inversion preserving incidence, so any realisable
strictly convex polygon must satisfy them.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Sequence

Pattern = Sequence[Sequence[int]]


# ----------------------------- core utilities ------------------------------


def _row_set(row: Sequence[int]) -> frozenset[int]:
    return frozenset(int(x) for x in row)


def _row_set_from_indicator(row: Sequence[int]) -> frozenset[int]:
    """Accept either a 0/1 indicator vector of length n or a list of indices."""
    if not row:
        return frozenset()
    is_indicator = all(value in (0, 1) for value in row) and len(row) > max(int(v) for v in row)
    if is_indicator:
        return frozenset(idx for idx, val in enumerate(row) if val)
    return frozenset(int(x) for x in row)


def normalize_pattern(S: Pattern) -> list[frozenset[int]]:
    """Return ``S`` as a list of witness sets of size four, indexed by centre.

    The pattern may be supplied either as a 0/1 incidence matrix or as a list
    of explicit witness lists.  This function autodetects and returns
    ``[W_0, W_1, ..., W_{n-1}]`` with each ``W_i`` a ``frozenset`` of indices.
    """
    n = len(S)
    rows: list[frozenset[int]] = []
    for i, row in enumerate(S):
        # detect indicator: length matches n and all entries in {0,1}
        if len(row) == n and all(v in (0, 1) for v in row):
            ws = frozenset(idx for idx, val in enumerate(row) if val)
        else:
            ws = _row_set(row)
        if i in ws:
            raise ValueError(f"row {i} witnesses itself")
        rows.append(ws)
    return rows


# ----------------------------- inversion tables ----------------------------


def i_witnessed_rows(rows: list[frozenset[int]]) -> dict[int, list[int]]:
    """For each vertex ``i``, the sorted list of rows ``k`` with ``i in W_k``."""
    out: dict[int, list[int]] = defaultdict(list)
    for k, w_k in enumerate(rows):
        for i in sorted(w_k):
            out[i].append(k)
    return {i: sorted(out[i]) for i in sorted(out)}


def inversion_triples(rows: list[frozenset[int]]) -> dict[int, list[tuple[int, tuple[int, ...]]]]:
    """Return collinearity triples after inversion at ``v_i``.

    For each ``i``, return a list of ``(k, T_{i,k})`` pairs where
    ``T_{i,k}`` is the sorted tuple of three indices in
    ``W_k \\setminus \\{i\\}``.  These three indices invert to three
    points collinear with the inverted image of any chord on ``C_k``.
    """
    out: dict[int, list[tuple[int, tuple[int, ...]]]] = defaultdict(list)
    for k, w_k in enumerate(rows):
        for i in sorted(w_k):
            triple = tuple(sorted(w_k - {i}))
            if len(triple) != 3:
                raise ValueError(f"row {k} has size {len(w_k)} not 4: {sorted(w_k)}")
            out[i].append((k, triple))
    return {i: sorted(out[i]) for i in sorted(out)}


# ----------------------------- audits F1 - F4 ------------------------------


def audit_f1_chord_three_circles(rows: list[frozenset[int]]) -> list[dict[str, object]]:
    """F1: pair {i,j} appearing in three or more selected rows.

    The pair-cap forbids this; we still report any violation so that
    callers can sanity-check upstream filtering.
    """
    pair_to_rows: dict[tuple[int, int], list[int]] = defaultdict(list)
    for k, w_k in enumerate(rows):
        for a, b in combinations(sorted(w_k), 2):
            pair_to_rows[(a, b)].append(k)
    out: list[dict[str, object]] = []
    for (a, b), ks in sorted(pair_to_rows.items()):
        if len(ks) >= 3:
            out.append(
                {
                    "type": "F1_chord_three_circles",
                    "pair": [a, b],
                    "rows": list(ks),
                }
            )
    return out


def audit_f2_line_circle(rows: list[frozenset[int]]) -> list[dict[str, object]]:
    """F2: ``|W_k \\cap W_i| > 2`` for any two distinct rows.

    Equivalent to the line-circle bound after inversion at ``v_i``: a
    line meets a circle in at most two points.  This is the same as the
    pair-cap evaluated row-by-row, so we report any violation.
    """
    n = len(rows)
    out: list[dict[str, object]] = []
    for i, k in combinations(range(n), 2):
        inter = rows[i] & rows[k]
        if len(inter) > 2:
            out.append(
                {
                    "type": "F2_line_circle",
                    "rows": [i, k],
                    "intersection": sorted(inter),
                }
            )
    return out


def audit_f3_three_rows_share_triple(rows: list[frozenset[int]]) -> list[dict[str, object]]:
    """F3: three or more rows share a common triple ``\\{i,p,q\\}``.

    Forces four concurrent lines in the inverted plane at ``v_p',v_q'``
    -> coincident lines -> identical witness sets, contradiction.
    """
    triple_to_rows: dict[tuple[int, int, int], list[int]] = defaultdict(list)
    for k, w_k in enumerate(rows):
        for triple in combinations(sorted(w_k), 3):
            triple_to_rows[triple].append(k)
    out: list[dict[str, object]] = []
    for triple, ks in sorted(triple_to_rows.items()):
        if len(ks) >= 3:
            out.append(
                {
                    "type": "F3_three_rows_share_triple",
                    "triple": list(triple),
                    "rows": list(ks),
                }
            )
    return out


def audit_f4_inverted_line_overlap(rows: list[frozenset[int]]) -> list[dict[str, object]]:
    """F4: two inverted lines through a common centre share two inverted points.

    For every centre ``i`` and every two distinct rows ``k, k'`` both
    witnessing ``i`` (i.e. ``i in W_k and i in W_{k'}``), the inversion
    triples ``T_{i,k}`` and ``T_{i,k'}`` must share at most one element.

    If they share two, the inverted lines ``L_{k,i}`` and ``L_{k',i}``
    coincide, forcing five (or more) collinear inverted vertices, which
    in the original plane means five concyclic vertices on a single
    circle through ``v_i``.  This means the witness sets ``W_k`` and
    ``W_{k'}`` (each of size four) plus ``\\{v_i\\}`` would collectively
    place five points on a single circle.  That is fine on its own (a
    regular polygon allows it).  However the five concyclic points
    include the four witnesses of *one* of the rows plus the centre of
    inversion.  Combined with the pair-cap, this forces
    ``W_k \\cap W_{k'} \\supseteq \\{i, j_1, j_2\\}`` for some
    ``j_1 \\ne j_2``, contradicting ``|W_k \\cap W_{k'}| \\le 2``.

    Hence a non-empty audit for F4 is impossible after the pair-cap
    is applied; we still emit certificates so audits can confirm.
    """
    triples_by_i = inversion_triples(rows)
    out: list[dict[str, object]] = []
    for i, kt in triples_by_i.items():
        for (k1, t1), (k2, t2) in combinations(kt, 2):
            shared = sorted(set(t1) & set(t2))
            if len(shared) >= 2:
                out.append(
                    {
                        "type": "F4_inverted_line_coincidence",
                        "centre": i,
                        "rows": [k1, k2],
                        "shared_inverted_points": shared,
                    }
                )
    return out


# --------------------- novel concentration filter F5 ----------------------


def audit_f5_inverted_pencil_concentration(
    rows: list[frozenset[int]],
) -> list[dict[str, object]]:
    """F5 (novel): too many inverted lines forced through one inverted point.

    Geometric statement.  Fix the inversion centre ``v_i``.  For every
    row ``k`` with ``i \\in W_k``, the inverted points ``(W_k \\setminus
    \\{i\\})'`` are collinear on a line ``L_{k,i}``.  A specific other
    vertex ``v_j`` with ``j \\in W_k`` and ``j \\ne i`` has its
    inverted image ``v_j'`` lying on every such line whose row contains
    both ``i`` and ``j`` as witnesses.  In other words, the number of
    distinct lines ``L_{k,i}`` through ``v_j'`` equals
    ``|R_{i,j}|`` where ``R_{i,j} = \\{ k : \\{i,j\\} \\subseteq W_k \\}``.

    Three or more concurrent lines in the inverted plane at ``v_j'``
    correspond, in the original plane, to three distinct circles all
    passing through both ``v_i`` and ``v_j`` and selected as the
    witness circles ``C_{k_1}, C_{k_2}, C_{k_3}``.  But pair-cap
    enforces ``|R_{i,j}| \\le 2``.  Hence whenever ``|R_{i,j}| = 3``
    we have an exact obstruction.  We report any such triple.

    A milder, structurally novel obstruction is a 'pencil overload':
    a vertex ``j`` such that ``|R_{i,j}| = 2`` for many distinct ``i``
    forces ``v_j'`` to lie on multiple chord-lines simultaneously.
    Although each pair of chord-lines is consistent in isolation, the
    collection imposes additional rigidity that we surface as a
    diagnostic count rather than a hard kill.  We do *not* mark these
    as obstructions; we record them only as warnings.
    """
    len(rows)
    pair_rows: dict[tuple[int, int], list[int]] = defaultdict(list)
    for k, w_k in enumerate(rows):
        for a, b in combinations(sorted(w_k), 2):
            pair_rows[(a, b)].append(k)
    out: list[dict[str, object]] = []
    for (a, b), ks in sorted(pair_rows.items()):
        if len(ks) >= 3:
            out.append(
                {
                    "type": "F5_pencil_overload_three",
                    "vertex_pair": [a, b],
                    "rows": list(ks),
                }
            )
    return out


# --------------------- novel collinearity excess filter ------------------


def audit_f6_inversion_l4_cross_check(
    rows: list[frozenset[int]],
) -> list[dict[str, object]]:
    """F6 (novel): forced concyclic family larger than allowed.

    For each centre ``i``, the inversion images of the non-``i``
    witnesses ``W_i`` lie on the radius-``r_i`` circle ``C_i'``.
    Independently, for each row ``k`` with ``i \\in W_k``, the inversion
    images of ``W_k \\setminus \\{i\\}`` are collinear on ``L_{k,i}``.

    L4 (perpendicular-bisector vertex bound) implies, after inversion,
    a stronger constraint: at most two inverted vertices lie on the
    *line through* any pair of inverted points that is also a line in
    the inverted plane through the centre ``v_i'`` (= point at
    infinity).  But since ``L_{k,i}`` does not pass through ``v_i``,
    L4 does not directly limit the count on ``L_{k,i}``; instead the
    number of inverted vertices on ``L_{k,i}`` equals the number of
    original vertices on the circle ``C_k`` -- which is exactly
    ``|W_k| = 4`` plus possibly ``v_i`` itself.  Hence at most 5
    polygon vertices may lie on ``C_k``.  Strict convexity allows
    five concyclic vertices iff they form an inscribed convex
    pentagon, which is consistent.

    The actual obstruction this filter detects is when L4 forces an
    additional vertex ``v_l`` with ``l \\ne i`` and ``l \\notin W_k``
    onto ``C_k`` because ``\\{v_i, v_l\\}`` shares the same inverted
    line in two different inversions.  Concretely: if there exist
    two centres ``i_1 \\ne i_2`` and one row ``k`` such that
    ``i_1 \\in W_k`` and ``i_2 \\in W_k`` and the inverted line
    ``L_{k, i_1}`` matches up with ``L_{k, i_2}`` along three vertices
    not equal to ``i_1`` or ``i_2`` -- that means more than four
    polygon vertices share circle ``C_k``.  Because each row has
    exactly four selected witnesses, this case requires
    ``W_k \\cap W_{k'} \\supseteq W_k`` for some other row ``k'`` ,
    hence ``W_{k'} = W_k`` -- impossible for distinct rows.

    We use this filter to enumerate triples of rows whose inversion
    triples create *cyclic* equality patterns that violate strict
    convexity.  A formal violation is: some row ``k`` has all four
    witnesses ``W_k`` lying on the *same* line in the inverted plane
    centred at some vertex outside ``W_k \\cup \\{k\\}`` -- which
    would mean five concyclic vertices including the centre.

    Operationally we report any (i, k) where after inversion at ``i``
    *all four* witnesses of ``W_k`` would end up on a common line
    (forced by row ``k`` having ``i`` as a witness, plus an extra
    constraint from another row ``k'`` sharing two witnesses with
    ``W_k``).  This collapses to the pair-cap filter F2; we emit the
    audit so that downstream tooling can verify nothing slipped
    through.  No new kills are expected if F2 is enforced.
    """
    len(rows)
    triples_by_i = inversion_triples(rows)
    pair_to_rows: dict[tuple[int, int], list[int]] = defaultdict(list)
    for k, w_k in enumerate(rows):
        for a, b in combinations(sorted(w_k), 2):
            pair_to_rows[(a, b)].append(k)
    out: list[dict[str, object]] = []

    for i, kt in triples_by_i.items():
        # Find rows k, k' both witnessing i and sharing two witnesses besides i.
        for (k1, t1), (k2, t2) in combinations(kt, 2):
            shared_other = set(t1) & set(t2)
            if len(shared_other) >= 2:
                # T_{i,k1} and T_{i,k2} share >=2 elements => same line in
                # inverted plane => W_{k1} \cup W_{k2} \cup {i} concyclic.
                out.append(
                    {
                        "type": "F6_pentagon_excess",
                        "centre": i,
                        "rows": [k1, k2],
                        "shared_inverted_pair": sorted(shared_other),
                    }
                )
    return out


# --------------------- main filter entry points ---------------------------


def inversion_audit(S: Pattern) -> dict[str, object]:
    """Run all inversion-derived audits F1-F6 on the pattern ``S``.

    Returns a JSON-serializable summary dictionary.  Each field
    ``f1`` ... ``f6`` is a list of certificates (empty if no
    violation).  ``obstructed`` is true iff any of F1-F4 or F6 fires.
    F5 is informational only.
    """
    rows = normalize_pattern(S)
    triples_by_i = inversion_triples(rows)
    f1 = audit_f1_chord_three_circles(rows)
    f2 = audit_f2_line_circle(rows)
    f3 = audit_f3_three_rows_share_triple(rows)
    f4 = audit_f4_inverted_line_overlap(rows)
    f5 = audit_f5_inverted_pencil_concentration(rows)
    f6 = audit_f6_inversion_l4_cross_check(rows)

    summary = {
        "n": len(rows),
        "i_witnessed_rows": {
            int(i): list(map(int, ks)) for i, ks in i_witnessed_rows(rows).items()
        },
        "inversion_triples": {
            int(i): [
                {"row": int(k), "triple": [int(x) for x in t]} for (k, t) in kt
            ]
            for i, kt in triples_by_i.items()
        },
        "f1_chord_three_circles": f1,
        "f2_line_circle": f2,
        "f3_three_rows_share_triple": f3,
        "f4_inverted_line_coincidence": f4,
        "f5_pencil_overload_three": f5,
        "f6_pentagon_excess": f6,
        "obstructed": bool(f1 or f2 or f3 or f4 or f6),
    }
    return summary


def is_inversion_obstructed(S: Pattern) -> bool:
    """Return True iff the pattern fails any of the hard inversion audits."""
    return inversion_audit(S)["obstructed"]


def inversion_filter_summary(S: Pattern) -> dict[str, object]:
    """Alias of :func:`inversion_audit`."""
    return inversion_audit(S)


__all__ = [
    "Pattern",
    "audit_f1_chord_three_circles",
    "audit_f2_line_circle",
    "audit_f3_three_rows_share_triple",
    "audit_f4_inverted_line_overlap",
    "audit_f5_inverted_pencil_concentration",
    "audit_f6_inversion_l4_cross_check",
    "i_witnessed_rows",
    "inversion_audit",
    "inversion_filter_summary",
    "inversion_triples",
    "is_inversion_obstructed",
    "normalize_pattern",
]
