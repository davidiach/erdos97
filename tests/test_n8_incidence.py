from __future__ import annotations

import itertools
import json
from pathlib import Path

import pytest

from erdos97.n8_incidence import (
    canonical_key,
    enumeration_data,
    existing_reconstructed_survivor_keys,
    matrix_to_row_masks,
    n8_column_sum_proof_summary,
)


def test_n8_column_sum_four_is_derived_from_column_pair_cap() -> None:
    proof = n8_column_sum_proof_summary()

    assert proof["max_pair_uses_for_fixed_vertex"] == 14
    assert proof["max_indegree"] == 4
    assert proof["total_indegree"] == 32
    assert proof["forced_indegrees"] == [4] * 8


@pytest.fixture(scope="module")
def generated_n8_incidence_data() -> dict:
    root = Path(__file__).resolve().parents[1]
    reconstructed = root / "data" / "incidence" / "n8_reconstructed_15_survivors.json"
    return enumeration_data(reconstructed)


def test_n8_incidence_enumeration_counts_and_matches_reconstructed_survivors(
    generated_n8_incidence_data: dict,
) -> None:
    assert generated_n8_incidence_data["balanced_cap_matrices_with_row0_fixed"] == 117072
    assert generated_n8_incidence_data["forced_perpendicular_survivors_with_row0_fixed"] == 4560
    assert generated_n8_incidence_data["canonical_survivor_class_count"] == 15
    assert generated_n8_incidence_data["matches_existing_reconstructed_survivors"] is True


def test_checked_in_n8_incidence_artifact_matches_generator(
    generated_n8_incidence_data: dict,
) -> None:
    root = Path(__file__).resolve().parents[1]
    artifact = root / "data" / "incidence" / "n8_incidence_completeness.json"

    checked_in = json.loads(artifact.read_text(encoding="utf-8"))
    assert checked_in == generated_n8_incidence_data


def test_checked_in_reconstructed_survivors_are_exactly_the_incidence_survivors() -> None:
    root = Path(__file__).resolve().parents[1]
    artifact = root / "data" / "incidence" / "n8_incidence_completeness.json"
    reconstructed = root / "data" / "incidence" / "n8_reconstructed_15_survivors.json"

    checked_in = json.loads(artifact.read_text(encoding="utf-8"))
    generated_keys = {
        tuple(int(bit_string[::-1], 2) for bit_string in record["row_strings"])
        for record in checked_in["canonical_survivor_classes"]
    }

    assert generated_keys == set(existing_reconstructed_survivor_keys(reconstructed))


def brute_force_canonical_key(rows: tuple[int, ...]) -> tuple[int, ...]:
    best = None
    for permutation in itertools.permutations(range(8)):
        relabelled = [0] * 8
        for old_center, mask in enumerate(rows):
            new_mask = 0
            for old_target in range(8):
                if (mask >> old_target) & 1:
                    new_mask |= 1 << permutation[old_target]
            relabelled[permutation[old_center]] = new_mask
        key = tuple(relabelled)
        if best is None or key < best:
            best = key
    assert best is not None
    return best


def test_fast_canonical_key_matches_full_permutation_search_for_sample_classes() -> None:
    root = Path(__file__).resolve().parents[1]
    reconstructed = root / "data" / "incidence" / "n8_reconstructed_15_survivors.json"
    classes = json.loads(reconstructed.read_text(encoding="utf-8"))

    for record in [classes[0], classes[5], classes[14]]:
        rows = matrix_to_row_masks(record["rows"])
        assert canonical_key(rows) == brute_force_canonical_key(rows)
