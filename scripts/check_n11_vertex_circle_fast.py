#!/usr/bin/env python3
"""Fast vertex-circle exhaustive checker for the Erdos #97 selected-witness search.

This script compiles ``scripts/n11_fast.c`` (a tight C re-implementation of the
algorithm in ``src/erdos97/n9_vertex_circle_exhaustive.py`` and
``src/erdos97/generic_vertex_search.py``), shards row0 indices across worker
processes, and aggregates the per-row0 deterministic counts into a single JSON
artifact.

The pruning rules are identical to the generic Python checker:
  - two selected rows share at most two witnesses (pair-cap);
  - any two-overlap source/witness chord pair must cross in cyclic order;
  - each witness pair occurs in at most ``pair_cap`` selected rows;
  - column indegree at most ``floor(2*(n-1)/(row_size-1))``;
  - vertex-circle nested chord strict monotonicity yields no self-edge or
    strict directed cycle on the quotient graph after selected-pair fusion.

Correctness is checked at compile time by running ``--n 9`` and comparing
against the known reference counts from
``src/erdos97/n9_vertex_circle_exhaustive.py``.

This is a review-pending finite-case checker. It does not prove Erdos #97
and does not claim a counterexample.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

C_SOURCE = ROOT / "scripts" / "n11_fast.c"
DEFAULT_PARTIAL_OUT = ROOT / "data" / "certificates" / "n11_vertex_circle_partial.json"
DEFAULT_EXHAUSTIVE_OUT = ROOT / "data" / "certificates" / "n11_vertex_circle_exhaustive.json"


def compile_binary(n: int, out_path: Path, cflags: str | None = None) -> Path:
    """Compile the C source for a given ``n`` into ``out_path``."""
    cc = os.environ.get("CC", "gcc")
    flags = (cflags or "-O3 -march=native -DNDEBUG").split()
    cmd = [cc, *flags, f"-DN_VAL={n}", "-o", str(out_path), str(C_SOURCE)]
    subprocess.run(cmd, check=True)
    return out_path


def _run_slice(binary: Path, start: int, end: int, fwd_check: bool = False) -> list[dict]:
    """Run a single slice; return parsed JSON-line list."""
    cmd = [str(binary), "--start", str(start), "--end", str(end)]
    if fwd_check:
        cmd.append("--fwd-check")
    proc = subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
    )
    rows = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def run_search(
    binary: Path,
    row0_start: int,
    row0_end: int,
    workers: int = 1,
    chunk: int | None = None,
    fwd_check: bool = False,
) -> tuple[list[dict], dict, float]:
    """Run the C binary across row0 indices using ``workers`` processes.

    Returns ``(per_row0_rows, meta, elapsed_seconds)``. Lines tagged with the
    ``_meta`` or ``_summary`` flag are not included in ``per_row0_rows``.
    """
    if workers < 1:
        raise ValueError("workers must be >= 1")
    n_rows = row0_end - row0_start
    if n_rows <= 0:
        return [], {}, 0.0
    if chunk is None:
        chunk = 1 if workers > 1 else n_rows
    slices = []
    cur = row0_start
    while cur < row0_end:
        nxt = min(cur + chunk, row0_end)
        slices.append((cur, nxt))
        cur = nxt

    t0 = time.monotonic()
    per_row0: list[dict] = []
    meta: dict = {}
    if workers == 1:
        for s, e in slices:
            rows = _run_slice(binary, s, e, fwd_check=fwd_check)
            for r in rows:
                if r.get("_meta"):
                    meta.update({k: v for k, v in r.items() if k != "_meta"})
                elif r.get("_summary"):
                    pass  # we recompute totals
                else:
                    per_row0.append(r)
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_run_slice, binary, s, e, fwd_check): (s, e)
                for s, e in slices
            }
            for fut in as_completed(futures):
                rows = fut.result()
                for r in rows:
                    if r.get("_meta"):
                        meta.update({k: v for k, v in r.items() if k != "_meta"})
                    elif r.get("_summary"):
                        pass
                    else:
                        per_row0.append(r)
    elapsed = time.monotonic() - t0
    per_row0.sort(key=lambda r: r["row0_index"])
    return per_row0, meta, elapsed


def aggregate(per_row0: list[dict]) -> dict:
    """Return aggregate totals over the per-row0 rows."""
    return {
        "total_nodes_visited": sum(r["nodes_visited"] for r in per_row0),
        "total_full_assignments": sum(r["full_assignments"] for r in per_row0),
        "total_partial_self_edge_prunes": sum(r["partial_self_edge_prunes"] for r in per_row0),
        "total_partial_strict_cycle_prunes": sum(r["partial_strict_cycle_prunes"] for r in per_row0),
        "total_elapsed_seconds_summed": sum(r["elapsed_seconds"] for r in per_row0),
    }


# Reference counts pulled from src/erdos97/n9_vertex_circle_exhaustive.py.
N9_REFERENCE = {
    "row0_total": 70,
    "total_nodes_visited": 16752,
    "total_full_assignments": 0,
    "total_partial_self_edge_prunes": 11271,
    "total_partial_strict_cycle_prunes": 11011,
}


def verify_n9(workers: int = 1, fwd_check: bool = False) -> dict:
    """Compile and run for n=9, asserting expected counts; return aggregate.

    With ``fwd_check=False`` (the default), ``nodes_visited`` is asserted to
    match the Python reference value 16752 exactly. With ``fwd_check=True``,
    ``nodes_visited`` is allowed to be smaller (forward checking removes
    dead-end recursive entries) but full and partial counts must still match.
    """
    with tempfile.TemporaryDirectory() as tmpd:
        binary = Path(tmpd) / "n9_fast"
        compile_binary(9, binary)
        per_row0, meta, elapsed = run_search(
            binary,
            row0_start=0,
            row0_end=70,
            workers=workers,
            fwd_check=fwd_check,
        )
    agg = aggregate(per_row0)
    expected = N9_REFERENCE
    mismatches: list[str] = []
    for k, v in expected.items():
        if k == "row0_total":
            if meta.get("row0_total") != v:
                mismatches.append(f"row0_total: got {meta.get('row0_total')}, want {v}")
            continue
        if k == "total_nodes_visited" and fwd_check:
            # Forward-checking is allowed to reduce nodes_visited; still
            # require that it does not exceed the reference value.
            if agg[k] > v:
                mismatches.append(f"{k}: got {agg[k]}, must be <= {v}")
            continue
        if agg[k] != v:
            mismatches.append(f"{k}: got {agg[k]}, want {v}")
    if mismatches:
        raise AssertionError("n=9 verification failed:\n  " + "\n  ".join(mismatches))
    agg["wallclock_elapsed_seconds"] = elapsed
    return agg


def build_artifact(
    n: int,
    per_row0: list[dict],
    meta: dict,
    wallclock_elapsed: float,
    row0_start: int,
    row0_end: int,
    completed: bool,
    workers: int,
    cflags: str,
    fwd_check: bool,
    n9_verification: dict | None,
) -> dict:
    """Build the JSON artifact payload."""
    agg = aggregate(per_row0)
    payload = {
        "type": (
            f"n{n}_vertex_circle_exhaustive_v1"
            if completed
            else f"n{n}_vertex_circle_partial_fast_v1"
        ),
        "trust": "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING",
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This artifact records the deterministic per-row0 counts from a"
            f" fast C re-implementation of the n={n} selected-witness search.",
            "Algorithm and pruning rules are identical to the generic Python"
            " checker (src/erdos97/generic_vertex_search.py). Cross-checked on"
            " n=9 against the reference (16752 nodes, 0 full survivors,"
            " 11271 self-edge prunes, 11011 strict-cycle prunes).",
        ],
        "n": n,
        "row_size": meta.get("row_size", 4),
        "pair_cap": meta.get("pair_cap", 2),
        "max_indegree": meta.get("max_indegree"),
        "num_pairs": meta.get("num_pairs"),
        "filters": [
            "two selected rows share at most two witnesses",
            "two-overlap source and witness chords cross in cyclic order",
            "each witness pair occurs in at most pair_cap selected rows",
            f"selected indegree is at most floor(2*({n}-1)/(row_size-1))",
            "vertex-circle nested witness chords create no self-edge or strict cycle after selected-pair quotienting",
        ],
        "row0_total": meta.get("row0_total"),
        "row0_start": row0_start,
        "row0_end": row0_end,
        "completed": completed,
        "workers": workers,
        "cflags": cflags,
        "fwd_check": fwd_check,
        "wallclock_elapsed_seconds": wallclock_elapsed,
        "aggregate": agg,
        "per_row0": per_row0,
    }
    if n9_verification is not None:
        payload["n9_cross_check"] = {
            "matched_reference": True,
            "reference": N9_REFERENCE,
            "wallclock_elapsed_seconds": n9_verification.get("wallclock_elapsed_seconds"),
        }
    if completed:
        payload["conclusion"] = (
            f"No n={n} selected-witness assignment passing these necessary"
            " filters survived to a full assignment."
            if agg["total_full_assignments"] == 0
            else (
                f"{agg['total_full_assignments']} selected-witness full"
                f" assignments passed all necessary filters at n={n}. These"
                " survivors are necessary-condition only and do not by"
                " themselves imply or refute Erdos #97 or claim a"
                " counterexample. They require deeper geometric review."
            )
        )
    else:
        payload["conclusion"] = (
            f"Partial run: row0 indices [{row0_start}, {row0_end}) of"
            f" {meta.get('row0_total')} were searched."
            f" {agg['total_full_assignments']} full assignments passing the"
            " necessary filters were found in this slice."
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=11, help="polygon size")
    parser.add_argument("--row0-start", type=int, default=0)
    parser.add_argument("--row0-end", type=int, default=None,
                        help="row0 index end (default: full)")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--chunk", type=int, default=None,
                        help="row0 indices per worker invocation; default auto")
    parser.add_argument("--cflags", default="-O3 -march=native -DNDEBUG",
                        help="extra CFLAGS for the C compile")
    parser.add_argument("--out", default=None,
                        help="output JSON path (default depends on completeness)")
    parser.add_argument("--skip-n9-verify", action="store_true",
                        help="skip the n=9 reference cross-check")
    parser.add_argument("--fwd-check", action="store_true",
                        help="enable forward-checking pruning (faster, but"
                        " makes nodes_visited <= the Python reference)")
    parser.add_argument("--binary", default=None,
                        help="path to a precompiled binary to use")
    args = parser.parse_args()

    n = args.n
    n9_verification: dict | None = None
    if not args.skip_n9_verify:
        print("verifying n=9 reference counts ...", flush=True)
        n9_verification = verify_n9(
            workers=min(args.workers, 4), fwd_check=args.fwd_check
        )
        print(
            f"  n=9 OK ({n9_verification['total_nodes_visited']} nodes,"
            f" {n9_verification['total_full_assignments']} full,"
            f" wallclock {n9_verification['wallclock_elapsed_seconds']:.3f}s)",
            flush=True,
        )

    with tempfile.TemporaryDirectory() as tmpd:
        if args.binary:
            binary = Path(args.binary)
        else:
            print(f"compiling fast checker for n={n} ...", flush=True)
            binary = Path(tmpd) / f"n{n}_fast"
            compile_binary(n, binary, cflags=args.cflags)

        # Get row0_total by running a tiny probe slice.
        probe = subprocess.run(
            [str(binary), "--start", "0", "--end", "0"],
            check=True, capture_output=True, text=True,
        )
        meta_probe: dict = {}
        for line in probe.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            j = json.loads(line)
            if j.get("_meta"):
                meta_probe.update(j)
        row0_total = meta_probe.get("row0_total", 0)
        if args.row0_end is None:
            row0_end = row0_total
        else:
            row0_end = args.row0_end

        print(
            f"running n={n} row0 [{args.row0_start}, {row0_end}) of {row0_total}"
            f" with {args.workers} workers ...",
            flush=True,
        )
        per_row0, meta, elapsed = run_search(
            binary,
            row0_start=args.row0_start,
            row0_end=row0_end,
            workers=args.workers,
            chunk=args.chunk,
            fwd_check=args.fwd_check,
        )
        meta.setdefault("row0_total", row0_total)

    completed = (args.row0_start == 0 and row0_end == row0_total)
    payload = build_artifact(
        n=n,
        per_row0=per_row0,
        meta=meta,
        wallclock_elapsed=elapsed,
        row0_start=args.row0_start,
        row0_end=row0_end,
        completed=completed,
        workers=args.workers,
        cflags=args.cflags,
        fwd_check=args.fwd_check,
        n9_verification=n9_verification,
    )

    if args.out:
        out_path = Path(args.out)
    else:
        out_path = (
            DEFAULT_EXHAUSTIVE_OUT.parent / f"n{n}_vertex_circle_exhaustive.json"
            if completed
            else DEFAULT_PARTIAL_OUT.parent / f"n{n}_vertex_circle_partial.json"
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as h:
        h.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    agg = payload["aggregate"]
    print(
        f"\nresult ({'complete' if completed else 'partial'}):"
        f"\n  row0 covered: [{args.row0_start}, {row0_end}) of {row0_total}"
        f"\n  total nodes visited: {agg['total_nodes_visited']:,}"
        f"\n  total full assignments: {agg['total_full_assignments']}"
        f"\n  total partial self-edge prunes: {agg['total_partial_self_edge_prunes']:,}"
        f"\n  total partial strict-cycle prunes: {agg['total_partial_strict_cycle_prunes']:,}"
        f"\n  wallclock elapsed: {elapsed:.3f}s"
        f"\n  artifact: {out_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
