"""Sparse-overlap diagnostics for selected-witness patterns.

These routines explain when the minimum-radius and radius-propagation filters
have no leverage because each row has an uncovered consecutive witness pair in
the supplied cyclic order.  They are exact incidence/order diagnostics, not
geometric realization tests.
"""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass
from itertools import combinations, permutations
from typing import Sequence

from erdos97.min_radius_filter import (
    consecutive_witness_pairs,
    covered_witness_path_orders,
    row_is_order_free_blocked,
    row_has_order_free_empty_gap,
    selected_pair_sources,
)
from erdos97.stuck_sets import (
    RadiusChoice,
    RadiusChoiceOptimizationResult,
    RadiusPropagationResult,
    optimize_radius_choice_edges,
    radius_propagation_obstruction,
    validate_selected_pattern,
)

Pair = tuple[int, int]
Pattern = Sequence[Sequence[int]]


@dataclass(frozen=True)
class PairSourceProfile:
    pair: Pair
    sources: list[int]


@dataclass(frozen=True)
class SparseRowProfile:
    center: int
    all_pairs: list[PairSourceProfile]
    consecutive_pairs: list[PairSourceProfile]
    order_free_blocked: bool
    order_free_empty_gap: bool
    covered_witness_path_orders: list[list[int]]

    @property
    def covered_pairs(self) -> list[PairSourceProfile]:
        return [item for item in self.all_pairs if item.sources]

    @property
    def uncovered_pairs(self) -> list[PairSourceProfile]:
        return [item for item in self.all_pairs if not item.sources]

    @property
    def uncovered_consecutive_pairs(self) -> list[PairSourceProfile]:
        return [item for item in self.consecutive_pairs if not item.sources]


def _source_profile(S: Pattern, pair: Pair) -> PairSourceProfile:
    return PairSourceProfile(pair=pair, sources=selected_pair_sources(S, *pair))


def _histogram(values: Sequence[int]) -> dict[str, int]:
    return {str(key): count for key, count in sorted(Counter(values).items())}


def _row_blocked_in_order(S: Pattern, order: Sequence[int], center: int) -> bool:
    """Return True iff every short witness gap for ``center`` is covered."""

    return all(
        selected_pair_sources(S, *pair)
        for pair in consecutive_witness_pairs(order, center, S[center])
    )


def _blocked_rows_in_order(S: Pattern, order: Sequence[int]) -> list[int]:
    """Return centers with no uncovered consecutive witness pair."""

    return [
        center
        for center in range(len(S))
        if _row_blocked_in_order(S, order, center)
    ]


def _row_pair_source_histogram(S: Pattern) -> tuple[dict[str, int], list[dict[str, object]]]:
    """Return source-count histogram for row-local witness pairs."""

    counts: Counter[int] = Counter()
    multi_source_pairs: list[dict[str, object]] = []
    for center, row in enumerate(S):
        for a, b in combinations(row, 2):
            pair = (min(a, b), max(a, b))
            sources = selected_pair_sources(S, *pair)
            counts[len(sources)] += 1
            if len(sources) > 1:
                multi_source_pairs.append(
                    {
                        "center": center,
                        "pair": [pair[0], pair[1]],
                        "sources": sources,
                    }
                )
    return _histogram(list(counts.elements())), multi_source_pairs


def _covered_local_cycles(S: Pattern, center: int) -> list[tuple[int, ...]]:
    """Return local five-label cycles that make ``center`` row-blocked."""

    cycles: list[tuple[int, ...]] = []
    for witness_order in permutations(S[center]):
        if all(
            selected_pair_sources(S, a, b)
            for a, b in zip(witness_order, witness_order[1:])
        ):
            cycles.append((center, *witness_order))
    return cycles


def _covered_local_target_sets(S: Pattern, center: int) -> list[tuple[int, ...]]:
    """Return target sets for all-covered local witness orders."""

    target_sets: set[tuple[int, ...]] = set()
    for witness_order in permutations(S[center]):
        targets = []
        for a, b in zip(witness_order, witness_order[1:]):
            sources = selected_pair_sources(S, a, b)
            if len(sources) != 1:
                break
            targets.append(sources[0])
        else:
            target_sets.add(tuple(sorted(set(targets))))
    return sorted(target_sets)


