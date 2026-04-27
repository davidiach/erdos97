#!/usr/bin/env python3
"""Exact n=8 survivor-class obstruction checks for Erdos Problem #97.

This script is intentionally proof-hygiene oriented:
- no floating-point equality;
- no numerical optimization;
- cyclic-order tests are purely finite combinatorics;
- polynomial checks use SymPy over QQ when SymPy is available.

The bundled JSON list is the 15-class survivor list produced by the n=8
incidence-completeness checker, up to simultaneous relabeling. External
paper-style claims should still receive independent review.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict, deque
from functools import lru_cache
from pathlib import Path
from typing import Iterable

N = 8
Y2_SPAN_CLASS_IDS = {0, 1, 2, 6, 7, 8, 9, 10, 11, 13}
CYCLIC_KILLED_IDS = {12}
EXPECTED_COMPATIBLE_COUNTS = {
    0: 2520,
    1: 280,
    2: 21,
    3: 2520,
    4: 280,
    5: 4,
    6: 280,
    7: 50,
    8: 538,
    9: 100,
    10: 74,
    11: 44,
    12: 0,
    13: 280,
    14: 72,
}
ARCHIVE_ID_TO_RECONSTRUCTED_ID = {
    2: 12,
    7: 11,
    8: 10,
    9: 14,
    19: 7,
    28: 9,
    51: 5,
    70: 6,
    88: 8,
    92: 2,
    117: 4,
    120: 1,
    134: 13,
    138: 3,
    139: 0,
}
EXPECTED_ARCHIVE_COMPATIBLE_COUNTS = {
    archive_id: EXPECTED_COMPATIBLE_COUNTS[reconstructed_id]
    for archive_id, reconstructed_id in ARCHIVE_ID_TO_RECONSTRUCTED_ID.items()
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def chord(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def all_chords() -> list[tuple[int, int]]:
    return [chord(a, b) for a in range(N) for b in range(a + 1, N)]


def witnesses(rows: list[list[int]], i: int) -> list[int]:
    return [j for j, value in enumerate(rows[i]) if value]


def phi_edges(rows: list[list[int]]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    w = [set(witnesses(rows, i)) for i in range(N)]
    edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for i in range(N):
        for j in range(i + 1, N):
            inter = sorted(w[i] & w[j])
            if len(inter) == 2:
                edges.append((chord(i, j), chord(inter[0], inter[1])))
    return edges


def forced_perp_graph(rows: list[list[int]]) -> dict[tuple[int, int], set[tuple[int, int]]]:
    graph = {c: set() for c in all_chords()}
    for src, dst in phi_edges(rows):
        graph[src].add(dst)
        graph[dst].add(src)
    return graph


def bipartite_color_classes(
    graph: dict[tuple[int, int], set[tuple[int, int]]]
) -> tuple[bool, list[list[tuple[int, int]]]]:
    """Return (is_bipartite, same-color classes of size >= 2)."""
    color: dict[tuple[int, int], int] = {}
    classes: list[list[tuple[int, int]]] = []
    for start in sorted(graph):
        if start in color:
            continue
        color[start] = 0
        component = [start]
        q: deque[tuple[int, int]] = deque([start])
        ok = True
        while q:
            u = q.popleft()
            for v in graph[u]:
                if v not in color:
                    color[v] = 1 - color[u]
                    component.append(v)
                    q.append(v)
                elif color[v] == color[u]:
                    ok = False
        if not ok:
            return False, []
        by_color: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for c in component:
            by_color[color[c]].append(c)
        for same_color in by_color.values():
            if len(same_color) >= 2:
                classes.append(sorted(same_color))
    return True, classes


def normalized_cyclic_orders() -> Iterable[tuple[int, ...]]:
    # Fix rotation by putting 0 first; quotient reversal by order[1] < order[-1].
    for tail in itertools.permutations(range(1, N)):
        order = (0,) + tail
        if order[1] < order[-1]:
            yield order


def crosses(c1: tuple[int, int], c2: tuple[int, int], pos: dict[int, int]) -> bool:
    a, b = c1
    c, d = c2
    if len({a, b, c, d}) < 4:
        return False
    a_pos, b_pos, c_pos, d_pos = pos[a], pos[b], pos[c], pos[d]
    if a_pos > b_pos:
        a_pos, b_pos = b_pos, a_pos
    c_inside = a_pos < c_pos < b_pos
    d_inside = a_pos < d_pos < b_pos
    return c_inside != d_inside


def same_color_classes_are_noncrossing(
    same_color_classes: list[list[tuple[int, int]]],
    order: tuple[int, ...],
) -> bool:
    pos = {label: idx for idx, label in enumerate(order)}
    for cls in same_color_classes:
        used: set[int] = set()
        for a, b in cls:
            if a in used or b in used:
                return False
            used.add(a)
            used.add(b)
        for left, right in itertools.combinations(cls, 2):
            if crosses(left, right, pos):
                return False
    return True


def compatible_orders(rows: list[list[int]]) -> list[tuple[int, ...]]:
    is_bipartite, classes = bipartite_color_classes(forced_perp_graph(rows))
    if not is_bipartite:
        return []
    return [
        order
        for order in normalized_cyclic_orders()
        if same_color_classes_are_noncrossing(classes, order)
    ]


def load_survivors(root: Path) -> list[dict]:
    path = root / "data" / "incidence" / "n8_reconstructed_15_survivors.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def sympy_context():
    try:
        import sympy as sp
    except ImportError as exc:  # pragma: no cover - depends on optional dev dep
        raise SystemExit("SymPy is required for polynomial checks: pip install sympy") from exc

    symbols = {}
    for i in range(2, N):
        symbols[f"x{i}"] = sp.symbols(f"x{i}")
        symbols[f"y{i}"] = sp.symbols(f"y{i}")
    coords = {0: (sp.Integer(0), sp.Integer(0)), 1: (sp.Integer(1), sp.Integer(0))}
    for i in range(2, N):
        coords[i] = (symbols[f"x{i}"], symbols[f"y{i}"])
    var_list = []
    for i in range(2, N):
        var_list.extend([symbols[f"x{i}"], symbols[f"y{i}"]])
    return sp, symbols, coords, var_list


def pb_equations(rows: list[list[int]]):
    eqs = []
    for dot, bis in pb_equation_map(rows).values():
        eqs.extend([dot, bis])
    return eqs


def pb_equation_map(rows: list[list[int]]):
    sp, _symbols, p, _vars = sympy_context()
    eqs = {}
    for (i, j), (a, b) in phi_edges(rows):
        pix, piy = p[i]
        pjx, pjy = p[j]
        pax, pay = p[a]
        pbx, pby = p[b]
        dot = sp.expand((pix - pjx) * (pax - pbx) + (piy - pjy) * (pay - pby))
        # This is twice the midpoint equation, avoiding denominators:
        # det(p_j - p_i, p_a + p_b - 2 p_i) = 0.
        bis = sp.expand((pjx - pix) * (pay + pby - 2 * piy) - (pjy - piy) * (pax + pbx - 2 * pix))
        eqs[((i, j), (a, b))] = (dot, bis)
    return eqs


def ed_equations(rows: list[list[int]]):
    sp, _symbols, p, _vars = sympy_context()
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


def ed_equation_records(rows: list[list[int]]) -> list[dict]:
    sp, _symbols, p, _vars = sympy_context()
    records = []
    for i in range(N):
        w = witnesses(rows, i)
        base = w[0]
        pix, piy = p[i]
        pbx, pby = p[base]
        base_dist = (pix - pbx) ** 2 + (piy - pby) ** 2
        for other in w[1:]:
            pox, poy = p[other]
            equation = sp.expand((pix - pox) ** 2 + (piy - poy) ** 2 - base_dist)
            records.append({
                "center": i,
                "base": base,
                "other": other,
                "equation": str(equation),
            })
    return records


def in_rational_span(polys, target) -> bool:
    sp, _symbols, _coords, var_list = sympy_context()
    all_polys = list(polys) + [target]
    monoms: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()
    rows = []
    for poly in all_polys:
        p = sp.Poly(poly, *var_list, domain=sp.QQ)
        terms = dict(p.terms())
        row_terms = {}
        for monom, coeff in terms.items():
            if monom not in seen:
                seen.add(monom)
                monoms.append(monom)
            row_terms[monom] = coeff
        rows.append(row_terms)
    matrix_rows = [[row.get(monom, sp.Integer(0)) for monom in monoms] for row in rows]
    matrix_without_target = sp.Matrix(matrix_rows[:-1])
    matrix_with_target = sp.Matrix(matrix_rows)
    return matrix_without_target.rank() == matrix_with_target.rank()


def ideal_contains(groebner_basis, expr) -> bool:
    sp, _symbols, _coords, _vars = sympy_context()
    return sp.expand(groebner_basis.reduce(expr)[1]) == 0


def check_cyclic_counts(survivors: list[dict]) -> dict[int, int]:
    counts = {}
    for cls in survivors:
        counts[int(cls["id"])] = len(compatible_orders(cls["rows"]))
    return counts


def compatible_orders_artifact(survivors: list[dict]) -> dict:
    orders_by_class_id = {}
    counts = {}
    for cls in survivors:
        class_id = str(int(cls["id"]))
        orders = [list(order) for order in compatible_orders(cls["rows"])]
        counts[class_id] = len(orders)
        orders_by_class_id[class_id] = orders
    return {
        "normalization": "order[0]=0, order[1]<order[-1]; modulo rotation and reversal",
        "counts": counts,
        "orders_by_class_id": orders_by_class_id,
    }


def system_record(cls: dict) -> dict:
    rows = cls["rows"]
    pb_map = pb_equation_map(rows)
    orders = [list(order) for order in compatible_orders(rows)]
    return {
        "class_id": int(cls["id"]),
        "rows": rows,
        "W": {str(i): witnesses(rows, i) for i in range(N)},
        "compatible_cyclic_orders_count": len(orders),
        "compatible_cyclic_orders": orders,
        "phi_edges_count": len(pb_map),
        "phi_edges_with_perpendicular_bisector_equations": [
            {
                "source": list(source),
                "target": list(target),
                "dot_equation": str(dot),
                "bisector_midpoint_equation": str(bisector),
            }
            for (source, target), (dot, bisector) in pb_map.items()
        ],
        "full_equal_distance_equations": ed_equation_records(rows),
    }


def check_exact_analysis_artifact(survivors: list[dict], path: Path, counts: dict[int, int]) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    killed = sorted(class_id for class_id, count in counts.items() if count == 0)
    remaining = sorted(class_id for class_id, count in counts.items() if count != 0)

    cyclic_filter_ok = data.get("cyclic_filter") == {
        "total_classes": len(survivors),
        "killed_count": len(killed),
        "killed_ids": killed,
        "remaining_count": len(remaining),
        "remaining_ids": remaining,
        "compatible_order_counts": {str(k): v for k, v in counts.items()},
    }

    systems = data.get("systems_for_remaining_after_cyclic", {})
    regenerated_systems = {
        str(int(cls["id"])): system_record(cls)
        for cls in survivors
        if counts[int(cls["id"])] != 0
    }
    systems_ok = systems == regenerated_systems

    contradictions = data.get("contradictions", {})
    contradiction_ids_ok = (
        contradictions.get("cyclic_order_noncrossing", {}).get("killed_ids") == killed
        and contradictions.get("pb_linear_span_y2_zero", {}).get("killed_ids")
        == sorted(Y2_SPAN_CLASS_IDS)
        and contradictions.get("class_3", {}).get("killed_ids") == [3]
        and contradictions.get("class_4", {}).get("killed_ids") == [4]
        and contradictions.get("class_5", {}).get("killed_ids") == [5]
        and contradictions.get("class_14", {}).get("killed_ids") == [14]
    )
    final_status_ok = data.get("final_status") == {
        "remaining_after_exact_geometry": [],
        "all_reconstructed_15_rejected": True,
        "numerical_search_used": False,
    }
    return {
        "path": str(path),
        "cyclic_filter_verified": cyclic_filter_ok,
        "systems_verified": systems_ok,
        "contradiction_ids_verified": contradiction_ids_ok,
        "final_status_verified": final_status_ok,
        "verified": (
            cyclic_filter_ok
            and systems_ok
            and contradiction_ids_ok
            and final_status_ok
        ),
    }


def check_y2_span(survivors: list[dict]) -> dict[int, bool]:
    sp, symbols, _coords, _vars = sympy_context()
    out = {}
    for cls in survivors:
        class_id = int(cls["id"])
        if class_id in Y2_SPAN_CLASS_IDS:
            out[class_id] = in_rational_span(pb_equations(cls["rows"]), symbols["y2"])
    return out


def check_class3_duplicate_certificate(survivors: list[dict]) -> bool:
    sp, symbols, _coords, _vars = sympy_context()
    rows = next(cls["rows"] for cls in survivors if int(cls["id"]) == 3)
    eq = pb_equation_map(rows)
    x2, y2 = symbols["x2"], symbols["y2"]
    x3, y3 = symbols["x3"], symbols["y3"]
    x4, y4 = symbols["x4"], symbols["y4"]
    x7, y7 = symbols["x7"], symbols["y7"]

    first = [
        eq[((0, 1), (2, 3))][0],
        eq[((0, 1), (2, 3))][1],
        eq[((2, 3), (0, 1))][1],
    ]
    first_basis = sp.groebner(first, x3, y3, x2, y2, order="lex", domain=sp.QQ)
    if not all(
        ideal_contains(first_basis, rel)
        for rel in [x3 - x2, y3 + y2, y2 * (2 * x2 - 1)]
    ):
        return False

    stage1 = {x2: sp.Rational(1, 2), x3: sp.Rational(1, 2), y3: -y2}
    second = [
        sp.expand(poly.subs(stage1))
        for edge in [((0, 2), (1, 4)), ((1, 4), (0, 2))]
        for poly in eq[edge]
    ]
    second_basis = sp.groebner(second, x4, y4, y2, order="lex", domain=sp.QQ)
    if not all(
        ideal_contains(second_basis, rel)
        for rel in [y4 - y2, x4 + 2 * y2**2 - 1, y2 * (4 * y2**2 - 3)]
    ):
        return False

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
    return ideal_contains(third_basis, x7) and ideal_contains(third_basis, y7)


def check_class4_collinearity_certificate(survivors: list[dict]) -> bool:
    sp, symbols, _coords, _vars = sympy_context()
    rows = next(cls["rows"] for cls in survivors if int(cls["id"]) == 4)
    eq = pb_equation_map(rows)
    x2, y2 = symbols["x2"], symbols["y2"]
    x3, y3 = symbols["x3"], symbols["y3"]
    x4, y4 = symbols["x4"], symbols["y4"]

    first = [
        eq[((0, 1), (2, 3))][0],
        eq[((0, 1), (2, 3))][1],
        eq[((2, 3), (0, 1))][1],
    ]
    first_basis = sp.groebner(first, x3, y3, x2, y2, order="lex", domain=sp.QQ)
    if not all(
        ideal_contains(first_basis, rel)
        for rel in [x3 - x2, y3 + y2, y2 * (2 * x2 - 1)]
    ):
        return False

    stage1 = {x2: sp.Rational(1, 2), x3: sp.Rational(1, 2), y3: -y2}
    collinearity_equations = [
        sp.expand(eq[((0, 2), (1, 4))][0].subs(stage1)),
        sp.expand(eq[((0, 4), (1, 2))][0].subs(stage1)),
        sp.expand(eq[((0, 4), (1, 2))][1].subs(stage1)),
    ]
    basis = sp.groebner(collinearity_equations, x4, y4, y2, order="lex", domain=sp.QQ)
    coldet_234 = 2 * y2 * (x4 - sp.Rational(1, 2))
    return all(
        ideal_contains(basis, rel)
        for rel in [2 * x4 - 1, y2**2 - sp.Rational(3, 4), coldet_234]
    )


def check_class5_groebner(survivors: list[dict]) -> bool:
    sp, symbols, _coords, var_list = sympy_context()
    rows = next(cls["rows"] for cls in survivors if int(cls["id"]) == 5)
    x2, y2 = symbols["x2"], symbols["y2"]
    subs = {
        symbols["x3"]: x2,
        symbols["y3"]: -y2,
        symbols["x6"]: 2 * x2 - symbols["x4"],
        symbols["y6"]: symbols["y4"],
    }
    eqs = [sp.expand(eq.subs(subs)) for eq in pb_equations(rows)]
    eqs = [eq for eq in eqs if eq != 0]
    vars_after = [
        symbols["x2"], symbols["y2"],
        symbols["x4"], symbols["y4"],
        symbols["x5"], symbols["y5"],
        symbols["x7"], symbols["y7"],
    ]
    basis = sp.groebner(eqs, *vars_after, order="lex", domain=sp.QQ)
    return any(sp.Poly(g, *vars_after, domain=sp.QQ).as_expr() == y2 for g in basis.polys)


def check_class14_certificate(survivors: list[dict]) -> dict[str, bool]:
    """Verify the exact PB+ED basis and strict-interior branches for class 14."""
    sp, symbols, _coords, _vars = sympy_context()
    rows = next(cls["rows"] for cls in survivors if int(cls["id"]) == 14)
    eqs = pb_equations(rows) + ed_equations(rows)
    names = [
        "x6", "y6", "y7", "x2", "y2", "x3",
        "y3", "x4", "y4", "x5", "y5", "x7",
    ]
    vars_order = [symbols[name] for name in names]
    basis = sp.groebner(eqs, *vars_order, order="lex", domain=sp.QQ)

    def monic(expr):
        return sp.factor(sp.Poly(expr, *vars_order, domain=sp.QQ).monic().as_expr())

    basis_exprs = {monic(g.as_expr()) for g in basis.polys}
    x2, x3, y5 = symbols["x2"], symbols["x3"], symbols["y5"]
    x4, y4 = symbols["x4"], symbols["y4"]
    x5 = symbols["x5"]
    x6, y6 = symbols["x6"], symbols["y6"]
    x7, y7 = symbols["x7"], symbols["y7"]
    y2, y3 = symbols["y2"], symbols["y3"]
    expected_basis = {
        monic(2 * x2 - 1),
        monic(2 * x7 - 1),
        monic(2 * y3 - y5),
        monic(4 * x3**2 - 3),
        monic((y5 - 1) * (y5 + 1)),
        monic(y5 - 2 * y6),
        monic(-x3 * y5 + y2),
        monic(x3 + x6 - 1),
        monic(x3 * y5 - y5 + y7),
        monic(x4),
        monic(x5 - 1),
        monic(y4 - y5),
    }
    basis_verified = basis_exprs == expected_basis

    a = sp.sqrt(3) / 2
    branches = [
        (
            {
                x2: sp.Rational(1, 2),
                y2: -a,
                x3: -a,
                y3: sp.Rational(1, 2),
                x4: 0,
                y4: 1,
                x5: 1,
                y5: 1,
                x6: 1 + a,
                y6: sp.Rational(1, 2),
                x7: sp.Rational(1, 2),
                y7: 1 + a,
            },
            [3, 2, 6, 7],
        ),
        (
            {
                x2: sp.Rational(1, 2),
                y2: a,
                x3: -a,
                y3: -sp.Rational(1, 2),
                x4: 0,
                y4: -1,
                x5: 1,
                y5: -1,
                x6: 1 + a,
                y6: -sp.Rational(1, 2),
                x7: sp.Rational(1, 2),
                y7: -1 - a,
            },
            [3, 7, 6, 2],
        ),
        (
            {
                x2: sp.Rational(1, 2),
                y2: -a,
                x3: a,
                y3: -sp.Rational(1, 2),
                x4: 0,
                y4: -1,
                x5: 1,
                y5: -1,
                x6: 1 - a,
                y6: -sp.Rational(1, 2),
                x7: sp.Rational(1, 2),
                y7: -1 + a,
            },
            [0, 1, 5, 4],
        ),
        (
            {
                x2: sp.Rational(1, 2),
                y2: a,
                x3: a,
                y3: sp.Rational(1, 2),
                x4: 0,
                y4: 1,
                x5: 1,
                y5: 1,
                x6: 1 - a,
                y6: sp.Rational(1, 2),
                x7: sp.Rational(1, 2),
                y7: 1 - a,
            },
            [0, 1, 5, 4],
        ),
    ]

    def branch_points(subs):
        points = {0: (sp.Integer(0), sp.Integer(0)), 1: (sp.Integer(1), sp.Integer(0))}
        for i in range(2, N):
            points[i] = (subs[symbols[f"x{i}"]], subs[symbols[f"y{i}"]])
        return points

    def orientation(points, left: int, right: int, test: int):
        px, py = points[left]
        qx, qy = points[right]
        rx, ry = points[test]
        return sp.simplify((qx - px) * (ry - py) - (qy - py) * (rx - px))

    def all_strict_same_sign(values) -> bool:
        simplified = [sp.simplify(value) for value in values]
        return all(value.is_positive for value in simplified) or all(value.is_negative for value in simplified)

    branches_solve = True
    strict_interior = True
    for subs, hull in branches:
        if any(sp.simplify(eq.subs(subs)) != 0 for eq in eqs):
            branches_solve = False
        points = branch_points(subs)
        hull_turns = [
            orientation(points, hull[i], hull[(i + 1) % len(hull)], hull[(i + 2) % len(hull)])
            for i in range(len(hull))
        ]
        if not all_strict_same_sign(hull_turns):
            strict_interior = False
        for label in sorted(set(range(N)) - set(hull)):
            edge_sides = [
                orientation(points, hull[i], hull[(i + 1) % len(hull)], label)
                for i in range(len(hull))
            ]
            if not all_strict_same_sign(edge_sides):
                strict_interior = False

    return {
        "groebner_basis_verified": basis_verified,
        "branches_solve_pb_ed": branches_solve,
        "all_branches_have_four_hull_vertices": strict_interior,
    }


def selected_pairs(rows: list[list[int]]) -> set[tuple[int, int]]:
    pairs = set()
    for i, row in enumerate(rows):
        if len(row) == N and all(value in (0, 1, False, True) for value in row):
            selected = [j for j, value in enumerate(row) if value]
        else:
            selected = [int(value) for value in row]
        pairs.update((i, j) for j in selected)
    return pairs


def matrix_key(pairs: set[tuple[int, int]]) -> tuple[str, ...]:
    return tuple(
        "".join("1" if (i, j) in pairs else "0" for j in range(N))
        for i in range(N)
    )


def canonical_key(pairs: set[tuple[int, int]]) -> tuple[str, ...]:
    best = None
    for perm in itertools.permutations(range(N)):
        relabeled = {(perm[i], perm[j]) for i, j in pairs}
        key = matrix_key(relabeled)
        if best is None or key < best:
            best = key
    assert best is not None
    return best


def load_provenance_classes(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    for key in ["classes", "survivor_classes"]:
        if key in data:
            return data[key]
    raise ValueError(f"{path} does not contain classes or survivor_classes")


def check_provenance_mapping(survivors: list[dict], path: Path) -> dict:
    source_classes = load_provenance_classes(path)
    reconstructed_by_key = {}
    for cls in survivors:
        reconstructed_by_key[canonical_key(selected_pairs(cls["rows"]))] = int(cls["id"])

    archive_to_reconstructed = {}
    compatible_counts_ok = True
    source_keys = set()
    for cls in source_classes:
        archive_id = int(cls["id"])
        key = canonical_key(selected_pairs(cls["rows"]))
        source_keys.add(key)
        if key in reconstructed_by_key:
            archive_to_reconstructed[archive_id] = reconstructed_by_key[key]
        count = cls.get("compatible_cyclic_orders_count")
        if count is not None and count != EXPECTED_ARCHIVE_COMPATIBLE_COUNTS.get(archive_id):
            compatible_counts_ok = False

    sets_equal = set(reconstructed_by_key) == source_keys
    expected_mapping_verified = archive_to_reconstructed == ARCHIVE_ID_TO_RECONSTRUCTED_ID
    return {
        "path": str(path),
        "source_classes": len(source_classes),
        "source_unique_canonical_classes": len(source_keys),
        "reconstructed_unique_canonical_classes": len(reconstructed_by_key),
        "sets_equal": sets_equal,
        "archive_id_to_reconstructed_id": dict(sorted(archive_to_reconstructed.items())),
        "expected_mapping_verified": expected_mapping_verified,
        "compatible_counts_verified": compatible_counts_ok,
        "verified": sets_equal and expected_mapping_verified and compatible_counts_ok,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="assert expected exact fingerprints")
    parser.add_argument("--json", action="store_true", help="print summary JSON")
    parser.add_argument(
        "--provenance-json",
        type=Path,
        help="optional archived survivor JSON to compare up to simultaneous relabeling",
    )
    parser.add_argument(
        "--check-compatible-orders-data",
        type=Path,
        help="compare checked-in compatible-order JSON against regenerated data",
    )
    parser.add_argument(
        "--check-exact-analysis-data",
        type=Path,
        help="check regenerated exact-analysis fields against the checked-in JSON",
    )
    args = parser.parse_args()

    root = repo_root()
    survivors = load_survivors(root)
    counts = check_cyclic_counts(survivors)
    killed = sorted(k for k, v in counts.items() if v == 0)
    y2_span = check_y2_span(survivors)
    class3 = check_class3_duplicate_certificate(survivors)
    class4 = check_class4_collinearity_certificate(survivors)
    class5 = check_class5_groebner(survivors)
    class14 = check_class14_certificate(survivors)
    provenance = check_provenance_mapping(survivors, args.provenance_json) if args.provenance_json else None
    compatible_orders_check = None
    if args.check_compatible_orders_data:
        checked_in_compatible_orders = json.loads(args.check_compatible_orders_data.read_text(encoding="utf-8"))
        compatible_orders_check = {
            "path": str(args.check_compatible_orders_data),
            "verified": checked_in_compatible_orders == compatible_orders_artifact(survivors),
        }
    exact_analysis_check = (
        check_exact_analysis_artifact(survivors, args.check_exact_analysis_data, counts)
        if args.check_exact_analysis_data
        else None
    )

    summary = {
        "survivor_classes": len(survivors),
        "cyclic_order_compatible_counts": counts,
        "cyclic_order_killed_ids": killed,
        "cyclic_order_remaining_count": len(survivors) - len(killed),
        "pb_y2_span_ids_verified": sorted(k for k, ok in y2_span.items() if ok),
        "class3_duplicate_vertex_certificate_verified": class3,
        "class4_collinearity_certificate_verified": class4,
        "class5_groebner_contains_y2_after_exact_substitution": class5,
        "class14_pb_ed_groebner_basis_verified": class14["groebner_basis_verified"],
        "class14_solution_branches_solve_pb_ed": class14["branches_solve_pb_ed"],
        "class14_strict_interior_certificate_verified": class14["all_branches_have_four_hull_vertices"],
        "provenance_identity": provenance,
        "compatible_orders_artifact": compatible_orders_check,
        "exact_analysis_artifact": exact_analysis_check,
        "status": "exact_obstruction_artifact_pending_independent_review",
    }
    if provenance and provenance["verified"]:
        summary["status"] = "exact_obstruction_artifact_archive_identity_verified_pending_independent_review"

    if args.check:
        assert len(survivors) == 15, len(survivors)
        assert counts == EXPECTED_COMPATIBLE_COUNTS, counts
        assert set(killed) == CYCLIC_KILLED_IDS, killed
        assert all(y2_span.values()), y2_span
        assert set(y2_span) == Y2_SPAN_CLASS_IDS, y2_span
        assert class3, "class 3 duplicate-vertex certificate failed"
        assert class4, "class 4 collinearity certificate failed"
        assert class5, "class 5 Groebner check did not find y2"
        assert all(class14.values()), f"class 14 certificate mismatch: {class14}"
        if provenance is not None:
            assert provenance["verified"], provenance
        if compatible_orders_check is not None:
            assert compatible_orders_check["verified"], compatible_orders_check
        if exact_analysis_check is not None:
            assert exact_analysis_check["verified"], exact_analysis_check

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        for key, value in summary.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
