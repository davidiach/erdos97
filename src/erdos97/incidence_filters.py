"""Exact incidence filters for selected-witness patterns.

The utilities in this module are combinatorial or rational-linear. They do not
use geometry coordinates, numerical optimization, NumPy, or floating-point
equality.
"""

from __future__ import annotations

from collections import defaultdict, deque
from itertools import combinations
from typing import Sequence

Chord = tuple[int, int]
Pattern = list[list[int]]


def normalize_chord(a: int, b: int) -> Chord:
    """Return a sorted unordered chord tuple. Reject loops."""
    if a == b:
        raise ValueError(f"loop chord is not allowed: ({a}, {b})")
    return (a, b) if a < b else (b, a)


def phi_map(S: Sequence[Sequence[int]]) -> dict[Chord, Chord]:
    """
    Return phi({i,j}) = S_i cap S_j whenever the intersection has size 2.

    Chords are normalized sorted tuples.
    """
    witness_sets = [set(row) for row in S]
    out: dict[Chord, Chord] = {}
    for i, j in combinations(range(len(S)), 2):
        inter = sorted(witness_sets[i] & witness_sets[j])
        if len(inter) == 2:
            out[normalize_chord(i, j)] = normalize_chord(inter[0], inter[1])
    return out


def _positions(order: Sequence[int]) -> dict[int, int]:
    pos: dict[int, int] = {}
    for idx, label in enumerate(order):
        if label in pos:
            raise ValueError(f"cyclic order is not a permutation: repeated label {label}")
        pos[label] = idx
    return pos


def chords_cross_in_order(e: Chord, f: Chord, order: Sequence[int]) -> bool:
    """
    Return True iff disjoint chords e and f have alternating endpoints.

    The supplied order is a cyclic order of labels. Chords sharing an endpoint
    return False.
    """
    e = normalize_chord(*e)
    f = normalize_chord(*f)
    if set(e) & set(f):
        return False

    pos = _positions(order)
    missing = [label for label in (*e, *f) if label not in pos]
    if missing:
        raise ValueError(f"chord endpoint is missing from cyclic order: {missing[0]}")

    a, b = e
    c, d = f
    a_pos, b_pos = pos[a], pos[b]
    if a_pos > b_pos:
        a_pos, b_pos = b_pos, a_pos
    c_inside = a_pos < pos[c] < b_pos
    d_inside = a_pos < pos[d] < b_pos
    return c_inside != d_inside


def adjacent_pairs(order: Sequence[int]) -> set[Chord]:
    """Return polygon edges for the supplied cyclic order."""
    if len(order) < 2:
        return set()
    _positions(order)
    return {
        normalize_chord(order[i], order[(i + 1) % len(order)])
        for i in range(len(order))
    }


def adjacent_two_overlap_violations(
    S: Sequence[Sequence[int]],
    order: Sequence[int] | None = None,
) -> list[tuple[Chord, Chord]]:
    """
    Return row-edge violations for adjacent center chords with two overlaps.

    Each item is (source_chord, witness_chord). The default order is the natural
    label order 0,1,...,n-1.
    """
    if order is None:
        order = list(range(len(S)))
    edges = adjacent_pairs(order)
    phis = phi_map(S)
    return [(edge, phis[edge]) for edge in sorted(edges) if edge in phis]


def crossing_bisector_violations(
    S: Sequence[Sequence[int]],
    order: Sequence[int],
) -> list[tuple[Chord, Chord]]:
    """Return phi edges e -> f where e and f do not cross in the supplied order."""
    violations: list[tuple[Chord, Chord]] = []
    for source, target in sorted(phi_map(S).items()):
        if not chords_cross_in_order(source, target, order):
            violations.append((source, target))
    return violations


def forced_perpendicular_graph(S: Sequence[Sequence[int]]) -> dict[Chord, set[Chord]]:
    """Build the undirected graph with an edge e--phi(e) for every two-overlap."""
    n = len(S)
    graph: dict[Chord, set[Chord]] = {
        normalize_chord(i, j): set() for i, j in combinations(range(n), 2)
    }
    for source, target in phi_map(S).items():
        graph.setdefault(source, set()).add(target)
        graph.setdefault(target, set()).add(source)
    return graph


