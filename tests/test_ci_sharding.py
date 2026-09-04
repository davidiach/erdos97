"""Tests for deterministic CI partitioning shared by audit and pytest."""

from __future__ import annotations

import pytest

from erdos97.ci_sharding import (
    ARTIFACT_PR_SHARD_NAMESPACE,
    select_shard,
    stable_shard,
    validate_shard,
)


HEAVIEST_ARTIFACT_PR_TESTS = [
    "tests/test_bootstrap_t12_151_6_label4_center8_target_sparse_three_row_repairs.py::test_target_sparse_three_row_repairs_cli_json",
    "tests/test_bootstrap_t12_151_6_label4_center8_target_sparse_three_row_repairs.py::test_target_sparse_three_row_repairs_artifact_matches_generator",
    "tests/test_c19_fifth_pair_two_row_prefilter.py::test_c19_fifth_pair_two_row_prefilter_replay_matches_artifact",
    "tests/test_c19_kalmanson_prefix_window_prefilter.py::test_c19_prefilter_window_416_447_replay_matches_artifact",
    "tests/test_fragile_cycle_halo_slot_budget.py::test_fast_motif_predicates_match_generic_two_halo_frontier",
    "tests/test_c19_kalmanson_prefix_window_prefilter.py::test_c19_prefilter_window_448_479_replay_matches_artifact",
    "tests/test_c19_kalmanson_prefix_window.py::test_c19_prefix_window_160_191_replay_matches_artifact",
    "tests/test_c19_kalmanson_prefix_window_prefilter.py::test_c19_prefilter_window_384_415_replay_matches_artifact",
]


def test_stable_shards_partition_keys_exactly_once() -> None:
    keys = [f"tests/test_packet_{index}.py::test_case" for index in range(200)]
    shards = [
        select_shard(keys, key=str, shard_index=index, shard_count=8)
        for index in range(8)
    ]

    flattened = [key for shard in shards for key in shard]
    assert len(flattened) == len(keys)
    assert set(flattened) == set(keys)
    assert len(set(flattened)) == len(keys)
    assert all(shard for shard in shards)


def test_stable_shard_normalizes_platform_path_separators() -> None:
    assert stable_shard("tests/test_a.py::test_x", 8) == stable_shard(
        "tests\\test_a.py::test_x",
        8,
    )


def test_artifact_pr_namespace_separates_measured_heavy_tests() -> None:
    assignments = [
        stable_shard(
            nodeid,
            8,
            namespace=ARTIFACT_PR_SHARD_NAMESPACE,
        )
        for nodeid in HEAVIEST_ARTIFACT_PR_TESTS
    ]

    assert assignments == [3, 4, 5, 0, 2, 6, 7, 1]


@pytest.mark.parametrize(
    ("index", "count"),
    [(-1, 4), (4, 4), (0, 0)],
)
def test_invalid_shard_coordinates_are_rejected(index: int, count: int) -> None:
    with pytest.raises(ValueError):
        validate_shard(index, count)
