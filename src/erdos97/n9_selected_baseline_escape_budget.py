"""Selected-baseline escape-budget overlay for the n=9 base-apex ledger.

This module is diagnostic bookkeeping. It compares the 184 complete n=9
selected-witness assignments before vertex-circle pruning against the cyclic
base-capacity ledger used by the base-apex workstream. It does not prove the
n=9 case and does not claim a counterexample.
"""

from __future__ import annotations

import math
import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Iterable, Sequence

from erdos97.n9_base_apex import (
    canonical_deficit_placement,
    turn_cover_diagnostic,
)
from erdos97.n9_vertex_circle_obstruction_shapes import (
    EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS,
    EXPECTED_PRE_VERTEX_CIRCLE_NODES,
    _rows_from_assignment,
    pre_vertex_circle_assignments,
)
from erdos97.vertex_circle_order_filter import vertex_circle_order_obstruction

N = 9
ROW_SIZE = 4
BASE_APEX_SLACK = 9
SELECTED_BASELINE_USAGE = N * math.comb(ROW_SIZE, 2)
CYCLIC_BASE_CAPACITY_TOTAL = 63
STRICT_POSITIVE_THRESHOLD = 3
SUM_EXCEEDS_THRESHOLD = 4
ROOT = Path(__file__).resolve().parents[2]
ACCEPTED_FRONTIER_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_incidence_frontier_bounded.json"
)

EXPECTED_RELEVANT_DEFICIT_DISTRIBUTION = {
    0: 2,
    3: 24,
    4: 36,
    5: 36,
    6: 24,
    8: 18,
    9: 44,
}
EXPECTED_SELECTED_BASELINE_REMAINING_FORCED_TURNS = {
    0: 50,
    1: 54,
    2: 36,
    3: 42,
    5: 2,
}
EXPECTED_STRICT_FORCED_ASSIGNMENTS = 44
EXPECTED_CONSERVATIVE_FORCED_ASSIGNMENTS = 2
EXPECTED_DIHEDRAL_RELEVANT_PLACEMENT_CLASSES = 13
EXPECTED_STRICT_UNIVERSALLY_FORCED_BY_BUDGET = {
    0: 184,
    1: 184,
    2: 184,
    3: 48,
    4: 48,
    5: 44,
    6: 44,
    7: 44,
    8: 44,
    9: 44,
}
EXPECTED_CONSERVATIVE_UNIVERSALLY_FORCED_BY_BUDGET = {
    0: 184,
    1: 184,
    2: 6,
    3: 2,
    4: 2,
    5: 2,
    6: 2,
    7: 2,
    8: 2,
    9: 2,
}


def pair(a: int, b: int) -> tuple[int, int]:
    """Return a normalized unordered pair."""

    return (a, b) if a < b else (b, a)


def cyclic_length(a: int, b: int, n: int = N) -> int:
    """Return the shorter cyclic length of a base."""

    delta = (b - a) % n
    return min(delta, n - delta)


def capacity_for_cyclic_length(cyclic_length_value: int) -> int:
    """Return the base-apex selected-baseline capacity for one cyclic length."""

    return 1 if cyclic_length_value == 1 else 2


def base_index(a: int, b: int, cyclic_length_value: int, n: int = N) -> int:
    """Return the cyclic base index for a length-2 or length-3 base."""

    if cyclic_length_value not in (2, 3):
        raise ValueError("base index is only used for length-2 and length-3 bases")
    return a if (b - a) % n == cyclic_length_value else b


def selected_base_usage(rows: Sequence[Sequence[int]]) -> Counter[tuple[int, int]]:
    """Count selected-witness row usage for each ordinary base."""

    usage: Counter[tuple[int, int]] = Counter()
    for row in rows:
        for left_index in range(len(row)):
            for right_index in range(left_index + 1, len(row)):
                usage[pair(row[left_index], row[right_index])] += 1
    return usage


