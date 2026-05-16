from __future__ import annotations

import pytest

from erdos97.adaptive_blockers import first_blocker
from erdos97.bridge_negative_controls import c13_sidon_rows
from erdos97.radius_blocker_packets import (
    analyze_radius_blocker_packet,
    canonical_dihedral_subset,
    dihedral_subset_images,
    dihedral_subset_representatives,
    exact_four_rich_classes_from_rows,
    full_exact_four_radius_blocker_rich_classes,
    row_options_from_rich_classes,
)


def test_c13_fixed_packet_has_blocker_and_strict_cycle() -> None:
    rows = c13_sidon_rows()
    rich_classes = exact_four_rich_classes_from_rows(rows)
    blocker = first_blocker(rich_classes, max_size=4)

    assert blocker == [0, 1, 2, 3]

    result = analyze_radius_blocker_packet(
        "c13-test",
        rich_classes,
        blocker,
        list(range(13)),
    )

    assert result.radius_blocker_ok
    assert result.incidence_survivors == 1
    assert result.vertex_circle_status_counts == {"strict_cycle": 1}
    assert result.all_incidence_survivors_obstructed


def test_packet_accepts_multiple_exact_four_options() -> None:
    rows = c13_sidon_rows()
    rich_classes = list(exact_four_rich_classes_from_rows(rows))
    rich_classes[0] = (tuple(rows[0]), (1, 3, 4, 10))

    result = analyze_radius_blocker_packet(
        "c13-two-row0-options",
        tuple(rich_classes),
        [0, 1, 2, 3],
        list(range(13)),
    )

    assert result.radius_blocker_ok
    assert result.row_option_counts[0] == 2
    assert result.raw_selection_upper_bound == 2
    assert not result.aborted


def test_full_exact_four_radius_blocker_options_enforce_blocker() -> None:
    rich_classes = full_exact_four_radius_blocker_rich_classes(9, [0, 1, 2, 3])

    assert [len(rows) for rows in rich_classes] == [
        65,
        65,
        65,
        65,
        70,
        70,
        70,
        70,
        70,
    ]
    for center in [0, 1, 2, 3]:
        assert all(
            len({0, 1, 2, 3}.intersection(row)) <= 2
            for row in rich_classes[center]
        )


def test_dihedral_four_blocker_representatives_cover_n9_subsets() -> None:
    representatives = dihedral_subset_representatives(9, 4)

    assert representatives == (
        (0, 1, 2, 3),
        (0, 1, 2, 4),
        (0, 1, 2, 5),
        (0, 1, 3, 4),
        (0, 1, 3, 5),
        (0, 1, 3, 6),
        (0, 1, 3, 7),
        (0, 1, 4, 5),
        (0, 1, 4, 6),
        (0, 2, 4, 6),
    )
    assert sum(len(dihedral_subset_images(9, rep)) for rep in representatives) == 126
    assert canonical_dihedral_subset(9, [5, 6, 7, 8]) == (0, 1, 2, 3)


def test_large_rich_classes_are_rejected_until_semantics_are_added() -> None:
    rich_classes = (
        ((1, 2, 3, 4, 5),),
        ((0, 2, 3, 4),),
        ((0, 1, 3, 4),),
        ((0, 1, 2, 4),),
        ((0, 1, 2, 3),),
        ((0, 1, 2, 3),),
    )

    with pytest.raises(ValueError, match="requires exact four-rich classes"):
        row_options_from_rich_classes(rich_classes)
