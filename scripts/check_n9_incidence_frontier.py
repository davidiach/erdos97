#!/usr/bin/env python3
"""Run the bounded n=9 selected-witness incidence frontier scan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.incidence_filters import (  # noqa: E402
    row_ptolemy_product_cancellation_certificates,
)
from erdos97.n9_incidence_frontier import run_bounded_scan  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "certificates" / "n9_incidence_frontier_bounded.json"
EXPECTED_FILTER_ORDER = [
    "row_pair_intersection_cap",
    "adjacent_two_overlap",
    "crossing_bisector",
    "column_indegree_upper",
    "column_pair_cap",
    "odd_forced_perpendicular_cycle",
    "mutual_midpoint_collapse",
    "phi4_rectangle_trap",
    "row_ptolemy_product_cancellation",
    "accepted_frontier",
]


def _require_nonclaiming_notes(payload: dict[str, object]) -> None:
    notes = payload.get("notes")
    if not isinstance(notes, list) or not all(isinstance(note, str) for note in notes):
        raise AssertionError("payload notes should be a list of strings")
    joined = "\n".join(notes).lower()
    for phrase in ("no general proof", "no counterexample"):
        if phrase not in joined:
            raise AssertionError(f"payload notes must preserve {phrase!r}")


def _assert_row_ptolemy_examples(payload: dict[str, object]) -> None:
    examples = payload["examples"]
    if not isinstance(examples, dict):
        raise AssertionError("examples should be a mapping")
    row_ptolemy_examples = examples.get("row_ptolemy_product_cancellation")
    limits = payload.get("limits")
    max_examples = limits.get("max_examples_per_bucket") if isinstance(limits, dict) else None
    if max_examples == 0:
        if row_ptolemy_examples is not None:
            raise AssertionError("max_examples=0 should not store row-Ptolemy examples")
        return
    if not isinstance(row_ptolemy_examples, list) or len(row_ptolemy_examples) != 1:
        raise AssertionError("expected one row-Ptolemy example")

    example = row_ptolemy_examples[0]
    if not isinstance(example, dict):
        raise AssertionError("row-Ptolemy example should be a mapping")
    if example["status"] != "row_ptolemy_product_cancellation":
        raise AssertionError("row-Ptolemy example has unexpected status")
    if example["row_ptolemy_product_cancellation_count"] != 6:
        raise AssertionError("row-Ptolemy example should have six certificates")

    rows = example["rows"]
    order = example["order"]
    certificates = example["row_ptolemy_product_cancellation_certificates"]
    if not isinstance(rows, list) or not isinstance(order, list):
        raise AssertionError("row-Ptolemy example rows/order should be lists")
    if not isinstance(certificates, list) or not certificates:
        raise AssertionError("row-Ptolemy example should store certificate examples")
    replayed = row_ptolemy_product_cancellation_certificates(rows, order)
    if len(replayed) != example["row_ptolemy_product_cancellation_count"]:
        raise AssertionError("row-Ptolemy certificate count does not replay")
    if replayed[: len(certificates)] != certificates:
        raise AssertionError("stored row-Ptolemy certificate examples do not replay")

    first_certificate = certificates[0]
    if first_certificate["type"] != "row_ptolemy_product_cancellation":
        raise AssertionError("unexpected row-Ptolemy certificate type")
    if first_certificate["status"] != "EXACT_OBSTRUCTION_FOR_FIXED_PATTERN_AND_FIXED_ROW_ORDER":
        raise AssertionError("unexpected row-Ptolemy certificate status")
    if first_certificate["ptolemy_identity"] != "d02*d13 = d01*d23 + d03*d12":
        raise AssertionError("unexpected row-Ptolemy identity")
    if "supplied/certified row order" not in first_certificate["scope"]:
        raise AssertionError("row-Ptolemy certificate scope must mention supplied row order")


def assert_expected(payload: dict[str, object]) -> None:
    if payload["type"] != "n9_incidence_frontier_bounded_scan_v1":
        raise AssertionError("unexpected payload type")
    if payload["trust"] != "BOUNDED_INCIDENCE_CSP_DIAGNOSTIC":
        raise AssertionError("unexpected payload trust")
    _require_nonclaiming_notes(payload)
    if payload["search_complete"] is not True or payload["truncated"] is not False:
        raise AssertionError("default bounded frontier scan should complete")
    if payload["nodes_visited"] != 6793:
        raise AssertionError("unexpected node count")
    if payload["row_options_considered"] != 475231:
        raise AssertionError("unexpected row-options count")
    if payload["full_patterns_checked"] != 3:
        raise AssertionError("unexpected full-pattern count")

    full_counts = payload["full_classification_counts"]
    if not isinstance(full_counts, dict):
        raise AssertionError("full classification counts should be a mapping")
    if payload.get("filter_order") != EXPECTED_FILTER_ORDER:
        raise AssertionError("filter order drifted")
    if list(full_counts) != EXPECTED_FILTER_ORDER:
        raise AssertionError("full classification count order drifted")
    if set(full_counts) != set(EXPECTED_FILTER_ORDER):
        raise AssertionError("full classification keys drifted")
    expected_full_counts = {
        status: 0 for status in EXPECTED_FILTER_ORDER
    }
    expected_full_counts.update(
        {
            "odd_forced_perpendicular_cycle": 1,
            "phi4_rectangle_trap": 1,
            "row_ptolemy_product_cancellation": 1,
        }
    )
    if full_counts != expected_full_counts:
        raise AssertionError(f"unexpected full classification counts: {full_counts}")
    if sum(int(count) for count in full_counts.values()) != payload["full_patterns_checked"]:
        raise AssertionError("full classification counts do not sum to checked patterns")
    if payload["accepted_frontier_count"] != full_counts["accepted_frontier"]:
        raise AssertionError("accepted frontier count drifted")
    if payload["accepted_frontier_count"] != 0:
        raise AssertionError("row-Ptolemy should kill the previous accepted frontier example")
    _assert_row_ptolemy_examples(payload)

    seeded = payload["seeded_cases"]
    if not isinstance(seeded, list) or len(seeded) != 1:
        raise AssertionError("missing seeded n=9 rectangle-trap case")
    classification = seeded[0]["classification"]
    if not isinstance(classification, dict):
        raise AssertionError("seeded case classification should be a mapping")
    if classification["status"] != "phi4_rectangle_trap":
        raise AssertionError("registered n=9 seed should be killed by phi4 rectangle trap")
    if classification["rectangle_trap_4_cycles"] != 1:
        raise AssertionError("registered n=9 seed should have one phi4 trap")


def print_summary(payload: dict[str, object]) -> None:
    print("bounded n=9 incidence/CSP frontier scan")
    print(f"nodes visited: {payload['nodes_visited']}")
    print(f"row options considered: {payload['row_options_considered']}")
    print(f"full patterns checked: {payload['full_patterns_checked']}")
    print(f"truncated: {payload['truncated']}")
    print(f"partial rejections: {payload['partial_rejection_counts']}")
    print(f"full classifications: {payload['full_classification_counts']}")
    print(f"accepted frontier count: {payload['accepted_frontier_count']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print full JSON")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="write JSON payload here")
    parser.add_argument("--write", action="store_true", help="write --out")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--max-nodes", type=int, default=250_000)
    parser.add_argument("--max-full-patterns", type=int, default=250)
    parser.add_argument("--max-examples", type=int, default=3)
    args = parser.parse_args()

    payload = run_bounded_scan(
        max_nodes=args.max_nodes,
        max_full_patterns=args.max_full_patterns,
        max_examples=args.max_examples,
    )
    if args.assert_expected:
        assert_expected(payload)

    if args.write:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_summary(payload)
        if args.assert_expected:
            print("OK: bounded n=9 frontier expectations verified")
        if args.write:
            print(f"wrote {display_path(args.out, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
