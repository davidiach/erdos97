#!/usr/bin/env python3
"""Bounded row-Ptolemy audit for block-6 fragile full extensions."""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.fragile_hypergraph import _selected_pair_ok, block6_family  # noqa: E402
from erdos97.incidence_filters import (  # noqa: E402
    row_ptolemy_product_cancellation_certificates,
)


def _full_extensions(
    n: int,
    fixed_rows: dict[int, list[int]],
    order: Sequence[int],
    max_nodes: int,
    state: dict[str, int | bool],
):
    candidates: dict[int, list[tuple[int, ...]]] = {}
    for center in range(n):
        if center in fixed_rows:
            candidates[center] = [tuple(fixed_rows[center])]
        else:
            labels = [label for label in range(n) if label != center]
            candidates[center] = [tuple(row) for row in combinations(labels, 4)]

    assigned: dict[int, tuple[int, ...]] = {}
    nodes = 0
    hit_limit = False

    def candidate_ok(center: int, row: Sequence[int]) -> bool:
        return all(
            _selected_pair_ok(center, row, other, other_row, order)
            for other, other_row in assigned.items()
        )

    def choose_center() -> tuple[int | None, list[tuple[int, ...]]]:
        best_center: int | None = None
        best_rows: list[tuple[int, ...]] = []
        for center in range(n):
            if center in assigned:
                continue
            viable = [row for row in candidates[center] if candidate_ok(center, row)]
            if best_center is None or len(viable) < len(best_rows):
                best_center = center
                best_rows = viable
            if not viable:
                break
        return best_center, best_rows

    def search():
        nonlocal nodes, hit_limit
        state["nodes_visited"] = nodes
        state["hit_node_limit"] = hit_limit
        if len(assigned) == n:
            yield {center: list(row) for center, row in sorted(assigned.items())}
            return
        if nodes >= max_nodes:
            hit_limit = True
            state["hit_node_limit"] = hit_limit
            return
        center, viable = choose_center()
        if center is None:
            yield {center: list(row) for center, row in sorted(assigned.items())}
            return
        for row in viable:
            nodes += 1
            state["nodes_visited"] = nodes
            assigned[center] = row
            yield from search()
            del assigned[center]
            if hit_limit:
                return

    yield from search()
    state["nodes_visited"] = nodes
    state["hit_node_limit"] = hit_limit


def _rows_as_sequence(rows: dict[int, list[int]]) -> list[list[int]]:
    return [rows[center] for center in range(len(rows))]


def audit(blocks: int, max_extensions: int, max_nodes: int) -> dict[str, object]:
    n, fixed_rows = block6_family(blocks)
    order = list(range(n))
    records = []
    killed = 0
    survivor = None

    state: dict[str, int | bool] = {"nodes_visited": 0, "hit_node_limit": False}
    generator = _full_extensions(n, fixed_rows, order, max_nodes, state)
    for index, rows in enumerate(generator, start=1):
        certs = row_ptolemy_product_cancellation_certificates(
            _rows_as_sequence(rows),
            order,
        )
        record = {
            "extension_index": index,
            "row_ptolemy_product_cancellation_count": len(certs),
            "status": "killed_by_row_ptolemy_product_cancellation"
            if certs
            else "survives_row_ptolemy_product_cancellation",
            "rows": {str(center): row for center, row in sorted(rows.items())},
        }
        if certs:
            killed += 1
            first = certs[0]
            record["first_certificate"] = {
                "row": first["row"],
                "witness_order": first["witness_order"],
                "variant": first["variant"],
                "zero_product": first["zero_product"],
            }
        elif survivor is None:
            survivor = record
        records.append(record)
        if survivor is not None or len(records) >= max_extensions:
            break

    return {
        "type": "block6_row_ptolemy_full_extension_audit",
        "schema": "erdos97.block6_row_ptolemy_full_extension_audit.v1",
        "blocks": blocks,
        "n": n,
        "fixed_rows": {str(center): row for center, row in sorted(fixed_rows.items())},
        "cyclic_order": order,
        "max_extensions": max_extensions,
        "max_nodes": max_nodes,
        "extensions_examined": len(records),
        "extensions_killed_by_row_ptolemy_product_cancellation": killed,
        "survivor_found": survivor is not None,
        "survivor": survivor,
        "records": records,
        "nodes_visited": state["nodes_visited"],
        "hit_node_limit": state["hit_node_limit"],
        "interpretation": (
            "Bounded exact audit only. A survivor is an obstruction to the "
            "claim that row-Ptolemy product-cancellation kills every full "
            "selected-row extension of the fixed block-6 fragile rows."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blocks", type=int, default=2)
    parser.add_argument("--max-extensions", type=int, default=3)
    parser.add_argument("--max-nodes", type=int, default=100_000)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-survivor", action="store_true")
    args = parser.parse_args()

    payload = audit(args.blocks, args.max_extensions, args.max_nodes)
    if args.assert_survivor and not payload["survivor_found"]:
        raise AssertionError("expected a row-Ptolemy survivor extension")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("block6 row-Ptolemy full-extension audit")
        print(f"blocks: {payload['blocks']}")
        print(f"extensions examined: {payload['extensions_examined']}")
        print(
            "killed by product-cancellation: "
            f"{payload['extensions_killed_by_row_ptolemy_product_cancellation']}"
        )
        print(f"survivor found: {payload['survivor_found']}")
        if args.assert_survivor:
            print("OK: survivor expectation verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
