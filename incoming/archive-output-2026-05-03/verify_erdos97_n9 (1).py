#!/usr/bin/env python3
"""Exact verifier for the finite n=9 extension in the Erdős #97 report.

This script is intentionally self-contained and uses only Python's standard
library. It verifies two things:

1. The n=9 selected-witness incidence/order backtracking leaves exactly the
   patterns listed in erdos97_n9_certificates.json.
2. For every listed pattern, the attached positive Kalmanson/Farkas certificate
   sums exactly to the zero vector after quotienting ordinary distance variables
   by the selected-distance equalities.

It does not attempt to prove the full Erdős #97 problem.
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from typing import Iterable

N = 9
ROW_SIZE = 4
PAIR_CAP = 2
MAX_INDEGREE = (PAIR_CAP * (N - 1)) // (ROW_SIZE - 1)  # floor(16/3) = 5

Pair = tuple[int, int]
Pattern = tuple[tuple[int, ...], ...]


def pair(a: int, b: int) -> Pair:
    if a == b:
        raise ValueError("degenerate pair")
    return (a, b) if a < b else (b, a)


def bits(mask: int) -> list[int]:
    return [i for i in range(N) if (mask >> i) & 1]


def mask_from_values(values: Iterable[int]) -> int:
    out = 0
    for v in values:
        out |= 1 << int(v)
    return out


def is_adjacent(a: int, b: int) -> bool:
    return (a - b) % N in (1, N - 1)


def crosses(e: Pair, f: Pair) -> bool:
    a, b = pair(*e)
    c, d = pair(*f)
    if len({a, b, c, d}) < 4:
        return False
    return ((a < c < b) != (a < d < b))


CHORDS: list[Pair] = [(a, b) for a in range(N) for b in range(a + 1, N)]
CHORD_INDEX = {chord: index for index, chord in enumerate(CHORDS)}


def enumerate_patterns() -> list[Pattern]:
    """Enumerate all n=9 patterns surviving the exact necessary filters."""
    row_options: list[list[int]] = []
    for center in range(N):
        row_options.append(
            [
                mask_from_values(combo)
                for combo in combinations([j for j in range(N) if j != center], ROW_SIZE)
            ]
        )

    mask_bits: dict[int, list[int]] = {}
    mask_pair_indices: dict[int, list[int]] = {}
    for options in row_options:
        for mask in options:
            if mask not in mask_bits:
                row = bits(mask)
                mask_bits[mask] = row
                mask_pair_indices[mask] = [
                    CHORD_INDEX[pair(a, b)] for a, b in combinations(row, 2)
                ]

    compat: dict[tuple[int, int], dict[int, dict[int, bool]]] = {}
    for center in range(N):
        for previous in range(center):
            table: dict[int, dict[int, bool]] = {}
            for mask in row_options[center]:
                inner: dict[int, bool] = {}
                for previous_mask in row_options[previous]:
                    common = mask & previous_mask
                    common_count = common.bit_count()
                    ok = True
                    if common_count > PAIR_CAP:
                        ok = False
                    elif common_count == PAIR_CAP:
                        source = pair(previous, center)
                        witnesses = bits(common)
                        target = pair(witnesses[0], witnesses[1])
                        ok = (not is_adjacent(previous, center)) and crosses(source, target)
                    inner[previous_mask] = ok
                table[mask] = inner
            compat[(previous, center)] = table

    def reflected(row: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(sorted((N - x) % N for x in row))

    row0_reps: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()
    for row in combinations(range(1, N), ROW_SIZE):
        rep = min(tuple(row), reflected(tuple(row)))
        if rep not in seen:
            seen.add(rep)
            row0_reps.append(rep)

    patterns: list[Pattern] = []
    for row0 in row0_reps:
        rows = [mask_from_values(row0)]
        indegree = [0] * N
        pair_counts = [0] * len(CHORDS)
        for v in mask_bits[rows[0]]:
            indegree[v] += 1
        for idx in mask_pair_indices[rows[0]]:
            pair_counts[idx] += 1

        def search(center: int) -> None:
            if center == N:
                patterns.append(tuple(tuple(mask_bits[m]) for m in rows))
                return
            for mask in row_options[center]:
                if any(not compat[(previous, center)][mask][previous_mask]
                       for previous, previous_mask in enumerate(rows)):
                    continue
                row = mask_bits[mask]
                if any(indegree[v] >= MAX_INDEGREE for v in row):
                    continue
                pair_indices = mask_pair_indices[mask]
                if any(pair_counts[idx] >= PAIR_CAP for idx in pair_indices):
                    continue
                rows.append(mask)
                for v in row:
                    indegree[v] += 1
                for idx in pair_indices:
                    pair_counts[idx] += 1
                search(center + 1)
                for idx in pair_indices:
                    pair_counts[idx] -= 1
                for v in row:
                    indegree[v] -= 1
                rows.pop()

        search(1)
    return patterns


class DSU:
    def __init__(self, items: Iterable[Pair]):
        self.parent = {item: item for item in items}

    def find(self, item: Pair) -> Pair:
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, a: Pair, b: Pair) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def distance_classes(pattern: Pattern) -> dict[Pair, int]:
    all_pairs = [pair(a, b) for a, b in combinations(range(N), 2)]
    dsu = DSU(all_pairs)
    for center, row in enumerate(pattern):
        base = pair(center, row[0])
        for witness in row[1:]:
            dsu.union(base, pair(center, witness))
    roots: dict[Pair, int] = {}
    classes: dict[Pair, int] = {}
    for p in all_pairs:
        root = dsu.find(p)
        if root not in roots:
            roots[root] = len(roots)
        classes[p] = roots[root]
    return classes


def inequality_terms(kind: str, quad: list[int]) -> list[tuple[Pair, int]]:
    a, b, c, d = quad
    if kind == "K1":
        return [(pair(a, c), +1), (pair(b, d), +1), (pair(a, b), -1), (pair(c, d), -1)]
    if kind == "K2":
        return [(pair(a, c), +1), (pair(b, d), +1), (pair(a, d), -1), (pair(b, c), -1)]
    raise ValueError(f"unknown Kalmanson inequality kind: {kind!r}")


def verify_certificate(item: dict) -> None:
    pattern = tuple(tuple(int(x) for x in row) for row in item["rows"])
    classes = distance_classes(pattern)
    totals = [0] * (max(classes.values()) + 1)
    for ineq in item["inequalities"]:
        weight = int(ineq["weight"])
        if weight <= 0:
            raise AssertionError("non-positive certificate weight")
        quad = [int(x) for x in ineq["quad"]]
        if quad != sorted(quad) or len(set(quad)) != 4:
            raise AssertionError(f"quad is not in natural cyclic order: {quad}")
        for p, coef in inequality_terms(str(ineq["kind"]), quad):
            totals[classes[p]] += weight * coef
    if any(totals):
        raise AssertionError(f"certificate does not cancel exactly: {totals}")


def main() -> int:
    cert_path = Path(__file__).with_name("erdos97_n9_certificates.json")
    payload = json.loads(cert_path.read_text(encoding="utf-8"))
    certificates = payload["certificates"]

    enumerated = enumerate_patterns()
    enumerated_set = set(enumerated)
    certified_set = {
        tuple(tuple(int(x) for x in row) for row in item["rows"])
        for item in certificates
    }
    if len(enumerated) != 102:
        raise AssertionError(f"expected 102 enumerated patterns, got {len(enumerated)}")
    if enumerated_set != certified_set:
        missing = enumerated_set - certified_set
        extra = certified_set - enumerated_set
        raise AssertionError(f"certificate pattern mismatch: missing={len(missing)}, extra={len(extra)}")

    for item in certificates:
        verify_certificate(item)

    print("OK")
    print("row-0 reflection representatives: 38")
    print("incidence/order survivors: 102")
    print("exact Kalmanson/Farkas certificates verified: 102")
    print("conclusion verified: no n=9 selected-witness counterexample in the fixed cyclic order; by relabeling, no n=9 counterexample")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