def _closed_target_subset_order(
    S: Pattern,
    subset: set[int],
    node_limit: int,
) -> tuple[list[int] | None, int, bool]:
    """Return a compatible cyclic order for a closed target subset, if any."""

    constraints = []
    for center in sorted(subset):
        rotations = []
        for witness_order in permutations(S[center]):
            targets = []
            for a, b in zip(witness_order, witness_order[1:]):
                sources = selected_pair_sources(S, a, b)
                if len(sources) != 1:
                    break
                targets.append(sources[0])
            else:
                if set(targets) <= subset:
                    rotations.extend(_cycle_rotations((center, *witness_order)))
        rotations = sorted(set(rotations))
        if not rotations:
            return None, 0, False
        constraints.append((set(rotations[0]), rotations))

    explored_nodes = 0
    hit_limit = False

    def compatible(
        rotations: Sequence[tuple[int, ...]],
        involved: set[int],
        prefix: Sequence[int],
    ) -> bool:
        placed = tuple(label for label in prefix if label in involved)
        return any(placed == rotation[: len(placed)] for rotation in rotations)

    def search(prefix: list[int], remaining: set[int]) -> list[int] | None:
        nonlocal explored_nodes, hit_limit
        explored_nodes += 1
        if explored_nodes > node_limit:
            hit_limit = True
            return None
        if not all(
            compatible(rotations, involved, prefix)
            for involved, rotations in constraints
        ):
            return None
        if not remaining:
            return list(prefix)

        candidates = []
        for label in remaining:
            next_prefix = [*prefix, label]
            alive = sum(
                compatible(rotations, involved, next_prefix)
                for involved, rotations in constraints
            )
            candidates.append((-alive, label))
        for _, label in sorted(candidates):
            next_remaining = set(remaining)
            next_remaining.remove(label)
            result = search([*prefix, label], next_remaining)
            if result is not None:
                return result
            if hit_limit:
                return None
        return None

    return search([0], set(range(len(S))) - {0}), explored_nodes, hit_limit


def _cycle_rotations(cycle: Sequence[int]) -> list[tuple[int, ...]]:
    return [
        tuple(cycle[offset:]) + tuple(cycle[:offset])
        for offset in range(len(cycle))
    ]


def _prefix_can_still_block(
    rotations: Sequence[tuple[int, ...]],
    involved: set[int],
    prefix: Sequence[int],
) -> bool:
    """Return whether future appended labels could make one row blocked."""

    if not rotations:
        return False
    placed = tuple(label for label in prefix if label in involved)
    return any(placed == rotation[: len(placed)] for rotation in rotations)


def _sample_cyclic_orders(
    n: int,
    random_samples: int,
    seed: int,
    include_natural: bool,
) -> list[list[int]]:
    if random_samples < 0:
        raise ValueError("random_samples must be nonnegative")
    rng = random.Random(seed)
    orders: list[list[int]] = []
    seen: set[tuple[int, ...]] = set()

    def add_order(order: Sequence[int]) -> None:
        normalized = tuple(normalize_cyclic_order(order))
        if normalized not in seen:
            seen.add(normalized)
            orders.append(list(normalized))

    if include_natural:
        add_order(list(range(n)))
    attempts = 0
    max_attempts = max(100, random_samples * 20)
    while (
        len(orders) < random_samples + int(include_natural)
        and attempts < max_attempts
    ):
        attempts += 1
        order = list(range(n))
        rng.shuffle(order)
        add_order(order)
    return orders


def normalize_cyclic_order(order: Sequence[int]) -> list[int]:
    """Return a rotation/reversal canonical representative of a cyclic order."""

    if not order:
        raise ValueError("cyclic order must be nonempty")
    n = len(order)
    seen = set(order)
    if seen != set(range(n)):
        missing = sorted(set(range(n)) - seen)
        extra = sorted(seen - set(range(n)))
        raise ValueError(
            f"cyclic order is not a permutation; missing={missing}, extra={extra}"
        )
    pos0 = list(order).index(0)
    rotated = list(order[pos0:]) + list(order[:pos0])
    reversed_order = [rotated[0], *reversed(rotated[1:])]
    return min(rotated, reversed_order)


def sparse_row_profiles(
    S: Pattern,
    order: Sequence[int] | None = None,
) -> list[SparseRowProfile]:
    """Return source-count diagnostics for all witness pairs in every row."""

    validate_selected_pattern(S)
    n = len(S)
    if order is None:
        order = list(range(n))
    profiles: list[SparseRowProfile] = []
    for center, row in enumerate(S):
        all_pairs = [
            _source_profile(S, (min(a, b), max(a, b)))
            for a, b in combinations(row, 2)
        ]
        consecutive = [
            _source_profile(S, pair)
            for pair in consecutive_witness_pairs(order, center, row)
        ]
        profiles.append(
            SparseRowProfile(
                center=center,
                all_pairs=all_pairs,
                consecutive_pairs=consecutive,
                order_free_blocked=row_is_order_free_blocked(S, center),
                order_free_empty_gap=row_has_order_free_empty_gap(S, center),
                covered_witness_path_orders=covered_witness_path_orders(S, center),
            )
        )
    return profiles


