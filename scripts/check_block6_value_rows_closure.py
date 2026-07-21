#!/usr/bin/env python3
"""Check the squared-distance value-row closure of the block-6 escapes.

The 16 vertex-circle-clean fixed-order selected-row systems recorded by
``check_block6_reversed_block_shuffle_vertex_circle_escape.py`` were
previously closed only by exact Kalmanson quotient-cone certificates.  This
checker replays a second, Kalmanson-free exact closure using per-center
squared-distance value rows proved in
``docs/squared-distance-value-rows-2026-07-10.md``:

- Row O (obtuse): for witnesses ``a<b<c<d`` in angular order at center
  ``i``, ``D_ac > D_ab + D_bc``, ``D_bd > D_bc + D_cd``,
  ``D_ad > D_ab + D_bd``, ``D_ad > D_ac + D_cd``.
- Row D (diameter): ``D_xy < 4 R_i`` for every witness pair.
- Row S (short-chord pigeonhole, the k=4-essential row): the three
  consecutive angular gaps at ``i`` sum to less than pi, so one gap is
  below pi/3 and ``min(D_ab, D_bc, D_cd) < R_i``.

Layered exact decisions (z3 over the reals) on squared-distance variables
with per-row radius equalities and the repo's strict nested-interval rows
as baseline ``N``:

- ``N`` alone must be satisfiable for every escape record (they are
  vertex-circle clean by construction; control).
- ``N + S`` must be unsatisfiable for all 16 records (headline closure).
- ``N + O + D`` must be unsatisfiable for exactly 15 of 16 records, with
  the record of escape index 13 the unique survivor (ablation).
- The C29 Sidon fixed orders (natural and the recorded Kalmanson-escape
  order) must stay satisfiable under all value-row layers (negative
  control: the value rows complement, and do not dominate,
  Kalmanson/Altman certificates).

Unsatisfiability verdicts are sound kills regardless of baseline
completeness because every added row is a proved necessary condition for a
realizable strictly convex selected-witness configuration.  Satisfiability
verdicts are solver outcomes recorded as controls only.

Claim scope: exact fixed-order diagnostics for the encoded selected-row
assignments and cyclic orders only.  This does not prove all-order closure,
the fragile bridge, or Erdos Problem #97, does not provide a counterexample,
and does not change the official/global falsifiable/open status.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any

from erdos97.vertex_circle_order_filter import (
    angular_witness_order,
    vertex_circle_order_obstruction,
)

ROOT = Path(__file__).resolve().parents[1]

SOURCE = (
    ROOT / "data" / "certificates"
    / "block6_reversed_block_shuffle_vertex_circle_escape.json"
)
OUT = ROOT / "data" / "certificates" / "block6_value_rows_closure.json"
SCHEMA = "erdos97.block6_value_rows_closure.v1"
STATUS = "EXACT_FIXED_ORDER_VALUE_ROW_CLOSURE_FOR_REVERSED_BLOCK_VC_CLEAN_ROWS"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact z3 real-arithmetic value-row diagnostics for the 16 "
    "vertex-circle-clean fixed-order selected-row assignments of the "
    "reversed-second-block shuffle packet, plus C29 fixed-order negative "
    "controls. Each unsat verdict applies only to its encoded selected-row "
    "assignment and encoded cyclic order. This is not all-order closure, "
    "not a fragile-bridge proof, not a proof of Erdos Problem #97, and not "
    "a counterexample."
)
PROVENANCE = {
    "generator": "scripts/check_block6_value_rows_closure.py",
    "command": (
        "python scripts/check_block6_value_rows_closure.py --write "
        "--assert-expected"
    ),
}

EXPECTED_RECORDS = 16
EXPECTED_BASELINE_SAT = 16
EXPECTED_SHORT_CHORD_UNSAT = 16
EXPECTED_OBTUSE_DIAMETER_UNSAT = 15
EXPECTED_OBTUSE_DIAMETER_SURVIVORS = (13,)

C29_OFFSETS = (1, 3, 7, 15)
C29_N = 29
# Recorded fixed escape order for C29_sidon_1_3_7_15 (metadata/erdos97.yaml);
# it escaped the two-inequality Kalmanson search and needed a 165-row
# Kalmanson/Farkas certificate.
C29_ESCAPE_ORDER = (
    0, 27, 11, 4, 19, 5, 26, 12, 6, 21, 13, 28, 14, 2, 20, 18, 7, 24,
    10, 25, 17, 3, 9, 15, 1, 22, 8, 23, 16,
)


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pairkey(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def solve_layers(order: list[int], rows: list[tuple[int, ...]],
                 layers: str) -> str:
    """Decide the value-row system exactly; layers is a subset of 'ODS'."""
    import z3

    n = len(order)
    solver = z3.Solver()
    dist: dict[tuple[int, int], Any] = {}
    for a, b in combinations(range(n), 2):
        dist[(a, b)] = z3.Real(f"D_{a}_{b}")
        solver.add(dist[(a, b)] > 0)

    def d(a: int, b: int) -> Any:
        return dist[pairkey(a, b)]

    radius = {}
    for center, row in enumerate(rows):
        radius[center] = d(center, row[0])
        for witness in row[1:]:
            solver.add(d(center, witness) == radius[center])

    for center, row in enumerate(rows):
        wit = angular_witness_order(order, center, row)
        a, b, c, e = wit
        index = {a: 0, b: 1, c: 2, e: 3}
        for p1, q1 in combinations(wit, 2):
            for p2, q2 in combinations(wit, 2):
                if (p1, q1) == (p2, q2):
                    continue
                o1, e1 = index[p1], index[q1]
                o2, e2 = index[p2], index[q2]
                if o1 <= o2 and e2 <= e1 and (o1 < o2 or e2 < e1):
                    solver.add(d(p1, q1) > d(p2, q2))
        if "O" in layers:
            solver.add(d(a, c) > d(a, b) + d(b, c))
            solver.add(d(b, e) > d(b, c) + d(c, e))
            solver.add(d(a, e) > d(a, b) + d(b, e))
            solver.add(d(a, e) > d(a, c) + d(c, e))
        if "D" in layers:
            for x, y in combinations(row, 2):
                solver.add(d(x, y) < 4 * radius[center])
        if "S" in layers:
            solver.add(
                z3.Or(
                    d(a, b) < radius[center],
                    d(b, c) < radius[center],
                    d(c, e) < radius[center],
                )
            )
    solver.set("timeout", 300000)
    return str(solver.check())


def block6_records() -> list[dict[str, Any]]:
    payload = json.loads(SOURCE.read_text())
    return payload["clean_order_records"]


def run_block6() -> list[dict[str, Any]]:
    results = []
    for record in block6_records():
        order = list(record["order"])
        rows = [tuple(r) for r in record["pruned_search"]["first_clean_rows"]]
        clean = not vertex_circle_order_obstruction(rows, order).obstructed
        entry = {
            "index": record["index"],
            "order": order,
            "rows": [list(r) for r in rows],
            "vertex_circle_clean": clean,
            "baseline": solve_layers(order, rows, ""),
            "short_chord": solve_layers(order, rows, "S"),
            "obtuse_diameter": solve_layers(order, rows, "OD"),
        }
        results.append(entry)
    return results


def c29_rows() -> list[tuple[int, ...]]:
    return [
        tuple(sorted((i + o) % C29_N for o in C29_OFFSETS))
        for i in range(C29_N)
    ]


def run_c29() -> list[dict[str, Any]]:
    rows = c29_rows()
    out = []
    for name, order in (
        ("natural", list(range(C29_N))),
        ("kalmanson_escape", list(C29_ESCAPE_ORDER)),
    ):
        out.append(
            {
                "order_name": name,
                "all_value_rows": solve_layers(order, rows, "ODS"),
            }
        )
    return out


def build_payload() -> dict[str, Any]:
    block6 = run_block6()
    c29 = run_c29()
    summary = {
        "records": len(block6),
        "vertex_circle_clean": sum(
            1 for r in block6 if r["vertex_circle_clean"]
        ),
        "baseline_sat": sum(1 for r in block6 if r["baseline"] == "sat"),
        "short_chord_unsat": sum(
            1 for r in block6 if r["short_chord"] == "unsat"
        ),
        "obtuse_diameter_unsat": sum(
            1 for r in block6 if r["obtuse_diameter"] == "unsat"
        ),
        "obtuse_diameter_survivors": sorted(
            r["index"] for r in block6 if r["obtuse_diameter"] == "sat"
        ),
        "c29_all_sat": all(r["all_value_rows"] == "sat" for r in c29),
    }
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "provenance": PROVENANCE,
        "source_artifact": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha256_of(SOURCE),
        "summary": summary,
        "block6_records": block6,
        "c29_controls": c29,
    }


def assert_expected(payload: dict[str, Any]) -> list[str]:
    errors = []
    summary = payload["summary"]
    checks = (
        ("records", EXPECTED_RECORDS),
        ("vertex_circle_clean", EXPECTED_RECORDS),
        ("baseline_sat", EXPECTED_BASELINE_SAT),
        ("short_chord_unsat", EXPECTED_SHORT_CHORD_UNSAT),
        ("obtuse_diameter_unsat", EXPECTED_OBTUSE_DIAMETER_UNSAT),
        (
            "obtuse_diameter_survivors",
            list(EXPECTED_OBTUSE_DIAMETER_SURVIVORS),
        ),
        ("c29_all_sat", True),
    )
    for key, want in checks:
        got = summary.get(key)
        if got != want:
            errors.append(f"summary[{key!r}] = {got!r}, expected {want!r}")
    if payload.get("source_sha256") != sha256_of(SOURCE):
        errors.append("source artifact digest changed; regenerate")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true",
        help="recompute and write the artifact JSON",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="recompute and compare against the stored artifact",
    )
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    payload = build_payload()

    if args.write:
        OUT.write_text(json.dumps(payload, indent=1) + "\n")
        print(f"wrote {OUT.relative_to(ROOT)}")
    if args.check:
        stored = json.loads(OUT.read_text())
        mismatch = []
        for key in ("summary", "block6_records", "c29_controls",
                    "source_sha256"):
            if stored.get(key) != payload.get(key):
                mismatch.append(key)
        if mismatch:
            print(f"stored artifact mismatch in: {', '.join(mismatch)}")
            return 1
        print("stored artifact matches recomputation")
    if args.assert_expected:
        errors = assert_expected(payload)
        if errors:
            for line in errors:
                print(f"UNEXPECTED: {line}")
            return 1
        print("expected value-row closure summary confirmed")
    if args.json:
        print(json.dumps(payload["summary"], indent=1))
    if not (args.write or args.check or args.assert_expected or args.json):
        print(json.dumps(payload["summary"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
