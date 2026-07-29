#!/usr/bin/env python3
"""Full-cone screen for the 63 fresh C25/C29 lightweight survivors.

Each fixed order is classified by Gordan's theorem of alternatives.  The
checker accepts a conclusive classification only when it can replay either:

* an exact positive integer zero-sum certificate over all fixed-order
  Kalmanson rows; or
* an exact integer separating potential having positive dot product with
  every row, proving that no nonzero nonnegative zero sum exists for that row
  family and fixed order.

Numerical LP feasibility or infeasibility is never promoted by itself.  All
results remain bounded fixed-pattern, fixed-order diagnostics rather than
geometric realizability results, counterexamples, or a proof of Erdos
Problem #97.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.optimize import linprog


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
EXPLORATION = Path(__file__).resolve().parent
for path in (SCRIPTS, EXPLORATION):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_kalmanson_certificate import check_certificate_dict  # noqa: E402
from compress_sparse_full_cone_certificates import (  # noqa: E402
    exact_certificate_for_support,
    positive_circuit_audit,
    random_lp_support,
)
from find_kalmanson_certificate import lp_support  # noqa: E402
from kalmanson_order_utils import (  # noqa: E402
    InequalityRow,
    all_kalmanson_rows,
)
from pilot_sparse_full_cone_order_cegar import (  # noqa: E402
    PATTERNS,
    certificate_order_quads,
)
from run_sparse_full_cone_seeded_cegar import file_sha256  # noqa: E402


DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_small_template_fresh_stream_2026-07-30"
    / "summary.json"
)


def stable_json_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def selected_survivors(
    payload: Mapping[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    selected: dict[str, list[dict[str, Any]]] = {}
    for run in payload["runs"]:
        name = str(run["pattern"])
        models = [
            model
            for model in run["fresh_stream"]["models"]
            if bool(model["lightweight_filters"]["survives"])
        ]
        selected[name] = models
    return selected


def integer_primitive(values: Sequence[int]) -> list[int]:
    divisor = 0
    for value in values:
        divisor = math.gcd(divisor, abs(int(value)))
    if divisor == 0:
        return [int(value) for value in values]
    return [int(value) // divisor for value in values]


def rationalize_vector(
    values: Sequence[float],
    *,
    max_denominator: int,
) -> list[int]:
    fractions = [
        Fraction(float(value)).limit_denominator(max_denominator) for value in values
    ]
    denominator_lcm = 1
    for value in fractions:
        denominator_lcm = math.lcm(denominator_lcm, value.denominator)
    integers = [
        value.numerator * (denominator_lcm // value.denominator) for value in fractions
    ]
    return integer_primitive(integers)


def separator_audit(
    rows: Sequence[InequalityRow],
    potential: Sequence[int],
) -> dict[str, object]:
    if not rows:
        raise ValueError("separator audit requires at least one row")
    class_count = len(rows[0].vector)
    if len(potential) != class_count:
        raise ValueError("separator dimension does not match row vectors")
    dots = [
        sum(
            int(coefficient) * int(weight)
            for coefficient, weight in zip(row.vector, potential, strict=True)
        )
        for row in rows
    ]
    minimum = min(dots)
    return {
        "distance_class_count": class_count,
        "strict_row_count": len(rows),
        "minimum_row_dot": minimum,
        "maximum_row_dot": max(dots),
        "minimum_dot_row_count": sum(value == minimum for value in dots),
        "all_row_dots_strictly_positive": minimum > 0,
        "potential_nonzero_count": sum(int(value) != 0 for value in potential),
        "potential_max_abs": max(abs(int(value)) for value in potential),
    }


def exact_separator(
    rows: Sequence[InequalityRow],
    *,
    max_denominator: int,
) -> tuple[list[int], dict[str, object]] | None:
    matrix = np.asarray([row.vector for row in rows], dtype=float)
    class_count = matrix.shape[1]
    result = linprog(
        np.zeros(class_count),
        A_ub=-matrix,
        b_ub=-np.ones(len(rows)),
        bounds=[(None, None)] * class_count,
        method="highs",
    )
    if not result.success:
        return None
    potential = rationalize_vector(
        result.x,
        max_denominator=max_denominator,
    )
    audit = separator_audit(rows, potential)
    if not bool(audit["all_row_dots_strictly_positive"]):
        return None
    return potential, audit


def equality_system(
    rows: Sequence[InequalityRow],
) -> tuple[np.ndarray, np.ndarray]:
    matrix = np.asarray([row.vector for row in rows], dtype=float)
    equality_matrix = np.vstack([matrix.T, np.ones((1, len(rows)))])
    equality_rhs = np.zeros(matrix.shape[1] + 1)
    equality_rhs[-1] = 1.0
    return equality_matrix, equality_rhs


def exact_positive_certificate(
    name: str,
    n: int,
    offsets: Sequence[int],
    order: Sequence[int],
    rows: Sequence[InequalityRow],
    *,
    tolerance: float,
    retry_count: int,
    retry_seed: int,
) -> tuple[dict[str, object] | None, dict[str, object]]:
    support = lp_support(rows, tolerance)
    primary_support_size = len(support) if support is not None else None
    if support is not None:
        certificate = exact_certificate_for_support(
            name,
            n,
            offsets,
            order,
            rows,
            support,
        )
        if certificate is not None:
            return certificate, {
                "primary_numerical_support_size": primary_support_size,
                "exactification_method": "zero_objective_basic_support",
                "retry_index": None,
            }

    equality_matrix, equality_rhs = equality_system(rows)
    for retry_index in range(retry_count):
        retry_support = random_lp_support(
            rows,
            equality_matrix,
            equality_rhs,
            seed=retry_seed + retry_index,
            tolerance=tolerance,
        )
        if retry_support is None:
            continue
        certificate = exact_certificate_for_support(
            name,
            n,
            offsets,
            order,
            rows,
            retry_support,
        )
        if certificate is not None:
            return certificate, {
                "primary_numerical_support_size": primary_support_size,
                "exactification_method": "deterministic_random_objective",
                "retry_index": retry_index,
            }
    return None, {
        "primary_numerical_support_size": primary_support_size,
        "exactification_method": None,
        "retry_index": None,
    }


def classify_order(
    name: str,
    model: Mapping[str, Any],
    *,
    tolerance: float,
    retry_count: int,
    retry_seed: int,
    max_separator_denominator: int,
) -> dict[str, object]:
    n, offsets = PATTERNS[name]
    order = [int(label) for label in model["order"]]
    rows = all_kalmanson_rows(n, offsets, order)
    certificate, search = exact_positive_certificate(
        name,
        n,
        offsets,
        order,
        rows,
        tolerance=tolerance,
        retry_count=retry_count,
        retry_seed=retry_seed,
    )
    base = {
        "fresh_model_index": int(model["fresh_model_index"]),
        "order": order,
        "order_sha256": str(model["order_sha256"]),
        "dihedral_order_sha256": str(model["dihedral_order_sha256"]),
        "strict_row_count": len(rows),
        "distance_class_count": len(rows[0].vector),
        "certificate_search": search,
    }
    if certificate is not None:
        checked = check_certificate_dict(certificate)
        quads = certificate_order_quads(certificate, order)
        circuit_audit = positive_circuit_audit(certificate)
        if not bool(circuit_audit["positive_circuit_verified"]):
            raise AssertionError("full-cone certificate is not a positive circuit")
        return {
            **base,
            "classification": "EXACT_POSITIVE_ZERO_SUM_CERTIFICATE",
            "positive_inequalities": checked.positive_inequalities,
            "unique_ordered_quad_count": len(quads),
            "weight_sum": checked.weight_sum,
            "max_weight": checked.max_weight,
            "positive_circuit_audit": circuit_audit,
            "certificate_sha256": stable_json_sha256(certificate),
            "certificate": certificate,
        }

    separated = exact_separator(
        rows,
        max_denominator=max_separator_denominator,
    )
    if separated is None:
        return {
            **base,
            "classification": "UNRESOLVED_NUMERICAL_SCREEN",
            "reason": (
                "no exact positive circuit or exact integer separating potential "
                "was recovered"
            ),
        }
    potential, audit = separated
    return {
        **base,
        "classification": "EXACT_INTEGER_SEPARATING_POTENTIAL",
        "separating_potential": potential,
        "separator_sha256": stable_json_sha256(potential),
        "separator_audit": audit,
    }


def run_summary(records: Sequence[Mapping[str, Any]]) -> dict[str, object]:
    classifications = Counter(str(record["classification"]) for record in records)
    widths = Counter(
        int(record["unique_ordered_quad_count"])
        for record in records
        if record["classification"] == "EXACT_POSITIVE_ZERO_SUM_CERTIFICATE"
    )
    supports = Counter(
        int(record["positive_inequalities"])
        for record in records
        if record["classification"] == "EXACT_POSITIVE_ZERO_SUM_CERTIFICATE"
    )
    return {
        "selected_fresh_lightweight_survivor_count": len(records),
        "exact_positive_certificate_count": classifications[
            "EXACT_POSITIVE_ZERO_SUM_CERTIFICATE"
        ],
        "exact_separating_potential_count": classifications[
            "EXACT_INTEGER_SEPARATING_POTENTIAL"
        ],
        "unresolved_numerical_screen_count": classifications[
            "UNRESOLVED_NUMERICAL_SCREEN"
        ],
        "classification_histogram": {
            key: classifications[key] for key in sorted(classifications)
        },
        "certificate_unique_quad_count_histogram": {
            str(key): widths[key] for key in sorted(widths)
        },
        "certificate_positive_inequality_count_histogram": {
            str(key): supports[key] for key in sorted(supports)
        },
        "minimum_certificate_unique_quad_count": min(widths, default=None),
        "maximum_certificate_unique_quad_count": max(widths, default=None),
        "minimum_certificate_positive_inequality_count": min(
            supports,
            default=None,
        ),
        "maximum_certificate_positive_inequality_count": max(
            supports,
            default=None,
        ),
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    source = json.loads(source_path.read_text(encoding="utf-8"))
    selected = selected_survivors(source)
    names = args.pattern or list(PATTERNS)
    runs = []
    for pattern_index, name in enumerate(names):
        records = []
        for model in selected[name]:
            model_index = int(model["fresh_model_index"])
            retry_seed = (
                args.retry_seed
                + pattern_index * args.pattern_seed_stride
                + model_index * args.model_seed_stride
            )
            records.append(
                classify_order(
                    name,
                    model,
                    tolerance=args.tolerance,
                    retry_count=args.retry_count,
                    retry_seed=retry_seed,
                    max_separator_denominator=args.max_separator_denominator,
                )
            )
        n, offsets = PATTERNS[name]
        runs.append(
            {
                "pattern": name,
                "n": n,
                "circulant_offsets": offsets,
                "records": records,
                "summary": run_summary(records),
            }
        )
    total_records = [
        record
        for run in runs
        for record in run["records"]  # type: ignore[index]
    ]
    return {
        "type": "sparse_full_cone_fresh_order_screen_v1",
        "trust": "EXACT_FIXED_ORDER_ALTERNATIVE_CERTIFICATES_IN_BOUNDED_PACKET",
        "status": "BOUNDED_FRESH_ORDER_FULL_CONE_CLASSIFICATION",
        "claim_scope": (
            "Exact Gordan-alternative screening of the 63 fresh C25/C29 orders "
            "that survive the stored lightweight filters. Each conclusive record "
            "contains either an exact positive Kalmanson zero-sum certificate or "
            "an exact integer separating potential for that fixed pattern and "
            "fixed order. This does not establish geometric realizability, an "
            "all-order obstruction, a counterexample, a proof of Erdos Problem "
            "#97, or an official/global status update."
        ),
        "source_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_sha256": file_sha256(source_path),
        "configuration": {
            "selection": "fresh orders with lightweight_filters.survives true",
            "tolerance": args.tolerance,
            "retry_count": args.retry_count,
            "retry_seed": args.retry_seed,
            "pattern_seed_stride": args.pattern_seed_stride,
            "model_seed_stride": args.model_seed_stride,
            "max_separator_denominator": args.max_separator_denominator,
        },
        "runs": runs,
        "summary": run_summary(total_records),
    }


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    source_path = ROOT / str(payload["source_artifact"])
    if file_sha256(source_path) != str(payload["source_sha256"]):
        raise AssertionError("fresh-order source artifact hash drifted")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    selected = selected_survivors(source)
    verified_certificates = 0
    verified_separators = 0
    verified_unresolved = 0
    all_records = []

    for run in payload["runs"]:
        name = str(run["pattern"])
        n, offsets = PATTERNS[name]
        source_by_index = {
            int(model["fresh_model_index"]): model for model in selected[name]
        }
        records = run["records"]
        if len(records) != len(source_by_index):
            raise AssertionError(f"{name} selected survivor count drifted")
        seen_indices: set[int] = set()
        for record in records:
            model_index = int(record["fresh_model_index"])
            if model_index in seen_indices or model_index not in source_by_index:
                raise AssertionError(f"{name} invalid fresh model index")
            seen_indices.add(model_index)
            source_model = source_by_index[model_index]
            order = [int(label) for label in record["order"]]
            if order != [int(label) for label in source_model["order"]]:
                raise AssertionError(f"{name} source order drifted")
            for field in ("order_sha256", "dihedral_order_sha256"):
                if record[field] != source_model[field]:
                    raise AssertionError(f"{name} {field} drifted")

            classification = str(record["classification"])
            if classification == "EXACT_POSITIVE_ZERO_SUM_CERTIFICATE":
                certificate = record["certificate"]
                checked = check_certificate_dict(certificate)
                if not checked.zero_sum_verified:
                    raise AssertionError(f"{name} exact certificate failed")
                if stable_json_sha256(certificate) != record["certificate_sha256"]:
                    raise AssertionError(f"{name} certificate hash drifted")
                quads = certificate_order_quads(certificate, order)
                if len(quads) != int(record["unique_ordered_quad_count"]):
                    raise AssertionError(f"{name} certificate width drifted")
                if checked.positive_inequalities != int(
                    record["positive_inequalities"]
                ):
                    raise AssertionError(f"{name} certificate support drifted")
                circuit_audit = positive_circuit_audit(certificate)
                if circuit_audit != record["positive_circuit_audit"]:
                    raise AssertionError(f"{name} circuit audit drifted")
                if not bool(circuit_audit["positive_circuit_verified"]):
                    raise AssertionError(f"{name} certificate is not a circuit")
                verified_certificates += 1
            elif classification == "EXACT_INTEGER_SEPARATING_POTENTIAL":
                rows = all_kalmanson_rows(n, offsets, order)
                potential = [int(value) for value in record["separating_potential"]]
                if stable_json_sha256(potential) != record["separator_sha256"]:
                    raise AssertionError(f"{name} separator hash drifted")
                audit = separator_audit(rows, potential)
                if audit != record["separator_audit"]:
                    raise AssertionError(f"{name} separator audit drifted")
                if not bool(audit["all_row_dots_strictly_positive"]):
                    raise AssertionError(f"{name} separator is not strict")
                verified_separators += 1
            elif classification == "UNRESOLVED_NUMERICAL_SCREEN":
                verified_unresolved += 1
            else:
                raise AssertionError(f"{name} unknown classification")
            all_records.append(record)
        if run["summary"] != run_summary(records):
            raise AssertionError(f"{name} summary drifted")

    if payload["summary"] != run_summary(all_records):
        raise AssertionError("aggregate full-cone summary drifted")
    return {
        "status": "OK",
        "verified_selected_fresh_lightweight_survivors": len(all_records),
        "verified_exact_positive_certificates": verified_certificates,
        "verified_exact_integer_separators": verified_separators,
        "recorded_unresolved_numerical_screens": verified_unresolved,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--pattern", action="append", choices=sorted(PATTERNS))
    parser.add_argument("--tolerance", type=float, default=1.0e-9)
    parser.add_argument("--retry-count", type=int, default=8)
    parser.add_argument("--retry-seed", type=int, default=20260731)
    parser.add_argument("--pattern-seed-stride", type=int, default=100_000)
    parser.add_argument("--model-seed-stride", type=int, default=1_000)
    parser.add_argument("--max-separator-denominator", type=int, default=1_000_000)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    positive = (
        args.tolerance,
        args.retry_count,
        args.pattern_seed_stride,
        args.model_seed_stride,
        args.max_separator_denominator,
    )
    if any(value <= 0 for value in positive):
        raise SystemExit(
            "tolerance, retries, strides, and denominator must be positive"
        )
    if args.check is not None:
        payload = json.loads(args.check.read_text(encoding="utf-8"))
        print(json.dumps(check_payload(payload), indent=2, sort_keys=True))
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
            summary = run["summary"]
            print(
                f"{run['pattern']}: "
                f"selected={summary['selected_fresh_lightweight_survivor_count']} "
                f"certificates={summary['exact_positive_certificate_count']} "
                f"separators={summary['exact_separating_potential_count']} "
                f"unresolved={summary['unresolved_numerical_screen_count']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
