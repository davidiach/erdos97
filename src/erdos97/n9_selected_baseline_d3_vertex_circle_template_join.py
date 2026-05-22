"""Join selected-baseline D=3 escape landings to vertex-circle templates.

This module is finite bookkeeping. It labels the 1,746 selected-baseline
budget-3 escaping assignment/slot-choice landings and joins each landing by
``assignment_id`` to the existing n=9 vertex-circle family/template
diagnostics. It does not test geometric realizability, prove the n=9 case, or
claim a counterexample.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Any, Sequence

from erdos97.n9_base_apex import canonical_deficit_placement, turn_cover_diagnostic
from erdos97.n9_d3_escape_slice import json_counter
from erdos97.n9_selected_baseline_d3_escape_class_crosswalk import (
    BASE_APEX_SLACK,
    CAPACITY_DEFICIT_BUDGET,
    CONTRADICTION_THRESHOLD,
    EXPECTED_COUNTS as CROSSWALK_EXPECTED_COUNTS,
    EXPECTED_SCHEMA as CROSSWALK_SCHEMA,
    EXPECTED_TRUST as CROSSWALK_TRUST,
    _assignment_class_id,
    _chosen_relevant_placement,
    _escape_rows,
    _selected_baseline_rows,
)
from erdos97.n9_selected_baseline_escape_budget import (
    deficit_summary,
    placement_key_payload,
    selected_baseline_empty_slots,
)
from erdos97.n9_vertex_circle_frontier_motif_classification import (
    SCHEMA as CLASSIFICATION_SCHEMA,
)
from erdos97.n9_vertex_circle_obstruction_shapes import (
    EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS,
    _rows_from_assignment,
    pre_vertex_circle_assignments,
)
from erdos97.n9_vertex_circle_template_lemma_catalog import (
    SCHEMA as TEMPLATE_CATALOG_SCHEMA,
)

N = 9
WITNESS_SIZE = 4

SCHEMA = "erdos97.n9_selected_baseline_d3_vertex_circle_template_join.v1"
STATUS = "EXPLORATORY_LEDGER_ONLY"
TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
CLAIM_SCOPE = (
    "Selected-baseline D=3 escaping assignment/slot-choice landings joined "
    "to n=9 vertex-circle family/template diagnostics; not a proof of n=9, "
    "not a counterexample, not an incidence-completeness result, not a "
    "geometric realizability test, and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_selected_baseline_d3_vertex_circle_template_join.py",
    "command": (
        "python scripts/check_n9_selected_baseline_d3_vertex_circle_template_join.py "
        "--assert-expected --write"
    ),
}
SOURCE_ARTIFACTS = [
    {
        "path": "data/certificates/n9_selected_baseline_d3_escape_class_crosswalk.json",
        "role": "aggregate selected-baseline D=3 escape-class crosswalk",
        "schema": CROSSWALK_SCHEMA,
        "trust": CROSSWALK_TRUST,
    },
    {
        "path": "data/certificates/n9_vertex_circle_frontier_motif_classification.json",
        "role": "assignment_id to vertex-circle family/template diagnostics",
        "schema": CLASSIFICATION_SCHEMA,
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
    },
    {
        "path": "data/certificates/n9_vertex_circle_template_lemma_catalog.json",
        "role": "vertex-circle template status and coverage diagnostics",
        "schema": TEMPLATE_CATALOG_SCHEMA,
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
    },
]
INTERPRETATION = [
    "Each landing record is one labelled pre-vertex-circle assignment plus one escaping budget-3 selected-baseline empty-slot choice.",
    "The join key is assignment_id; vertex-circle family and template ids are inherited diagnostics.",
    "Landing counts are assignment/slot-choice bookkeeping counts, not geometric realizability counts.",
    "Template ids and family ids are reviewer-navigation aids and lemma-mining diagnostics, not theorem names.",
    "No proof of the n=9 case is claimed.",
]

EXPECTED_ESCAPING_LANDING_COUNT = 1746
EXPECTED_STATUS_LANDING_COUNTS = {"self_edge": 1026, "strict_cycle": 720}
EXPECTED_TEMPLATE_LANDING_COUNTS = {
    "T01": 72,
    "T02": 72,
    "T03": 342,
    "T04": 108,
    "T05": 0,
    "T06": 324,
    "T07": 72,
    "T08": 36,
    "T09": 0,
    "T10": 612,
    "T11": 0,
    "T12": 108,
}
EXPECTED_ESCAPE_LANDING_COUNTS = {
    "X00": 198,
    "X01": 90,
    "X02": 144,
    "X03": 234,
    "X04": 396,
    "X05": 162,
    "X06": 126,
    "X07": 396,
}
EXPECTED_NONZERO_TEMPLATE_ESCAPE_CELL_COUNT = 38
EXPECTED_FAMILY_LANDING_COUNTS = {
    "F01": 36,
    "F02": 36,
    "F03": 0,
    "F04": 36,
    "F05": 342,
    "F06": 72,
    "F07": 0,
    "F08": 0,
    "F09": 72,
    "F10": 0,
    "F11": 324,
    "F12": 612,
    "F13": 108,
    "F14": 0,
    "F15": 0,
    "F16": 108,
}


def _assignment_rows_by_id(
    classification_payload: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Return classification assignment rows keyed by stable assignment id."""

    if classification_payload.get("schema") != CLASSIFICATION_SCHEMA:
        raise ValueError("unexpected frontier motif-classification schema")
    assignments = classification_payload.get("assignments")
    if not isinstance(assignments, list):
        raise ValueError("classification payload must contain assignments")
    rows: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(assignments, start=1):
        if not isinstance(row, dict):
            raise ValueError("classification assignment rows must be objects")
        assignment_id = str(row.get("assignment_id"))
        expected_id = f"A{index:03d}"
        if assignment_id != expected_id:
            raise AssertionError(f"unexpected assignment id {assignment_id!r}")
        if assignment_id in rows:
            raise AssertionError(f"duplicate assignment id {assignment_id}")
        rows[assignment_id] = row
    return rows


