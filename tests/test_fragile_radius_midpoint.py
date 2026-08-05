from __future__ import annotations

from pathlib import Path

from erdos97.fragile_radius_midpoint import (
    TwoOverlapRelation,
    midpoint_equation_row,
    radius_midpoint_branch_certificate,
    two_overlap_relations,
    verify_radius_midpoint_identity,
)
from erdos97.json_io import load_json
from scripts.check_fragile_radius_midpoint import assert_expected, build_payload


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "fragile_radius_midpoint.json"


def test_symbolic_radius_midpoint_identity_replays() -> None:
    replay = verify_radius_midpoint_identity()

    assert replay["polynomial_identity_verified"] is True
    assert replay["normalized_factorization_verified"] is True


def test_block6_atom_equal_branch_is_the_midpoint_equation() -> None:
    rows = {0: (1, 2, 3, 4), 3: (0, 2, 4, 5)}
    relations = two_overlap_relations(rows)

    assert relations == [TwoOverlapRelation((0, 3), (2, 4))]
    assert midpoint_equation_row(6, relations[0]) == [1, 0, -1, 1, -1, 0]
    branch = radius_midpoint_branch_certificate(6, relations, [(0, 3)])
    assert branch["midpoint_matrix_rank"] == 1
    assert branch["forced_point_equal_classes"] == []
    assert branch["survives_local_diagnostic"] is True


def test_stored_radius_midpoint_packet_matches_expected() -> None:
    stored = load_json(ARTIFACT)
    assert isinstance(stored, dict)

    assert_expected(stored)
    assert stored == build_payload()


def test_two_block_all_equal_and_atom_equal_branches_split() -> None:
    payload = build_payload()
    for record in payload["benchmarks"][1:]:
        assert record["all_equal_branch"]["coordinate_collision_obstruction"] is True
        assert record["atom_equal_mixed_escape_branch"]["survives_local_diagnostic"] is True
