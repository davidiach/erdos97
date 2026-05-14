#!/usr/bin/env python3
"""Focused audit for the n=8 class 14 PB+ED certificate.

This is a small reviewer-facing checker for the most delicate n=8 survivor
class.  It intentionally does not regenerate the n=8 incidence enumeration and
does not promote the repo-local finite-case result to a public theorem claim.

The checker reads the checked-in class 14 survivor rows and exact-analysis
certificate, rebuilds only the class 14 perpendicular-bisector plus
equal-distance polynomial system, compares the recorded Groebner basis, derives
the four real branches from that basis, and checks exact strict-interior
failure on every branch.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

N = 8
CLASS_ID = 14
VARS_ORDER = (
    "x6",
    "y6",
    "y7",
    "x2",
    "y2",
    "x3",
    "y3",
    "x4",
    "y4",
    "x5",
    "y5",
    "x7",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def json_load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sympy_context():
    try:
        import sympy as sp
    except ImportError as exc:  # pragma: no cover - depends on dev dependency
        raise SystemExit("SymPy is required: pip install sympy") from exc

    symbols = {
        f"{axis}{i}": sp.symbols(f"{axis}{i}")
        for i in range(2, N)
        for axis in ("x", "y")
    }
    coords = {
        0: (sp.Integer(0), sp.Integer(0)),
        1: (sp.Integer(1), sp.Integer(0)),
    }
    for i in range(2, N):
        coords[i] = (symbols[f"x{i}"], symbols[f"y{i}"])
    vars_order = [symbols[name] for name in VARS_ORDER]
    return sp, symbols, coords, vars_order


def witnesses(rows: list[list[int]], i: int) -> list[int]:
    return [j for j, value in enumerate(rows[i]) if value]


def chord(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def phi_edges(rows: list[list[int]]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    witness_sets = [set(witnesses(rows, i)) for i in range(N)]
    edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for i in range(N):
        for j in range(i + 1, N):
            inter = sorted(witness_sets[i] & witness_sets[j])
            if len(inter) == 2:
                edges.append((chord(i, j), chord(inter[0], inter[1])))
    return edges


def pb_equations(rows: list[list[int]]):
    sp, _symbols, p, _vars_order = sympy_context()
    eqs = []
    for (i, j), (a, b) in phi_edges(rows):
        pix, piy = p[i]
        pjx, pjy = p[j]
        pax, pay = p[a]
        pbx, pby = p[b]
        dot = sp.expand((pix - pjx) * (pax - pbx) + (piy - pjy) * (pay - pby))
        # Twice the midpoint equation, avoiding denominators:
        # det(p_j - p_i, p_a + p_b - 2 p_i) = 0.
        bis = sp.expand(
            (pjx - pix) * (pay + pby - 2 * piy)
            - (pjy - piy) * (pax + pbx - 2 * pix)
        )
        eqs.extend([dot, bis])
    return eqs


def ed_equations(rows: list[list[int]]):
    sp, _symbols, p, _vars_order = sympy_context()
    eqs = []
    for i in range(N):
        w = witnesses(rows, i)
        base = w[0]
        pix, piy = p[i]
        pbx, pby = p[base]
        base_dist = (pix - pbx) ** 2 + (piy - pby) ** 2
        for other in w[1:]:
            pox, poy = p[other]
            eqs.append(sp.expand((pix - pox) ** 2 + (piy - poy) ** 2 - base_dist))
    return eqs


def load_class14_rows(root: Path) -> list[list[int]]:
    survivors = json_load(root / "data" / "incidence" / "n8_reconstructed_15_survivors.json")
    for record in survivors:
        if int(record.get("id")) == CLASS_ID:
            return record["rows"]
    raise SystemExit("class 14 was not found in n8_reconstructed_15_survivors.json")


def load_class14_certificate(root: Path) -> dict[str, Any]:
    exact = json_load(root / "certificates" / "n8_exact_analysis.json")
    try:
        return exact["contradictions"]["class_14"]
    except KeyError as exc:
        raise SystemExit("class_14 certificate missing from n8_exact_analysis.json") from exc


def parse_expr(text: str):
    sp, symbols, _coords, _vars_order = sympy_context()
    return sp.sympify(text, locals={**symbols, "sqrt": sp.sqrt})


def monic_factor(expr):
    sp, _symbols, _coords, vars_order = sympy_context()
    return sp.factor(sp.Poly(expr, *vars_order, domain=sp.QQ).monic().as_expr())


def branch_from_signs(x3_sign: int, y5_sign: int):
    sp, symbols, _coords, _vars_order = sympy_context()
    a = sp.sqrt(3) / 2
    x3 = x3_sign * a
    y5 = sp.Integer(y5_sign)
    return {
        symbols["x2"]: sp.Rational(1, 2),
        symbols["y2"]: x3 * y5,
        symbols["x3"]: x3,
        symbols["y3"]: y5 / 2,
        symbols["x4"]: sp.Integer(0),
        symbols["y4"]: y5,
        symbols["x5"]: sp.Integer(1),
        symbols["y5"]: y5,
        symbols["x6"]: 1 - x3,
        symbols["y6"]: y5 / 2,
        symbols["x7"]: sp.Rational(1, 2),
        symbols["y7"]: y5 * (1 - x3),
    }


def derived_branches() -> list[dict[Any, Any]]:
    return [
        branch_from_signs(-1, 1),
        branch_from_signs(-1, -1),
        branch_from_signs(1, -1),
        branch_from_signs(1, 1),
    ]


def parse_artifact_branch(branch: dict[str, str]) -> dict[Any, Any]:
    _sp, symbols, _coords, _vars_order = sympy_context()
    return {symbols[name]: parse_expr(value) for name, value in branch.items()}


def branch_key(branch: dict[Any, Any]) -> tuple[str, ...]:
    sp, symbols, _coords, _vars_order = sympy_context()
    ordered_names = [f"{axis}{i}" for i in range(2, N) for axis in ("x", "y")]
    return tuple(str(sp.simplify(branch[symbols[name]])) for name in ordered_names)


def branch_points(branch: dict[Any, Any]) -> dict[int, tuple[Any, Any]]:
    sp, symbols, _coords, _vars_order = sympy_context()
    points = {0: (sp.Integer(0), sp.Integer(0)), 1: (sp.Integer(1), sp.Integer(0))}
    for i in range(2, N):
        points[i] = (branch[symbols[f"x{i}"]], branch[symbols[f"y{i}"]])
    return points


def orientation(points: dict[int, tuple[Any, Any]], left: int, right: int, test: int):
    sp, _symbols, _coords, _vars_order = sympy_context()
    px, py = points[left]
    qx, qy = points[right]
    rx, ry = points[test]
    return sp.simplify((qx - px) * (ry - py) - (qy - py) * (rx - px))


def sign_of(expr) -> int:
    sp, _symbols, _coords, _vars_order = sympy_context()
    simplified = sp.simplify(expr)
    if simplified.is_positive:
        return 1
    if simplified.is_negative:
        return -1
    if simplified == 0:
        return 0
    raise ValueError(f"could not determine exact sign of {simplified!s}")


def expected_hull(branch: dict[Any, Any]) -> list[int]:
    sp, symbols, _coords, _vars_order = sympy_context()
    x3 = sp.simplify(branch[symbols["x3"]])
    y5 = sp.simplify(branch[symbols["y5"]])
    if x3 == sp.sqrt(3) / 2:
        return [0, 1, 5, 4]
    if x3 == -sp.sqrt(3) / 2 and y5 == 1:
        return [3, 2, 6, 7]
    if x3 == -sp.sqrt(3) / 2 and y5 == -1:
        return [3, 7, 6, 2]
    raise ValueError("unexpected class 14 branch")


def convexity_record(branch: dict[Any, Any]) -> dict[str, Any]:
    sp, _symbols, _coords, _vars_order = sympy_context()
    points = branch_points(branch)
    hull = expected_hull(branch)
    interior = sorted(set(range(N)) - set(hull))
    hull_turns = [
        orientation(points, hull[i], hull[(i + 1) % len(hull)], hull[(i + 2) % len(hull)])
        for i in range(len(hull))
    ]
    hull_signs = [sign_of(value) for value in hull_turns]
    hull_strict = len(set(hull_signs)) == 1 and 0 not in hull_signs
    edge_sign = hull_signs[0] if hull_strict else 0

    interior_checks = []
    for label in interior:
        edge_values = [
            orientation(points, hull[i], hull[(i + 1) % len(hull)], label)
            for i in range(len(hull))
        ]
        edge_signs = [sign_of(value) for value in edge_values]
        interior_checks.append({
            "label": label,
            "strict_inside_expected_hull": bool(
                hull_strict and all(sign == edge_sign for sign in edge_signs)
            ),
            "edge_orientation_signs": edge_signs,
            "edge_orientations": [str(sp.simplify(value)) for value in edge_values],
        })

    return {
        "hull_labels": hull,
        "interior_labels": interior,
        "hull_strictly_convex": hull_strict,
        "hull_turn_signs": hull_signs,
        "hull_turns": [str(sp.simplify(value)) for value in hull_turns],
        "all_other_labels_strictly_inside_hull": all(
            item["strict_inside_expected_hull"] for item in interior_checks
        ),
        "interior_checks": interior_checks,
    }


def check_class14(root: Path) -> dict[str, Any]:
    sp, _symbols, _coords, vars_order = sympy_context()
    rows = load_class14_rows(root)
    certificate = load_class14_certificate(root)
    pb = pb_equations(rows)
    ed = ed_equations(rows)
    equations = pb + ed
    errors: list[str] = []

    computed_basis = sp.groebner(equations, *vars_order, order="lex", domain=sp.QQ)
    computed_basis_exprs = {monic_factor(poly.as_expr()) for poly in computed_basis.polys}
    artifact_basis_exprs = {
        monic_factor(parse_expr(item))
        for item in certificate.get("groebner_basis_PB_plus_ED", [])
    }
    basis_matches = computed_basis_exprs == artifact_basis_exprs
    if not basis_matches:
        errors.append("computed Groebner basis does not match artifact basis")

    artifact_basis = sp.groebner(
        [parse_expr(item) for item in certificate.get("groebner_basis_PB_plus_ED", [])],
        *vars_order,
        order="lex",
        domain=sp.QQ,
    )
    equations_reduce_to_zero = all(
        sp.expand(artifact_basis.reduce(eq)[1]) == 0 for eq in equations
    )
    if not equations_reduce_to_zero:
        errors.append("some PB+ED equations do not reduce to zero modulo artifact basis")

    basis_zero_dimensional = bool(computed_basis.is_zero_dimensional)
    if not basis_zero_dimensional:
        errors.append("computed Groebner basis is not zero-dimensional")

    derived = derived_branches()
    artifact_branches = [
        parse_artifact_branch(branch)
        for branch in certificate.get("solution_branches", [])
    ]
    branches_match = {branch_key(branch) for branch in derived} == {
        branch_key(branch) for branch in artifact_branches
    }
    if not branches_match:
        errors.append("derived branches do not match artifact solution branches")

    branch_records = []
    for index, branch in enumerate(derived):
        solves_pb_ed = all(sp.simplify(eq.subs(branch)) == 0 for eq in equations)
        satisfies_basis = all(
            sp.simplify(parse_expr(item).subs(branch)) == 0
            for item in certificate.get("groebner_basis_PB_plus_ED", [])
        )
        convexity = convexity_record(branch)
        branch_records.append({
            "index": index,
            "solves_pb_ed": bool(solves_pb_ed),
            "satisfies_artifact_basis": bool(satisfies_basis),
            "convexity": convexity,
        })
    if not all(record["solves_pb_ed"] for record in branch_records):
        errors.append("at least one derived branch does not solve PB+ED")
    if not all(record["satisfies_artifact_basis"] for record in branch_records):
        errors.append("at least one derived branch does not satisfy the artifact basis")
    if not all(
        record["convexity"]["hull_strictly_convex"]
        and record["convexity"]["all_other_labels_strictly_inside_hull"]
        for record in branch_records
    ):
        errors.append("at least one branch did not verify the strict-interior certificate")

    verified = not errors
    return {
        "type": "n8_class14_certificate_audit_v1",
        "verified": verified,
        "trust": "REPO_LOCAL_EXACT_OBSTRUCTION_AUDIT_PENDING_EXTERNAL_REVIEW",
        "claim_scope": (
            "Focused audit of the checked-in n=8 class 14 PB+ED Groebner "
            "and strict-interior certificate only. No general proof of "
            "Erdos Problem #97 and no counterexample are claimed."
        ),
        "class_id": CLASS_ID,
        "row_strings": ["".join(str(value) for value in row) for row in rows],
        "equation_counts": {
            "phi_edges": len(phi_edges(rows)),
            "perpendicular_bisector_equations": len(pb),
            "equal_distance_equations": len(ed),
            "total_equations": len(equations),
        },
        "groebner": {
            "basis_polynomial_count": len(computed_basis.polys),
            "artifact_basis_matches_computed_basis": basis_matches,
            "artifact_basis_reduces_all_pb_ed_equations": equations_reduce_to_zero,
            "computed_basis_is_zero_dimensional": basis_zero_dimensional,
        },
        "branches": {
            "artifact_branch_count": len(artifact_branches),
            "derived_branch_count": len(derived),
            "derived_branches_match_artifact": branches_match,
            "all_derived_branches_solve_pb_ed": all(
                record["solves_pb_ed"] for record in branch_records
            ),
            "all_derived_branches_satisfy_artifact_basis": all(
                record["satisfies_artifact_basis"] for record in branch_records
            ),
            "all_derived_branches_have_four_hull_vertices": all(
                len(record["convexity"]["hull_labels"]) == 4 for record in branch_records
            ),
            "all_remaining_labels_are_strict_interior": all(
                record["convexity"]["all_other_labels_strictly_inside_hull"]
                for record in branch_records
            ),
            "records": branch_records,
        },
        "does_not_check": [
            "n=8 incidence completeness",
            "other n=8 survivor classes",
            "external independent review",
            "general Erdos Problem #97 proof",
        ],
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit nonzero if verification fails.")
    parser.add_argument("--json", action="store_true", help="Print full JSON summary.")
    args = parser.parse_args(argv)

    summary = check_class14(repo_root())
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        status = "verified" if summary["verified"] else "FAILED"
        print(f"n=8 class 14 certificate audit: {status}")
        print(
            "branches: "
            f"{summary['branches']['derived_branch_count']} derived, "
            f"strict-interior={summary['branches']['all_remaining_labels_are_strict_interior']}"
        )
    if args.check and not summary["verified"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
