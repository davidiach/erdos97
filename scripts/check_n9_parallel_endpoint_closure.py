#!/usr/bin/env python3
"""Combinatorial parity + parallel-endpoint closure of the n=9 frontier.

This is a SECOND, lighter source for the closure of the review-pending n=9
pre-vertex-circle frontier. It takes the 184 stored frontier selected-witness
assignments as input and applies two sound necessary-condition combinatorial
filters, with NO vertex-circle quotient / metric reasoning:

  1. parity: the forced-perpendicularity graph must have no odd cycle
     (``odd_forced_perpendicular_cycle``); and
  2. parallel-endpoint: no two forced-parallel chords may share a vertex
     (``forced_parallel_endpoint_violation``), which under strict convexity
     would force three collinear vertices.

Both filters are consequences of repo lemmas L6 (radical-axis perpendicularity)
and L2 (distinct vertices of a strictly convex polygon), so they are sound
necessary conditions for Euclidean realizability.

Scope / non-claims. This script does NOT prove n=9, does NOT prove Erdos
Problem #97, does NOT claim a counterexample, and does NOT change the
official/global falsifiable-open status. The 184-assignment frontier is itself
the output of the review-pending n=9 incidence enumerator, which remains
review-pending; this script only re-closes that same stored frontier by a
lighter combinatorial argument and records the provenance gap that the
parallel-endpoint filter is not wired into ``src/erdos97/n9_incidence_frontier``.
The filters are necessary-only: all 15 n=8 survivor classes pass both, so this
route cannot settle n=8, let alone the global problem.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping, Sequence

from erdos97.incidence_filters import (
    forced_parallel_endpoint_violation,
    odd_forced_perpendicular_cycle,
)

ROOT = Path(__file__).resolve().parents[1]

FRONTIER = (
    ROOT / "data" / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)
DEFAULT_OUT = ROOT / "data" / "certificates" / "n9_parallel_endpoint_closure.json"

SCHEMA = "erdos97.n9_parallel_endpoint_closure.v1"
CLAIM_SCOPE = (
    "Lighter combinatorial second-source closure of the review-pending n=9 "
    "pre-vertex-circle frontier: the 184 stored frontier assignments are all "
    "killed by the parity (odd forced-perpendicular cycle) and parallel-endpoint "
    "necessary-condition filters, with no vertex-circle quotient reasoning. Not a "
    "proof of n=9, not a proof of Erdos Problem #97, not a counterexample, and not "
    "an official/global status update; the underlying n=9 frontier enumeration "
    "remains review-pending."
)
EXPECTED = {
    "total": 184,
    "killed_by_parity_odd_cycle": 22,
    "killed_by_parallel_endpoint": 162,
    "survive_both": 0,
}


def _chord_list(chord) -> list[int]:
    return [int(chord[0]), int(chord[1])]


def selected_rows_to_S(selected_rows: Sequence[Sequence[int]], n: int) -> list[list[int]]:
    """Convert ``[center, w1, w2, w3, w4]`` rows to S indexed by center."""
    S: list[list[int]] = [[] for _ in range(n)]
    for row in selected_rows:
        center = int(row[0])
        S[center] = sorted(int(w) for w in row[1:])
    return S


def classify_assignment(selected_rows: Sequence[Sequence[int]], n: int) -> dict[str, object]:
    """Apply parity then parallel-endpoint filters to one assignment."""
    S = selected_rows_to_S(selected_rows, n)
    odd_cycle = odd_forced_perpendicular_cycle(S)
    if odd_cycle is not None:
        return {
            "obstruction": "parity_odd_cycle",
            "witness": [_chord_list(c) for c in odd_cycle],
        }
    violation = forced_parallel_endpoint_violation(S)
    if violation is not None:
        u, v, shared = violation
        return {
            "obstruction": "parallel_endpoint",
            "witness": {
                "chord_u": _chord_list(u),
                "chord_v": _chord_list(v),
                "shared_vertices": [int(x) for x in shared],
            },
        }
    return {"obstruction": None, "witness": None}


def build_payload(root: Path = ROOT) -> dict[str, object]:
    frontier_path = root / "data" / "certificates" / (
        "n9_vertex_circle_frontier_motif_classification.json"
    )
    data = json.loads(frontier_path.read_text(encoding="utf-8"))
    assignments = data["assignments"]
    n = 9

    records: list[dict[str, object]] = []
    counts = {"parity_odd_cycle": 0, "parallel_endpoint": 0, "survive": 0}
    by_status: dict[str, dict[str, int]] = {}
    for entry in assignments:
        result = classify_assignment(entry["selected_rows"], n)
        status = str(entry.get("status", "unknown"))
        bucket = by_status.setdefault(
            status, {"total": 0, "parity_odd_cycle": 0, "parallel_endpoint": 0, "survive": 0}
        )
        bucket["total"] += 1
        obstruction = result["obstruction"]
        if obstruction == "parity_odd_cycle":
            counts["parity_odd_cycle"] += 1
            bucket["parity_odd_cycle"] += 1
        elif obstruction == "parallel_endpoint":
            counts["parallel_endpoint"] += 1
            bucket["parallel_endpoint"] += 1
        else:
            counts["survive"] += 1
            bucket["survive"] += 1
        records.append(
            {
                "assignment_id": str(entry["assignment_id"]),
                "vertex_circle_status": status,
                "obstruction": obstruction,
                "witness": result["witness"],
            }
        )

    records.sort(key=lambda r: r["assignment_id"])
    summary = {
        "total": len(assignments),
        "killed_by_parity_odd_cycle": counts["parity_odd_cycle"],
        "killed_by_parallel_endpoint": counts["parallel_endpoint"],
        "survive_both": counts["survive"],
        "by_vertex_circle_status": dict(sorted(by_status.items())),
    }
    payload = {
        "schema": SCHEMA,
        "claim_scope": CLAIM_SCOPE,
        "provenance": {
            "generator": "scripts/check_n9_parallel_endpoint_closure.py",
            "command": "python scripts/check_n9_parallel_endpoint_closure.py --write",
            "input": "data/certificates/n9_vertex_circle_frontier_motif_classification.json",
            "filters": [
                "erdos97.incidence_filters.odd_forced_perpendicular_cycle",
                "erdos97.incidence_filters.forced_parallel_endpoint_violation",
            ],
            "lemmas": ["L6 radical-axis perpendicularity", "L2 distinct vertices (strict convexity)"],
            "note": (
                "Necessary-condition combinatorial closure of the stored frontier; "
                "no proof of n=9 or Erdos #97 and no counterexample is claimed."
            ),
        },
        "summary": summary,
        "assignments": records,
    }
    return payload


def assert_expected_payload(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    for key, expected in EXPECTED.items():
        actual = summary.get(key)
        if actual != expected:
            raise AssertionError(
                f"summary[{key!r}] is {actual!r}, expected {expected!r}"
            )
    if summary["survive_both"] != 0:
        raise AssertionError("some frontier assignment survives both filters")


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    checked = json.loads(path.read_text(encoding="utf-8"))
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_human_summary(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("n=9 parallel-endpoint combinatorial closure")
    print(f"claim scope: {CLAIM_SCOPE}")
    print(
        f"total={summary['total']} "
        f"parity_odd_cycle={summary['killed_by_parity_odd_cycle']} "
        f"parallel_endpoint={summary['killed_by_parallel_endpoint']} "
        f"survive_both={summary['survive_both']}"
    )
    print(f"by vertex-circle status: {summary['by_vertex_circle_status']}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--write", action="store_true", help="write the checked artifact")
    parser.add_argument("--check", action="store_true", help="compare against the checked artifact")
    parser.add_argument("--assert-expected", action="store_true", help="assert stable closure counts")
    parser.add_argument("--json", action="store_true", help="print the full JSON payload")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload(ROOT)
    if args.assert_expected:
        assert_expected_payload(payload)
    if args.check:
        compare_artifact(payload, args.out)
    if args.write:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_human_summary(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
