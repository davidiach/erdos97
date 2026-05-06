#!/usr/bin/env python3
"""Run the integrated n=10 vertex-circle exhaustive selected-witness search.

This script drives ``GenericVertexSearch(n=10).exhaustive_search`` over the full
row0 sweep. It is a review-pending finite-case extension of the n=9
vertex-circle artifact. It does NOT prove Erdos Problem #97 and does NOT
claim a counterexample. Independent review is required before any
source-of-truth promotion.

Two modes:

* ``--single`` runs the search in one call (matches the n=9 driver shape).
* default (``--chunked``) runs each row0 index as its own slice and prints a
  progress line per slice; the aggregate counts are equivalent because each
  row0 slice sees only its own initial assignment and the dynamic
  minimum-remaining-options ordering is otherwise identical.
"""

from __future__ import annotations

import argparse
import json
import signal
import sys
from collections import Counter
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.generic_vertex_search import GenericVertexSearch  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "certificates" / "n10_vertex_circle_exhaustive.json"


def _print_payload(label: str, payload: dict[str, object]) -> None:
    print(label)
    print(f"  N: {payload.get('N')}")
    print(f"  row0_choices (M): {payload.get('M')}")
    print(f"  row0_start: {payload.get('row0_start')}")
    print(f"  row0_end: {payload.get('row0_end')}")
    print(f"  vertex_circle_pruning: {payload.get('vertex_circle_pruning')}")
    print(f"  nodes: {payload.get('nodes')}")
    print(f"  full: {payload.get('full')}")
    print(f"  aborted: {payload.get('aborted')}")
    print(f"  counts: {payload.get('counts')}")
    if "elapsed" in payload:
        print(f"  elapsed: {payload['elapsed']:.6f} s")


def _aggregate(slices: list[dict[str, object]]) -> dict[str, object]:
    """Aggregate slice results into a single payload-shaped record."""
    if not slices:
        return {
            "N": 10,
            "M": 126,
            "row0_start": 0,
            "row0_end": 0,
            "vertex_circle_pruning": None,
            "nodes": 0,
            "full": 0,
            "aborted": False,
            "counts": {},
            "elapsed": 0.0,
        }
    counts: Counter[str] = Counter()
    nodes = 0
    full = 0
    aborted = False
    elapsed = 0.0
    for slot in slices:
        nodes += int(slot["nodes"])  # type: ignore[arg-type]
        full += int(slot["full"])  # type: ignore[arg-type]
        aborted = aborted or bool(slot.get("aborted", False))
        elapsed += float(slot.get("elapsed", 0.0))
        for key, value in dict(slot.get("counts", {})).items():
            counts[key] += int(value)
    first = slices[0]
    return {
        "N": int(first["N"]),
        "M": int(first["M"]),
        "row0_start": int(first["row0_start"]),
        "row0_end": int(slices[-1]["row0_end"]),
        "vertex_circle_pruning": first["vertex_circle_pruning"],
        "nodes": nodes,
        "full": full,
        "aborted": aborted,
        "counts": dict(sorted(counts.items())),
        "elapsed": elapsed,
        "row_slices": slices,
    }


def _run_single(
    use_vertex_circle: bool, node_limit: int | None
) -> dict[str, object]:
    s = GenericVertexSearch(n=10)
    start = perf_counter()
    result = s.exhaustive_search(
        use_vertex_circle=use_vertex_circle, node_limit=node_limit
    )
    elapsed = perf_counter() - start
    payload = result.to_json(include_elapsed=True)
    payload["elapsed"] = elapsed
    return payload


