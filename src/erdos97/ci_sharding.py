"""Deterministic helpers for partitioning CI work without losing coverage."""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterable
from typing import TypeVar


T = TypeVar("T")
SHARD_ALGORITHM = "sha256(key) modulo shard_count"
NAMESPACED_SHARD_ALGORITHM = "sha256(namespace + NUL + key) modulo shard_count"
# Selected from PR #926 duration telemetry so the eight slowest PR artifact
# tests occupy eight distinct shards. The focused regression test pins that split.
ARTIFACT_PR_SHARD_NAMESPACE = "artifact-pr-balanced-v1-1118"


def validate_shard(shard_index: int, shard_count: int) -> None:
    """Validate a zero-based shard coordinate."""
    if shard_count < 1:
        raise ValueError("shard count must be at least 1")
    if shard_index < 0 or shard_index >= shard_count:
        raise ValueError(
            f"shard index must satisfy 0 <= index < {shard_count}; got {shard_index}"
        )


def stable_shard(key: str, shard_count: int, *, namespace: str = "") -> int:
    """Return the stable shard for ``key``.

    SHA-256 avoids Python's process-randomized ``hash`` and keeps assignment
    independent of collection order and platform path separators. An optional
    namespace permits a measured workload to use a different stable partition
    without changing the default assignment used by existing consumers.
    """
    validate_shard(0, shard_count)
    normalized = key.replace("\\", "/")
    digest_input = normalized if not namespace else f"{namespace}\0{normalized}"
    digest = hashlib.sha256(digest_input.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % shard_count


def select_shard(
    items: Iterable[T],
    *,
    key: Callable[[T], str],
    shard_index: int,
    shard_count: int,
    namespace: str = "",
) -> list[T]:
    """Return exactly the items assigned to one deterministic shard."""
    validate_shard(shard_index, shard_count)
    return [
        item
        for item in items
        if stable_shard(key(item), shard_count, namespace=namespace) == shard_index
    ]