def _pair_json(profile: PairSourceProfile) -> dict[str, object]:
    return {
        "pair": [profile.pair[0], profile.pair[1]],
        "sources": profile.sources,
        "source_count": len(profile.sources),
    }


def sparse_frontier_summary(
    pattern_name: str,
    S: Pattern,
    order: Sequence[int] | None = None,
    max_row_examples: int = 4,
) -> dict[str, object]:
    """Return a JSON-ready sparse-frontier diagnostic summary."""

    if max_row_examples < 0:
        raise ValueError("max_row_examples must be nonnegative")
    validate_selected_pattern(S)
    n = len(S)
    if order is None:
        order = list(range(n))
    order = list(order)
    profiles = sparse_row_profiles(S, order=order)
    all_source_counts = [
        len(pair.sources) for row in profiles for pair in row.all_pairs
    ]
    consecutive_source_counts = [
        len(pair.sources) for row in profiles for pair in row.consecutive_pairs
    ]
    rows_with_uncovered_pair = [
        row.center for row in profiles if row.uncovered_pairs
    ]
    rows_with_uncovered_consecutive = [
        row.center for row in profiles if row.uncovered_consecutive_pairs
    ]
    order_free_blocked = [
        row.center for row in profiles if row.order_free_blocked
    ]
    order_free_empty_gap = [
        row.center for row in profiles if row.order_free_empty_gap
    ]
    empty_choice = [
        _pair_json(row.uncovered_consecutive_pairs[0])
        for row in profiles
        if row.uncovered_consecutive_pairs
    ]
    row_examples = []
    for row in profiles[:max_row_examples]:
        row_examples.append(
            {
                "center": row.center,
                "all_pairs": [_pair_json(pair) for pair in row.all_pairs],
                "consecutive_pairs": [
                    _pair_json(pair) for pair in row.consecutive_pairs
                ],
                "uncovered_pair_count": len(row.uncovered_pairs),
                "covered_pair_count": len(row.covered_pairs),
                "uncovered_consecutive_pair_count": len(
                    row.uncovered_consecutive_pairs
                ),
                "order_free_blocked": row.order_free_blocked,
                "order_free_empty_gap": row.order_free_empty_gap,
                "covered_witness_path_count": len(row.covered_witness_path_orders),
                "covered_witness_path_examples": row.covered_witness_path_orders[:3],
            }
        )

    all_rows_have_empty_consecutive_choice = (
        len(rows_with_uncovered_consecutive) == n
    )
    return {
        "type": "sparse_frontier_pair_source_diagnostic",
        "pattern": pattern_name,
        "n": n,
        "order": order,
        "all_pair_source_count_histogram": _histogram(all_source_counts),
        "consecutive_pair_source_count_histogram": _histogram(
            consecutive_source_counts
        ),
        "rows_with_uncovered_pair": rows_with_uncovered_pair,
        "rows_with_uncovered_consecutive_pair": rows_with_uncovered_consecutive,
        "order_free_blocked_rows": order_free_blocked,
        "order_free_empty_gap_rows": order_free_empty_gap,
        "all_rows_have_uncovered_consecutive_pair": (
            all_rows_have_empty_consecutive_choice
        ),
        "all_rows_order_free_empty_gap": len(order_free_empty_gap) == n,
        "trivial_empty_radius_choice_exists": (
            all_rows_have_empty_consecutive_choice
        ),
        "trivial_empty_radius_choice_all_orders": len(order_free_empty_gap) == n,
        "empty_radius_choice": (
            empty_choice if all_rows_have_empty_consecutive_choice else None
        ),
        "row_examples": row_examples,
        "semantics": (
            "Exact fixed-order incidence diagnostic. If every row has an "
            "uncovered consecutive witness pair, the radius-propagation filter "
            "can choose those pairs and force no strict radius inequalities. "
            "If all_rows_order_free_empty_gap is true, the same empty-choice "
            "escape holds for every cyclic order by a row-local covered-path "
            "certificate. "
            "This is a blindness certificate for that filter, not evidence of "
            "geometric realizability."
        ),
    }


