#!/usr/bin/env python3
"""Replay the S12A parity two-orbit frontier-pattern diagnostics.

S12A is the n=12 selected-witness pattern with even centers using offsets
{1, 2, 10, 11} and odd centers using offsets {2, 5, 7, 10}, taken at the
natural cyclic order. This historical diagnostic records why the pattern was
once a frontier lead. It is now superseded by the exact equilateral-ear
obstruction in ``scripts/check_s12a_equilateral_ears.py``.

Replayed checks (all deterministic):

- structure: the rows realize the stated parity offsets;
- two-circle row-pair cap, witness-pair capacity with the hull-edge
  refinement, and the two-overlap crossing rule: no violations;
- vertex-circle selected-distance quotient filter: not obstructed;
- full Kalmanson quotient cone at the natural order: 32 distance classes,
  770 distinct nonzero strict rows, no zero rows, and both normalized LP
  screens (zero-sum and nonpositive) infeasible under HiGHS - a solver
  diagnostic recording that no Kalmanson/Farkas certificate exists over
  this row family at this order;
- squared-distance value rows (see
  ``scripts/check_block6_value_rows_closure.py``): satisfiable at layers
  N, N+S, N+OD, N+ODS (solver outcomes recorded as controls).

Claim scope: this is superseded diagnostic provenance only. Passing these
necessary abstract filters never implied realizability. The later elementary
certificate excludes S12A in this fixed natural order. Neither artifact proves
an all-order obstruction for the abstract pattern or changes the
official/global falsifiable/open status.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for entry in (str(SRC), str(ROOT)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from erdos97.quotient_cone import (  # noqa: E402
    kalmanson_row,
    selected_distance_quotient,
)
from erdos97.vertex_circle_order_filter import (  # noqa: E402
    vertex_circle_order_obstruction,
)
from scripts.check_block6_value_rows_closure import solve_layers  # noqa: E402

OUT = ROOT / "data" / "certificates" / "s12a_parity_two_orbit_frontier.json"
SCHEMA = "erdos97.s12a_parity_two_orbit_frontier.v3"
STATUS = "SUPERSEDED_FRONTIER_DIAGNOSTIC"
TRUST = "REVIEW_PENDING_PROVENANCE"
CLAIM_SCOPE = (
    "Superseded abstract selected-witness diagnostic: S12A passed the "
    "implemented necessary abstract filters at the "
    "natural order (row caps, witness-pair capacity, two-overlap crossing, "
    "vertex-circle quotient, full Kalmanson cone LP screens, value rows). "
    "The exact equilateral-ear certificate now obstructs this fixed natural "
    "order. This retained artifact is provenance only, not a live frontier, "
    "an all-order S12A obstruction, a proof of Erdos Problem #97, or a "
    "counterexample."
)
PROVENANCE = {
    "generator": "scripts/check_s12a_frontier_pattern.py",
    "command": (
        "python scripts/check_s12a_frontier_pattern.py --write "
        "--assert-expected"
    ),
}

N = 12
EVEN_OFFSETS = (1, 2, 10, 11)
ODD_OFFSETS = (2, 5, 7, 10)
EXPECTED_DISTANCE_CLASSES = 32
EXPECTED_STRICT_ROWS = 770
EXPECTED_VALUE_ROW_LAYERS = {"N": "sat", "S": "sat", "OD": "sat", "ODS": "sat"}


def s12a_rows() -> list[tuple[int, ...]]:
    rows = []
    for center in range(N):
        offsets = EVEN_OFFSETS if center % 2 == 0 else ODD_OFFSETS
        rows.append(tuple(sorted((center + o) % N for o in offsets)))
    return rows


def crossing_separated(center_a: int, center_b: int, x: int, y: int) -> bool:
    """Centers sharing chord {x, y} must lie on opposite sides in order."""

    span = (y - x) % N

    def inside(label: int) -> bool:
        return 0 < (label - x) % N < span

    return inside(center_a) != inside(center_b)


def incidence_diagnostics(rows: list[tuple[int, ...]]) -> dict[str, Any]:
    max_intersection = max(
        len(set(a) & set(b)) for a, b in combinations(rows, 2)
    )
    pair_counts: Counter[tuple[int, int]] = Counter()
    for row in rows:
        for pair in combinations(sorted(row), 2):
            pair_counts[pair] += 1
    hull_edges = {tuple(sorted((i, (i + 1) % N))) for i in range(N)}
    capacity_violations = sum(
        1
        for pair, count in pair_counts.items()
        if count > 2 or (pair in hull_edges and count > 1)
    )
    crossing_violations = 0
    for (i, row_i), (j, row_j) in combinations(enumerate(rows), 2):
        shared = sorted(set(row_i) & set(row_j))
        if len(shared) == 2 and not crossing_separated(i, j, *shared):
            crossing_violations += 1
    return {
        "row_pair_intersection_max": max_intersection,
        "witness_pair_capacity_violations": capacity_violations,
        "two_overlap_crossing_violations": crossing_violations,
    }


def kalmanson_diagnostics(rows: list[tuple[int, ...]]) -> dict[str, Any]:
    import numpy as np
    from scipy.optimize import linprog

    quotient = selected_distance_quotient(rows)
    vectors = set()
    zero_rows = 0
    for quad in combinations(range(N), 4):
        for kind in ("K1_diag_gt_sides", "K2_diag_gt_other"):
            vector = tuple(kalmanson_row(quotient, kind, quad).vector)
            if any(vector):
                vectors.add(vector)
            else:
                zero_rows += 1
    matrix = np.array(sorted(vectors), dtype=float)
    count, classes = matrix.shape
    zero_sum = linprog(
        c=np.zeros(count),
        A_eq=np.vstack([matrix.T, np.ones((1, count))]),
        b_eq=np.concatenate([np.zeros(classes), [1.0]]),
        bounds=[(0, None)] * count,
        method="highs",
    )
    nonpositive = linprog(
        c=np.zeros(count),
        A_ub=matrix.T,
        b_ub=np.zeros(classes),
        A_eq=np.ones((1, count)),
        b_eq=[1.0],
        bounds=[(0, None)] * count,
        method="highs",
    )
    return {
        "distance_classes": quotient.class_count,
        "distinct_nonzero_strict_rows": count,
        "zero_rows": zero_rows,
        "zero_sum_lp_feasible": zero_sum.status == 0,
        "nonpositive_lp_feasible": nonpositive.status == 0,
        "solver": "scipy linprog (HiGHS); solver diagnostic only",
    }


def build_payload() -> dict[str, Any]:
    rows = s12a_rows()
    order = list(range(N))
    vertex_circle = vertex_circle_order_obstruction(rows, order)
    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "provenance": PROVENANCE,
        "n": N,
        "cyclic_order": order,
        "rows": [list(row) for row in rows],
        "structure": (
            "circulant with parity: even centers use offsets {1, 2, 10, 11}; "
            "odd centers use offsets {2, 5, 7, 10}"
        ),
        "superseded_by": {
            "artifact": (
                "data/certificates/s12a_equilateral_ear_obstruction.json"
            ),
            "checker": "scripts/check_s12a_equilateral_ears.py",
            "reason": "six forced equilateral ears exceed the exterior-turn budget",
        },
        "incidence": incidence_diagnostics(rows),
        "vertex_circle_obstructed": vertex_circle.obstructed,
        "kalmanson_full_cone_natural_order": kalmanson_diagnostics(rows),
        "value_row_layers": {
            name: solve_layers(order, rows, layers)
            for name, layers in (
                ("N", ""),
                ("S", "S"),
                ("OD", "OD"),
                ("ODS", "ODS"),
            )
        },
        "non_claims": [
            "not a counterexample to Erdos Problem #97",
            "not a Euclidean realizability claim",
            "not an all-order classification",
            "not a live frontier lead",
            "no change to the official/global falsifiable/open status",
        ],
    }
    return payload


def assert_expected(payload: dict[str, Any]) -> list[str]:
    errors = []
    incidence = payload["incidence"]
    kalmanson = payload["kalmanson_full_cone_natural_order"]
    checks = (
        ("row_pair_intersection_max", incidence, 2),
        ("witness_pair_capacity_violations", incidence, 0),
        ("two_overlap_crossing_violations", incidence, 0),
        ("distance_classes", kalmanson, EXPECTED_DISTANCE_CLASSES),
        ("distinct_nonzero_strict_rows", kalmanson, EXPECTED_STRICT_ROWS),
        ("zero_rows", kalmanson, 0),
        ("zero_sum_lp_feasible", kalmanson, False),
        ("nonpositive_lp_feasible", kalmanson, False),
    )
    for key, section, want in checks:
        got = section.get(key)
        if got != want:
            errors.append(f"{key} = {got!r}, expected {want!r}")
    if payload["vertex_circle_obstructed"] is not False:
        errors.append("vertex-circle filter unexpectedly obstructed S12A")
    if payload["value_row_layers"] != EXPECTED_VALUE_ROW_LAYERS:
        errors.append(
            f"value-row layers {payload['value_row_layers']!r}, expected "
            f"{EXPECTED_VALUE_ROW_LAYERS!r}"
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true",
        help="recompute and write the artifact JSON",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="recompute and compare against the stored artifact",
    )
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    payload = build_payload()

    if args.write:
        OUT.write_text(
            json.dumps(payload, indent=1) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"wrote {OUT.relative_to(ROOT)}")
    if args.check:
        stored = json.loads(OUT.read_text())
        if stored != payload:
            keys = sorted(
                key
                for key in set(stored) | set(payload)
                if stored.get(key) != payload.get(key)
            )
            print(f"stored artifact mismatch in: {', '.join(keys)}")
            return 1
        print("stored artifact matches recomputation")
    if args.assert_expected:
        errors = assert_expected(payload)
        if errors:
            for line in errors:
                print(f"UNEXPECTED: {line}")
            return 1
        print("expected S12A frontier diagnostics confirmed")
    if args.json or not (args.write or args.check or args.assert_expected):
        summary = {
            "incidence": payload["incidence"],
            "vertex_circle_obstructed": payload["vertex_circle_obstructed"],
            "kalmanson": payload["kalmanson_full_cone_natural_order"],
            "value_row_layers": payload["value_row_layers"],
        }
        print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
