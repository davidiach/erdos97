#!/usr/bin/env python3
"""Lazy SMT search for Kalmanson two-inequality order obstructions.

For a fixed circulant selected-witness pattern, this script searches for a
cyclic order with no inverse pair of strict Kalmanson inequalities.  It uses a
counterexample-guided loop:

1. Ask Z3 for a cyclic order, represented by integer label positions with
   label 0 fixed at position 0.
2. Check the order with the same inverse-pair predicate used by
   ``check_kalmanson_two_order_search.py``.
3. If an inverse pair is found, add an exact clause forbidding that pair of
   ordered quadrilaterals and repeat.

If the accumulated exact clauses are UNSAT, every cyclic order of this fixed
abstract pattern contains a two-inequality Kalmanson/Farkas obstruction.

This is an all-order statement only for the supplied fixed abstract pattern.
It is not a proof of Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import NamedTuple, Sequence

try:
    from z3 import Distinct, Int, Or, Solver, sat, unsat
except ImportError as exc:  # pragma: no cover - depends on optional dev dep
    raise SystemExit("z3-solver is required for this checker") from exc

ROOT = Path(__file__).resolve().parents[1]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_kalmanson_two_order_search import _prepare_vector_tables  # noqa: E402
from kalmanson_order_utils import parse_int_list  # noqa: E402


Quad = tuple[int, int, int, int]
Clause = tuple[Quad, Quad]


class Conflict(NamedTuple):
    left_kind: int
    left_quad: Quad
    right_kind: int
    right_quad: Quad


def _make_solver(n: int, random_seed: int) -> tuple[Solver, list[object]]:
    positions = [Int(f"p{label}") for label in range(n)]
    solver = Solver()
    solver.set("random_seed", random_seed)
    solver.add(positions[0] == 0)
    solver.add(Distinct(positions))
    for position in positions:
        solver.add(position >= 0, position < n)
    return solver, positions


def _order_from_model(model: object, positions: Sequence[object], n: int) -> list[int]:
    return sorted(range(n), key=lambda label: model[positions[label]].as_long())


def _clause_key(left: Quad, right: Quad) -> Clause:
    return (left, right) if left <= right else (right, left)


def _add_clause(solver: Solver, positions: Sequence[object], clause: Clause) -> None:
    left, right = clause
    solver.add(
        Or(
            positions[left[0]] > positions[left[1]],
            positions[left[1]] > positions[left[2]],
            positions[left[2]] > positions[left[3]],
            positions[right[0]] > positions[right[1]],
            positions[right[1]] > positions[right[2]],
            positions[right[2]] > positions[right[3]],
        )
    )


def _collect_conflicts(
    order: Sequence[int],
    quad_ids: dict[Quad, tuple[int, int]],
    inverse_id: Sequence[int],
    cap: int,
) -> list[Conflict]:
    seen: dict[int, tuple[int, Quad]] = {}
    conflicts: list[Conflict] = []
    for quad_raw in itertools.combinations(order, 4):
        quad = tuple(int(label) for label in quad_raw)
        for kind, vector_id in enumerate(quad_ids[quad]):
            inverse = inverse_id[vector_id]
            if inverse >= 0 and inverse in seen:
                left_kind, left_quad = seen[inverse]
                conflicts.append(Conflict(left_kind, left_quad, kind, quad))
                if len(conflicts) >= cap:
                    return conflicts
            seen.setdefault(vector_id, (kind, quad))
    return conflicts


def _clause_is_valid(
    clause: Clause,
    quad_ids: dict[Quad, tuple[int, int]],
    inverse_id: Sequence[int],
) -> bool:
    left, right = clause
    left_ids = quad_ids[left]
    right_ids = set(quad_ids[right])
    return any(inverse_id[vector_id] in right_ids for vector_id in left_ids)


def _validate_clause(
    clause: Clause,
    n: int,
    quad_ids: dict[Quad, tuple[int, int]],
    inverse_id: Sequence[int],
) -> None:
    for quad in clause:
        if len(quad) != 4 or len(set(quad)) != 4:
            raise AssertionError(f"bad clause quadrilateral: {quad}")
        if any(label < 0 or label >= n for label in quad):
            raise AssertionError(f"clause label out of range: {quad}")
        if quad not in quad_ids:
            raise AssertionError(f"unknown ordered quadrilateral: {quad}")
    if not _clause_is_valid(clause, quad_ids, inverse_id):
        raise AssertionError(f"clause is not justified by an inverse pair: {clause}")


def _format_quad(quad: Quad) -> str:
    return ",".join(str(label) for label in quad)


def _json_clause(clause: Clause) -> str:
    left, right = clause
    return f"{_format_quad(left)}|{_format_quad(right)}"


def _parse_clause(item: object) -> Clause:
    if isinstance(item, str):
        parts = item.split("|")
        if len(parts) != 2:
            raise AssertionError(f"bad clause item: {item!r}")
        left = tuple(int(label) for label in parts[0].split(","))
        right = tuple(int(label) for label in parts[1].split(","))
        if len(left) != 4 or len(right) != 4:
            raise AssertionError(f"bad clause item: {item!r}")
        return _clause_key(left, right)  # type: ignore[arg-type]
    if not isinstance(item, dict):
        raise AssertionError(f"bad clause item: {item!r}")
    left = tuple(int(label) for label in item["left_quad"])
    right = tuple(int(label) for label in item["right_quad"])
    if len(left) != 4 or len(right) != 4:
        raise AssertionError(f"bad clause item: {item!r}")
    return _clause_key(left, right)  # type: ignore[arg-type]


def _payload(
    *,
    name: str,
    n: int,
    offsets: Sequence[int],
    status: str,
    trust: str,
    solver_result: str,
    iterations: int | None,
    conflict_cap: int | None,
    random_seed: int,
    clauses: Sequence[Clause],
    candidate_order: Sequence[int] | None = None,
) -> dict[str, object]:
    out: dict[str, object] = {
        "type": "kalmanson_two_order_z3_refinement_v1",
        "trust": trust,
        "status": status,
        "pattern": {
            "name": name,
            "n": n,
            "circulant_offsets": [int(offset) for offset in offsets],
        },
        "rotation_quotient": "The cyclic order is represented with label 0 at position 0.",
        "reversal_quotient": "none",
        "smt_solver": "z3",
        "solver_result": solver_result,
        "random_seed": random_seed,
        "iterations": iterations,
        "conflict_cap": conflict_cap,
        "forbidden_clause_count": len(clauses),
        "forbidden_order_pairs": [_json_clause(clause) for clause in clauses],
        "semantics": (
            "If status is EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION, "
            "every cyclic order of this fixed abstract pattern contains some "
            "inverse pair of strict Kalmanson inequalities. This does not prove "
            "Erdos Problem #97."
        ),
    }
    if candidate_order is not None:
        out["candidate_order"] = [int(label) for label in candidate_order]
    return out


def generate_certificate(
    name: str,
    n: int,
    offsets: Sequence[int],
    *,
    max_iterations: int,
    conflict_cap: int,
    random_seed: int,
) -> dict[str, object]:
    quad_ids, inverse_id = _prepare_vector_tables(n, offsets)
    solver, positions = _make_solver(n, random_seed)
    clauses: set[Clause] = set()

    for iteration in range(1, max_iterations + 1):
        result = solver.check()
        if result == unsat:
            ordered_clauses = sorted(clauses)
            return _payload(
                name=name,
                n=n,
                offsets=offsets,
                status="EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION",
                trust="SMT_EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN",
                solver_result="unsat",
                iterations=iteration,
                conflict_cap=conflict_cap,
                random_seed=random_seed,
                clauses=ordered_clauses,
            )
        if result != sat:
            ordered_clauses = sorted(clauses)
            return _payload(
                name=name,
                n=n,
                offsets=offsets,
                status="UNKNOWN_SMT_RESULT",
                trust="SMT_DIAGNOSTIC",
                solver_result=str(result),
                iterations=iteration,
                conflict_cap=conflict_cap,
                random_seed=random_seed,
                clauses=ordered_clauses,
            )

        model = solver.model()
        order = _order_from_model(model, positions, n)
        conflicts = _collect_conflicts(order, quad_ids, inverse_id, conflict_cap)
        if not conflicts:
            ordered_clauses = sorted(clauses)
            return _payload(
                name=name,
                n=n,
                offsets=offsets,
                status="FOUND_ORDER_WITHOUT_TWO_INEQUALITY_KALMANSON_CERTIFICATE",
                trust="EXACT_COUNTEREXAMPLE_TO_THIS_FILTER_ONLY",
                solver_result="sat",
                iterations=iteration,
                conflict_cap=conflict_cap,
                random_seed=random_seed,
                clauses=ordered_clauses,
                candidate_order=order,
            )

        for conflict in conflicts:
            clause = _clause_key(conflict.left_quad, conflict.right_quad)
            if clause not in clauses:
                _validate_clause(clause, n, quad_ids, inverse_id)
                clauses.add(clause)
                _add_clause(solver, positions, clause)

    ordered_clauses = sorted(clauses)
    return _payload(
        name=name,
        n=n,
        offsets=offsets,
        status="UNKNOWN_ITERATION_LIMIT_REACHED",
        trust="BOUNDED_SMT_REFINEMENT_DIAGNOSTIC",
        solver_result="iteration_limit",
        iterations=max_iterations,
        conflict_cap=conflict_cap,
        random_seed=random_seed,
        clauses=ordered_clauses,
    )


def verify_certificate(payload: dict[str, object]) -> dict[str, object]:
    pattern = payload["pattern"]
    if not isinstance(pattern, dict):
        raise AssertionError("pattern must be an object")
    name = str(pattern["name"])
    n = int(pattern["n"])
    offsets = [int(offset) for offset in pattern["circulant_offsets"]]  # type: ignore[index]
    random_seed = int(payload.get("random_seed", 0))
    conflict_cap_raw = payload.get("conflict_cap")
    conflict_cap = None if conflict_cap_raw is None else int(conflict_cap_raw)

    quad_ids, inverse_id = _prepare_vector_tables(n, offsets)
    clauses = [_parse_clause(item) for item in payload["forbidden_order_pairs"]]  # type: ignore[index]
    if len(set(clauses)) != len(clauses):
        raise AssertionError("duplicate forbidden clauses in certificate")

    solver, positions = _make_solver(n, random_seed)
    for clause in clauses:
        _validate_clause(clause, n, quad_ids, inverse_id)
        _add_clause(solver, positions, clause)
    result = solver.check()
    status = (
        "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION"
        if result == unsat
        else "CERTIFICATE_DID_NOT_REPLAY_AS_UNSAT"
    )
    trust = (
        "SMT_EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN"
        if result == unsat
        else "INVALID_OR_INCOMPLETE_SMT_CERTIFICATE"
    )
    return _payload(
        name=name,
        n=n,
        offsets=offsets,
        status=status,
        trust=trust,
        solver_result=str(result),
        iterations=None,
        conflict_cap=conflict_cap,
        random_seed=random_seed,
        clauses=clauses,
    )


def assert_unsat(payload: dict[str, object]) -> None:
    if payload["status"] != "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION":
        raise AssertionError(f"expected UNSAT obstruction, got {payload['status']}")


def print_summary(payload: dict[str, object]) -> None:
    pattern = payload["pattern"]
    print(
        f"{pattern['name']} {payload['status']} "
        f"solver={payload['solver_result']} "
        f"clauses={payload['forbidden_clause_count']} "
        f"iterations={payload['iterations']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", help="pattern name")
    parser.add_argument("--n", type=int)
    parser.add_argument("--offsets", type=parse_int_list)
    parser.add_argument("--certificate", type=Path, help="verify an existing JSON certificate")
    parser.add_argument("--out", type=Path, help="optional JSON output path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--assert-unsat", action="store_true")
    parser.add_argument("--max-iterations", type=int, default=1000)
    parser.add_argument("--conflict-cap", type=int, default=1024)
    parser.add_argument("--random-seed", type=int, default=7)
    args = parser.parse_args()

    if args.certificate:
        payload = verify_certificate(json.loads(args.certificate.read_text(encoding="utf-8")))
    else:
        if args.name is None or args.n is None or args.offsets is None:
            raise SystemExit("--name, --n, and --offsets are required unless --certificate is used")
        if args.n <= 0:
            raise SystemExit("--n must be positive")
        if args.max_iterations <= 0:
            raise SystemExit("--max-iterations must be positive")
        if args.conflict_cap <= 0:
            raise SystemExit("--conflict-cap must be positive")
        payload = generate_certificate(
            args.name,
            args.n,
            args.offsets,
            max_iterations=args.max_iterations,
            conflict_cap=args.conflict_cap,
            random_seed=args.random_seed,
        )

    if args.assert_unsat:
        assert_unsat(payload)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_summary(payload)
        if args.assert_unsat:
            print("OK: Z3 Kalmanson order obstruction verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