def sample_empty_gap_orders(
    pattern_name: str,
    S: Pattern,
    random_samples: int = 100,
    seed: int = 0,
    include_natural: bool = True,
    max_examples: int = 3,
) -> dict[str, object]:
    """Sample cyclic orders and test for all-row uncovered short-gap choices."""

    if random_samples < 0:
        raise ValueError("random_samples must be nonnegative")
    if max_examples < 0:
        raise ValueError("max_examples must be nonnegative")
    validate_selected_pattern(S)
    n = len(S)
    orders = _sample_cyclic_orders(n, random_samples, seed, include_natural)

    row_counts: list[int] = []
    empty_choice_orders = 0
    natural_order_result: dict[str, object] | None = None
    examples_without_empty_choice: list[dict[str, object]] = []
    examples_with_empty_choice: list[dict[str, object]] = []

    for order in orders:
        summary = sparse_frontier_summary(
            pattern_name,
            S,
            order=order,
            max_row_examples=0,
        )
        rows = list(summary["rows_with_uncovered_consecutive_pair"])
        row_count = len(rows)
        row_counts.append(row_count)
        missing = [center for center in range(n) if center not in rows]
        has_empty_choice = row_count == n
        if has_empty_choice:
            empty_choice_orders += 1
        item = {
            "order": order,
            "rows_with_uncovered_consecutive_pair": rows,
            "rows_without_uncovered_consecutive_pair": missing,
            "trivial_empty_radius_choice_exists": has_empty_choice,
        }
        if order == list(range(n)):
            natural_order_result = item
        if has_empty_choice and len(examples_with_empty_choice) < max_examples:
            examples_with_empty_choice.append(item)
        if not has_empty_choice and len(examples_without_empty_choice) < max_examples:
            examples_without_empty_choice.append(item)

    return {
        "type": "sparse_frontier_empty_gap_order_sample",
        "pattern": pattern_name,
        "n": n,
        "random_samples_requested": random_samples,
        "seed": seed,
        "include_natural": include_natural,
        "orders_checked": len(orders),
        "unique_orders_generated": len(orders),
        "empty_choice_orders": empty_choice_orders,
        "empty_choice_fraction": (
            empty_choice_orders / len(orders) if orders else None
        ),
        "rows_with_uncovered_consecutive_histogram": _histogram(row_counts),
        "min_rows_with_uncovered_consecutive_pair": (
            min(row_counts) if row_counts else None
        ),
        "natural_order": natural_order_result,
        "examples_with_empty_choice": examples_with_empty_choice,
        "examples_without_empty_choice": examples_without_empty_choice,
        "semantics": (
            "Random cyclic-order sampling only, quotienting rotation and "
            "reversal for reporting. Failing to find an order without the "
            "empty-gap escape is not an exhaustive abstract-order theorem."
        ),
    }


