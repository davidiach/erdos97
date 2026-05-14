#!/usr/bin/env python3
"""Focused audit for the n=8 classes 3, 4, and 5 certificates.

This complements ``check_n8_class14_certificate.py`` by isolating the remaining
Groebner/substitution survivor-class certificates from the larger n=8 exact
checker.  It does not regenerate n=8 incidence completeness, and it does not
promote the repo-local finite-case result to a public theorem claim.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import check_n8_class14_certificate as base

N = base.N
TARGET_CLASS_IDS = (3, 4, 5)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_class_rows(root: Path, class_id: int) -> list[list[int]]:
    survivors = base.json_load(root / "data" / "incidence" / "n8_reconstructed_15_survivors.json")
    for record in survivors:
        if int(record.get("id")) == class_id:
            return record["rows"]
    raise SystemExit(f"class {class_id} was not found in n8_reconstructed_15_survivors.json")


def load_certificate(root: Path, class_id: int) -> dict[str, Any]:
    exact = base.json_load(root / "certificates" / "n8_exact_analysis.json")
    key = f"class_{class_id}"
    try:
        return exact["contradictions"][key]
    except KeyError as exc:
        raise SystemExit(f"{key} certificate missing from n8_exact_analysis.json") from exc


def pb_equation_map(rows: list[list[int]]):
    sp, _symbols, p, _vars_order = base.sympy_context()
    eqs = {}
    for (i, j), (a, b) in base.phi_edges(rows):
        pix, piy = p[i]
        pjx, pjy = p[j]
        pax, pay = p[a]
        pbx, pby = p[b]
        dot = sp.expand((pix - pjx) * (pax - pbx) + (piy - pjy) * (pay - pby))
        bis = sp.expand(
            (pjx - pix) * (pay + pby - 2 * piy)
            - (pjy - piy) * (pax + pbx - 2 * pix)
        )
        eqs[((i, j), (a, b))] = (dot, bis)
    return eqs


def ideal_contains(groebner_basis, expr) -> bool:
    sp, _symbols, _coords, _vars_order = base.sympy_context()
    return sp.expand(groebner_basis.reduce(expr)[1]) == 0


def first_stage_relations(eq):
    sp, symbols, _coords, _vars_order = base.sympy_context()
    x2, y2 = symbols["x2"], symbols["y2"]
    x3, y3 = symbols["x3"], symbols["y3"]
    first = [
        eq[((0, 1), (2, 3))][0],
        eq[((0, 1), (2, 3))][1],
        eq[((2, 3), (0, 1))][1],
    ]
    basis = sp.groebner(first, x3, y3, x2, y2, order="lex", domain=sp.QQ)
    relations = [x3 - x2, y3 + y2, y2 * (2 * x2 - 1)]
    return {
        "basis_polynomial_count": len(basis.polys),
        "contains_x3_equals_x2": ideal_contains(basis, relations[0]),
        "contains_y3_equals_minus_y2": ideal_contains(basis, relations[1]),
        "contains_y2_times_2x2_minus_1": ideal_contains(basis, relations[2]),
        "all_expected_relations_hold": all(ideal_contains(basis, rel) for rel in relations),
    }


def check_class3(root: Path) -> dict[str, Any]:
    sp, symbols, _coords, _vars_order = base.sympy_context()
    rows = load_class_rows(root, 3)
    eq = pb_equation_map(rows)
    x2, y2 = symbols["x2"], symbols["y2"]
    x3, y3 = symbols["x3"], symbols["y3"]
    x4, y4 = symbols["x4"], symbols["y4"]
    x7, y7 = symbols["x7"], symbols["y7"]

    first = first_stage_relations(eq)
    stage1 = {x2: sp.Rational(1, 2), x3: sp.Rational(1, 2), y3: -y2}
    second = [
        sp.expand(poly.subs(stage1))
        for edge in [((0, 2), (1, 4)), ((1, 4), (0, 2))]
        for poly in eq[edge]
    ]
    second_basis = sp.groebner(second, x4, y4, y2, order="lex", domain=sp.QQ)
    second_relations = [
        y4 - y2,
        x4 + 2 * y2**2 - 1,
        y2 * (4 * y2**2 - 3),
    ]

    stage2 = {
        x2: sp.Rational(1, 2),
        x3: sp.Rational(1, 2),
        y3: -y2,
        x4: -sp.Rational(1, 2),
        y4: y2,
    }
    third = [
        sp.expand(poly.subs(stage2))
        for edge in [((0, 7), (3, 4)), ((3, 4), (0, 7))]
        for poly in eq[edge]
    ]
    third.append(y2**2 - sp.Rational(3, 4))
    third_basis = sp.groebner(third, x7, y7, y2, order="lex", domain=sp.QQ)
    duplicate_forced = ideal_contains(third_basis, x7) and ideal_contains(third_basis, y7)
    verified = (
        first["all_expected_relations_hold"]
        and all(ideal_contains(second_basis, rel) for rel in second_relations)
        and duplicate_forced
    )
    return {
        "class_id": 3,
        "verified": verified,
        "mechanism": "duplicate_vertex",
        "row_strings": ["".join(str(value) for value in row) for row in rows],
        "first_stage": first,
        "second_stage": {
            "basis_polynomial_count": len(second_basis.polys),
            "contains_y4_equals_y2": ideal_contains(second_basis, second_relations[0]),
            "contains_x4_relation": ideal_contains(second_basis, second_relations[1]),
            "contains_y2_squared_relation_up_to_y2": ideal_contains(second_basis, second_relations[2]),
        },
        "third_stage": {
            "basis_polynomial_count": len(third_basis.polys),
            "contains_x7": ideal_contains(third_basis, x7),
            "contains_y7": ideal_contains(third_basis, y7),
            "forces_p7_equals_p0": duplicate_forced,
        },
    }


def check_class4(root: Path) -> dict[str, Any]:
    sp, symbols, _coords, _vars_order = base.sympy_context()
    rows = load_class_rows(root, 4)
    eq = pb_equation_map(rows)
    x2, y2 = symbols["x2"], symbols["y2"]
    x3, y3 = symbols["x3"], symbols["y3"]
    x4, y4 = symbols["x4"], symbols["y4"]

    first = first_stage_relations(eq)
    stage1 = {x2: sp.Rational(1, 2), x3: sp.Rational(1, 2), y3: -y2}
    collinearity_equations = [
        sp.expand(eq[((0, 2), (1, 4))][0].subs(stage1)),
        sp.expand(eq[((0, 4), (1, 2))][0].subs(stage1)),
        sp.expand(eq[((0, 4), (1, 2))][1].subs(stage1)),
    ]
    basis = sp.groebner(collinearity_equations, x4, y4, y2, order="lex", domain=sp.QQ)
    coldet_234 = 2 * y2 * (x4 - sp.Rational(1, 2))
    relations = [2 * x4 - 1, y2**2 - sp.Rational(3, 4), coldet_234]
    verified = first["all_expected_relations_hold"] and all(
        ideal_contains(basis, rel) for rel in relations
    )
    return {
        "class_id": 4,
        "verified": verified,
        "mechanism": "collinear_vertices",
        "row_strings": ["".join(str(value) for value in row) for row in rows],
        "first_stage": first,
        "collinearity_stage": {
            "basis_polynomial_count": len(basis.polys),
            "contains_2x4_minus_1": ideal_contains(basis, relations[0]),
            "contains_y2_squared_minus_3_over_4": ideal_contains(basis, relations[1]),
            "contains_collinearity_determinant": ideal_contains(basis, relations[2]),
            "collinear_labels": [2, 3, 4],
        },
    }


def check_class5(root: Path) -> dict[str, Any]:
    sp, symbols, _coords, _vars_order = base.sympy_context()
    rows = load_class_rows(root, 5)
    certificate = load_certificate(root, 5)
    x2, y2 = symbols["x2"], symbols["y2"]
    subs = {
        symbols["x3"]: x2,
        symbols["y3"]: -y2,
        symbols["x6"]: 2 * x2 - symbols["x4"],
        symbols["y6"]: symbols["y4"],
    }
    eqs = [sp.expand(eq.subs(subs)) for eq in base.pb_equations(rows)]
    eqs = [eq for eq in eqs if eq != 0]
    vars_after = [
        symbols["x2"],
        symbols["y2"],
        symbols["x4"],
        symbols["y4"],
        symbols["x5"],
        symbols["y5"],
        symbols["x7"],
        symbols["y7"],
    ]
    basis = sp.groebner(eqs, *vars_after, order="lex", domain=sp.QQ)
    artifact_polys = [
        base.parse_expr(item)
        for item in certificate.get("groebner_basis_after_substitution", [])
    ]
    artifact_basis = sp.groebner(artifact_polys, *vars_after, order="lex", domain=sp.QQ)
    artifact_polys_reduce_in_computed_ideal = all(
        sp.expand(basis.reduce(poly)[1]) == 0 for poly in artifact_polys
    )
    original_equations_reduce_in_artifact_ideal = all(
        sp.expand(artifact_basis.reduce(eq)[1]) == 0 for eq in eqs
    )
    artifact_generating_set_equivalent = (
        artifact_polys_reduce_in_computed_ideal
        and original_equations_reduce_in_artifact_ideal
    )
    contains_y2 = any(
        sp.Poly(poly.as_expr(), *vars_after, domain=sp.QQ).as_expr() == y2
        for poly in basis.polys
    )
    artifact_contains_y2 = any(sp.expand(poly - y2) == 0 for poly in artifact_polys)
    verified = artifact_generating_set_equivalent and contains_y2 and artifact_contains_y2
    return {
        "class_id": 5,
        "verified": verified,
        "mechanism": "groebner_contains_y2_after_substitution",
        "row_strings": ["".join(str(value) for value in row) for row in rows],
        "substitutions": {
            "x3": "x2",
            "y3": "-y2",
            "x6": "2*x2 - x4",
            "y6": "y4",
        },
        "groebner": {
            "basis_polynomial_count": len(basis.polys),
            "artifact_generating_set_polynomial_count": len(artifact_polys),
            "artifact_polys_reduce_in_computed_ideal": artifact_polys_reduce_in_computed_ideal,
            "original_equations_reduce_in_artifact_ideal": original_equations_reduce_in_artifact_ideal,
            "artifact_generating_set_equivalent": artifact_generating_set_equivalent,
            "contains_y2": contains_y2,
            "artifact_contains_y2": artifact_contains_y2,
        },
    }


def check_all(root: Path) -> dict[str, Any]:
    class3 = check_class3(root)
    class4 = check_class4(root)
    class5 = check_class5(root)
    classes = [class3, class4, class5]
    verified = all(record["verified"] for record in classes)
    return {
        "type": "n8_residual_certificate_audit_v1",
        "verified": verified,
        "trust": "REPO_LOCAL_EXACT_OBSTRUCTION_AUDIT_PENDING_EXTERNAL_REVIEW",
        "claim_scope": (
            "Focused audit of the checked-in n=8 class 3, 4, and 5 "
            "substitution/Groebner certificates only. No general proof of "
            "Erdos Problem #97 and no counterexample are claimed."
        ),
        "class_ids": list(TARGET_CLASS_IDS),
        "classes": classes,
        "does_not_check": [
            "n=8 incidence completeness",
            "class 14 certificate",
            "external independent review",
            "general Erdos Problem #97 proof",
        ],
        "errors": [
            f"class {record['class_id']} did not verify"
            for record in classes
            if not record["verified"]
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit nonzero if verification fails.")
    parser.add_argument("--json", action="store_true", help="Print full JSON summary.")
    args = parser.parse_args(argv)

    summary = check_all(repo_root())
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        status = "verified" if summary["verified"] else "FAILED"
        mechanisms = ", ".join(record["mechanism"] for record in summary["classes"])
        print(f"n=8 residual certificate audit: {status}")
        print(f"mechanisms: {mechanisms}")
    if args.check and not summary["verified"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
