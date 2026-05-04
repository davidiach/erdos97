#!/usr/bin/env python3
"""Check registered sparse abstract-order survivors against exact filters."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from check_kalmanson_certificate import check_certificate_file  # noqa: E402
from erdos97.altman_diagonal_sums import (  # noqa: E402
    altman_order_linear_certificate,
    altman_order_obstruction,
)
from erdos97.cyclic_crossing_csp import (  # noqa: E402
    all_constraints_cross,
    crossing_constraints,
)
from erdos97.min_radius_filter import (  # noqa: E402
    minimum_radius_order_obstruction,
    radius_propagation_order_obstruction,
)
from erdos97.search import PatternInfo, built_in_patterns  # noqa: E402
from erdos97.sparse_frontier import sparse_frontier_summary  # noqa: E402
from erdos97.vertex_circle_order_filter import vertex_circle_order_obstruction  # noqa: E402

REGISTERED_ORDERS: dict[str, dict[str, list[int]]] = {
    "C13_sidon_1_2_4_10": {
        "sample_full_filter_survivor": [5, 0, 10, 8, 9, 7, 4, 6, 2, 11, 12, 3, 1],
    },
    "C19_skew": {
        "vertex_circle_survivor": [
            18,
            10,
            7,
            17,
            6,
            3,
            5,
            9,
            14,
            11,
            2,
            13,
            4,
            16,
            12,
            15,
            0,
            8,
            1,
        ],
    },
}

KALMANSON_CERTIFICATES: dict[str, Path] = {
    "C13_sidon_1_2_4_10:sample_full_filter_survivor": (
        ROOT
        / "data"
        / "certificates"
        / "c13_sidon_order_survivor_kalmanson_two_unsat.json"
    ),
    "C19_skew:vertex_circle_survivor": (
        ROOT
        / "data"
        / "certificates"
        / "round2"
        / "c19_kalmanson_known_order_two_unsat.json"
    ),
}


def parse_order(raw: str) -> list[int]:
    try:
        return [int(item.strip()) for item in raw.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid comma-separated order: {raw}") from exc


def evaluate_order(
    pattern: PatternInfo,
    order: list[int],
    order_label: str,
) -> dict[str, object]:
    case = f"{pattern.name}:{order_label}"
    constraints = crossing_constraints(pattern.S)
    crossing_ok = all_constraints_cross(order, constraints)
    altman_signature = altman_order_obstruction(pattern.S, order, pattern.name)
    altman_linear = altman_order_linear_certificate(pattern.S, order, pattern.name)
    vertex = vertex_circle_order_obstruction(pattern.S, order, pattern.name)
    min_radius = minimum_radius_order_obstruction(pattern.S, order, pattern.name)
    radius = radius_propagation_order_obstruction(pattern.S, order, pattern.name)
    sparse = sparse_frontier_summary(
        pattern.name,
        pattern.S,
        order=order,
        max_row_examples=0,
    )
    survives_pre_kalmanson = (
        crossing_ok
        and not altman_signature.altman_contradiction
        and altman_linear.obstructed is False
        and not vertex.obstructed
        and not min_radius.obstructed
        and radius.obstructed is False
    )
    kalmanson = kalmanson_status(case, pattern, order)
    survives = survives_pre_kalmanson and not kalmanson["obstructed"]
    return {
        "case": case,
        "pattern": pattern.name,
        "n": pattern.n,
        "order_label": order_label,
        "order": order,
        "survives_pre_kalmanson_filters": survives_pre_kalmanson,
        "survives_current_exact_filters": survives,
        "crossing": {
            "constraint_count": len(constraints),
            "passes": crossing_ok,
        },
        "altman_signature": {
            "status": altman_signature.status,
            "obstructed": altman_signature.altman_contradiction,
            "equal_diagonal_order_groups": (
                altman_signature.equal_diagonal_order_groups
            ),
        },
        "altman_linear_certificate": {
            "status": altman_linear.status,
            "obstructed": altman_linear.obstructed,
            "certificate_method": altman_linear.certificate_method,
            "nonzero_gap_orders": altman_linear.nonzero_gap_orders,
        },
        "vertex_circle": {
            "obstructed": vertex.obstructed,
            "strict_edge_count": vertex.strict_edge_count,
            "self_edge_count": len(vertex.self_edge_conflicts),
            "cycle": bool(vertex.cycle_edges),
        },
        "minimum_radius": {
            "obstructed": min_radius.obstructed,
            "blocked_center_count": len(min_radius.blocked_centers),
            "possible_min_center_count": len(min_radius.possible_min_centers),
        },
        "radius_propagation": {
            "status": radius.status,
            "obstructed": radius.obstructed,
            "nodes_visited": radius.nodes_visited,
            "max_depth": radius.max_depth,
            "acyclic_choice_edge_count": (
                None
                if radius.acyclic_choice is None
                else sum(len(choice.inequality_edges) for choice in radius.acyclic_choice)
            ),
        },
        "kalmanson_certificate": kalmanson,
        "sparse_frontier": {
            "rows_with_uncovered_consecutive_pair": (
                sparse["rows_with_uncovered_consecutive_pair"]
            ),
            "rows_with_uncovered_consecutive_pair_count": len(
                sparse["rows_with_uncovered_consecutive_pair"]
            ),
            "trivial_empty_radius_choice_exists": (
                sparse["trivial_empty_radius_choice_exists"]
            ),
        },
        "semantics": (
            "Fixed-order exact-filter diagnostic only. Surviving all listed "
            "filters is not evidence of geometric realizability."
        ),
    }


def kalmanson_status(
    case: str,
    pattern: PatternInfo,
    order: list[int],
) -> dict[str, object]:
    path = KALMANSON_CERTIFICATES.get(case)
    if path is None:
        return {
            "status": "NO_REGISTERED_KALMANSON_CERTIFICATE",
            "obstructed": False,
        }

    certificate = json.loads(path.read_text(encoding="utf-8"))
    certificate_pattern = certificate.get("pattern", {})
    if not isinstance(certificate_pattern, dict):
        raise ValueError(f"{path} pattern metadata should be an object")
    if certificate_pattern.get("name") != pattern.name:
        raise ValueError(f"{path} pattern {certificate_pattern.get('name')} does not match {pattern.name}")
    if certificate_pattern.get("n") != pattern.n:
        raise ValueError(f"{path} n {certificate_pattern.get('n')} does not match {pattern.n}")
    certificate_offsets = certificate_pattern.get("circulant_offsets")
    if normalize_offsets(certificate_offsets, pattern.n) != circulant_offsets(pattern):
        raise ValueError(f"{path} circulant offsets do not match registered {case}")
    if certificate.get("cyclic_order") != order:
        raise ValueError(f"{path} cyclic order does not match registered {case}")

    result = check_certificate_file(path)
    return {
        "status": result.status,
        "obstructed": result.zero_sum_verified,
        "path": path.relative_to(ROOT).as_posix(),
        "positive_inequalities": result.positive_inequalities,
        "distance_classes_after_selected_equalities": (
            result.distance_classes_after_selected_equalities
        ),
        "weight_sum": result.weight_sum,
        "max_weight": result.max_weight,
        "claim_strength": result.claim_strength,
    }


def circulant_offsets(pattern: PatternInfo) -> list[int]:
    row0 = sorted(int(witness) % pattern.n for witness in pattern.S[0])
    for center, witnesses in enumerate(pattern.S):
        offsets = sorted((int(witness) - center) % pattern.n for witness in witnesses)
        if offsets != row0:
            raise ValueError(f"{pattern.name} is not a circulant row pattern")
    return row0


def normalize_offsets(raw_offsets: object, n: int) -> list[int]:
    if not isinstance(raw_offsets, list):
        raise ValueError("circulant_offsets should be a list")
    return sorted(int(offset) % n for offset in raw_offsets)


def registered_rows(patterns: dict[str, PatternInfo]) -> list[dict[str, object]]:
    rows = []
    for pattern_name, orders in REGISTERED_ORDERS.items():
        pattern = patterns[pattern_name]
        for order_label, order in orders.items():
            rows.append(evaluate_order(pattern, order, order_label))
    return rows


def assert_expected(rows: list[dict[str, object]]) -> None:
    by_case = {str(row["case"]): row for row in rows}
    expected = {
        "C13_sidon_1_2_4_10:sample_full_filter_survivor",
        "C19_skew:vertex_circle_survivor",
    }
    missing = sorted(expected - set(by_case))
    if missing:
        raise AssertionError(f"missing expected case(s): {', '.join(missing)}")
    for case in sorted(expected):
        if by_case[case]["survives_pre_kalmanson_filters"] is not True:
            raise AssertionError(f"{case} did not survive pre-Kalmanson filters")
        kalmanson = by_case[case]["kalmanson_certificate"]
        if not isinstance(kalmanson, dict) or kalmanson["obstructed"] is not True:
            raise AssertionError(f"{case} is missing its Kalmanson obstruction")
        if by_case[case]["survives_current_exact_filters"] is not False:
            raise AssertionError(f"{case} unexpectedly survived current exact filters")


def payload(rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "type": "sparse_order_survivor_filter_sweep_v2",
        "trust": "FIXED_ORDER_EXACT_FILTER_DIAGNOSTIC",
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "The registered C13 and C19 orders survive the older sparse-frontier filters but are killed by fixed-order Kalmanson/Farkas certificates.",
            "A fixed-order Kalmanson obstruction is not an abstract all-order obstruction.",
        ],
        "cases": rows,
    }


def print_table(rows: list[dict[str, object]]) -> None:
    headers = [
        "case",
        "n",
        "survives",
        "kalmanson",
        "vertex",
        "altman",
        "radius",
        "empty rows",
    ]
    table = [
        [
            str(row["case"]),
            str(row["n"]),
            str(row["survives_current_exact_filters"]),
            str(row["kalmanson_certificate"]["obstructed"]),
            str(row["vertex_circle"]["obstructed"]),
            str(row["altman_linear_certificate"]["status"]),
            str(row["radius_propagation"]["status"]),
            str(row["sparse_frontier"]["rows_with_uncovered_consecutive_pair_count"]),
        ]
        for row in rows
    ]
    widths = [
        max(len(headers[col]), *(len(row[col]) for row in table))
        for col in range(len(headers))
    ]
    print("  ".join(headers[col].ljust(widths[col]) for col in range(len(headers))))
    print("  ".join("-" * widths[col] for col in range(len(headers))))
    for row in table:
        print("  ".join(row[col].ljust(widths[col]) for col in range(len(headers))))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--out", help="write JSON payload to this path")
    parser.add_argument("--pattern", help="built-in pattern name for a supplied --order")
    parser.add_argument("--order", type=parse_order, help="comma-separated cyclic order")
    parser.add_argument("--order-label", default="supplied", help="label for --order")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    patterns = built_in_patterns()
    if args.order is not None:
        if not args.pattern:
            raise SystemExit("--pattern is required with --order")
        if args.pattern not in patterns:
            raise SystemExit(f"unknown pattern {args.pattern}; known: {', '.join(patterns)}")
        rows = [
            evaluate_order(
                patterns[args.pattern],
                args.order,
                args.order_label,
            )
        ]
    else:
        if args.pattern:
            raise SystemExit("--pattern requires --order")
        rows = registered_rows(patterns)

    if args.assert_expected:
        assert_expected(rows)
    data = payload(rows)
    if args.out:
        with Path(args.out).open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_table(rows)
        if args.assert_expected:
            print("OK: sparse order survivor expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
