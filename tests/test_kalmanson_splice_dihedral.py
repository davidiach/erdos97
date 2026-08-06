from __future__ import annotations

from erdos97.kalmanson_splice import find_dihedral_splice_embeddings


def test_dihedral_scan_finds_five_role_footprint_across_cyclic_cut() -> None:
    rows = {
        3: (1, 4, 5, 6),
        4: (0, 2, 3, 5),
        1: (0, 2, 4, 7),
    }

    embeddings = find_dihedral_splice_embeddings(rows, tuple(range(8)))

    assert any(
        embedding.template == "five_role_K2_K1_splice"
        and dict(embedding.role_map) == {"a": 3, "b": 4, "c": 5, "d": 1, "e": 2}
        for embedding in embeddings
    )
