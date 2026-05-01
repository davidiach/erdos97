from __future__ import annotations

from erdos97.motif_fingerprint import (
    cyclic_dihedral_key,
    pattern_profile,
    transform_cyclic_dihedral,
)


ROWS = [
    [1, 2, 4, 5],
    [0, 2, 4, 5],
    [0, 1, 4, 5],
    [0, 1, 4, 5],
    [0, 1, 2, 3],
    [0, 1, 2, 3],
]


def test_cyclic_dihedral_key_is_invariant_under_shift_and_reversal() -> None:
    shifted = transform_cyclic_dihedral(ROWS, shift=2)
    reversed_rows = transform_cyclic_dihedral(ROWS, shift=1, reverse=True)

    assert cyclic_dihedral_key(shifted) == cyclic_dihedral_key(ROWS)
    assert cyclic_dihedral_key(reversed_rows) == cyclic_dihedral_key(ROWS)


def test_pattern_profile_contains_expected_histograms() -> None:
    profile = pattern_profile(ROWS)

    assert profile["n"] == 6
    assert len(profile["cyclic_dihedral_sha256"]) == 64
    assert profile["cyclic_dihedral_orbit_size"] <= 12
    assert profile["indegree_histogram"] == {"2": 1, "4": 3, "5": 2}
    assert profile["reciprocal_edge_pairs"] == 11
