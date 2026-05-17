#!/usr/bin/env python3
"""Check full rich-class quotient replay over generated n=9 blocker packets.

This is a finite bridge diagnostic only. It proves no general theorem about
Erdos Problem #97 and supplies no counterexample.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.adaptive_blockers import is_radius_blocker  # noqa: E402
from erdos97.radius_blocker_packets import TRUST  # noqa: E402
from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    RichClassRow,
    StrictInequality,
    replay_vertex_circle_rich_quotient,
)

SCHEMA = "erdos97.n9_radius_blocker_rich_quotient_sweep.v1"
STATUS = "N9_RADIUS_BLOCKER_RICH_QUOTIENT_SWEEP_ONLY"
DEFAULT_SOURCE = (
    ROOT / "data" / "certificates" / "n9_radius_blocker_shape_sweep.json"
)
DEFAULT_OUT = (
    ROOT / "data" / "certificates" / "n9_radius_blocker_rich_quotient_sweep.json"
)
N = 9
ORDER = list(range(N))
SOURCE_STATUS_ORDER = ("self_edge", "strict_cycle")
EXPECTED_SUMMARY = {
    "n": 9,
    "source_shape_count": 10,
    "packet_count": 20,
    "source_status_counts": {"self_edge": 10, "strict_cycle": 10},
    "rich_class_count_total": 180,
    "max_rich_class_size": 5,
    "all_packets_radius_blockers": True,
    "quotient_status_counts": {"self_edge": 20},
    "all_packets_obstructed": True,
    "total_strict_edge_count": 4500,
    "total_self_edge_conflict_count": 3533,
    "min_self_edge_conflict_count": 148,
    "max_self_edge_conflict_count": 207,
    "first_self_edge_row_counts": {"0": 20},
    "packet_max_blocker_intersection_size_counts": {"2": 1, "3": 3, "4": 16},
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_shape_sweep(path: Path) -> Mapping[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise AssertionError("shape sweep artifact is not an object")
    return payload


def ordered_source_statuses(examples: Mapping[str, object]) -> list[str]:
    """Return stable source statuses, putting known statuses first."""

    known = [status for status in SOURCE_STATUS_ORDER if status in examples]
    rest = sorted(status for status in examples if status not in SOURCE_STATUS_ORDER)
    return known + rest


def source_examples(payload: Mapping[str, object]) -> list[dict[str, object]]:
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise AssertionError("shape sweep artifact has no cases list")
    records: list[dict[str, object]] = []
    for case_index, raw_case in enumerate(cases):
        if not isinstance(raw_case, Mapping):
            raise AssertionError(f"shape sweep case {case_index} is not an object")
        examples = raw_case.get("obstruction_examples")
        if not isinstance(examples, Mapping):
            raise AssertionError(f"shape sweep case {case_index} has no examples")
        for status in ordered_source_statuses(examples):
            raw_examples = examples[status]
            if not isinstance(raw_examples, list):
                raise AssertionError(f"examples for {status!r} are not a list")
            for example_index, raw_example in enumerate(raw_examples):
                if not isinstance(raw_example, Mapping):
                    raise AssertionError("source obstruction example is not an object")
                rows = raw_example.get("selected_rows")
                if not isinstance(rows, list):
                    raise AssertionError("source example has no selected rows")
                records.append(
                    {
                        "case_index": case_index,
                        "case_name": raw_case.get("name"),
                        "blocker": [int(label) for label in raw_case["blocker"]],
                        "source_status": status,
                        "source_example_index": example_index,
                        "source_selected_rows": [
                            [int(label) for label in row] for row in rows
                        ],
                    }
                )
    return records


def extra_label_candidates(
    center: int,
    row: Sequence[int],
    blocker: Sequence[int],
) -> list[int]:
    row_set = set(int(label) for label in row)
    blocker_set = set(int(label) for label in blocker)
    candidates: list[int] = []
    for label in range(N):
        if label == center or label in row_set:
            continue
        if center in blocker_set and len((row_set | {label}) & blocker_set) >= 3:
            continue
        candidates.append(label)
    return candidates


def choose_extra_label(center: int, row: Sequence[int], blocker: Sequence[int]) -> int:
    """Choose a deterministic size-five extension preserving blocker status.

    The radius-blocker condition only constrains centers inside the blocker.
    For continuity with the earlier pilot, prefer an added label that also
    keeps the enlarged class below three blocker vertices when such a label
    exists.
    """

    row_set = set(int(label) for label in row)
    blocker_set = set(int(label) for label in blocker)
    candidates = extra_label_candidates(center, row, blocker)
    for label in candidates:
        if len((row_set | {label}) & blocker_set) <= 2:
            return label
    if candidates:
        return candidates[0]
    raise AssertionError(f"no safe size-five extension for center {center}")


def rich_rows_from_source(
    selected_rows: Sequence[Sequence[int]],
    blocker: Sequence[int],
) -> tuple[list[RichClassRow], list[dict[str, object]]]:
    blocker_set = set(int(label) for label in blocker)
    rich_rows: list[RichClassRow] = []
    expansion_records: list[dict[str, object]] = []
    for center, row in enumerate(selected_rows):
        row_list = [int(label) for label in row]
        added = choose_extra_label(center, row_list, blocker)
        rich_class = tuple(sorted(set(row_list) | {added}))
        intersection_size = len(set(rich_class) & blocker_set)
        rich_rows.append(RichClassRow(center=center, witnesses=rich_class))
        expansion_records.append(
            {
                "center": center,
                "source_exact_row": row_list,
                "added_label": added,
                "rich_class": list(rich_class),
                "blocker_intersection_size": intersection_size,
                "inside_blocker_center": center in blocker_set,
            }
        )
    return rich_rows, expansion_records


def rich_classes_for_blocker(rows: Sequence[RichClassRow]) -> tuple[tuple[tuple[int, ...], ...], ...]:
    return tuple((row.witnesses,) for row in rows)


def counter_to_json(counter: Counter[object]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter, key=lambda item: str(item))}


def strict_inequality_to_json(edge: StrictInequality) -> dict[str, object]:
    return {
        "row": edge.row,
        "witness_order": list(edge.witness_order),
        "outer_interval": list(edge.outer_interval),
        "inner_interval": list(edge.inner_interval),
        "outer_pair": list(edge.outer_pair),
        "inner_pair": list(edge.inner_pair),
        "outer_class": list(edge.outer_class),
        "inner_class": list(edge.inner_class),
    }


def build_packet_record(source: Mapping[str, object]) -> dict[str, object]:
    blocker = [int(label) for label in source["blocker"]]
    selected_rows = source["source_selected_rows"]
    if not isinstance(selected_rows, list):
        raise AssertionError("source selected rows are missing")
    rich_rows, expansions = rich_rows_from_source(selected_rows, blocker)
    radius_blocker_ok = is_radius_blocker(rich_classes_for_blocker(rich_rows), blocker)
    replay = replay_vertex_circle_rich_quotient(N, ORDER, rich_rows)
    first_self_edge = (
        strict_inequality_to_json(replay.self_edge_conflicts[0])
        if replay.self_edge_conflicts
        else None
    )

    return {
        "packet_id": (
            f"{source['case_name']}:{source['source_status']}:"
            f"{source['source_example_index']}"
        ),
        "case_index": source["case_index"],
        "case_name": source["case_name"],
        "blocker": blocker,
        "source_status": source["source_status"],
        "source_example_index": source["source_example_index"],
        "source_selected_rows": selected_rows,
        "expansion_records": expansions,
        "radius_blocker_ok": radius_blocker_ok,
        "replay_summary": {
            "vertex_circle_status": replay.status,
            "strict_edge_count": replay.strict_edge_count,
            "self_edge_conflict_count": len(replay.self_edge_conflicts),
            "cycle_edge_count": len(replay.cycle_edges),
            "first_self_edge": first_self_edge,
        },
    }


def build_summary(records: Sequence[Mapping[str, object]], source_shape_count: int) -> dict[str, object]:
    source_status_counts: Counter[str] = Counter()
    quotient_status_counts: Counter[str] = Counter()
    first_self_edge_rows: Counter[int | None] = Counter()
    max_blocker_intersections: Counter[int] = Counter()
    self_edge_counts: list[int] = []
    total_strict_edges = 0
    rich_class_total = 0
    max_rich_class_size = 0

    for record in records:
        source_status_counts[str(record["source_status"])] += 1
        replay_summary = record["replay_summary"]
        if not isinstance(replay_summary, Mapping):
            raise AssertionError("packet has no replay summary")
        quotient_status_counts[str(replay_summary["vertex_circle_status"])] += 1
        total_strict_edges += int(replay_summary["strict_edge_count"])
        self_edge_counts.append(int(replay_summary["self_edge_conflict_count"]))
        first_edge = replay_summary["first_self_edge"]
        first_self_edge_rows[
            int(first_edge["row"]) if isinstance(first_edge, Mapping) else None
        ] += 1
        expansions = record["expansion_records"]
        if not isinstance(expansions, list):
            raise AssertionError("packet has no expansion records")
        rich_class_total += len(expansions)
        max_blocker_intersections[
            max(int(expansion["blocker_intersection_size"]) for expansion in expansions)
        ] += 1
        max_rich_class_size = max(
            max_rich_class_size,
            max(len(expansion["rich_class"]) for expansion in expansions),
        )

    return {
        "n": N,
        "order": ORDER,
        "source_shape_count": source_shape_count,
        "packet_count": len(records),
        "source_status_counts": counter_to_json(source_status_counts),
        "rich_class_count_total": rich_class_total,
        "max_rich_class_size": max_rich_class_size,
        "all_packets_radius_blockers": all(
            bool(record["radius_blocker_ok"]) for record in records
        ),
        "quotient_status_counts": counter_to_json(quotient_status_counts),
        "all_packets_obstructed": quotient_status_counts.get("ok", 0) == 0,
        "total_strict_edge_count": total_strict_edges,
        "total_self_edge_conflict_count": sum(self_edge_counts),
        "min_self_edge_conflict_count": min(self_edge_counts),
        "max_self_edge_conflict_count": max(self_edge_counts),
        "first_self_edge_row_counts": counter_to_json(first_self_edge_rows),
        "packet_max_blocker_intersection_size_counts": counter_to_json(
            max_blocker_intersections
        ),
    }


def build_payload(source: Path = DEFAULT_SOURCE) -> dict[str, object]:
    """Build the deterministic full rich-class quotient sweep payload."""

    shape_sweep = load_shape_sweep(source)
    sources = source_examples(shape_sweep)
    records = [build_packet_record(source_record) for source_record in sources]
    cases = shape_sweep.get("cases")
    if not isinstance(cases, list):
        raise AssertionError("shape sweep artifact has no cases list")

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Bounded n=9 full rich-class quotient sweep. It enlarges each "
            "stored shape-sweep obstruction example to one synthetic "
            "size-five rich class per center, preserving the actual "
            "radius-blocker condition, and replays the full rich quotient. "
            "This is finite packet evidence only: it is not an n=9 proof, "
            "not a proof of the adaptive blocker bridge, and not a "
            "counterexample."
        ),
        "summary": build_summary(records, len(cases)),
        "source_shape_sweep": {
            "path": source.relative_to(ROOT).as_posix(),
            "schema": shape_sweep.get("schema"),
            "status": shape_sweep.get("status"),
            "trust": shape_sweep.get("trust"),
            "sha256": sha256_file(source),
            "summary": shape_sweep.get("summary"),
        },
        "expansion_rule": {
            "rule": (
                "For each stored exact-four source row, add one deterministic "
                "extra label to make a size-five rich class."
            ),
            "radius_blocker_boundary": (
                "When the row center is inside the blocker, the added label "
                "must keep the rich class below three blocker vertices. For "
                "centers outside the blocker, the radius-blocker definition "
                "does not constrain blocker intersection."
            ),
            "preference": (
                "Among labels preserving the actual blocker condition, choose "
                "the first label that also keeps the class below three blocker "
                "vertices when such a label exists; otherwise choose the "
                "first actual-condition-preserving label."
            ),
        },
        "packets": records,
        "interpretation_warnings": [
            "This checks only synthetic size-five packets generated from stored examples.",
            "It does not enumerate arbitrary rich-class catalogues.",
            "It does not prove the adaptive radius-blocker bridge.",
            "No general proof and no counterexample are claimed.",
        ],
        "provenance": {
            "generator": "scripts/check_n9_radius_blocker_rich_quotient_sweep.py",
            "command": (
                "python scripts/check_n9_radius_blocker_rich_quotient_sweep.py "
                "--write --assert-expected"
            ),
            "sources": [
                "data/certificates/n9_radius_blocker_shape_sweep.json",
                "src/erdos97/adaptive_blockers.py",
                "src/erdos97/vertex_circle_quotient_replay.py",
            ],
        },
    }


def assert_expected_payload(payload: Mapping[str, object]) -> None:
    """Assert the stable full rich-class quotient sweep counts."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"unexpected status: {payload.get('status')!r}")
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("summary is missing")
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary[{key!r}] is {summary.get(key)!r}, expected {expected!r}"
            )

    packets = payload.get("packets")
    if not isinstance(packets, list):
        raise AssertionError("packet records are missing")
    packet_ids = [packet["packet_id"] for packet in packets]
    if len(packet_ids) != len(set(packet_ids)):
        raise AssertionError("packet IDs are not unique")


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    checked = json.loads(path.read_text(encoding="utf-8"))
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_summary(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("n=9 radius-blocker full rich-class quotient sweep")
    print(f"claim scope: {payload['claim_scope']}")
    print(f"packets: {summary['packet_count']}")
    print(f"quotient statuses: {summary['quotient_status_counts']}")
    print(f"strict edges: {summary['total_strict_edge_count']}")
    print(f"self-edge conflicts: {summary['total_self_edge_conflict_count']}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--write", action="store_true", help="write the artifact")
    parser.add_argument("--check", action="store_true", help="compare artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="print full JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload(args.source)
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
        print_summary(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
