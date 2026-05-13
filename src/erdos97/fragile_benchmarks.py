"""Shared fragile-cover benchmark selected-row systems."""

from __future__ import annotations

BLOCK6_TWO_BLOCK_SURVIVOR_EXTENSION_3: tuple[tuple[int, ...], ...] = (
    (1, 2, 3, 4),
    (3, 6, 9, 11),
    (1, 3, 5, 10),
    (0, 2, 4, 5),
    (0, 3, 8, 11),
    (0, 1, 6, 7),
    (7, 8, 9, 10),
    (1, 5, 6, 8),
    (0, 5, 7, 9),
    (6, 8, 10, 11),
    (2, 5, 9, 11),
    (0, 4, 6, 10),
)


def block6_two_block_survivor_extension_3_rows() -> list[list[int]]:
    """Return a mutable copy of the fixed two-block block-6 survivor rows."""

    return [list(row) for row in BLOCK6_TWO_BLOCK_SURVIVOR_EXTENSION_3]
