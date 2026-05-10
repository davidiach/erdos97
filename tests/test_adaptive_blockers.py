from __future__ import annotations

import pytest

from erdos97.adaptive_blockers import (
    adaptive_reverse_peeling,
    first_blocker,
    is_radius_blocker,
    outside_pair_expansion_bound,
    singleton_rich_classes_from_pattern,
)
from erdos97.bridge_negative_controls import c13_sidon_rows


def test_adaptive_reverse_peeling_builds_ear_order_without_blocker() -> None:
    rich_classes = tuple(
        (tuple(label for label in range(5) if label != center),)
        for center in range(5)
    )

    result = adaptive_reverse_peeling(rich_classes)

    assert result.success
    assert result.seed is not None
    assert len(result.seed) == 3
    assert result.forward_order is not None
    assert sorted(result.forward_order) == list(range(5))
    assert result.blocker is None
    assert sorted(result.selected_rows) == list(range(5))


def test_radius_blocker_detects_fixed_linear_sidon_seed() -> None:
    rich_classes = singleton_rich_classes_from_pattern(c13_sidon_rows())
    blocker = [0, 1, 2, 3]

    assert is_radius_blocker(rich_classes, blocker)
    assert first_blocker(rich_classes, max_size=4) is not None


def test_radius_blocker_rejects_out_of_range_subset_label() -> None:
    rich_classes = singleton_rich_classes_from_pattern(c13_sidon_rows())

    with pytest.raises(ValueError, match="out-of-range"):
        is_radius_blocker(rich_classes, [0, 1, 2, 99])


def test_outside_pair_expansion_bound() -> None:
    assert outside_pair_expansion_bound(0) == 0
    assert outside_pair_expansion_bound(1) == 0
    assert outside_pair_expansion_bound(5) == 20