def certify_min_uncovered_consecutive_rows(
    pattern_name: str,
    S: Pattern,
    node_limit: int = 1_000_000,
    initial_order: Sequence[int] | None = None,
) -> dict[str, object]:
    """Certify the best possible empty-gap row count over cyclic orders.

    The objective is row-local: minimize the number of centers whose four
    witnesses have at least one uncovered consecutive pair.  Equivalently, this
    maximizes rows that are blocked by the minimum-radius short-chord test.
    The search fixes label 0 first, which quotients cyclic rotations but not
    reversal.
    """

    validate_selected_pattern(S)
    if node_limit <= 0:
        raise ValueError("node_limit must be positive")
    n = len(S)
    if initial_order is None:
        initial_order = list(range(n))
    initial_order = normalize_cyclic_order(initial_order)
    if len(initial_order) != n:
        raise ValueError("initial order has wrong length")

    local_cycles = [_covered_local_cycles(S, center) for center in range(n)]
    row_rotations = []
    row_involved = []
    for cycles in local_cycles:
        rotations = sorted(
            {
                rotation
                for cycle in cycles
                for rotation in _cycle_rotations(cycle)
            }
        )
        row_rotations.append(rotations)
        row_involved.append(set(rotations[0]) if rotations else set())

    def possible_blocked_rows(prefix: Sequence[int]) -> list[int]:
        return [
            center
            for center in range(n)
            if _prefix_can_still_block(
                row_rotations[center],
                row_involved[center],
                prefix,
            )
        ]

    best_order = list(initial_order)
    best_blocked_rows = _blocked_rows_in_order(S, best_order)
    best_blocked_count = len(best_blocked_rows)
    explored_nodes = 0
    pruned_nodes = 0
    hit_limit = False

    def search(prefix: list[int], remaining: set[int]) -> None:
        nonlocal best_order, best_blocked_rows, best_blocked_count
        nonlocal explored_nodes, pruned_nodes, hit_limit

        if hit_limit:
            return
        explored_nodes += 1
        if explored_nodes > node_limit:
            hit_limit = True
            return

        possible = possible_blocked_rows(prefix)
        if len(possible) <= best_blocked_count:
            pruned_nodes += 1
            return
        if not remaining:
            blocked = _blocked_rows_in_order(S, prefix)
            if len(blocked) > best_blocked_count:
                best_blocked_count = len(blocked)
                best_blocked_rows = blocked
                best_order = list(prefix)
            return

        candidates = []
        for label in remaining:
            next_prefix = [*prefix, label]
            candidates.append((len(possible_blocked_rows(next_prefix)), label))
        for _, label in sorted(candidates):
            next_remaining = set(remaining)
            next_remaining.remove(label)
            search([*prefix, label], next_remaining)

    search([0], set(range(1, n)))

    search_complete = not hit_limit
    rows_with_uncovered = [
        center for center in range(n) if center not in set(best_blocked_rows)
    ]
    radius = radius_propagation_obstruction(S, order=best_order)
    minimization = optimize_radius_choice_edges(S, order=best_order, objective="min")
    status = "CERTIFIED_OPTIMUM" if search_complete else "UNKNOWN_NODE_LIMIT"
    return {
        "type": "sparse_frontier_empty_gap_order_bound",
        "pattern": pattern_name,
        "n": n,
        "status": status,
        "search_complete": search_complete,
        "node_limit": node_limit,
        "explored_nodes": explored_nodes,
        "pruned_nodes": pruned_nodes,
        "rotation_quotient_fixed_label": 0,
        "reversal_quotiented": False,
        "best_order": best_order,
        "best_rows_with_uncovered_consecutive_pair": rows_with_uncovered,
        "best_rows_without_uncovered_consecutive_pair": best_blocked_rows,
        "best_rows_with_uncovered_consecutive_pair_count": len(rows_with_uncovered),
        "max_blocked_rows_found": best_blocked_count,
        "certified_min_rows_with_uncovered_consecutive_pair": (
            len(rows_with_uncovered) if search_complete else None
        ),
        "certified_max_blocked_rows": (
            best_blocked_count if search_complete else None
        ),
        "covered_local_cycle_counts": [
            len(cycles) for cycles in local_cycles
        ],
        "best_radius_propagation": _radius_summary(radius),
        "best_radius_choice_minimization": _radius_optimization_summary(
            minimization
        ),
        "semantics": (
            "Exact branch-and-bound over cyclic orders when search_complete is "
            "true. The objective is only the row-local empty-gap count for the "
            "minimum-radius/radius-propagation filter; it is not a geometric "
            "realizability test."
        ),
    }


