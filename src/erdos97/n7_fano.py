"""n=7 incidence obstruction for Erdős Problem #97.

This module is intentionally finite and dependency-free. It formalizes the
small-case argument that a 7-vertex counterexample cannot exist.

Setup
-----
For a putative counterexample choose a 4-element witness set W_i for each
center i. If W_i and W_j have three common witnesses, then two distinct
circles share three points, impossible. Hence |W_i cap W_j| <= 2.

When n=7 this upper bound is tight everywhere by a counting argument. The
complements T_i = V \\ W_i form a Fano-plane incidence structure with i in
T_i. For each chord e={i,j}, the two common witnesses

    phi(e) = W_i cap W_j

form another chord. The map phi is a permutation of the 21 chords. In any
geometric realization e is perpendicular to phi(e), because both centers i
and j lie on the perpendicular bisector of the common-witness chord.

A permutation of 21 objects has an odd cycle. Alternating perpendicularity
around an odd cycle is impossible for nonzero Euclidean chords. Therefore no
n=7 counterexample exists.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations, permutations
from typing import Dict, Iterable, Mapping, Sequence, Tuple

Vertex = int
Pair = Tuple[int, int]
Triple = Tuple[int, int, int]
WitnessPattern = Tuple[Tuple[int, ...], ...]
ComplementPattern = Tuple[Triple, ...]
ChordMap = Dict[Pair, Pair]


def ordered_pair(a: int, b: int) -> Pair:
    """Return a sorted two-vertex tuple."""

    if a == b:
        raise ValueError("a chord must have two distinct vertices")
    return (a, b) if a < b else (b, a)


def normalize_row(row: Iterable[int]) -> Tuple[int, ...]:
    """Return a sorted row and reject duplicates."""

    out = tuple(sorted(int(x) for x in row))
    if len(set(out)) != len(out):
        raise ValueError(f"row contains a duplicate vertex: {out}")
    return out


def normalize_witness_pattern(pattern: Sequence[Sequence[int]]) -> WitnessPattern:
    """Normalize a witness pattern as a tuple of sorted rows."""

    return tuple(normalize_row(row) for row in pattern)


def validate_witness_pattern(pattern: Sequence[Sequence[int]], n: int | None = None) -> WitnessPattern:
    """Validate the basic witness-pattern shape.

    The function checks row length four, no repeated targets, no loops, and
    vertices in range. It does not assert the geometric circle-intersection
    cap; use :func:`pairwise_intersection_cap` for that.
    """

    W = normalize_witness_pattern(pattern)
    if n is None:
        n = len(W)
    if len(W) != n:
        raise ValueError(f"expected {n} rows, found {len(W)}")
    for i, row in enumerate(W):
        if len(row) != 4:
            raise ValueError(f"row {i} has length {len(row)}, expected 4")
        if i in row:
            raise ValueError(f"row {i} contains its own center")
        bad = [j for j in row if j < 0 or j >= n]
        if bad:
            raise ValueError(f"row {i} has vertices outside 0..{n - 1}: {bad}")
    return W


def all_chords(n: int) -> Tuple[Pair, ...]:
    """All unordered chords on vertices 0..n-1."""

    return tuple((a, b) for a, b in combinations(range(n), 2))


def indegrees(pattern: Sequence[Sequence[int]], n: int | None = None) -> Tuple[int, ...]:
    """Column sums of a witness pattern."""

    W = normalize_witness_pattern(pattern)
    if n is None:
        n = len(W)
    out = [0] * n
    for row in W:
        for j in row:
            out[j] += 1
    return tuple(out)


def pairwise_intersection_sizes(pattern: Sequence[Sequence[int]]) -> Dict[Pair, int]:
    """Size of W_i cap W_j for every pair of rows."""

    W = normalize_witness_pattern(pattern)
    return {
        (i, j): len(set(W[i]).intersection(W[j]))
        for i, j in combinations(range(len(W)), 2)
    }


def pairwise_intersection_cap(pattern: Sequence[Sequence[int]]) -> int:
    """Maximum common-witness count over two distinct centers."""

    sizes = pairwise_intersection_sizes(pattern)
    return max(sizes.values(), default=0)


def complements_from_witnesses(pattern: Sequence[Sequence[int]]) -> ComplementPattern:
    """Return T_i = V \\ W_i for an n=7 witness pattern.

    For n=7 each complement is a triple and should contain its center if the
    witness pattern has no loops.
    """

    W = validate_witness_pattern(pattern, n=7)
    vertices = set(range(7))
    return tuple(tuple(sorted(vertices.difference(row))) for row in W)  # type: ignore[return-value]


def witnesses_from_complements(complements: Sequence[Sequence[int]]) -> WitnessPattern:
    """Return W_i = V \\ T_i for n=7 complement triples."""

    if len(complements) != 7:
        raise ValueError(f"expected 7 complement triples, found {len(complements)}")
    vertices = set(range(7))
    rows: list[tuple[int, ...]] = []
    for i, row in enumerate(complements):
        T = normalize_row(row)
        if len(T) != 3:
            raise ValueError(f"complement row {i} has length {len(T)}, expected 3")
        if i not in T:
            raise ValueError(f"complement row {i} must contain its center {i}: {T}")
        rows.append(tuple(sorted(vertices.difference(T))))
    return validate_witness_pattern(rows, n=7)


def chord_permutation_from_witnesses(pattern: Sequence[Sequence[int]]) -> ChordMap:
    """Map each center chord {i,j} to the common-witness chord W_i cap W_j.

    Raises if the pattern does not satisfy the n=7 equality case where every
    pair of rows has exactly two common witnesses and the resulting map is a
    permutation of the 21 unordered chords.
    """

    W = validate_witness_pattern(pattern, n=7)
    mapping: ChordMap = {}
    for i, j in all_chords(7):
        common = tuple(sorted(set(W[i]).intersection(W[j])))
        if len(common) != 2:
            raise ValueError(
                f"rows {i} and {j} share {len(common)} witnesses, expected 2: {common}"
            )
        mapping[(i, j)] = (common[0], common[1])

    chord_set = set(all_chords(7))
    image_set = set(mapping.values())
    if set(mapping) != chord_set or image_set != chord_set or len(image_set) != 21:
        raise ValueError("common-witness map is not a permutation of the 21 chords")
    return mapping


def permutation_cycles(mapping: Mapping[Pair, Pair]) -> Tuple[Tuple[Pair, ...], ...]:
    """Cycle decomposition of a chord permutation."""

    domain = set(mapping)
    image = set(mapping.values())
    if domain != image:
        raise ValueError("mapping is not a permutation: domain and image differ")

    unseen = set(domain)
    cycles: list[tuple[Pair, ...]] = []
    while unseen:
        start = min(unseen)
        cur = start
        cycle: list[Pair] = []
        while cur in unseen:
            unseen.remove(cur)
            cycle.append(cur)
            cur = mapping[cur]
        if cur != start:
            raise ValueError(f"mapping chain from {start} did not close to its start")
        cycles.append(tuple(cycle))
    return tuple(sorted(cycles, key=lambda c: (len(c), c)))


@dataclass(frozen=True)
class N7Analysis:
    """Finite summary of an n=7 witness-pattern analysis."""

    witness_pattern: WitnessPattern
    complement_pattern: ComplementPattern
    indegrees: Tuple[int, ...]
    intersection_sizes: Tuple[int, ...]
    chord_map: Tuple[Tuple[Pair, Pair], ...]
    cycles: Tuple[Tuple[Pair, ...], ...]
    cycle_lengths: Tuple[int, ...]
    has_odd_cycle: bool
    geometrically_realizable: bool
    obstruction: str

    def to_jsonable(self) -> dict[str, object]:
        """Return a JSON-friendly representation."""

        return {
            "n": 7,
            "witness_pattern": [list(row) for row in self.witness_pattern],
            "complement_pattern": [list(row) for row in self.complement_pattern],
            "indegrees": list(self.indegrees),
            "intersection_sizes": list(self.intersection_sizes),
            "chord_map": [
                {"center_chord": list(edge), "common_witness_chord": list(image)}
                for edge, image in self.chord_map
            ],
            "cycles": [[list(edge) for edge in cycle] for cycle in self.cycles],
            "cycle_lengths": list(self.cycle_lengths),
            "has_odd_cycle": self.has_odd_cycle,
            "geometrically_realizable": self.geometrically_realizable,
            "obstruction": self.obstruction,
        }


def analyze_n7_witness_pattern(pattern: Sequence[Sequence[int]]) -> N7Analysis:
    """Analyze an n=7 witness pattern satisfying the circle-intersection cap.

    The returned ``geometrically_realizable`` field is always ``False`` for a
    cap-satisfying n=7 pattern, because the induced chord permutation must have
    an odd perpendicularity cycle.
    """

    W = validate_witness_pattern(pattern, n=7)
    cap = pairwise_intersection_cap(W)
    if cap > 2:
        raise ValueError(f"pattern violates the two-circle cap: max intersection {cap} > 2")

    row_intersections = tuple(pairwise_intersection_sizes(W).values())
    if set(row_intersections) != {2}:
        raise ValueError(
            "n=7 counting equality failed unexpectedly; expected all row intersections to be 2"
        )

    deg = indegrees(W, n=7)
    if deg != (4, 4, 4, 4, 4, 4, 4):
        raise ValueError(
            "n=7 counting equality failed unexpectedly; expected every indegree to be 4"
        )

    mapping = chord_permutation_from_witnesses(W)
    cycles = permutation_cycles(mapping)
    cycle_lengths = tuple(len(cycle) for cycle in cycles)
    has_odd = any(length % 2 for length in cycle_lengths)
    obstruction = (
        "The common-witness chord map is a permutation of the 21 chords. "
        "It has an odd cycle, but each map edge would impose perpendicularity; "
        "alternating perpendicularity around an odd cycle is impossible for "
        "nonzero Euclidean chords."
    )
    return N7Analysis(
        witness_pattern=W,
        complement_pattern=complements_from_witnesses(W),
        indegrees=deg,
        intersection_sizes=row_intersections,
        chord_map=tuple(sorted(mapping.items())),
        cycles=cycles,
        cycle_lengths=cycle_lengths,
        has_odd_cycle=has_odd,
        geometrically_realizable=not has_odd,
        obstruction=obstruction,
    )


def cyclic_fano_complements() -> ComplementPattern:
    """A canonical pointed Fano complement pattern.

    The triples are T_i = {i, i+1, i+3} modulo 7. They are the lines of the
    cyclic Fano plane, labelled so each row T_i contains its own center i.
    """

    return tuple(
        tuple(sorted({i, (i + 1) % 7, (i + 3) % 7})) for i in range(7)
    )  # type: ignore[return-value]


def cyclic_fano_witnesses() -> WitnessPattern:
    """Witness sets W_i complementary to :func:`cyclic_fano_complements`."""

    return witnesses_from_complements(cyclic_fano_complements())


def _apply_vertex_permutation_to_lines(
    lines: Sequence[Sequence[int]], perm: Sequence[int]
) -> Tuple[Triple, ...]:
    return tuple(
        sorted(tuple(tuple(sorted(perm[x] for x in line)) for line in lines))
    )  # type: ignore[return-value]


def all_labeled_fano_planes() -> Tuple[Tuple[Triple, ...], ...]:
    """All 30 labelled Fano planes on vertices 0..6.

    Every labelled Fano plane is obtained by relabelling the cyclic difference
    set construction. The automorphism group has order 168, so 7!/168 = 30
    distinct labelled planes; this function constructs and deduplicates them.
    """

    base = cyclic_fano_complements()
    planes = {
        _apply_vertex_permutation_to_lines(base, perm) for perm in permutations(range(7))
    }
    return tuple(sorted(planes))


def pointed_matchings_for_plane(lines: Sequence[Sequence[int]]) -> Tuple[ComplementPattern, ...]:
    """All bijective assignments i -> T_i with i in T_i for one Fano plane."""

    normalized_lines = tuple(normalize_row(line) for line in lines)
    if len(normalized_lines) != 7:
        raise ValueError("a Fano plane should have 7 lines")
    choices = {
        i: tuple(idx for idx, line in enumerate(normalized_lines) if i in line)
        for i in range(7)
    }
    assignment: list[int | None] = [None] * 7
    used: set[int] = set()
    out: list[ComplementPattern] = []

    def rec(i: int) -> None:
        if i == 7:
            out.append(tuple(normalized_lines[assignment[j]] for j in range(7)))  # type: ignore[index,arg-type]
            return
        for idx in choices[i]:
            if idx in used:
                continue
            used.add(idx)
            assignment[i] = idx
            rec(i + 1)
            assignment[i] = None
            used.remove(idx)

    rec(0)
    return tuple(sorted(out))


def all_pointed_fano_complements() -> Tuple[ComplementPattern, ...]:
    """All 720 n=7 complement patterns forced by the counting equality."""

    patterns: set[ComplementPattern] = set()
    for plane in all_labeled_fano_planes():
        patterns.update(pointed_matchings_for_plane(plane))
    return tuple(sorted(patterns))


def _dihedral_permutations(n: int = 7) -> Tuple[Tuple[int, ...], ...]:
    """Dihedral permutations preserving cyclic order on n labelled vertices."""

    return tuple(tuple((shift + sign * i) % n for i in range(n)) for sign in (1, -1) for shift in range(n))


def apply_vertex_permutation_to_complements(
    complements: Sequence[Sequence[int]], perm: Sequence[int]
) -> ComplementPattern:
    """Relabel a pointed complement pattern by a vertex permutation."""

    if len(complements) != 7:
        raise ValueError("expected 7 complement rows")
    out: list[Triple | None] = [None] * 7
    for old_center, line in enumerate(complements):
        new_center = perm[old_center]
        out[new_center] = tuple(sorted(perm[x] for x in line))  # type: ignore[assignment]
    return tuple(out)  # type: ignore[return-value]


def canonical_dihedral_representative(complements: Sequence[Sequence[int]]) -> ComplementPattern:
    """Canonical representative modulo rotations and reversal of cyclic order."""

    return min(apply_vertex_permutation_to_complements(complements, perm) for perm in _dihedral_permutations())


def pointed_fano_dihedral_classes() -> Tuple[ComplementPattern, ...]:
    """The 54 pointed n=7 Fano patterns up to dihedral cyclic relabelling."""

    return tuple(sorted({canonical_dihedral_representative(T) for T in all_pointed_fano_complements()}))


def _json_pair(pair: Pair) -> list[int]:
    return [int(pair[0]), int(pair[1])]


def _json_row(row: Sequence[int]) -> list[int]:
    return [int(x) for x in row]


def dihedral_orbit_size_distribution() -> dict[int, int]:
    """Distribution of orbit sizes among the 54 dihedral classes."""

    sizes: dict[ComplementPattern, int] = {}
    for T in all_pointed_fano_complements():
        rep = canonical_dihedral_representative(T)
        sizes[rep] = sizes.get(rep, 0) + 1
    return dict(Counter(sizes.values()))


def dihedral_class_records() -> list[dict[str, object]]:
    """Canonical class representatives with induced perpendicularity constraints."""

    records: list[dict[str, object]] = []
    for idx, T in enumerate(pointed_fano_dihedral_classes()):
        witnesses = witnesses_from_complements(T)
        analysis = analyze_n7_witness_pattern(witnesses)
        records.append(
            {
                "id": idx,
                "complements_T": [_json_row(row) for row in analysis.complement_pattern],
                "witnesses_W": [_json_row(row) for row in analysis.witness_pattern],
                "indegrees": list(analysis.indegrees),
                "intersection_sizes": list(analysis.intersection_sizes),
                "perpendicularity_map": [
                    {
                        "center_chord": _json_pair(edge),
                        "common_witness_chord": _json_pair(image),
                    }
                    for edge, image in analysis.chord_map
                ],
                "perpendicularity_cycles": [
                    [_json_pair(edge) for edge in cycle] for cycle in analysis.cycles
                ],
                "cycle_lengths": list(analysis.cycle_lengths),
                "has_odd_perpendicularity_cycle": analysis.has_odd_cycle,
                "geometrically_realizable_under_required_perpendicularities": analysis.geometrically_realizable,
                "obstruction": analysis.obstruction,
            }
        )
    return records


def enumeration_data() -> dict[str, object]:
    """Full deterministic JSON-serializable n=7 enumeration artifact."""

    planes = all_labeled_fano_planes()
    complements = all_pointed_fano_complements()
    classes = pointed_fano_dihedral_classes()

    all_cycle_type_counts: Counter[str] = Counter()
    for T in complements:
        analysis = analyze_n7_witness_pattern(witnesses_from_complements(T))
        key = "+".join(str(x) for x in sorted(analysis.cycle_lengths))
        all_cycle_type_counts[key] += 1

    class_cycle_type_counts: Counter[str] = Counter()
    odd_cycle_classes = 0
    for T in classes:
        analysis = analyze_n7_witness_pattern(witnesses_from_complements(T))
        key = "+".join(str(x) for x in sorted(analysis.cycle_lengths))
        class_cycle_type_counts[key] += 1
        if analysis.has_odd_cycle:
            odd_cycle_classes += 1

    orbit_sizes = dihedral_orbit_size_distribution()
    return {
        "schema": "erdos97_n7_fano_dihedral_representatives_v1",
        "status": "exact_finite_enumeration_for_n7_not_general_solution",
        "n": 7,
        "counts": {
            "labelled_fano_planes": len(planes),
            "pointed_fano_patterns": len(complements),
            "dihedral_classes": len(classes),
            "dihedral_orbit_size_distribution": {str(k): orbit_sizes[k] for k in sorted(orbit_sizes)},
            "all_pattern_cycle_type_counts": dict(sorted(all_cycle_type_counts.items())),
            "dihedral_class_cycle_type_counts": dict(sorted(class_cycle_type_counts.items())),
            "classes_with_odd_perpendicularity_cycle": odd_cycle_classes,
            "all_classes_obstructed": odd_cycle_classes == len(classes),
        },
        "conclusion": "No n=7 witness pattern satisfying the two-circle cap can be geometrically realized.",
        "representatives": dihedral_class_records(),
    }


def enumeration_summary() -> dict[str, object]:
    """Summarize the finite n=7 enumeration and obstruction."""

    data = enumeration_data()
    counts = data["counts"]
    assert isinstance(counts, dict)
    return {
        "labelled_fano_planes": counts["labelled_fano_planes"],
        "pointed_fano_patterns": counts["pointed_fano_patterns"],
        "dihedral_classes": counts["dihedral_classes"],
        "dihedral_orbit_size_distribution": counts["dihedral_orbit_size_distribution"],
        "cycle_type_counts": counts["dihedral_class_cycle_type_counts"],
        "all_pattern_cycle_type_counts": counts["all_pattern_cycle_type_counts"],
        "classes_with_odd_perpendicularity_cycle": counts["classes_with_odd_perpendicularity_cycle"],
        "all_classes_obstructed": counts["all_classes_obstructed"],
        "conclusion": data["conclusion"],
    }
