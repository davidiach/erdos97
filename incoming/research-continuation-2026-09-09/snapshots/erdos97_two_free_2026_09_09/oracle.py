"""Independent arithmetic/geometry and set-based search for the partition.

This file imports neither geometry.py nor row_search.py nor verify.py.
The preceding oracle supplies a polynomial radical ring and its own ray-slot
construction. Norms are bounded using Minkowski-difference convex hulls.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path
import sys

from prior import load, archive_hash

if sys.flags.optimize:
    raise RuntimeError("Run the exact oracle without -O")
A = load("audit_one_free")
ROOT = Path(__file__).resolve().parent
BASE_SHA = "047d05149382e48b602b292df4b8fc9e2da560bb"


@lru_cache(maxsize=1)
def context():
    R, points, previous, slots, edges = A.context()
    triangles = tuple(A.initial_triangle(points, k) for k in range(9))
    cells = tuple(row["cell"] for row in previous["slots"])
    return R, points, slots, tuple(edges), triangles, cells


@lru_cache(maxsize=None)
def incoming(triangle):
    R, points, slots, _, _, _ = context()
    return frozenset(i for i, slot in enumerate(slots)
                     if A.inside_range(A.source_range(points, slot, triangle, R)))


@lru_cache(maxsize=None)
def outgoing(triangle, old):
    R, points, slots, _, _, _ = context()
    if old is None:
        return frozenset(range(42))
    return frozenset(i for i, slot in enumerate(slots)
                     if A.inside_range(A.target_range(points, old, slot, triangle, R)))


@lru_cache(maxsize=None)
def free_edge(first, second, old):
    if old is None:
        return True
    R, points, _, _, _, _ = context()
    values = []
    for f in first:
        radius = A.distance(f, points[old])
        differences = [A.minus(g, f) for g in second]
        values.extend(A.square(d) - radius for d in differences)
        values.append(A.distance_from_origin(differences, R) - radius)
    return min(values) <= 0 <= max(values)


@lru_cache(maxsize=None)
def triangle_radial(first, second):
    R = context()[0]
    differences = [A.minus(x, y) for x in first for y in second]
    return A.distance_from_origin(differences, R), max(A.square(v) for v in differences)


@lru_cache(maxsize=None)
def slot_radial(slot, triangle):
    R, _, slots, _, _, _ = context()
    return A.radial_range(slots[slot], triangle, R)


def prune(graph, old_support):
    active = set(graph)
    while True:
        before = len(active)
        for vertex in sorted(active, reverse=True):
            if len(graph[vertex] & active) < 4 - len(old_support[vertex]):
                active.remove(vertex)
        if len(active) == before:
            return active


def covers(intervals, degree):
    # The largest lower endpoint of any common-radius set belongs to them all.
    result = set()
    for left in {bounds[0] for bounds in intervals.values()}:
        compatible = frozenset(i for i, (low, high) in intervals.items() if low <= left <= high)
        if len(compatible) >= degree:
            result.add(compatible)
    return sorted((s for s in result if not any(s < t for t in result)), key=lambda s: tuple(sorted(s)))


def model_list(first, second, cells, old_witnesses):
    _, _, slots, edges, _, slot_cells = context()
    graph = {i: set() for i in range(44)}
    for i, j in edges:
        graph[i].add(j)
    support = {i: frozenset(slot[0]) for i, slot in enumerate(slots)}
    for i, triangle, old in ((42, first, old_witnesses[0]), (43, second, old_witnesses[1])):
        support[i] = frozenset() if old is None else frozenset([old])
        for j in incoming(triangle):
            graph[j].add(i)
        graph[i].update(outgoing(triangle, old))
    if free_edge(first, second, old_witnesses[0]):
        graph[42].add(43)
    if free_edge(second, first, old_witnesses[1]):
        graph[43].add(42)
    active = prune(graph, support)
    if not {42, 43} <= active:
        return []
    partitions = []
    for i, triangle, other, old in ((42, first, second, old_witnesses[0]),
                                    (43, second, first, old_witnesses[1])):
        eligible = graph[i] & active
        if old is not None:
            partitions.append([frozenset(eligible)])
        else:
            intervals = {j: slot_radial(j, triangle) if j < 42 else triangle_radial(triangle, other)
                         for j in eligible}
            partitions.append(covers(intervals, 4))
    ranks = {v: 2 * k for k, v in enumerate(A.ORDER)}
    ranks.update({9 + i: 2 * cell + 1 for i, cell in enumerate(slot_cells)})
    ranks.update({51: 2 * cells[0] + 1, 52: 2 * cells[1] + 1})
    result = []
    for left, right in product(*partitions):
        restricted = {i: set(targets) for i, targets in graph.items()}
        restricted[42] = set(left)
        restricted[43] = set(right)
        active = prune(restricted, support)
        if not {42, 43} <= active:
            continue
        result.append((
            {i: frozenset(restricted[i] & active) for i in sorted(active)},
            {i: support[i] for i in sorted(active)}, ranks,
        ))
    return result


def interlace_possible(ranks, i, j, a, b):
    # A cyclic sequence respects weak ranks exactly when it has at most one
    # strict cyclic descent. This differs from enumerating all 24 permutations.
    for sequence in ((i, a, j, b), (i, b, j, a)):
        values = [ranks[k] for k in sequence]
        descents = sum(values[k] > values[(k + 1) % 4] for k in range(4))
        if descents <= 1:
            return True
    return False


def metric_cancelled(rows, ranks, old_count=9):
    """Independent connected-component quotient and signed-multiset test."""
    links = {}
    labels = set(range(old_count))
    for source, witnesses in rows.items():
        labels.add(source)
        labels.update(witnesses)
        chords = [tuple(sorted((source, target))) for target in witnesses]
        for edge in chords:
            links.setdefault(edge, set()).update(chords)
    component = {}
    for start in sorted(links, reverse=True):
        if start in component:
            continue
        stack = [start]
        found = set()
        while stack:
            edge = stack.pop()
            if edge in found:
                continue
            found.add(edge)
            stack.extend(links[edge] - found)
        name = max(found)
        for edge in found:
            component[edge] = name
    def name(a, b):
        edge = tuple(sorted((a, b)))
        return component.get(edge, edge)
    signatures = set()
    labels = sorted(labels, key=lambda v: (ranks[v], v), reverse=True)
    for a, b, c, d in combinations(labels, 4):
        if len({ranks[a], ranks[b], ranks[c], ranks[d]}) < 4:
            continue
        diagonal = [name(a, c), name(b, d)]
        for pairs in (((a, b), (c, d)), ((a, d), (b, c))):
            positive = list(diagonal)
            negative = [name(*edge) for edge in pairs]
            for edge in list(positive):
                if edge in negative:
                    positive.remove(edge)
                    negative.remove(edge)
            if not positive and not negative:
                return "zero"
            positive, negative = tuple(sorted(positive)), tuple(sorted(negative))
            if (negative, positive) in signatures:
                return "inverse"
            signatures.add((positive, negative))
    return None


def exact_search(graph, support, ranks, mandatory=frozenset([42, 43])):
    domains = {
        i: tuple(
            support[i] | frozenset(9 + j for j in chosen)
            for chosen in combinations(sorted(targets), 4 - len(support[i]))
        )
        for i, targets in graph.items()
    }
    calls = 0
    metric_counts = {"zero": 0, "inverse": 0}

    @lru_cache(maxsize=None)
    def compatible(i, row, j, other):
        common = row & other
        if len(common) < 2:
            return True
        if len(common) > 2:
            return False
        a, b = sorted(common)
        return interlace_possible(ranks, i + 9, j + 9, a, b)

    def solve(fixed, needed, available):
        nonlocal calls
        calls += 1
        remaining = needed - fixed.keys()
        if not remaining:
            physical = {i + 9: sorted(row) for i, row in fixed.items()}
            kind = metric_cancelled(physical, ranks)
            if kind is not None:
                metric_counts[kind] += 1
                return None
            return {i: sorted(row) for i, row in fixed.items()}
        if any(not available[i] for i in remaining):
            return None
        # Reverse tie-breaking and reverse candidate order versus the primary.
        i = min(remaining, key=lambda i: (len(available[i]), -i))
        for row in reversed(available[i]):
            if any(not compatible(i, row, j, other) for j, other in fixed.items()):
                continue
            new_fixed = {**fixed, i: row}
            new_needed = needed | {j - 9 for j in row if j >= 9}
            new_available = {
                j: tuple(candidate for candidate in options if compatible(i, row, j, candidate))
                for j, options in available.items() if j not in new_fixed
            }
            while True:
                impossible = {j for j, options in new_available.items() if not options}
                if impossible & new_needed:
                    break
                changed = False
                for j, options in list(new_available.items()):
                    filtered = tuple(option for option in options
                                     if all(k - 9 not in impossible for k in option if k >= 9))
                    if filtered != options:
                        changed = True
                        new_available[j] = filtered
                if not changed:
                    result = solve(new_fixed, new_needed, new_available)
                    if result is not None:
                        return result
                    break
        return None

    answer = solve({}, set(mandatory), domains)
    return answer, calls, metric_counts


def audit(certificate, selected_indices=None, progress=False):
    if set(certificate) != {"schema", "base_sha", "input_sha256", "not_an_unrestricted_solution", "cases"}:
        raise ValueError("Unexpected certificate fields")
    if selected_indices is not None:
        if (len(set(selected_indices)) != len(selected_indices)
                or any(type(i) is not int or not 0 <= i < 4500 for i in selected_indices)):
            raise ValueError("Invalid selected case indices")
    for case in certificate["cases"]:
        if len(case["cells"]) != 2 or any(type(c) is not int or not 0 <= c < 9 for c in case["cells"]):
            raise ValueError("Invalid cell labels")
        if len(case["old_witnesses"]) != 2 or any(x is not None and (type(x) is not int or not 0 <= x < 9) for x in case["old_witnesses"]):
            raise ValueError("Invalid old witness labels")
    expected = [(a, b, u, v) for a, b in combinations_with_replacement(range(9), 2)
                for u, v in product([None] + list(range(9)), repeat=2)]
    if certificate.get("schema") != "erdos97.two_free_partition.v1":
        raise ValueError("Unknown certificate schema")
    if certificate.get("base_sha") != BASE_SHA or certificate.get("input_sha256") != archive_hash():
        raise ValueError("Bad provenance")
    if certificate.get("not_an_unrestricted_solution") is not True:
        raise ValueError("Claim boundary missing")
    if [tuple(c["cells"] + c["old_witnesses"]) for c in certificate["cases"]] != expected:
        raise ValueError("Incomplete or reordered case coverage")
    R, _, _, _, triangles, _ = context()
    totals = dict(cases=0, partition_nodes=0, leaves=0, maximum_depth=0,
                  row_models=0, row_search_nodes=0, metric_zero_rejections=0, metric_inverse_rejections=0)
    indices = range(4500) if selected_indices is None else selected_indices
    for index in indices:
        case = certificate["cases"][index]
        if set(case) != {"cells", "old_witnesses", "tree"}:
            raise ValueError("Malformed case")
        cells, old = case["cells"], case["old_witnesses"]
        def visit(tree, first, second, depth):
            totals["partition_nodes"] += 1
            totals["maximum_depth"] = max(totals["maximum_depth"], depth)
            if tree is None:
                totals["leaves"] += 1
                batches = model_list(first, second, cells, old)
                for graph, support, ranks in batches:
                    assignment, nodes, metric_counts = exact_search(graph, support, ranks)
                    totals["row_models"] += 1
                    totals["row_search_nodes"] += nodes
                    for kind in ("zero", "inverse"):
                        totals[f"metric_{kind}_rejections"] += metric_counts[kind]
                    if assignment is not None:
                        raise ValueError(f"Unresolved oracle leaf in case {index}: {assignment}")
                return
            if not isinstance(tree, dict) or set(tree) != {"coordinate", "edge", "children"}:
                raise ValueError("Malformed partition node")
            which, edge = tree["coordinate"], tree["edge"]
            if type(which) is not int or which not in (0, 1) or type(edge) is not int or not 0 <= edge < 3:
                raise ValueError("Invalid product subdivision")
            if not isinstance(tree["children"], list) or len(tree["children"]) != 2:
                raise ValueError("Missing child domain")
            triangle = (first, second)[which]
            a, b, c = (triangle[(edge + j) % 3] for j in range(3))
            midpoint = A.times(A.plus(a, b), R(1) / 2)
            pieces = ((a, midpoint, c), (midpoint, b, c))
            for subtree, piece in zip(tree["children"], pieces):
                if A.orientation(*piece) <= 0:
                    raise ValueError("Nonpositive subdivision orientation")
                visit(subtree, piece if which == 0 else first,
                      second if which == 0 else piece, depth + 1)
        visit(case["tree"], triangles[cells[0]], triangles[cells[1]], 0)
        totals["cases"] += 1
        if progress and totals["cases"] % 100 == 0:
            print(json.dumps(totals), file=sys.stderr, flush=True)
    return {"status": "passed", **totals, "input_sha256": archive_hash(),
            "largest_sign_enclosure_bits": A.O.MAX_BITS,
            "arithmetic": "independent polynomial radical ring with rational square-root enclosures",
            "geometry": "Minkowski difference hulls and interpolated quadratics",
            "search": "sets, reverse variable ties and candidate orders, cyclic descents",
            "primary_mathematical_code_imported": False,
            "external_mathematical_review": False, "formalization": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--progress", action="store_true")
    parser.add_argument("--cases", type=int, nargs="*")
    args = parser.parse_args()
    certificate = json.loads((ROOT / "data/certificate.json").read_text())
    result = audit(certificate, args.cases, args.progress)
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    path = ROOT / "data/oracle_report.json"
    if args.write:
        if args.cases is not None:
            raise ValueError("Partial oracle replay cannot replace full report")
        path.write_text(output)
    if args.check and path.read_text() != output:
        raise ValueError("Oracle report differs")
    print(output)


if __name__ == "__main__":
    main()
