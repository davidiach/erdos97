#!/usr/bin/env python3
"""Scout sparse cyclic orders before a free-Cartesian realization search.

Every fixed order first passes the repository's exact lightweight filters and
then a full fixed-order Kalmanson/Farkas search.  Free coordinates are only
optimized when no exact Kalmanson certificate is found.  A numerical hit is
not a counterexample until exact equality, distinctness, and convexity
certificates are supplied independently.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in (SRC, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_kalmanson_certificate import check_certificate_dict  # noqa: E402
from erdos97.altman_diagonal_sums import (  # noqa: E402
    altman_order_linear_certificate,
    altman_order_obstruction,
)
from erdos97.cyclic_crossing_csp import (  # noqa: E402
    all_constraints_cross,
    crossing_constraints,
)
from erdos97.free_cartesian import (  # noqa: E402
    CartesianConfig,
    search_fixed_order,
)
from erdos97.search import (  # noqa: E402
    PatternInfo,
    built_in_patterns,
    relabel_pattern_by_cyclic_order,
)
from erdos97.vertex_circle_order_filter import (  # noqa: E402
    vertex_circle_order_obstruction,
)
from find_kalmanson_certificate import find_certificate  # noqa: E402


PATTERN_OFFSETS = {
    "C25_sidon_2_5_9_14": [2, 5, 9, 14],
    "C29_sidon_1_3_7_15": [1, 3, 7, 15],
}


def sampled_orders(n: int, count: int, seed: int) -> list[list[int]]:
    if count <= 0:
        raise ValueError("order count must be positive")
    rng = random.Random(seed)
    orders: list[list[int]] = []
    seen: set[tuple[int, ...]] = set()
    while len(orders) < count:
        tail = list(range(1, n))
        rng.shuffle(tail)
        order = [0, *tail]
        key = tuple(order)
        if key not in seen:
            seen.add(key)
            orders.append(order)
    return orders


def lightweight_filter_row(pattern: PatternInfo, order: list[int]) -> dict[str, object]:
    constraints = crossing_constraints(pattern.S)
    crossing_passes = all_constraints_cross(order, constraints)
    vertex = vertex_circle_order_obstruction(pattern.S, order, pattern.name)
    altman_signature = altman_order_obstruction(pattern.S, order, pattern.name)
    altman_linear = altman_order_linear_certificate(pattern.S, order, pattern.name)
    survives = bool(
        crossing_passes
        and not vertex.obstructed
        and not altman_signature.altman_contradiction
        and altman_linear.obstructed is False
    )
    return {
        "survives": survives,
        "crossing": {
            "constraint_count": len(constraints),
            "passes": crossing_passes,
        },
        "vertex_circle": {
            "obstructed": vertex.obstructed,
            "strict_edge_count": vertex.strict_edge_count,
            "self_edge_count": len(vertex.self_edge_conflicts),
            "cycle": bool(vertex.cycle_edges),
        },
        "altman_signature": {
            "status": altman_signature.status,
            "obstructed": altman_signature.altman_contradiction,
        },
        "altman_linear": {
            "status": altman_linear.status,
            "obstructed": altman_linear.obstructed,
            "certificate_method": altman_linear.certificate_method,
        },
    }


def certificate_summary(certificate: dict[str, object]) -> dict[str, object]:
    checked = check_certificate_dict(certificate)
    return {
        "status": checked.status,
        "positive_inequalities": checked.positive_inequalities,
        "distance_classes_after_selected_equalities": (
            checked.distance_classes_after_selected_equalities
        ),
        "weight_sum": checked.weight_sum,
        "max_weight": checked.max_weight,
        "zero_sum_verified": checked.zero_sum_verified,
    }


def run_pattern(
    pattern: PatternInfo,
    *,
    order_count: int,
    seed: int,
    restarts: int,
    max_nfev: int,
    config: CartesianConfig,
) -> dict[str, object]:
    offsets = PATTERN_OFFSETS[pattern.name]
    rows = []
    lightweight_survivors = 0
    exact_kalmanson_obstructions = 0
    coordinate_attempts = 0
    candidates = 0
    for index, order in enumerate(sampled_orders(pattern.n, order_count, seed)):
        filters = lightweight_filter_row(pattern, order)
        row: dict[str, object] = {
            "sample_index": index,
            "order": order,
            "lightweight_filters": filters,
        }
        if bool(filters["survives"]):
            lightweight_survivors += 1
            certificate = find_certificate(
                pattern.name,
                pattern.n,
                offsets,
                order,
                1.0e-9,
            )
            if certificate is not None:
                exact_kalmanson_obstructions += 1
                row["kalmanson"] = {
                    "summary": certificate_summary(certificate),
                    "certificate": certificate,
                }
                row["coordinate_search"] = {
                    "status": "SKIPPED_EXACT_FIXED_ORDER_OBSTRUCTION"
                }
            else:
                coordinate_attempts += 1
                ordered = relabel_pattern_by_cyclic_order(pattern, order)
                report = search_fixed_order(
                    ordered.S,
                    restarts=restarts,
                    max_nfev=max_nfev,
                    seed=seed + 1009 * (index + 1),
                    config=config,
                )
                candidates += int(bool(report["candidate"]))
                row["kalmanson"] = {
                    "summary": {
                        "status": "NO_EXACT_FIXED_ORDER_CERTIFICATE_FOUND"
                    }
                }
                row["coordinate_search"] = {
                    "status": "NUMERICAL_CANDIDATE" if report["candidate"] else "NO_CANDIDATE",
                    "report": report,
                }
        else:
            row["kalmanson"] = {"summary": {"status": "NOT_RUN"}}
            row["coordinate_search"] = {
                "status": "SKIPPED_LIGHTWEIGHT_EXACT_OBSTRUCTION"
            }
        rows.append(row)

    return {
        "pattern": pattern.name,
        "n": pattern.n,
        "circulant_offsets": offsets,
        "seed": seed,
        "order_count": order_count,
        "lightweight_survivors": lightweight_survivors,
        "exact_kalmanson_obstructions": exact_kalmanson_obstructions,
        "coordinate_attempts": coordinate_attempts,
        "numerical_candidates": candidates,
        "orders": rows,
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    patterns = built_in_patterns()
    config = CartesianConfig(
        pair_floor=args.pair_floor,
        side_floor=args.side_floor,
        candidate_tolerance=args.candidate_tolerance,
    )
    names = args.pattern or list(PATTERN_OFFSETS)
    runs = [
        run_pattern(
            patterns[name],
            order_count=args.orders_per_pattern,
            seed=args.seed + patterns[name].n,
            restarts=args.restarts,
            max_nfev=args.max_nfev,
            config=config,
        )
        for name in names
    ]
    return {
        "type": "sparse_free_cartesian_order_preflight_v1",
        "trust": "EXACT_FIXED_ORDER_CERTIFICATES_AND_BOUNDED_NUMERICAL_SEARCH",
        "status": (
            "NUMERICAL_CANDIDATE_REQUIRES_EXACTIFICATION"
            if any(int(run["numerical_candidates"]) for run in runs)
            else "NO_COUNTEREXAMPLE_FOUND_IN_BOUNDED_RUN"
        ),
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed unless a separate exact certificate is supplied.",
            "Each stored Kalmanson certificate is an exact obstruction only for its fixed pattern and fixed cyclic order.",
            "The order sample is deterministic but not exhaustive.",
        ],
        "configuration": {
            "orders_per_pattern": args.orders_per_pattern,
            "seed": args.seed,
            "restarts": args.restarts,
            "max_nfev": args.max_nfev,
            "pair_floor": args.pair_floor,
            "side_floor": args.side_floor,
            "candidate_tolerance": args.candidate_tolerance,
        },
        "runs": runs,
    }


def check_payload(payload: dict[str, Any]) -> dict[str, object]:
    certificate_count = 0
    candidate_count = 0
    for run in payload.get("runs", []):
        for row in run.get("orders", []):
            kalmanson = row.get("kalmanson", {})
            certificate = kalmanson.get("certificate")
            if certificate is not None:
                checked = check_certificate_dict(certificate)
                if not checked.zero_sum_verified:
                    raise AssertionError("stored Kalmanson certificate did not verify")
                if certificate.get("cyclic_order") != row.get("order"):
                    raise AssertionError("certificate cyclic order does not match sample row")
                certificate_count += 1
            coordinate = row.get("coordinate_search", {})
            if coordinate.get("status") == "NUMERICAL_CANDIDATE":
                candidate_count += 1
    expected = sum(int(run["exact_kalmanson_obstructions"]) for run in payload["runs"])
    if certificate_count != expected:
        raise AssertionError(
            f"verified {certificate_count} certificates, expected {expected}"
        )
    return {
        "status": "OK",
        "verified_exact_fixed_order_certificates": certificate_count,
        "numerical_candidates": candidate_count,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", action="append", choices=sorted(PATTERN_OFFSETS))
    parser.add_argument("--orders-per-pattern", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260722)
    parser.add_argument("--restarts", type=int, default=8)
    parser.add_argument("--max-nfev", type=int, default=4000)
    parser.add_argument("--pair-floor", type=float, default=2.0e-3)
    parser.add_argument("--side-floor", type=float, default=2.0e-6)
    parser.add_argument("--candidate-tolerance", type=float, default=1.0e-10)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path, help="verify an existing JSON artifact")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check is not None:
        payload = json.loads(args.check.read_text(encoding="utf-8"))
        result = check_payload(payload)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    payload = build_payload(args)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8", newline="\n")
    if args.json or args.out is None:
        print(text, end="")
    else:
        for run in payload["runs"]:
            print(
                f"{run['pattern']}: orders={run['order_count']} "
                f"lightweight_survivors={run['lightweight_survivors']} "
                f"exact_kalmanson_obstructions={run['exact_kalmanson_obstructions']} "
                f"coordinate_attempts={run['coordinate_attempts']} "
                f"candidates={run['numerical_candidates']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
