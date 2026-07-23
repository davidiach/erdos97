#!/usr/bin/env python3
"""Bounded full-Kalmanson-cone CEGAR pilot for the C25/C29 frontier.

Z3 first learns the existing exact clauses that exclude any cyclic order with
a two-inequality inverse-pair certificate.  Whenever a surviving order has a
larger exact Kalmanson/Farkas certificate, the pilot adds one stronger clause:
not all ordered quadrilaterals used by that certificate may occur together.

Every learned clause is exact, but an iteration-limited run is only a bounded
fixed-pattern diagnostic.  It is not a geometric counterexample, an all-order
obstruction, or a proof of Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from z3 import Or, sat, unsat
except ImportError as exc:  # pragma: no cover - optional development dependency
    Or = sat = unsat = None  # type: ignore[assignment]
    Z3_IMPORT_ERROR: ImportError | None = exc
else:
    Z3_IMPORT_ERROR = None


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in (SRC, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_kalmanson_certificate import check_certificate_dict  # noqa: E402
from check_kalmanson_two_order_search import _prepare_vector_tables  # noqa: E402
from check_kalmanson_two_order_z3 import (  # noqa: E402
    _add_clause,
    _clause_key,
    _collect_conflicts,
    _make_solver,
    _order_from_model,
)
from check_sparse_frontier_kalmanson_escapes import check_case  # noqa: E402
from erdos97.altman_diagonal_sums import (  # noqa: E402
    altman_order_linear_certificate,
    altman_order_obstruction,
)
from erdos97.search import built_in_patterns  # noqa: E402
from erdos97.vertex_circle_order_filter import (  # noqa: E402
    vertex_circle_order_obstruction,
)
from find_kalmanson_certificate import find_certificate  # noqa: E402


PATTERNS = {
    "C25_sidon_2_5_9_14": (25, [2, 5, 9, 14]),
    "C29_sidon_1_3_7_15": (29, [1, 3, 7, 15]),
}


def require_z3() -> None:
    if Z3_IMPORT_ERROR is not None:
        raise RuntimeError("z3-solver is required for this pilot") from Z3_IMPORT_ERROR


def certificate_order_quads(
    certificate: Mapping[str, object], order: Sequence[int]
) -> list[tuple[int, int, int, int]]:
    """Return unique certificate quadrilaterals, validating their order."""

    if certificate.get("cyclic_order") != list(order):
        raise AssertionError("certificate order does not match the CEGAR model")
    positions = {label: index for index, label in enumerate(order)}
    quads: set[tuple[int, int, int, int]] = set()
    inequalities = certificate.get("inequalities")
    if not isinstance(inequalities, list) or not inequalities:
        raise AssertionError("certificate must contain positive inequalities")
    for inequality in inequalities:
        if not isinstance(inequality, Mapping):
            raise AssertionError("certificate inequality must be an object")
        quad_raw = inequality.get("quad")
        if not isinstance(quad_raw, list) or len(quad_raw) != 4:
            raise AssertionError(f"invalid certificate quadrilateral: {quad_raw!r}")
        quad = tuple(int(label) for label in quad_raw)
        if len(set(quad)) != 4:
            raise AssertionError(f"repeated label in quadrilateral: {quad!r}")
        indices = [positions[label] for label in quad]
        if indices != sorted(indices):
            raise AssertionError(f"quadrilateral is not ordered in model: {quad!r}")
        quads.add(quad)
    return sorted(quads)


def add_full_certificate_clause(
    solver: object,
    positions: Sequence[object],
    quads: Sequence[tuple[int, int, int, int]],
) -> None:
    """Forbid every supplied ordered quadrilateral from co-occurring."""

    require_z3()
    assert Or is not None
    if not quads:
        raise ValueError("a full-certificate clause needs at least one quadrilateral")
    violations = []
    for a, b, c, d in quads:
        violations.extend(
            (positions[a] > positions[b], positions[b] > positions[c], positions[c] > positions[d])
        )
    solver.add(Or(*violations))


def lightweight_summary(name: str, order: list[int]) -> dict[str, object]:
    pattern = built_in_patterns()[name]
    vertex = vertex_circle_order_obstruction(pattern.S, order, name)
    signature = altman_order_obstruction(pattern.S, order, name)
    linear = altman_order_linear_certificate(pattern.S, order, name)
    survives = bool(
        not vertex.obstructed
        and not signature.altman_contradiction
        and linear.obstructed is False
    )
    return {
        "survives": survives,
        "vertex_circle_obstructed": vertex.obstructed,
        "altman_signature_obstructed": signature.altman_contradiction,
        "altman_linear_obstructed": linear.obstructed,
        "altman_linear_method": linear.certificate_method,
    }


def inverse_pair_audit(
    name: str, n: int, offsets: Sequence[int], order: Sequence[int]
) -> dict[str, object]:
    case = {
        "case": f"{name}:full_cone_cegar_model",
        "pattern": name,
        "n": n,
        "order": list(order),
    }
    result = check_case(case)
    if result.offsets != list(offsets):
        raise AssertionError("independent inverse-pair audit offsets disagree")
    return {
        "status": result.status,
        "full_kalmanson_rows_seen": result.full_kalmanson_rows_seen,
        "inverse_pair_conflicts": result.inverse_pair_conflicts,
    }


def run_pattern(
    name: str,
    *,
    full_certificate_limit: int,
    max_iterations: int,
    conflict_cap: int,
    random_seed: int,
) -> dict[str, object]:
    n, offsets = PATTERNS[name]
    quad_ids, inverse_id = _prepare_vector_tables(n, offsets)
    solver, positions = _make_solver(n, random_seed)
    inverse_clauses: set[tuple[tuple[int, int, int, int], tuple[int, int, int, int]]] = set()
    cases = []
    full_clause_count = 0
    solver_result = "iteration_limit"
    status = "BOUNDED_FULL_CONE_CEGAR_ITERATION_LIMIT"
    iterations = 0

    for iteration in range(1, max_iterations + 1):
        iterations = iteration
        result = solver.check()
        if result == unsat:
            solver_result = "unsat"
            status = "EXACT_ALL_ORDER_FULL_KALMANSON_CONE_OBSTRUCTION"
            break
        if result != sat:
            solver_result = str(result)
            status = "UNKNOWN_SMT_RESULT"
            break

        order = _order_from_model(solver.model(), positions, n)
        conflicts = _collect_conflicts(order, quad_ids, inverse_id, conflict_cap)
        if conflicts:
            for conflict in conflicts:
                clause = _clause_key(conflict.left_quad, conflict.right_quad)
                if clause not in inverse_clauses:
                    inverse_clauses.add(clause)
                    _add_clause(solver, positions, clause)
            continue

        certificate = find_certificate(name, n, offsets, order, 1.0e-9)
        if certificate is None:
            solver_result = "sat"
            status = "NO_EXACT_FULL_CONE_CERTIFICATE_FOUND_FOR_MODEL"
            cases.append(
                {
                    "model_index": len(cases),
                    "z3_iteration": iteration,
                    "order": order,
                    "lightweight_filters": lightweight_summary(name, order),
                    "inverse_pair_audit": inverse_pair_audit(name, n, offsets, order),
                    "full_kalmanson": {
                        "status": "NO_EXACT_FIXED_ORDER_CERTIFICATE_FOUND"
                    },
                }
            )
            break

        checked = check_certificate_dict(certificate)
        if not checked.zero_sum_verified:
            raise AssertionError("generated full-cone certificate did not verify")
        quads = certificate_order_quads(certificate, order)
        add_full_certificate_clause(solver, positions, quads)
        full_clause_count += 1
        cases.append(
            {
                "model_index": len(cases),
                "z3_iteration": iteration,
                "inverse_clause_count_at_discovery": len(inverse_clauses),
                "order": order,
                "lightweight_filters": lightweight_summary(name, order),
                "inverse_pair_audit": inverse_pair_audit(name, n, offsets, order),
                "full_kalmanson": {
                    "status": checked.status,
                    "positive_inequalities": checked.positive_inequalities,
                    "unique_ordered_quad_count": len(quads),
                    "weight_sum": checked.weight_sum,
                    "max_weight": checked.max_weight,
                    "zero_sum_verified": checked.zero_sum_verified,
                    "certificate": certificate,
                },
            }
        )
        if full_clause_count >= full_certificate_limit:
            solver_result = "bounded_after_sat_models"
            status = "BOUNDED_FULL_CONE_CERTIFICATE_LIMIT_REACHED"
            break

    return {
        "pattern": name,
        "n": n,
        "circulant_offsets": offsets,
        "status": status,
        "solver_result": solver_result,
        "iterations": iterations,
        "random_seed": random_seed,
        "conflict_cap": conflict_cap,
        "inverse_pair_clause_count": len(inverse_clauses),
        "full_certificate_clause_count": full_clause_count,
        "models": cases,
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    names = args.pattern or list(PATTERNS)
    runs = [
        run_pattern(
            name,
            full_certificate_limit=args.full_certificate_limit,
            max_iterations=args.max_iterations,
            conflict_cap=args.conflict_cap,
            random_seed=args.random_seed,
        )
        for name in names
    ]
    return {
        "type": "sparse_full_kalmanson_cone_order_cegar_v1",
        "trust": "EXACT_CLAUSES_IN_BOUNDED_FIXED_PATTERN_CEGAR",
        "status": "BOUNDED_DIAGNOSTIC_UNLESS_A_RUN_REPORTS_EXACT_UNSAT",
        "claim_scope": (
            "Exact fixed-pattern inverse-pair and full-certificate clauses in a bounded "
            "cyclic-order CEGAR pilot. Certificate-limit results are not all-order "
            "obstructions, geometric realizability results, counterexamples, or a proof "
            "of Erdos Problem #97."
        ),
        "configuration": {
            "full_certificate_limit": args.full_certificate_limit,
            "max_iterations": args.max_iterations,
            "conflict_cap": args.conflict_cap,
            "random_seed": args.random_seed,
        },
        "runs": runs,
    }


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    verified_certificates = 0
    verified_inverse_pair_escapes = 0
    for run in payload.get("runs", []):
        name = str(run["pattern"])
        n, offsets = PATTERNS[name]
        for model in run.get("models", []):
            order = [int(label) for label in model["order"]]
            audit = inverse_pair_audit(name, n, offsets, order)
            if audit["inverse_pair_conflicts"] != 0:
                raise AssertionError(f"{name} stored model has an inverse-pair conflict")
            verified_inverse_pair_escapes += 1
            full = model["full_kalmanson"]
            certificate = full.get("certificate")
            if certificate is None:
                continue
            checked = check_certificate_dict(certificate)
            if not checked.zero_sum_verified:
                raise AssertionError(f"{name} full-cone certificate did not verify")
            quads = certificate_order_quads(certificate, order)
            if len(quads) != int(full["unique_ordered_quad_count"]):
                raise AssertionError(f"{name} full-clause width drifted")
            verified_certificates += 1
    return {
        "status": "OK",
        "verified_inverse_pair_escape_orders": verified_inverse_pair_escapes,
        "verified_exact_full_cone_certificates": verified_certificates,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", action="append", choices=sorted(PATTERNS))
    parser.add_argument("--full-certificate-limit", type=int, default=3)
    parser.add_argument("--max-iterations", type=int, default=2000)
    parser.add_argument("--conflict-cap", type=int, default=1024)
    parser.add_argument("--random-seed", type=int, default=7)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.full_certificate_limit <= 0 or args.max_iterations <= 0 or args.conflict_cap <= 0:
        raise SystemExit("limits and conflict cap must be positive")
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
            print(
                f"{run['pattern']}: status={run['status']} iterations={run['iterations']} "
                f"inverse_clauses={run['inverse_pair_clause_count']} "
                f"full_clauses={run['full_certificate_clause_count']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
