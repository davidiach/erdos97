"""Selected-baseline D=3 escape-class crosswalk for n=9.

This module is finite bookkeeping. It joins the 184 pre-vertex-circle
selected-witness assignments to budget-3 selected-baseline empty-slot choices
and records which choices land in the strict r=3 escape classes. It does not
test geometric realizability and does not prove the n=9 case.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Any, Sequence

from erdos97.n9_base_apex import canonical_deficit_placement, turn_cover_diagnostic
from erdos97.n9_base_apex_low_excess_escape_crosswalk import escape_class_rows
from erdos97.n9_d3_escape_slice import escape_placements, json_counter
from erdos97.n9_selected_baseline_escape_budget import (
    deficit_summary,
    placement_key_payload,
    selected_baseline_class_rows,
    selected_baseline_empty_slots,
)
from erdos97.n9_vertex_circle_obstruction_shapes import (
    EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS,
    _rows_from_assignment,
    pre_vertex_circle_assignments,
)

N = 9
WITNESS_SIZE = 4
BASE_APEX_SLACK = 9
CAPACITY_DEFICIT_BUDGET = 3
CONTRADICTION_THRESHOLD = 3

EXPECTED_SCHEMA = "erdos97.n9_selected_baseline_d3_escape_class_crosswalk.v1"
EXPECTED_STATUS = "EXPLORATORY_LEDGER_ONLY"
EXPECTED_TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
EXPECTED_CLAIM_SCOPE = (
    "Focused n=9 selected-baseline D=3 escape-class crosswalk bookkeeping; "
    "not a proof of n=9, not a counterexample, not an incidence-completeness "
    "result, not a geometric realizability test, and not a global status update."
)
EXPECTED_SOURCE_ARTIFACTS = {
    "pre_vertex_circle_assignments": "data/certificates/n9_vertex_circle_exhaustive.json",
    "selected_baseline_overlay": (
        "data/certificates/n9_selected_baseline_escape_budget_overlay.json"
    ),
    "d3_escape_slice": "data/certificates/n9_base_apex_d3_escape_slice.json",
    "low_excess_escape_crosswalk": (
        "data/certificates/n9_base_apex_low_excess_escape_crosswalk.json"
    ),
}
EXPECTED_INTERPRETATION = [
    "Rows join selected-baseline relevant-deficit classes Bxx to strict r=3 escape classes Xyy.",
    "Budget-3 choices are three selected-baseline empty capacity slots per pre-vertex-circle assignment.",
    "The 1746 escaping assignment/slot-choice landings are not geometric realizability counts.",
    "The 1746 landings are not comparable to the 18088 common-dihedral profile/escape classes.",
    "Selected-baseline empty slots can later be filled by unselected equal-distance triples or profile excess.",
    "No proof of the n=9 case is claimed.",
]
EXPECTED_PROVENANCE = {
    "generator": "scripts/analyze_n9_selected_baseline_d3_escape_class_crosswalk.py",
    "command": (
        "python scripts/analyze_n9_selected_baseline_d3_escape_class_crosswalk.py "
        "--assert-expected --out "
        "data/certificates/n9_selected_baseline_d3_escape_class_crosswalk.json"
    ),
}
EXPECTED_COUNTS = {
    "assignment_count": 184,
    "selected_baseline_class_count": 13,
    "escape_class_count": 8,
    "total_budget3_slot_choice_count": 15456,
    "forced_budget3_slot_choice_count": 13710,
    "escaping_budget3_slot_choice_count": 1746,
    "nonzero_crosswalk_cell_count": 36,
    "relevant_count_distribution": {"0": 1176, "1": 4032, "2": 4536, "3": 5712},
    "escaping_relevant_count_distribution": {"3": 1746},
    "forced_relevant_count_distribution": {
        "0": 1176,
        "1": 4032,
        "2": 4536,
        "3": 3966,
    },
}


def _selected_baseline_rows(
    summaries: Sequence[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[tuple[tuple[int, ...], tuple[int, ...]], str]]:
    """Return Bxx selected-baseline class rows and canonical key lookup."""

    rows = []
    key_to_id: dict[tuple[tuple[int, ...], tuple[int, ...]], str] = {}
    for index, row in enumerate(selected_baseline_class_rows(summaries)):
        class_id = f"B{index:02d}"
        placement = row["canonical_relevant_placement"]
        key = (
            tuple(placement["spoiled_length2"]),
            tuple(placement["spoiled_length3"]),
        )
        key_to_id[key] = class_id
        rows.append({"selected_baseline_class_id": class_id, **row})
    return rows, key_to_id


def _escape_rows() -> tuple[list[dict[str, Any]], dict[tuple[tuple[int, ...], tuple[int, ...]], str]]:
    """Return Xyy escape-class rows and canonical key lookup."""

    rows, _members = escape_class_rows(escape_placements())
    key_to_id = {
        (
            tuple(row["canonical_escape_placement"]["spoiled_length2"]),
            tuple(row["canonical_escape_placement"]["spoiled_length3"]),
        ): str(row["escape_class_id"])
        for row in rows
    }
    return rows, key_to_id


def _assignment_class_id(
    summary: dict[str, Any],
    selected_class_ids: dict[tuple[tuple[int, ...], tuple[int, ...]], str],
) -> str:
    """Return the Bxx class id for one selected-baseline assignment."""

    key = canonical_deficit_placement(
        N,
        summary["spoiled_length2"],
        summary["spoiled_length3"],
    )
    return selected_class_ids[key]


def _chosen_relevant_placement(
    slots: Sequence[dict[str, int]],
    chosen_indices: Sequence[int],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return relevant length-2/length-3 deficits for one slot choice."""

    spoiled2 = tuple(
        sorted(
            {
                slots[index]["base_index"]
                for index in chosen_indices
                if slots[index]["cyclic_length"] == 2
            }
        )
    )
    spoiled3 = tuple(
        sorted(
            {
                slots[index]["base_index"]
                for index in chosen_indices
                if slots[index]["cyclic_length"] == 3
            }
        )
    )
    return spoiled2, spoiled3