def _odd_cycle_from_conflict(
    u: Chord,
    v: Chord,
    parent: dict[Chord, Chord | None],
) -> list[Chord]:
    u_path: list[Chord] = []
    cur: Chord | None = u
    while cur is not None:
        u_path.append(cur)
        cur = parent[cur]

    v_path: list[Chord] = []
    cur = v
    while cur is not None:
        v_path.append(cur)
        cur = parent[cur]

    u_index = {node: idx for idx, node in enumerate(u_path)}
    lca = next(node for node in v_path if node in u_index)
    u_prefix = u_path[: u_index[lca] + 1]
    v_prefix = v_path[: v_path.index(lca)]
    return u_prefix + list(reversed(v_prefix))


def odd_forced_perpendicular_cycle(
    S: Sequence[Sequence[int]],
) -> list[Chord] | None:
    """
    Return one odd cycle in the forced-perpendicularity graph if found.

    The graph is checked by BFS 2-coloring. A same-color edge reconstructs an
    odd cycle from the two parent paths plus the conflict edge.
    """
    graph = forced_perpendicular_graph(S)
    color: dict[Chord, int] = {}
    parent: dict[Chord, Chord | None] = {}

    for start in sorted(graph):
        if start in color:
            continue
        color[start] = 0
        parent[start] = None
        q: deque[Chord] = deque([start])
        while q:
            u = q.popleft()
            for v in sorted(graph[u]):
                if v not in color:
                    color[v] = 1 - color[u]
                    parent[v] = u
                    q.append(v)
                elif color[v] == color[u] and parent.get(u) != v:
                    return _odd_cycle_from_conflict(u, v, parent)
    return None


def _canonical_directed_cycle(
    cycle: tuple[Chord, Chord, Chord, Chord],
) -> tuple[Chord, Chord, Chord, Chord]:
    rotations = [cycle[i:] + cycle[:i] for i in range(len(cycle))]
    return min(rotations)


def phi_directed_4_cycles(S: Sequence[Sequence[int]]) -> list[tuple[Chord, Chord, Chord, Chord]]:
    """Return directed 4-cycles in the partial phi map, up to rotation."""
    phis = phi_map(S)
    cycles: set[tuple[Chord, Chord, Chord, Chord]] = set()

    for e0 in sorted(phis):
        e1 = phis[e0]
        e2 = phis.get(e1)
        if e2 is None:
            continue
        e3 = phis.get(e2)
        if e3 is None:
            continue
        if phis.get(e3) != e0:
            continue
        cycle = (e0, e1, e2, e3)
        if len(set(cycle)) != 4:
            continue
        cycles.add(_canonical_directed_cycle(cycle))

    return sorted(cycles)


def _other_endpoint(chord: Chord, endpoint: int) -> int:
    if endpoint == chord[0]:
        return chord[1]
    if endpoint == chord[1]:
        return chord[0]
    raise ValueError(f"{endpoint} is not an endpoint of {chord}")


def _induced_order(order: Sequence[int], labels: set[int]) -> tuple[int, ...]:
    _positions(order)
    seq = tuple(label for label in order if label in labels)
    if len(seq) != len(labels):
        missing = sorted(labels - set(seq))
        raise ValueError(f"cyclic order is missing labels: {missing}")
    return seq


def _cyclically_equal(seq: Sequence[int], target: Sequence[int]) -> bool:
    if len(seq) != len(target):
        return False
    if not seq:
        return True
    tup = tuple(seq)
    want = tuple(target)
    return any(tup[i:] + tup[:i] == want for i in range(len(tup)))


