"""Fast landmark tests for the doubled-Danzer 18-gon slice model."""

import json
from pathlib import Path

import numpy as np
import pytest

from erdos97.danzer18_doubling import (
    EXPECTED_RANK6,
    SUBSETS,
    assignment_rank_and_kernel,
    assignment_residuals,
    collision_x,
    kernel_split_norms,
    numpy_blocks,
    projected_blocks,
    split_direction_matrix,
    trivial_directions,
)


def test_subset_order_matches_documented_table():
    assert SUBSETS[0] == (0, 1, 2, 3)
    assert SUBSETS[1] == (0, 1, 2, 4)
    assert SUBSETS[5] == (0, 1, 4, 5)
    assert SUBSETS[10] == (1, 2, 3, 4)
    assert SUBSETS[14] == (2, 3, 4, 5)
    assert len(SUBSETS) == 15


def test_collision_point_solves_every_uniform_assignment():
    x = collision_x()
    worst = 0.0
    for k in range(15):
        res = assignment_residuals(x, (k,) * 6)
        worst = max(worst, max(abs(v) for v in res))
    assert worst < 1e-12


def test_trivial_directions_annihilated_by_all_blocks():
    x = collision_x()
    blocks = numpy_blocks(x)
    triv = trivial_directions()
    assert np.abs(np.einsum("ckij,jl->ckil", blocks, triv)).max() < 1e-12


@pytest.mark.parametrize("assign,expected_rank", [
    ((5, 5, 5, 5, 5, 5), 9),
    ((1, 2, 3, 4, 5, 6), 9),
    ((1, 2, 1, 2, 1, 2), 8),
    ((10, 0, 5, 5, 0, 0), 7),
])
def test_landmark_ranks(assign, expected_rank):
    pblocks, b = projected_blocks()
    rank, _ = assignment_rank_and_kernel(assign, pblocks, b)
    assert rank == expected_rank


def test_recorded_rank6_assignments():
    pblocks, b = projected_blocks()
    for assign in EXPECTED_RANK6:
        rank, _ = assignment_rank_and_kernel(assign, pblocks, b)
        assert rank == 6


def test_chiral_kernel_splits_all_three_orbits():
    pblocks, b = projected_blocks()
    psplit = split_direction_matrix()
    _, kernel = assignment_rank_and_kernel((1, 2, 1, 2, 1, 2), pblocks, b)
    norms = kernel_split_norms(kernel, psplit)
    assert kernel.shape[0] == 1
    assert (norms > 0.5).all()


def test_diagonal_kernel_survivor_has_no_split_component():
    pblocks, b = projected_blocks()
    psplit = split_direction_matrix()
    _, kernel = assignment_rank_and_kernel((1, 10, 0, 0, 9, 0), pblocks, b)
    norms = kernel_split_norms(kernel, psplit)
    assert kernel.shape[0] == 1
    assert (norms < 1e-12).all()


def test_mp_base_polish_reaches_1e50():
    from mpmath import mpf

    from erdos97.danzer18_doubling import mp_base

    _, residuals = mp_base(dps=60)
    assert max(abs(r) for r in residuals) < mpf("1e-50")


def test_family_scan_records_its_numerical_limitations():
    artifact = (
        Path(__file__).parents[1]
        / "data/certificates/danzer18_family_coincidence_scan.json"
    )
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    assert payload["status"] == "NO_NONDEGENERATE_SIGN_CHANGE_ROOT_DETECTED"
    assert payload["all_detected_sign_change_roots_at_degenerate_endpoint"]
    assert payload["near_coincidence_negative_on_profile"]
    limitations = " ".join(payload["scan_limitations"]).lower()
    assert "tangential" in limitations
    assert "certified full-branch parameterization" in limitations
