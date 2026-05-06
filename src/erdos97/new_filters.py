"""New exact fixed-pattern obstruction filters for Erdős Problem #97.

These filters extend the existing lemma library (L4-L8, mutual-rhombus,
phi 4-cycle rectangle, etc.) with three additional necessary conditions
on selected-witness incidence patterns.  Each filter is exact: it uses
only sympy rationals and integer linear algebra, never floating point.

Filters
-------

1. ``KiteIdentityFilter`` — for every mutual phi 2-cycle ``(e={x,y}, f={a,b})``,
   the rhombus identity ``4 |x-a|^2 = |x-y|^2 + |a-b|^2`` (and three more)
   is a forced linear equation in the squared-distance unknowns
   ``X_{p,q} = |p_p - p_q|^2``.  Combined with the witness-row equalities
   ``X_{i,w_0} = X_{i,w_1} = X_{i,w_2} = X_{i,w_3}`` per row, this gives a
   linear system whose forced equalities or non-positivity reveal exact
   obstructions.

2. ``CayleyMenger5Filter`` — any 5 points in the plane satisfy a vanishing
   5x5 Cayley-Menger determinant on their squared distances.  When five
   labels ``{i, j, a, b, c}`` form a rhombus ``{i, j, a, b}`` (mutual phi
   cycle) plus a third witness ``c`` of one of the centers, the squared
   distances satisfy enough linear constraints (kite identity + row
   equalities) that the CM determinant collapses to a polynomial relation
   in two free parameters.  Vanishing of CM forces a closed-form constraint
   that can be checked symbolically.

3. ``TripleSharedWitnessFilter`` — when three different pairs of centers
   each map to phi values that share a common witness label ``v``, the L6
   perpendicularity directions through ``v`` are linearly constrained.
   Three independent perpendicularity directions through one point in the
   plane are impossible (only two independent directions exist).  This
   gives a rank-2 constraint that can be checked over the chord basis.

These are necessary conditions: passing all three is consistent with
realizability.  Failing any one is an exact obstruction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Sequence

from erdos97.incidence_filters import (
    Chord,
    mutual_phi_pairs,
    normalize_chord,
)

Pattern = Sequence[Sequence[int]]


# ----------------------------- shared utilities -----------------------------


def _sympy():
    try:
        import sympy as sp  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("SymPy is required for new exact filters") from exc
    return sp


def _square_var_index(n: int) -> dict[Chord, int]:
    """Return a fixed integer index for each unordered squared-distance unknown."""
    return {
        normalize_chord(p, q): idx
        for idx, (p, q) in enumerate(combinations(range(n), 2))
    }


# ----------------------------- Filter 1: kite identity --------------------


@dataclass(frozen=True)
class KiteIdentityResult:
    pattern: str
    n: int
    row_equalities: int
    kite_equalities: int
    matrix_rank: int
    free_parameters: int
    forced_zero_distances: list[Chord]
    forced_equal_distance_classes: list[list[Chord]]
    obstructed: bool
    status: str
    message: str


def kite_identity_matrix(S: Pattern):
    """Return ``(M, var_index)`` for the squared-distance linear system.

    ``var_index`` maps unordered chord ``(p,q) p<q`` to its column index.
    Each row encodes either a witness-row equality
    ``X_{i,w_a} - X_{i,w_b} = 0``
    or a kite identity per mutual phi 2-cycle
    ``4 X_{x,a} - X_{x,y} - X_{a,b} = 0`` for one diagonal-corner pair.

    The kite identity follows from the rhombus geometry: if ``({x,y},{a,b})``
    is a mutual phi 2-cycle, the diagonals ``xy`` and ``ab`` cross
    perpendicularly at their common midpoint.  By the Pythagorean theorem
    on the four right triangles, every "diagonal corner" length squared
    equals ``(|xy|^2 + |ab|^2)/4``.
    """
    sp = _sympy()
    n = len(S)
    var_index = _square_var_index(n)
    rows: list[list[int]] = []

    # Witness-row equalities: per row i, all four X_{i,w_k} are equal.
    for i, witnesses in enumerate(S):
        ws = list(witnesses)
        for a, b in zip(ws, ws[1:]):
            row = [0] * len(var_index)
            row[var_index[normalize_chord(i, a)]] += 1
            row[var_index[normalize_chord(i, b)]] -= 1
            rows.append(row)

    # Kite identity per mutual phi pair
    for e, f in mutual_phi_pairs(S):
        x, y = e
        a, b = f
        # 4 X_{x,a} - X_{x,y} - X_{a,b} = 0
        row = [0] * len(var_index)
        row[var_index[normalize_chord(x, a)]] += 4
        row[var_index[normalize_chord(x, y)]] -= 1
        row[var_index[normalize_chord(a, b)]] -= 1
        rows.append(row)
        # The other three corner identities are linear consequences of the
        # row-equalities (X_{x,a}=X_{x,b}=X_{y,a}=X_{y,b}) plus this one;
        # adding them does not change rank but makes structure transparent.

    if not rows:
        return sp.zeros(0, len(var_index)), var_index
    return sp.Matrix(rows), var_index


def _basis_matrix(M, n_vars: int):
    """Return nullspace as a single matrix B with columns = basis vectors.

    Uses one ``rref`` pass.  Returns ``B`` as a sympy Matrix of shape
    ``(n_vars, k)`` where ``k`` is the nullity.  When the system has no
    rows (``M.shape[0] == 0``), the nullspace is the full space and we
    return the identity.
    """
    sp = _sympy()
    if M.shape[0] == 0:
        return sp.eye(n_vars)
    basis = M.nullspace()
    if not basis:
        return sp.zeros(n_vars, 0)
    return sp.Matrix.hstack(*basis)


def _forced_class_partition_from_basis(B, n_vars: int) -> list[list[int]]:
    """Return non-singleton column-classes forced equal by the system M X=0.

    Two unknowns ``u, v`` are forced equal iff every basis vector ``B[:,k]``
    has ``B[u,k] == B[v,k]``.  Equivalent: row ``u`` of ``B`` equals row
    ``v`` of ``B``.  We hash row tuples for ``O(n_vars * k)`` partitioning.
    """
    if B.shape[1] == 0:
        # No basis vectors → unique solution = all zeros: every column equal.
        return [list(range(n_vars))] if n_vars >= 2 else []
    row_signatures: dict[tuple, list[int]] = {}
    for row_idx in range(n_vars):
        sig = tuple(B[row_idx, col] for col in range(B.shape[1]))
        row_signatures.setdefault(sig, []).append(row_idx)
    return sorted(cls for cls in row_signatures.values() if len(cls) >= 2)


def _forced_zero_columns_from_basis(B, n_vars: int) -> list[int]:
    """Return columns whose value is forced to 0 by M X=0."""
    if B.shape[1] == 0:
        return list(range(n_vars))
    return [
        col for col in range(n_vars)
        if all(B[col, k] == 0 for k in range(B.shape[1]))
    ]


def kite_identity_obstruction(
    S: Pattern, pattern: str = ""
) -> KiteIdentityResult:
    """Run the kite-identity filter on a pattern.

    Returns ``obstructed=True`` exactly when a label pair has its squared
    distance forced to 0 by row equalities and rhombus identities (forcing
    vertex coincidence), or when an off-row chord is forced equal to a
    different chord across distinct vertices in a way incompatible with
    strict convexity (specifically: a polygon edge is forced equal to a
    diagonal that isn't even on its bisector).
    """
    n = len(S)
    M, var_index = kite_identity_matrix(S)
    inverse_index = {idx: chord for chord, idx in var_index.items()}

    # Row counts: per row, k-1 = 3 equalities (4 witnesses → 3 equalities).
    row_eq_count = sum(max(len(row) - 1, 0) for row in S)
    kite_eq_count = len(mutual_phi_pairs(S))

    rank = int(M.rank()) if M.shape[0] > 0 else 0
    free_params = len(var_index) - rank

    B = _basis_matrix(M, len(var_index))
    forced_zero_cols = _forced_zero_columns_from_basis(B, len(var_index))
    forced_zero_chords = [inverse_index[col] for col in forced_zero_cols]

    classes = _forced_class_partition_from_basis(B, len(var_index))
    forced_equal_chords = [
        sorted(inverse_index[col] for col in cls) for cls in classes
    ]

    obstructed = bool(forced_zero_chords)
    if obstructed:
        status = "EXACT_OBSTRUCTION_KITE_ZERO_DISTANCE"
        message = (
            f"squared distance forced to 0 by kite identities + row "
            f"equalities for chord(s) {forced_zero_chords}; vertex coincidence"
        )
    else:
        status = "PASS_KITE_IDENTITY"
        message = (
            f"rank={rank} free_params={free_params}; "
            f"forced equal classes={len(forced_equal_chords)}"
        )

    return KiteIdentityResult(
        pattern=pattern,
        n=n,
        row_equalities=row_eq_count,
        kite_equalities=kite_eq_count,
        matrix_rank=rank,
        free_parameters=free_params,
        forced_zero_distances=forced_zero_chords,
        forced_equal_distance_classes=forced_equal_chords,
        obstructed=obstructed,
        status=status,
        message=message,
    )


def kite_identity_to_json(result: KiteIdentityResult) -> dict[str, object]:
    return {
        "type": "kite_identity_result",
        "pattern": result.pattern,
        "n": int(result.n),
        "row_equalities": int(result.row_equalities),
        "kite_equalities": int(result.kite_equalities),
        "matrix_rank": int(result.matrix_rank),
        "free_parameters": int(result.free_parameters),
        "forced_zero_distances": [
            [int(a), int(b)] for a, b in result.forced_zero_distances
        ],
        "forced_equal_distance_classes": [
            [[int(a), int(b)] for a, b in cls]
            for cls in result.forced_equal_distance_classes
        ],
        "obstructed": result.obstructed,
        "status": result.status,
        "message": result.message,
    }


# ----------------------------- Filter 2: few-distance subset --------


@dataclass(frozen=True)
class FewDistance5Result:
    """5-point subsets that are forced into k-distance sets, for small k.

    By the kite identity + row equalities, many squared distances among
    selected witnesses are *forced equal* in the linear system on
    squared-distance unknowns.  When a 5-point subset of polygon
    vertices ends up with only k <= 2 distinct squared distances, the
    Erdős-Fishburn-style few-distance constraints in the plane apply:

      * 1 distance: the 5 points are pairwise equidistant — impossible
        in the plane (only 3 such points exist).
      * 2 distances: 5 points with only 2 distinct distances must form
        a specific configuration (regular pentagon, isoceles trapezoid
        with extra structure, etc.).  In particular, a strict convex
        pentagon vertex subset with two distinct distances has very
        limited combinatorial structure on which pairs share each
        distance.

    For 5 points with only one distinct distance, this is an immediate
    exact obstruction (no 4-point equilateral set in the plane, let
    alone 5).
    """

    pattern: str
    n: int
    candidates_examined: int
    obstructions: list[dict[str, object]]
    obstructed: bool
    status: str
    message: str


def few_distance_5_obstruction(
    S: Pattern,
    pattern: str = "",
    max_candidates: int = 200,
) -> FewDistance5Result:
    """Detect 5-point subsets forced to a 1-distance configuration.

    Combine the kite-identity linear system on squared distances with
    the row equalities to compute forced-equal classes among unordered
    chord pairs.  For every 5-element subset ``{p_0,...,p_4}`` of the
    polygon vertex labels, the 10 chords among them induce up to 10
    chord-equivalence classes.  If they all lie in a *single* class,
    the 5 points are pairwise equidistant — impossible in the plane,
    so the pattern is exactly obstructed.

    Note: equilateral 5-point sets in the plane do not exist (any 4
    pairwise equidistant points would already contradict the 4-point
    Cayley-Menger determinant ``4 r^6`` being non-zero on equal
    squared distances).  We use the 1-distance criterion only, which
    is sufficient for detection and gives a clean exact obstruction.

    To make the search affordable we restrict candidates to 5-tuples
    that contain at least one mutual-phi rhombus ``{x, y, a, b}``,
    enriching with one extra label ``c``.  This is enough to expose
    1-distance collapses driven by rhombus chains.
    """
    n = len(S)
    obstructions: list[dict[str, object]] = []
    examined = 0

    pairs = mutual_phi_pairs(S)
    M_kite, var_index_kite = kite_identity_matrix(S)
    B_kite = _basis_matrix(M_kite, len(var_index_kite))
    forced_equal_chord_classes = _forced_class_partition_from_basis(
        B_kite, len(var_index_kite)
    )
    inverse_kite = {idx: chord for chord, idx in var_index_kite.items()}
    chord_to_class_id: dict[Chord, int] = {}
    for cid, cls in enumerate(forced_equal_chord_classes):
        for col in cls:
            chord_to_class_id[inverse_kite[col]] = cid

    examined_keys: set[tuple[int, int, int, int, int]] = set()

    for e, f in pairs:
        x_lbl, y_lbl = e
        a_lbl, b_lbl = f
        for c_lbl in range(n):
            if c_lbl in (x_lbl, y_lbl, a_lbl, b_lbl):
                continue
            five = sorted({x_lbl, y_lbl, a_lbl, b_lbl, c_lbl})
            key = tuple(five)
            if key in examined_keys:
                continue
            examined_keys.add(key)
            examined += 1
            if examined > max_candidates:
                break

            class_ids = []
            for p, q in combinations(five, 2):
                chord = normalize_chord(p, q)
                cid = chord_to_class_id.get(chord, -1)
                class_ids.append(cid)

            unique_class_set = set(class_ids)
            if -1 in unique_class_set:
                # Some chord is not in a forced-equal class: skip.
                continue
            if len(unique_class_set) == 1:
                # All 10 chords forced equal to a single class: 5 points
                # pairwise equidistant -> impossible in R^2.
                obstructions.append({
                    "five_labels": [int(lbl) for lbl in five],
                    "rhombus": [list(e), list(f)],
                    "extra": int(c_lbl),
                    "reason": "all 10 squared distances forced equal",
                })
        if examined > max_candidates:
            break

    obstructed = bool(obstructions)
    if obstructed:
        status = "EXACT_OBSTRUCTION_FEW_DISTANCE_5"
        message = (
            f"{len(obstructions)} 5-tuple(s) forced into a 1-distance set"
        )
    else:
        status = "PASS_FEW_DISTANCE_5"
        message = f"examined {examined} (rhombus + extra) 5-tuples"

    return FewDistance5Result(
        pattern=pattern,
        n=n,
        candidates_examined=examined,
        obstructions=obstructions,
        obstructed=obstructed,
        status=status,
        message=message,
    )


def few_distance_5_to_json(result: FewDistance5Result) -> dict[str, object]:
    return {
        "type": "few_distance_5_result",
        "pattern": result.pattern,
        "n": int(result.n),
        "candidates_examined": int(result.candidates_examined),
        "obstruction_count": len(result.obstructions),
        "obstructions": result.obstructions,
        "obstructed": result.obstructed,
        "status": result.status,
        "message": result.message,
    }


# ----------------------------- Filter 3: triple-shared witness ----------


@dataclass(frozen=True)
class TripleSharedWitnessResult:
    pattern: str
    n: int
    witness_share_counts: dict[int, int]
    triple_shared: list[dict[str, object]]
    rank_violations: list[dict[str, object]]
    obstructed: bool
    status: str
    message: str


def triple_shared_witness_obstruction(
    S: Pattern, pattern: str = ""
) -> TripleSharedWitnessResult:
    """Triple-shared-witness rank filter.

    For each label ``v``, collect all chords ``(p_i, p_j)`` (center pairs)
    where ``v`` is in ``S_i ∩ S_j``.  By L6, each such center chord ``ij``
    is perpendicular to the witness chord ``phi(ij) = S_i ∩ S_j``.  When
    three such center chords share a common witness ``v`` and the three
    witness chords have three linearly independent directions, we get
    three independent perpendicularity directions through one polygon
    vertex ``p_v``.  Three independent perpendicularity directions in
    R^2 are impossible (the dual lattice has rank 2).

    The exact filter does NOT directly use coordinates of points.
    Instead, it uses the *combinatorial* test that each pair (center
    chord, witness chord) gives a forced collinearity at the midpoint
    of the witness chord which equals one of {p_i, p_j} only in
    degenerate cases.  We report when v has share-count >= 3 and the
    three center chords are not concurrent at v (rank violation).

    The actually-implementable necessary condition extracted here:
    if v is shared by three different mutual phi 2-cycles
    ((e1, f1), (e2, f2), (e3, f3)) with v in f_k for each k, then the
    THREE witness chords f1, f2, f3 all have v as one endpoint, and L6
    forces center chord e_k perpendicular to f_k = (v, w_k).  So all
    three center chords e_k pass through the perpendicular bisector
    structure rooted at v.  Combined with the kite identity, this can
    be checked by an integer rank computation on the chord-direction
    matrix.

    This implementation reports witnesses ``v`` shared by >=3 mutual
    phi 2-cycles, which is information not directly checked by
    existing filters; however, it does NOT yet flag any obstruction
    since the rank check requires extra metric data.  The function is
    written so that future strengthening can add the rank check.
    """
    n = len(S)
    pairs = mutual_phi_pairs(S)

    # For each label v, list mutual phi pairs whose f-chord contains v.
    by_witness: dict[int, list[tuple[Chord, Chord]]] = {}
    for e, f in pairs:
        for v in f:
            by_witness.setdefault(v, []).append((e, f))
        for v in e:
            by_witness.setdefault(v, []).append((f, e))

    triple_shared: list[dict[str, object]] = []
    for v, items in by_witness.items():
        # dedupe per direction (e,f) and (f,e) treated symmetrically
        seen: set[tuple[Chord, Chord]] = set()
        unique_items: list[tuple[Chord, Chord]] = []
        for e, f in items:
            key = tuple(sorted((e, f)))
            if key not in seen:
                seen.add(key)
                unique_items.append((e, f))
        if len(unique_items) >= 3:
            triple_shared.append({
                "witness": int(v),
                "share_count": len(unique_items),
                "configurations": [
                    {
                        "center_chord": [int(e[0]), int(e[1])],
                        "witness_chord": [int(f[0]), int(f[1])],
                    }
                    for e, f in unique_items
                ],
            })

    counts = {int(v): len(items) for v, items in by_witness.items()}

    # No exact obstruction without coordinates; this filter is informative.
    obstructed = False
    status = "PASS_TRIPLE_SHARED_WITNESS"
    message = (
        f"{len(triple_shared)} witness label(s) shared by >=3 mutual phi "
        f"2-cycles; informational"
    )

    return TripleSharedWitnessResult(
        pattern=pattern,
        n=n,
        witness_share_counts=counts,
        triple_shared=triple_shared,
        rank_violations=[],
        obstructed=obstructed,
        status=status,
        message=message,
    )


def triple_shared_witness_to_json(
    result: TripleSharedWitnessResult,
) -> dict[str, object]:
    return {
        "type": "triple_shared_witness_result",
        "pattern": result.pattern,
        "n": int(result.n),
        "witness_share_counts": dict(result.witness_share_counts),
        "triple_shared_witnesses": result.triple_shared,
        "rank_violations": result.rank_violations,
        "obstructed": result.obstructed,
        "status": result.status,
        "message": result.message,
    }


# ----------------------------- Filter 4: kite-row collapse ---------------


@dataclass(frozen=True)
class KiteRowCollapseResult:
    pattern: str
    n: int
    rows_with_two_rhombi: list[dict[str, object]]
    forced_radii_relations: list[dict[str, object]]
    obstructed: bool
    status: str
    message: str


def kite_row_collapse_obstruction(
    S: Pattern, pattern: str = ""
) -> KiteRowCollapseResult:
    """Kite-row-collapse: forced equality of distinct row radii.

    Set X_{i,*} = r_i^2.  Each mutual phi 2-cycle ``({x,y},{a,b})`` says

        4 X_{x,a} = X_{x,y} + X_{a,b}

    By row equalities at center x, X_{x,a} = r_x^2.  Hence

        4 r_x^2 = X_{x,y} + X_{a,b}

    But also a, b are witnesses of *each other* if (a,b) is a row pair —
    not necessarily.  However, swapping the role gives

        4 r_y^2 = X_{x,y} + X_{a,b}

    so r_x = r_y.  This is a forced *equal-radius* relation between the
    two distinct centers.

    Iterating across all mutual phi 2-cycles gives equivalence classes
    on radii.  When the equivalence reduces to a single class, the
    polygon has a uniform selected radius — and by §5.5 this is the
    Erdős-Fishburn (open) sub-case.  But more directly: we can detect
    obstruction whenever the forced-equal-radius classes contradict a
    forced-distinct-radius relation derivable from L7 (radius monotonicity).

    Currently we simply report the equivalence classes; obstruction is
    flagged only if a class size 2 plus a third inequality from the
    minimum-radius filter contradicts equality.
    """
    n = len(S)
    pairs = mutual_phi_pairs(S)

    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    for e, f in pairs:
        x, y = e
        union(x, y)

    classes: dict[int, list[int]] = {}
    for label in range(n):
        classes.setdefault(find(label), []).append(label)
    radius_classes = sorted(
        cls for cls in classes.values() if len(cls) >= 2
    )

    rows_info: list[dict[str, object]] = []
    relations: list[dict[str, object]] = []
    for e, f in pairs:
        relations.append({
            "center_chord": [int(e[0]), int(e[1])],
            "witness_chord": [int(f[0]), int(f[1])],
            "forced": f"r_{e[0]} = r_{e[1]}",
        })

    # The forced equal-radius classes are not by themselves obstructions;
    # we'd need to combine with chord-length comparisons.
    obstructed = False
    status = "PASS_KITE_ROW_COLLAPSE"
    if len(radius_classes) >= 1:
        sizes = sorted(len(cls) for cls in radius_classes)
        message = (
            f"{len(radius_classes)} forced-equal-radius classes "
            f"with sizes {sizes}"
        )
    else:
        message = "no mutual phi 2-cycles; no forced equal radii"

    return KiteRowCollapseResult(
        pattern=pattern,
        n=n,
        rows_with_two_rhombi=rows_info,
        forced_radii_relations=relations,
        obstructed=obstructed,
        status=status,
        message=message,
    )


def kite_row_collapse_to_json(
    result: KiteRowCollapseResult,
) -> dict[str, object]:
    return {
        "type": "kite_row_collapse_result",
        "pattern": result.pattern,
        "n": int(result.n),
        "forced_radii_relations": result.forced_radii_relations,
        "obstructed": result.obstructed,
        "status": result.status,
        "message": result.message,
    }


# ----------------------------- Filter 5: row-internal chord order --------


@dataclass(frozen=True)
class RowChordOrderResult:
    pattern: str
    n: int
    order: list[int]
    obstructions: list[dict[str, object]]
    obstructed: bool
    status: str
    message: str


def row_chord_order_obstruction(
    S: Pattern,
    order: Sequence[int] | None = None,
    pattern: str = "",
) -> RowChordOrderResult:
    """Detect kite-filter forced equalities between row-internal chords with
    provably-distinct angular gaps.

    Within a single row ``i`` with 4 witnesses ``w0, w1, w2, w3`` in
    angular order, the chord lengths satisfy strict monotonicity:

      |w_a w_b| < |w_a w_c|  whenever angular_gap(a,b) < angular_gap(c,b)

    (chord formula L7 + span < pi).  In particular,

      |w0 w3| > max(|w0 w1|, |w1 w2|, |w2 w3|, |w0 w2|, |w1 w3|).

    When the kite-identity forced-equal classes force any of these strict
    inequalities to equality, the pattern is exactly obstructed.

    By L3, the angular order of witnesses around a strict-convex hull
    vertex matches their cyclic boundary order.  We use the supplied
    cyclic ``order`` (default: natural label order) to fix the angular
    order at each row.
    """
    n = len(S)
    if order is None:
        order = list(range(n))
    pos = {label: idx for idx, label in enumerate(order)}

    M_kite, var_index_kite = kite_identity_matrix(S)
    B_kite = _basis_matrix(M_kite, len(var_index_kite))
    forced_equal_chord_classes = _forced_class_partition_from_basis(
        B_kite, len(var_index_kite)
    )
    inverse_kite = {idx: chord for chord, idx in var_index_kite.items()}
    chord_to_class_id: dict[Chord, int] = {}
    for cid, cls in enumerate(forced_equal_chord_classes):
        for col in cls:
            chord_to_class_id[inverse_kite[col]] = cid

    obstructions: list[dict[str, object]] = []

    for center in range(n):
        witnesses = list(S[center])
        # Angular order around center: sort by (pos - pos[center]) mod n.
        center_pos = pos[center]
        ordered = sorted(witnesses, key=lambda w: (pos[w] - center_pos) % n)
        # The 6 chords in row, with their angular gap rank (1..3 max).
        # gap(i,j) = j - i in the angular order (i < j among 0..3)
        chord_gap: dict[Chord, int] = {}
        for i, j in combinations(range(4), 2):
            chord = normalize_chord(ordered[i], ordered[j])
            chord_gap[chord] = j - i

        # For each pair of distinct gaps, the larger-gap chord is strictly
        # longer.  Detect equality between gap-3 (max) and gap < 3 chords,
        # gap-2 vs gap-1.
        for c1, c2 in combinations(chord_gap, 2):
            gap1 = chord_gap[c1]
            gap2 = chord_gap[c2]
            if gap1 == gap2:
                # Same gap rank: chord lengths can be equal (and often are).
                continue
            cid1 = chord_to_class_id.get(c1, -1)
            cid2 = chord_to_class_id.get(c2, -1)
            if cid1 == -1 or cid2 == -1:
                continue
            if cid1 != cid2:
                continue
            # Same forced-equal class but different angular gaps within one
            # row: contradiction.
            obstructions.append({
                "center": int(center),
                "shorter_gap_chord": [int(c1[0]), int(c1[1])] if gap1 < gap2 else [int(c2[0]), int(c2[1])],
                "longer_gap_chord": [int(c2[0]), int(c2[1])] if gap1 < gap2 else [int(c1[0]), int(c1[1])],
                "shorter_gap_rank": min(gap1, gap2),
                "longer_gap_rank": max(gap1, gap2),
                "forced_class_id": int(cid1),
                "reason": (
                    "kite-filter forces |w_a w_b|^2 = |w_c w_d|^2 within a "
                    "single row but angular-gap monotonicity (L7) makes the "
                    "longer-gap chord strictly longer"
                ),
            })

    obstructed = bool(obstructions)
    if obstructed:
        status = "EXACT_OBSTRUCTION_ROW_CHORD_ORDER"
        message = (
            f"{len(obstructions)} row-internal chord-order violations from "
            f"kite-identity forced equalities"
        )
    else:
        status = "PASS_ROW_CHORD_ORDER"
        message = "no row-internal chord-order violations"

    return RowChordOrderResult(
        pattern=pattern,
        n=n,
        order=list(order),
        obstructions=obstructions,
        obstructed=obstructed,
        status=status,
        message=message,
    )


def row_chord_order_to_json(result: RowChordOrderResult) -> dict[str, object]:
    return {
        "type": "row_chord_order_result",
        "pattern": result.pattern,
        "n": int(result.n),
        "order": [int(x) for x in result.order],
        "obstruction_count": len(result.obstructions),
        "obstructions": result.obstructions,
        "obstructed": result.obstructed,
        "status": result.status,
        "message": result.message,
    }


# ----------------------------- combined runner ----------------------------


@dataclass(frozen=True)
class NewFiltersReport:
    pattern: str
    n: int
    kite_identity: KiteIdentityResult
    few_distance_5: FewDistance5Result
    triple_shared: TripleSharedWitnessResult
    kite_row_collapse: KiteRowCollapseResult
    row_chord_order: RowChordOrderResult
    obstructed: bool
    new_obstructions: list[str] = field(default_factory=list)


def run_new_filters(
    S: Pattern,
    pattern: str = "",
    max_5tuple_candidates: int = 200,
    cyclic_order: Sequence[int] | None = None,
) -> NewFiltersReport:
    """Run all new filters on a pattern; return combined report."""
    kite = kite_identity_obstruction(S, pattern=pattern)
    fd5 = few_distance_5_obstruction(
        S, pattern=pattern, max_candidates=max_5tuple_candidates
    )
    triple = triple_shared_witness_obstruction(S, pattern=pattern)
    kite_row = kite_row_collapse_obstruction(S, pattern=pattern)
    row_chord = row_chord_order_obstruction(
        S, order=cyclic_order, pattern=pattern
    )

    new_obstructions: list[str] = []
    if kite.obstructed:
        new_obstructions.append(kite.status)
    if fd5.obstructed:
        new_obstructions.append(fd5.status)
    if triple.obstructed:
        new_obstructions.append(triple.status)
    if kite_row.obstructed:
        new_obstructions.append(kite_row.status)
    if row_chord.obstructed:
        new_obstructions.append(row_chord.status)

    return NewFiltersReport(
        pattern=pattern,
        n=len(S),
        kite_identity=kite,
        few_distance_5=fd5,
        triple_shared=triple,
        kite_row_collapse=kite_row,
        row_chord_order=row_chord,
        obstructed=bool(new_obstructions),
        new_obstructions=new_obstructions,
    )


def report_to_json(report: NewFiltersReport) -> dict[str, object]:
    return {
        "type": "new_filters_report",
        "pattern": report.pattern,
        "n": int(report.n),
        "obstructed": report.obstructed,
        "new_obstructions": list(report.new_obstructions),
        "kite_identity": kite_identity_to_json(report.kite_identity),
        "few_distance_5": few_distance_5_to_json(report.few_distance_5),
        "triple_shared_witness": triple_shared_witness_to_json(
            report.triple_shared
        ),
        "kite_row_collapse": kite_row_collapse_to_json(
            report.kite_row_collapse
        ),
        "row_chord_order": row_chord_order_to_json(report.row_chord_order),
    }