def certify_single_target_radius_pass(
    pattern_name: str,
    S: Pattern,
    max_active_rows: int = 24,
    compatibility_node_limit: int = 100_000,
) -> dict[str, object]:
    """Certify all-order radius-propagation pass in the single-target case.

    When every covered row-local witness pair has exactly one endpoint source,
    a fixed-order radius obstruction is equivalent to a nonempty closed target
    set: every row in the set is blocked, and all of its possible radius targets
    stay inside the set.  If no such target set exists even before imposing a
    global cyclic order, every cyclic order passes this radius-cycle filter.
    """

    validate_selected_pattern(S)
    if max_active_rows <= 0:
        raise ValueError("max_active_rows must be positive")
    if compatibility_node_limit <= 0:
        raise ValueError("compatibility_node_limit must be positive")
    n = len(S)
    source_histogram, multi_source_pairs = _row_pair_source_histogram(S)
    if multi_source_pairs:
        return {
            "type": "sparse_frontier_single_target_radius_pass_certificate",
            "pattern": pattern_name,
            "n": n,
            "status": "UNSUPPORTED_MULTI_TARGET_PAIR",
            "search_complete": False,
            "radius_pass_all_orders": None,
            "row_pair_source_count_histogram": source_histogram,
            "multi_source_pair_examples": multi_source_pairs[:8],
            "semantics": (
                "This certificate only applies when every row-local covered "
                "witness pair has at most one endpoint source."
            ),
        }

    target_sets_by_center = [
        _covered_local_target_sets(S, center) for center in range(n)
    ]
    active_rows = [
        center for center, target_sets in enumerate(target_sets_by_center)
        if target_sets
    ]
    if len(active_rows) > max_active_rows:
        return {
            "type": "sparse_frontier_single_target_radius_pass_certificate",
            "pattern": pattern_name,
            "n": n,
            "status": "UNKNOWN_TOO_MANY_ACTIVE_ROWS",
            "search_complete": False,
            "radius_pass_all_orders": None,
            "max_active_rows": max_active_rows,
            "active_rows": active_rows,
            "active_row_count": len(active_rows),
            "row_pair_source_count_histogram": source_histogram,
        }

    checked_subsets = 0
    candidate_closed_subsets = 0
    compatibility_nodes = 0
    closed_target_set: list[int] | None = None
    closed_target_order: list[int] | None = None
    hit_limit = False
    active_count = len(active_rows)
    for mask in range(1, 1 << active_count):
        checked_subsets += 1
        subset = {
            active_rows[index]
            for index in range(active_count)
            if mask & (1 << index)
        }
        if all(
            any(set(targets) <= subset for targets in target_sets_by_center[center])
            for center in subset
        ):
            candidate_closed_subsets += 1
            order, nodes, subset_hit_limit = _closed_target_subset_order(
                S,
                subset,
                compatibility_node_limit,
            )
            compatibility_nodes += nodes
            if subset_hit_limit:
                hit_limit = True
                break
            if order is not None:
                closed_target_set = sorted(subset)
                closed_target_order = order
                break

    no_closed_set = closed_target_set is None and not hit_limit
    return {
        "type": "sparse_frontier_single_target_radius_pass_certificate",
        "pattern": pattern_name,
        "n": n,
        "status": (
            "CERTIFIED_PASS_ALL_ORDERS"
            if no_closed_set
            else (
                "UNKNOWN_COMPATIBILITY_NODE_LIMIT"
                if hit_limit
                else "COMPATIBLE_CLOSED_TARGET_SET_FOUND"
            )
        ),
        "search_complete": not hit_limit,
        "radius_pass_all_orders": (
            True if no_closed_set else False if closed_target_set is not None else None
        ),
        "row_pair_source_count_histogram": source_histogram,
        "active_rows": active_rows,
        "active_row_count": active_count,
        "checked_subsets": checked_subsets,
        "candidate_closed_subsets": candidate_closed_subsets,
        "compatibility_node_limit": compatibility_node_limit,
        "compatibility_nodes": compatibility_nodes,
        "closed_target_set": closed_target_set,
        "closed_target_order": closed_target_order,
        "target_set_counts_by_center": [
            len(target_sets) for target_sets in target_sets_by_center
        ],
        "target_set_examples_by_center": [
            [list(targets) for targets in target_sets[:4]]
            for target_sets in target_sets_by_center
        ],
        "semantics": (
            "Exact row-local certificate for the single-target radius-choice "
            "case, plus a cyclic-order compatibility check for any closed "
            "target-set candidate. If radius_pass_all_orders is true, no "
            "cyclic order can be obstructed by the current radius-propagation "
            "cycle filter. This does not test geometric realizability."
        ),
    }


def _radius_summary(order_result: RadiusPropagationResult) -> dict[str, object]:
    acyclic_choice = order_result.acyclic_choice
    return {
        "status": order_result.status,
        "obstructed": order_result.obstructed,
        "explored_nodes": order_result.explored_nodes,
        "acyclic_edge_count": (
            None
            if acyclic_choice is None
            else sum(len(choice.smaller_centers) for choice in acyclic_choice)
        ),
    }


def _choice_summary(choice: RadiusChoice) -> dict[str, object]:
    return {
        "center": choice.center,
        "consecutive_pair": [
            choice.consecutive_pair[0],
            choice.consecutive_pair[1],
        ],
        "smaller_centers": choice.smaller_centers,
    }


def _radius_optimization_summary(
    result: RadiusChoiceOptimizationResult,
) -> dict[str, object]:
    return {
        "status": result.status,
        "obstructed": result.obstructed,
        "objective": result.objective,
        "optimality_certified": result.optimality_certified,
        "edge_count": result.edge_count,
        "edge_lower_bound": result.edge_lower_bound,
        "edge_upper_bound": result.edge_upper_bound,
        "explored_nodes": result.explored_nodes,
        "acyclic_choice": (
            None
            if result.acyclic_choice is None
            else [_choice_summary(choice) for choice in result.acyclic_choice]
        ),
    }


def _order_radius_item(
    pattern_name: str,
    S: Pattern,
    order: Sequence[int],
    node_limit: int,
) -> dict[str, object]:
    n = len(S)
    summary = sparse_frontier_summary(
        pattern_name,
        S,
        order=order,
        max_row_examples=0,
    )
    rows = list(summary["rows_with_uncovered_consecutive_pair"])
    missing = [center for center in range(n) if center not in rows]
    radius = radius_propagation_obstruction(
        S,
        order=order,
        node_limit=node_limit,
    )
    return {
        "order": list(order),
        "rows_with_uncovered_consecutive_pair": rows,
        "rows_without_uncovered_consecutive_pair": missing,
        "trivial_empty_radius_choice_exists": len(rows) == n,
        "radius_propagation": _radius_summary(radius),
    }