def _run_chunked(
    use_vertex_circle: bool,
    node_limit: int | None,
    progress_label: str,
    *,
    row0_start: int = 0,
    row0_end: int | None = None,
    incremental_path: Path | None = None,
) -> dict[str, object]:
    s = GenericVertexSearch(n=10)
    M = s.row0_choice_count
    if row0_end is None:
        row0_end = M
    slices: list[dict[str, object]] = []
    aborted_at: int | None = None
    print(
        f"[{progress_label}] starting chunked sweep "
        f"row0=[{row0_start},{row0_end}) of {M}"
    )
    sys.stdout.flush()
    overall_start = perf_counter()

    def _save_incremental() -> None:
        if incremental_path is None:
            return
        snapshot = _aggregate(slices)
        snapshot["progress_label"] = progress_label
        snapshot["row0_planned_start"] = row0_start
        snapshot["row0_planned_end"] = row0_end
        snapshot["wallclock_elapsed"] = perf_counter() - overall_start
        snapshot["aborted_at_row0_index"] = aborted_at
        snapshot["row0_indices_completed"] = [
            int(s["row0_start"]) for s in slices if not s.get("aborted")
        ]
        incremental_path.parent.mkdir(parents=True, exist_ok=True)
        with incremental_path.open("w", encoding="utf-8", newline="\n") as h:
            h.write(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")

    interrupted = False

    def _handle(sig, _frame):  # type: ignore[no-untyped-def]
        nonlocal interrupted
        interrupted = True
        # Restore default and re-raise, but only after saving snapshot.
        signal.signal(sig, signal.SIG_DFL)

    prev_int = signal.getsignal(signal.SIGINT)
    prev_term = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGINT, _handle)
    signal.signal(signal.SIGTERM, _handle)
    try:
        for idx in range(row0_start, row0_end):
            slice_start = perf_counter()
            slice_result = s.exhaustive_search(
                row0_start=idx,
                row0_end=idx + 1,
                use_vertex_circle=use_vertex_circle,
                node_limit=node_limit,
            )
            slice_elapsed = perf_counter() - slice_start
            payload = slice_result.to_json(include_elapsed=True)
            payload["elapsed"] = slice_elapsed
            slices.append(payload)
            progress = (
                f"[{progress_label}] row0={idx:3d} "
                f"nodes={int(payload['nodes']):>9d} "
                f"full={int(payload['full']):>4d} "
                f"aborted={bool(payload['aborted'])} "
                f"counts={payload['counts']} "
                f"elapsed={slice_elapsed:.3f}s"
            )
            print(progress)
            sys.stdout.flush()
            _save_incremental()
            if payload.get("aborted"):
                aborted_at = idx
                break
            if interrupted:
                aborted_at = idx + 1 if idx + 1 < row0_end else None
                break
    finally:
        signal.signal(signal.SIGINT, prev_int)
        signal.signal(signal.SIGTERM, prev_term)

    overall_elapsed = perf_counter() - overall_start
    aggregate = _aggregate(slices)
    aggregate["wallclock_elapsed"] = overall_elapsed
    aggregate["aborted_at_row0_index"] = aborted_at
    aggregate["row0_indices_completed"] = [
        int(s["row0_start"]) for s in slices if not s.get("aborted")
    ]
    aggregate["row0_planned_start"] = row0_start
    aggregate["row0_planned_end"] = row0_end
    aggregate["interrupted"] = interrupted
    return aggregate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--node-limit", type=int, default=None,
        help=(
            "abort after this many visited nodes; in chunked mode applies "
            "per row0 slice"
        ),
    )
    parser.add_argument(
        "--main-only", action="store_true",
        help="run only the vertex-circle main search",
    )
    parser.add_argument(
        "--cross-check-only", action="store_true",
        help="run only the no-vertex-circle cross-check",
    )
    parser.add_argument(
        "--single", action="store_true",
        help="single-call non-chunked driver (matches the n=9 shape)",
    )
    parser.add_argument(
        "--write", action="store_true",
        help="write the stable JSON artifact",
    )
    parser.add_argument(
        "--out", default=str(DEFAULT_OUT),
        help="path used by --write",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="print the stable JSON payload to stdout",
    )
    parser.add_argument(
        "--row0-start", type=int, default=0,
        help="start row0 index (chunked mode only)",
    )
    parser.add_argument(
        "--row0-end", type=int, default=None,
        help="exclusive end row0 index (chunked mode only)",
    )
    parser.add_argument(
        "--incremental-out", type=str, default=None,
        help="path to write incremental aggregated snapshot per slice",
    )
    args = parser.parse_args()

    if args.main_only and args.cross_check_only:
        parser.error("--main-only and --cross-check-only are mutually exclusive")

    main_search: dict[str, object] | None = None
    cross_check: dict[str, object] | None = None

    incremental_main = (
        Path(args.incremental_out + ".main.json")
        if args.incremental_out
        else None
    )
    incremental_cross = (
        Path(args.incremental_out + ".cross.json")
        if args.incremental_out
        else None
    )

    if not args.cross_check_only:
        if args.single:
            main_search = _run_single(True, args.node_limit)
            _print_payload(
                "n=10 main vertex-circle exhaustive run", main_search
            )
        else:
            main_search = _run_chunked(
                True, args.node_limit, "main",
                row0_start=args.row0_start,
                row0_end=args.row0_end,
                incremental_path=incremental_main,
            )
            _print_payload(
                "n=10 main vertex-circle exhaustive run (aggregated)",
                main_search,
            )

    if not args.main_only:
        if args.single:
            cross_check = _run_single(False, args.node_limit)
            _print_payload(
                "n=10 cross-check (no vertex-circle pruning)", cross_check
            )
        else:
            cross_check = _run_chunked(
                False, args.node_limit, "cross",
                row0_start=args.row0_start,
                row0_end=args.row0_end,
                incremental_path=incremental_cross,
            )
            _print_payload(
                "n=10 cross-check (no vertex-circle pruning, aggregated)",
                cross_check,
            )

    payload: dict[str, object] = {
        "type": "n10_vertex_circle_exhaustive_v1",
        "trust": "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING",
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "The repo source-of-truth strongest local result remains n <= 8.",
            "This integrated n=10 vertex-circle artifact needs independent "
            "checker review before any public theorem-style use.",
        ],
        "n": 10,
        "row_size": 4,
        "cyclic_order": list(range(10)),
        "filters": [
            "two selected rows share at most two witnesses",
            "two-overlap source and witness chords cross in the cyclic order",
            "each witness pair occurs in at most two selected rows",
            "selected indegree is at most floor(2*(n-1)/(row_size-1))",
            "vertex-circle nested witness chords create no self-edge or "
            "strict cycle after selected-distance quotienting",
        ],
        "scope": (
            "Candidate repo-local machine-checked finite-case extension only; "
            "does not update the official/global falsifiable-open status."
        ),
    }
    if main_search is not None:
        payload["main_search"] = main_search
    if cross_check is not None:
        payload["cross_check_without_vertex_circle_pruning"] = cross_check
    main_complete = (
        main_search is not None
        and not main_search.get("aborted")
        and not main_search.get("interrupted", False)
        and main_search.get("row0_planned_end", 0) == 126
        and main_search.get("row0_planned_start", 1) == 0
    )
    cross_complete = (
        cross_check is not None
        and not cross_check.get("aborted")
        and not cross_check.get("interrupted", False)
        and cross_check.get("row0_planned_end", 0) == 126
        and cross_check.get("row0_planned_start", 1) == 0
    )
    if (
        main_search is not None
        and cross_check is not None
        and main_complete
        and cross_complete
        and main_search.get("full") == 0
    ):
        payload["conclusion"] = (
            "No n=10 selected-witness assignment survives these exact "
            "necessary filters in this checker."
        )
    else:
        payload["conclusion"] = (
            "Run incomplete: at least one phase aborted at the node limit "
            "or was interrupted; see partial counts and "
            "row0_indices_completed."
        )

    if args.write:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(f"wrote {display_path(out, ROOT)}")

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
