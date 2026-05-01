"""Cyclic-order fingerprints for fixed selected-witness patterns."""

from __future__ import annotations

import hashlib
from collections import Counter
from itertools import combinations
from typing import Sequence

Pattern = Sequence[Sequence[int]]


def _validate_pattern(S: Pattern) -> None:
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


def row_masks(S: Pattern) -> tuple[int, ...]:
    """Return bit-mask rows for a validated selected-witness pattern."""

    _validate_pattern(S)
    masks: list[int] = []
    for row in S:
        mask = 0
        for label in row:
            mask |= 1 << int(label)
        masks.append(mask)
    return tuple(masks)


def row_strings_from_masks(masks: Sequence[int], n: int) -> list[str]:
    return [
        "".join("1" if (mask >> label) & 1 else "0" for label in range(n))
        for mask in masks
    ]


def transform_cyclic_dihedral(S: Pattern, shift: int = 0, reverse: bool = False) -> list[list[int]]:
    """Relabel a pattern by a cyclic shift, optionally followed by reversal."""

    _validate_pattern(S)
    n = len(S)

    def map_label(label: int) -> int:
        if reverse:
            return (shift - label) % n
        return (label + shift) % n

    out: list[list[int]] = [[] for _ in range(n)]
    for old_center, row in enumerate(S):
        new_center = map_label(old_center)
        out[new_center] = sorted(map_label(label) for label in row)
    return out


def cyclic_dihedral_key(S: Pattern) -> tuple[int, ...]:
    """Return the lexicographically least row-mask key under D_n relabeling."""

    _validate_pattern(S)
    n = len(S)
    keys = []
    for shift in range(n):
        for reverse in (False, True):
            keys.append(row_masks(transform_cyclic_dihedral(S, shift=shift, reverse=reverse)))
    return min(keys)


def _histogram(values: Sequence[int]) -> dict[str, int]:
    return {str(key): count for key, count in sorted(Counter(values).items())}


def pattern_profile(S: Pattern) -> dict[str, object]:
    """Return a JSON-ready fixed-order profile and cyclic-dihedral fingerprint."""

    _validate_pattern(S)
    n = len(S)
    masks = row_masks(S)
    key = cyclic_dihedral_key(S)
    key_strings = row_strings_from_masks(key, n)
    key_blob = "|".join(key_strings).encode("ascii")
    orbit_keys = {
        row_masks(transform_cyclic_dihedral(S, shift=shift, reverse=reverse))
        for shift in range(n)
        for reverse in (False, True)
    }

    indegrees = [0] * n
    for row in S:
        for label in row:
            indegrees[label] += 1

    row_intersections = [
        (masks[left] & masks[right]).bit_count()
        for left, right in combinations(range(n), 2)
    ]
    column_pair_codegrees = []
    for a, b in combinations(range(n), 2):
        count = sum(1 for row in S if a in row and b in row)
        column_pair_codegrees.append(count)

    reciprocal_pairs = 0
    for a, b in combinations(range(n), 2):
        if b in S[a] and a in S[b]:
            reciprocal_pairs += 1

    return {
        "type": "fixed_order_cyclic_dihedral_fingerprint",
        "n": n,
        "cyclic_dihedral_sha256": hashlib.sha256(key_blob).hexdigest(),
        "cyclic_dihedral_key_rows": key_strings,
        "cyclic_dihedral_orbit_size": len(orbit_keys),
        "indegree_histogram": _histogram(indegrees),
        "row_intersection_histogram": _histogram(row_intersections),
        "column_pair_codegree_histogram": _histogram(column_pair_codegrees),
        "reciprocal_edge_pairs": reciprocal_pairs,
        "semantics": (
            "Fingerprint is canonical only under cyclic rotations and reversal "
            "of the fixed order, not under arbitrary relabeling."
        ),
    }
