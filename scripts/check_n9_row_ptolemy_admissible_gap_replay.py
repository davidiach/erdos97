#!/usr/bin/env python3
"""Generate or check replay data for n=9 row-Ptolemy admissible gaps."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
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

from erdos97.incidence_filters import (  # noqa: E402
    adjacent_two_overlap_violations,
    crossing_bisector_violations,
    row_ptolemy_product_cancellation_certificates,
)
from erdos97.path_display import display_path  # noqa: E402
from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    parse_selected_rows,
    replay_vertex_circle_quotient,
    result_to_json,
)
from scripts.check_n9_row_ptolemy_family_signatures import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_FAMILY_SIGNATURES_ARTIFACT,
    validate_payload as validate_family_signatures_payload,
)
from scripts.check_n9_row_ptolemy_order_admissible_census import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_CENSUS_ARTIFACT,
    EXPECTED_ZERO_COMPATIBLE_ASSIGNMENTS,
    EXPECTED_ZERO_COMPATIBLE_ORDER,
    load_artifact,
    validate_payload as validate_census_payload,
    write_json,
)

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_row_ptolemy_admissible_gap_replay.json"
)
SCHEMA = "erdos97.n9_row_ptolemy_admissible_gap_replay.v1"
STATUS = "EXPLORATORY_LEDGER_ONLY"
TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
CLAIM_SCOPE = (
    "Replay of the two zero-certificate n=9 row-Ptolemy admissible "
    "assignment-order records; not a proof of n=9, not a counterexample, "
    "not an all-order obstruction, not an orderless abstract-incidence "
    "obstruction, not a geometric realizability count, and not a global "
    "status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_row_ptolemy_admissible_gap_replay.py",
    "command": (
        "python scripts/check_n9_row_ptolemy_admissible_gap_replay.py "
        "--assert-expected --write"
    ),
}
SOURCE_ARTIFACTS = [
    {
        "path": "data/certificates/n9_row_ptolemy_order_admissible_census.json",
        "role": "zero-certificate admissible assignment-order source records",
        "schema": "erdos97.n9_row_ptolemy_order_admissible_census.v1",
        "status": "EXPLORATORY_LEDGER_ONLY",
        "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
    },
    {
        "path": "data/certificates/n9_row_ptolemy_family_signatures.json",
        "role": "row-Ptolemy family to local-core template crosswalk",
        "schema": "erdos97.n9_row_ptolemy_family_signatures.v2",
        "status": "EXPLORATORY_LEDGER_ONLY",
        "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
    },
]
EXPECTED_TOP_LEVEL_KEYS = {
    "assignment_indices",
    "claim_scope",
    "family_signature_source",
    "filter_replay_scope",
    "interpretation",
    "n",
    "normalized_order",
    "provenance",
    "record_count",
    "records",
    "row_ptolemy_certificate_count_histogram",
    "schema",
    "self_edge_conflict_count_histogram",
    "source_admissible_census",
    "source_artifacts",
    "status",
    "strict_edge_count_histogram",
    "trust",
    "vertex_circle_status_counts",
    "witness_size",
}
EXPECTED_RECORD_COUNT = 2
EXPECTED_FAMILY_ID = "F13"
EXPECTED_TEMPLATE_ID = "T04"
EXPECTED_TEMPLATE_KEY = "self_edge|rows=4|strict_edges=36|conflicts=2:1:1x2"
EXPECTED_VERTEX_STATUS_COUNTS = {"self_edge": 2}
EXPECTED_ROW_PTOLEMY_HISTOGRAM = {"0": 2}
EXPECTED_STRICT_EDGE_HISTOGRAM = {"81": 2}
EXPECTED_SELF_EDGE_CONFLICT_HISTOGRAM = {"27": 2}
EXPECTED_SOURCE_ADMISSIBLE_CENSUS = {
    "path": SOURCE_ARTIFACTS[0]["path"],
    "compatible_zero_certificate_order_count": 2,
    "compatible_order_count": 28,
    "compatible_vertex_circle_status_counts": {"self_edge": 28},
}
EXPECTED_FAMILY_SIGNATURE_SOURCE = {
    "path": SOURCE_ARTIFACTS[1]["path"],
    "family_id": EXPECTED_FAMILY_ID,
    "template_id": EXPECTED_TEMPLATE_ID,
    "template_status": "self_edge",
    "template_key": EXPECTED_TEMPLATE_KEY,
    "hit_assignment_count": 2,
    "hit_certificate_count": 36,
    "certificate_count_per_assignment": 18,
}


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a stable mismatch message when two values differ."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _family_signature_row(family_signatures: dict[str, Any]) -> dict[str, Any]:
    raw_rows = family_signatures.get("signature_rows")
    if not isinstance(raw_rows, Sequence) or isinstance(raw_rows, str):
        raise ValueError("family signatures must contain signature_rows")
    rows = [
        row
        for row in raw_rows
        if isinstance(row, dict) and row.get("family_id") == EXPECTED_FAMILY_ID
    ]
    if len(rows) != 1:
        raise ValueError("expected exactly one F13 family signature row")
    return rows[0]


def _zero_census_rows(census: dict[str, Any]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    raw_rows = census.get("assignment_rows")
    if not isinstance(raw_rows, Sequence) or isinstance(raw_rows, str):
        raise ValueError("admissible census must contain assignment_rows")

    zero_rows: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for raw_row in raw_rows:
        if not isinstance(raw_row, dict):
            continue
        raw_orders = raw_row.get("compatible_orders")
        if not isinstance(raw_orders, Sequence) or isinstance(raw_orders, str):
            continue
        for raw_order in raw_orders:
            if (
                isinstance(raw_order, dict)
                and raw_order.get("certificate_count") == 0
            ):
                zero_rows.append((raw_row, raw_order))
    zero_rows.sort(key=lambda item: int(item[0]["assignment_index"]))
    return zero_rows


def _record_payload(
    row: dict[str, Any],
    order_row: dict[str, Any],
    family_signature: dict[str, Any],
) -> dict[str, Any]:
    selected_rows = row["selected_rows"]
    order = order_row["order"]
    adjacent_violations = adjacent_two_overlap_violations(selected_rows, order)
    crossing_violations = crossing_bisector_violations(selected_rows, order)
    certificates = row_ptolemy_product_cancellation_certificates(selected_rows, order)
    replay = replay_vertex_circle_quotient(
        9,
        order,
        parse_selected_rows(selected_rows),
    )
    replay_json = result_to_json(replay)
    return {
        "assignment_index": int(row["assignment_index"]),
        "family_id": str(row["family_id"]),
        "family_orbit_size": int(row["family_orbit_size"]),
        "template_id": str(family_signature["template_id"]),
        "template_status": str(family_signature["template_status"]),
        "template_key": str(family_signature["template_key"]),
        "order": list(order),
        "is_natural_order": bool(order_row["is_natural_order"]),
        "selected_rows": selected_rows,
        "adjacent_two_overlap_violation_count": len(adjacent_violations),
        "crossing_bisector_violation_count": len(crossing_violations),
        "row_ptolemy_certificate_count": len(certificates),
        "source_vertex_circle_status": str(order_row["vertex_circle_status"]),
        "vertex_circle_replay": replay_json,
    }


def gap_replay_payload(
    census: dict[str, Any],
    family_signatures: dict[str, Any],
) -> dict[str, Any]:
    """Return the generated replay payload for the two zero-certificate records."""

    family_signature = _family_signature_row(family_signatures)
    zero_rows = _zero_census_rows(census)
    records = [
        _record_payload(row, order_row, family_signature)
        for row, order_row in zero_rows
    ]
    vertex_status_counts = Counter(
        str(record["vertex_circle_replay"]["status"]) for record in records
    )
    row_ptolemy_counts = Counter(
        int(record["row_ptolemy_certificate_count"]) for record in records
    )
    strict_edge_counts = Counter(
        int(record["vertex_circle_replay"]["strict_edge_count"]) for record in records
    )
    self_edge_counts = Counter(
        len(record["vertex_circle_replay"]["self_edge_conflicts"])
        for record in records
    )
    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": 9,
        "witness_size": 4,
        "source_artifacts": SOURCE_ARTIFACTS,
        "provenance": PROVENANCE,
        "filter_replay_scope": (
            "Replay only the zero-certificate admissible assignment-order "
            "records from the row-Ptolemy admissible-order census."
        ),
        "interpretation": [
            (
                "Zero row-Ptolemy certificates are diagnostic gaps for this "
                "filter, not realizability evidence."
            ),
            (
                "Both records still replay as vertex-circle self-edge "
                "obstructions under the supplied normalized order."
            ),
            "The F13 -> T04 label is crosswalk metadata, not a theorem name.",
            "No proof of the n=9 case is claimed.",
            "No counterexample or global status update is claimed.",
        ],
        "source_admissible_census": {
            "path": SOURCE_ARTIFACTS[0]["path"],
            "compatible_zero_certificate_order_count": int(
                census["compatible_zero_certificate_order_count"]
            ),
            "compatible_order_count": int(census["compatible_order_count"]),
            "compatible_vertex_circle_status_counts": (
                census["compatible_vertex_circle_status_counts"]
            ),
        },
        "family_signature_source": {
            "path": SOURCE_ARTIFACTS[1]["path"],
            "family_id": EXPECTED_FAMILY_ID,
            "template_id": str(family_signature["template_id"]),
            "template_status": str(family_signature["template_status"]),
            "template_key": str(family_signature["template_key"]),
            "hit_assignment_count": int(family_signature["hit_assignment_count"]),
            "hit_certificate_count": int(family_signature["hit_certificate_count"]),
            "certificate_count_per_assignment": int(
                family_signature["certificate_count_per_assignment"]
            ),
        },
        "record_count": len(records),
        "assignment_indices": [
            int(record["assignment_index"]) for record in records
        ],
        "normalized_order": list(EXPECTED_ZERO_COMPATIBLE_ORDER),
        "row_ptolemy_certificate_count_histogram": _json_counter(row_ptolemy_counts),
        "vertex_circle_status_counts": dict(sorted(vertex_status_counts.items())),
        "strict_edge_count_histogram": _json_counter(strict_edge_counts),
        "self_edge_conflict_count_histogram": _json_counter(self_edge_counts),
        "records": records,
    }
    assert_expected_counts(payload)
    return payload


def assert_expected_counts(payload: dict[str, Any]) -> None:
    """Raise AssertionError if the replay payload no longer has expected counts."""

    assert payload["record_count"] == EXPECTED_RECORD_COUNT
    assert payload["assignment_indices"] == EXPECTED_ZERO_COMPATIBLE_ASSIGNMENTS
    assert payload["normalized_order"] == EXPECTED_ZERO_COMPATIBLE_ORDER
    assert (
        payload["row_ptolemy_certificate_count_histogram"]
        == EXPECTED_ROW_PTOLEMY_HISTOGRAM
    )
    assert payload["vertex_circle_status_counts"] == EXPECTED_VERTEX_STATUS_COUNTS
    assert payload["strict_edge_count_histogram"] == EXPECTED_STRICT_EDGE_HISTOGRAM
    assert (
        payload["self_edge_conflict_count_histogram"]
        == EXPECTED_SELF_EDGE_CONFLICT_HISTOGRAM
    )
    assert payload["family_signature_source"]["template_id"] == EXPECTED_TEMPLATE_ID
    assert all(
        record["vertex_circle_replay"]["status"] == "self_edge"
        for record in payload["records"]
    )


def _validate_record(errors: list[str], record: Any, index: int) -> None:
    if not isinstance(record, dict):
        errors.append(f"records[{index}] must be an object")
        return
    label = f"records[{index}]"
    assignment_index = record.get("assignment_index")
    if assignment_index not in EXPECTED_ZERO_COMPATIBLE_ASSIGNMENTS:
        errors.append(f"{label}.assignment_index is not an expected gap assignment")
    expect_equal(errors, f"{label}.family_id", record.get("family_id"), EXPECTED_FAMILY_ID)
    expect_equal(
        errors,
        f"{label}.template_id",
        record.get("template_id"),
        EXPECTED_TEMPLATE_ID,
    )
    expect_equal(errors, f"{label}.template_status", record.get("template_status"), "self_edge")
    expect_equal(errors, f"{label}.template_key", record.get("template_key"), EXPECTED_TEMPLATE_KEY)
    expect_equal(errors, f"{label}.family_orbit_size", record.get("family_orbit_size"), 2)
    expect_equal(errors, f"{label}.order", record.get("order"), EXPECTED_ZERO_COMPATIBLE_ORDER)
    expect_equal(errors, f"{label}.is_natural_order", record.get("is_natural_order"), False)

    selected_rows = record.get("selected_rows")
    order = record.get("order")
    if (
        not isinstance(selected_rows, Sequence)
        or isinstance(selected_rows, str)
        or not isinstance(order, Sequence)
        or isinstance(order, str)
    ):
        errors.append(f"{label} must contain selected_rows and order sequences")
        return
    adjacent_violations = adjacent_two_overlap_violations(selected_rows, order)
    crossing_violations = crossing_bisector_violations(selected_rows, order)
    certificates = row_ptolemy_product_cancellation_certificates(selected_rows, order)
    replay_json = result_to_json(
        replay_vertex_circle_quotient(9, order, parse_selected_rows(selected_rows))
    )
    expect_equal(
        errors,
        f"{label}.adjacent_two_overlap_violation_count",
        record.get("adjacent_two_overlap_violation_count"),
        len(adjacent_violations),
    )
    expect_equal(
        errors,
        f"{label}.crossing_bisector_violation_count",
        record.get("crossing_bisector_violation_count"),
        len(crossing_violations),
    )
    expect_equal(
        errors,
        f"{label}.row_ptolemy_certificate_count",
        record.get("row_ptolemy_certificate_count"),
        len(certificates),
    )
    expect_equal(
        errors,
        f"{label}.source_vertex_circle_status",
        record.get("source_vertex_circle_status"),
        replay_json["status"],
    )
    expect_equal(
        errors,
        f"{label}.vertex_circle_replay",
        record.get("vertex_circle_replay"),
        replay_json,
    )
    if adjacent_violations:
        errors.append(f"{label} no longer passes adjacent two-overlap filter")
    if crossing_violations:
        errors.append(f"{label} no longer passes crossing-bisector filter")
    if certificates:
        errors.append(f"{label} no longer has zero row-Ptolemy certificates")


def validate_payload(
    payload: Any,
    *,
    census: Any | None = None,
    family_signatures: Any | None = None,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a loaded gap replay artifact."""

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
        "n": 9,
        "witness_size": 4,
        "source_artifacts": SOURCE_ARTIFACTS,
        "provenance": PROVENANCE,
        "source_admissible_census": EXPECTED_SOURCE_ADMISSIBLE_CENSUS,
        "family_signature_source": EXPECTED_FAMILY_SIGNATURE_SOURCE,
        "record_count": EXPECTED_RECORD_COUNT,
        "assignment_indices": EXPECTED_ZERO_COMPATIBLE_ASSIGNMENTS,
        "normalized_order": EXPECTED_ZERO_COMPATIBLE_ORDER,
        "row_ptolemy_certificate_count_histogram": EXPECTED_ROW_PTOLEMY_HISTOGRAM,
        "vertex_circle_status_counts": EXPECTED_VERTEX_STATUS_COUNTS,
        "strict_edge_count_histogram": EXPECTED_STRICT_EDGE_HISTOGRAM,
        "self_edge_conflict_count_histogram": EXPECTED_SELF_EDGE_CONFLICT_HISTOGRAM,
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
            "Zero row-Ptolemy certificates are diagnostic gaps for this filter, not realizability evidence.",
            "Both records still replay as vertex-circle self-edge obstructions under the supplied normalized order.",
            "No proof of the n=9 case is claimed.",
            "No counterexample or global status update is claimed.",
        )
        for phrase in required:
            if phrase not in interpretation:
                errors.append(f"interpretation must include {phrase!r}")

    records = payload.get("records")
    if not isinstance(records, list):
        errors.append("records must be a list")
    else:
        actual_assignments = [
            record.get("assignment_index")
            for record in records
            if isinstance(record, dict)
        ]
        expect_equal(
            errors,
            "record assignment indices",
            actual_assignments,
            EXPECTED_ZERO_COMPATIBLE_ASSIGNMENTS,
        )
        expect_equal(errors, "record count", len(records), EXPECTED_RECORD_COUNT)
        for index, record in enumerate(records):
            _validate_record(errors, record, index)

    try:
        assert_expected_counts(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected counts failed: {exc}")

    if recompute:
        if census is None:
            try:
                census = load_artifact(DEFAULT_CENSUS_ARTIFACT)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"failed to load admissible census artifact: {exc}")
                census = None
        if family_signatures is None:
            try:
                family_signatures = load_artifact(DEFAULT_FAMILY_SIGNATURES_ARTIFACT)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"failed to load family-signature artifact: {exc}")
                family_signatures = None
        if isinstance(census, dict) and isinstance(family_signatures, dict):
            try:
                expected_payload = gap_replay_payload(census, family_signatures)
            except (AssertionError, TypeError, ValueError) as exc:
                errors.append(f"recomputed gap replay failed: {exc}")
            else:
                expect_equal(errors, "gap replay payload", payload, expected_payload)
        else:
            errors.append("source artifacts must be JSON objects")
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
        "normalized_order": object_payload.get("normalized_order"),
        "row_ptolemy_certificate_count_histogram": object_payload.get(
            "row_ptolemy_certificate_count_histogram"
        ),
        "vertex_circle_status_counts": object_payload.get(
            "vertex_circle_status_counts"
        ),
        "strict_edge_count_histogram": object_payload.get(
            "strict_edge_count_histogram"
        ),
        "self_edge_conflict_count_histogram": object_payload.get(
            "self_edge_conflict_count_histogram"
        ),
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--census", type=Path, default=DEFAULT_CENSUS_ARTIFACT)
    parser.add_argument(
        "--family-signatures",
        type=Path,
        default=DEFAULT_FAMILY_SIGNATURES_ARTIFACT,
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write generated replay")
    parser.add_argument("--check", action="store_true", help="validate existing replay")
    parser.add_argument("--json", action="store_true", help="print stable JSON summary")
    parser.add_argument("--assert-expected", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact
    census_path = args.census if args.census.is_absolute() else ROOT / args.census
    family_path = (
        args.family_signatures
        if args.family_signatures.is_absolute()
        else ROOT / args.family_signatures
    )
    out = args.out if args.out.is_absolute() else ROOT / args.out

    source_errors: list[str] = []
    try:
        census = load_artifact(census_path)
        source_errors.extend(
            f"admissible census invalid: {error}"
            for error in validate_census_payload(census, recompute=False)
        )
    except (OSError, json.JSONDecodeError) as exc:
        census = {}
        source_errors.append(f"failed to load admissible census: {exc}")
    try:
        family_signatures = load_artifact(family_path)
        source_errors.extend(
            f"family signatures invalid: {error}"
            for error in validate_family_signatures_payload(
                family_signatures,
                recompute=False,
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        family_signatures = {}
        source_errors.append(f"failed to load family signatures: {exc}")

    if args.write:
        if source_errors:
            for error in source_errors:
                print(error, file=sys.stderr)
            return 1
        payload = gap_replay_payload(census, family_signatures)
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
            census=census,
            family_signatures=family_signatures,
            recompute=args.check or args.assert_expected,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]
    errors.extend(source_errors)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact, ROOT)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 row-Ptolemy admissible gap replay")
        print(f"artifact: {summary['artifact']}")
        print(f"records: {summary['record_count']}")
        print(f"assignments: {summary['assignment_indices']}")
        print(f"order: {summary['normalized_order']}")
        print(
            "row-Ptolemy certificate histogram: "
            f"{summary['row_ptolemy_certificate_count_histogram']}"
        )
        print(f"vertex-circle statuses: {summary['vertex_circle_status_counts']}")
        if args.check or args.assert_expected:
            print("OK: row-Ptolemy admissible gap replay checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
