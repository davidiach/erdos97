"""Inversive point-line incidence diagnostics for selected-witness systems.

The diagnostics here are proof-mining aids. They do not prove Erdos Problem
#97, certify Euclidean realizability, or claim a counterexample.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Sequence

from erdos97 import n9_vertex_circle_exhaustive as n9
from erdos97.n9_vertex_circle_obstruction_shapes import pre_vertex_circle_assignments

SCHEMA = "erdos97.n9_inversive_incidence_pilot.v1"
STATUS = "INVERSION_INCIDENCE_HEURISTIC_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Inversive point-line incidence diagnostic on the 184 regenerated n=9 "
    "pre-vertex-circle frontier assignments; not a proof of n=9, not a "
    "counterexample, not an independent review of the exhaustive checker, and "
    "not a global status update."
)

EXPECTED_ASSIGNMENTS = 184
EXPECTED_NODES = 100_817
EXPECTED_TOTAL_PIVOTS = EXPECTED_ASSIGNMENTS * n9.N
EXPECTED_TOTAL_LINE_SEEDS = EXPECTED_ASSIGNMENTS * n9.N * n9.ROW_SIZE
EXPECTED_TOTAL_CLOSED_LINES = 6_624
EXPECTED_COMPRESSED_PIVOTS = 0
EXPECTED_ASSIGNMENTS_WITH_COMPRESSION = 0
EXPECTED_ALL_COLLINEAR_PIVOTS = 0
EXPECTED_MAX_CLOSED_LINE_SIZE = 3
EXPECTED_HISTOGRAMS = {
    "pivot_seed_count": {"4": 1_656},
    "pivot_merged_line_count": {"4": 1_656},
    "pivot_max_closed_line_size": {"3": 1_656},
    "pivot_repeated_pair_count": {"0": 1_656},
    "closed_line_size": {"3": 6_624},
    "assignment_max_closed_line_size": {"3": 184},
    "assignment_compressed_pivot_count": {"0": 184},
}

Line = tuple[int, ...]
Rows = Sequence[Sequence[int]]


@dataclass(frozen=True)
class InversionLineSeed:
    """One line forced after inversion around ``pivot``.

    If ``pivot in S_center``, then inversion around the pivot maps the selected
    circle of row ``center`` to a line containing the three inverted witnesses
    in ``S_center - {pivot}``.
    """

    pivot: int
    center: int
    points: Line

    def to_json(self) -> dict[str, object]:
        return {
            "pivot": int(self.pivot),
            "center": int(self.center),
            "points": [int(point) for point in self.points],
        }


@dataclass(frozen=True)
class PivotIncidence:
    """Closed line-incidence summary for one inversion pivot."""

    pivot: int
    seeds: tuple[InversionLineSeed, ...]
    closed_lines: tuple[Line, ...]
    pair_multiplicities: tuple[tuple[tuple[int, int], int], ...]

    @property
    def seed_count(self) -> int:
        return len(self.seeds)

    @property
    def merged_line_count(self) -> int:
        return len(self.closed_lines)

    @property
    def max_closed_line_size(self) -> int:
        if not self.closed_lines:
            return 0
        return max(len(line) for line in self.closed_lines)

    @property
    def repeated_pair_count(self) -> int:
        return sum(1 for _, count in self.pair_multiplicities if count > 1)

    def to_json(self) -> dict[str, object]:
        return {
            "pivot": int(self.pivot),
            "seed_count": self.seed_count,
            "merged_line_count": self.merged_line_count,
            "max_closed_line_size": self.max_closed_line_size,
            "repeated_pair_count": self.repeated_pair_count,
            "line_size_counts": _json_counter(Counter(len(line) for line in self.closed_lines)),
            "seeds": [seed.to_json() for seed in self.seeds],
            "closed_lines": [[int(point) for point in line] for line in self.closed_lines],
            "repeated_pairs": [
                {"pair": [int(pair[0]), int(pair[1])], "count": int(count)}
                for pair, count in self.pair_multiplicities
                if count > 1
            ],
        }


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _rows_from_assignment(assign: dict[int, int]) -> list[list[int]]:
    return [list(n9.MASK_BITS[assign[center]]) for center in range(n9.N)]


def inversion_line_seeds(rows: Rows, pivot: int) -> tuple[InversionLineSeed, ...]:
    """Return the line triples forced by inversion around one pivot."""

    seeds: list[InversionLineSeed] = []
    for center, row in enumerate(rows):
        if pivot not in row:
            continue
        points = tuple(sorted(point for point in row if point != pivot))
        if len(points) != n9.ROW_SIZE - 1:
            raise AssertionError("inversion seed does not have three witness points")
        seeds.append(InversionLineSeed(pivot=pivot, center=center, points=points))
    return tuple(sorted(seeds, key=lambda seed: (seed.center, seed.points)))


def close_lines_from_seeds(seeds: Sequence[InversionLineSeed]) -> tuple[Line, ...]:
    """Merge line seeds that must be the same Euclidean line.

    Two forced lines sharing two points are the same line. After merging two
    line sets, the enlarged line can create new two-point overlaps, so the
    closure is iterated to a fixed point.
    """

    lines = [set(seed.points) for seed in seeds]
    changed = True
    while changed:
        changed = False
        for first in range(len(lines)):
            if changed:
                break
            for second in range(first + 1, len(lines)):
                if len(lines[first] & lines[second]) < 2:
                    continue
                lines[first].update(lines[second])
                del lines[second]
                changed = True
                break
    return tuple(sorted(tuple(sorted(line)) for line in lines))


def seed_pair_multiplicities(
    seeds: Sequence[InversionLineSeed],
) -> tuple[tuple[tuple[int, int], int], ...]:
    """Count witness-pairs that occur together in forced inversion lines."""

    counts: Counter[tuple[int, int]] = Counter()
    for seed in seeds:
        for pair in combinations(seed.points, 2):
            counts[tuple(sorted(pair))] += 1
    return tuple(sorted(counts.items()))


def pivot_inversive_incidence(rows: Rows, pivot: int) -> PivotIncidence:
    """Return the closed point-line incidence system for one pivot."""

    seeds = inversion_line_seeds(rows, pivot)
    return PivotIncidence(
        pivot=pivot,
        seeds=seeds,
        closed_lines=close_lines_from_seeds(seeds),
        pair_multiplicities=seed_pair_multiplicities(seeds),
    )


def assignment_inversive_incidence(rows: Rows) -> tuple[PivotIncidence, ...]:
    """Return inversion incidence summaries for every label as pivot."""

    return tuple(pivot_inversive_incidence(rows, pivot) for pivot in range(len(rows)))


def _representative_key(
    assignment_index: int,
    pivot_summary: PivotIncidence,
) -> tuple[int, int, int, int]:
    return (
        pivot_summary.max_closed_line_size,
        pivot_summary.repeated_pair_count,
        pivot_summary.seed_count,
        -assignment_index,
    )


def _assignment_to_json(rows: Rows) -> list[list[int]]:
    return [[int(witness) for witness in row] for row in rows]


def n9_inversive_incidence_summary() -> dict[str, object]:
    """Return the stable n=9 inversive-incidence pilot artifact."""

    assignments, nodes = pre_vertex_circle_assignments()
    seed_count_histogram: Counter[int] = Counter()
    merged_line_count_histogram: Counter[int] = Counter()
    max_line_size_histogram: Counter[int] = Counter()
    repeated_pair_count_histogram: Counter[int] = Counter()
    line_size_histogram: Counter[int] = Counter()
    assignment_max_line_size_histogram: Counter[int] = Counter()
    assignment_compressed_pivot_count_histogram: Counter[int] = Counter()
    assignments_with_compression = 0
    total_line_seeds = 0
    total_closed_lines = 0
    compressed_pivots = 0
    all_collinear_pivots = 0
    best_rows: list[list[int]] | None = None
    best_pivot: PivotIncidence | None = None
    best_assignment_index = -1

    for assignment_index, assign in enumerate(assignments):
        rows = _rows_from_assignment(assign)
        pivot_summaries = assignment_inversive_incidence(rows)
        assignment_max = 0
        assignment_compressed = 0
        for pivot_summary in pivot_summaries:
            total_line_seeds += pivot_summary.seed_count
            total_closed_lines += pivot_summary.merged_line_count
            seed_count_histogram[pivot_summary.seed_count] += 1
            merged_line_count_histogram[pivot_summary.merged_line_count] += 1
            max_line_size_histogram[pivot_summary.max_closed_line_size] += 1
            repeated_pair_count_histogram[pivot_summary.repeated_pair_count] += 1
            for line in pivot_summary.closed_lines:
                line_size_histogram[len(line)] += 1

            assignment_max = max(assignment_max, pivot_summary.max_closed_line_size)
            if pivot_summary.max_closed_line_size > n9.ROW_SIZE - 1:
                compressed_pivots += 1
                assignment_compressed += 1
            if pivot_summary.max_closed_line_size == n9.N - 1:
                all_collinear_pivots += 1

            if best_pivot is None or _representative_key(
                assignment_index,
                pivot_summary,
            ) > _representative_key(best_assignment_index, best_pivot):
                best_rows = rows
                best_pivot = pivot_summary
                best_assignment_index = assignment_index

        if assignment_compressed:
            assignments_with_compression += 1
        assignment_max_line_size_histogram[assignment_max] += 1
        assignment_compressed_pivot_count_histogram[assignment_compressed] += 1

    if best_rows is None or best_pivot is None:
        raise AssertionError("no n=9 inversion incidence representative found")

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "The official/global status remains falsifiable/open.",
            "This pilot records forced point-line incidences after inversion; it is not a realizability or impossibility certificate.",
        ],
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "cyclic_order": list(n9.ORDER),
        "source_frontier": {
            "source": "n9 pre-vertex-circle assignments regenerated by erdos97.n9_vertex_circle_obstruction_shapes.pre_vertex_circle_assignments",
            "source_artifact": "data/certificates/n9_vertex_circle_exhaustive.json",
            "row0_choices": len(n9.OPTIONS[0]),
            "nodes_visited": int(nodes),
            "assignment_count": len(assignments),
        },
        "inversion_rule": {
            "description": (
                "For pivot b and any selected row i with b in S_i, inversion "
                "around b maps the row circle through b to a line containing "
                "the three inverted witnesses S_i - {b}."
            ),
            "incidence_only": True,
            "line_closure_rule": (
                "Forced lines sharing at least two inverted points are merged "
                "to a fixed point."
            ),
        },
        "summary": {
            "total_pivots": len(assignments) * n9.N,
            "total_line_seeds": int(total_line_seeds),
            "total_closed_lines": int(total_closed_lines),
            "compressed_pivots": int(compressed_pivots),
            "assignments_with_compression": int(assignments_with_compression),
            "all_collinear_pivots": int(all_collinear_pivots),
            "max_closed_line_size": max(max_line_size_histogram),
        },
        "histograms": {
            "pivot_seed_count": _json_counter(seed_count_histogram),
            "pivot_merged_line_count": _json_counter(merged_line_count_histogram),
            "pivot_max_closed_line_size": _json_counter(max_line_size_histogram),
            "pivot_repeated_pair_count": _json_counter(repeated_pair_count_histogram),
            "closed_line_size": _json_counter(line_size_histogram),
            "assignment_max_closed_line_size": _json_counter(
                assignment_max_line_size_histogram
            ),
            "assignment_compressed_pivot_count": _json_counter(
                assignment_compressed_pivot_count_histogram
            ),
        },
        "representative": {
            "assignment_index": int(best_assignment_index),
            "selected_rows": _assignment_to_json(best_rows),
            "pivot_summary": best_pivot.to_json(),
        },
        "interpretation": [
            "The inversion transform is exact at the incidence level, but this pilot does not check realizability of the resulting point-line systems.",
            "The n=9 frontier has only four line seeds per pivot on average, so this is not dense enough by itself to trigger a global Szemeredi-Trotter-style contradiction.",
            "The useful output is motif data: pivots where several forced triples close into larger collinear blocks are candidates for small local lemmas.",
            "The pilot currently finds no standalone incidence-only contradiction.",
        ],
        "provenance": {
            "generator": "scripts/check_n9_inversive_incidence_pilot.py",
            "command": "python scripts/check_n9_inversive_incidence_pilot.py --assert-expected --write",
        },
    }
    assert_expected_counts(payload)
    return payload


def assert_expected_counts(payload: dict[str, object]) -> None:
    """Assert that the pilot still targets the known n=9 frontier."""

    if payload["schema"] != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload['schema']}")
    if payload["status"] != STATUS:
        raise AssertionError(f"unexpected status: {payload['status']}")
    if payload["trust"] != TRUST:
        raise AssertionError(f"unexpected trust: {payload['trust']}")
    source = payload["source_frontier"]
    summary = payload["summary"]
    if not isinstance(source, dict) or not isinstance(summary, dict):
        raise AssertionError("missing source or summary block")
    if source["nodes_visited"] != EXPECTED_NODES:
        raise AssertionError(f"unexpected nodes: {source['nodes_visited']}")
    if source["assignment_count"] != EXPECTED_ASSIGNMENTS:
        raise AssertionError(f"unexpected assignments: {source['assignment_count']}")
    if summary["total_pivots"] != EXPECTED_TOTAL_PIVOTS:
        raise AssertionError(f"unexpected pivot count: {summary['total_pivots']}")
    if summary["total_line_seeds"] != EXPECTED_TOTAL_LINE_SEEDS:
        raise AssertionError(f"unexpected line seeds: {summary['total_line_seeds']}")
    if summary["total_closed_lines"] != EXPECTED_TOTAL_CLOSED_LINES:
        raise AssertionError(f"unexpected closed lines: {summary['total_closed_lines']}")
    if summary["compressed_pivots"] != EXPECTED_COMPRESSED_PIVOTS:
        raise AssertionError(f"unexpected compressed pivots: {summary['compressed_pivots']}")
    if summary["assignments_with_compression"] != EXPECTED_ASSIGNMENTS_WITH_COMPRESSION:
        raise AssertionError(
            "unexpected assignments with compression: "
            f"{summary['assignments_with_compression']}"
        )
    if summary["all_collinear_pivots"] != EXPECTED_ALL_COLLINEAR_PIVOTS:
        raise AssertionError(
            f"unexpected all-collinear pivots: {summary['all_collinear_pivots']}"
        )
    if summary["max_closed_line_size"] != EXPECTED_MAX_CLOSED_LINE_SIZE:
        raise AssertionError(
            f"unexpected max closed line size: {summary['max_closed_line_size']}"
        )
    histograms = payload["histograms"]
    if not isinstance(histograms, dict):
        raise AssertionError("missing histogram block")
    for key, expected in EXPECTED_HISTOGRAMS.items():
        if histograms.get(key) != expected:
            raise AssertionError(f"unexpected histogram {key}: {histograms.get(key)}")
