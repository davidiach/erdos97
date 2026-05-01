"""Combinatorial checks for fragile-cover hypergraphs.

These checks model only the consequences proved from the fragile-cover lemma:
fragile centers give pointed four-sets that cover all vertices, two fragile
cohorts overlap in at most two vertices, and a two-overlap forces the cyclic
crossing rule. Passing these checks is not a geometric realization certificate.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Mapping, Sequence

from erdos97.incidence_filters import chords_cross_in_order, normalize_chord

Rows = dict[int, list[int]]
WitnessMap = dict[int, int]


@dataclass(frozen=True)
class FragileHypergraphCheck:
    n: int
    fragile_centers: list[int]
    cover_ok: bool
    self_exclusion_ok: bool
    uniformity_ok: bool
    pairwise_intersection_ok: bool
    crossing_ok: bool
    witness_map_ok: bool | None
    cover_missing: list[int]
    self_exclusion_violations: list[int]
    uniformity_violations: list[dict[str, object]]
    pairwise_intersection_violations: list[dict[str, object]]
    crossing_violations: list[dict[str, object]]
    witness_map_violations: list[dict[str, object]]

    @property
    def ok(self) -> bool:
        witness_ok = True if self.witness_map_ok is None else self.witness_map_ok
        return (
            self.cover_ok
            and self.self_exclusion_ok
            and self.uniformity_ok
            and self.pairwise_intersection_ok
            and self.crossing_ok
            and witness_ok
        )


def _validate_labels(n: int, rows: Mapping[int, Sequence[int]]) -> None:
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    for center, row in rows.items():
        if center < 0 or center >= n:
            raise ValueError(f"center out of range: {center}")
        for label in row:
            if label < 0 or label >= n:
                raise ValueError(f"row {center} has out-of-range label {label}")


def covered_vertices(rows: Mapping[int, Sequence[int]]) -> set[int]:
    """Return all vertices that appear in at least one fragile cohort."""
    out: set[int] = set()
    for row in rows.values():
        out.update(row)
    return out


def canonical_witness_map(n: int, rows: Mapping[int, Sequence[int]]) -> WitnessMap:
    """Choose the smallest fragile center covering each vertex."""
    _validate_labels(n, rows)
    witnesses: WitnessMap = {}
    for vertex in range(n):
        centers = sorted(center for center, row in rows.items() if vertex in row)
        if not centers:
            raise ValueError(f"vertex {vertex} is not covered")
        witnesses[vertex] = centers[0]
    return witnesses


def check_fragile_hypergraph(
    n: int,
    rows: Mapping[int, Sequence[int]],
    order: Sequence[int] | None = None,
    witness_map: Mapping[int, int] | None = None,
) -> FragileHypergraphCheck:
    """Check fragile-cover axioms for a partial pointed four-uniform system."""
    _validate_labels(n, rows)
    if order is None:
        order = list(range(n))
    if sorted(order) != list(range(n)):
        raise ValueError("order must be a permutation of range(n)")

    normalized_rows: Rows = {int(center): [int(v) for v in row] for center, row in rows.items()}
    centers = sorted(normalized_rows)

    cover = covered_vertices(normalized_rows)
    cover_missing = [vertex for vertex in range(n) if vertex not in cover]

    self_exclusion_violations = [
        center for center, row in normalized_rows.items() if center in row
    ]

    uniformity_violations: list[dict[str, object]] = []
    for center, row in sorted(normalized_rows.items()):
        if len(row) != 4 or len(set(row)) != 4:
            uniformity_violations.append(
                {
                    "center": center,
                    "row": row,
                    "size": len(row),
                    "distinct_size": len(set(row)),
                }
            )

    pairwise_intersection_violations: list[dict[str, object]] = []
    crossing_violations: list[dict[str, object]] = []
    row_sets = {center: set(row) for center, row in normalized_rows.items()}
    for left, right in combinations(centers, 2):
        inter = sorted(row_sets[left] & row_sets[right])
        if len(inter) > 2:
            pairwise_intersection_violations.append(
                {
                    "centers": [left, right],
                    "intersection": inter,
                    "intersection_size": len(inter),
                }
            )
        if len(inter) == 2:
            source = normalize_chord(left, right)
            target = normalize_chord(inter[0], inter[1])
            if not chords_cross_in_order(source, target, order):
                crossing_violations.append(
                    {
                        "source": [source[0], source[1]],
                        "target": [target[0], target[1]],
                        "order": list(order),
                    }
                )

    witness_map_violations: list[dict[str, object]] = []
    witness_map_ok: bool | None
    if witness_map is None:
        witness_map_ok = None
    else:
        witness_map_ok = True
        for vertex in range(n):
            if vertex not in witness_map:
                witness_map_ok = False
                witness_map_violations.append(
                    {"vertex": vertex, "reason": "missing witness"}
                )
                continue
            center = int(witness_map[vertex])
            if center not in normalized_rows:
                witness_map_ok = False
                witness_map_violations.append(
                    {
                        "vertex": vertex,
                        "center": center,
                        "reason": "witness center is not fragile",
                    }
                )
            elif vertex not in normalized_rows[center]:
                witness_map_ok = False
                witness_map_violations.append(
                    {
                        "vertex": vertex,
                        "center": center,
                        "reason": "witness center does not cover vertex",
                    }
                )

    return FragileHypergraphCheck(
        n=n,
        fragile_centers=centers,
        cover_ok=not cover_missing,
        self_exclusion_ok=not self_exclusion_violations,
        uniformity_ok=not uniformity_violations,
        pairwise_intersection_ok=not pairwise_intersection_violations,
        crossing_ok=not crossing_violations,
        witness_map_ok=witness_map_ok,
        cover_missing=cover_missing,
        self_exclusion_violations=self_exclusion_violations,
        uniformity_violations=uniformity_violations,
        pairwise_intersection_violations=pairwise_intersection_violations,
        crossing_violations=crossing_violations,
        witness_map_violations=witness_map_violations,
    )


def block6_family(blocks: int) -> tuple[int, Rows]:
    """Return an abstract covering family satisfying the fragile hypergraph rules.

    Each block of six vertices has two fragile centers. In local coordinates
    b,b+1,...,b+5, the rows are

        b   -> {b+1,b+2,b+3,b+4}
        b+3 -> {b,b+2,b+4,b+5}

    The two rows intersect in {b+2,b+4}; the center chord {b,b+3}
    separates that pair in the natural cyclic order. Different blocks are
    disjoint, so all cross-block intersection constraints are vacuous.
    """
    if blocks <= 0:
        raise ValueError(f"blocks must be positive, got {blocks}")
    rows: Rows = {}
    for block in range(blocks):
        base = 6 * block
        rows[base] = [base + 1, base + 2, base + 3, base + 4]
        rows[base + 3] = [base, base + 2, base + 4, base + 5]
    return 6 * blocks, rows


def check_to_json(result: FragileHypergraphCheck) -> dict[str, object]:
    """Return a JSON-serializable check result."""
    return {
        "type": "fragile_hypergraph_check",
        "n": result.n,
        "fragile_centers": result.fragile_centers,
        "ok": result.ok,
        "cover_ok": result.cover_ok,
        "self_exclusion_ok": result.self_exclusion_ok,
        "uniformity_ok": result.uniformity_ok,
        "pairwise_intersection_ok": result.pairwise_intersection_ok,
        "crossing_ok": result.crossing_ok,
        "witness_map_ok": result.witness_map_ok,
        "cover_missing": result.cover_missing,
        "self_exclusion_violations": result.self_exclusion_violations,
        "uniformity_violations": result.uniformity_violations,
        "pairwise_intersection_violations": result.pairwise_intersection_violations,
        "crossing_violations": result.crossing_violations,
        "witness_map_violations": result.witness_map_violations,
    }


def rows_from_zero_one_matrix(matrix: Sequence[Sequence[int]]) -> Rows:
    """Convert a full zero-one selected-row matrix to row-set form."""
    rows: Rows = {}
    for center, row in enumerate(matrix):
        rows[center] = [idx for idx, value in enumerate(row) if value]
    return rows


def covering_subsets(
    n: int,
    rows: Mapping[int, Sequence[int]],
    max_examples: int = 8,
    max_size: int | None = None,
) -> dict[str, object]:
    """Return small-n cover statistics for possible fragile centers.

    The subset size is the number of rows declared fragile. This is purely an
    incidence-level calculation: it assumes any listed row is eligible to be
    fragile and asks only whether the fragile rows cover every vertex.
    """
    _validate_labels(n, rows)
    if max_examples < 0:
        raise ValueError("max_examples must be nonnegative")
    if max_size is None:
        max_size = len(rows)
    if max_size < 0:
        raise ValueError("max_size must be nonnegative")

    centers = sorted(rows)
    row_sets = {center: set(row) for center, row in rows.items()}
    counts_by_size: dict[int, int] = {}
    examples_by_size: dict[int, list[list[int]]] = {}
    min_size: int | None = None
    total = 0

    for size in range(min(max_size, len(centers)) + 1):
        for subset in combinations(centers, size):
            covered: set[int] = set()
            for center in subset:
                covered.update(row_sets[center])
            if len(covered) != n:
                continue
            total += 1
            counts_by_size[size] = counts_by_size.get(size, 0) + 1
            if min_size is None:
                min_size = size
            bucket = examples_by_size.setdefault(size, [])
            if len(bucket) < max_examples:
                bucket.append([int(center) for center in subset])

    return {
        "cover_exists": total > 0,
        "searched_up_to_size": min(max_size, len(centers)),
        "search_complete": max_size >= len(centers),
        "min_cover_size": min_size,
        "total_cover_subsets": total,
        "cover_counts_by_size": {
            str(size): count for size, count in sorted(counts_by_size.items())
        },
        "example_covers_by_size": {
            str(size): examples for size, examples in sorted(examples_by_size.items())
        },
    }
