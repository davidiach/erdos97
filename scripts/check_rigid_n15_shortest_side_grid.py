#!/usr/bin/env python3
"""Exact finite checker for the rigid-n=15 shortest-side grid lemma.

This script verifies only the finite algebra/combinatorics used in
``docs/rigid-n15-moser-geometry.md``:

* the four endpoint branch-count cases ``k_A,k_B in {1,2}``;
* saturation of the ``(2,2)`` case into a matching/complementary-matching
  2x2 radius grid; and
* the exact two-Kalmanson-row cancellation for both matching orbits.

It uses integer coefficient vectors only.  It is not a Euclidean
realizability test and does not prove Erdős Problem 97.
"""

from __future__ import annotations

import argparse
import json
from itertools import permutations, product
from pathlib import Path
from typing import Iterable, Sequence

EXPECTED = {
    "checkerboard_orbit_count": 2,
    "endpoint_case_count": 4,
    "count_contradiction_count": 3,
    "checkerboard_count": 1,
}


def add(u: Sequence[int], v: Sequence[int]) -> tuple[int, ...]:
    return tuple(a + b for a, b in zip(u, v, strict=True))


def sub(u: Sequence[int], v: Sequence[int]) -> tuple[int, ...]:
    return tuple(a - b for a, b in zip(u, v, strict=True))


def neg(u: Sequence[int]) -> tuple[int, ...]:
    return tuple(-a for a in u)


def h_vector(cell: tuple[int, int]) -> tuple[int, int, int, int]:
    """Coefficient vector of h_ij = a_i - b_j.

    Coordinates are ordered as ``(a_0,a_1,b_0,b_1)``.
    For cyclic ``A < B < x < y``, strict Kalmanson K2 says
    ``h(x) > h(y)``.
    """

    i, j = cell
    out = [0, 0, 0, 0]
    out[i] += 1
    out[2 + j] -= 1
    return tuple(out)  # type: ignore[return-value]


def checkerboard_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for permutation in permutations((0, 1)):
        matching = ((0, permutation[0]), (1, permutation[1]))
        complement = ((0, 1 - permutation[0]), (1, 1 - permutation[1]))

        # All matching-cell vertices lie in the first cap block and all
        # complementary-cell vertices lie in the later cap block.  Compare
        # the two cells having the same A-radius index.  The A-terms cancel,
        # and the two resulting strict B-radius inequalities are opposites.
        strict_vectors = tuple(
            sub(h_vector(matching[i]), h_vector(complement[i]))
            for i in (0, 1)
        )
        assert strict_vectors[0] == neg(strict_vectors[1])
        assert add(strict_vectors[0], strict_vectors[1]) == (0, 0, 0, 0)

        records.append(
            {
                "matching": [list(cell) for cell in matching],
                "complement": [list(cell) for cell in complement],
                "strict_vectors": [list(v) for v in strict_vectors],
                "sum": [0, 0, 0, 0],
                "interpretation": "two strict K2 rows sum to 0 > 0",
            }
        )
    return records


def endpoint_count_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for k_a, k_b in product((1, 2), repeat=2):
        cross_hits = k_a + k_b
        grid_cells = k_a * k_b
        assert cross_hits >= grid_cells
        if cross_hits > grid_cells:
            status = "count_contradiction"
        else:
            assert (k_a, k_b) == (2, 2)
            status = "checkerboard"
        records.append(
            {
                "k_A": k_a,
                "k_B": k_b,
                "cross_hits": cross_hits,
                "grid_cells": grid_cells,
                "status": status,
            }
        )
    return records


def build_report() -> dict[str, object]:
    checkerboard = checkerboard_records()
    endpoint = endpoint_count_records()
    summary = {
        "checkerboard_orbit_count": len(checkerboard),
        "endpoint_case_count": len(endpoint),
        "count_contradiction_count": sum(
            row["status"] == "count_contradiction" for row in endpoint
        ),
        "checkerboard_count": sum(row["status"] == "checkerboard" for row in endpoint),
    }
    assert summary == EXPECTED
    return {
        "schema": "rigid_n15_shortest_side_grid_v1",
        "trust": "EXACT_FINITE_ALGEBRA",
        "summary": summary,
        "endpoint_cases": endpoint,
        "checkerboard_orbits": checkerboard,
        "non_claims": [
            "not a proof of Erdős Problem 97",
            "not a Euclidean realizability test",
            "the geometric rigid-n=15 hypotheses are proved separately in prose",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the complete report")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--write", type=Path, help="write the deterministic JSON report")
    args = parser.parse_args()

    report = build_report()
    if args.assert_expected:
        assert report["summary"] == EXPECTED
    if args.write is not None:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        summary = report["summary"]
        print(
            "PASS rigid-n15 grid: "
            f"{summary['count_contradiction_count']} count cases, "
            f"{summary['checkerboard_count']} checkerboard case, "
            f"{summary['checkerboard_orbit_count']} exact cancellation orbits"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
