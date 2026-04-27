"""Exact cyclic-order CSP for crossing-bisection constraints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from erdos97.incidence_filters import Chord, chords_cross_in_order, phi_map

Constraint = tuple[Chord, Chord]


@dataclass(frozen=True)
class CyclicCrossingResult:
    pattern: str
    n: int
    constraints: list[Constraint]
    symmetry_normalization: list[list[int]]
    sat: bool
    order: list[int] | None
    nodes_visited: int
    max_depth: int
    terminal_conflicts: list[dict[str, object]]


def crossing_constraints(S: Sequence[Sequence[int]]) -> list[Constraint]:
    """Return all phi crossing constraints source -> target."""
    return sorted(phi_map(S).items())


def all_constraints_cross(order: Sequence[int], constraints: Sequence[Constraint]) -> bool:
    """Return True iff every source chord crosses its target in order."""
    return all(chords_cross_in_order(source, target, order) for source, target in constraints)


def _constraint_labels(constraint: Constraint) -> set[int]:
    return set(constraint[0]) | set(constraint[1])


def _json_chord(chord: Chord) -> list[int]:
    return [int(chord[0]), int(chord[1])]


def _json_constraint(constraint: Constraint) -> dict[str, list[int]]:
    return {
        "source": _json_chord(constraint[0]),
        "target": _json_chord(constraint[1]),
    }


def _initial_orders(constraints: Sequence[Constraint], n: int) -> list[list[int]]:
    if not constraints:
        return [[0]] if n else [[]]
    source, target = constraints[0]
    return [
        [source[0], target[0], source[1], target[1]],
        [source[0], target[1], source[1], target[0]],
    ]


def find_cyclic_crossing_order(
    S: Sequence[Sequence[int]],
    pattern: str = "",
) -> CyclicCrossingResult:
    """
    Search for a cyclic order satisfying all crossing-bisection constraints.

    The search fixes the first crossing constraint up to rotation/reversal and
    then inserts one unplaced label at a time into circular gaps. It is exact
    finite combinatorics: a branch is rejected only when a completed crossing
    constraint fails.
    """
    n = len(S)
    constraints = crossing_constraints(S)
    labels = set(range(n))
    constraint_label_sets = [_constraint_labels(constraint) for constraint in constraints]
    label_to_constraints: dict[int, list[int]] = {label: [] for label in labels}
    for idx, constraint_labels in enumerate(constraint_label_sets):
        for label in constraint_labels:
            label_to_constraints[label].append(idx)

    nodes_visited = 0
    max_depth = 0
    terminal_conflicts: list[dict[str, object]] = []

    def completed_failure(
        order: Sequence[int],
        placed: set[int],
        affected_labels: set[int] | None = None,
    ) -> int | None:
        if affected_labels is None:
            candidate_idxs = range(len(constraints))
        else:
            idxs: set[int] = set()
            for label in affected_labels:
                idxs.update(label_to_constraints[label])
            candidate_idxs = sorted(idxs)
        for idx in candidate_idxs:
            if constraint_label_sets[idx] <= placed:
                source, target = constraints[idx]
                if not chords_cross_in_order(source, target, order):
                    return idx
        return None

    def choose_label(placed: set[int]) -> int:
        def score(label: int) -> tuple[int, int, int, int, int]:
            touches = [
                len(constraint_label_sets[idx] & placed)
                for idx in label_to_constraints[label]
            ]
            return (
                sum(count == 3 for count in touches),
                sum(count == 2 for count in touches),
                sum(count == 1 for count in touches),
                len(label_to_constraints[label]),
                -label,
            )

        return max(labels - placed, key=score)

    def search(order: list[int], placed: set[int]) -> list[int] | None:
        nonlocal nodes_visited, max_depth
        nodes_visited += 1
        max_depth = max(max_depth, len(placed))
        if len(placed) == n:
            return order if completed_failure(order, placed) is None else None

        label = choose_label(placed)
        gap_conflicts: list[dict[str, object]] = []
        tried_valid_child = False
        for position in range(1, len(order) + 1):
            candidate_order = order[:position] + [label] + order[position:]
            candidate_placed = placed | {label}
            failed_idx = completed_failure(candidate_order, candidate_placed, {label})
            if failed_idx is not None:
                gap_conflicts.append(
                    {
                        "insert_position": position,
                        "gap_after": int(candidate_order[position - 1]),
                        "constraint": _json_constraint(constraints[failed_idx]),
                    }
                )
                continue
            tried_valid_child = True
            found = search(candidate_order, candidate_placed)
            if found is not None:
                return found

        if not tried_valid_child:
            terminal_conflicts.append(
                {
                    "partial_order": [int(label) for label in order],
                    "blocked_label": int(label),
                    "reasons": gap_conflicts,
                }
            )
        return None

    normalizations = _initial_orders(constraints, n)
    for initial_order in normalizations:
        found = search(initial_order, set(initial_order))
        if found is not None:
            return CyclicCrossingResult(
                pattern=pattern,
                n=n,
                constraints=constraints,
                symmetry_normalization=normalizations,
                sat=True,
                order=found,
                nodes_visited=nodes_visited,
                max_depth=max_depth,
                terminal_conflicts=[],
            )

    return CyclicCrossingResult(
        pattern=pattern,
        n=n,
        constraints=constraints,
        symmetry_normalization=normalizations,
        sat=False,
        order=None,
        nodes_visited=nodes_visited,
        max_depth=max_depth,
        terminal_conflicts=terminal_conflicts,
    )


def result_to_json(result: CyclicCrossingResult) -> dict[str, object]:
    """Return a JSON-serializable form of a CSP result."""
    return {
        "pattern": result.pattern,
        "n": result.n,
        "constraints": [_json_constraint(constraint) for constraint in result.constraints],
        "constraint_count": len(result.constraints),
        "symmetry_normalization": result.symmetry_normalization,
        "result": "SAT" if result.sat else "UNSAT",
        "sat": result.sat,
        "order": result.order,
        "nodes_visited": result.nodes_visited,
        "max_depth": result.max_depth,
        "terminal_conflicts": result.terminal_conflicts,
    }
