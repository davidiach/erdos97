#!/usr/bin/env python3
"""SMT realizability test for a fixed selected-witness incidence pattern.

Given a pattern (n rows of 4 witnesses) we ask z3 over the reals whether there
exist 2-D coordinates (x_i, y_i) for i = 0..n-1 such that:

  - The points are in convex position with strictly cyclic orientation
    (consecutive triples have positive cross product) when ordered by their
    cyclic label 0, 1, ..., n-1.
  - For each row i with witnesses {a, b, c, d}, the four squared distances
    |p_i - p_w|^2 are equal for w in {a, b, c, d}, i.e. they all lie on a
    circle centered at p_i.
  - Strict convexity gap epsilon > 0 (passed as a parameter; default 1e-9
    expressed as a rational).

This script is meant to be run on patterns that the SAT/SMT vertex-witness
encoding has *not* refuted.  A SAT result here is **not** a proof of
counterexample to Erdos #97 — geometric realization plus strict convexity is a
necessary condition but the result needs independent verification.  An UNSAT
result for a specific pattern proves only that this particular incidence
pattern has no realization in the reals (with the supplied epsilon).

Usage:
  python3 scripts/smt_realize_witness.py --pattern-file path/to/pattern.json \
      --timeout-ms 600000

The pattern file can be either:
  - {"pattern": [[...], [...], ...]}
  - {"sample_pattern": [[...], [...], ...]}
  - a bare list-of-lists JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_pattern(path: Path) -> list[list[int]]:
    data = json.loads(path.read_text())
    if isinstance(data, list):
        return [list(row) for row in data]
    for key in ("pattern", "sample_pattern", "rows"):
        if key in data:
            return [list(row) for row in data[key]]
    raise ValueError(f"could not find pattern in {path}")


def encode_realizability(pattern: list[list[int]], epsilon_str: str = "1/1000000"):
    import z3

    n = len(pattern)

    s = z3.Solver()
    xs = [z3.Real(f"x_{i}") for i in range(n)]
    ys = [z3.Real(f"y_{i}") for i in range(n)]

    # Fix gauge: p_0 = (0, 0), p_1 = (1, 0).  Removes translation/rotation/scale
    # ambiguity for any non-degenerate witness.  (We assume p_0 != p_1.)
    s.add(xs[0] == 0)
    s.add(ys[0] == 0)
    s.add(xs[1] == 1)
    s.add(ys[1] == 0)

    eps = z3.Q(*[int(p) for p in epsilon_str.split("/")])

    # Strict convexity: for each consecutive triple (i, i+1, i+2) mod n,
    # the cross product (p_{i+1} - p_i) x (p_{i+2} - p_{i+1}) >= eps.
    for i in range(n):
        a = i
        b = (i + 1) % n
        c = (i + 2) % n
        cross = (xs[b] - xs[a]) * (ys[c] - ys[b]) - (ys[b] - ys[a]) * (xs[c] - xs[b])
        s.add(cross >= eps)

    # Distance equalities for each row.
    def dsq(u: int, v: int):
        return (xs[u] - xs[v]) * (xs[u] - xs[v]) + (ys[u] - ys[v]) * (ys[u] - ys[v])

    for i, witnesses in enumerate(pattern):
        if not witnesses:
            continue
        first = witnesses[0]
        for w in witnesses[1:]:
            s.add(dsq(i, first) == dsq(i, w))

    return s, xs, ys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern-file", type=str, required=True)
    parser.add_argument("--timeout-ms", type=int, default=300000)
    parser.add_argument("--epsilon", type=str, default="1/1000000")
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    pattern_path = Path(args.pattern_file)
    pattern = load_pattern(pattern_path)
    n = len(pattern)
    print(f"[smt] loaded {n}-row pattern from {pattern_path}")
    for i, row in enumerate(pattern):
        print(f"  row {i}: {row}")

    import z3

    s, xs, ys = encode_realizability(pattern, args.epsilon)
    s.set("timeout", int(args.timeout_ms))
    print(f"[smt] z3 solver invoked with timeout={args.timeout_ms}ms epsilon={args.epsilon}")
    start = time.perf_counter()
    res = s.check()
    elapsed = time.perf_counter() - start

    payload: dict[str, object] = {
        "n": n,
        "pattern": pattern,
        "epsilon": args.epsilon,
        "elapsed_seconds": round(elapsed, 3),
        "trust": "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING",
        "notes": [
            "An UNSAT result with this epsilon proves no realization with strict convexity gap >= epsilon exists for this exact incidence pattern.",
            "A SAT result returns a numeric witness; it does NOT settle Erdos #97 because (a) the witness must be checked for independent geometric correctness, and (b) Erdos #97 asks about every strictly convex polygon, not a specific incidence pattern.",
            "Z3 over QF_NRA may return UNKNOWN due to resource limits.",
        ],
    }
    if res == z3.sat:
        m = s.model()
        coords = []
        for i in range(n):
            xv = m.eval(xs[i])
            yv = m.eval(ys[i])
            coords.append({"i": i, "x": str(xv), "y": str(yv)})
        payload["result"] = "sat"
        payload["coordinates"] = coords
        print(f"[smt] SAT in {elapsed:.2f}s -- realization found (coordinates in output)")
    elif res == z3.unsat:
        payload["result"] = "unsat"
        print(f"[smt] UNSAT in {elapsed:.2f}s -- no realization for this pattern with epsilon={args.epsilon}")
    else:
        payload["result"] = "unknown"
        print(f"[smt] UNKNOWN in {elapsed:.2f}s -- z3 hit timeout / resource limit")

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(f"[smt] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