def selected_baseline_empty_slots(
    rows: Sequence[Sequence[int]],
) -> list[dict[str, int]]:
    """Return unit empty capacity slots after selected-witness row usage."""

    usage = selected_base_usage(rows)
    slots: list[dict[str, int]] = []
    for a in range(N):
        for b in range(a + 1, N):
            length = cyclic_length(a, b)
            gap = capacity_for_cyclic_length(length) - usage[(a, b)]
            if gap < 0:
                raise AssertionError(f"selected usage exceeds capacity on base {(a, b)}")
            for unit in range(gap):
                row = {
                    "a": a,
                    "b": b,
                    "cyclic_length": length,
                    "slot": unit,
                }
                if length in (2, 3):
                    row["base_index"] = base_index(a, b, length)
                slots.append(row)
    return slots


def deficit_summary(rows: Sequence[Sequence[int]]) -> dict[str, object]:
    """Return selected-baseline capacity summary for one row assignment."""

    usage = selected_base_usage(rows)
    usage_by_length: Counter[int] = Counter()
    deficit_by_length: Counter[int] = Counter()
    saturated_by_length: Counter[int] = Counter()
    spoiled_by_length: Counter[int] = Counter()
    overfull_bases = []
    spoiled_length2 = []
    spoiled_length3 = []
    total_deficit = 0

    for a in range(N):
        for b in range(a + 1, N):
            length = cyclic_length(a, b)
            capacity = capacity_for_cyclic_length(length)
            used = usage[(a, b)]
            usage_by_length[length] += used
            if used > capacity:
                overfull_bases.append(
                    {
                        "base": [a, b],
                        "cyclic_length": length,
                        "usage": used,
                        "capacity": capacity,
                    }
                )
                continue
            gap = capacity - used
            total_deficit += gap
            deficit_by_length[length] += gap
            if gap == 0:
                saturated_by_length[length] += 1
            else:
                spoiled_by_length[length] += 1
                if length == 2:
                    spoiled_length2.append(base_index(a, b, length))
                elif length == 3:
                    spoiled_length3.append(base_index(a, b, length))

    return {
        "usage_by_cyclic_length": length_counter_payload(usage_by_length),
        "deficit_by_cyclic_length": length_counter_payload(deficit_by_length),
        "saturated_base_count_by_cyclic_length": length_counter_payload(
            saturated_by_length
        ),
        "spoiled_base_count_by_cyclic_length": length_counter_payload(spoiled_by_length),
        "total_deficit": total_deficit,
        "overfull_bases": overfull_bases,
        "spoiled_length2": sorted(spoiled_length2),
        "spoiled_length3": sorted(spoiled_length3),
    }


def length_counter_payload(counter: Counter[int]) -> dict[str, int]:
    """Return length keys 1..4 as JSON strings."""

    return {str(length): int(counter[length]) for length in range(1, 5)}


def counter_payload(counter: Counter[int]) -> dict[str, int]:
    """Return a sorted integer-key counter with JSON string keys."""

    return {str(key): int(counter[key]) for key in sorted(counter)}


def placement_key_payload(
    spoiled_length2: Iterable[int],
    spoiled_length3: Iterable[int],
) -> dict[str, list[int]]:
    """Return a JSON-shaped spoiled-base placement key."""

    return {
        "spoiled_length2": [int(value) for value in spoiled_length2],
        "spoiled_length3": [int(value) for value in spoiled_length3],
    }


