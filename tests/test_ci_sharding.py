"""Tests for deterministic CI partitioning shared by audit and pytest."""

from __future__ import annotations

import pytest

from erdos97.ci_sharding import select_shard, stable_shard, validate_shard


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


@pytest.mark.parametrize(
    ("index", "count"),
    [(-1, 4), (4, 4), (0, 0)],
)
def test_invalid_shard_coordinates_are_rejected(index: int, count: int) -> None:
    with pytest.raises(ValueError):
        validate_shard(index, count)