def _adversarial_score(item: dict[str, object]) -> tuple[int, int, int, int]:
    rows = item["rows_with_uncovered_consecutive_pair"]
    radius = item["radius_propagation"]
    if not isinstance(rows, list) or not isinstance(radius, dict):
        raise TypeError("invalid adversarial item")
    status = radius["status"]
    if status == "RADIUS_CYCLE_OBSTRUCTED":
        status_rank = 0
    elif status == "UNKNOWN_NODE_LIMIT":
        status_rank = 1
    else:
        status_rank = 2
    edge_count = radius["acyclic_edge_count"]
    explored = radius["explored_nodes"]
    return (
        len(rows),
        status_rank,
        -(int(edge_count) if edge_count is not None else -1),
        -int(explored),
    )


def sample_radius_propagation_orders(
    pattern_name: str,
    S: Pattern,
    random_samples: int = 100,
    seed: int = 0,
    include_natural: bool = True,
    max_examples: int = 3,
    node_limit: int = 100_000,
) -> dict[str, object]:
    """Sample cyclic orders and run the full radius-propagation filter."""

    if random_samples < 0:
        raise ValueError("random_samples must be nonnegative")
    if max_examples < 0:
        raise ValueError("max_examples must be nonnegative")
    if node_limit <= 0:
        raise ValueError("node_limit must be positive")
    validate_selected_pattern(S)
    n = len(S)
    orders = _sample_cyclic_orders(n, random_samples, seed, include_natural)

    row_counts: list[int] = []
    empty_choice_orders = 0
    status_counts: Counter[str] = Counter()
    empty_choice_status_counts: Counter[str] = Counter()
    no_empty_choice_status_counts: Counter[str] = Counter()
    explored_nodes: list[int] = []
    natural_order_result: dict[str, object] | None = None
    examples_without_empty_choice: list[dict[str, object]] = []
    examples_obstructed_or_unknown: list[dict[str, object]] = []

    for order in orders:
        summary = sparse_frontier_summary(
            pattern_name,
            S,
            order=order,
            max_row_examples=0,
        )
        rows = list(summary["rows_with_uncovered_consecutive_pair"])
        row_count = len(rows)
        row_counts.append(row_count)
        missing = [center for center in range(n) if center not in rows]
        has_empty_choice = row_count == n
        radius = radius_propagation_obstruction(
            S,
            order=order,
            node_limit=node_limit,
        )
        status_counts[radius.status] += 1
        if has_empty_choice:
            empty_choice_orders += 1
            empty_choice_status_counts[radius.status] += 1
        else:
            no_empty_choice_status_counts[radius.status] += 1
        explored_nodes.append(radius.explored_nodes)
        item = {
            "order": order,
            "rows_with_uncovered_consecutive_pair": rows,
            "rows_without_uncovered_consecutive_pair": missing,
            "trivial_empty_radius_choice_exists": has_empty_choice,
            "radius_propagation": _radius_summary(radius),
        }
        if order == list(range(n)):
            natural_order_result = item
        if (
            not has_empty_choice
            and len(examples_without_empty_choice) < max_examples
        ):
            examples_without_empty_choice.append(item)
        if (
            radius.obstructed is not False
            and len(examples_obstructed_or_unknown) < max_examples
        ):
            examples_obstructed_or_unknown.append(item)

    return {
        "type": "sparse_frontier_radius_order_sample",
        "pattern": pattern_name,
        "n": n,
        "random_samples_requested": random_samples,
        "seed": seed,
        "include_natural": include_natural,
        "orders_checked": len(orders),
        "unique_orders_generated": len(orders),
        "node_limit": node_limit,
        "empty_choice_orders": empty_choice_orders,
        "empty_choice_fraction": (
            empty_choice_orders / len(orders) if orders else None
        ),
        "rows_with_uncovered_consecutive_histogram": _histogram(row_counts),
        "min_rows_with_uncovered_consecutive_pair": (
            min(row_counts) if row_counts else None
        ),
        "radius_status_histogram": dict(sorted(status_counts.items())),
        "empty_choice_radius_status_histogram": dict(
            sorted(empty_choice_status_counts.items())
        ),
        "no_empty_choice_radius_status_histogram": dict(
            sorted(no_empty_choice_status_counts.items())
        ),
        "max_explored_nodes": max(explored_nodes) if explored_nodes else None,
        "natural_order": natural_order_result,
        "examples_without_empty_choice": examples_without_empty_choice,
        "examples_obstructed_or_unknown": examples_obstructed_or_unknown,
        "semantics": (
            "Random cyclic-order sampling only. The radius-propagation status "
            "is an exact fixed-order necessary filter for each sampled order. "
            "PASS_ACYCLIC_CHOICE is not evidence of geometric realizability; "
            "it only means that this radius-cycle filter did not obstruct "
            "that order."
        ),
    }


