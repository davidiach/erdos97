#!/usr/bin/env python3
"""Generate or check compact self-edge cores for n=9 row-Ptolemy gaps."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict, deque
from itertools import combinations
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from erdos97.path_display import display_path  # noqa: E402
from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    pair,
    parse_selected_rows,
    replay_vertex_circle_quotient,
    result_to_json,
)
from scripts.check_n9_row_ptolemy_admissible_gap_replay import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_GAP_REPLAY_ARTIFACT,
    load_artifact,
    validate_payload as validate_gap_replay_payload,
    write_json,
)

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_row_ptolemy_gap_self_edge_cores.json"
)
SCHEMA = "erdos97.n9_row_ptolemy_gap_self_edge_cores.v1"
STATUS = "EXPLORATORY_LEDGER_ONLY"
TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
CLAIM_SCOPE = (
    "Compact self-edge core certificates for the two zero-certificate n=9 "
    "row-Ptolemy admissible assignment-order records; not a proof of n=9, "
    "not a counterexample, not an all-order obstruction, not an orderless "
    "abstract-incidence obstruction, not a geometric realizability count, and "
    "not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_row_ptolemy_gap_self_edge_cores.py",
    "command": (
        "python scripts/check_n9_row_ptolemy_gap_self_edge_cores.py "
        "--assert-expected --write"
    ),
}
SOURCE_ARTIFACT = {
    "path": "data/certificates/n9_row_ptolemy_admissible_gap_replay.json",
    "schema": "erdos97.n9_row_ptolemy_admissible_gap_replay.v1",
    "status": "EXPLORATORY_LEDGER_ONLY",
    "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
}
EXPECTED_TOP_LEVEL_KEYS = {
    "assignment_indices",
    "claim_scope",
    "core_row_index_sets",
    "core_self_edge_conflict_count_histogram",
    "core_size_counts",
    "core_strict_edge_count_histogram",
    "equality_path_length_histogram",
    "interpretation",
    "minimal_self_edge_core_count_histogram",
    "n",
    "normalized_order",
    "provenance",
    "record_count",
    "records",
    "schema",
    "source_artifact",
    "status",
    "trust",
    "vertex_circle_status_counts",
    "witness_size",
}
EXPECTED_ASSIGNMENTS = [22, 173]
EXPECTED_ORDER = [0, 2, 4, 6, 8, 1, 3, 5, 7]
EXPECTED_CORE_ROW_INDICES = [0, 2, 4]
EXPECTED_RECORD_COUNT = 2
EXPECTED_CORE_SIZE_COUNTS = {"3": 2}
EXPECTED_VERTEX_STATUS_COUNTS = {"self_edge": 2}
EXPECTED_CORE_STRICT_EDGE_HISTOGRAM = {"27": 2}
EXPECTED_CORE_CONFLICT_HISTOGRAM = {"1": 2}
EXPECTED_EQUALITY_PATH_LENGTH_HISTOGRAM = {"3": 2}
EXPECTED_MINIMAL_CORE_COUNT_HISTOGRAM = {"9": 2}

Pair = tuple[int, int]


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a mismatch error when values differ."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _explicit_rows(raw_rows: Sequence[Any]) -> list[dict[str, Any]]:
    rows = []
    for center, witnesses in enumerate(raw_rows):
        if not isinstance(witnesses, Sequence) or isinstance(witnesses, str):
            raise ValueError(f"selected row {center} must be a sequence")
        rows.append(
            {
                "row": center,
                "witnesses": [int(witness) for witness in witnesses],
            }
        )
    return rows


def _rows_at_indices(rows: Sequence[dict[str, Any]], indices: Sequence[int]) -> list[dict[str, Any]]:
    return [rows[index] for index in indices]


def _replay_json(n: int, order: Sequence[int], rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    return result_to_json(replay_vertex_circle_quotient(n, order, parse_selected_rows(rows)))


def _self_edge_core_indices(
    n: int,
    order: Sequence[int],
    rows: Sequence[dict[str, Any]],
) -> list[tuple[int, ...]]:
    """Return every smallest row-index subset that replays as self_edge."""

    for size in range(1, len(rows) + 1):
        found = []
        for indices in combinations(range(len(rows)), size):
            replay = replay_vertex_circle_quotient(
                n,
                order,
                parse_selected_rows(_rows_at_indices(rows, indices)),
            )
            if replay.status == "self_edge":
                found.append(indices)
        if found:
            return found
    return []


def _proper_subcore_status_counts(
    n: int,
    order: Sequence[int],
    rows: Sequence[dict[str, Any]],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for size in range(1, len(rows)):
        for indices in combinations(range(len(rows)), size):
            replay = replay_vertex_circle_quotient(
                n,
                order,
                parse_selected_rows(_rows_at_indices(rows, indices)),
            )
            counts[replay.status] += 1
    return dict(sorted(counts.items()))


def _selected_equality_graph(
    rows: Sequence[dict[str, Any]],
) -> dict[Pair, list[tuple[Pair, dict[str, Any]]]]:
    graph: dict[Pair, list[tuple[Pair, dict[str, Any]]]] = defaultdict(list)
    for raw_row in rows:
        center = int(raw_row["row"])
        witnesses = [int(witness) for witness in raw_row["witnesses"]]
        row_pairs = [pair(center, witness) for witness in witnesses]
        reason = {
            "row": center,
            "witnesses": witnesses,
            "reason": "selected distances from this center to its witnesses are equal",
        }
        for left, right in combinations(row_pairs, 2):
            graph[left].append((right, reason))
            graph[right].append((left, reason))
    for neighbors in graph.values():
        neighbors.sort(key=lambda item: (item[0], item[1]["row"]))
    return graph


def _selected_equality_path(
    rows: Sequence[dict[str, Any]],
    start_pair: Sequence[int],
    end_pair: Sequence[int],
) -> list[dict[str, Any]]:
    """Return a stable selected-distance equality path between two pairs."""

    start = pair(int(start_pair[0]), int(start_pair[1]))
    end = pair(int(end_pair[0]), int(end_pair[1]))
    graph = _selected_equality_graph(rows)
    queue: deque[Pair] = deque([start])
    parents: dict[Pair, tuple[Pair, dict[str, Any]] | None] = {start: None}
    while queue:
        node = queue.popleft()
        if node == end:
            break
        for neighbor, reason in graph.get(node, []):
            if neighbor not in parents:
                parents[neighbor] = (node, reason)
                queue.append(neighbor)
    if end not in parents:
        raise ValueError(f"no equality path between {start!r} and {end!r}")

    path: list[dict[str, Any]] = []
    node = end
    while node != start:
        parent = parents[node]
        if parent is None:
            raise ValueError("malformed equality path parent map")
        previous, reason = parent
        path.append(
            {
                "from_pair": list(previous),
                "to_pair": list(node),
                "row": reason["row"],
                "row_witnesses": reason["witnesses"],
                "reason": reason["reason"],
            }
        )
        node = previous
    path.reverse()
    return path


def _record_payload(record: dict[str, Any]) -> dict[str, Any]:
    assignment_index = int(record["assignment_index"])
    order = [int(label) for label in record["order"]]
    rows = _explicit_rows(record["selected_rows"])
    minimal_cores = _self_edge_core_indices(9, order, rows)
    if not minimal_cores:
        raise ValueError(f"assignment {assignment_index} has no self-edge core")
    core_indices = list(minimal_cores[0])
    core_rows = _rows_at_indices(rows, core_indices)
    core_replay = _replay_json(9, order, core_rows)
    conflicts = core_replay["self_edge_conflicts"]
    if len(conflicts) != 1:
        raise ValueError(f"assignment {assignment_index} core must have one conflict")
    conflict = conflicts[0]
    equality_path = _selected_equality_path(
        core_rows,
        conflict["outer_pair"],
        conflict["inner_pair"],
    )
    proper_counts = _proper_subcore_status_counts(9, order, core_rows)
    return {
        "assignment_index": assignment_index,
        "family_id": str(record["family_id"]),
        "template_id": str(record["template_id"]),
        "source_record": {
            "selected_row_count": int(record["vertex_circle_replay"]["selected_row_count"]),
            "strict_edge_count": int(record["vertex_circle_replay"]["strict_edge_count"]),
            "self_edge_conflict_count": len(
                record["vertex_circle_replay"]["self_edge_conflicts"]
            ),
        },
        "order": order,
        "core_row_indices": core_indices,
        "core_rows": core_rows,
        "core_replay": core_replay,
        "self_edge_conflict": conflict,
        "selected_distance_equality_path": equality_path,
        "minimality": {
            "minimal_self_edge_core_size": len(core_indices),
            "minimal_self_edge_core_count": len(minimal_cores),
            "lexicographic_min_core_row_indices": core_indices,
            "proper_subcore_status_counts": proper_counts,
            "proper_self_edge_subcore_count": int(proper_counts.get("self_edge", 0)),
        },
    }


def _source_records_by_assignment(source: Any) -> dict[int, dict[str, Any]]:
    if not isinstance(source, dict):
        return {}
    raw_records = source.get("records")
    if not isinstance(raw_records, Sequence) or isinstance(raw_records, str):
        return {}
    records = {}
    for record in raw_records:
        if isinstance(record, dict) and isinstance(record.get("assignment_index"), int):
            records[int(record["assignment_index"])] = record
    return records


def _source_record_summary(source_record: dict[str, Any]) -> dict[str, int]:
    replay = source_record["vertex_circle_replay"]
    return {
        "selected_row_count": int(replay["selected_row_count"]),
        "strict_edge_count": int(replay["strict_edge_count"]),
        "self_edge_conflict_count": len(replay["self_edge_conflicts"]),
    }


def self_edge_core_payload(gap_replay: dict[str, Any]) -> dict[str, Any]:
    """Return the generated compact self-edge core artifact."""

    raw_records = gap_replay.get("records")
    if not isinstance(raw_records, Sequence) or isinstance(raw_records, str):
        raise ValueError("gap replay artifact must contain records")
    records = [
        _record_payload(record)
        for record in raw_records
        if isinstance(record, dict)
    ]
    records.sort(key=lambda record: int(record["assignment_index"]))

    core_sizes = Counter(len(record["core_rows"]) for record in records)
    statuses = Counter(record["core_replay"]["status"] for record in records)
    strict_edges = Counter(
        int(record["core_replay"]["strict_edge_count"]) for record in records
    )
    conflict_counts = Counter(
        len(record["core_replay"]["self_edge_conflicts"]) for record in records
    )
    path_lengths = Counter(
        len(record["selected_distance_equality_path"]) for record in records
    )
    minimal_counts = Counter(
        int(record["minimality"]["minimal_self_edge_core_count"])
        for record in records
    )
    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": 9,
        "witness_size": 4,
        "source_artifact": SOURCE_ARTIFACT,
        "provenance": PROVENANCE,
        "interpretation": [
            (
                "Each core is a compact replay certificate for one recorded "
                "self-edge gap record, not a standalone theorem."
            ),
            (
                "The selected-distance equality path explains why the strict "
                "outer chord and inner chord are identified in the quotient."
            ),
            (
                "The listed core is the lexicographically first minimal "
                "self-edge row subset for that recorded assignment-order pair."
            ),
            "No proof of the n=9 case is claimed.",
            "No counterexample or global status update is claimed.",
        ],
        "record_count": len(records),
        "assignment_indices": [
            int(record["assignment_index"]) for record in records
        ],
        "normalized_order": EXPECTED_ORDER,
        "core_row_index_sets": [
            record["core_row_indices"] for record in records
        ],
        "core_size_counts": _json_counter(core_sizes),
        "vertex_circle_status_counts": dict(sorted(statuses.items())),
        "core_strict_edge_count_histogram": _json_counter(strict_edges),
        "core_self_edge_conflict_count_histogram": _json_counter(conflict_counts),
        "equality_path_length_histogram": _json_counter(path_lengths),
        "minimal_self_edge_core_count_histogram": _json_counter(minimal_counts),
        "records": records,
    }
    assert_expected_counts(payload)
    return payload


def assert_expected_counts(payload: dict[str, Any]) -> None:
    """Raise AssertionError if expected compact-core counts change."""

    assert payload["record_count"] == EXPECTED_RECORD_COUNT
    assert payload["assignment_indices"] == EXPECTED_ASSIGNMENTS
    assert payload["normalized_order"] == EXPECTED_ORDER
    assert payload["core_row_index_sets"] == [EXPECTED_CORE_ROW_INDICES] * 2
    assert payload["core_size_counts"] == EXPECTED_CORE_SIZE_COUNTS
    assert payload["vertex_circle_status_counts"] == EXPECTED_VERTEX_STATUS_COUNTS
    assert payload["core_strict_edge_count_histogram"] == EXPECTED_CORE_STRICT_EDGE_HISTOGRAM
    assert payload["core_self_edge_conflict_count_histogram"] == EXPECTED_CORE_CONFLICT_HISTOGRAM
    assert (
        payload["equality_path_length_histogram"]
        == EXPECTED_EQUALITY_PATH_LENGTH_HISTOGRAM
    )
    assert (
        payload["minimal_self_edge_core_count_histogram"]
        == EXPECTED_MINIMAL_CORE_COUNT_HISTOGRAM
    )
    assert all(
        record["minimality"]["proper_self_edge_subcore_count"] == 0
        for record in payload["records"]
    )


def _validate_equality_path(
    errors: list[str],
    record: dict[str, Any],
    label: str,
) -> None:
    conflict = record.get("self_edge_conflict")
    path = record.get("selected_distance_equality_path")
    core_rows = record.get("core_rows")
    if not isinstance(conflict, dict) or not isinstance(path, list):
        errors.append(f"{label} must contain conflict and equality path")
        return
    if not isinstance(core_rows, Sequence) or isinstance(core_rows, str):
        errors.append(f"{label}.core_rows must be a sequence")
        return
    try:
        expected_path = _selected_equality_path(
            core_rows,
            conflict["outer_pair"],
            conflict["inner_pair"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"{label} equality path failed: {exc}")
        return
    expect_equal(
        errors,
        f"{label}.selected_distance_equality_path",
        path,
        expected_path,
    )


def _validate_record(
    errors: list[str],
    record: Any,
    index: int,
    source_record: dict[str, Any] | None,
) -> None:
    if not isinstance(record, dict):
        errors.append(f"records[{index}] must be an object")
        return
    label = f"records[{index}]"
    expect_equal(errors, f"{label}.family_id", record.get("family_id"), "F13")
    expect_equal(errors, f"{label}.template_id", record.get("template_id"), "T04")
    expect_equal(errors, f"{label}.order", record.get("order"), EXPECTED_ORDER)
    expect_equal(
        errors,
        f"{label}.core_row_indices",
        record.get("core_row_indices"),
        EXPECTED_CORE_ROW_INDICES,
    )
    core_rows = record.get("core_rows")
    if not isinstance(core_rows, Sequence) or isinstance(core_rows, str):
        errors.append(f"{label}.core_rows must be a sequence")
        return
    if source_record is not None:
        source_rows = _explicit_rows(source_record["selected_rows"])
        expected_core_rows = _rows_at_indices(source_rows, record["core_row_indices"])
        expect_equal(errors, f"{label}.core_rows", core_rows, expected_core_rows)
        expect_equal(
            errors,
            f"{label}.source_record",
            record.get("source_record"),
            _source_record_summary(source_record),
        )
    try:
        replay = _replay_json(9, EXPECTED_ORDER, core_rows)
    except (TypeError, ValueError) as exc:
        errors.append(f"{label} core replay failed: {exc}")
        return
    expect_equal(errors, f"{label}.core_replay", record.get("core_replay"), replay)
    conflicts = replay["self_edge_conflicts"]
    if len(conflicts) != 1:
        errors.append(f"{label} core must replay exactly one self-edge conflict")
    else:
        expect_equal(errors, f"{label}.self_edge_conflict", record.get("self_edge_conflict"), conflicts[0])
    _validate_equality_path(errors, record, label)
    minimality = record.get("minimality")
    if not isinstance(minimality, dict):
        errors.append(f"{label}.minimality must be an object")
        return
    expect_equal(
        errors,
        f"{label}.minimality.minimal_self_edge_core_size",
        minimality.get("minimal_self_edge_core_size"),
        len(core_rows),
    )
    expect_equal(
        errors,
        f"{label}.minimality.lexicographic_min_core_row_indices",
        minimality.get("lexicographic_min_core_row_indices"),
        record.get("core_row_indices"),
    )
    proper_counts = _proper_subcore_status_counts(9, EXPECTED_ORDER, core_rows)
    expect_equal(
        errors,
        f"{label}.minimality.proper_subcore_status_counts",
        minimality.get("proper_subcore_status_counts"),
        proper_counts,
    )
    expect_equal(
        errors,
        f"{label}.minimality.proper_self_edge_subcore_count",
        minimality.get("proper_self_edge_subcore_count"),
        int(proper_counts.get("self_edge", 0)),
    )
    if source_record is not None:
        source_rows = _explicit_rows(source_record["selected_rows"])
        minimal_cores = _self_edge_core_indices(9, EXPECTED_ORDER, source_rows)
        expect_equal(
            errors,
            f"{label}.minimality.minimal_self_edge_core_count",
            minimality.get("minimal_self_edge_core_count"),
            len(minimal_cores),
        )
        expect_equal(
            errors,
            f"{label}.minimality.minimal_self_edge_core_size",
            minimality.get("minimal_self_edge_core_size"),
            len(minimal_cores[0]) if minimal_cores else None,
        )
        expect_equal(
            errors,
            f"{label}.minimality.lexicographic_min_core_row_indices",
            minimality.get("lexicographic_min_core_row_indices"),
            list(minimal_cores[0]) if minimal_cores else None,
        )


def validate_payload(
    payload: Any,
    *,
    source: Any | None = None,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a loaded compact-core artifact."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    errors: list[str] = []
    if set(payload) != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(payload)!r}"
        )
    expected_meta = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifact": SOURCE_ARTIFACT,
        "provenance": PROVENANCE,
        "n": 9,
        "witness_size": 4,
        "record_count": EXPECTED_RECORD_COUNT,
        "assignment_indices": EXPECTED_ASSIGNMENTS,
        "normalized_order": EXPECTED_ORDER,
        "core_row_index_sets": [EXPECTED_CORE_ROW_INDICES] * 2,
        "core_size_counts": EXPECTED_CORE_SIZE_COUNTS,
        "vertex_circle_status_counts": EXPECTED_VERTEX_STATUS_COUNTS,
        "core_strict_edge_count_histogram": EXPECTED_CORE_STRICT_EDGE_HISTOGRAM,
        "core_self_edge_conflict_count_histogram": EXPECTED_CORE_CONFLICT_HISTOGRAM,
        "equality_path_length_histogram": EXPECTED_EQUALITY_PATH_LENGTH_HISTOGRAM,
        "minimal_self_edge_core_count_histogram": EXPECTED_MINIMAL_CORE_COUNT_HISTOGRAM,
    }
    for key, expected in expected_meta.items():
        expect_equal(errors, key, payload.get(key), expected)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list) or not all(
        isinstance(item, str) for item in interpretation
    ):
        errors.append("interpretation must be a list of strings")
    else:
        required = (
            "Each core is a compact replay certificate for one recorded self-edge gap record, not a standalone theorem.",
            "No proof of the n=9 case is claimed.",
            "No counterexample or global status update is claimed.",
        )
        for phrase in required:
            if phrase not in interpretation:
                errors.append(f"interpretation must include {phrase!r}")

    if source is None:
        try:
            source = load_artifact(DEFAULT_GAP_REPLAY_ARTIFACT)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"failed to load gap replay artifact: {exc}")
            source = None
    source_records = _source_records_by_assignment(source)

    records = payload.get("records")
    if not isinstance(records, list):
        errors.append("records must be a list")
    else:
        expect_equal(errors, "record count", len(records), EXPECTED_RECORD_COUNT)
        expect_equal(
            errors,
            "record assignment indices",
            [record.get("assignment_index") for record in records if isinstance(record, dict)],
            EXPECTED_ASSIGNMENTS,
        )
        for index, record in enumerate(records):
            assignment_index = (
                record.get("assignment_index") if isinstance(record, dict) else None
            )
            source_record = (
                source_records.get(int(assignment_index))
                if isinstance(assignment_index, int)
                else None
            )
            if source_records and source_record is None:
                errors.append(f"records[{index}] assignment missing from source artifact")
            _validate_record(errors, record, index, source_record)

    try:
        assert_expected_counts(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected counts failed: {exc}")

    if recompute:
        if isinstance(source, dict):
            try:
                expected_payload = self_edge_core_payload(source)
            except (AssertionError, TypeError, ValueError) as exc:
                errors.append(f"recomputed self-edge cores failed: {exc}")
            else:
                expect_equal(errors, "self-edge core payload", payload, expected_payload)
        else:
            errors.append("source gap replay artifact must be an object")
    return errors


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    return {
        "ok": not errors,
        "artifact": display_path(path, ROOT),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "record_count": object_payload.get("record_count"),
        "assignment_indices": object_payload.get("assignment_indices"),
        "core_row_index_sets": object_payload.get("core_row_index_sets"),
        "core_size_counts": object_payload.get("core_size_counts"),
        "vertex_circle_status_counts": object_payload.get(
            "vertex_circle_status_counts"
        ),
        "core_strict_edge_count_histogram": object_payload.get(
            "core_strict_edge_count_histogram"
        ),
        "core_self_edge_conflict_count_histogram": object_payload.get(
            "core_self_edge_conflict_count_histogram"
        ),
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--source", type=Path, default=DEFAULT_GAP_REPLAY_ARTIFACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write generated cores")
    parser.add_argument("--check", action="store_true", help="validate existing cores")
    parser.add_argument("--json", action="store_true", help="print stable JSON summary")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args(raw_argv)
    args.artifact_explicit = any(
        item == "--artifact" or item.startswith("--artifact=") for item in raw_argv
    )
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    out = args.out if args.out.is_absolute() else ROOT / args.out
    if args.write and args.check:
        if args.artifact_explicit and artifact != out:
            print(
                "combined --write --check requires --artifact to match --out",
                file=sys.stderr,
            )
            return 2
        artifact = out

    try:
        source = load_artifact(source_path)
    except (OSError, json.JSONDecodeError) as exc:
        source = {}
        source_errors = [str(exc)]
    else:
        source_errors = validate_gap_replay_payload(source, recompute=False)

    if args.write:
        if source_errors:
            for error in source_errors:
                print(f"source artifact invalid: {error}", file=sys.stderr)
            return 1
        payload = self_edge_core_payload(source)
        if args.assert_expected:
            assert_expected_counts(payload)
        write_json(payload, out)
        if not args.check:
            if args.json:
                print(json.dumps(summary_payload(out, payload, []), indent=2, sort_keys=True))
            else:
                print(f"wrote {display_path(out, ROOT)}")
            return 0

    try:
        payload = load_artifact(artifact)
        errors = validate_payload(
            payload,
            source=source,
            recompute=args.check or args.assert_expected,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]
    errors.extend(f"source artifact invalid: {error}" for error in source_errors)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact, ROOT)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 row-Ptolemy gap self-edge cores")
        print(f"artifact: {summary['artifact']}")
        print(f"records: {summary['record_count']}")
        print(f"assignments: {summary['assignment_indices']}")
        print(f"core row indices: {summary['core_row_index_sets']}")
        print(f"core sizes: {summary['core_size_counts']}")
        print(f"vertex-circle statuses: {summary['vertex_circle_status_counts']}")
        if args.check or args.assert_expected:
            print("OK: row-Ptolemy gap self-edge core checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
