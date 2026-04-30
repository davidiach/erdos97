#!/usr/bin/env python3
"""Independently check the checked-in n=8 incidence survivor JSON.

This verifier intentionally does not import ``erdos97.n8_incidence``. It does
not prove that the 15 classes are exhaustive; instead it checks that the
checked-in survivor records are internally valid incidence matrices and that
their representatives are true brute-force canonical representatives under all
8! simultaneous relabellings.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import deque
from pathlib import Path
from typing import Iterable

N = 8
CHORDS = tuple((a, b) for a in range(N) for b in range(a + 1, N))


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def chord(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def bits(mask: int) -> list[int]:
    return [idx for idx in range(N) if (mask >> idx) & 1]


def row_masks(rows: Iterable[Iterable[int]]) -> tuple[int, ...]:
    masks: list[int] = []
    for row in rows:
        mask = 0
        for idx, value in enumerate(row):
            if value not in (0, 1):
                raise ValueError(f"matrix entries must be 0 or 1, got {value!r}")
            if value:
                mask |= 1 << idx
        masks.append(mask)
    return tuple(masks)


def relabel_rows(rows: tuple[int, ...], permutation: tuple[int, ...]) -> tuple[int, ...]:
    relabelled = [0] * N
    for old_center, mask in enumerate(rows):
        new_mask = 0
        for old_target in range(N):
            if (mask >> old_target) & 1:
                new_mask |= 1 << permutation[old_target]
        relabelled[permutation[old_center]] = new_mask
    return tuple(relabelled)


def brute_force_canonical_key(rows: tuple[int, ...]) -> tuple[int, ...]:
    return min(relabel_rows(rows, permutation) for permutation in itertools.permutations(range(N)))


def forced_perpendicularity_graph(rows: tuple[int, ...]) -> dict[tuple[int, int], set[tuple[int, int]]]:
    graph = {edge: set() for edge in CHORDS}
    for i in range(N):
        for j in range(i + 1, N):
            common = rows[i] & rows[j]
            if common.bit_count() != 2:
                continue
            a, b = bits(common)
            source = (i, j)
            target = chord(a, b)
            graph[source].add(target)
            graph[target].add(source)
    return graph


def passes_forced_perpendicularity_filter(rows: tuple[int, ...]) -> bool:
    graph = forced_perpendicularity_graph(rows)
    color: dict[tuple[int, int], int] = {}
    for start in CHORDS:
        if start in color:
            continue
        color[start] = 0
        q: deque[tuple[int, int]] = deque([start])
        component: list[tuple[int, int]] = [start]
        while q:
            current = q.popleft()
            for neighbor in graph[current]:
                if neighbor not in color:
                    color[neighbor] = 1 - color[current]
                    component.append(neighbor)
                    q.append(neighbor)
                elif color[neighbor] == color[current]:
                    return False

        used_endpoints_by_color = [0, 0]
        for edge in component:
            edge_color = color[edge]
            a, b = edge
            endpoint_bits = (1 << a) | (1 << b)
            if used_endpoints_by_color[edge_color] & endpoint_bits:
                return False
            used_endpoints_by_color[edge_color] |= endpoint_bits
    return True


def validate_incidence_record(
    record: dict,
) -> tuple[tuple[int, ...] | None, tuple[int, ...] | None, list[str]]:
    errors: list[str] = []
    record_id = record.get("id", "<missing id>")
    rows_data = record.get("rows")
    if not isinstance(rows_data, list) or len(rows_data) != N:
        return None, None, [f"class {record_id}: rows should be an {N}x{N} matrix"]
    if any(not isinstance(row, list) or len(row) != N for row in rows_data):
        return None, None, [f"class {record_id}: rows should be an {N}x{N} matrix"]

    try:
        rows = row_masks(rows_data)
    except ValueError as exc:
        return None, None, [f"class {record_id}: {exc}"]

    for i, mask in enumerate(rows):
        if (mask >> i) & 1:
            errors.append(f"class {record_id}: row {i} contains its own center")
        if mask.bit_count() != 4:
            errors.append(f"class {record_id}: row {i} has sum {mask.bit_count()}, expected 4")

    column_sums = [
        sum(1 for mask in rows if (mask >> target) & 1)
        for target in range(N)
    ]
    if column_sums != [4] * N:
        errors.append(f"class {record_id}: column sums are {column_sums}, expected all 4")

    for i, j in itertools.combinations(range(N), 2):
        overlap = (rows[i] & rows[j]).bit_count()
        if overlap > 2:
            errors.append(f"class {record_id}: rows {i},{j} overlap in {overlap} columns")

    for a, b in itertools.combinations(range(N), 2):
        pair_count = sum(1 for mask in rows if (mask >> a) & 1 and (mask >> b) & 1)
        if pair_count > 2:
            errors.append(f"class {record_id}: columns {a},{b} co-occur in {pair_count} rows")

    if not passes_forced_perpendicularity_filter(rows):
        errors.append(f"class {record_id}: failed forced-perpendicularity filter")

    canonical = brute_force_canonical_key(rows)
    if rows != canonical:
        errors.append(f"class {record_id}: stored representative is not brute-force canonical")

    return rows, canonical, errors


def check_file(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if not isinstance(data, list):
        return {
            "verified": False,
            "path": str(path),
            "errors": ["top-level JSON value should be a list"],
        }

    ids: list[int] = []
    canonical_keys: list[tuple[int, ...]] = []
    for record in data:
        if not isinstance(record, dict):
            errors.append("each survivor record should be an object")
            continue
        record_id = record.get("id")
        if not isinstance(record_id, int):
            errors.append(f"class {record_id!r}: id should be an integer")
        else:
            ids.append(record_id)
        rows, canonical, record_errors = validate_incidence_record(record)
        errors.extend(record_errors)
        if canonical is not None:
            canonical_keys.append(canonical)

    if len(ids) != len(set(ids)):
        errors.append("survivor ids are not unique")
    if ids and sorted(ids) != list(range(len(ids))):
        errors.append(f"survivor ids are {sorted(ids)}, expected contiguous ids 0..{len(ids) - 1}")
    if len(canonical_keys) != len(set(canonical_keys)):
        errors.append("two records have the same brute-force canonical representative")

    return {
        "verified": not errors,
        "path": str(path),
        "record_count": len(data),
        "canonical_class_count": len(set(canonical_keys)),
        "checked_conditions": [
            "matrix shape, binary entries, row sums, and zero diagonal",
            "column sums all equal 4",
            "row-pair intersection cap",
            "column-pair co-occurrence cap",
            "forced-perpendicularity bipartiteness and same-color endpoint filter",
            "brute-force canonical representatives over all 8! relabellings",
            "distinct brute-force canonical classes",
        ],
        "errors": errors,
        "status": "survivor_json_independent_consistency_check_not_completeness_proof",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=repo_root() / "data" / "incidence" / "n8_reconstructed_15_survivors.json",
        help="survivor JSON file to verify",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    summary = check_file(args.path)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif summary["verified"]:
        print(
            "verified "
            f"{summary['record_count']} n=8 survivor records; "
            f"{summary['canonical_class_count']} brute-force canonical classes"
        )
    else:
        print("independent incidence JSON check failed")
        for error in summary["errors"]:
            print(f"- {error}")
    return 0 if summary["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
