"""Fixed-selection stuck-set analysis for the bridge/peeling program.

The checks here are combinatorial.  They analyze a chosen selected-witness
system ``S_i`` and do not claim geometric realizability, a general proof, or a
counterexample to Erdos Problem #97.

Two notions are intentionally kept separate:

* a forward ear order from a three-vertex seed, where each added vertex has
  three selected witnesses already present;
* the stronger fixed-row Key Peeling property, whose obstruction is a subset
  ``U`` with no vertex of ``U`` seeing three selected witnesses inside ``U``.

The second notion is the stuck-set miner's target.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Sequence

from erdos97.fragile_hypergraph import (
    check_fragile_hypergraph,
    check_to_json,
    covering_subsets,
)
from erdos97.incidence_filters import (
    adjacent_two_overlap_violations,
    crossing_bisector_violations,
    odd_forced_perpendicular_cycle,
    phi4_rectangle_trap_certificates,
    phi_map,
)
from erdos97.min_radius_filter import (
    consecutive_witness_pairs,
    minimum_radius_order_obstruction,
    selected_pair_sources,
)
from erdos97.motif_fingerprint import pattern_profile

Pattern = Sequence[Sequence[int]]


@dataclass(frozen=True)
class StuckRow:
    center: int
    internal_witnesses: list[int]
    outside_witnesses: list[int]
    internal_count: int


@dataclass(frozen=True)
class StuckSet:
    vertices: list[int]
    rows: list[StuckRow]


@dataclass(frozen=True)
class StuckSearchResult:
    n: int
    threshold: int
    searched_from_size: int
    searched_up_to_size: int
    search_complete: bool
    minimal_size: int | None
    total_at_minimal_size: int
    examples: list[StuckSet]

    @property
    def found(self) -> bool:
        return self.minimal_size is not None

    @property
    def key_peeling_ok(self) -> bool | None:
        if self.found:
            return False
        if self.search_complete and self.searched_from_size <= self.threshold + 1:
            return True
        return None


@dataclass(frozen=True)
class ForwardEarOrderResult:
    exists: bool
    seed: list[int] | None
    order: list[int] | None
    largest_closure_size: int
    largest_closure_seed: list[int] | None
    largest_closure: list[int]


@dataclass(frozen=True)
class GreedyPeelingResult:
    """One deterministic reverse-peeling run from the full vertex set."""

    success: bool
    removed_order: list[int]
    terminal_vertices: list[int]
    terminal_stuck_set: StuckSet | None


@dataclass(frozen=True)
class RadiusChoice:
    center: int
    consecutive_pair: tuple[int, int]
    smaller_centers: list[int]


@dataclass(frozen=True)
class RadiusPropagationResult:
    n: int
    order: list[int]
    status: str
    obstructed: bool | None
    explored_nodes: int
    node_limit: int
    acyclic_choice: list[RadiusChoice] | None
    choices_by_center: list[list[RadiusChoice]]


@dataclass(frozen=True)
class RadiusChoiceOptimizationResult:
    n: int
    order: list[int]
    objective: str
    status: str
    obstructed: bool | None
    optimality_certified: bool
    edge_count: int | None
    edge_lower_bound: int
    edge_upper_bound: int
    explored_nodes: int
    node_limit: int
    acyclic_choice: list[RadiusChoice] | None
    choices_by_center: list[list[RadiusChoice]]


def validate_selected_pattern(S: Pattern) -> None:
    """Validate the fixed selected-witness contract."""

    n = len(S)
    if n < 4:
        raise ValueError(f"pattern must have at least four rows, got {n}")
    for center, row in enumerate(S):
        if len(row) != 4:
            raise ValueError(f"row {center} has length {len(row)}, expected 4")
        if len(set(row)) != 4:
            raise ValueError(f"row {center} has repeated witnesses: {list(row)}")
        if center in row:
            raise ValueError(f"row {center} contains its own center")
        for label in row:
            if label < 0 or label >= n:
                raise ValueError(f"row {center} contains out-of-range label {label}")


def rows_to_masks(S: Pattern) -> list[int]:
    """Return one bit mask of selected witnesses per row."""

    validate_selected_pattern(S)
    masks: list[int] = []
    for row in S:
        mask = 0
        for label in row:
            mask |= 1 << int(label)
        masks.append(mask)
    return masks


def mask_from_vertices(vertices: Iterable[int]) -> int:
    mask = 0
    for vertex in vertices:
        mask |= 1 << int(vertex)
    return mask


def vertices_from_mask(mask: int, n: int) -> list[int]:
    return [vertex for vertex in range(n) if mask & (1 << vertex)]


def internal_witness_count(S: Pattern, subset: Iterable[int], center: int) -> int:
    """Return ``|S_center cap subset|`` for a fixed selected row."""

    masks = rows_to_masks(S)
    return (masks[center] & mask_from_vertices(subset)).bit_count()


def peelable_vertices(S: Pattern, subset: Iterable[int], threshold: int = 3) -> list[int]:
    """Return vertices in ``subset`` with at least ``threshold`` internal witnesses."""

    if threshold < 0:
        raise ValueError("threshold must be nonnegative")
    masks = rows_to_masks(S)
    subset_mask = mask_from_vertices(subset)
    n = len(S)
    return [
        vertex
        for vertex in range(n)
        if subset_mask & (1 << vertex)
        and (masks[vertex] & subset_mask).bit_count() >= threshold
    ]


def is_stuck_subset(S: Pattern, subset: Iterable[int], threshold: int = 3) -> bool:
    """Return True iff ``subset`` is a fixed-row stuck set."""

    subset_vertices = list(subset)
    if len(subset_vertices) < threshold + 1:
        return False
    return not peelable_vertices(S, subset_vertices, threshold=threshold)


def describe_stuck_set(S: Pattern, subset: Iterable[int]) -> StuckSet:
    """Return row-level diagnostics for a stuck subset."""

    validate_selected_pattern(S)
    subset_vertices = sorted(int(v) for v in subset)
    subset_mask = mask_from_vertices(subset_vertices)
    rows: list[StuckRow] = []
    for center in subset_vertices:
        internal = sorted(label for label in S[center] if subset_mask & (1 << label))
        outside = sorted(label for label in S[center] if not subset_mask & (1 << label))
        rows.append(
            StuckRow(
                center=int(center),
                internal_witnesses=[int(label) for label in internal],
                outside_witnesses=[int(label) for label in outside],
                internal_count=len(internal),
            )
        )
    return StuckSet(vertices=subset_vertices, rows=rows)


def find_minimal_stuck_sets(
    S: Pattern,
    min_size: int | None = None,
    max_size: int | None = None,
    max_examples: int = 8,
    threshold: int = 3,
) -> StuckSearchResult:
    """Find cardinality-minimal fixed-row stuck sets.

    The search is exhaustive through ``max_size``.  If ``max_size`` is at least
    ``n``, a no-stuck result certifies the fixed-row Key Peeling property for
    this selected-witness system.
    """

    validate_selected_pattern(S)
    if max_examples < 0:
        raise ValueError("max_examples must be nonnegative")
    if threshold <= 0:
        raise ValueError("threshold must be positive")

    n = len(S)
    if min_size is None:
        min_size = threshold + 1
    if max_size is None:
        max_size = n
    min_size = max(min_size, threshold + 1)
    max_size = min(max_size, n)
    if max_size < min_size:
        raise ValueError(f"max_size must be at least min_size={min_size}, got {max_size}")

    masks = rows_to_masks(S)
    all_vertices = range(n)
    for size in range(min_size, max_size + 1):
        examples: list[StuckSet] = []
        total = 0
        for subset in combinations(all_vertices, size):
            subset_mask = mask_from_vertices(subset)
            if all((masks[center] & subset_mask).bit_count() < threshold for center in subset):
                total += 1
                if len(examples) < max_examples:
                    examples.append(describe_stuck_set(S, subset))
        if total:
            return StuckSearchResult(
                n=n,
                threshold=threshold,
                searched_from_size=min_size,
                searched_up_to_size=size,
                search_complete=size == n,
                minimal_size=size,
                total_at_minimal_size=total,
                examples=examples,
            )

    return StuckSearchResult(
        n=n,
        threshold=threshold,
        searched_from_size=min_size,
        searched_up_to_size=max_size,
        search_complete=max_size == n,
        minimal_size=None,
        total_at_minimal_size=0,
        examples=[],
    )


def forward_ear_order(S: Pattern, threshold: int = 3) -> ForwardEarOrderResult:
    """Search for a forward ear order from a three-vertex seed."""

    validate_selected_pattern(S)
    n = len(S)
    masks = rows_to_masks(S)
    best_seed: tuple[int, ...] | None = None
    best_closure_mask = 0

    for seed in combinations(range(n), threshold):
        closure_mask = mask_from_vertices(seed)
        order = list(seed)
        changed = True
        while changed:
            changed = False
            for vertex in range(n):
                if closure_mask & (1 << vertex):
                    continue
                if (masks[vertex] & closure_mask).bit_count() >= threshold:
                    closure_mask |= 1 << vertex
                    order.append(vertex)
                    changed = True
        if closure_mask.bit_count() > best_closure_mask.bit_count():
            best_seed = seed
            best_closure_mask = closure_mask
        if closure_mask.bit_count() == n:
            return ForwardEarOrderResult(
                exists=True,
                seed=list(seed),
                order=order,
                largest_closure_size=n,
                largest_closure_seed=list(seed),
                largest_closure=vertices_from_mask(closure_mask, n),
            )

    return ForwardEarOrderResult(
        exists=False,
        seed=None,
        order=None,
        largest_closure_size=best_closure_mask.bit_count(),
        largest_closure_seed=list(best_seed) if best_seed is not None else None,
        largest_closure=vertices_from_mask(best_closure_mask, n),
    )


def greedy_peeling_run(S: Pattern, threshold: int = 3) -> GreedyPeelingResult:
    """Run a deterministic reverse-peeling pass from the full set.

    At each step, remove a currently peelable vertex with largest internal
    selected-witness count, breaking ties by smallest label.  The result is a
    diagnostic motif, not a completeness proof over all possible peel orders.
    """

    validate_selected_pattern(S)
    n = len(S)
    masks = rows_to_masks(S)
    remaining_mask = (1 << n) - 1
    removed: list[int] = []

    while remaining_mask.bit_count() > threshold:
        candidates: list[tuple[int, int]] = []
        for vertex in range(n):
            if remaining_mask & (1 << vertex):
                internal_count = (masks[vertex] & remaining_mask).bit_count()
                if internal_count >= threshold:
                    candidates.append((vertex, internal_count))
        if not candidates:
            break
        vertex, _ = min(candidates, key=lambda item: (-item[1], item[0]))
        remaining_mask &= ~(1 << vertex)
        removed.append(vertex)

    terminal = vertices_from_mask(remaining_mask, n)
    success = len(terminal) <= threshold
    return GreedyPeelingResult(
        success=success,
        removed_order=removed,
        terminal_vertices=terminal,
        terminal_stuck_set=None if success else describe_stuck_set(S, terminal),
    )


def short_chord_radius_choices(
    S: Pattern,
    order: Sequence[int] | None = None,
) -> list[list[RadiusChoice]]:
    """Return all possible short-chord inequality choices for each row.

    If the consecutive witness pair ``{a,b}`` is the short pair for center
    ``i`` and one endpoint selects the other, then that endpoint's selected
    radius is strictly smaller than ``r_i``.
    """

    validate_selected_pattern(S)
    n = len(S)
    if order is None:
        order = list(range(n))
    choices_by_center: list[list[RadiusChoice]] = []
    for center in range(n):
        choices: list[RadiusChoice] = []
        for pair in consecutive_witness_pairs(order, center, S[center]):
            sources = selected_pair_sources(S, *pair)
            choices.append(
                RadiusChoice(
                    center=center,
                    consecutive_pair=pair,
                    smaller_centers=[int(source) for source in sources],
                )
            )
        choices_by_center.append(choices)
    return choices_by_center


def _reaches(adjacency: list[set[int]], start: int, target: int) -> bool:
    if start == target:
        return True
    seen = {start}
    stack = [start]
    while stack:
        cur = stack.pop()
        for nxt in adjacency[cur]:
            if nxt == target:
                return True
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return False


def _choice_json(choice: RadiusChoice) -> dict[str, object]:
    return {
        "center": choice.center,
        "consecutive_pair": [choice.consecutive_pair[0], choice.consecutive_pair[1]],
        "smaller_centers": choice.smaller_centers,
    }


def radius_propagation_obstruction(
    S: Pattern,
    order: Sequence[int] | None = None,
    node_limit: int = 100_000,
) -> RadiusPropagationResult:
    """Search for an acyclic assignment of short-chord radius inequalities.

    A strict directed cycle among selected radii is impossible.  The filter is
    obstructed only if every possible choice of one short consecutive pair per
    row forces such a cycle.  If an acyclic choice is found, the pattern merely
    passes this necessary filter.
    """

    validate_selected_pattern(S)
    if node_limit <= 0:
        raise ValueError("node_limit must be positive")

    n = len(S)
    if order is None:
        order = list(range(n))
    order = list(order)
    choices_by_center = short_chord_radius_choices(S, order=order)
    row_order = sorted(
        range(n),
        key=lambda center: (
            min(len(choice.smaller_centers) for choice in choices_by_center[center]),
            len(choices_by_center[center]),
            center,
        ),
    )
    sorted_choices = {
        center: sorted(
            choices_by_center[center],
            key=lambda choice: (len(choice.smaller_centers), choice.consecutive_pair),
        )
        for center in range(n)
    }

    adjacency: list[set[int]] = [set() for _ in range(n)]
    selected: list[RadiusChoice] = []
    explored = 0
    hit_limit = False

    def search(depth: int) -> bool:
        nonlocal explored, hit_limit
        explored += 1
        if explored > node_limit:
            hit_limit = True
            return False
        if depth == len(row_order):
            return True

        center = row_order[depth]
        for choice in sorted_choices[center]:
            added: list[tuple[int, int]] = []
            creates_cycle = False
            for smaller in choice.smaller_centers:
                if smaller == center or _reaches(adjacency, smaller, center):
                    creates_cycle = True
                    break
                if smaller not in adjacency[center]:
                    adjacency[center].add(smaller)
                    added.append((center, smaller))
            if creates_cycle:
                for source, target in added:
                    adjacency[source].remove(target)
                continue
            selected.append(choice)
            if search(depth + 1):
                return True
            selected.pop()
            for source, target in added:
                adjacency[source].remove(target)
        return False

    found_acyclic = search(0)
    if found_acyclic:
        status = "PASS_ACYCLIC_CHOICE"
        obstructed: bool | None = False
        acyclic_choice: list[RadiusChoice] | None = list(selected)
    elif hit_limit:
        status = "UNKNOWN_NODE_LIMIT"
        obstructed = None
        acyclic_choice = None
    else:
        status = "RADIUS_CYCLE_OBSTRUCTED"
        obstructed = True
        acyclic_choice = None

    return RadiusPropagationResult(
        n=n,
        order=order,
        status=status,
        obstructed=obstructed,
        explored_nodes=explored,
        node_limit=node_limit,
        acyclic_choice=acyclic_choice,
        choices_by_center=choices_by_center,
    )


def radius_result_to_json(result: RadiusPropagationResult) -> dict[str, object]:
    """Return a JSON-serializable radius propagation result."""

    return {
        "type": "radius_propagation_short_chord_result",
        "n": result.n,
        "order": result.order,
        "status": result.status,
        "obstructed": result.obstructed,
        "explored_nodes": result.explored_nodes,
        "node_limit": result.node_limit,
        "acyclic_choice": (
            None
            if result.acyclic_choice is None
            else [_choice_json(choice) for choice in result.acyclic_choice]
        ),
        "choices_by_center": [
            [_choice_json(choice) for choice in choices]
            for choices in result.choices_by_center
        ],
        "interpretation": (
            "Exact fixed-order necessary filter. PASS means there exists a "
            "choice of short witness gaps whose implied strict radius "
            "inequalities are acyclic; it is not evidence of realizability."
        ),
    }


def optimize_radius_choice_edges(
    S: Pattern,
    order: Sequence[int] | None = None,
    objective: str = "min",
    node_limit: int = 100_000,
) -> RadiusChoiceOptimizationResult:
    """Optimize acyclic short-chord radius choices by edge count.

    The objective is over choices that pass the fixed-order radius-propagation
    necessary filter.  A certified optimum is still only a statement about this
    incidence/order filter, not about geometric realizability.
    """

    validate_selected_pattern(S)
    if objective not in {"min", "max"}:
        raise ValueError("objective must be 'min' or 'max'")
    if node_limit <= 0:
        raise ValueError("node_limit must be positive")

    n = len(S)
    if order is None:
        order = list(range(n))
    order = list(order)
    choices_by_center = short_chord_radius_choices(S, order=order)
    row_order = sorted(
        range(n),
        key=lambda center: (
            min(len(choice.smaller_centers) for choice in choices_by_center[center]),
            len(choices_by_center[center]),
            center,
        ),
    )
    if objective == "max":
        row_order = sorted(
            range(n),
            key=lambda center: (
                -max(
                    len(choice.smaller_centers)
                    for choice in choices_by_center[center]
                ),
                len(choices_by_center[center]),
                center,
            ),
        )

    def choice_sort_key(choice: RadiusChoice) -> tuple[int, tuple[int, int]]:
        edge_count = len(choice.smaller_centers)
        if objective == "min":
            return (edge_count, choice.consecutive_pair)
        return (-edge_count, choice.consecutive_pair)

    sorted_choices = {
        center: sorted(
            choices_by_center[center],
            key=choice_sort_key,
        )
        for center in range(n)
    }
    min_edges_by_center = [
        min(len(choice.smaller_centers) for choice in choices_by_center[center])
        for center in row_order
    ]
    max_edges_by_center = [
        max(len(choice.smaller_centers) for choice in choices_by_center[center])
        for center in row_order
    ]
    edge_lower_bound = sum(min_edges_by_center)
    edge_upper_bound = sum(max_edges_by_center)
    suffix_min = [0] * (len(row_order) + 1)
    suffix_max = [0] * (len(row_order) + 1)
    for idx in range(len(row_order) - 1, -1, -1):
        suffix_min[idx] = suffix_min[idx + 1] + min_edges_by_center[idx]
        suffix_max[idx] = suffix_max[idx + 1] + max_edges_by_center[idx]

    adjacency: list[set[int]] = [set() for _ in range(n)]
    selected: list[RadiusChoice] = []
    best_choice: list[RadiusChoice] | None = None
    best_edge_count: int | None = None
    explored = 0
    hit_limit = False
    optimality_certified = False

    def improves(edge_count: int) -> bool:
        if best_edge_count is None:
            return True
        if objective == "min":
            return edge_count < best_edge_count
        return edge_count > best_edge_count

    def best_possible(depth: int, edge_count: int) -> int:
        if objective == "min":
            return edge_count + suffix_min[depth]
        return edge_count + suffix_max[depth]

    def cannot_improve(depth: int, edge_count: int) -> bool:
        if best_edge_count is None:
            return False
        possible = best_possible(depth, edge_count)
        if objective == "min":
            return possible >= best_edge_count
        return possible <= best_edge_count

    def search(depth: int, edge_count: int) -> None:
        nonlocal best_choice, best_edge_count, explored, hit_limit, optimality_certified
        if optimality_certified:
            return
        explored += 1
        if explored > node_limit:
            hit_limit = True
            return
        if cannot_improve(depth, edge_count):
            return
        if depth == len(row_order):
            if improves(edge_count):
                best_edge_count = edge_count
                best_choice = list(selected)
                if (
                    (objective == "min" and edge_count == edge_lower_bound)
                    or (objective == "max" and edge_count == edge_upper_bound)
                ):
                    optimality_certified = True
            return

        center = row_order[depth]
        for choice in sorted_choices[center]:
            added: list[tuple[int, int]] = []
            creates_cycle = False
            for smaller in choice.smaller_centers:
                if smaller == center or _reaches(adjacency, smaller, center):
                    creates_cycle = True
                    break
                if smaller not in adjacency[center]:
                    adjacency[center].add(smaller)
                    added.append((center, smaller))
            if creates_cycle:
                for source, target in added:
                    adjacency[source].remove(target)
                continue
            selected.append(choice)
            search(depth + 1, edge_count + len(choice.smaller_centers))
            selected.pop()
            for source, target in added:
                adjacency[source].remove(target)
            if optimality_certified or hit_limit:
                break

    search(0, 0)
    if best_choice is not None:
        if optimality_certified or not hit_limit:
            status = "PASS_OPTIMAL_CHOICE"
            obstructed: bool | None = False
            optimality_certified = True
        else:
            status = "UNKNOWN_NODE_LIMIT"
            obstructed = None
    elif hit_limit:
        status = "UNKNOWN_NODE_LIMIT"
        obstructed = None
    else:
        status = "RADIUS_CYCLE_OBSTRUCTED"
        obstructed = True
        optimality_certified = True

    return RadiusChoiceOptimizationResult(
        n=n,
        order=order,
        objective=objective,
        status=status,
        obstructed=obstructed,
        optimality_certified=optimality_certified,
        edge_count=best_edge_count,
        edge_lower_bound=edge_lower_bound,
        edge_upper_bound=edge_upper_bound,
        explored_nodes=explored,
        node_limit=node_limit,
        acyclic_choice=best_choice,
        choices_by_center=choices_by_center,
    )


def radius_choice_optimization_to_json(
    result: RadiusChoiceOptimizationResult,
) -> dict[str, object]:
    """Return a JSON-serializable radius choice optimization result."""

    return {
        "type": "radius_choice_edge_optimization_result",
        "n": result.n,
        "order": result.order,
        "objective": result.objective,
        "status": result.status,
        "obstructed": result.obstructed,
        "optimality_certified": result.optimality_certified,
        "edge_count": result.edge_count,
        "edge_lower_bound": result.edge_lower_bound,
        "edge_upper_bound": result.edge_upper_bound,
        "explored_nodes": result.explored_nodes,
        "node_limit": result.node_limit,
        "acyclic_choice": (
            None
            if result.acyclic_choice is None
            else [_choice_json(choice) for choice in result.acyclic_choice]
        ),
        "choices_by_center": [
            [_choice_json(choice) for choice in choices]
            for choices in result.choices_by_center
        ],
        "interpretation": (
            "Exact fixed-order optimization over this radius-propagation "
            "necessary filter when optimality_certified is true. PASS is not "
            "evidence of geometric realizability."
        ),
    }


def fragile_cover_snapshot(
    S: Pattern,
    order: Sequence[int] | None = None,
    max_cover_size: int | None = None,
    max_examples: int = 8,
    exhaustive_n_limit: int = 20,
) -> dict[str, object]:
    """Return incidence-level fragile-cover compatibility diagnostics."""

    validate_selected_pattern(S)
    n = len(S)
    if order is None:
        order = list(range(n))
    rows = {center: list(row) for center, row in enumerate(S)}
    full_check = check_fragile_hypergraph(n, rows, order=order)

    if max_cover_size is None and n > exhaustive_n_limit:
        cover_stats: dict[str, object] = {
            "status": "SKIPPED_LARGE_N",
            "reason": (
                "exact subset-cover enumeration is skipped by default for "
                f"n>{exhaustive_n_limit}; pass a max cover size to search a window"
            ),
        }
    else:
        cover_stats = {
            "status": "SEARCHED",
            **covering_subsets(
                n,
                rows,
                max_examples=max_examples,
                max_size=max_cover_size,
            ),
        }

    return {
        "type": "fragile_cover_incidence_snapshot",
        "semantics": (
            "Incidence-level only, assuming any selected row may be declared "
            "fragile. This does not certify unique exact four-cohorts."
        ),
        "all_rows_fragile_hypergraph_check": check_to_json(full_check),
        "cover_stats": cover_stats,
    }


def column_pair_cap_violations(S: Pattern) -> list[dict[str, object]]:
    """Return witness-pair codegree violations of the at-most-two cap."""

    validate_selected_pattern(S)
    n = len(S)
    violations: list[dict[str, object]] = []
    for a, b in combinations(range(n), 2):
        centers = [center for center, row in enumerate(S) if a in row and b in row]
        if len(centers) > 2:
            violations.append({"pair": [a, b], "centers": centers, "count": len(centers)})
    return violations


def pattern_filter_snapshot(
    S: Pattern,
    order: Sequence[int] | None = None,
    radius_node_limit: int = 100_000,
    fragile_cover_max_size: int | None = None,
    fragile_cover_max_examples: int = 2,
) -> dict[str, object]:
    """Return cheap exact-filter diagnostics for the full fixed pattern."""

    validate_selected_pattern(S)
    n = len(S)
    if order is None:
        order = list(range(n))

    row_pair_violations: list[dict[str, object]] = []
    max_row_intersection = 0
    for left, right in combinations(range(n), 2):
        inter = sorted(set(S[left]) & set(S[right]))
        max_row_intersection = max(max_row_intersection, len(inter))
        if len(inter) > 2:
            row_pair_violations.append(
                {"centers": [left, right], "intersection": inter, "count": len(inter)}
            )

    column_violations = column_pair_cap_violations(S)
    odd_cycle = odd_forced_perpendicular_cycle(S)
    adjacent = adjacent_two_overlap_violations(S, order)
    crossing = crossing_bisector_violations(S, order)
    rectangle_traps = phi4_rectangle_trap_certificates(S, order)
    min_radius = minimum_radius_order_obstruction(S, order=order)
    radius = radius_propagation_obstruction(S, order=order, node_limit=radius_node_limit)
    covered = sorted({label for row in S for label in row})

    return {
        "row_size_ok": all(len(row) == 4 and len(set(row)) == 4 for row in S),
        "self_exclusion_ok": all(center not in row for center, row in enumerate(S)),
        "row_pair_cap_ok": not row_pair_violations,
        "max_row_intersection": max_row_intersection,
        "row_pair_cap_violations": row_pair_violations,
        "column_pair_cap_ok": not column_violations,
        "column_pair_cap_violations": column_violations,
        "phi_edges": len(phi_map(S)),
        "odd_forced_perpendicular_cycle_length": len(odd_cycle) if odd_cycle else None,
        "rectangle_trap_4_cycles": len(rectangle_traps),
        "rectangle_trap_certificates": rectangle_traps,
        "adjacent_two_overlap_violations": [
            [[int(a), int(b)] for a, b in pair] for pair in adjacent
        ],
        "crossing_bisector_violations": [
            [[int(a), int(b)] for a, b in pair] for pair in crossing
        ],
        "minimum_radius_obstructed_in_order": min_radius.obstructed,
        "minimum_radius_possible_centers": min_radius.possible_min_centers,
        "minimum_radius_order_free_blocked_centers": (
            min_radius.order_free_blocked_centers
        ),
        "minimum_radius_order_free_empty_gap_centers": (
            min_radius.order_free_empty_gap_centers
        ),
        "radius_propagation": radius_result_to_json(radius),
        "fragile_cover": fragile_cover_snapshot(
            S,
            order=order,
            max_cover_size=fragile_cover_max_size,
            max_examples=fragile_cover_max_examples,
        ),
        "all_rows_cover_vertices": covered == list(range(n)),
        "uncovered_by_all_rows": [vertex for vertex in range(n) if vertex not in covered],
    }


def _json_stuck_row(row: StuckRow) -> dict[str, object]:
    return {
        "center": row.center,
        "internal_witnesses": row.internal_witnesses,
        "outside_witnesses": row.outside_witnesses,
        "internal_count": row.internal_count,
    }


def _json_stuck_set(stuck_set: StuckSet) -> dict[str, object]:
    return {
        "vertices": stuck_set.vertices,
        "rows": [_json_stuck_row(row) for row in stuck_set.rows],
    }


def result_to_json(
    pattern_name: str,
    S: Pattern,
    stuck_result: StuckSearchResult,
    forward_result: ForwardEarOrderResult,
    greedy_result: GreedyPeelingResult | None = None,
    filters: dict[str, object] | None = None,
) -> dict[str, object]:
    """Return a JSON-serializable stuck-set analysis payload."""

    key_status: str
    if stuck_result.key_peeling_ok is True:
        key_status = "NO_STUCK_SETS"
    elif stuck_result.key_peeling_ok is False:
        key_status = "STUCK_SET_FOUND"
    else:
        key_status = "UNKNOWN_TRUNCATED_SEARCH"

    return {
        "type": "fixed_selection_stuck_set_analysis",
        "pattern": pattern_name,
        "n": stuck_result.n,
        "selected_rows": [[int(label) for label in row] for row in S],
        "fingerprint": pattern_profile(S),
        "semantics": (
            "Fixed selected-witness system only. Stuck sets obstruct the "
            "strong fixed-row Key Peeling property; they are not geometric "
            "realization certificates and do not settle Erdos Problem #97."
        ),
        "forward_ear_order": {
            "exists": forward_result.exists,
            "seed": forward_result.seed,
            "order": forward_result.order,
            "largest_closure_size": forward_result.largest_closure_size,
            "largest_closure_seed": forward_result.largest_closure_seed,
            "largest_closure": forward_result.largest_closure,
        },
        "greedy_reverse_peeling": (
            None
            if greedy_result is None
            else {
                "success": greedy_result.success,
                "removed_order": greedy_result.removed_order,
                "terminal_vertices": greedy_result.terminal_vertices,
                "terminal_stuck_set": (
                    None
                    if greedy_result.terminal_stuck_set is None
                    else _json_stuck_set(greedy_result.terminal_stuck_set)
                ),
                "interpretation": (
                    "One deterministic peeling run only; failure gives a concrete "
                    "fixed-selection stuck motif, while success is not a complete "
                    "no-stuck certificate."
                ),
            }
        ),
        "key_peeling_status": key_status,
        "stuck_search": {
            "searched_from_size": stuck_result.searched_from_size,
            "searched_up_to_size": stuck_result.searched_up_to_size,
            "threshold": stuck_result.threshold,
            "search_complete": stuck_result.search_complete,
            "minimal_size": stuck_result.minimal_size,
            "total_at_minimal_size": stuck_result.total_at_minimal_size,
            "examples": [_json_stuck_set(item) for item in stuck_result.examples],
        },
        "filters": filters if filters is not None else pattern_filter_snapshot(S),
    }