def _crosswalk_matrix(
    selected_rows: Sequence[dict[str, Any]],
    escape_rows_payload: Sequence[dict[str, Any]],
    cell_counts: Counter[tuple[str, str]],
) -> dict[str, Any]:
    """Return a dense Bxx by Xyy matrix view."""

    escape_ids = [str(row["escape_class_id"]) for row in escape_rows_payload]
    matrix_rows = []
    for selected_row in selected_rows:
        selected_id = str(selected_row["selected_baseline_class_id"])
        matrix_rows.append(
            {
                "selected_baseline_class_id": selected_id,
                "canonical_relevant_placement": selected_row[
                    "canonical_relevant_placement"
                ],
                "assignment_count": selected_row["assignment_count"],
                "escaping_landing_counts": {
                    escape_id: int(cell_counts[(selected_id, escape_id)])
                    for escape_id in escape_ids
                },
            }
        )
    return {"escape_class_ids": escape_ids, "rows": matrix_rows}


def _nonzero_crosswalk_rows(
    selected_rows: Sequence[dict[str, Any]],
    escape_rows_payload: Sequence[dict[str, Any]],
    cell_counts: Counter[tuple[str, str]],
) -> list[dict[str, Any]]:
    """Return nonzero Bxx/Xyy landing rows."""

    selected_by_id = {
        str(row["selected_baseline_class_id"]): row for row in selected_rows
    }
    escape_by_id = {str(row["escape_class_id"]): row for row in escape_rows_payload}
    rows = []
    for selected_id, escape_id in sorted(cell_counts):
        count = int(cell_counts[(selected_id, escape_id)])
        if count == 0:
            continue
        rows.append(
            {
                "selected_baseline_class_id": selected_id,
                "escape_class_id": escape_id,
                "selected_baseline_assignment_count": selected_by_id[selected_id][
                    "assignment_count"
                ],
                "selected_baseline_relevant_deficit_count": selected_by_id[
                    selected_id
                ]["relevant_deficit_count"],
                "canonical_selected_baseline_relevant_placement": selected_by_id[
                    selected_id
                ]["canonical_relevant_placement"],
                "canonical_escape_placement": escape_by_id[escape_id][
                    "canonical_escape_placement"
                ],
                "escaping_assignment_slot_choice_landing_count": count,
            }
        )
    return rows