def budget_overlay_rows(
    slot_sets: Sequence[Sequence[dict[str, int]]],
    *,
    contradiction_threshold: int,
) -> list[dict[str, object]]:
    """Summarize all final deficit placements for each capacity budget."""

    rows = []
    for budget in range(BASE_APEX_SLACK + 1):
        total_placements = 0
        forced_placements = 0
        escaping_placements = 0
        universally_forced_assignments = 0
        assignments_with_escape = 0
        remaining_turn_counts: Counter[int] = Counter()
        relevant_deficit_counts: Counter[int] = Counter()

        for slots in slot_sets:
            assignment_forced = True
            assignment_has_escape = False
            for chosen_indices in combinations(range(len(slots)), budget):
                total_placements += 1
                spoiled2 = sorted(
                    {
                        slots[index]["base_index"]
                        for index in chosen_indices
                        if slots[index]["cyclic_length"] == 2
                    }
                )
                spoiled3 = sorted(
                    {
                        slots[index]["base_index"]
                        for index in chosen_indices
                        if slots[index]["cyclic_length"] == 3
                    }
                )
                diagnostic = turn_cover_diagnostic(
                    spoiled_length2=spoiled2,
                    spoiled_length3=spoiled3,
                    contradiction_threshold=contradiction_threshold,
                )
                remaining_turn_counts[diagnostic.minimum_forced_turns] += 1
                relevant_deficit_counts[len(spoiled2) + len(spoiled3)] += 1
                if diagnostic.forces_turn_contradiction:
                    forced_placements += 1
                else:
                    escaping_placements += 1
                    assignment_forced = False
                    assignment_has_escape = True
            if assignment_forced:
                universally_forced_assignments += 1
            if assignment_has_escape:
                assignments_with_escape += 1

        rows.append(
            {
                "capacity_deficit_budget": budget,
                "total_final_deficit_placement_count": total_placements,
                "forced_final_deficit_placement_count": forced_placements,
                "escaping_final_deficit_placement_count": escaping_placements,
                "universally_forced_assignment_count": universally_forced_assignments,
                "assignment_with_escape_count": assignments_with_escape,
                "remaining_forced_turn_count_by_final_placement": counter_payload(
                    remaining_turn_counts
                ),
                "relevant_deficit_count_by_final_placement": counter_payload(
                    relevant_deficit_counts
                ),
            }
        )
    return rows


def threshold_section(
    slot_sets: Sequence[Sequence[dict[str, int]]],
    *,
    contradiction_threshold: int,
) -> dict[str, object]:
    """Return one threshold section for final-budget overlay rows."""

    rows = budget_overlay_rows(
        slot_sets,
        contradiction_threshold=contradiction_threshold,
    )
    return {
        "contradiction_threshold": contradiction_threshold,
        "budget_rows": rows,
    }


