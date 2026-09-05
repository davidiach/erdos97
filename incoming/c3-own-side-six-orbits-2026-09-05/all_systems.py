#!/usr/bin/env python3
"""All own-side C3 systems through six orbits: exact finite replay.

Only the own-triangle-side four-witness hypothesis is covered. The general
Erdos problem and other-radius ties are NOT covered. See README.md for the
geometric reduction, including radius ties and the no-shortcut lemma.
"""
from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
from itertools import combinations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("six_orbit_certificate_core", ROOT / "certificate.py")
assert SPEC is not None and SPEC.loader is not None
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)
EXPECTED_GRAPHS = (
    ((3, 4), (0, 5), (0, 5), (1, 2), (1, 2), (3, 4)),
    ((3, 5), (0, 5), (0, 5), (1, 2), (1, 2), (3, 4)),
    ((4, 5), (0, 5), (0, 5), (1, 2), (1, 2), (3, 4)),
    ((4, 5), (4, 5), (0, 1), (0, 1), (2, 3), (2, 3)),
)
EXPECTED_PHASE_COUNTS = ((1600, 320), (1888, 32), (1888, 32), (1712, 208))


def oriented_graphs(n: int):
    if n not in (5, 6):
        raise ValueError("this bounded replay supports n=5 or n=6 orbits only")
    choices = [tuple(combinations([j for j in range(n) if j != i], 2)) for i in range(n)]
    selected = []

    def visit(i):
        if i == n:
            yield tuple(selected)
            return
        for row in choices[i]:
            if any(j < i and i in selected[j] for j in row):
                continue
            selected.append(row)
            yield from visit(i + 1)
            selected.pop()

    yield from visit(0)


def shortcut_certificate(graph: tuple) -> dict | None:
    n = len(graph)
    neighbors = [set() for _ in range(n)]
    for i, row in enumerate(graph):
        for j in row:
            neighbors[i].add(j)
            neighbors[j].add(i)
    for hi, row in enumerate(graph):
        for lo in row:
            if lo >= hi:
                continue
            parents = {lo: None}
            for mid in range(lo + 1, hi):
                previous = sorted(neighbors[mid] & parents.keys())
                if previous:
                    parents[mid] = previous[0]
            previous = sorted((neighbors[hi] & parents.keys()) - {lo})
            if previous:
                path = [hi, previous[0]]
                while parents[path[-1]] is not None:
                    path.append(parents[path[-1]])
                return {"edge": [hi, lo], "path": path[::-1]}
    return None


def verify_shortcut(graph: tuple, certificate: dict) -> None:
    hi, lo = certificate["edge"]
    path = certificate["path"]
    if (not 0 <= lo < hi < len(graph) or lo not in graph[hi]
            or len(path) < 3 or path[0] != lo or path[-1] != hi
            or any(type(v) is not int or not 0 <= v < len(graph) for v in path)
            or any(a >= b or (b not in graph[a] and a not in graph[b])
                   for a, b in zip(path, path[1:]))):
        raise ValueError("invalid monotone-path/downward-edge certificate")


def graph_audit() -> tuple[list[dict], list[tuple]]:
    records, survivors = [], []
    for n in (5, 6):
        count = 0
        for graph in oriented_graphs(n):
            count += 1
            certificate = shortcut_certificate(graph)
            if certificate is not None:
                verify_shortcut(graph, certificate)
            else:
                survivors.append(graph)
            records.append({"n": n, "graph": graph, "shortcut": certificate})
        if count != {5: 24, 6: 14490}[n]:
            raise ValueError("oriented graph coverage mismatch")
    if tuple(survivors) != EXPECTED_GRAPHS:
        raise ValueError("unexpected radius-path survivor")
    return records, survivors


def generate() -> tuple[dict, list[dict], list[dict]]:
    graph_records, graphs = graph_audit()
    phase_records, summary = [], []
    for graph_index, graph in enumerate(graphs):
        census = Counter()
        for case_index, (order, gains) in enumerate(core.cases(tuple(range(6)), graph)):
            rows = core.expand(order, gains, graph)
            certificate = core.find_certificate(rows)
            if certificate is None:
                raise ValueError(f"unobstructed graph/phase case: {graph_index}, {case_index}")
            core.verify_certificate(rows, certificate)
            census[certificate["kind"]] += 1
            phase_records.append({"graph_index": graph_index, "case": case_index,
                                  "angle_order": order, "gains": gains,
                                  "certificate": certificate})
        crossing, inverse = EXPECTED_PHASE_COUNTS[graph_index]
        if dict(census) != {"crossing": crossing, "kalmanson_inverse": inverse}:
            raise ValueError("phase census mismatch")
        summary.append({"graph": [list(row) for row in graph], "cases": sum(census.values()),
                        "obstructions": dict(census)})
    report = {
        "schema": "erdos97.own_side_at_most_six_orbits.v1",
        "status": "EXACT_FINITE_CERTIFICATE_REVIEW_PENDING",
        "scope": "All strictly convex C3 own-side four-witness systems with at most six orbits; NOT arbitrary radii of rich classes.",
        "n5": {"oriented_graphs": 24, "shortcut_obstructions": 24, "survivors": 0},
        "n6": {"oriented_graphs": 14490, "shortcut_obstructions": 14486,
               "shortcut_survivors": 4, "phase_cases": 7680, "final_survivors": 0},
        "phase_summary": summary,
        "graph_certificates_sha256": core.digest(graph_records),
        "phase_certificates_sha256": core.digest(phase_records),
        "positive_control": core.positive_control(),
    }
    return report, graph_records, phase_records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--write", action="store_true")
    actions.add_argument("--check", action="store_true")
    parser.add_argument("--certificates", type=Path, help="export all graph and phase certificates")
    args = parser.parse_args()
    report, graphs, phases = generate()
    encoded = json.dumps(report, sort_keys=True, indent=2) + "\n"
    stored = ROOT / "all_systems_report.json"
    if args.write:
        stored.write_text(encoded, encoding="utf-8")
    if args.check and stored.read_text(encoding="utf-8") != encoded:
        raise ValueError("stored all-systems report mismatch")
    if args.certificates:
        args.certificates.write_text(json.dumps({"graphs": graphs, "phases": phases},
                                              sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
