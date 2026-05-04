#!/usr/bin/env python3
"""Find a two-inequality Kalmanson/Farkas certificate for one fixed order.

This searches the fixed-order Kalmanson rows for an inverse pair: two strict
Kalmanson inequalities whose coefficient vectors cancel exactly after
quotienting by the selected-distance equalities.  Such a pair gives a tiny
``0 > 0`` certificate with weights ``1, 1``.

The result is still fixed-pattern and fixed-cyclic-order only.  It is not an
all-order obstruction and does not prove Erdos Problem #97.
"""
from __future__ import annotations

import argparse
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
    check_certificate_dict,
)
from kalmanson_order_utils import (  # noqa: E402
    InequalityRow,
    all_kalmanson_rows,
    certificate_payload,
    parse_int_list,
)


def _nonzero_indices(vector: Sequence[int]) -> list[int]:
    return [idx for idx, value in enumerate(vector) if value != 0]


def _class_sizes(n: int, offsets: Sequence[int]) -> dict[int, int]:
    classes = build_distance_classes(n, offsets)
    return dict(Counter(classes.values()))


def _candidate_sort_key(
    pair: tuple[int, int],
    rows: Sequence[InequalityRow],
    sizes: dict[int, int],
) -> tuple[int, int, int, int, int]:
    """Prefer the most local-looking inverse pair, then deterministic order."""

    left, right = pair
    nonzero = _nonzero_indices(rows[left].vector)
    total_class_size = sum(sizes[idx] for idx in nonzero)
    min_class_size = min((sizes[idx] for idx in nonzero), default=0)
    return (len(nonzero), -total_class_size, -min_class_size, left, right)


def inverse_pairs(rows: Sequence[InequalityRow]) -> list[tuple[int, int]]:
    """Return row-index pairs whose coefficient vectors are exact negatives."""

    by_vector: dict[tuple[int, ...], list[int]] = {}
    pairs: list[tuple[int, int]] = []
    for idx, row in enumerate(rows):
        vector = tuple(row.vector)
        negative = tuple(-value for value in vector)
        for left in by_vector.get(negative, []):
            pairs.append((left, idx))
        by_vector.setdefault(vector, []).append(idx)
    return pairs


def find_two_certificate(
    name: str,
    n: int,
    offsets: Sequence[int],
    order: Sequence[int],
) -> tuple[dict[str, object], dict[str, object]] | None:
    """Return a compact certificate and summary, if an inverse pair exists."""

    if sorted(order) != list(range(n)):
        raise ValueError("cyclic order must be a permutation of 0..n-1")
    rows = all_kalmanson_rows(n, offsets, order)
    pairs = inverse_pairs(rows)
    if not pairs:
        return None

    sizes = _class_sizes(n, offsets)
    left, right = min(pairs, key=lambda item: _candidate_sort_key(item, rows, sizes))
    certificate = certificate_payload(
        name=name,
        n=n,
        offsets=offsets,
        order=order,
        rows=rows,
        support=[left, right],
        weights=[1, 1],
    )
    certificate["certificate_variant"] = "kalmanson_two_inequality_inverse_pair"
    certificate["finder"] = "scripts/find_kalmanson_two_certificate.py"
    certificate["support_selection"] = (
        "Among exact inverse row pairs, prefer fewer nonzero distance classes, "
        "then larger selected-distance class support, then deterministic row order."
    )
    check = check_certificate_dict(certificate)
    nonzero = _nonzero_indices(rows[left].vector)
    summary = {
        **check._asdict(),
        "inverse_pair_candidates": len(pairs),
        "selected_support_indices": [left, right],
        "nonzero_distance_class_count": len(nonzero),
        "nonzero_distance_classes": nonzero,
        "nonzero_class_sizes": [sizes[idx] for idx in nonzero],
    }
    return certificate, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="pattern name for the certificate")
    parser.add_argument("--n", required=True, type=int)
    parser.add_argument("--offsets", required=True, type=parse_int_list)
    parser.add_argument("--order", required=True, type=parse_int_list)
    parser.add_argument("--out", type=Path, help="optional certificate output path")
    parser.add_argument("--assert-found", action="store_true")
    parser.add_argument("--summary-json", action="store_true")
    args = parser.parse_args()

    result = find_two_certificate(args.name, args.n, args.offsets, args.order)
    if result is None:
        summary = {
            "status": "NO_TWO_INEQUALITY_KALMANSON_CERTIFICATE_FOUND",
            "pattern": args.name,
            "n": args.n,
        }
        if args.summary_json:
            print(json.dumps(summary, indent=2, sort_keys=True))
        elif args.assert_found:
            print("no two-inequality Kalmanson certificate found")
        return 1 if args.assert_found else 0

    certificate, summary = result
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.summary_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            "found two-inequality Kalmanson certificate "
            f"for {summary['pattern']} using rows "
            f"{summary['selected_support_indices']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