def _rectangle_signature(
    cycle: tuple[Chord, Chord, Chord, Chord],
    order: Sequence[int],
) -> tuple[tuple[int, ...], str] | None:
    e0, e1, e2, e3 = cycle
    labels = set(e0 + e1 + e2 + e3)
    if len(labels) != 8:
        return None

    induced = _induced_order(order, labels)
    reversed_induced = tuple(reversed(induced))

    for A in e0:
        A_bar = _other_endpoint(e0, A)
        for B in e1:
            B_bar = _other_endpoint(e1, B)
            for C in e2:
                C_bar = _other_endpoint(e2, C)
                for D in e3:
                    D_bar = _other_endpoint(e3, D)
                    signature = (A, C, B, D, C_bar, A_bar, D_bar, B_bar)
                    if _cyclically_equal(induced, signature):
                        return signature, "supplied"
                    if _cyclically_equal(reversed_induced, signature):
                        return signature, "reversed"
    return None


def phi4_rectangle_trap_certificates(
    S: Sequence[Sequence[int]],
    order: Sequence[int] | None = None,
) -> list[dict[str, object]]:
    """
    Return exact certificates for the perpendicular-bisector 4-cycle trap.

    The detected cyclic order type is

        A, C, B, D, C_bar, A_bar, D_bar, B_bar

    for a directed phi cycle e0 -> e1 -> e2 -> e3 -> e0, with
    e0={A,A_bar}, e1={B,B_bar}, e2={C,C_bar}, and e3={D,D_bar}.
    In the standard normalization this gives the determinant identity
    D1 + D3 + D5 + D7 = -4*a*b. The endpoint order puts the e1/e3
    crossings in this order along e0 and the e2/e0 crossings in this order
    along e1, so a>0 and b>0. Strict convexity would make each D_i positive,
    yielding an exact fixed-pattern obstruction.
    """
    if order is None:
        order = list(range(len(S)))

    out: list[dict[str, object]] = []
    for cycle in phi_directed_4_cycles(S):
        matched = _rectangle_signature(cycle, order)
        if matched is None:
            continue
        signature, orientation = matched
        A, C, B, D, C_bar, A_bar, D_bar, B_bar = signature
        out.append(
            {
                "type": "phi4_rectangle_trap",
                "status": "EXACT_OBSTRUCTION",
                "phi_cycle": [_json_chord(chord) for chord in cycle],
                "cyclic_subsequence": [int(label) for label in signature],
                "cyclic_order_orientation": orientation,
                "roles": {
                    "A": int(A),
                    "A_bar": int(A_bar),
                    "B": int(B),
                    "B_bar": int(B_bar),
                    "C": int(C),
                    "C_bar": int(C_bar),
                    "D": int(D),
                    "D_bar": int(D_bar),
                },
                "coordinate_normalization": {
                    "A": ["L0", "0"],
                    "A_bar": ["-L0", "0"],
                    "B": ["a", "L1"],
                    "B_bar": ["a", "-L1"],
                    "C": ["a + L2", "b"],
                    "C_bar": ["a - L2", "b"],
                    "D": ["0", "b + L3"],
                    "D_bar": ["0", "b - L3"],
                },
                "positive_parameter_reasons": [
                    "Along chord A-A_bar, the B-B_bar crossing precedes the D-D_bar crossing; hence a > 0.",
                    "Along chord B-B_bar, the C-C_bar crossing precedes the A-A_bar crossing; hence b > 0.",
                ],
                "turn_determinants": {
                    "D1": "L1*L2 + L1*a - L2*L3 - L2*b - a*b",
                    "D3": "-L0*L3 + L2*L3 + L2*b - L3*a - a*b",
                    "D5": "-L0*L1 + L0*L3 - L0*b + L3*a - a*b",
                    "D7": "L0*L1 + L0*b - L1*L2 - L1*a - a*b",
                },
                "determinant_identity": {
                    "left": "D1 + D3 + D5 + D7",
                    "right": "-4*a*b",
                    "contradiction": "Strict convexity requires D1,D3,D5,D7 > 0, but a,b > 0 makes their sum negative.",
                },
            }
        )
    return out


