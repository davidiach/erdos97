"""Minimal vertex-circle obstruction cores for the n=9 selected-witness frontier.

This is an independent diagnostic written from scratch. It consumes the 184
incidence-surviving n=9 selected-witness systems (regenerated here, not read
from a stored artifact) and, for each, finds every *minimal* sub-configuration
of selected rows whose vertex-circle quotient already forces a contradiction
(a self-edge or a strict directed cycle). Minimality is by row-set inclusion:
no proper subset of the rows is already obstructing.

It then canonicalizes those minimal cores under the dihedral symmetry D_9 of
the cyclic order (9 rotations x -> x+k, 9 reflections x -> c-x, all mod 9) and
reports the distinct catalogue, together with two properties:

* coverage: every one of the 184 frontier systems contains at least one
  catalogued minimal core (so the catalogue is a complete obstruction cover of
  the frontier); and
* soundness of each core: each catalogued core is re-checked in isolation and
  confirmed to be an exact vertex-circle obstruction.

This sharpens the existing "16 motif families / compact local cores" view by
exhibiting the full set of *minimal* obstructions and their sizes. It shows
every incidence-surviving nonagon system dies from a local core of at most six
rows, and usually from just three.

No general proof of Erdos Problem #97 is claimed, and no counterexample is
claimed. This is a finite-case structural diagnostic only. It reuses the
independent primitives in ``independent_n9_vertex_circle_recheck.py`` and
shares no code with ``src/erdos97/n9_vertex_circle_exhaustive.py``.
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "rec", os.path.join(HERE, "independent_n9_vertex_circle_recheck.py")
)
rec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rec)

N = rec.N
ROW_SIZE = rec.ROW_SIZE
EXPECTED_SUMMARY = {
    "frontier_systems": 184,
    "frontier_systems_covered_by_a_minimal_core": 184,
    "coverage_complete": True,
    "distinct_minimal_cores": 219,
    "minimal_core_size_counts": {"3": 105, "4": 106, "5": 7, "6": 1},
    "minimal_core_status_counts": {"self_edge": 36, "strict_cycle": 183},
    "minimal_core_size_occurrences": {"3": 2058, "4": 2016, "5": 126, "6": 12},
    "smallest_core_size": 3,
    "largest_core_size": 6,
    "isolated_recheck_mismatches": 0,
}


def status_of_subset(assign, centers):
    sub = {c: assign[c] for c in centers}
    return rec.vertex_circle_status(sub)


def minimal_cores(assign):
    """Return the list of minimal obstructing center-subsets for one system."""
    centers = sorted(assign)
    minimal: list[frozenset[int]] = []
    for k in range(2, len(centers) + 1):
        for combo in itertools.combinations(centers, k):
            cs = frozenset(combo)
            if any(m <= cs for m in minimal):
                continue  # a smaller core already sits inside this subset
            if status_of_subset(assign, combo) in ("self_edge", "strict_cycle"):
                minimal.append(cs)
    return minimal


# Dihedral group D_9 acting on labels, preserving the cyclic order up to
# reversal (and hence preserving the vertex-circle obstruction structure).
def _syms():
    rots = [(lambda x, k=k: (x + k) % N) for k in range(N)]
    refls = [(lambda x, c=c: (c - x) % N) for c in range(N)]
    return rots + refls


SYMS = _syms()


def canon_core(assign, centers):
    best = None
    for g in SYMS:
        rows = []
        for c in centers:
            wit = tuple(sorted(g(w) for w in assign[c]))
            rows.append((g(c),) + wit)
        key = tuple(sorted(rows))
        if best is None or key < best:
            best = key
    return best


def core_status_isolated(core_rows):
    """Recompute obstruction status of a catalogued core from its rows alone."""
    assign = {r[0]: frozenset(r[1:]) for r in core_rows}
    return rec.vertex_circle_status(assign)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="data/certificates/n9_vertex_circle_minimal_cores.json")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--assert-expected", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true", help="write generated artifact")
    ap.add_argument("--no-write", action="store_true", help="deprecated no-op; output is not written unless --write is set")
    args = ap.parse_args()
    if args.write and args.no_write:
        ap.error("--write cannot be combined with --no-write")
    if args.write and args.check:
        ap.error("--write cannot be combined with --check")

    frontier = rec.enumerate_frontier()
    assert len(frontier) == 184, f"expected 184 frontier systems, got {len(frontier)}"

    catalogue: dict[tuple, dict] = {}
    size_occurrences: dict[int, int] = defaultdict(int)
    covered = 0

    for assign in frontier:
        mins = minimal_cores(assign)
        if mins:
            covered += 1
        for cs in mins:
            ck = canon_core(assign, sorted(cs))
            size_occurrences[len(cs)] += 1
            entry = catalogue.setdefault(
                ck,
                {
                    "rows": [list(r) for r in ck],
                    "size": len(ck),
                    "status": status_of_subset(assign, sorted(cs)),
                    "frontier_occurrences": 0,
                },
            )
            entry["frontier_occurrences"] += 1

    # Re-verify every catalogued core in isolation.
    isolated_mismatch = 0
    for ck, entry in catalogue.items():
        st = core_status_isolated(entry["rows"])
        if st != entry["status"] or st == "ok":
            isolated_mismatch += 1

    status_counts: dict[str, int] = defaultdict(int)
    size_counts: dict[int, int] = defaultdict(int)
    for entry in catalogue.values():
        status_counts[entry["status"]] += 1
        size_counts[entry["size"]] += 1

    ordered = sorted(catalogue.values(), key=lambda e: (e["size"], e["rows"]))

    report = {
        "schema": "erdos97.n9_vertex_circle_minimal_cores.v1",
        "trust": "INDEPENDENT_FINITE_CASE_DIAGNOSTIC_NO_GLOBAL_CLAIM",
        "n": N,
        "row_size": ROW_SIZE,
        "cyclic_order": list(range(N)),
        "symmetry_group": "dihedral D_9 (9 rotations + 9 reflections on labels)",
        "frontier_systems": len(frontier),
        "frontier_systems_covered_by_a_minimal_core": covered,
        "coverage_complete": covered == len(frontier),
        "distinct_minimal_cores": len(catalogue),
        "minimal_core_size_counts": dict(sorted(size_counts.items())),
        "minimal_core_status_counts": dict(status_counts),
        "minimal_core_size_occurrences": dict(sorted(size_occurrences.items())),
        "smallest_core_size": min(size_counts),
        "largest_core_size": max(size_counts),
        "isolated_recheck_mismatches": isolated_mismatch,
        "interpretation": [
            "Every one of the 184 incidence-surviving n=9 selected-witness systems "
            "contains at least one catalogued minimal vertex-circle obstruction core.",
            "Each catalogued core is an exact obstruction for any strictly convex "
            "realization with this cyclic order, using only the rows it names.",
            "The smallest obstruction uses three selected rows; the largest uses six.",
            "This is a structural refinement of the motif-family view, not a new "
            "claim about the official/global status, and not a counterexample.",
        ],
        "minimal_cores": ordered,
    }
    json_report = json.loads(json.dumps(report))

    expected_ok = all(
        json_report.get(key) == value for key, value in EXPECTED_SUMMARY.items()
    )
    ok = (
        json_report["coverage_complete"]
        and json_report["isolated_recheck_mismatches"] == 0
        and json_report["distinct_minimal_cores"] == len(catalogue)
        and (expected_ok or not args.assert_expected)
    )

    out_path = (
        os.path.join(os.path.dirname(HERE), args.out)
        if not os.path.isabs(args.out)
        else args.out
    )

    if args.check:
        try:
            with open(out_path, encoding="utf-8") as fh:
                stored = json.load(fh)
        except OSError:
            ok = False
        else:
            ok = ok and stored == json_report

    if args.write:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(json_report, fh, indent=2)

    if args.json:
        summary = {k: v for k, v in json_report.items() if k != "minimal_cores"}
        print(json.dumps(summary, indent=2))
    else:
        print("=== n=9 minimal vertex-circle obstruction cores ===")
        print(f"frontier systems: {json_report['frontier_systems']}")
        print(
            "covered by a minimal core: "
            f"{json_report['frontier_systems_covered_by_a_minimal_core']} "
            f"(complete cover: {json_report['coverage_complete']})"
        )
        print(
            "distinct minimal cores (up to D_9): "
            f"{json_report['distinct_minimal_cores']}"
        )
        print(f"  by size:   {json_report['minimal_core_size_counts']}")
        print(f"  by status: {json_report['minimal_core_status_counts']}")
        print(
            f"smallest core size: {json_report['smallest_core_size']}, "
            f"largest: {json_report['largest_core_size']}"
        )
        print(
            "isolated recheck mismatches: "
            f"{json_report['isolated_recheck_mismatches']}"
        )

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
