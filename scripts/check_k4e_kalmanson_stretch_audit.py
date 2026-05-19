#!/usr/bin/env python3
"""Replay K4-minus-edge stretch certificates against Kalmanson inequalities."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Iterable

Edge = tuple[int, int]
Rows = dict[int, tuple[int, int, int, int]]


def edge(i: int, j: int) -> Edge:
    return (i, j) if i < j else (j, i)


def edge_str(e: Edge) -> str:
    return f"{e[0]}{e[1]}"


@dataclass(frozen=True)
class QSqrt3:
    """An exact element of Q(sqrt(3)), represented as a + b sqrt(3)."""

    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    def __add__(self, other: QSqrt3) -> QSqrt3:
        return QSqrt3(self.a + other.a, self.b + other.b)

    def __sub__(self, other: QSqrt3) -> QSqrt3:
        return QSqrt3(self.a - other.a, self.b - other.b)

    def __neg__(self) -> QSqrt3:
        return QSqrt3(-self.a, -self.b)

    def is_zero(self) -> bool:
        return self.a == 0 and self.b == 0

    def sign(self) -> int:
        """Return the exact sign of this element."""

        a, b = self.a, self.b
        if a == 0 and b == 0:
            return 0
        if b == 0:
            return 1 if a > 0 else -1
        if a == 0:
            return 1 if b > 0 else -1
        if a > 0 and b > 0:
            return 1
        if a < 0 and b < 0:
            return -1

        lhs = a * a
        rhs = 3 * b * b
        if a > 0 and b < 0:
            return 1 if lhs > rhs else -1
        if a < 0 and b > 0:
            return 1 if rhs > lhs else -1
        raise AssertionError("unreachable sign case")

    def text(self) -> str:
        terms: list[str] = []
        if self.a:
            terms.append(str(self.a))
        if self.b == 1:
            terms.append("sqrt3")
        elif self.b == -1:
            terms.append("-sqrt3")
        elif self.b:
            terms.append(f"{self.b}*sqrt3")
        if not terms:
            return "0"

        out = terms[0]
        for term in terms[1:]:
            if term.startswith("-"):
                out += " - " + term[1:]
            else:
                out += " + " + term
        return out


ONE = QSqrt3(Fraction(1), Fraction(0))
SQRT3 = QSqrt3(Fraction(0), Fraction(1))
NEG_ONE = QSqrt3(Fraction(-1), Fraction(0))


class DSU:
    def __init__(self, items: Iterable[Edge]) -> None:
        self.parent = {x: x for x in items}

    def find(self, x: Edge) -> Edge:
        parent = self.parent[x]
        if parent != x:
            self.parent[x] = self.find(parent)
        return self.parent[x]

    def union(self, a: Edge, b: Edge) -> None:
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return
        if root_b < root_a:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a


def quotient_classes(n: int, rows: Rows) -> tuple[dict[Edge, list[Edge]], dict[Edge, Edge]]:
    all_edges = [edge(i, j) for i, j in combinations(range(n), 2)]
    dsu = DSU(all_edges)
    for i, row in rows.items():
        row_edges = [edge(i, j) for j in row]
        if len(row_edges) != 4:
            raise ValueError(f"row {i} has {len(row_edges)} witnesses, expected 4")
        base = row_edges[0]
        for row_edge in row_edges[1:]:
            dsu.union(base, row_edge)

    classes: dict[Edge, list[Edge]] = {}
    edge_root: dict[Edge, Edge] = {}
    for e in all_edges:
        root = dsu.find(e)
        edge_root[e] = root
        classes.setdefault(root, []).append(e)
    return {root: sorted(edges) for root, edges in classes.items()}, edge_root


def class_name(root: Edge) -> str:
    return "Q" + edge_str(root)


def find_k4(n: int, edges: Iterable[Edge]) -> list[tuple[int, int, int, int]]:
    edge_set = set(edges)
    hits: list[tuple[int, int, int, int]] = []
    for quad in combinations(range(n), 4):
        if all(edge(a, b) in edge_set for a, b in combinations(quad, 2)):
            hits.append(quad)
    return hits


def find_codegree_ge3(n: int, edges: Iterable[Edge]) -> list[tuple[int, int, tuple[int, ...]]]:
    edge_set = set(edges)
    hits: list[tuple[int, int, tuple[int, ...]]] = []
    for a, b in combinations(range(n), 2):
        common = tuple(
            v
            for v in range(n)
            if v not in (a, b)
            and edge(a, v) in edge_set
            and edge(b, v) in edge_set
        )
        if len(common) >= 3:
            hits.append((a, b, common))
    return hits


@dataclass(frozen=True)
class K4eRelation:
    source: Edge
    target: Edge
    quad: tuple[int, int, int, int]
    missing: Edge
    present: tuple[Edge, ...]


def find_k4e_relations(
    n: int,
    classes: dict[Edge, list[Edge]],
    edge_root: dict[Edge, Edge],
) -> list[K4eRelation]:
    relations: list[K4eRelation] = []
    seen: set[tuple[Edge, Edge, tuple[int, int, int, int], Edge]] = set()
    for root, class_edges in classes.items():
        edge_set = set(class_edges)
        if len(edge_set) < 5:
            continue
        for quad in combinations(range(n), 4):
            quad_edges = [edge(a, b) for a, b in combinations(quad, 2)]
            present = tuple(sorted(e for e in quad_edges if e in edge_set))
            if len(present) != 5:
                continue
            missing = next(e for e in quad_edges if e not in edge_set)
            target = edge_root[missing]
            key = (root, target, quad, missing)
            if target != root and key not in seen:
                relations.append(K4eRelation(root, target, quad, missing, present))
                seen.add(key)
    return relations


def expr_for_edge(
    e: Edge,
    edge_root: dict[Edge, Edge],
    rel: K4eRelation,
) -> dict[Edge, QSqrt3]:
    root = edge_root[e]
    if root == rel.target:
        return {rel.source: SQRT3}
    return {root: ONE}


def add_expr(
    dst: dict[Edge, QSqrt3],
    src: dict[Edge, QSqrt3],
    scale: QSqrt3,
) -> None:
    if scale not in (ONE, NEG_ONE):
        raise ValueError("only +/-1 expression scaling is supported")
    for key, value in src.items():
        scaled = value if scale == ONE else -value
        dst[key] = dst.get(key, QSqrt3()) + scaled
        if dst[key].is_zero():
            del dst[key]


def diff_for_inequality(
    lhs: tuple[Edge, Edge],
    rhs: tuple[Edge, Edge],
    edge_root: dict[Edge, Edge],
    rel: K4eRelation,
) -> dict[Edge, QSqrt3]:
    diff: dict[Edge, QSqrt3] = {}
    for e in lhs:
        add_expr(diff, expr_for_edge(e, edge_root, rel), ONE)
    for e in rhs:
        add_expr(diff, expr_for_edge(e, edge_root, rel), NEG_ONE)
    return diff


def positive_contradiction(diff: dict[Edge, QSqrt3]) -> bool:
    """Return true when LHS - RHS is positive for all positive class lengths."""

    if not diff:
        return False
    saw_positive = False
    for coeff in diff.values():
        sign = coeff.sign()
        if sign < 0:
            return False
        if sign > 0:
            saw_positive = True
    return saw_positive


@dataclass(frozen=True)
class StretchCertificate:
    rel: K4eRelation
    quad: tuple[int, int, int, int]
    kind: str
    lhs: tuple[Edge, Edge]
    rhs: tuple[Edge, Edge]
    diff: dict[Edge, QSqrt3]


def kalmanson_stretch_certificates(
    n: int,
    edge_root: dict[Edge, Edge],
    relations: list[K4eRelation],
) -> list[StretchCertificate]:
    certs: list[StretchCertificate] = []
    for rel in relations:
        for i, j, k, m in combinations(range(n), 4):
            inequalities = [
                ("K1", (edge(i, j), edge(k, m)), (edge(i, k), edge(j, m))),
                ("K2", (edge(i, m), edge(j, k)), (edge(i, k), edge(j, m))),
            ]
            for kind, lhs, rhs in inequalities:
                diff = diff_for_inequality(lhs, rhs, edge_root, rel)
                if positive_contradiction(diff):
                    certs.append(StretchCertificate(rel, (i, j, k, m), kind, lhs, rhs, diff))
    return certs


@dataclass(frozen=True)
class PatternAudit:
    name: str
    n: int
    classes: dict[Edge, list[Edge]]
    edge_root: dict[Edge, Edge]
    k4_obstructions: list[tuple[Edge, tuple[int, int, int, int]]]
    codegree_obstructions: list[tuple[Edge, tuple[int, int, tuple[int, ...]]]]
    k4e_relations: list[K4eRelation]
    stretch_certificates: list[StretchCertificate]


def audit_pattern(name: str, n: int, rows: Rows) -> PatternAudit:
    classes, edge_root = quotient_classes(n, rows)
    k4_obstructions = [
        (root, quad)
        for root, edges in classes.items()
        for quad in find_k4(n, edges)
    ]
    codegree_obstructions = [
        (root, hit)
        for root, edges in classes.items()
        for hit in find_codegree_ge3(n, edges)
    ]
    relations = find_k4e_relations(n, classes, edge_root)
    certs = kalmanson_stretch_certificates(n, edge_root, relations)
    return PatternAudit(
        name=name,
        n=n,
        classes=classes,
        edge_root=edge_root,
        k4_obstructions=k4_obstructions,
        codegree_obstructions=codegree_obstructions,
        k4e_relations=relations,
        stretch_certificates=certs,
    )


def format_edges(edges: Iterable[Edge]) -> str:
    return " ".join(edge_str(e) for e in sorted(edges))


def format_expr_terms(
    terms: tuple[Edge, Edge],
    edge_root: dict[Edge, Edge],
    rel: K4eRelation,
) -> str:
    pieces: list[str] = []
    for e in terms:
        root = edge_root[e]
        if root == rel.target:
            pieces.append(f"d{edge_str(e)}=sqrt3*{class_name(rel.source)}")
        else:
            pieces.append(f"d{edge_str(e)}={class_name(root)}")
    return " + ".join(pieces)


def format_diff(diff: dict[Edge, QSqrt3]) -> str:
    if not diff:
        return "0"
    return " + ".join(
        f"({coeff.text()})*{class_name(root)}"
        for root, coeff in sorted(diff.items())
    )


def render_text(audit: PatternAudit, max_certs: int = 5) -> str:
    lines: list[str] = [f"=== {audit.name} ==="]
    nontrivial = [
        (root, edges)
        for root, edges in audit.classes.items()
        if len(edges) > 1
    ]
    nontrivial.sort(key=lambda item: (-len(item[1]), item[0]))
    lines.append(
        f"n={audit.n}; quotient classes={len(audit.classes)}; "
        f"nontrivial classes={len(nontrivial)}"
    )
    for root, edges in nontrivial:
        lines.append(f"  {class_name(root)} size {len(edges)}: {format_edges(edges)}")

    lines.append(f"K4 obstructions: {len(audit.k4_obstructions)}")
    for root, quad in audit.k4_obstructions[:max_certs]:
        lines.append(f"  {class_name(root)} contains K4 on {quad}")

    lines.append(f"K2,3/codegree>=3 obstructions: {len(audit.codegree_obstructions)}")
    for root, (a, b, common) in audit.codegree_obstructions[:max_certs]:
        lines.append(f"  {class_name(root)} vertices {a},{b} share {common}")

    lines.append(f"K4-e relations extracted: {len(audit.k4e_relations)}")
    for rel in audit.k4e_relations[:max_certs]:
        lines.append(
            f"  {class_name(rel.target)} = sqrt3*{class_name(rel.source)} "
            f"from quad {rel.quad}, missing {edge_str(rel.missing)}, "
            f"present {format_edges(rel.present)}"
        )

    lines.append(
        "K4-e/Kalmanson stretch contradictions: "
        f"{len(audit.stretch_certificates)}"
    )
    for cert in audit.stretch_certificates[:max_certs]:
        rel = cert.rel
        lines.append("  CERT")
        lines.append(
            f"    relation: {class_name(rel.target)} = sqrt3*"
            f"{class_name(rel.source)} from K4-e quad {rel.quad} "
            f"missing {edge_str(rel.missing)}"
        )
        lines.append(
            f"    {cert.kind} on cyclic quad {cert.quad}: "
            f"d{edge_str(cert.lhs[0])}+d{edge_str(cert.lhs[1])} <= "
            f"d{edge_str(cert.rhs[0])}+d{edge_str(cert.rhs[1])}"
        )
        lines.append(
            "    LHS substitutions: "
            f"{format_expr_terms(cert.lhs, audit.edge_root, rel)}"
        )
        lines.append(
            "    RHS substitutions: "
            f"{format_expr_terms(cert.rhs, audit.edge_root, rel)}"
        )
        lines.append(f"    LHS-RHS = {format_diff(cert.diff)} > 0")
    return "\n".join(lines)


def rel_json(rel: K4eRelation) -> dict[str, object]:
    return {
        "source": class_name(rel.source),
        "target": class_name(rel.target),
        "quad": list(rel.quad),
        "missing": edge_str(rel.missing),
        "present": [edge_str(e) for e in rel.present],
    }


def cert_json(cert: StretchCertificate) -> dict[str, object]:
    rel = cert.rel
    return {
        "relation": rel_json(rel),
        "quad": list(cert.quad),
        "kind": cert.kind,
        "lhs": [edge_str(e) for e in cert.lhs],
        "rhs": [edge_str(e) for e in cert.rhs],
        "diff": {
            class_name(root): coeff.text()
            for root, coeff in sorted(cert.diff.items())
        },
    }


def audit_json(audit: PatternAudit) -> dict[str, object]:
    nontrivial = {
        class_name(root): [edge_str(e) for e in edges]
        for root, edges in sorted(audit.classes.items())
        if len(edges) > 1
    }
    return {
        "name": audit.name,
        "n": audit.n,
        "status": "EXACT_FIXED_PATTERN_AUDIT",
        "claim_scope": (
            "Kills only the listed selected-witness pattern and fixed cyclic "
            "order; not an n=10 exclusion."
        ),
        "quotient_classes": len(audit.classes),
        "nontrivial_classes": nontrivial,
        "k4_obstructions": len(audit.k4_obstructions),
        "codegree_obstructions": len(audit.codegree_obstructions),
        "k4e_relations": [rel_json(rel) for rel in audit.k4e_relations],
        "stretch_certificates": [
            cert_json(cert)
            for cert in audit.stretch_certificates
        ],
    }


PATTERNS: dict[str, tuple[int, Rows]] = {
    "n10_frontier": (
        10,
        {
            0: (1, 4, 5, 8),
            1: (2, 3, 6, 9),
            2: (0, 1, 3, 4),
            3: (1, 2, 5, 6),
            4: (0, 3, 5, 7),
            5: (0, 4, 6, 8),
            6: (2, 4, 7, 9),
            7: (3, 5, 8, 9),
            8: (1, 6, 7, 9),
            9: (0, 2, 7, 8),
        },
    ),
    "case2_diagnostic": (
        9,
        {
            0: (1, 3, 4, 6),
            1: (3, 6, 7, 8),
            2: (1, 3, 4, 6),
            3: (1, 5, 6, 7),
            4: (2, 3, 7, 8),
            5: (1, 2, 6, 8),
            6: (1, 3, 4, 8),
            7: (1, 2, 3, 5),
            8: (0, 2, 3, 5),
        },
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pattern",
        choices=sorted(PATTERNS),
        action="append",
        help="Pattern to audit. Defaults to all registered patterns.",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    names = args.pattern or sorted(PATTERNS)
    audits = []
    for name in names:
        n, rows = PATTERNS[name]
        audits.append(audit_pattern(name, n, rows))

    if args.assert_expected:
        expected = {
            "n10_frontier": (0, 0, 2, 3),
            "case2_diagnostic": (0, 0, 3, 24),
        }
        for audit in audits:
            want = expected[audit.name]
            got = (
                len(audit.k4_obstructions),
                len(audit.codegree_obstructions),
                len(audit.k4e_relations),
                len(audit.stretch_certificates),
            )
            if got != want:
                raise AssertionError(f"{audit.name}: expected {want}, got {got}")

    if args.json:
        print(json.dumps([audit_json(audit) for audit in audits], indent=2))
    else:
        for index, audit in enumerate(audits):
            if index:
                print()
            print(render_text(audit))
        if args.assert_expected:
            print("OK: expected K4-e/Kalmanson stretch audit verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
