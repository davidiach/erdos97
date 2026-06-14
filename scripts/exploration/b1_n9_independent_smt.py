#!/usr/bin/env python3
"""B1: Independent from-scratch z3 SMT re-derivation of the n=9 frontier obstruction.

Lane B1 (Erdos Problem #97). This is a *coordinate-geometry* nonlinear-real
SMT model built from scratch. It shares NO code with the repository's
combinatorial vertex-circle brancher (``scripts/check_n9_vertex_circle_exhaustive.py``
and ``src/erdos97/n9_vertex_circle_exhaustive.py``), which never introduces
point coordinates at all. Here every vertex is a pair of z3 Reals and the
question "does this selected-witness incidence pattern embed as a strictly
convex 9-gon?" is posed directly as nonlinear real arithmetic and handed to z3.

Trust label of any output: at most
``MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`` (an independent second
source corroborating the stored combinatorial claim). This script does NOT and
CANNOT promote n=9, prove Erdos #97, or claim a counterexample. A SAT result
would be a flag for exact follow-up, NOT a counterexample claim (z3 nonlinear
real models are subject to solver trust and the model must be re-checked
exactly).

Model, for a fixed incidence assignment (one 4-set S_i of OTHER vertices per
center i, taken as a CASE SPLIT from the stored 184-row frontier):

  variables : x_i, y_i in Reals, i = 0..8
  gauge     : p0 = (0,0), p1 = (1,0)            # kills translation, rotation,
                                                 # and the scale of edge 0->1
  convexity : for every cyclically consecutive triple (p_a, p_b, p_c) the signed
              turn cross((p_b-p_a),(p_c-p_b)) > 0  (STRICT, all 9 turns) -- this
              is the strict-convexity encoding required by the impossibility lane
  distinct  : p_i != p_j for all i<j  (explicit; convexity already implies it,
              but we assert it as the problem statement requires distinct vertices)
  witnesses : for each center i with S_i = {a,b,c,d},
              |p_i-p_a|^2 == |p_i-p_b|^2 == |p_i-p_c|^2 == |p_i-p_d|^2
              (3 equations per center; 27 polynomial equations total)

Then ask z3 (logic QF_NRA) for SAT / UNSAT per assignment.

  UNSAT  -> this incidence pattern admits NO strictly convex 9-gon realization.
            Confirms (independently of the combinatorial brancher) that the
            pattern is obstructed.
  SAT    -> a realization exists; would REFUTE the stored "all obstructed"
            claim. Flagged for exact certification; NOT a counterexample claim.
  unknown/timeout -> z3 could not decide within the budget. Reported honestly.

Usage:
  python scripts/exploration/b1_n9_independent_smt.py --limit 40 --timeout-ms 8000
  python scripts/exploration/b1_n9_independent_smt.py --all --timeout-ms 6000 --json out.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import z3

ROOT = Path(__file__).resolve().parents[2]
FRONTIER = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)

N = 9
ROW_SIZE = 4


def load_assignments(path: Path) -> tuple[list[dict], list[int]]:
    """Load the 184 frontier assignments as INPUT data (not trusted truth).

    Returns the list of assignment records and the stored cyclic order. Each
    record's ``selected_rows`` is a list of 9 rows ``[center, w1, w2, w3, w4]``.
    The schema is validated defensively; we treat the file purely as the source
    of incidence patterns for the case split.
    """
    with path.open() as fh:
        data = json.load(fh)
    if int(data.get("n", -1)) != N:
        raise ValueError(f"expected n={N}, got {data.get('n')}")
    cyclic_order = list(data["cyclic_order"])
    if sorted(cyclic_order) != list(range(N)):
        raise ValueError(f"cyclic_order is not a permutation of 0..{N - 1}")
    assignments = data["assignments"]
    # Defensive schema validation of every row.
    for a in assignments:
        rows = a["selected_rows"]
        if len(rows) != N:
            raise ValueError(f"{a.get('assignment_id')}: expected {N} rows")
        centers = sorted(r[0] for r in rows)
        if centers != list(range(N)):
            raise ValueError(f"{a.get('assignment_id')}: centers not 0..{N - 1}")
        for r in rows:
            if len(r) != ROW_SIZE + 1:
                raise ValueError(f"{a.get('assignment_id')}: bad row width {r}")
            center, wit = r[0], r[1:]
            if len(set(wit)) != ROW_SIZE:
                raise ValueError(f"{a.get('assignment_id')}: witnesses not distinct {r}")
            if center in wit:
                raise ValueError(f"{a.get('assignment_id')}: center is its own witness {r}")
            if any(not (0 <= w < N) for w in wit):
                raise ValueError(f"{a.get('assignment_id')}: witness out of range {r}")
    return assignments, cyclic_order


def sq_dist(px, py, qx, qy):
    """Squared Euclidean distance between two symbolic points."""
    dx = px - qx
    dy = py - qy
    return dx * dx + dy * dy


def cross(ax, ay, bx, by, cx, cy):
    """Signed turn (cross product) at b for the directed path a -> b -> c.

    cross > 0 means a left turn. Requiring this for every cyclically
    consecutive triple in a fixed cyclic order encodes strict convexity with a
    consistent (counter-clockwise) orientation.
    """
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


def build_solver(assignment: dict, cyclic_order: list[int], timeout_ms: int):
    """Build a fresh z3 solver encoding one incidence assignment.

    Returns (solver, x, y) where x, y are the coordinate variable lists.
    Nothing here is reused from the repository's combinatorial pipeline; the
    geometry is assembled directly from coordinates.
    """
    solver = z3.Solver()
    solver.set("timeout", int(timeout_ms))
    # QF_NRA: quantifier-free nonlinear real arithmetic.
    try:
        solver.set("logic", "QF_NRA")
    except z3.Z3Exception:
        pass

    x = [z3.Real(f"x{i}") for i in range(N)]
    y = [z3.Real(f"y{i}") for i in range(N)]

    # Gauge fixing: translation + rotation + one edge scale.
    solver.add(x[0] == 0, y[0] == 0)
    solver.add(x[1] == 1, y[1] == 0)

    # Strict convexity: all 9 consecutive turns strictly positive (CCW) in the
    # stored cyclic order. This is the strict-convexity ingredient the
    # impossibility lane is required to encode.
    order = cyclic_order
    for k in range(N):
        a = order[k]
        b = order[(k + 1) % N]
        c = order[(k + 2) % N]
        solver.add(cross(x[a], y[a], x[b], y[b], x[c], y[c]) > 0)

    # Explicit pairwise distinctness (problem requires distinct vertices).
    for i in range(N):
        for j in range(i + 1, N):
            solver.add(z3.Or(x[i] != x[j], y[i] != y[j]))

    # Selected-witness equal-squared-distance constraints: 3 equations/center.
    for row in assignment["selected_rows"]:
        center = row[0]
        wit = row[1:]
        ref = sq_dist(x[center], y[center], x[wit[0]], y[wit[0]])
        for w in wit[1:]:
            solver.add(sq_dist(x[center], y[center], x[w], y[w]) == ref)

    return solver, x, y


def solve_assignment(assignment: dict, cyclic_order: list[int], timeout_ms: int) -> dict:
    """Run z3 on one assignment; return a result record."""
    solver, x, y = build_solver(assignment, cyclic_order, timeout_ms)
    t0 = time.perf_counter()
    res = solver.check()
    elapsed = time.perf_counter() - t0
    # z3's CheckSatResult is not hashable in all versions, so compare directly.
    if res == z3.sat:
        label = "sat"
    elif res == z3.unsat:
        label = "unsat"
    else:
        label = "unknown"
    record = {
        "assignment_id": assignment.get("assignment_id"),
        "stored_status": assignment.get("status"),
        "family_id": assignment.get("family_id"),
        "template_id": assignment.get("template_id"),
        "z3_result": label,
        "elapsed_seconds": round(elapsed, 4),
    }
    if res == z3.unknown:
        record["reason"] = solver.reason_unknown()
    if res == z3.sat:
        # Extract an approximate numeric model for exact follow-up. NOT a
        # counterexample claim -- this must be re-certified exactly.
        m = solver.model()
        pts = []
        for i in range(N):
            xi = m.eval(x[i], model_completion=True)
            yi = m.eval(y[i], model_completion=True)
            try:
                fx = float(xi.as_fraction())
                fy = float(yi.as_fraction())
            except (AttributeError, ValueError):
                fx, fy = repr(xi), repr(yi)
            pts.append([fx, fy])
        record["model_points_float"] = pts
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--frontier",
        default=str(FRONTIER),
        help="path to the 184-row frontier motif-classification JSON (input data)",
    )
    parser.add_argument("--limit", type=int, default=None, help="only the first K assignments")
    parser.add_argument("--all", action="store_true", help="run all assignments")
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=8000,
        help="per-assignment z3 timeout in milliseconds",
    )
    parser.add_argument("--json", default=None, help="write full per-assignment JSON here")
    parser.add_argument(
        "--budget-seconds",
        type=float,
        default=None,
        help="stop launching new assignments once wall time exceeds this",
    )
    args = parser.parse_args()

    assignments, cyclic_order = load_assignments(Path(args.frontier))
    total_available = len(assignments)

    if args.all:
        chosen = assignments
    elif args.limit is not None:
        chosen = assignments[: args.limit]
    else:
        chosen = assignments[: min(40, total_available)]

    print("# B1 independent n=9 z3 SMT (coordinate geometry, from scratch)")
    print(f"# frontier file: {args.frontier}")
    print(f"# total stored assignments: {total_available}")
    print(f"# attempting: {len(chosen)}   per-assignment timeout: {args.timeout_ms} ms")
    print(f"# z3 version: {z3.get_version_string()}")
    print()

    results = []
    counts = {"unsat": 0, "sat": 0, "unknown": 0}
    by_status = {}
    wall0 = time.perf_counter()
    for idx, a in enumerate(chosen):
        if args.budget_seconds is not None and (time.perf_counter() - wall0) > args.budget_seconds:
            print(f"# budget {args.budget_seconds}s exceeded after {idx} assignments; stopping")
            break
        rec = solve_assignment(a, cyclic_order, args.timeout_ms)
        results.append(rec)
        counts[rec["z3_result"]] += 1
        st = rec["stored_status"]
        by_status.setdefault(st, {"unsat": 0, "sat": 0, "unknown": 0})
        by_status[st][rec["z3_result"]] += 1
        flag = ""
        if rec["z3_result"] == "sat":
            flag = "   <<< SAT: FLAG FOR EXACT FOLLOW-UP (NOT a counterexample claim)"
        elif rec["z3_result"] == "unknown":
            flag = f"   (unknown: {rec.get('reason', '')})"
        print(
            f"{rec['assignment_id']:>5}  stored={rec['stored_status']:<12}"
            f"  fam={rec['family_id']:<4} tmpl={rec['template_id']:<4}"
            f"  z3={rec['z3_result']:<8} {rec['elapsed_seconds']:>7.3f}s{flag}"
        )

    wall = time.perf_counter() - wall0
    print()
    print(f"# attempted: {len(results)}   wall: {wall:.2f}s")
    print(f"# z3 results: {counts}")
    print(f"# by stored status: {json.dumps(by_status)}")
    sat_ids = [r["assignment_id"] for r in results if r["z3_result"] == "sat"]
    if sat_ids:
        print(f"# !!! SAT assignments (need exact follow-up, NOT counterexamples): {sat_ids}")
    else:
        print("# no SAT assignments: every attempted pattern was UNSAT or unknown")

    if args.json:
        payload = {
            "lane": "B1",
            "type": "b1_n9_independent_smt_v1",
            "trust": "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING",
            "scope": (
                "Independent coordinate-geometry z3 corroboration of the stored "
                "n=9 vertex-circle frontier obstruction; does not promote n=9, "
                "prove Erdos #97, or claim a counterexample."
            ),
            "encodes_strict_convexity": True,
            "model": "QF_NRA: 9 (x,y) reals, gauge p0=(0,0) p1=(1,0), all 9 "
            "consecutive turns strictly positive, pairwise distinct, "
            "27 equal-squared-distance witness equations",
            "frontier_file": args.frontier,
            "total_available": total_available,
            "attempted": len(results),
            "per_assignment_timeout_ms": args.timeout_ms,
            "z3_version": z3.get_version_string(),
            "wall_seconds": round(wall, 3),
            "counts": counts,
            "by_stored_status": by_status,
            "sat_assignment_ids": sat_ids,
            "results": results,
        }
        with open(args.json, "w") as fh:
            json.dump(payload, fh, indent=2)
        print(f"# wrote {args.json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