def _template_rows_by_id(
    template_catalog_payload: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Return template catalog rows keyed by Txx id."""

    if template_catalog_payload.get("schema") != TEMPLATE_CATALOG_SCHEMA:
        raise ValueError("unexpected vertex-circle template catalog schema")
    templates = template_catalog_payload.get("templates")
    if not isinstance(templates, list):
        raise ValueError("template catalog must contain templates")
    rows = {}
    for row in templates:
        if not isinstance(row, dict):
            raise ValueError("template catalog rows must be objects")
        template_id = str(row["template_id"])
        if template_id in rows:
            raise AssertionError(f"duplicate template id {template_id}")
        rows[template_id] = row
    expected_ids = set(EXPECTED_TEMPLATE_LANDING_COUNTS)
    if set(rows) != expected_ids:
        raise AssertionError("template catalog does not contain T01..T12")
    return rows


def _compact_rows(rows: Sequence[Sequence[int]]) -> list[list[int]]:
    """Return full selected rows as compact ``[center, witnesses...]`` records."""

    return [
        [int(center), *[int(witness) for witness in witnesses]]
        for center, witnesses in enumerate(rows)
    ]


def _slot_payload(slot: dict[str, int]) -> dict[str, Any]:
    """Return a stable JSON slot payload."""

    payload: dict[str, Any] = {
        "base": [int(slot["a"]), int(slot["b"])],
        "cyclic_length": int(slot["cyclic_length"]),
        "slot": int(slot["slot"]),
    }
    if "base_index" in slot:
        payload["base_index"] = int(slot["base_index"])
    return payload


def _template_summary_rows(
    template_catalog_payload: dict[str, Any],
    landing_counts: Counter[str],
) -> list[dict[str, Any]]:
    """Return compact template coverage plus landing counts."""

    template_rows = _template_rows_by_id(template_catalog_payload)
    rows = []
    for template_id in sorted(EXPECTED_TEMPLATE_LANDING_COUNTS):
        template = template_rows[template_id]
        coverage = template["coverage"]
        rows.append(
            {
                "template_id": template_id,
                "status": str(template["status"]),
                "source_assignment_count": int(coverage["assignment_count"]),
                "source_family_count": int(coverage["family_count"]),
                "escaping_landing_count": int(landing_counts[template_id]),
            }
        )
    return rows


def _dense_template_escape_matrix(
    template_counts: Counter[tuple[str, str]],
) -> dict[str, Any]:
    """Return a dense Txx by Xyy matrix view."""

    escape_ids = [f"X{index:02d}" for index in range(8)]
    return {
        "escape_class_ids": escape_ids,
        "rows": [
            {
                "template_id": template_id,
                "escaping_landing_counts": {
                    escape_id: int(template_counts[(template_id, escape_id)])
                    for escape_id in escape_ids
                },
            }
            for template_id in sorted(EXPECTED_TEMPLATE_LANDING_COUNTS)
        ],
    }


def _nonzero_template_escape_rows(
    template_escape_counts: Counter[tuple[str, str]],
) -> list[dict[str, Any]]:
    """Return nonzero template/escape landing rows."""

    rows = []
    for template_id, escape_id in sorted(template_escape_counts):
        count = int(template_escape_counts[(template_id, escape_id)])
        if count <= 0:
            continue
        rows.append(
            {
                "template_id": template_id,
                "escape_class_id": escape_id,
                "escaping_assignment_slot_choice_landing_count": count,
            }
        )
    return rows


def _nested_counter(counter: Counter[tuple[str, str]]) -> dict[str, dict[str, int]]:
    """Return a sorted nested JSON counter."""

    outer_keys = sorted({key[0] for key in counter})
    inner_keys = sorted({key[1] for key in counter})
    return {
        outer: {
            inner: int(counter[(outer, inner)])
            for inner in inner_keys
            if counter[(outer, inner)]
        }
        for outer in outer_keys
    }


def selected_baseline_d3_vertex_circle_template_join_payload(
    classification_payload: dict[str, Any],
    template_catalog_payload: dict[str, Any],
) -> dict[str, Any]:
    """Return the selected-baseline D=3 landing-to-template join artifact."""

    assignments, _nodes = pre_vertex_circle_assignments()
    summaries = [deficit_summary(_rows_from_assignment(assign)) for assign in assignments]
    selected_rows, selected_class_ids = _selected_baseline_rows(summaries)
    escape_rows, escape_class_ids = _escape_rows()
    assignments_by_id = _assignment_rows_by_id(classification_payload)

    landing_records: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter(
        {family_id: 0 for family_id in EXPECTED_FAMILY_LANDING_COUNTS}
    )
    template_counts: Counter[str] = Counter(
        {template_id: 0 for template_id in EXPECTED_TEMPLATE_LANDING_COUNTS}
    )
    escape_counts: Counter[str] = Counter(
        {escape_id: 0 for escape_id in EXPECTED_ESCAPE_LANDING_COUNTS}
    )
    selected_counts: Counter[str] = Counter()
    status_escape_counts: Counter[tuple[str, str]] = Counter()
    template_escape_counts: Counter[tuple[str, str]] = Counter()
    family_escape_counts: Counter[tuple[str, str]] = Counter()

    total_choices = 0
    forced_choices = 0
    landing_index = 0
    for assignment_index, (assignment, summary) in enumerate(
        zip(assignments, summaries),
        start=1,
    ):
        assignment_id = f"A{assignment_index:03d}"
        rows = _rows_from_assignment(assignment)
        compact_rows = _compact_rows(rows)
        classification = assignments_by_id[assignment_id]
        if classification.get("selected_rows") != compact_rows:
            raise AssertionError(f"{assignment_id} selected rows do not match")
        slots = selected_baseline_empty_slots(rows)
        if len(slots) != BASE_APEX_SLACK:
            raise AssertionError("unexpected selected-baseline empty-slot count")
        selected_id = _assignment_class_id(summary, selected_class_ids)

        for choice_index, chosen_indices in enumerate(
            combinations(range(len(slots)), CAPACITY_DEFICIT_BUDGET),
        ):
            total_choices += 1
            spoiled2, spoiled3 = _chosen_relevant_placement(slots, chosen_indices)
            diagnostic = turn_cover_diagnostic(
                N,
                spoiled_length2=spoiled2,
                spoiled_length3=spoiled3,
                contradiction_threshold=CONTRADICTION_THRESHOLD,
            )
            if diagnostic.forces_turn_contradiction:
                forced_choices += 1
                continue

            landing_index += 1
            escape_key = canonical_deficit_placement(N, spoiled2, spoiled3)
            escape_id = escape_class_ids[escape_key]
            status = str(classification["status"])
            family_id = str(classification["family_id"])
            template_id = str(classification["template_id"])
            core_size = int(classification["core_size"])
            selected_counts[selected_id] += 1
            status_counts[status] += 1
            family_counts[family_id] += 1
            template_counts[template_id] += 1
            escape_counts[escape_id] += 1
            status_escape_counts[(status, escape_id)] += 1
            template_escape_counts[(template_id, escape_id)] += 1
            family_escape_counts[(family_id, escape_id)] += 1
            landing_records.append(
                {
                    "landing_id": f"L{landing_index:04d}",
                    "assignment_id": assignment_id,
                    "budget3_slot_choice_index": int(choice_index),
                    "budget3_slot_choice_indices": [int(index) for index in chosen_indices],
                    "budget3_slot_choice_slots": [
                        _slot_payload(slots[index]) for index in chosen_indices
                    ],
                    "selected_baseline_class_id": selected_id,
                    "escape_class_id": escape_id,
                    "relevant_escape_placement": placement_key_payload(
                        spoiled2,
                        spoiled3,
                    ),
                    "vertex_circle_status": status,
                    "vertex_circle_family_id": family_id,
                    "vertex_circle_template_id": template_id,
                    "vertex_circle_core_size": core_size,
                }
            )

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "witness_size": WITNESS_SIZE,
        "base_apex_slack": BASE_APEX_SLACK,
        "capacity_deficit_budget": CAPACITY_DEFICIT_BUDGET,
        "contradiction_threshold": CONTRADICTION_THRESHOLD,
        "source_assignment_count": len(assignments),
        "total_budget3_slot_choice_count": total_choices,
        "forced_budget3_slot_choice_count": forced_choices,
        "escaping_assignment_slot_choice_landing_count": len(landing_records),
        "selected_baseline_class_count": len(selected_rows),
        "escape_class_count": len(escape_rows),
        "vertex_circle_template_count": len(EXPECTED_TEMPLATE_LANDING_COUNTS),
        "vertex_circle_family_count": len(EXPECTED_FAMILY_LANDING_COUNTS),
        "vertex_circle_status_landing_counts": dict(sorted(status_counts.items())),
        "vertex_circle_template_landing_counts": {
            key: int(template_counts[key]) for key in sorted(template_counts)
        },
        "vertex_circle_family_landing_counts": {
            key: int(family_counts[key]) for key in sorted(family_counts)
        },
        "escape_class_landing_counts": {
            key: int(escape_counts[key]) for key in sorted(escape_counts)
        },
        "selected_baseline_class_landing_counts": {
            key: int(selected_counts[key]) for key in sorted(selected_counts)
        },
        "status_escape_class_landing_counts": _nested_counter(status_escape_counts),
        "template_escape_class_landing_matrix": _dense_template_escape_matrix(
            template_escape_counts,
        ),
        "template_escape_class_landing_rows": _nonzero_template_escape_rows(
            template_escape_counts,
        ),
        "family_escape_class_landing_counts": _nested_counter(family_escape_counts),
        "vertex_circle_template_summaries": _template_summary_rows(
            template_catalog_payload,
            template_counts,
        ),
        "landing_records": landing_records,
        "interpretation": INTERPRETATION,
        "source_artifacts": SOURCE_ARTIFACTS,
        "provenance": PROVENANCE,
    }
    assert_expected_template_join_counts(payload)
    return payload


def assert_expected_template_join_counts(payload: dict[str, Any]) -> None:
    """Assert pinned counts and nonclaiming metadata for this join artifact."""

    expected_meta = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "witness_size": WITNESS_SIZE,
        "base_apex_slack": BASE_APEX_SLACK,
        "capacity_deficit_budget": CAPACITY_DEFICIT_BUDGET,
        "contradiction_threshold": CONTRADICTION_THRESHOLD,
        "source_assignment_count": EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS,
        "total_budget3_slot_choice_count": CROSSWALK_EXPECTED_COUNTS[
            "total_budget3_slot_choice_count"
        ],
        "forced_budget3_slot_choice_count": CROSSWALK_EXPECTED_COUNTS[
            "forced_budget3_slot_choice_count"
        ],
        "escaping_assignment_slot_choice_landing_count": (
            EXPECTED_ESCAPING_LANDING_COUNT
        ),
        "selected_baseline_class_count": CROSSWALK_EXPECTED_COUNTS[
            "selected_baseline_class_count"
        ],
        "escape_class_count": CROSSWALK_EXPECTED_COUNTS["escape_class_count"],
        "vertex_circle_template_count": len(EXPECTED_TEMPLATE_LANDING_COUNTS),
        "vertex_circle_family_count": len(EXPECTED_FAMILY_LANDING_COUNTS),
        "vertex_circle_status_landing_counts": EXPECTED_STATUS_LANDING_COUNTS,
        "vertex_circle_template_landing_counts": EXPECTED_TEMPLATE_LANDING_COUNTS,
        "vertex_circle_family_landing_counts": EXPECTED_FAMILY_LANDING_COUNTS,
        "escape_class_landing_counts": EXPECTED_ESCAPE_LANDING_COUNTS,
        "interpretation": INTERPRETATION,
        "source_artifacts": SOURCE_ARTIFACTS,
        "provenance": PROVENANCE,
    }
    for key, expected in expected_meta.items():
        if payload.get(key) != expected:
            raise AssertionError(f"unexpected {key}")

    records = payload.get("landing_records")
    if not isinstance(records, list):
        raise AssertionError("landing_records must be a list")
    if len(records) != EXPECTED_ESCAPING_LANDING_COUNT:
        raise AssertionError("unexpected landing record count")
    if [record.get("landing_id") for record in records] != [
        f"L{index:04d}" for index in range(1, EXPECTED_ESCAPING_LANDING_COUNT + 1)
    ]:
        raise AssertionError("unexpected landing ids")

    template_rows = payload.get("template_escape_class_landing_rows")
    if not isinstance(template_rows, list):
        raise AssertionError("template_escape_class_landing_rows must be a list")
    if len(template_rows) != EXPECTED_NONZERO_TEMPLATE_ESCAPE_CELL_COUNT:
        raise AssertionError("unexpected nonzero template/escape cell count")
    row_total = sum(
        int(row["escaping_assignment_slot_choice_landing_count"])
        for row in template_rows
    )
    if row_total != EXPECTED_ESCAPING_LANDING_COUNT:
        raise AssertionError("template/escape rows do not sum to landings")

    summaries = payload.get("vertex_circle_template_summaries")
    if not isinstance(summaries, list):
        raise AssertionError("vertex_circle_template_summaries must be a list")
    summary_counts = {
        str(row["template_id"]): int(row["escaping_landing_count"])
        for row in summaries
    }
    if summary_counts != EXPECTED_TEMPLATE_LANDING_COUNTS:
        raise AssertionError("template summaries do not match pinned counts")


def landing_record_count_by_assignment(
    payload: dict[str, Any],
) -> dict[str, int]:
    """Return landing-record counts by assignment id for tests and diagnostics."""

    records = payload.get("landing_records")
    if not isinstance(records, list):
        raise ValueError("landing_records must be a list")
    counts: Counter[str] = Counter()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("landing records must be objects")
        counts[str(record["assignment_id"])] += 1
    return json_counter(counts)