def mutual_phi_pairs(S: Sequence[Sequence[int]]) -> list[tuple[Chord, Chord]]:
    """Return unordered reciprocal pairs (e,f) with phi(e)=f and phi(f)=e."""
    phis = phi_map(S)
    pairs: set[tuple[Chord, Chord]] = set()
    for source, target in phis.items():
        if phis.get(target) == source:
            pairs.add((source, target) if source < target else (target, source))
    return sorted(pairs)


def _sympy():
    try:
        import sympy as sp  # type: ignore
    except ImportError as exc:  # pragma: no cover - depends on optional dev dep
        raise RuntimeError("SymPy is required for mutual midpoint filters") from exc
    return sp


def mutual_midpoint_matrix(S: Sequence[Sequence[int]]):
    """
    Return a SymPy integer matrix with one row per mutual phi 2-cycle.

    Each row is X_e0 + X_e1 - X_f0 - X_f1 = 0.
    """
    sp = _sympy()
    n = len(S)
    rows: list[list[int]] = []
    for e, f in mutual_phi_pairs(S):
        row = [0] * n
        row[e[0]] += 1
        row[e[1]] += 1
        row[f[0]] -= 1
        row[f[1]] -= 1
        rows.append(row)
    if not rows:
        return sp.zeros(0, n)
    return sp.Matrix(rows)


def forced_equal_classes_from_matrix(M, n: int) -> list[list[int]]:
    """
    Return non-singleton label classes forced equal by the system M X = 0.

    Labels u,v are forced equal iff every basis vector of nullspace(M) has equal
    coordinates at u and v.
    """
    if M.shape[1] != n:
        raise ValueError(f"matrix has {M.shape[1]} columns, expected {n}")

    basis = M.nullspace()
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for u, v in combinations(range(n), 2):
        if all(vec[u, 0] == vec[v, 0] for vec in basis):
            union(u, v)

    classes: dict[int, list[int]] = defaultdict(list)
    for label in range(n):
        classes[find(label)].append(label)
    return sorted(cls for cls in classes.values() if len(cls) >= 2)


def _json_chord(chord: Chord) -> list[int]:
    return [int(chord[0]), int(chord[1])]


def _json_chord_pair(pair: tuple[Chord, Chord]) -> list[list[int]]:
    return [_json_chord(pair[0]), _json_chord(pair[1])]


def filter_summary(
    S: Sequence[Sequence[int]],
    order: Sequence[int] | None = None,
) -> dict[str, object]:
    """
    Return a JSON-serializable summary of exact incidence filters.
    """
    if order is None:
        order = list(range(len(S)))

    phis = phi_map(S)
    odd_cycle = odd_forced_perpendicular_cycle(S)
    mutual_pairs = mutual_phi_pairs(S)
    matrix = mutual_midpoint_matrix(S)
    forced_classes = forced_equal_classes_from_matrix(matrix, len(S))
    adjacent_violations = adjacent_two_overlap_violations(S, order)
    crossing_violations = crossing_bisector_violations(S, order)
    rectangle_traps = phi4_rectangle_trap_certificates(S, order)

    return {
        "n": len(S),
        "phi_edges": len(phis),
        "odd_cycle_length": len(odd_cycle) if odd_cycle else None,
        "odd_cycle": [_json_chord(chord) for chord in odd_cycle] if odd_cycle else None,
        "mutual_phi_2_cycles": len(mutual_pairs),
        "mutual_phi_pairs": [_json_chord_pair(pair) for pair in mutual_pairs],
        "midpoint_matrix_rank": int(matrix.rank()),
        "forced_equality_classes": forced_classes,
        "adjacent_two_overlap_violations": [
            _json_chord_pair(pair) for pair in adjacent_violations
        ],
        "crossing_bisector_violations": [
            _json_chord_pair(pair) for pair in crossing_violations
        ],
        "rectangle_trap_4_cycles": len(rectangle_traps),
        "rectangle_trap_certificates": rectangle_traps,
    }