def selected_baseline_d3_escape_class_crosswalk_report() -> dict[str, Any]:
    """Return the selected-baseline D=3 escape-class crosswalk artifact."""

    assignments, _nodes = pre_vertex_circle_assignments()
    summaries = [deficit_summary(_rows_from_assignment(assign)) for assign in assignments]
    selected_rows, selected_class_ids = _selected_baseline_rows(summaries)
    escape_rows_payload, escape_class_ids = _escape_rows()

    total_choices = 0
    forced_choices = 0
    escaping_choices = 0
    relevant_counts: Counter[int] = Counter()
    forced_relevant_counts: Counter[int] = Counter()
    escaping_relevant_counts: Counter[int] = Counter()
    cell_counts: Counter[tuple[str, str]] = Counter()

    for assignment, summary in zip(assignments, summaries):
        rows = _rows_from_assignment(assignment)
        slots = selected_baseline_empty_slots(rows)
        if len(slots) != BASE_APEX_SLACK:
            raise AssertionError("unexpected selected-baseline empty-slot count")
        selected_id = _assignment_class_id(summary, selected_class_ids)
        for chosen_indices in combinations(range(len(slots)), CAPACITY_DEFICIT_BUDGET):
            total_choices += 1
            spoiled2, spoiled3 = _chosen_relevant_placement(slots, chosen_indices)
            relevant_count = len(spoiled2) + len(spoiled3)
            relevant_counts[relevant_count] += 1
            diagnostic = turn_cover_diagnostic(
                N,
                spoiled_length2=spoiled2,
                spoiled_length3=spoiled3,
                contradiction_threshold=CONTRADICTION_THRESHOLD,
            )
            if diagnostic.forces_turn_contradiction:
                forced_choices += 1
                forced_relevant_counts[relevant_count] += 1
                continue
            escaping_choices += 1
            escaping_relevant_counts[relevant_count] += 1
            escape_key = canonical_deficit_placement(N, spoiled2, spoiled3)
            escape_id = escape_class_ids[escape_key]
            cell_counts[(selected_id, escape_id)] += 1

    crosswalk_rows = _nonzero_crosswalk_rows(
        selected_rows,
        escape_rows_payload,
        cell_counts,
    )
    by_selected = Counter()
    by_escape = Counter()
    for (selected_id, escape_id), count in cell_counts.items():
        by_selected[selected_id] += count
        by_escape[escape_id] += count

    payload = {
        "schema": EXPECTED_SCHEMA,
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "claim_scope": EXPECTED_CLAIM_SCOPE,
        "n": N,
        "witness_size": WITNESS_SIZE,
        "base_apex_slack": BASE_APEX_SLACK,
        "capacity_deficit_budget": CAPACITY_DEFICIT_BUDGET,
        "contradiction_threshold": CONTRADICTION_THRESHOLD,
        "source_artifacts": EXPECTED_SOURCE_ARTIFACTS,
        "assignment_count": len(assignments),
        "selected_baseline_class_count": len(selected_rows),
        "escape_class_count": len(escape_rows_payload),
        "total_budget3_slot_choice_count": total_choices,
        "forced_budget3_slot_choice_count": forced_choices,
        "escaping_budget3_slot_choice_count": escaping_choices,
        "relevant_count_distribution": json_counter(relevant_counts),
        "forced_relevant_count_distribution": json_counter(forced_relevant_counts),
        "escaping_relevant_count_distribution": json_counter(escaping_relevant_counts),
        "every_escaping_placement_relevant_count": (
            sorted(escaping_relevant_counts) == [CAPACITY_DEFICIT_BUDGET]
        ),
        "selected_baseline_classes": selected_rows,
        "escape_classes": escape_rows_payload,
        "crosswalk_matrix": _crosswalk_matrix(
            selected_rows,
            escape_rows_payload,
            cell_counts,
        ),
        "crosswalk_rows": crosswalk_rows,
        "crosswalk_summary": {
            "nonzero_crosswalk_cell_count": len(crosswalk_rows),
            "escaping_landing_count_by_selected_baseline_class": {
                key: int(by_selected[key]) for key in sorted(by_selected)
            },
            "escaping_landing_count_by_escape_class": {
                key: int(by_escape[key]) for key in sorted(by_escape)
            },
            "escaping_assignment_slot_choice_landing_count": escaping_choices,
            "not_comparable_reference_common_dihedral_profile_escape_class_count": 18088,
        },
        "interpretation": EXPECTED_INTERPRETATION,
        "provenance": EXPECTED_PROVENANCE,
    }
    assert_expected_crosswalk_counts(payload)
    return payload


