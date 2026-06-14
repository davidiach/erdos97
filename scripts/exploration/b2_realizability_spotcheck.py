#!/usr/bin/env python3
"""B2 add-on: z3 strict-convex realizability spot-check for incidence survivors.

Lane B2 (Erdos Problem #97). If the scalable abstract-incidence search
(``b2_scalable_incidence_search.py``) ever leaves a SURVIVING necessary-incidence
system at n>=10, this helper hands that system to z3 as a coordinate-geometry
realizability question: does the selected-witness incidence pattern embed as a
strictly convex n-gon with equal selected squared distances per center?

This is the SAME geometric encoding lane B1 uses at n=9 (strict turns + equal
squared distances). It is included here ONLY as an optional spot-check on n>=10
survivors so a small surviving system can be triaged immediately. It does not
duplicate B1's n=9 study.

A z3 cyclic order is REQUIRED (the natural order 0..n-1 is used by default, which
matches the abstract search convention). For a genuine triage you must try the
relevant crossing-compatible orders, since the abstract filters only pin chord
crossings, not a unique order.

TRUST: UNSAT for a given order => that incidence system has no strictly convex
realization in that order (subject to z3 nonlinear-real solver trust; re-check
exactly before relying on it). SAT => a candidate realization exists for that
order and MUST be exactly re-certified; it is NOT a counterexample claim. This
script never promotes any n and never claims a counterexample.

Usage:
  # rows = list of n rows, each [center, w1, w2, w3, w4]; or a JSON file with
  # {"n":..,"survivors":[[[w,w,w,w] per center], ...]} from the search.
  python scripts/exploration/b2_realizability_spotcheck.py --rows-json survivors.json \
      --timeout-ms 10000
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import z3


def sq(px, py, qx, qy):
    dx, dy = px - qx, py - qy
    return dx * dx + dy * dy


def cross(ax, ay, bx, by, cx, cy):
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


def realizable_status(
    n: int,
    rows: list[list[int]],
    cyclic_order: list[int],
    timeout_ms: int,
) -> dict:
    """Return {'status': 'sat'|'unsat'|'unknown', ...} for one incidence system.

    rows[i] is the witness list (length 4) for center i. Strict convexity is
    encoded as all n consecutive signed turns strictly positive in cyclic_order.
    """
    s = z3.Solver()
    s.set("timeout", int(timeout_ms))
    try:
        s.set("logic", "QF_NRA")
    except z3.Z3Exception:
        pass
    x = [z3.Real(f"x{i}") for i in range(n)]
    y = [z3.Real(f"y{i}") for i in range(n)]
    s.add(x[0] == 0, y[0] == 0, x[1] == 1, y[1] == 0)  # gauge
    for k in range(n):
        a, b, c = cyclic_order[k], cyclic_order[(k + 1) % n], cyclic_order[(k + 2) % n]
        s.add(cross(x[a], y[a], x[b], y[b], x[c], y[c]) > 0)  # strict convexity
    for i in range(n):
        for j in range(i + 1, n):
            s.add(z3.Or(x[i] != x[j], y[i] != y[j]))
    for center in range(n):
        wit = rows[center]
        ref = sq(x[center], y[center], x[wit[0]], y[wit[0]])
        for w in wit[1:]:
            s.add(sq(x[center], y[center], x[w], y[w]) == ref)
    t0 = time.perf_counter()
    res = s.check()
    dt = time.perf_counter() - t0
    label = "sat" if res == z3.sat else "unsat" if res == z3.unsat else "unknown"
    out = {"status": label, "elapsed_seconds": round(dt, 3)}
    if res == z3.unknown:
        out["reason"] = s.reason_unknown()
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rows-json", type=Path, required=True)
    ap.add_argument("--timeout-ms", type=int, default=10000)
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args(argv)

    data = json.loads(args.rows_json.read_text())
    n = int(data["n"])
    survivors = data.get("survivors") or data.get("_survivor_rows") or []
    order = list(data.get("cyclic_order", list(range(n))))
    if not survivors:
        print("no survivors in file; nothing to spot-check.")
        return 0
    print(f"n={n} survivors={len(survivors)} order={order}")
    for idx, rows in enumerate(survivors[: args.limit]):
        rec = realizable_status(n, rows, order, args.timeout_ms)
        print(f"  survivor[{idx}] -> {rec['status']} ({rec['elapsed_seconds']}s)")
        if rec["status"] == "sat":
            print("  *** SAT: candidate realization; requires EXACT re-certification; NOT a counterexample claim ***")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
