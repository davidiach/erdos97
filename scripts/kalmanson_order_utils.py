"""Lightweight helpers for Kalmanson order/certificate scripts."""

from __future__ import annotations

import argparse
import itertools
from typing import NamedTuple, Sequence

from check_kalmanson_certificate import build_distance_classes, inequality_terms


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
