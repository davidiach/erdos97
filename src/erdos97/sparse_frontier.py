"""Sparse-overlap diagnostics for selected-witness patterns.

These routines explain when the minimum-radius and radius-propagation filters
have no leverage because each row has an uncovered consecutive witness pair in
the supplied cyclic order.  They are exact incidence/order diagnostics, not
geometric realization tests.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Sequence

from erdos97.min_radius_filter import (
    consecutive_witness_pairs,
    row_is_order_free_blocked,
    selected_pair_sources,
)
from erdos97.stuck_sets import validate_selected_pattern

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
                "uncovered_consecutive_pair_count": len(
                    row.uncovered_consecutive_pairs
                ),
                "order_free_blocked": row.order_free_blocked,
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
        "all_rows_have_uncovered_consecutive_pair": (
            all_rows_have_empty_consecutive_choice
        ),
        "trivial_empty_radius_choice_exists": (
            all_rows_have_empty_consecutive_choice
        ),
        "empty_radius_choice": (
            empty_choice if all_rows_have_empty_consecutive_choice else None
        ),
        "row_examples": row_examples,
        "semantics": (
            "Exact fixed-order incidence diagnostic. If every row has an "
            "uncovered consecutive witness pair, the radius-propagation filter "
            "can choose those pairs and force no strict radius inequalities. "
            "This is a blindness certificate for that filter, not evidence of "
            "geometric realizability."
        ),
    }
