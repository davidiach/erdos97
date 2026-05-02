from __future__ import annotations

from erdos97.altman_diagonal_sums import (
    altman_order_obstruction,
    check_altman,
    chord_order,
)
from erdos97.search import built_in_patterns


def test_chord_order_uses_shorter_cyclic_offset() -> None:
    assert chord_order(19, -8) == 8
    assert chord_order(19, 9) == 9
    assert chord_order(24, -13) == 11


def test_c19_natural_order_altman_kill() -> None:
    result = check_altman(built_in_patterns()["C19_skew"])

    assert result.natural_order_only
    assert result.offsets == [-8, -3, 5, 9]
    assert result.chord_orders == [8, 3, 5, 9]
    assert set(result.forced_equal_U) == {3, 5, 8, 9}
    assert result.altman_contradiction


def test_c17_is_also_natural_order_altman_killed() -> None:
    result = check_altman(built_in_patterns()["C17_skew"])

    assert result.altman_contradiction
    assert set(result.forced_equal_U) == {2, 4, 7, 8}


def test_parity_patterns_are_not_automatically_altman_checked() -> None:
    result = check_altman(built_in_patterns()["P18_parity_balanced"])

    assert not result.altman_contradiction
    assert result.status == "NOT_APPLIED_NONCONSTANT_OFFSETS"


def test_c19_natural_order_signature_filter_recovers_altman_kill() -> None:
    pattern = built_in_patterns()["C19_skew"]
    result = altman_order_obstruction(pattern.S, list(range(pattern.n)), pattern.name)

    assert result.status == "ORDER_EXACT_OBSTRUCTION"
    assert result.altman_contradiction
    assert result.equal_diagonal_order_groups == [[3, 5, 8, 9]]


def test_c19_known_abstract_order_passes_signature_filter() -> None:
    pattern = built_in_patterns()["C19_skew"]
    order = [18, 10, 7, 17, 6, 3, 5, 9, 14, 11, 2, 13, 4, 16, 12, 15, 0, 8, 1]
    result = altman_order_obstruction(pattern.S, order, pattern.name)

    assert result.status == "NO_ORDER_ALTMAN_SIGNATURE_OBSTRUCTION"
    assert not result.altman_contradiction
    assert result.equal_diagonal_order_groups == []