def assert_expected_crosswalk_counts(payload: dict[str, Any]) -> None:
    """Assert pinned counts and nonclaiming metadata for the crosswalk."""

    top_level_expected = {
        "schema": EXPECTED_SCHEMA,
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "claim_scope": EXPECTED_CLAIM_SCOPE,
        "n": N,
        "witness_size": WITNESS_SIZE,
        "base_apex_slack": BASE_APEX_SLACK,
        "capacity_deficit_budget": CAPACITY_DEFICIT_BUDGET,
        "contradiction_threshold": CONTRADICTION_THRESHOLD,
        "source_artifacts": EXPECTED_SOURCE_ARTIFACTS,
        "interpretation": EXPECTED_INTERPRETATION,
        "provenance": EXPECTED_PROVENANCE,
    }
    for key in (
        "assignment_count",
        "selected_baseline_class_count",
        "escape_class_count",
        "total_budget3_slot_choice_count",
        "forced_budget3_slot_choice_count",
        "escaping_budget3_slot_choice_count",
        "relevant_count_distribution",
        "escaping_relevant_count_distribution",
        "forced_relevant_count_distribution",
    ):
        top_level_expected[key] = EXPECTED_COUNTS[key]

    for key, expected in top_level_expected.items():
        if payload.get(key) != expected:
            raise AssertionError(f"unexpected {key}")

    if payload.get("assignment_count") != EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS:
        raise AssertionError("unexpected source assignment count")
    if payload.get("every_escaping_placement_relevant_count") is not True:
        raise AssertionError("escaping placements must all have relevant count 3")

    selected_rows = payload.get("selected_baseline_classes")
    if not isinstance(selected_rows, list):
        raise AssertionError("selected_baseline_classes must be a list")
    if [row.get("selected_baseline_class_id") for row in selected_rows] != [
        f"B{index:02d}" for index in range(EXPECTED_COUNTS["selected_baseline_class_count"])
    ]:
        raise AssertionError("unexpected selected-baseline class ids")
    selected_total = sum(int(row["assignment_count"]) for row in selected_rows)
    if selected_total != EXPECTED_COUNTS["assignment_count"]:
        raise AssertionError("selected-baseline class counts do not sum to assignments")

    escape_rows_payload = payload.get("escape_classes")
    if not isinstance(escape_rows_payload, list):
        raise AssertionError("escape_classes must be a list")
    if [row.get("escape_class_id") for row in escape_rows_payload] != [
        f"X{index:02d}" for index in range(EXPECTED_COUNTS["escape_class_count"])
    ]:
        raise AssertionError("unexpected escape class ids")

    crosswalk_rows = payload.get("crosswalk_rows")
    if not isinstance(crosswalk_rows, list):
        raise AssertionError("crosswalk_rows must be a list")
    if len(crosswalk_rows) != EXPECTED_COUNTS["nonzero_crosswalk_cell_count"]:
        raise AssertionError("unexpected nonzero crosswalk cell count")
    row_total = sum(
        int(row["escaping_assignment_slot_choice_landing_count"])
        for row in crosswalk_rows
    )
    if row_total != EXPECTED_COUNTS["escaping_budget3_slot_choice_count"]:
        raise AssertionError("crosswalk row landings do not sum to escaping choices")

    summary = payload.get("crosswalk_summary")
    if not isinstance(summary, dict):
        raise AssertionError("missing crosswalk_summary")
    if summary.get("nonzero_crosswalk_cell_count") != EXPECTED_COUNTS[
        "nonzero_crosswalk_cell_count"
    ]:
        raise AssertionError("summary has unexpected nonzero cell count")
    if summary.get(
        "escaping_assignment_slot_choice_landing_count"
    ) != EXPECTED_COUNTS["escaping_budget3_slot_choice_count"]:
        raise AssertionError("summary has unexpected escaping landing count")

    for row in crosswalk_rows:
        if row.get("escaping_assignment_slot_choice_landing_count", 0) <= 0:
            raise AssertionError("crosswalk rows must be nonzero")


def selected_baseline_d3_class_payload(
    spoiled_length2: Sequence[int],
    spoiled_length3: Sequence[int],
) -> dict[str, list[int]]:
    """Return a canonical selected-baseline placement payload.

    This small public helper is useful in tests and mirrors the JSON shape used
    by the selected-baseline overlay.
    """

    return placement_key_payload(
        *canonical_deficit_placement(N, spoiled_length2, spoiled_length3)
    )