def search_adversarial_orders(
    pattern_name: str,
    S: Pattern,
    random_samples: int = 100,
    seed: int = 0,
    include_natural: bool = True,
    restarts: int = 8,
    local_steps: int = 200,
    max_examples: int = 5,
    node_limit: int = 100_000,
) -> dict[str, object]:
    """Heuristically search for cyclic orders stressing radius propagation."""

    if random_samples < 0:
        raise ValueError("random_samples must be nonnegative")
    if restarts < 0:
        raise ValueError("restarts must be nonnegative")
    if local_steps < 0:
        raise ValueError("local_steps must be nonnegative")
    if max_examples < 0:
        raise ValueError("max_examples must be nonnegative")
    if node_limit <= 0:
        raise ValueError("node_limit must be positive")
    validate_selected_pattern(S)
    n = len(S)
    rng = random.Random(seed)
    initial_orders = _sample_cyclic_orders(n, random_samples, seed, include_natural)

    cache: dict[tuple[int, ...], dict[str, object]] = {}
    evaluated: list[dict[str, object]] = []

    def evaluate(order: Sequence[int]) -> dict[str, object]:
        normalized = tuple(normalize_cyclic_order(order))
        if normalized in cache:
            return cache[normalized]
        item = _order_radius_item(pattern_name, S, normalized, node_limit)
        cache[normalized] = item
        evaluated.append(item)
        return item

    for order in initial_orders:
        evaluate(order)

    if not evaluated:
        return {
            "type": "sparse_frontier_adversarial_order_search",
            "pattern": pattern_name,
            "n": n,
            "random_samples_requested": random_samples,
            "seed": seed,
            "include_natural": include_natural,
            "restarts": restarts,
            "local_steps": local_steps,
            "node_limit": node_limit,
            "orders_evaluated": 0,
            "best_examples": [],
            "semantics": (
                "Heuristic cyclic-order search only. No exhaustive abstract-order "
                "claim is made."
            ),
        }

    starts = sorted(evaluated, key=lambda item: (_adversarial_score(item), item["order"]))
    for restart in range(restarts):
        current = starts[restart % len(starts)]
        current_order = list(current["order"])
        current_score = _adversarial_score(current)
        for _ in range(local_steps):
            trial = list(current_order)
            left, right = rng.sample(range(n), 2)
            trial[left], trial[right] = trial[right], trial[left]
            trial_item = evaluate(trial)
            trial_score = _adversarial_score(trial_item)
            if trial_score <= current_score:
                current = trial_item
                current_order = list(current["order"])
                current_score = trial_score

    row_counts = [
        len(item["rows_with_uncovered_consecutive_pair"]) for item in evaluated
    ]
    status_counts: Counter[str] = Counter(
        str(item["radius_propagation"]["status"]) for item in evaluated
    )
    best = sorted(evaluated, key=lambda item: (_adversarial_score(item), item["order"]))
    best_examples: list[dict[str, object]] = []
    for item in best[:max_examples]:
        enriched = dict(item)
        minimization = optimize_radius_choice_edges(
            S,
            order=list(item["order"]),
            objective="min",
            node_limit=node_limit,
        )
        enriched["radius_choice_minimization"] = _radius_optimization_summary(
            minimization
        )
        best_examples.append(enriched)
    best_score = _adversarial_score(best[0]) if best else None

    return {
        "type": "sparse_frontier_adversarial_order_search",
        "pattern": pattern_name,
        "n": n,
        "random_samples_requested": random_samples,
        "seed": seed,
        "include_natural": include_natural,
        "restarts": restarts,
        "local_steps": local_steps,
        "node_limit": node_limit,
        "orders_evaluated": len(evaluated),
        "rows_with_uncovered_consecutive_histogram": _histogram(row_counts),
        "min_rows_with_uncovered_consecutive_pair": (
            min(row_counts) if row_counts else None
        ),
        "radius_status_histogram": dict(sorted(status_counts.items())),
        "best_score": (
            None
            if best_score is None
            else {
                "rows_with_uncovered_consecutive_pair": best_score[0],
                "radius_status_rank": best_score[1],
                "negative_acyclic_edge_count": best_score[2],
                "negative_explored_nodes": best_score[3],
            }
        ),
        "best_examples": best_examples,
        "semantics": (
            "Heuristic cyclic-order search only, using random starts plus "
            "swap hill-climbing. It looks for orders with fewer rows admitting "
            "uncovered consecutive witness pairs, then for stronger "
            "radius-propagation stress. Failure to find an obstruction is not "
            "an exhaustive abstract-order theorem."
        ),
    }
