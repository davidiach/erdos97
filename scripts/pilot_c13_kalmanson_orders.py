#!/usr/bin/env python3
"""Bounded C13 Kalmanson fixed-order pilot.

This is a deliberately small pilot for the later C13 all-order program. It
normalizes a pinned list of cyclic orders, removes dihedral duplicates, and
tries to exactify a positive-integer Kalmanson/Farkas certificate for each
remaining fixed order.

The output is not an exhaustive cyclic-order search.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from check_kalmanson_certificate import check_certificate_dict
from find_kalmanson_certificate import find_certificate

PATTERN_NAME = "C13_sidon_1_2_4_10"
N = 13
OFFSETS = [1, 2, 4, 10]


@dataclass(frozen=True)
class PilotOrder:
    label: str
    order: tuple[int, ...]
    source: str


PILOT_ORDERS = (
    PilotOrder(
        "natural",
        tuple(range(N)),
        "natural cyclic order; already killed by Altman, included as a Kalmanson smoke test",
    ),
    PilotOrder(
        "registered_sparse_survivor",
        (5, 0, 10, 8, 9, 7, 4, 6, 2, 11, 12, 3, 1),
        "registered non-natural sparse-frontier survivor order",
    ),
    PilotOrder(
        "deterministic_probe_0",
        (0, 3, 10, 12, 2, 8, 6, 5, 11, 9, 7, 1, 4),
        "fixed non-natural probe sampled before this pilot and pinned here",
    ),
    PilotOrder(
        "deterministic_probe_1",
        (0, 10, 3, 7, 8, 4, 2, 6, 9, 5, 12, 1, 11),
        "fixed non-natural probe sampled before this pilot and pinned here",
    ),
    PilotOrder(
        "deterministic_probe_2",
        (0, 5, 1, 7, 4, 9, 11, 2, 3, 6, 8, 10, 12),
        "fixed non-natural probe sampled before this pilot and pinned here",
    ),
    PilotOrder(
        "deterministic_probe_3",
        (0, 2, 6, 3, 1, 9, 8, 7, 4, 12, 5, 10, 11),
        "fixed non-natural probe sampled before this pilot and pinned here",
    ),
    PilotOrder(
        "deterministic_probe_4",
        (0, 2, 10, 1, 6, 4, 5, 3, 11, 7, 9, 12, 8),
        "fixed non-natural probe sampled before this pilot and pinned here",
    ),
)


def canonical_dihedral_order(order: Sequence[int]) -> tuple[int, ...]:
    """Return the rotation/reflection canonical representative with label 0 first."""

    order = tuple(int(label) for label in order)
    if sorted(order) != list(range(N)):
        raise ValueError(f"order is not a permutation of 0..{N - 1}: {order}")
    zero = order.index(0)
    rotated = order[zero:] + order[:zero]
    reflected = (rotated[0],) + tuple(reversed(rotated[1:]))
    return min(rotated, reflected)


def summarize_certificate(cert: Mapping[str, object]) -> dict[str, object]:
    result = check_certificate_dict(cert)
    return {
        "status": result.status,
        "positive_inequalities": result.positive_inequalities,
        "distance_classes_after_selected_equalities": (
            result.distance_classes_after_selected_equalities
        ),
        "weight_sum": result.weight_sum,
        "max_weight": result.max_weight,
        "zero_sum_verified": result.zero_sum_verified,
        "claim_strength": result.claim_strength,
    }


def run_pilot(*, include_certificates: bool, tol: float) -> dict[str, object]:
    seen: dict[tuple[int, ...], str] = {}
    cases: list[dict[str, object]] = []
    duplicate_labels: list[dict[str, object]] = []

    for pilot_order in PILOT_ORDERS:
        canonical = canonical_dihedral_order(pilot_order.order)
        if canonical in seen:
            duplicate_labels.append(
                {
                    "label": pilot_order.label,
                    "duplicate_of": seen[canonical],
                    "canonical_order": list(canonical),
                }
            )
            continue
        seen[canonical] = pilot_order.label
        cert = find_certificate(
            PATTERN_NAME,
            N,
            OFFSETS,
            list(canonical),
            tol,
        )
        case: dict[str, object] = {
            "label": pilot_order.label,
            "source": pilot_order.source,
            "input_order": list(pilot_order.order),
            "canonical_order": list(canonical),
            "dihedral_normalized": tuple(pilot_order.order) != canonical,
            "status": (
                "EXACT_KALMANSON_CERTIFICATE_FOUND"
                if cert is not None
                else "NO_EXACT_KALMANSON_CERTIFICATE_FOUND"
            ),
        }
        if cert is not None:
            case["certificate_summary"] = summarize_certificate(cert)
            if include_certificates:
                case["certificate"] = cert
        cases.append(case)

    closed_count = sum(
        1 for case in cases if case["status"] == "EXACT_KALMANSON_CERTIFICATE_FOUND"
    )
    return {
        "type": "c13_kalmanson_bounded_order_pilot_v1",
        "trust": "EXACT_CERTIFICATE_DIAGNOSTIC",
        "pattern": {
            "name": PATTERN_NAME,
            "n": N,
            "circulant_offsets": OFFSETS,
        },
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This is a bounded fixed-order pilot, not an exhaustive all-order cyclic-order search.",
            "Every closed case was produced by an exact positive-integer Kalmanson/Farkas certificate checked by scripts/check_kalmanson_certificate.py.",
        ],
        "branch_accounting": {
            "raw_order_count": len(PILOT_ORDERS),
            "canonical_unique_order_count": len(cases),
            "dihedral_duplicate_count": len(duplicate_labels),
            "closed_by_kalmanson_certificate_count": closed_count,
            "unclosed_order_count": len(cases) - closed_count,
            "exhaustive_all_orders": False,
        },
        "dihedral_duplicates": duplicate_labels,
        "cases": cases,
    }


def assert_expected(data: Mapping[str, object]) -> None:
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise AssertionError("branch_accounting must be an object")
    if accounting["raw_order_count"] != 7:
        raise AssertionError("unexpected raw order count")
    if accounting["canonical_unique_order_count"] != 7:
        raise AssertionError("unexpected unique order count")
    if accounting["closed_by_kalmanson_certificate_count"] != 7:
        raise AssertionError("not all pilot orders closed")
    if accounting["unclosed_order_count"] != 0:
        raise AssertionError("pilot has unclosed orders")

    cases = data["cases"]
    if not isinstance(cases, list):
        raise AssertionError("cases must be a list")
    by_label = {case["label"]: case for case in cases}
    expected_labels = {
        "natural",
        "registered_sparse_survivor",
        "deterministic_probe_0",
        "deterministic_probe_1",
        "deterministic_probe_2",
        "deterministic_probe_3",
        "deterministic_probe_4",
    }
    if set(by_label) != expected_labels:
        raise AssertionError("pilot order labels changed")

    for label in expected_labels:
        case = by_label[label]
        if case["status"] != "EXACT_KALMANSON_CERTIFICATE_FOUND":
            raise AssertionError(f"{label} did not close")
        summary = case["certificate_summary"]
        if not isinstance(summary, Mapping):
            raise AssertionError(f"{label} missing certificate summary")
        if int(summary["positive_inequalities"]) <= 0:
            raise AssertionError(f"{label} has empty certificate support")
        if summary["distance_classes_after_selected_equalities"] != 39:
            raise AssertionError(f"{label} distance class count changed")
        if summary["zero_sum_verified"] is not True:
            raise AssertionError(f"{label} certificate did not verify")


def print_table(data: Mapping[str, object]) -> None:
    cases = data["cases"]
    if not isinstance(cases, list):
        raise TypeError("cases must be a list")
    headers = ["label", "status", "ineq", "classes", "max_weight"]
    rows = []
    for case in cases:
        if not isinstance(case, Mapping):
            raise TypeError("case must be an object")
        summary = case.get("certificate_summary", {})
        rows.append(
            [
                str(case["label"]),
                str(case["status"]),
                str(summary.get("positive_inequalities", "-")),
                str(summary.get("distance_classes_after_selected_equalities", "-")),
                str(summary.get("max_weight", "-")),
            ]
        )
    widths = [
        max(len(headers[col]), *(len(row[col]) for row in rows))
        for col in range(len(headers))
    ]
    print("  ".join(headers[col].ljust(widths[col]) for col in range(len(headers))))
    print("  ".join("-" * widths[col] for col in range(len(headers))))
    for row in rows:
        print("  ".join(row[col].ljust(widths[col]) for col in range(len(headers))))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tol", type=float, default=1e-9, help="LP support threshold")
    parser.add_argument("--out", type=Path, help="write JSON payload to this path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="omit full certificate objects from the output",
    )
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    data = run_pilot(include_certificates=not args.summary_only, tol=args.tol)
    if args.assert_expected:
        assert_expected(data)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_table(data)
        if args.assert_expected:
            print("OK: bounded C13 Kalmanson pilot matched expected closures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
