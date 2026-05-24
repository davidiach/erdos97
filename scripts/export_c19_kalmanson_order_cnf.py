#!/usr/bin/env python3
"""Export the checked C19 order clauses to a Z3-independent DIMACS encoding.

The stored C19 certificate already records exact forbidden ordered-quadrilateral
pairs.  This script validates those pairs against the selected-distance
quotient table and emits a standard CNF encoding of the cyclic-order problem:

* one Boolean variable records the precedence direction for each unordered
  label pair;
* unit clauses fix label 0 as the first label, matching the stored rotation
  quotient;
* transitivity clauses force the precedence tournament to be a linear order;
* each stored inverse-pair clause forbids the two ordered quadrilaterals from
  appearing simultaneously.

The generated CNF is a replay target for an external SAT proof checker.  This
script does not prove UNSAT and does not prove Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_kalmanson_two_order_search import _prepare_vector_tables  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402


Quad = tuple[int, int, int, int]
Clause = tuple[Quad, Quad]

SCHEMA = "erdos97.c19_kalmanson_order_cnf_summary.v1"
STATUS = "C19_ORDER_CNF_EXPORT_DIAGNOSTIC_ONLY"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Z3-independent DIMACS encoding summary for the checked fixed abstract "
    "C19_skew Kalmanson order clauses. It validates the stored forbidden "
    "ordered-quadrilateral pairs and exports the order-CNF target for an "
    "external SAT proof replay. It does not include a DRAT/LRAT proof, does "
    "not prove Erdos Problem #97, does not claim a counterexample, and does "
    "not transfer the obstruction to other patterns."
)

DEFAULT_CERTIFICATE = (
    ROOT / "data" / "certificates" / "c19_skew_all_orders_kalmanson_z3.json"
)
DEFAULT_ARTIFACT = ROOT / "reports" / "c19_kalmanson_order_cnf_summary.json"
DEFAULT_COMMAND = (
    "python scripts/export_c19_kalmanson_order_cnf.py --assert-expected "
    "--out reports/c19_kalmanson_order_cnf_summary.json"
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _clause_key(left: Quad, right: Quad) -> Clause:
    return (left, right) if left <= right else (right, left)


def _parse_quad(raw: str) -> Quad:
    labels = tuple(int(label) for label in raw.split(","))
    if len(labels) != 4:
        raise AssertionError(f"bad ordered quadrilateral: {raw!r}")
    return labels  # type: ignore[return-value]


def parse_clause(item: object) -> Clause:
    if not isinstance(item, str):
        raise AssertionError(f"forbidden clause must be a string: {item!r}")
    parts = item.split("|")
    if len(parts) != 2:
        raise AssertionError(f"bad forbidden clause: {item!r}")
    return _clause_key(_parse_quad(parts[0]), _parse_quad(parts[1]))


def clause_is_valid(
    clause: Clause,
    quad_ids: Mapping[Quad, tuple[int, int]],
    inverse_id: Sequence[int],
) -> bool:
    left, right = clause
    left_ids = quad_ids[left]
    right_ids = set(quad_ids[right])
    return any(inverse_id[vector_id] in right_ids for vector_id in left_ids)


def validate_clause(
    clause: Clause,
    *,
    n: int,
    quad_ids: Mapping[Quad, tuple[int, int]],
    inverse_id: Sequence[int],
) -> None:
    for quad in clause:
        if len(set(quad)) != 4:
            raise AssertionError(f"bad clause quadrilateral: {quad}")
        if any(label < 0 or label >= n for label in quad):
            raise AssertionError(f"clause label out of range: {quad}")
        if quad not in quad_ids:
            raise AssertionError(f"unknown ordered quadrilateral: {quad}")
    if not clause_is_valid(clause, quad_ids, inverse_id):
        raise AssertionError(f"clause is not justified by an inverse pair: {clause}")


def pair_variable(a: int, b: int, n: int) -> int:
    """Return the 1-based variable id for the unordered label pair {a,b}."""

    if a == b:
        raise ValueError("pair_variable needs distinct labels")
    i, j = sorted((a, b))
    variable = 1
    for left in range(i):
        variable += n - left - 1
    variable += j - i - 1
    return variable


def before_literal(a: int, b: int, n: int) -> int:
    """Return the literal meaning label ``a`` precedes label ``b``."""

    variable = pair_variable(a, b, n)
    return variable if a < b else -variable


def transitivity_clauses(n: int) -> list[list[int]]:
    clauses: list[list[int]] = []
    for a in range(n):
        for b in range(n):
            if b == a:
                continue
            for c in range(n):
                if c == a or c == b:
                    continue
                clauses.append(
                    [
                        -before_literal(a, b, n),
                        -before_literal(b, c, n),
                        before_literal(a, c, n),
                    ]
                )
    return clauses


def unit_clauses(n: int) -> list[list[int]]:
    return [[before_literal(0, label, n)] for label in range(1, n)]


def forbidden_cnf_clause(clause: Clause, n: int) -> list[int]:
    literals: list[int] = []
    for quad in clause:
        literals.extend(
            [
                -before_literal(quad[0], quad[1], n),
                -before_literal(quad[1], quad[2], n),
                -before_literal(quad[2], quad[3], n),
            ]
        )
    return literals


def dimacs_text(n: int, forbidden: Sequence[Clause]) -> str:
    units = unit_clauses(n)
    transitivity = transitivity_clauses(n)
    forbidden_clauses = [forbidden_cnf_clause(clause, n) for clause in forbidden]
    clauses = units + transitivity + forbidden_clauses
    lines = [
        "c C19_skew Kalmanson order-CNF export",
        "c variable o_i_j with i<j is true iff label i precedes label j",
        "c label 0 is fixed first by unit clauses",
        f"p cnf {n * (n - 1) // 2} {len(clauses)}",
    ]
    lines.extend(" ".join(str(literal) for literal in clause) + " 0" for clause in clauses)
    return "\n".join(lines) + "\n"


def source_clauses(payload: Mapping[str, Any]) -> tuple[dict[str, Any], list[Clause]]:
    pattern = payload.get("pattern")
    if not isinstance(pattern, dict):
        raise AssertionError("pattern must be an object")
    raw_clauses = payload.get("forbidden_order_pairs")
    if not isinstance(raw_clauses, list):
        raise AssertionError("forbidden_order_pairs must be a list")
    clauses = [parse_clause(item) for item in raw_clauses]
    if len(set(clauses)) != len(clauses):
        raise AssertionError("duplicate forbidden order clauses")
    return pattern, clauses


def diagnostic_payload(certificate: Path = DEFAULT_CERTIFICATE) -> dict[str, Any]:
    raw_payload = load_json(certificate)
    if not isinstance(raw_payload, dict):
        raise TypeError("source certificate must be a JSON object")
    pattern, clauses = source_clauses(raw_payload)
    name = str(pattern["name"])
    n = int(pattern["n"])
    offsets = [int(offset) for offset in pattern["circulant_offsets"]]
    quad_ids, inverse_id = _prepare_vector_tables(n, offsets)
    for clause in clauses:
        validate_clause(clause, n=n, quad_ids=quad_ids, inverse_id=inverse_id)

    dimacs = dimacs_text(n, clauses)
    unit_count = n - 1
    transitivity_count = n * (n - 1) * (n - 2)
    forbidden_count = len(clauses)
    variable_count = n * (n - 1) // 2
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_certificate": {
            "path": display_path(certificate, ROOT),
            "type": raw_payload.get("type"),
            "status": raw_payload.get("status"),
            "trust": raw_payload.get("trust"),
            "solver_result": raw_payload.get("solver_result"),
            "smt_solver": raw_payload.get("smt_solver"),
            "forbidden_clause_count": raw_payload.get("forbidden_clause_count"),
            "pattern": {
                "name": name,
                "n": n,
                "circulant_offsets": offsets,
            },
        },
        "encoding": {
            "format": "DIMACS CNF",
            "variable_count": variable_count,
            "clause_count": unit_count + transitivity_count + forbidden_count,
            "unit_clause_count": unit_count,
            "transitivity_clause_count": transitivity_count,
            "forbidden_order_clause_count": forbidden_count,
            "rotation_quotient": "label 0 is fixed first by unit clauses",
            "reversal_quotient": "none",
            "variable_semantics": (
                "For 0 <= i < j < n, variable o_i_j is true exactly when "
                "label i precedes label j in the linear representative order."
            ),
            "forbidden_clause_semantics": (
                "Each stored pair of ordered quadrilaterals contributes one "
                "six-literal clause forbidding both quadrilateral orders from "
                "appearing simultaneously."
            ),
        },
        "validation": {
            "parsed_forbidden_clause_count": len(clauses),
            "unique_forbidden_clause_count": len(set(clauses)),
            "all_forbidden_clauses_validate_as_inverse_pairs": True,
            "dimacs_sha256": hashlib.sha256(dimacs.encode("utf-8")).hexdigest(),
            "dimacs_line_count": dimacs.count("\n"),
            "dimacs_header": f"p cnf {variable_count} "
            f"{unit_count + transitivity_count + forbidden_count}",
        },
        "interpretation": (
            "This artifact provides a deterministic SAT encoding target for "
            "the stored C19 order clauses. A solver-independent UNSAT result "
            "still needs a separately checked DRAT/LRAT proof or equivalent "
            "finite proof replay."
        ),
        "provenance": {
            "generator": "scripts/export_c19_kalmanson_order_cnf.py",
            "command": DEFAULT_COMMAND,
        },
    }


def assert_expected(payload: Mapping[str, Any]) -> None:
    expected_top = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
    }
    for key, expected in expected_top.items():
        if payload.get(key) != expected:
            raise AssertionError(f"{key} mismatch: {payload.get(key)!r}")

    source = payload.get("source_certificate")
    if not isinstance(source, Mapping):
        raise AssertionError("source_certificate must be an object")
    expected_source = {
        "path": "data/certificates/c19_skew_all_orders_kalmanson_z3.json",
        "type": "kalmanson_two_order_z3_refinement_v1",
        "status": "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION",
        "trust": "SMT_EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN",
        "solver_result": "unsat",
        "smt_solver": "z3",
        "forbidden_clause_count": 7981,
        "pattern": {
            "name": "C19_skew",
            "n": 19,
            "circulant_offsets": [-8, -3, 5, 9],
        },
    }
    for key, expected in expected_source.items():
        if source.get(key) != expected:
            raise AssertionError(f"source_certificate[{key!r}] mismatch")

    encoding = payload.get("encoding")
    if not isinstance(encoding, Mapping):
        raise AssertionError("encoding must be an object")
    expected_encoding = {
        "format": "DIMACS CNF",
        "variable_count": 171,
        "clause_count": 13813,
        "unit_clause_count": 18,
        "transitivity_clause_count": 5814,
        "forbidden_order_clause_count": 7981,
        "rotation_quotient": "label 0 is fixed first by unit clauses",
        "reversal_quotient": "none",
    }
    for key, expected in expected_encoding.items():
        if encoding.get(key) != expected:
            raise AssertionError(f"encoding[{key!r}] mismatch: {encoding.get(key)!r}")

    validation = payload.get("validation")
    if not isinstance(validation, Mapping):
        raise AssertionError("validation must be an object")
    expected_validation = {
        "parsed_forbidden_clause_count": 7981,
        "unique_forbidden_clause_count": 7981,
        "all_forbidden_clauses_validate_as_inverse_pairs": True,
        "dimacs_sha256": "dd4b8f429fea232bf09ff878342d7a28f4e9b6e743c99cd1b48f681d0f9ec450",
        "dimacs_line_count": 13817,
        "dimacs_header": "p cnf 171 13813",
    }
    for key, expected in expected_validation.items():
        if validation.get(key) != expected:
            raise AssertionError(f"validation[{key!r}] mismatch: {validation.get(key)!r}")
    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping) or provenance.get("command") != DEFAULT_COMMAND:
        raise AssertionError("provenance command changed")
    for forbidden in (
        "does not include a DRAT/LRAT proof",
        "does not prove Erdos Problem #97",
        "does not claim a counterexample",
        "does not transfer the obstruction to other patterns",
    ):
        if forbidden not in str(payload.get("claim_scope", "")):
            raise AssertionError(f"claim_scope missing {forbidden!r}")


def check_artifact(path: Path, payload: Mapping[str, Any]) -> None:
    artifact = load_json(path)
    if artifact != payload:
        raise AssertionError(f"{display_path(path, ROOT)} does not match regenerated payload")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_CERTIFICATE)
    parser.add_argument("--out", type=Path, help="write JSON summary to this path")
    parser.add_argument("--write-cnf", type=Path, help="write DIMACS CNF to this path")
    parser.add_argument("--check-artifact", type=Path)
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    certificate = args.certificate if args.certificate.is_absolute() else ROOT / args.certificate
    payload = diagnostic_payload(certificate)
    if args.assert_expected:
        assert_expected(payload)
    if args.check_artifact:
        artifact = args.check_artifact if args.check_artifact.is_absolute() else ROOT / args.check_artifact
        check_artifact(artifact, payload)
    if args.out:
        out = args.out if args.out.is_absolute() else ROOT / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    if args.write_cnf:
        raw_payload = load_json(certificate)
        _, clauses = source_clauses(raw_payload)
        cnf = dimacs_text(int(raw_payload["pattern"]["n"]), clauses)
        cnf_path = args.write_cnf if args.write_cnf.is_absolute() else ROOT / args.write_cnf
        cnf_path.parent.mkdir(parents=True, exist_ok=True)
        cnf_path.write_text(cnf, encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        encoding = payload["encoding"]
        validation = payload["validation"]
        print("C19 Kalmanson order-CNF export")
        print(f"variables: {encoding['variable_count']}")
        print(f"clauses: {encoding['clause_count']}")
        print(f"dimacs sha256: {validation['dimacs_sha256']}")
        if args.assert_expected:
            print("OK: C19 order-CNF summary matches expected values")
        if args.check_artifact:
            print(f"OK: {display_path(args.check_artifact, ROOT)} matches regenerated payload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
