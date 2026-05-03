#!/usr/bin/env python3
"""Find a fixed-order Kalmanson/Farkas certificate by LP and exactification.

The search is deliberately fixed-pattern and fixed-order.  A found certificate
proves only that selected-distance equalities for the supplied circulant
pattern are inconsistent with the supplied cyclic order and strict convex
Kalmanson distance inequalities.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path
from typing import NamedTuple, Sequence

import numpy as np
import sympy as sp
from scipy.optimize import linprog

from check_kalmanson_certificate import (
    build_distance_classes,
    check_certificate_dict,
    inequality_terms,
)


KINDS = ("K1_diag_gt_sides", "K2_diag_gt_other")


class InequalityRow(NamedTuple):
    kind: str
    quad: tuple[int, int, int, int]
    vector: tuple[int, ...]


def parse_int_list(raw: str) -> list[int]:
    try:
        return [int(item.strip()) for item in raw.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid comma-separated integer list: {raw}") from exc


def all_kalmanson_rows(
    n: int,
    offsets: Sequence[int],
    order: Sequence[int],
) -> list[InequalityRow]:
    classes = build_distance_classes(n, offsets)
    class_count = len(set(classes.values()))
    rows: list[InequalityRow] = []
    for quad in itertools.combinations(order, 4):
        for kind in KINDS:
            vector = [0] * class_count
            for pair, coeff in inequality_terms(kind, quad):
                vector[classes[pair]] += coeff
            rows.append(InequalityRow(kind, tuple(int(v) for v in quad), tuple(vector)))
    return rows


def lp_support(rows: Sequence[InequalityRow], tol: float) -> list[int] | None:
    matrix = np.array([row.vector for row in rows], dtype=float)
    class_count = matrix.shape[1]
    a_eq = np.vstack([matrix.T, np.ones((1, len(rows)))])
    b_eq = np.zeros(class_count + 1)
    b_eq[-1] = 1.0
    result = linprog(
        np.zeros(len(rows)),
        A_eq=a_eq,
        b_eq=b_eq,
        bounds=(0, None),
        method="highs",
    )
    if not result.success:
        return None
    return [idx for idx, weight in enumerate(result.x) if weight > tol]


def exact_positive_weights(
    rows: Sequence[InequalityRow],
    support: Sequence[int],
) -> list[int] | None:
    if not support:
        return None
    class_count = len(rows[0].vector)
    matrix = sp.Matrix([[rows[idx].vector[col] for idx in support] for col in range(class_count)])
    nullspace = matrix.nullspace()
    if len(nullspace) != 1:
        return None
    vector = nullspace[0]
    if all(value < 0 for value in vector):
        vector = -vector
    if not all(value > 0 for value in vector):
        return None

    denominator_lcm = 1
    for value in vector:
        denominator_lcm = int(sp.lcm(denominator_lcm, value.q))
    weights = [int(value * denominator_lcm) for value in vector]
    divisor = 0
    for weight in weights:
        divisor = math.gcd(divisor, abs(weight))
    return [weight // divisor for weight in weights]


def certificate_payload(
    name: str,
    n: int,
    offsets: Sequence[int],
    order: Sequence[int],
    rows: Sequence[InequalityRow],
    support: Sequence[int],
    weights: Sequence[int],
) -> dict[str, object]:
    inequalities = [
        {
            "weight": int(weight),
            "quad": list(rows[idx].quad),
            "kind": rows[idx].kind,
        }
        for idx, weight in zip(support, weights)
    ]
    return {
        "certificate_type": "kalmanson_strict_inequality_farkas",
        "status": "EXACT_OBSTRUCTION_FOR_FIXED_PATTERN_AND_FIXED_CYCLIC_ORDER",
        "pattern": {
            "name": name,
            "n": n,
            "circulant_offsets": [int(offset) for offset in offsets],
        },
        "cyclic_order": [int(label) for label in order],
        "selected_witness_rule": "S_i={(i+d) mod n: d in circulant_offsets}",
        "distance_equalities": (
            "for each row i, all distances d(i,w), w in S_i, are identified"
        ),
        "inequality_lemma": (
            "for every convex quadrilateral a,b,c,d in cyclic order, "
            "d(a,c)+d(b,d)>d(a,b)+d(c,d) and "
            "d(a,c)+d(b,d)>d(a,d)+d(b,c)"
        ),
        "certificate_logic": (
            "the listed positive integer combination of Kalmanson strict "
            "inequalities has zero total coefficient after quotienting by "
            "selected-distance equalities, giving 0 > 0"
        ),
        "num_inequalities": len(inequalities),
        "weight_sum": int(sum(weights)),
        "inequalities": inequalities,
        "claim_strength": (
            "Exact obstruction for this fixed selected-witness pattern and "
            "fixed cyclic order only; not an abstract all-order obstruction."
        ),
    }


def find_certificate(
    name: str,
    n: int,
    offsets: Sequence[int],
    order: Sequence[int],
    tol: float,
) -> dict[str, object] | None:
    if sorted(order) != list(range(n)):
        raise ValueError("cyclic order must be a permutation of 0..n-1")
    rows = all_kalmanson_rows(n, offsets, order)
    support = lp_support(rows, tol)
    if support is None:
        return None
    weights = exact_positive_weights(rows, support)
    if weights is None:
        return None
    cert = certificate_payload(name, n, offsets, order, rows, support, weights)
    check_certificate_dict(cert)
    return cert


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="pattern name for the certificate")
    parser.add_argument("--n", required=True, type=int)
    parser.add_argument("--offsets", required=True, type=parse_int_list)
    parser.add_argument("--order", required=True, type=parse_int_list)
    parser.add_argument("--out", type=Path, help="optional certificate output path")
    parser.add_argument("--tol", type=float, default=1e-9, help="LP support threshold")
    parser.add_argument("--assert-found", action="store_true")
    parser.add_argument("--summary-json", action="store_true")
    args = parser.parse_args()

    cert = find_certificate(args.name, args.n, args.offsets, args.order, args.tol)
    if cert is None:
        summary = {
            "status": "NO_EXACT_KALMANSON_CERTIFICATE_FOUND",
            "pattern": args.name,
            "n": args.n,
        }
        if args.summary_json:
            print(json.dumps(summary, indent=2, sort_keys=True))
        elif args.assert_found:
            print("no exact Kalmanson certificate found")
        return 1 if args.assert_found else 0

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = check_certificate_dict(cert)._asdict()
    if args.summary_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            "found exact Kalmanson certificate "
            f"for {summary['pattern']} with {summary['positive_inequalities']} inequalities"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