def selected_baseline_class_rows(
    summaries: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    """Return dihedral classes of selected-baseline relevant deficits."""

    classes: Counter[tuple[tuple[int, ...], tuple[int, ...]]] = Counter()
    minimum_forced_turns: dict[tuple[tuple[int, ...], tuple[int, ...]], int] = {}
    strict_forced: dict[tuple[tuple[int, ...], tuple[int, ...]], bool] = {}
    conservative_forced: dict[tuple[tuple[int, ...], tuple[int, ...]], bool] = {}

    for summary in summaries:
        spoiled2 = tuple(summary["spoiled_length2"])
        spoiled3 = tuple(summary["spoiled_length3"])
        key = canonical_deficit_placement(N, spoiled2, spoiled3)
        diagnostic = turn_cover_diagnostic(
            spoiled_length2=spoiled2,
            spoiled_length3=spoiled3,
            contradiction_threshold=STRICT_POSITIVE_THRESHOLD,
        )
        conservative = turn_cover_diagnostic(
            spoiled_length2=spoiled2,
            spoiled_length3=spoiled3,
            contradiction_threshold=SUM_EXCEEDS_THRESHOLD,
        )
        classes[key] += 1
        minimum_forced_turns[key] = diagnostic.minimum_forced_turns
        strict_forced[key] = diagnostic.forces_turn_contradiction
        conservative_forced[key] = conservative.forces_turn_contradiction

    return [
        {
            "canonical_relevant_placement": placement_key_payload(*key),
            "assignment_count": int(classes[key]),
            "relevant_deficit_count": len(key[0]) + len(key[1]),
            "remaining_minimum_forced_turns": minimum_forced_turns[key],
            "strict_positive_forces_turn_cover": strict_forced[key],
            "sum_exceeds_forces_turn_cover": conservative_forced[key],
        }
        for key in sorted(classes, key=lambda item: (len(item[0]) + len(item[1]), item))
    ]


def accepted_frontier_overlay() -> dict[str, object]:
    """Return the selected-baseline overlay for the bounded accepted frontier."""

    artifact = json.loads(ACCEPTED_FRONTIER_ARTIFACT.read_text(encoding="utf-8"))
    examples = artifact.get("examples", {})
    frontiers = (
        examples.get("accepted_frontier", [])
        if isinstance(examples, dict)
        else []
    )
    accepted_frontier_count = int(artifact.get("accepted_frontier_count", len(frontiers)))
    if accepted_frontier_count != len(frontiers):
        raise AssertionError(
            "accepted_frontier_count does not match accepted_frontier examples"
        )
    if not frontiers:
        return {
            "source": "data/certificates/n9_incidence_frontier_bounded.json",
            "accepted_frontier_count": 0,
            "rows": [],
            "vertex_circle_status": "none",
            "selected_baseline": None,
            "turn_cover_overlay": None,
            "interpretation": (
                "No accepted_frontier row system is recorded in the bounded "
                "frontier artifact; this overlay therefore has no surviving "
                "frontier escape example to analyze."
            ),
        }
    if len(frontiers) != 1:
        raise AssertionError(f"expected one accepted_frontier, got {len(frontiers)}")
    rows = frontiers[0]["rows"]
    summary = deficit_summary(rows)
    spoiled2 = summary["spoiled_length2"]
    spoiled3 = summary["spoiled_length3"]
    strict = turn_cover_diagnostic(
        spoiled_length2=spoiled2,
        spoiled_length3=spoiled3,
        contradiction_threshold=STRICT_POSITIVE_THRESHOLD,
    )
    conservative = turn_cover_diagnostic(
        spoiled_length2=spoiled2,
        spoiled_length3=spoiled3,
        contradiction_threshold=SUM_EXCEEDS_THRESHOLD,
    )
    vc_result = vertex_circle_order_obstruction(rows, list(range(N)), "n9_accepted_frontier")
    if vc_result.self_edge_conflicts:
        status = "self_edge"
    elif vc_result.cycle_edges:
        status = "strict_cycle"
    else:
        status = "ok"
    return {
        "source": "data/certificates/n9_incidence_frontier_bounded.json",
        "accepted_frontier_count": accepted_frontier_count,
        "rows": rows,
        "vertex_circle_status": status,
        "selected_baseline": {
            "usage_by_cyclic_length": summary["usage_by_cyclic_length"],
            "deficit_by_cyclic_length": summary["deficit_by_cyclic_length"],
            "saturated_base_count_by_cyclic_length": summary[
                "saturated_base_count_by_cyclic_length"
            ],
            "spoiled_base_count_by_cyclic_length": summary[
                "spoiled_base_count_by_cyclic_length"
            ],
            "total_deficit": summary["total_deficit"],
            "overfull_base_count": len(summary["overfull_bases"]),
            "spoiled_length2": spoiled2,
            "spoiled_length3": spoiled3,
            "canonical_relevant_placement": placement_key_payload(
                *canonical_deficit_placement(N, spoiled2, spoiled3)
            ),
        },
        "turn_cover_overlay": {
            "remaining_turn_clauses": [list(clause) for clause in strict.turn_clauses],
            "remaining_minimum_forced_turns": strict.minimum_forced_turns,
            "strict_positive_forces_turn_cover": strict.forces_turn_contradiction,
            "sum_exceeds_forces_turn_cover": conservative.forces_turn_contradiction,
        },
        "interpretation": (
            "This accepted_frontier row system escapes the selected-baseline "
            "turn-cover overlay; accepted_frontier means it passed the bounded "
            "frontier filters, not that it is geometrically realizable."
        ),
    }


def selected_baseline_escape_budget_overlay() -> dict[str, object]:
    """Return the generated selected-baseline escape-budget overlay artifact."""

    assignments, nodes = pre_vertex_circle_assignments()
    summaries = [deficit_summary(_rows_from_assignment(assign)) for assign in assignments]
    slot_sets = [selected_baseline_empty_slots(_rows_from_assignment(assign)) for assign in assignments]

    relevant_counts: Counter[int] = Counter()
    remaining_turn_counts: Counter[int] = Counter()
    strict_forced = 0
    conservative_forced = 0
    deficit_vector_counts: Counter[tuple[int, int, int, int]] = Counter()
    overfull_assignment_count = 0

    for summary in summaries:
        if summary["overfull_bases"]:
            overfull_assignment_count += 1
        spoiled2 = summary["spoiled_length2"]
        spoiled3 = summary["spoiled_length3"]
        strict = turn_cover_diagnostic(
            spoiled_length2=spoiled2,
            spoiled_length3=spoiled3,
            contradiction_threshold=STRICT_POSITIVE_THRESHOLD,
        )
        conservative = turn_cover_diagnostic(
            spoiled_length2=spoiled2,
            spoiled_length3=spoiled3,
            contradiction_threshold=SUM_EXCEEDS_THRESHOLD,
        )
        remaining_turn_counts[strict.minimum_forced_turns] += 1
        relevant_counts[len(spoiled2) + len(spoiled3)] += 1
        strict_forced += int(strict.forces_turn_contradiction)
        conservative_forced += int(conservative.forces_turn_contradiction)
        deficits = summary["deficit_by_cyclic_length"]
        deficit_vector_counts[
            (
                int(deficits["1"]),
                int(deficits["2"]),
                int(deficits["3"]),
                int(deficits["4"]),
            )
        ] += 1

    payload = {
        "schema": "erdos97.n9_selected_baseline_escape_budget_overlay.v2",
        "status": "EXPLORATORY_LEDGER_ONLY",
        "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
        "claim_scope": (
            "Focused n=9 selected-baseline escape-budget overlay bookkeeping; "
            "not a proof of n=9, not a counterexample, not a geometric "
            "realizability test, and not a global status update."
        ),
        "n": N,
        "witness_size": ROW_SIZE,
        "base_apex_slack": BASE_APEX_SLACK,
        "source_artifacts": {
            "pre_vertex_circle_assignments": "data/certificates/n9_vertex_circle_exhaustive.json",
            "base_apex_escape_budget": "data/certificates/n9_base_apex_escape_budget_report.json",
            "accepted_frontier": "data/certificates/n9_incidence_frontier_bounded.json",
        },
        "selected_baseline": {
            "assignment_count": len(assignments),
            "pre_vertex_circle_nodes": int(nodes),
            "selected_baseline_usage_per_assignment": SELECTED_BASELINE_USAGE,
            "cyclic_base_capacity_total": CYCLIC_BASE_CAPACITY_TOTAL,
            "selected_baseline_total_deficit_per_assignment": BASE_APEX_SLACK,
            "overfull_assignment_count": overfull_assignment_count,
            "deficit_vector_count_by_cyclic_length": [
                {
                    "deficit_by_cyclic_length": {
                        str(length): int(vector[length - 1])
                        for length in range(1, 5)
                    },
                    "assignment_count": int(count),
                }
                for vector, count in sorted(deficit_vector_counts.items())
            ],
            "relevant_deficit_count_distribution": counter_payload(relevant_counts),
            "remaining_forced_turn_count_distribution": counter_payload(
                remaining_turn_counts
            ),
            "strict_positive_forced_assignment_count": strict_forced,
            "strict_positive_escaping_assignment_count": len(assignments) - strict_forced,
            "sum_exceeds_forced_assignment_count": conservative_forced,
            "sum_exceeds_escaping_assignment_count": len(assignments)
            - conservative_forced,
            "dihedral_relevant_placement_class_count": len(
                selected_baseline_class_rows(summaries)
            ),
            "dihedral_relevant_placement_classes": selected_baseline_class_rows(
                summaries
            ),
        },
        "budget_overlay": {
            "strict_positive_threshold": threshold_section(
                slot_sets,
                contradiction_threshold=STRICT_POSITIVE_THRESHOLD,
            ),
            "sum_exceeds_threshold": threshold_section(
                slot_sets,
                contradiction_threshold=SUM_EXCEEDS_THRESHOLD,
            ),
        },
        "accepted_frontier_overlay": accepted_frontier_overlay(),
        "interpretation": [
            "The selected baseline counts only the 4 chosen witnesses at each center.",
            "Every pre-vertex-circle selected-witness assignment uses 54 base-apex incidences against cyclic capacity 63, leaving 9 selected-baseline empty capacity units.",
            "Actual unselected equal-distance triples or profile excess could fill some selected-baseline empty slots, so these counts are not geometric realizability counts.",
            "A forced row for budget D means every way to leave D selected-baseline empty slots unfilled still triggers the current length-2/length-3 turn-cover contradiction.",
            "No proof of the n=9 case is claimed.",
        ],
        "provenance": {
            "generator": "scripts/analyze_n9_selected_baseline_escape_budget_overlay.py",
            "command": (
                "python scripts/analyze_n9_selected_baseline_escape_budget_overlay.py "
                "--assert-expected --out "
                "data/certificates/n9_selected_baseline_escape_budget_overlay.json"
            ),
        },
    }
    assert_expected_overlay_counts(payload)
    return payload


def assert_expected_overlay_counts(payload: dict[str, object]) -> None:
    """Assert stable counts for the selected-baseline overlay."""

    selected = payload["selected_baseline"]
    if not isinstance(selected, dict):
        raise AssertionError("missing selected_baseline block")
    if selected["assignment_count"] != EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS:
        raise AssertionError(f"unexpected assignment count: {selected['assignment_count']}")
    if selected["pre_vertex_circle_nodes"] != EXPECTED_PRE_VERTEX_CIRCLE_NODES:
        raise AssertionError(f"unexpected node count: {selected['pre_vertex_circle_nodes']}")
    if (
        selected["relevant_deficit_count_distribution"]
        != counter_payload(Counter(EXPECTED_RELEVANT_DEFICIT_DISTRIBUTION))
    ):
        raise AssertionError("unexpected relevant deficit distribution")
    if (
        selected["remaining_forced_turn_count_distribution"]
        != counter_payload(Counter(EXPECTED_SELECTED_BASELINE_REMAINING_FORCED_TURNS))
    ):
        raise AssertionError("unexpected selected-baseline forced-turn distribution")
    if (
        selected["strict_positive_forced_assignment_count"]
        != EXPECTED_STRICT_FORCED_ASSIGNMENTS
    ):
        raise AssertionError("unexpected strict forced assignment count")
    if (
        selected["sum_exceeds_forced_assignment_count"]
        != EXPECTED_CONSERVATIVE_FORCED_ASSIGNMENTS
    ):
        raise AssertionError("unexpected conservative forced assignment count")
    if (
        selected["dihedral_relevant_placement_class_count"]
        != EXPECTED_DIHEDRAL_RELEVANT_PLACEMENT_CLASSES
    ):
        raise AssertionError("unexpected dihedral placement class count")

    strict = payload["budget_overlay"]["strict_positive_threshold"]
    conservative = payload["budget_overlay"]["sum_exceeds_threshold"]
    if not isinstance(strict, dict) or not isinstance(conservative, dict):
        raise AssertionError("missing threshold blocks")
    strict_forced = {
        int(row["capacity_deficit_budget"]): int(row["universally_forced_assignment_count"])
        for row in strict["budget_rows"]
    }
    conservative_forced = {
        int(row["capacity_deficit_budget"]): int(row["universally_forced_assignment_count"])
        for row in conservative["budget_rows"]
    }
    if strict_forced != EXPECTED_STRICT_UNIVERSALLY_FORCED_BY_BUDGET:
        raise AssertionError("unexpected strict universal-forcing counts by budget")
    if conservative_forced != EXPECTED_CONSERVATIVE_UNIVERSALLY_FORCED_BY_BUDGET:
        raise AssertionError("unexpected conservative universal-forcing counts by budget")

    frontier = payload["accepted_frontier_overlay"]
    if not isinstance(frontier, dict):
        raise AssertionError("missing accepted_frontier_overlay block")
    if frontier["accepted_frontier_count"] != 0:
        raise AssertionError("unexpected accepted-frontier count")
    if frontier["vertex_circle_status"] != "none":
        raise AssertionError("unexpected accepted-frontier vertex-circle status")
    if frontier["rows"] != []:
        raise AssertionError("unexpected accepted-frontier rows")
    if frontier["selected_baseline"] is not None:
        raise AssertionError("unexpected accepted-frontier selected-baseline block")
    if frontier["turn_cover_overlay"] is not None:
        raise AssertionError("unexpected accepted-frontier turn-cover block")
