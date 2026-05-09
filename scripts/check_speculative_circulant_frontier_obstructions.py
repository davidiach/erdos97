#!/usr/bin/env python3
"""Generate or check speculative circulant frontier obstruction certificates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "speculative_circulant_frontier_obstructions.json"
)
SCHEMA = "erdos97.speculative_circulant_frontier_obstructions.v1"
STATUS = "EXACT_SPECULATIVE_FRONTIER_CLEANUP"
TRUST = "EXACT_OBSTRUCTION"
CLAIM_SCOPE = (
    "Exact cleanup for selected speculative circulant patterns: C45 is killed "
    "as a fixed abstract selected-witness incidence pattern by the two-circle "
    "cap, while C41, C43, and C49 are fixed-natural-order diagnostics only. "
    "No general proof of Erdos Problem #97 and no counterexample are claimed."
)
PROVENANCE = {
    "generator": "scripts/check_speculative_circulant_frontier_obstructions.py",
    "command": (
        "python scripts/check_speculative_circulant_frontier_obstructions.py --write"
    ),
}
FORBIDDEN_CLAIMS = [
    "Erdos Problem #97 is solved.",
    "No counterexample exists.",
    "C49 is killed across all cyclic orders.",
    "The speculative frontier is closed.",
    "This proves the bridge theorem.",
    "general proof of Erdos Problem #97",
    "counterexample to Erdos Problem #97",
]


def circulant_row(n: int, offsets: Sequence[int], center: int) -> list[int]:
    """Return the selected witnesses in formula order."""

    return [int((center + offset) % n) for offset in offsets]


def validate_circulant_rows(n: int, offsets: Sequence[int]) -> None:
    """Check that each row is a 4-set avoiding its own center."""

    if len(offsets) != 4:
        raise ValueError("frontier checks are for 4-offset rows")
    for center in range(n):
        row = circulant_row(n, offsets, center)
        if len(set(row)) != 4:
            raise AssertionError(f"row {center} has repeated witnesses: {row}")
        if center in row:
            raise AssertionError(f"row {center} contains its center")


def chord_crosses_in_natural_order(n: int, chord_a: Sequence[int], chord_b: Sequence[int]) -> bool:
    """Return whether two endpoint-disjoint chords alternate in natural order."""

    del n
    a, b = sorted(int(endpoint) for endpoint in chord_a)
    c, d = (int(endpoint) for endpoint in chord_b)

    def inside(endpoint: int) -> bool:
        return a < endpoint < b

    return inside(c) != inside(d)


def natural_witness_order(n: int, center: int, witnesses: Sequence[int]) -> list[int]:
    """Order witnesses around a center in the natural cyclic order."""

    return sorted((int(witness) for witness in witnesses), key=lambda witness: (witness - center) % n)


def interval_in_witness_order(
    witness_order: Sequence[int],
    outer_pair: Sequence[int],
    inner_pair: Sequence[int],
) -> dict[str, Any]:
    """Return interval-containment data for two witness-witness chords."""

    positions = {witness: index for index, witness in enumerate(witness_order)}
    outer = tuple(sorted((positions[int(outer_pair[0])], positions[int(outer_pair[1])])))
    inner = tuple(sorted((positions[int(inner_pair[0])], positions[int(inner_pair[1])])))
    contains = (
        outer[0] <= inner[0]
        and inner[1] <= outer[1]
        and (outer[0] < inner[0] or inner[1] < outer[1])
    )
    return {
        "outer_interval": list(outer),
        "inner_interval": list(inner),
        "properly_contains": contains,
    }


def pair_key(pair: Sequence[int]) -> tuple[int, int]:
    """Normalize an unordered pair for cycle checks."""

    a, b = (int(pair[0]), int(pair[1]))
    if a == b:
        raise ValueError("loop pair is not allowed")
    return (a, b) if a < b else (b, a)


def two_circle_cap_record() -> dict[str, Any]:
    n = 45
    offsets = [4, 13, 25, 37]
    validate_circulant_rows(n, offsets)
    row0 = circulant_row(n, offsets, 0)
    row12 = circulant_row(n, offsets, 12)
    shared = sorted(set(row0) & set(row12))
    if row0 != [4, 13, 25, 37]:
        raise AssertionError(f"unexpected C45 row 0: {row0}")
    if row12 != [16, 25, 37, 4]:
        raise AssertionError(f"unexpected C45 row 12: {row12}")
    if shared != [4, 25, 37]:
        raise AssertionError(f"unexpected C45 shared witnesses: {shared}")
    return {
        "pattern": "C45_offsets_4_13_25_37",
        "n": n,
        "offsets": offsets,
        "status": "EXACT_ABSTRACT_INCIDENCE_OBSTRUCTION_TWO_CIRCLE_CAP",
        "claim_scope": (
            "Fixed abstract selected-witness incidence pattern across all "
            "cyclic orders; this does not imply any global theorem."
        ),
        "cyclic_order_scope": "all_orders_not_order_dependent",
        "row_pair": [0, 12],
        "rows": {
            "0": row0,
            "12": row12,
        },
        "shared_witnesses": shared,
        "shared_witness_count": len(shared),
        "verified_reason": (
            "Two distinct Euclidean circles can share at most two points; "
            "these two selected rows share three witnesses."
        ),
    }


def natural_crossing_record(
    *,
    pattern: str,
    n: int,
    offsets: Sequence[int],
    second_row: int,
    expected_shared: Sequence[int],
) -> dict[str, Any]:
    validate_circulant_rows(n, offsets)
    row0 = circulant_row(n, offsets, 0)
    rowj = circulant_row(n, offsets, second_row)
    shared = sorted(set(row0) & set(rowj))
    if shared != list(expected_shared):
        raise AssertionError(f"unexpected {pattern} shared witnesses: {shared}")
    crosses = chord_crosses_in_natural_order(n, [0, second_row], shared)
    if crosses:
        raise AssertionError(f"{pattern} natural-order chords unexpectedly cross")
    return {
        "pattern": pattern,
        "n": n,
        "offsets": list(offsets),
        "status": "EXACT_NATURAL_ORDER_CROSSING_OBSTRUCTION",
        "claim_scope": (
            "Fixed natural cyclic order only; no all-order obstruction for "
            "the abstract selected-witness pattern is claimed."
        ),
        "cyclic_order_scope": "natural_order_only",
        "natural_cyclic_order": list(range(n)),
        "row_pair": [0, second_row],
        "rows": {
            "0": row0,
            str(second_row): rowj,
        },
        "shared_witnesses": shared,
        "source_chord": [0, second_row],
        "common_witness_chord": shared,
        "source_and_witness_chords_alternate": crosses,
        "verified_reason": (
            "A two-witness row overlap in a strictly convex realization forces "
            "the source chord and common-witness chord to cross; these chords "
            "do not alternate in the natural cyclic order."
        ),
    }


def c49_vertex_circle_record() -> dict[str, Any]:
    n = 49
    offsets = [5, 16, 29, 41]
    validate_circulant_rows(n, offsets)
    raw_edges = [
        (18, [10, 34], [34, 47]),
        (42, [34, 47], [22, 47]),
        (6, [22, 47], [22, 35]),
        (30, [22, 35], [10, 46]),
        (5, [10, 46], [10, 34]),
    ]
    strict_cycle = []
    for center, outer_pair, inner_pair in raw_edges:
        row = circulant_row(n, offsets, center)
        witness_order = natural_witness_order(n, center, row)
        for endpoint in [*outer_pair, *inner_pair]:
            if endpoint not in row:
                raise AssertionError(f"endpoint {endpoint} is not in row {center}: {row}")
        interval = interval_in_witness_order(witness_order, outer_pair, inner_pair)
        if not interval["properly_contains"]:
            raise AssertionError(f"C49 row {center} lacks proper interval containment")
        strict_cycle.append(
            {
                "row": center,
                "row_witnesses_formula_order": row,
                "witness_order_around_center": witness_order,
                "outer_pair": outer_pair,
                "inner_pair": inner_pair,
                **interval,
                "inequality": f"d({outer_pair[0]},{outer_pair[1]}) > d({inner_pair[0]},{inner_pair[1]})",
                "verified_reason": (
                    "In the natural order around this center, the outer witness "
                    "interval properly contains the inner witness interval on "
                    "the same selected circle."
                ),
            }
        )

    for index, edge in enumerate(strict_cycle):
        next_edge = strict_cycle[(index + 1) % len(strict_cycle)]
        if pair_key(edge["inner_pair"]) != pair_key(next_edge["outer_pair"]):
            raise AssertionError("C49 strict inequalities do not form the recorded cycle")

    return {
        "pattern": "C49_offsets_5_16_29_41",
        "n": n,
        "offsets": offsets,
        "status": "EXACT_NATURAL_ORDER_VERTEX_CIRCLE_STRICT_CYCLE_OBSTRUCTION",
        "claim_scope": (
            "Fixed natural cyclic order only; no all-order obstruction for "
            "the abstract selected-witness pattern is claimed."
        ),
        "cyclic_order_scope": "natural_order_only",
        "natural_cyclic_order": list(range(n)),
        "strict_cycle": strict_cycle,
        "cycle_summary": [
            "d(10,34) > d(34,47)",
            "d(34,47) > d(22,47)",
            "d(22,47) > d(22,35)",
            "d(22,35) > d(10,46)",
            "d(10,46) > d(10,34)",
        ],
        "verified_reason": (
            "The listed vertex-circle interval containments force a strict "
            "cycle of ordinary distance inequalities in the natural order."
        ),
    }


def build_payload() -> dict[str, Any]:
    patterns = [
        two_circle_cap_record(),
        natural_crossing_record(
            pattern="C41_offsets_5_14_24_34",
            n=41,
            offsets=[5, 14, 24, 34],
            second_row=10,
            expected_shared=[24, 34],
        ),
        natural_crossing_record(
            pattern="C43_offsets_6_15_27_36",
            n=43,
            offsets=[6, 15, 27, 36],
            second_row=9,
            expected_shared=[15, 36],
        ),
        c49_vertex_circle_record(),
    ]
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": {
            "pattern_count": len(patterns),
            "abstract_incidence_obstruction_count": 1,
            "fixed_natural_order_diagnostic_count": 3,
            "global_problem_status_changed": False,
            "counterexample_claimed": False,
        },
        "patterns": patterns,
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "provenance": PROVENANCE,
    }


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def print_summary(payload: dict[str, Any]) -> None:
    print("speculative circulant frontier obstruction checks")
    print(f"  patterns: {payload['summary']['pattern_count']}")
    for record in payload["patterns"]:
        scope = record["cyclic_order_scope"]
        print(f"  {record['pattern']}: {record['status']} ({scope})")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write the generated artifact")
    parser.add_argument("--check", action="store_true", help="compare --out with regenerated data")
    parser.add_argument("--json", action="store_true", help="print the generated payload as JSON")
    args = parser.parse_args(argv)

    out = args.out if args.out.is_absolute() else ROOT / args.out
    payload = build_payload()

    if args.check:
        existing = load_json(out)
        if existing != payload:
            print(f"{display_path(out)} does not match regenerated payload", file=sys.stderr)
            return 1

    if args.write:
        write_json(out, payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_summary(payload)
        if args.check:
            print(f"OK: {display_path(out)} matches regenerated payload")
        if args.write:
            print(f"wrote {display_path(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
