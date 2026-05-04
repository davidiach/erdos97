#!/usr/bin/env python3
"""Search cyclic orders that avoid two-inequality Kalmanson certificates.

For a fixed circulant selected-witness pattern, this exact DFS fixes label
``0`` first, using translation symmetry, and searches for a cyclic order whose
completed Kalmanson rows contain no inverse pair.  If the search exhausts, then
every cyclic order of that fixed abstract pattern has a two-inequality
Kalmanson/Farkas obstruction.

The result is an all-order statement only for the supplied fixed abstract
pattern.  It is not a proof of Erdos Problem #97.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_kalmanson_certificate import (  # noqa: E402
    build_distance_classes,
    inequality_terms,
)
from kalmanson_order_utils import parse_int_list  # noqa: E402

KINDS = ("K1_diag_gt_sides", "K2_diag_gt_other")


def _sparse_vector(
    classes: dict[tuple[int, int], int],
    kind: str,
    quad: Sequence[int],
) -> tuple[tuple[int, int], ...]:
    acc: Counter[int] = Counter()
    for pair, coefficient in inequality_terms(kind, quad):
        acc[classes[pair]] += coefficient
    return tuple(sorted((idx, value) for idx, value in acc.items() if value))


def _prepare_vector_tables(
    n: int,
    offsets: Sequence[int],
) -> tuple[dict[tuple[int, int, int, int], tuple[int, int]], list[int]]:
    """Precompute ordered-quad row-vector ids and inverse-vector ids."""

    classes = dict(build_distance_classes(n, offsets))
    vector_to_id: dict[tuple[tuple[int, int], ...], int] = {}
    inverse_id: list[int | None] = []

    def get_id(vector: tuple[tuple[int, int], ...]) -> int:
        existing = vector_to_id.get(vector)
        if existing is not None:
            return existing
        vector_id = len(vector_to_id)
        vector_to_id[vector] = vector_id
        inverse_id.append(None)
        negative = tuple((idx, -value) for idx, value in vector)
        negative_id = vector_to_id.get(negative)
        if negative_id is not None:
            inverse_id[vector_id] = negative_id
            inverse_id[negative_id] = vector_id
        return vector_id

    quad_ids: dict[tuple[int, int, int, int], tuple[int, int]] = {}
    labels = range(n)
    for quad in itertools.permutations(labels, 4):
        quad_ids[quad] = tuple(
            get_id(_sparse_vector(classes, kind, quad)) for kind in KINDS
        )  # type: ignore[assignment]

    return quad_ids, [-1 if value is None else value for value in inverse_id]


def search_avoiding_order(
    name: str,
    n: int,
    offsets: Sequence[int],
    *,
    node_limit: int | None = None,
) -> dict[str, object]:
    """Search for a cyclic order with no two-inequality inverse pair."""

    if n <= 0:
        raise ValueError("n must be positive")
    if node_limit is not None and node_limit <= 0:
        raise ValueError("node_limit must be positive when supplied")

    quad_ids, inverse_id = _prepare_vector_tables(n, offsets)
    counts = [0] * len(inverse_id)
    nodes_visited = 0
    pruned_branches = 0
    max_surviving_prefix: list[int] = []
    stopped_by_limit = False

    def dfs(order: list[int], remaining: list[int]) -> list[int] | None:
        nonlocal nodes_visited, pruned_branches, max_surviving_prefix, stopped_by_limit
        nodes_visited += 1
        if len(order) > len(max_surviving_prefix):
            max_surviving_prefix = order[:]
        if not remaining:
            return order[:]
        if node_limit is not None and nodes_visited >= node_limit:
            stopped_by_limit = True
            return None

        for label in remaining:
            new_vectors: list[int] = []
            local_vectors: set[int] = set()
            has_completed_certificate = False
            for a, b, c in itertools.combinations(order, 3):
                for vector_id in quad_ids[(a, b, c, label)]:
                    inverse = inverse_id[vector_id]
                    if (inverse >= 0 and counts[inverse]) or inverse in local_vectors:
                        has_completed_certificate = True
                        break
                    new_vectors.append(vector_id)
                    local_vectors.add(vector_id)
                if has_completed_certificate:
                    break
            if has_completed_certificate:
                pruned_branches += 1
                continue

            for vector_id in new_vectors:
                counts[vector_id] += 1
            next_remaining = [item for item in remaining if item != label]
            survivor = dfs(order + [label], next_remaining)
            for vector_id in new_vectors:
                counts[vector_id] -= 1
            if survivor is not None or stopped_by_limit:
                return survivor
        return None

    survivor = dfs([0], list(range(1, n)))
    if survivor is not None:
        status = "FOUND_ORDER_WITHOUT_TWO_INEQUALITY_KALMANSON_CERTIFICATE"
        trust = "EXACT_COUNTEREXAMPLE_TO_THIS_FILTER_ONLY"
    elif stopped_by_limit:
        status = "UNKNOWN_NODE_LIMIT_REACHED"
        trust = "BOUNDED_SEARCH_DIAGNOSTIC"
    else:
        status = "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION"
        trust = "EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN"

    return {
        "type": "kalmanson_two_inverse_pair_order_search_v1",
        "trust": trust,
        "status": status,
        "pattern": {
            "name": name,
            "n": n,
            "circulant_offsets": [int(offset) for offset in offsets],
        },
        "rotation_quotient": (
            "For circulant selected-witness patterns, translating labels lets "
            "the search fix label 0 as the first cyclic-order entry."
        ),
        "reversal_quotient": "none",
        "node_limit": node_limit,
        "nodes_visited": nodes_visited,
        "branches_pruned_by_completed_two_certificate": pruned_branches,
        "max_surviving_prefix_depth": len(max_surviving_prefix),
        "max_surviving_prefix": max_surviving_prefix,
        "survivor_order": survivor,
        "semantics": (
            "If status is EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION, "
            "every cyclic order of this fixed abstract pattern contains some "
            "inverse pair of strict Kalmanson inequalities. This does not prove "
            "Erdos Problem #97."
        ),
    }


def assert_c13_expected(payload: dict[str, object]) -> None:
    pattern = payload["pattern"]
    if not isinstance(pattern, dict) or pattern.get("name") != "C13_sidon_1_2_4_10":
        raise AssertionError(f"unexpected pattern: {pattern}")
    if payload["status"] != "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION":
        raise AssertionError(f"unexpected status: {payload['status']}")
    if payload["nodes_visited"] != 1496677:
        raise AssertionError(f"unexpected node count: {payload['nodes_visited']}")
    if payload["branches_pruned_by_completed_two_certificate"] != 6192576:
        raise AssertionError(
            "unexpected prune count: "
            f"{payload['branches_pruned_by_completed_two_certificate']}"
        )
    if payload["max_surviving_prefix_depth"] != 11:
        raise AssertionError(
            f"unexpected max prefix depth: {payload['max_surviving_prefix_depth']}"
        )
    if payload["survivor_order"] is not None:
        raise AssertionError(f"unexpected survivor: {payload['survivor_order']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="pattern name")
    parser.add_argument("--n", required=True, type=int)
    parser.add_argument("--offsets", required=True, type=parse_int_list)
    parser.add_argument("--node-limit", type=int, help="stop after this many DFS nodes")
    parser.add_argument("--out", type=Path, help="optional JSON output path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--assert-obstructed", action="store_true")
    parser.add_argument("--assert-c13-expected", action="store_true")
    args = parser.parse_args()

    payload = search_avoiding_order(
        args.name,
        args.n,
        args.offsets,
        node_limit=args.node_limit,
    )
    if args.assert_obstructed and (
        payload["status"] != "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION"
    ):
        raise AssertionError(f"search did not prove all-order obstruction: {payload['status']}")
    if args.assert_c13_expected:
        assert_c13_expected(payload)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            f"{payload['pattern']['name']} {payload['status']} "
            f"nodes={payload['nodes_visited']} "
            f"pruned={payload['branches_pruned_by_completed_two_certificate']} "
            f"max_prefix={payload['max_surviving_prefix_depth']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
