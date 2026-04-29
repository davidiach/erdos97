from __future__ import annotations

from erdos97.min_radius_filter import (
    minimum_radius_order_obstruction,
    row_is_order_free_blocked,
    selected_pair_sources,
)
from erdos97.search import built_in_patterns


def test_min_radius_filter_kills_all_other_pentagon_pattern() -> None:
    S = [[j for j in range(5) if j != i] for i in range(5)]

    result = minimum_radius_order_obstruction(S, list(range(5)), "K5_all_other")

    assert result.obstructed
    assert result.possible_min_centers == []
    assert result.blocked_centers == list(range(5))
    assert all(row.blocked for row in result.rows)
    assert all(row_is_order_free_blocked(S, center) for center in range(5))


def test_min_radius_filter_c19_survives_natural_order() -> None:
    pattern = built_in_patterns()["C19_skew"]

    result = minimum_radius_order_obstruction(pattern.S, pattern=pattern.name)

    assert not result.obstructed
    assert result.blocked_centers == []
    assert result.possible_min_centers == list(range(19))
    assert result.rows[0].witness_order == [5, 9, 11, 16]
    assert result.rows[0].uncovered_consecutive_pairs == [(5, 9), (9, 11)]
    assert selected_pair_sources(pattern.S, 11, 16) == [11]
