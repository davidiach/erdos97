"""Scalable abstract bridge control with a unique long strict cycle.

For ``k >= 8``, use ``n=6k-1`` and the circulant selected rows with offsets
``{k+1, 2k+3, 3k+1, 5k}``.  The helpers below replay the finite consequences
for chosen parameters.  The accompanying note contains the arbitrary-``k``
proof.

This is an abstract selected-row control, not a Euclidean realization and not
a counterexample to Erdos Problem #97.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from itertools import combinations
from math import comb, gcd

from erdos97.kalmanson_equilateral_hinge import find_hinge_instances
from erdos97.vertex_circle_quotient_replay import (
    SelectedRow,
    StrictInequality,
    UnionFind,
    pair,
    strict_quotient_edges,
)

Pair = tuple[int, int]
DistanceClassToken = tuple[int, int, int]
PrimitiveVector = tuple[tuple[DistanceClassToken, int], ...]


@dataclass(frozen=True)
class ScalableStrictCycleReport:
    """Exact finite replay of one member of the scalable family."""

    k: int
    n: int
    offsets: tuple[int, int, int, int]
    maximum_row_intersection: int
    two_overlap_count: int
    crossing_violations: int
    maximum_witness_pair_multiplicity: int
    hinge_count: int
    reciprocal_selected_pair_count: int
    selected_digraph_strongly_connected: bool
    fragile_bijection_ok: bool
    minimum_forward_turn_support: int
    minimum_reverse_turn_support: int
    uniform_turn_strictly_feasible: bool
    strict_edge_count: int
    strict_node_count: int
    self_edge_count: int
    kalmanson_self_edge_count: int
    kalmanson_zero_based_row_count: int
    kalmanson_primitive_vector_orbit_count: int
    kalmanson_primitive_inverse_orbit_count: int
    kalmanson_known_positive_circuit_size: int | None
    scc_size_histogram: tuple[tuple[int, int], ...]
    cyclic_scc_count: int
    cyclic_scc_size: int
    cyclic_scc_internal_edges: int
    shortest_strict_cycle: int | None

    def to_dict(self) -> dict[str, object]:
        return {
            "k": self.k,
            "n": self.n,
            "offsets": list(self.offsets),
            "incidence": {
                "maximum_row_intersection": self.maximum_row_intersection,
                "two_overlap_count": self.two_overlap_count,
                "crossing_violations": self.crossing_violations,
                "maximum_witness_pair_multiplicity": (
                    self.maximum_witness_pair_multiplicity
                ),
                "hinge_count": self.hinge_count,
                "reciprocal_selected_pair_count": (
                    self.reciprocal_selected_pair_count
                ),
                "selected_digraph_strongly_connected": (
                    self.selected_digraph_strongly_connected
                ),
                "fragile_bijection_ok": self.fragile_bijection_ok,
            },
            "turns": {
                "minimum_forward_support": self.minimum_forward_turn_support,
                "minimum_reverse_support": self.minimum_reverse_turn_support,
                "uniform_strictly_feasible": self.uniform_turn_strictly_feasible,
            },
            "strict_graph": {
                "edge_count": self.strict_edge_count,
                "node_count": self.strict_node_count,
                "self_edge_count": self.self_edge_count,
                "kalmanson_self_edge_count": self.kalmanson_self_edge_count,
                "kalmanson_zero_based_row_count": (
                    self.kalmanson_zero_based_row_count
                ),
                "kalmanson_primitive_vector_orbit_count": (
                    self.kalmanson_primitive_vector_orbit_count
                ),
                "kalmanson_primitive_inverse_orbit_count": (
                    self.kalmanson_primitive_inverse_orbit_count
                ),
                "kalmanson_known_positive_circuit_size": (
                    self.kalmanson_known_positive_circuit_size
                ),
                "scc_size_histogram": dict(self.scc_size_histogram),
                "cyclic_scc_count": self.cyclic_scc_count,
                "cyclic_scc_size": self.cyclic_scc_size,
                "cyclic_scc_internal_edges": self.cyclic_scc_internal_edges,
                "shortest_cycle": self.shortest_strict_cycle,
            },
        }


def family_parameters(k: int) -> tuple[int, tuple[int, int, int, int]]:
    """Return ``(n, offsets)`` and validate the theorem range."""
    if isinstance(k, bool) or not isinstance(k, int):
        raise TypeError("k must be an int (not bool)")
    if k < 8:
        raise ValueError("the scalable control requires k >= 8")
    n = 6 * k - 1
    return n, (k + 1, 2 * k + 3, 3 * k + 1, 5 * k)


def selected_rows(k: int) -> tuple[SelectedRow, ...]:
    """Return the full labelled circulant selected-row system."""
    n, offsets = family_parameters(k)
    return tuple(
        SelectedRow(
            center=center,
            witnesses=tuple(sorted((center + offset) % n for offset in offsets)),
        )
        for center in range(n)
    )


def _in_open_arc(a: int, b: int, x: int, n: int) -> bool:
    return x not in {a, b} and (x - a) % n < (b - a) % n


def _chords_cross(first: Pair, second: Pair, n: int) -> bool:
    a, b = first
    c, d = second
    if len({a, b, c, d}) != 4:
        return False
    return _in_open_arc(a, b, c, n) != _in_open_arc(a, b, d, n)


def _pair(a: int, b: int) -> Pair:
    return (a, b) if a < b else (b, a)


def _incidence_summary(
    rows: tuple[SelectedRow, ...],
    n: int,
) -> tuple[int, int, int, int]:
    row_sets = [set(row.witnesses) for row in rows]
    maximum_intersection = 0
    two_overlaps = 0
    crossing_violations = 0
    for first, second in combinations(range(n), 2):
        common = row_sets[first] & row_sets[second]
        maximum_intersection = max(maximum_intersection, len(common))
        if len(common) == 2:
            two_overlaps += 1
            if not _chords_cross(
                _pair(first, second),
                _pair(*sorted(common)),
                n,
            ):
                crossing_violations += 1

    pair_counts: Counter[Pair] = Counter()
    for row in rows:
        pair_counts.update(_pair(a, b) for a, b in combinations(row.witnesses, 2))
    return (
        maximum_intersection,
        two_overlaps,
        crossing_violations,
        max(pair_counts.values(), default=0),
    )


def _turn_summary(k: int) -> tuple[int, int, bool]:
    n, offsets = family_parameters(k)
    forward_sizes: list[int] = []
    reverse_sizes: list[int] = []
    for left, right in combinations(offsets, 2):
        forward_sizes.append(right - 1)
        reverse_sizes.append(n - left - 1)
    minimum_forward = min(forward_sizes)
    minimum_reverse = min(reverse_sizes)
    strict = 4 * minimum_forward > n and 4 * minimum_reverse > n
    return minimum_forward, minimum_reverse, strict


def _selected_digraph_summary(
    rows: tuple[SelectedRow, ...],
    n: int,
) -> tuple[int, bool]:
    """Return the reciprocal-pair count and strong-connectivity flag."""
    row_sets = [set(row.witnesses) for row in rows]
    reciprocal_pairs = sum(
        right in row_sets[left] and left in row_sets[right]
        for left, right in combinations(range(n), 2)
    )

    forward = [set(row.witnesses) for row in rows]
    reverse = [set() for _ in range(n)]
    for source, targets in enumerate(forward):
        for target in targets:
            reverse[target].add(source)

    def reachable(adjacency: list[set[int]]) -> set[int]:
        seen = {0}
        queue = deque([0])
        while queue:
            source = queue.popleft()
            for target in adjacency[source]:
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
        return seen

    strongly_connected = len(reachable(forward)) == n and len(reachable(reverse)) == n
    return reciprocal_pairs, strongly_connected


def _kalmanson_self_edge_count(
    rows: tuple[SelectedRow, ...],
    n: int,
) -> int:
    """Count strict Kalmanson rows that vanish in the selected quotient."""
    pairs = [pair(left, right) for left, right in combinations(range(n), 2)]
    quotient = UnionFind(pairs)
    for row in rows:
        spokes = [pair(row.center, witness) for witness in row.witnesses]
        for spoke in spokes[1:]:
            quotient.union(spokes[0], spoke)

    def vanishes(terms: tuple[tuple[Pair, int], ...]) -> bool:
        coefficients: Counter[Pair] = Counter()
        for raw_pair, coefficient in terms:
            coefficients[quotient.find(raw_pair)] += coefficient
        return all(coefficient == 0 for coefficient in coefficients.values())

    count = 0
    for a, b, c, d in combinations(range(n), 4):
        count += vanishes(
            (
                (pair(a, c), +1),
                (pair(b, d), +1),
                (pair(a, b), -1),
                (pair(c, d), -1),
            )
        )
        count += vanishes(
            (
                (pair(a, c), +1),
                (pair(b, d), +1),
                (pair(a, d), -1),
                (pair(b, c), -1),
            )
        )
    return count


def _family_distance_class(
    left: int,
    right: int,
    n: int,
    offsets: frozenset[int],
) -> DistanceClassToken:
    """Return the exact family quotient class of one unordered pair."""
    if (right - left) % n in offsets:
        return (0, left, -1)
    if (left - right) % n in offsets:
        return (0, right, -1)
    low, high = _pair(left, right)
    return (1, low, high)


def _primitive_kalmanson_vector(
    kind: int,
    quadruple: tuple[int, int, int, int],
    n: int,
    offsets: frozenset[int],
) -> PrimitiveVector:
    a, b, c, d = quadruple
    if kind == 1:
        terms = (
            ((a, c), +1),
            ((b, d), +1),
            ((a, b), -1),
            ((c, d), -1),
        )
    elif kind == 2:
        terms = (
            ((a, c), +1),
            ((b, d), +1),
            ((a, d), -1),
            ((b, c), -1),
        )
    else:
        raise ValueError("Kalmanson kind must be 1 or 2")

    coefficients: Counter[DistanceClassToken] = Counter()
    for (left, right), coefficient in terms:
        coefficients[_family_distance_class(left, right, n, offsets)] += coefficient
    reduced = {
        distance_class: coefficient
        for distance_class, coefficient in coefficients.items()
        if coefficient
    }
    divisor = 0
    for coefficient in reduced.values():
        divisor = gcd(divisor, abs(coefficient))
    if divisor == 0:
        return ()
    return tuple(
        sorted(
            (distance_class, coefficient // divisor)
            for distance_class, coefficient in reduced.items()
        )
    )


def _translate_distance_class(
    distance_class: DistanceClassToken,
    shift: int,
    n: int,
) -> DistanceClassToken:
    kind, first, second = distance_class
    if kind == 0:
        return (0, (first + shift) % n, -1)
    low, high = _pair((first + shift) % n, (second + shift) % n)
    return (1, low, high)


def _canonical_translation(vector: PrimitiveVector, n: int) -> PrimitiveVector:
    return min(
        tuple(
            sorted(
                (_translate_distance_class(distance_class, shift, n), coefficient)
                for distance_class, coefficient in vector
            )
        )
        for shift in range(n)
    )


def _primitive_inverse_orbit_summary(k: int) -> tuple[int, int, int]:
    """Return zero-based rows, vector orbits, and inverse-orbit pairs.

    Translating a strict row preserves the family.  Every translation orbit
    has a representative whose first cyclic label is zero, so it is enough to
    enumerate the two Kalmanson kinds on ``(0,b,c,d)``.  Canonicalizing the
    reduced primitive vector under all translations makes the inverse test
    exact while keeping the replay small.
    """
    n, raw_offsets = family_parameters(k)
    offsets = frozenset(raw_offsets)
    vector_orbits: set[PrimitiveVector] = set()
    zero_based_rows = 0
    for b, c, d in combinations(range(1, n), 3):
        quadruple = (0, b, c, d)
        for kind in (1, 2):
            zero_based_rows += 1
            vector = _primitive_kalmanson_vector(kind, quadruple, n, offsets)
            if vector:
                vector_orbits.add(_canonical_translation(vector, n))

    inverse_orbit_pairs: set[tuple[PrimitiveVector, PrimitiveVector]] = set()
    for vector in vector_orbits:
        inverse = _canonical_translation(
            tuple((distance_class, -coefficient) for distance_class, coefficient in vector),
            n,
        )
        if inverse in vector_orbits:
            inverse_orbit_pairs.add(
                (vector, inverse) if vector <= inverse else (inverse, vector)
            )
    return zero_based_rows, len(vector_orbits), len(inverse_orbit_pairs)


def _known_positive_circuit_size(k: int) -> int | None:
    """Replay the explicit four-row Kalmanson circuit in the ``k=8`` member."""
    if k != 8:
        return None
    n, raw_offsets = family_parameters(k)
    offsets = frozenset(raw_offsets)
    rows = (
        (1, (1, 8, 16, 27)),
        (2, (16, 18, 27, 37)),
        (2, (1, 16, 23, 37)),
        (1, (1, 16, 37, 44)),
    )
    vectors = [
        _primitive_kalmanson_vector(kind, quadruple, n, offsets)
        for kind, quadruple in rows
    ]
    if any(not vector for vector in vectors):
        return None
    total: Counter[DistanceClassToken] = Counter()
    for vector in vectors:
        for distance_class, coefficient in vector:
            total[distance_class] += coefficient
    if any(total.values()):
        return None
    return len(vectors)


def symbolic_inverse_classification(*, timeout_ms: int = 60_000) -> dict[str, object]:
    """Decide the all-``k`` primitive inverse-pair reduction in Presburger LIA.

    A quotient class is either one literal nonselected pair or one selected
    four-spoke star.  Two pair occurrences therefore name the same class iff
    they are the same unordered pair, or they are selected spokes with the
    same center.  An inverse pair matches four positive occurrences to four
    negative occurrences, giving four kind choices times ``4!`` bijections.

    The import is deliberately lazy because z3 is a development dependency.
    """
    import itertools

    import z3

    k = z3.Int("scalable_inverse_k")
    n = 6 * k - 1
    b, c, d, e, f, g, h = z3.Ints(
        "scalable_inverse_b scalable_inverse_c scalable_inverse_d "
        "scalable_inverse_e scalable_inverse_f scalable_inverse_g "
        "scalable_inverse_h"
    )
    offsets = (k + 1, 2 * k + 3, 3 * k + 1, 5 * k)

    def selected(center, witness):
        return z3.Or(
            *(
                z3.Or(witness - center == offset, witness - center == offset - n)
                for offset in offsets
            )
        )

    def same_class(first, second):
        left, right = first
        other_left, other_right = second
        return z3.Or(
            z3.And(left == other_left, right == other_right),
            z3.And(left == other_right, right == other_left),
            z3.And(
                left == other_left,
                selected(left, right),
                selected(left, other_right),
            ),
            z3.And(
                left == other_right,
                selected(left, right),
                selected(left, other_left),
            ),
            z3.And(
                right == other_left,
                selected(right, left),
                selected(right, other_right),
            ),
            z3.And(
                right == other_right,
                selected(right, left),
                selected(right, other_left),
            ),
        )

    def signed_pairs(quadruple, kind):
        a0, b0, c0, d0 = quadruple
        positive = ((a0, c0), (b0, d0))
        if kind == 1:
            negative = ((a0, b0), (c0, d0))
        else:
            negative = ((a0, d0), (b0, c0))
        return positive, negative

    first_quadruple = (z3.IntVal(0), b, c, d)
    second_quadruple = (e, f, g, h)
    templates: list[tuple[int, int, tuple[int, ...], object]] = []
    for first_kind in (1, 2):
        first_positive, first_negative = signed_pairs(
            first_quadruple, first_kind
        )
        for second_kind in (1, 2):
            second_positive, second_negative = signed_pairs(
                second_quadruple, second_kind
            )
            positive = first_positive + second_positive
            negative = first_negative + second_negative
            for permutation in itertools.permutations(range(4)):
                templates.append(
                    (
                        first_kind,
                        second_kind,
                        permutation,
                        z3.And(
                            *(
                                same_class(positive[index], negative[permutation[index]])
                                for index in range(4)
                            )
                        ),
                    )
                )

    order_constraints = (
        0 < b,
        b < c,
        c < d,
        d < n,
        0 <= e,
        e < f,
        f < g,
        g < h,
        h < n,
    )
    any_template = z3.Or(*(template[3] for template in templates))

    def decide(*extra, template=None) -> str:
        solver = z3.Solver()
        solver.set("timeout", timeout_ms)
        solver.add(*order_constraints, *extra)
        solver.add(any_template if template is None else template)
        return str(solver.check())

    decisions = {
        "all_k_at_least_8": decide(k >= 8),
        "all_k_at_least_6_except_6_7": decide(k >= 6, k != 6, k != 7),
        "k_6_control": decide(k == 6),
        "k_7_control": decide(k == 7),
    }
    reciprocal_solver = z3.Solver()
    reciprocal_solver.set("timeout", timeout_ms)
    reciprocal_solver.add(
        k >= 6,
        z3.Or(
            *(
                left_offset + right_offset == n
                for left_offset, right_offset in itertools.combinations_with_replacement(
                    offsets, 2
                )
            )
        ),
    )
    decisions["reciprocal_offset_k_at_least_6"] = str(reciprocal_solver.check())

    categories = ("impossible", "k6_only", "k7_only", "k6_or_k7", "unknown")
    totals: Counter[str] = Counter()
    by_kind: dict[str, Counter[str]] = {
        "K1/K1": Counter(),
        "K1/K2": Counter(),
        "K2/K1": Counter(),
        "K2/K2": Counter(),
    }
    for first_kind, second_kind, _permutation, template in templates:
        other = decide(k >= 6, k != 6, k != 7, template=template)
        at_six = decide(k == 6, template=template)
        at_seven = decide(k == 7, template=template)
        if other != "unsat" or at_six == "unknown" or at_seven == "unknown":
            category = "unknown"
        elif at_six == "sat" and at_seven == "sat":
            category = "k6_or_k7"
        elif at_six == "sat":
            category = "k6_only"
        elif at_seven == "sat":
            category = "k7_only"
        else:
            category = "impossible"
        totals[category] += 1
        by_kind[f"K{first_kind}/K{second_kind}"][category] += 1

    def complete(counter: Counter[str]) -> dict[str, int]:
        return {category: counter[category] for category in categories}

    return {
        "schema": "erdos97.scalable_kalmanson_inverse_control.v1",
        "solver": f"z3-{z3.get_version_string()}",
        "logic": "quantifier-free linear integer arithmetic",
        "matching_template_count": len(templates),
        "decisions": decisions,
        "template_classification": complete(totals),
        "template_classification_by_kind": {
            kind: complete(counter) for kind, counter in by_kind.items()
        },
    }


EXPECTED_SYMBOLIC_INVERSE_CLASSIFICATION = {
    "impossible": 70,
    "k6_only": 11,
    "k7_only": 11,
    "k6_or_k7": 4,
    "unknown": 0,
}

EXPECTED_SYMBOLIC_INVERSE_CLASSIFICATION_BY_KIND = {
    "K1/K1": {
        "impossible": 18,
        "k6_only": 1,
        "k7_only": 4,
        "k6_or_k7": 1,
        "unknown": 0,
    },
    "K1/K2": {
        "impossible": 17,
        "k6_only": 4,
        "k7_only": 2,
        "k6_or_k7": 1,
        "unknown": 0,
    },
    "K2/K1": {
        "impossible": 17,
        "k6_only": 2,
        "k7_only": 4,
        "k6_or_k7": 1,
        "unknown": 0,
    },
    "K2/K2": {
        "impossible": 18,
        "k6_only": 4,
        "k7_only": 1,
        "k6_or_k7": 1,
        "unknown": 0,
    },
}


def assert_expected_symbolic_inverse_classification(
    summary: dict[str, object],
) -> None:
    """Assert the exact all-parameter inverse-pair decision table."""
    decisions = summary.get("decisions")
    expected_decisions = {
        "all_k_at_least_8": "unsat",
        "all_k_at_least_6_except_6_7": "unsat",
        "k_6_control": "sat",
        "k_7_control": "sat",
        "reciprocal_offset_k_at_least_6": "unsat",
    }
    if decisions != expected_decisions:
        raise AssertionError(f"symbolic inverse decisions changed: {decisions!r}")
    if summary.get("matching_template_count") != 96:
        raise AssertionError("expected four kind choices times 4! matchings")
    if summary.get("template_classification") != (
        EXPECTED_SYMBOLIC_INVERSE_CLASSIFICATION
    ):
        raise AssertionError("symbolic inverse template classification changed")
    if summary.get("template_classification_by_kind") != (
        EXPECTED_SYMBOLIC_INVERSE_CLASSIFICATION_BY_KIND
    ):
        raise AssertionError("symbolic inverse per-kind classification changed")


def _adjacency(
    edges: tuple[StrictInequality, ...],
) -> dict[Pair, set[Pair]]:
    graph: dict[Pair, set[Pair]] = defaultdict(set)
    for edge in edges:
        graph[edge.outer_class].add(edge.inner_class)
        graph.setdefault(edge.inner_class, set())
    return dict(graph)


def _strong_components(graph: dict[Pair, set[Pair]]) -> list[set[Pair]]:
    index = 0
    indices: dict[Pair, int] = {}
    lowlinks: dict[Pair, int] = {}
    stack: list[Pair] = []
    on_stack: set[Pair] = set()
    components: list[set[Pair]] = []

    def visit(node: Pair) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for target in graph[node]:
            if target not in indices:
                visit(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[target])

        if lowlinks[node] != indices[node]:
            return
        component: set[Pair] = set()
        while True:
            target = stack.pop()
            on_stack.remove(target)
            component.add(target)
            if target == node:
                break
        components.append(component)

    for node in graph:
        if node not in indices:
            visit(node)
    return components


def _shortest_cycle(graph: dict[Pair, set[Pair]]) -> int | None:
    shortest: int | None = None
    for source in graph:
        distances = {source: 0}
        queue: deque[Pair] = deque([source])
        while queue:
            node = queue.popleft()
            next_distance = distances[node] + 1
            if shortest is not None and next_distance >= shortest:
                continue
            for target in graph[node]:
                if target == source:
                    shortest = next_distance
                    continue
                if target not in distances:
                    distances[target] = next_distance
                    queue.append(target)
    return shortest


def build_report(k: int) -> ScalableStrictCycleReport:
    """Recompute every finite check for one parameter ``k``."""
    n, offsets = family_parameters(k)
    rows = selected_rows(k)
    maximum_intersection, overlaps, crossing_violations, pair_cap = (
        _incidence_summary(rows, n)
    )
    hinge_count = len(
        find_hinge_instances(
            [list(row.witnesses) for row in rows],
            tuple(range(n)),
        )
    )
    reciprocal_pairs, selected_strong = _selected_digraph_summary(rows, n)
    fragile_offset = offsets[0]
    fragile_ok = all(
        vertex in rows[(vertex - fragile_offset) % n].witnesses
        for vertex in range(n)
    )
    minimum_forward, minimum_reverse, turn_feasible = _turn_summary(k)

    edges = strict_quotient_edges(n, tuple(range(n)), rows)
    graph = _adjacency(edges)
    components = _strong_components(graph)
    self_edges = sum(node in targets for node, targets in graph.items())
    kalmanson_self_edges = _kalmanson_self_edge_count(rows, n)
    (
        zero_based_rows,
        primitive_vector_orbits,
        primitive_inverse_orbits,
    ) = _primitive_inverse_orbit_summary(k)
    cyclic_components = [
        component
        for component in components
        if len(component) > 1
        or any(node in graph[node] for node in component)
    ]
    cyclic_component = cyclic_components[0] if len(cyclic_components) == 1 else set()
    internal_edges = sum(
        target in cyclic_component
        for node in cyclic_component
        for target in graph[node]
    )
    histogram = Counter(len(component) for component in components)

    return ScalableStrictCycleReport(
        k=k,
        n=n,
        offsets=offsets,
        maximum_row_intersection=maximum_intersection,
        two_overlap_count=overlaps,
        crossing_violations=crossing_violations,
        maximum_witness_pair_multiplicity=pair_cap,
        hinge_count=hinge_count,
        reciprocal_selected_pair_count=reciprocal_pairs,
        selected_digraph_strongly_connected=selected_strong,
        fragile_bijection_ok=fragile_ok,
        minimum_forward_turn_support=minimum_forward,
        minimum_reverse_turn_support=minimum_reverse,
        uniform_turn_strictly_feasible=turn_feasible,
        strict_edge_count=len(edges),
        strict_node_count=len(graph),
        self_edge_count=self_edges,
        kalmanson_self_edge_count=kalmanson_self_edges,
        kalmanson_zero_based_row_count=zero_based_rows,
        kalmanson_primitive_vector_orbit_count=primitive_vector_orbits,
        kalmanson_primitive_inverse_orbit_count=primitive_inverse_orbits,
        kalmanson_known_positive_circuit_size=_known_positive_circuit_size(k),
        scc_size_histogram=tuple(sorted(histogram.items())),
        cyclic_scc_count=len(cyclic_components),
        cyclic_scc_size=len(cyclic_component),
        cyclic_scc_internal_edges=internal_edges,
        shortest_strict_cycle=_shortest_cycle(graph),
    )


def assert_expected_structure(report: ScalableStrictCycleReport) -> None:
    """Assert the closed formulas proved in the accompanying note."""
    n = report.n
    if report.maximum_row_intersection != 2:
        raise AssertionError("row-intersection cap mismatch")
    if report.crossing_violations != 0:
        raise AssertionError("two-overlap crossing mismatch")
    if report.maximum_witness_pair_multiplicity != 2:
        raise AssertionError("witness-pair capacity mismatch")
    if report.hinge_count != 0:
        raise AssertionError("family must be hinge-free")
    if report.reciprocal_selected_pair_count != 0:
        raise AssertionError("family must have no reciprocal selected pair")
    if not report.selected_digraph_strongly_connected:
        raise AssertionError("selected digraph must be strongly connected")
    if not report.fragile_bijection_ok:
        raise AssertionError("fragile assignment must be bijective")
    if report.minimum_forward_turn_support != 2 * report.k + 2:
        raise AssertionError("forward turn support mismatch")
    if report.minimum_reverse_turn_support != 3 * report.k - 3:
        raise AssertionError("reverse turn support mismatch")
    if not report.uniform_turn_strictly_feasible:
        raise AssertionError("uniform turn assignment must be strictly feasible")
    if report.strict_edge_count != 9 * n:
        raise AssertionError("strict-edge count mismatch")
    if report.strict_node_count != 5 * n:
        raise AssertionError("strict-node count mismatch")
    if report.self_edge_count != 0:
        raise AssertionError("strict graph must have no self-edge")
    if report.kalmanson_self_edge_count != 0:
        raise AssertionError("selected quotient must have no Kalmanson self-edge")
    if report.kalmanson_zero_based_row_count != 2 * comb(n - 1, 3):
        raise AssertionError("zero-based Kalmanson row count mismatch")
    if report.kalmanson_primitive_inverse_orbit_count != 0:
        raise AssertionError("selected quotient must have no primitive inverse orbit")
    if report.k == 8 and report.kalmanson_known_positive_circuit_size != 4:
        raise AssertionError("the first family member must replay its four-row circuit")
    if report.scc_size_histogram != ((1, 4 * n), (n, 1)):
        raise AssertionError("strict SCC histogram mismatch")
    if report.cyclic_scc_count != 1 or report.cyclic_scc_size != n:
        raise AssertionError("unique cyclic SCC mismatch")
    if report.cyclic_scc_internal_edges != n:
        raise AssertionError("cyclic SCC must be one simple cycle")
    if report.shortest_strict_cycle != n:
        raise AssertionError("shortest strict-cycle length mismatch")
