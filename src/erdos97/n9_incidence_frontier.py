"""Bounded n=9 selected-witness incidence frontier diagnostics.

This module explores the n=9 selected-witness incidence layer with row 0 fixed
to a chosen four-witness row.  The default run prioritizes the registered
rectangle-trap seed and emits filter counts rather than a completeness claim.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Sequence

from erdos97.incidence_filters import (
    adjacent_pairs,
    crossing_bisector_violations,
    forced_equal_classes_from_matrix,
    mutual_midpoint_matrix,
    normalize_chord,
    odd_forced_perpendicular_cycle,
    phi4_rectangle_trap_certificates,
    phi_directed_4_cycles,
    phi_map,
)

N = 9
ROW_SIZE = 4
PAIR_CAP = 2
DEFAULT_ORDER = tuple(range(N))
DEFAULT_ROW0_WITNESSES = (1, 2, 3, 8)
CANONICAL_ROW0_WITNESSES = (1, 2, 3, 4)
MAX_INDEGREE = (PAIR_CAP * (N - 1)) // (ROW_SIZE - 1)

Pattern = Sequence[Sequence[int]]
Chord = tuple[int, int]

PARTIAL_REJECTION_REASONS = (
    "row_pair_intersection_cap",
    "adjacent_two_overlap",
    "crossing_bisector",
    "column_indegree_upper",
    "column_pair_cap",
)

FULL_CLASSIFICATION_STATUSES = (
    "row_pair_intersection_cap",
    "adjacent_two_overlap",
    "crossing_bisector",
    "column_indegree_upper",
    "column_pair_cap",
    "odd_forced_perpendicular_cycle",
    "mutual_midpoint_collapse",
    "phi4_rectangle_trap",
    "accepted_frontier",
)

N9_RECTANGLE_TRAP_PATTERN: list[list[int]] = [
    [1, 2, 3, 8],
    [0, 2, 4, 7],
    [1, 3, 5, 7],
    [1, 4, 6, 8],
    [0, 2, 5, 6],
    [3, 4, 6, 7],
    [2, 5, 7, 8],
    [0, 3, 6, 8],
    [0, 1, 4, 5],
]


@dataclass
class _SearchState:
    rows: list[int]
    column_counts: list[int]
    column_pair_counts: list[int]
    nodes_visited: int = 0
    row_options_considered: int = 0
    full_patterns_checked: int = 0
    hit_node_limit: bool = False
    hit_full_pattern_limit: bool = False


def mask_from_values(values: Sequence[int]) -> int:
    """Return a bit mask for labels in ``values``."""
    mask = 0
    for value in values:
        mask |= 1 << value
    return mask


def mask_bits(mask: int, n: int = N) -> list[int]:
    """Return sorted labels present in ``mask``."""
    return [idx for idx in range(n) if (mask >> idx) & 1]


def row_masks_to_pattern(rows: Sequence[int], n: int = N) -> list[list[int]]:
    """Convert row masks to sorted selected-witness rows."""
    return [mask_bits(mask, n=n) for mask in rows]


def validate_order(order: Sequence[int], n: int = N) -> list[int]:
    """Return ``order`` as a list after checking it is a full permutation."""
    order = list(order)
    expected = set(range(n))
    seen = set(order)
    if len(order) != n or seen != expected:
        missing = sorted(expected - seen)
        extra = sorted(seen - expected)
        raise ValueError(
            f"cyclic order is not a permutation of 0..{n - 1}; "
            f"missing={missing}, extra={extra}"
        )
    return order


def validate_selected_pattern(S: Pattern, n: int = N) -> None:
    """Validate an n=9 row-size-four selected-witness pattern."""
    if len(S) != n:
        raise ValueError(f"expected {n} rows, got {len(S)}")
    for center, row in enumerate(S):
        if len(row) != ROW_SIZE:
            raise ValueError(f"row {center} should have {ROW_SIZE} witnesses")
        if len(set(row)) != ROW_SIZE:
            raise ValueError(f"row {center} repeats a witness")
        if any(target < 0 or target >= n for target in row):
            raise ValueError(f"row {center} contains an out-of-range witness")
        if center in row:
            raise ValueError(f"row {center} contains its center")


def _chords(n: int = N) -> tuple[Chord, ...]:
    return tuple((a, b) for a in range(n) for b in range(a + 1, n))


CHORDS = _chords()
CHORD_INDEX = {chord: index for index, chord in enumerate(CHORDS)}


def row_options(
    center: int,
    row0_witnesses: Sequence[int] = DEFAULT_ROW0_WITNESSES,
    preferred_row: Sequence[int] | None = None,
) -> list[int]:
    """Return deterministic row masks for one center."""
    if center == 0:
        return [mask_from_values(row0_witnesses)]
    targets = [target for target in range(N) if target != center]
    options = [mask_from_values(combo) for combo in combinations(targets, ROW_SIZE)]
    if preferred_row is not None:
        preferred = mask_from_values(preferred_row)
        if preferred in options:
            options.remove(preferred)
            options.insert(0, preferred)
    return options


def _all_row_options(
    row0_witnesses: Sequence[int] = DEFAULT_ROW0_WITNESSES,
    preferred_pattern: Pattern | None = None,
) -> list[list[int]]:
    return [
        row_options(
            center,
            row0_witnesses,
            None if preferred_pattern is None else preferred_pattern[center],
        )
        for center in range(N)
    ]


def _json_chord(chord: Chord) -> list[int]:
    return [int(chord[0]), int(chord[1])]


def _json_pattern_from_masks(rows: Sequence[int]) -> list[list[int]]:
    return row_masks_to_pattern(rows, n=N)


def _pair_indices(row: Sequence[int]) -> list[int]:
    return [CHORD_INDEX[normalize_chord(a, b)] for a, b in combinations(row, 2)]


def _column_pair_violations(S: Pattern) -> list[dict[str, object]]:
    counts: Counter[Chord] = Counter()
    sources: dict[Chord, list[int]] = {}
    for center, row in enumerate(S):
        for pair in combinations(sorted(row), 2):
            chord = normalize_chord(*pair)
            counts[chord] += 1
            sources.setdefault(chord, []).append(center)
    return [
        {
            "witness_pair": _json_chord(pair),
            "source_rows": sources[pair],
            "count": counts[pair],
        }
        for pair in sorted(counts)
        if counts[pair] > PAIR_CAP
    ]


def _row_pair_cap_violations(S: Pattern) -> list[dict[str, object]]:
    witness_sets = [set(row) for row in S]
    out = []
    for i, j in combinations(range(len(S)), 2):
        common = sorted(witness_sets[i] & witness_sets[j])
        if len(common) > PAIR_CAP:
            out.append(
                {
                    "source_pair": [i, j],
                    "common_witnesses": common,
                    "count": len(common),
                }
            )
    return out


def _indegree_violations(S: Pattern) -> list[dict[str, object]]:
    counts = [0] * len(S)
    for row in S:
        for target in row:
            counts[target] += 1
    return [
        {"target": target, "count": count, "upper_bound": MAX_INDEGREE}
        for target, count in enumerate(counts)
        if count > MAX_INDEGREE
    ]


def classify_pattern(
    S: Pattern,
    order: Sequence[int] | None = None,
    max_details: int = 3,
) -> dict[str, object]:
    """Classify a fixed n=9 pattern by the current exact necessary filters."""
    validate_selected_pattern(S, n=N)
    if order is None:
        order = DEFAULT_ORDER
    order = validate_order(order, n=N)

    row_pair_violations = _row_pair_cap_violations(S)
    adjacent_violations = adjacent_two_overlap_violations_json(S, order)
    crossing_violations = crossing_bisector_violations(S, order)
    indegree_violations = _indegree_violations(S)
    column_pair_violations = _column_pair_violations(S)
    odd_cycle = odd_forced_perpendicular_cycle(S)
    matrix = mutual_midpoint_matrix(S)
    forced_classes = forced_equal_classes_from_matrix(matrix, N)
    rectangle_traps = phi4_rectangle_trap_certificates(S, order)
    phis = phi_map(S)
    directed_phi4 = phi_directed_4_cycles(S)

    status = "accepted_frontier"
    if row_pair_violations:
        status = "row_pair_intersection_cap"
    elif adjacent_violations:
        status = "adjacent_two_overlap"
    elif crossing_violations:
        status = "crossing_bisector"
    elif indegree_violations:
        status = "column_indegree_upper"
    elif column_pair_violations:
        status = "column_pair_cap"
    elif odd_cycle is not None:
        status = "odd_forced_perpendicular_cycle"
    elif forced_classes:
        status = "mutual_midpoint_collapse"
    elif rectangle_traps:
        status = "phi4_rectangle_trap"

    return {
        "status": status,
        "n": N,
        "row_size": ROW_SIZE,
        "order": order,
        "rows": [list(row) for row in S],
        "indegrees": [
            sum(1 for row in S if target in row) for target in range(N)
        ],
        "phi_edges": len(phis),
        "directed_phi_4_cycle_count": len(directed_phi4),
        "rectangle_trap_4_cycles": len(rectangle_traps),
        "midpoint_matrix_rank": int(matrix.rank()),
        "row_pair_intersection_cap_violations": row_pair_violations[:max_details],
        "adjacent_two_overlap_violations": adjacent_violations[:max_details],
        "crossing_bisector_violations": [
            [_json_chord(source), _json_chord(target)]
            for source, target in crossing_violations[:max_details]
        ],
        "column_indegree_upper_violations": indegree_violations[:max_details],
        "column_pair_cap_violations": column_pair_violations[:max_details],
        "odd_forced_perpendicular_cycle": (
            None
            if odd_cycle is None
            else [_json_chord(chord) for chord in odd_cycle]
        ),
        "forced_equality_classes": forced_classes[:max_details],
        "rectangle_trap_certificates": rectangle_traps[:max_details],
    }


def adjacent_two_overlap_violations_json(
    S: Pattern,
    order: Sequence[int],
) -> list[dict[str, object]]:
    """Return JSON-ready adjacent source-pair two-overlap violations."""
    edges = adjacent_pairs(order)
    phis = phi_map(S)
    return [
        {"source_pair": _json_chord(source), "witness_pair": _json_chord(phis[source])}
        for source in sorted(edges)
        if source in phis
    ]


def _record_example(
    examples: dict[str, list[dict[str, object]]],
    key: str,
    item: dict[str, object],
    max_examples: int,
) -> None:
    bucket = examples.setdefault(key, [])
    if len(bucket) < max_examples:
        bucket.append(item)


def _partial_rejection(
    state: _SearchState,
    center: int,
    mask: int,
    order: Sequence[int],
    edge_set: set[Chord],
) -> tuple[str, dict[str, object]] | None:
    row = mask_bits(mask)
    for previous_center, previous_mask in enumerate(state.rows):
        common_mask = mask & previous_mask
        common_count = common_mask.bit_count()
        source = normalize_chord(previous_center, center)
        if common_count > PAIR_CAP:
            return (
                "row_pair_intersection_cap",
                {
                    "center": center,
                    "row": row,
                    "source_pair": _json_chord(source),
                    "common_witnesses": mask_bits(common_mask),
                },
            )
        if common_count == PAIR_CAP:
            target = normalize_chord(*mask_bits(common_mask))
            if source in edge_set:
                return (
                    "adjacent_two_overlap",
                    {
                        "center": center,
                        "row": row,
                        "source_pair": _json_chord(source),
                        "witness_pair": _json_chord(target),
                    },
                )
            if not _chords_cross(source, target, order):
                return (
                    "crossing_bisector",
                    {
                        "center": center,
                        "row": row,
                        "source_pair": _json_chord(source),
                        "witness_pair": _json_chord(target),
                    },
                )

    for target in row:
        if state.column_counts[target] >= MAX_INDEGREE:
            return (
                "column_indegree_upper",
                {
                    "center": center,
                    "row": row,
                    "target": target,
                    "current_count": state.column_counts[target],
                    "upper_bound": MAX_INDEGREE,
                },
            )

    for pair_idx in _pair_indices(row):
        if state.column_pair_counts[pair_idx] >= PAIR_CAP:
            return (
                "column_pair_cap",
                {
                    "center": center,
                    "row": row,
                    "witness_pair": _json_chord(CHORDS[pair_idx]),
                    "current_count": state.column_pair_counts[pair_idx],
                    "upper_bound": PAIR_CAP,
                },
            )
    return None


def _chords_cross(source: Chord, target: Chord, order: Sequence[int]) -> bool:
    from erdos97.incidence_filters import chords_cross_in_order

    return chords_cross_in_order(source, target, order)


def run_bounded_scan(
    max_nodes: int = 250_000,
    max_full_patterns: int = 250,
    max_examples: int = 3,
    order: Sequence[int] | None = None,
    row0_witnesses: Sequence[int] = DEFAULT_ROW0_WITNESSES,
    preferred_pattern: Pattern | None = N9_RECTANGLE_TRAP_PATTERN,
) -> dict[str, object]:
    """Run a bounded row0-fixed n=9 incidence search and return a JSON payload."""
    if max_nodes <= 0:
        raise ValueError("max_nodes must be positive")
    if max_full_patterns <= 0:
        raise ValueError("max_full_patterns must be positive")
    if max_examples < 0:
        raise ValueError("max_examples must be nonnegative")
    if order is None:
        order = DEFAULT_ORDER
    order = validate_order(order, n=N)
    if (
        len(row0_witnesses) != ROW_SIZE
        or len(set(row0_witnesses)) != ROW_SIZE
        or 0 in row0_witnesses
        or any(target < 0 or target >= N for target in row0_witnesses)
    ):
        raise ValueError("row0_witnesses must contain four distinct labels from 1..8")

    if preferred_pattern is not None:
        validate_selected_pattern(preferred_pattern, n=N)

    options = _all_row_options(row0_witnesses, preferred_pattern)
    edge_set = adjacent_pairs(order)
    state = _SearchState(
        rows=[],
        column_counts=[0] * N,
        column_pair_counts=[0] * len(CHORDS),
    )
    partial_counts: Counter[str] = Counter({reason: 0 for reason in PARTIAL_REJECTION_REASONS})
    full_counts: Counter[str] = Counter({status: 0 for status in FULL_CLASSIFICATION_STATUSES})
    examples: dict[str, list[dict[str, object]]] = {
        reason: [] for reason in (*PARTIAL_REJECTION_REASONS, *FULL_CLASSIFICATION_STATUSES)
    }

    def add_row(mask: int) -> tuple[list[int], list[int]]:
        row = mask_bits(mask)
        pair_indices = _pair_indices(row)
        for target in row:
            state.column_counts[target] += 1
        for pair_idx in pair_indices:
            state.column_pair_counts[pair_idx] += 1
        state.rows.append(mask)
        return row, pair_indices

    def remove_row(row: Sequence[int], pair_indices: Sequence[int]) -> None:
        state.rows.pop()
        for pair_idx in pair_indices:
            state.column_pair_counts[pair_idx] -= 1
        for target in row:
            state.column_counts[target] -= 1

    def search(center: int) -> None:
        if state.hit_node_limit or state.hit_full_pattern_limit:
            return
        state.nodes_visited += 1
        if state.nodes_visited > max_nodes:
            state.hit_node_limit = True
            return
        if center == N:
            state.full_patterns_checked += 1
            S = row_masks_to_pattern(state.rows)
            classification = classify_pattern(S, order=order, max_details=max_examples)
            status = str(classification["status"])
            full_counts[status] += 1
            _record_example(examples, status, classification, max_examples)
            if state.full_patterns_checked >= max_full_patterns:
                state.hit_full_pattern_limit = True
            return

        for mask in options[center]:
            if state.hit_node_limit or state.hit_full_pattern_limit:
                return
            state.row_options_considered += 1
            rejection = _partial_rejection(state, center, mask, order, edge_set)
            if rejection is not None:
                reason, detail = rejection
                partial_counts[reason] += 1
                detail["prefix_rows"] = _json_pattern_from_masks(state.rows)
                _record_example(examples, reason, detail, max_examples)
                continue
            row, pair_indices = add_row(mask)
            search(center + 1)
            remove_row(row, pair_indices)

    search(0)
    seeded_case = classify_pattern(N9_RECTANGLE_TRAP_PATTERN, order=order)

    partial_counts_json = {
        reason: int(partial_counts[reason]) for reason in PARTIAL_REJECTION_REASONS
    }
    full_counts_json = {
        status: int(full_counts[status]) for status in FULL_CLASSIFICATION_STATUSES
    }
    truncated = state.hit_node_limit or state.hit_full_pattern_limit
    return {
        "type": "n9_incidence_frontier_bounded_scan_v1",
        "trust": "BOUNDED_INCIDENCE_CSP_DIAGNOSTIC",
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "The row0-fixed search is bounded by explicit node and full-pattern limits.",
            "An accepted_frontier item only means the listed necessary filters did not obstruct it.",
        ],
        "n": N,
        "row_size": ROW_SIZE,
        "cyclic_order": order,
        "symmetry_break": {
            "row": 0,
            "witnesses": list(row0_witnesses),
            "scope": "row0-fixed natural-order diagnostic search",
            "preferred_pattern": (
                None
                if preferred_pattern is None
                else "N9_phi4_rectangle_trap_selected_witness_pattern"
            ),
            "order_note": (
                "The natural cyclic order is held fixed. This is a bounded "
                "seed-prioritized scan, not a lossless quotient of all fixed-order "
                "n=9 selected-witness systems."
            ),
        },
        "limits": {
            "max_nodes": max_nodes,
            "max_full_patterns": max_full_patterns,
            "max_examples_per_bucket": max_examples,
        },
        "search_complete": not truncated,
        "truncated": truncated,
        "hit_node_limit": state.hit_node_limit,
        "hit_full_pattern_limit": state.hit_full_pattern_limit,
        "nodes_visited": state.nodes_visited,
        "row_options_considered": state.row_options_considered,
        "full_patterns_checked": state.full_patterns_checked,
        "partial_rejection_counts": partial_counts_json,
        "full_classification_counts": full_counts_json,
        "accepted_frontier_count": full_counts_json["accepted_frontier"],
        "examples": {
            key: value for key, value in examples.items() if value
        },
        "seeded_cases": [
            {
                "case": "N9_phi4_rectangle_trap_selected_witness_pattern",
                "source": "data/certificates/n9_phi4_rectangle_trap.json",
                "classification": seeded_case,
            }
        ],
        "filter_order": [
            *PARTIAL_REJECTION_REASONS,
            "odd_forced_perpendicular_cycle",
            "mutual_midpoint_collapse",
            "phi4_rectangle_trap",
            "accepted_frontier",
        ],
    }
