"""Exact three-halo vertex-circle closure for one fragile-cycle quotient core.

The proper seven-role quotient that identifies scalable-template roles 23 and
27 preserves four retained fragile rows.  This module inserts exactly three
formal halo roles into its cyclic gaps, exhausts the retained-row covers, and
asks whether any cover extends to a full selected-row system that remains
clean under the vertex-circle quotient test.

This is a bounded abstract computation.  It does not construct a Euclidean
realization, force the quotient from minimal-counterexample geometry, or make
an n=10 or global theorem claim.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import combinations_with_replacement
from typing import Any, Mapping

from erdos97.fragile_cycle_halo_lift_frontier import (
    CORE_ROLE_BLOCKS,
    FRAGILE_CENTERS,
    REQUIRED_WITNESSES,
    cyclic_order_for_gaps,
)
from erdos97.fragile_hypergraph import essential_row_matching
from erdos97.generic_vertex_search import Assignment, GenericVertexSearch
from erdos97.vertex_circle_quotient_replay import (
    SelectedRow,
    replay_vertex_circle_quotient,
    result_to_json,
)


SCHEMA = "erdos97.fragile_cycle_three_halo_vertex_circle.v1"
STATUS = "EXACT_BOUNDED_THREE_HALO_VERTEX_CIRCLE_CLOSURE"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact bounded abstract n=10 scan for the 23=27 seven-role quotient of "
    "the stored scalable four-row Kalmanson circuit with exactly three added "
    "cyclic halo roles. It exhausts all 84 canonical halo-gap multisets, all "
    "four-row retained fragile covers, and every full selected-row extension "
    "under the stated incidence, crossing, capacity, and vertex-circle rules. "
    "Not Euclidean realizability, not a fragile-cycle forcing lemma, not a "
    "proof of n=10, not a general proof, not a counterexample, and not an "
    "official/global status update."
)
CONCLUSION = (
    "None of the essential retained-row covers over the 84 canonical "
    "three-halo placements extends to a full selected-row system that stays "
    "vertex-circle clean. This closes the fixed three-halo abstract slice and "
    "sharpens the Contract F proof-mining target; it does not force the core "
    "from geometry or control four or more halo roles."
)
PROVENANCE = {
    "generator": "scripts/check_fragile_cycle_three_halo_vertex_circle.py",
    "command": (
        "python scripts/check_fragile_cycle_three_halo_vertex_circle.py "
        "--write --assert-expected"
    ),
}

N = 10
HALO_COUNT = 3
ROW_SIZE = 4
PAIR_CAP = 2
EXPECTED_PLACEMENT_COUNT = 84
EXPECTED_RAW_ROW_COMBINATION_COUNT = 16_336_404
EXPECTED_PAIR_AND_CROSSING_COUNT = 352_012
EXPECTED_ESSENTIAL_COVER_COUNT = 141_750
EXPECTED_RETAINED_COVER_STATUS_COUNTS = {
    "ok": 120_690,
    "self_edge": 5_544,
    "strict_cycle": 15_516,
}
EXPECTED_EXTENSION_CANDIDATE_COUNT = 420_682
EXPECTED_EXTENSION_DEAD_END_COUNT = 108_085
EXPECTED_EXTENSION_STATUS_COUNTS = {
    "ok": 144_714,
    "self_edge": 96_008,
    "strict_cycle": 179_960,
}
EXPECTED_FULL_SURVIVOR_COUNT = 0
EXPECTED_CATALOG_TRACE_SHA256 = (
    "06132f8cf83fa5015596a1d384c5cdff5aa90d857cd66a5c264392a1bdae2c56"
)


def _assignment_key(assignment: Mapping[int, int]) -> str:
    return ";".join(f"{center}:{assignment[center]}" for center in sorted(assignment))


def _rows_from_masks(
    engine: GenericVertexSearch,
    assignment: Mapping[int, int],
) -> dict[int, tuple[int, ...]]:
    return {
        center: tuple(engine.mask_bits[mask])
        for center, mask in sorted(assignment.items())
    }


def _rows_in_original_labels(
    engine: GenericVertexSearch,
    assignment: Mapping[int, int],
    order: tuple[int, ...],
) -> list[SelectedRow]:
    return [
        SelectedRow(
            center=order[center],
            witnesses=tuple(sorted(order[value] for value in engine.mask_bits[mask])),
        )
        for center, mask in sorted(assignment.items())
    ]


def _compact_rows(rows: list[SelectedRow]) -> list[list[int]]:
    return [[row.center, *row.witnesses] for row in rows]


def _record_representative(
    representatives: dict[str, dict[str, Any]],
    *,
    status: str,
    gaps: tuple[int, ...],
    order: tuple[int, ...],
    engine: GenericVertexSearch,
    assignment: Mapping[int, int],
) -> None:
    if status in representatives:
        return
    rows = _rows_in_original_labels(engine, assignment, order)
    replay = replay_vertex_circle_quotient(N, order, rows)
    if replay.status != status:
        raise AssertionError(
            f"optimized/replay status mismatch: {status} != {replay.status}"
        )
    representatives[status] = {
        "halo_gaps": list(gaps),
        "cyclic_order": list(order),
        "selected_rows": _compact_rows(rows),
        "optimized_status": status,
        "independent_replay": result_to_json(replay),
    }


def _placement_scan(
    engine: GenericVertexSearch,
    gaps: tuple[int, ...],
    representatives: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Exhaust one canonical placement and all of its selected-row branches."""

    order = cyclic_order_for_gaps(gaps)
    if len(order) != N:
        raise AssertionError("three-halo order must have ten labels")
    position = {label: index for index, label in enumerate(order)}
    retained_centers = tuple(position[center] for center in FRAGILE_CENTERS)
    retained_options: dict[int, list[int]] = {}
    for original_center in FRAGILE_CENTERS:
        center = position[original_center]
        required_mask = sum(
            1 << position[witness]
            for witness in REQUIRED_WITNESSES[original_center]
        )
        retained_options[center] = [
            mask
            for mask in engine.options[center]
            if mask & required_mask == required_mask
        ]
        if len(retained_options[center]) != 21:
            raise AssertionError("each retained row must have 21 completions")

    raw_count = 1
    for center in retained_centers:
        raw_count *= len(retained_options[center])

    trace = sha256()
    counts: Counter[str] = Counter()
    extension_status_counts: Counter[str] = Counter()
    full_survivors: list[dict[str, Any]] = []

    def extend(
        assignment: Assignment,
        column_counts: list[int],
        witness_pair_counts: list[int],
    ) -> None:
        if len(assignment) == N:
            counts["full_vertex_circle_survivor_count"] += 1
            if len(full_survivors) < 3:
                rows = _rows_in_original_labels(engine, assignment, order)
                full_survivors.append({"selected_rows": _compact_rows(rows)})
            return

        best_center: int | None = None
        best_options: list[int] | None = None
        for center in range(N):
            if center in assignment:
                continue
            options = engine.valid_options_for_center(
                center,
                assignment,
                column_counts,
                witness_pair_counts,
            )
            if best_options is None or len(options) < len(best_options):
                best_center = center
                best_options = options
                if not options:
                    break
        if not best_options:
            counts["extension_dead_end_count"] += 1
            return

        assert best_center is not None
        for mask in best_options:
            assignment[best_center] = mask
            for target in engine.mask_bits[mask]:
                column_counts[target] += 1
            for pair_index in engine.row_pair_indices[mask]:
                witness_pair_counts[pair_index] += 1

            status = engine.vertex_circle_status(assignment)
            counts["extension_candidate_count"] += 1
            extension_status_counts[status] += 1
            trace.update(
                f"extension|{status}|{_assignment_key(assignment)}\n".encode()
            )
            if status == "ok":
                extend(assignment, column_counts, witness_pair_counts)
            else:
                _record_representative(
                    representatives,
                    status=status,
                    gaps=gaps,
                    order=order,
                    engine=engine,
                    assignment=assignment,
                )

            for pair_index in engine.row_pair_indices[mask]:
                witness_pair_counts[pair_index] -= 1
            for target in engine.mask_bits[mask]:
                column_counts[target] -= 1
            del assignment[best_center]

    def accept_cover(assignment: Assignment) -> None:
        counts["essential_cover_count"] += 1
        status = engine.vertex_circle_status(assignment)
        counts[f"retained_cover_{status}_count"] += 1
        trace.update(f"cover|{status}|{_assignment_key(assignment)}\n".encode())
        if status != "ok":
            _record_representative(
                representatives,
                status=status,
                gaps=gaps,
                order=order,
                engine=engine,
                assignment=assignment,
            )
            return

        column_counts = [0] * N
        witness_pair_counts = [0] * len(engine.pairs)
        for mask in assignment.values():
            for target in engine.mask_bits[mask]:
                column_counts[target] += 1
            for pair_index in engine.row_pair_indices[mask]:
                witness_pair_counts[pair_index] += 1
        extend(assignment, column_counts, witness_pair_counts)

    def enumerate_retained(index: int, assignment: Assignment) -> None:
        if index == len(retained_centers):
            counts["pair_and_crossing_compatible_count"] += 1
            witness_pair_counts: Counter[int] = Counter(
                pair_index
                for mask in assignment.values()
                for pair_index in engine.row_pair_indices[mask]
            )
            if max(witness_pair_counts.values(), default=0) > PAIR_CAP:
                return
            counts["pair_capacity_compatible_count"] += 1
            union_mask = 0
            for mask in assignment.values():
                union_mask |= mask
            if union_mask != (1 << N) - 1:
                return
            counts["cover_count"] += 1
            rows = _rows_from_masks(engine, assignment)
            _, unmatched = essential_row_matching(N, rows)
            if unmatched:
                return
            accept_cover(assignment)
            return

        center = retained_centers[index]
        for mask in retained_options[center]:
            if all(
                engine.rows_compatible(center, mask, other, other_mask)
                for other, other_mask in assignment.items()
            ):
                assignment[center] = mask
                enumerate_retained(index + 1, assignment)
                del assignment[center]

    enumerate_retained(0, {})
    counts["raw_row_combination_count"] = raw_count
    if counts["extension_candidate_count"] != sum(extension_status_counts.values()):
        raise AssertionError("extension status accounting mismatch")
    return {
        "halo_gaps": list(gaps),
        "cyclic_order": list(order),
        "retained_center_positions": list(retained_centers),
        "retained_row_option_counts": {
            str(order[center]): len(retained_options[center])
            for center in retained_centers
        },
        **{
            key: counts[key]
            for key in (
                "raw_row_combination_count",
                "pair_and_crossing_compatible_count",
                "pair_capacity_compatible_count",
                "cover_count",
                "essential_cover_count",
                "retained_cover_ok_count",
                "retained_cover_self_edge_count",
                "retained_cover_strict_cycle_count",
                "extension_candidate_count",
                "extension_dead_end_count",
                "full_vertex_circle_survivor_count",
            )
        },
        "extension_candidate_status_counts": {
            status: extension_status_counts[status]
            for status in ("ok", "self_edge", "strict_cycle")
        },
        "trace_sha256": trace.hexdigest(),
        "stored_full_survivors": full_survivors,
    }


def three_halo_payload() -> dict[str, Any]:
    """Return the complete deterministic three-halo closure artifact."""

    engine = GenericVertexSearch(N, row_size=ROW_SIZE, pair_cap=PAIR_CAP)
    representatives: dict[str, dict[str, Any]] = {}
    placements = [
        _placement_scan(engine, gaps, representatives)
        for gaps in combinations_with_replacement(range(7), HALO_COUNT)
    ]
    aggregate_keys = (
        "raw_row_combination_count",
        "pair_and_crossing_compatible_count",
        "pair_capacity_compatible_count",
        "cover_count",
        "essential_cover_count",
        "retained_cover_ok_count",
        "retained_cover_self_edge_count",
        "retained_cover_strict_cycle_count",
        "extension_candidate_count",
        "extension_dead_end_count",
        "full_vertex_circle_survivor_count",
    )
    aggregate = {
        key: sum(int(placement[key]) for placement in placements)
        for key in aggregate_keys
    }
    aggregate["extension_candidate_status_counts"] = {
        status: sum(
            int(placement["extension_candidate_status_counts"][status])
            for placement in placements
        )
        for status in ("ok", "self_edge", "strict_cycle")
    }
    catalog_digest = sha256(
        "\n".join(
            f"{','.join(map(str, placement['halo_gaps']))}:{placement['trace_sha256']}"
            for placement in placements
        ).encode()
    ).hexdigest()
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_core": {
            "quotient_identification": "23=27",
            "canonical_core_order": list(range(7)),
            "core_role_blocks": CORE_ROLE_BLOCKS,
            "fragile_centers": list(FRAGILE_CENTERS),
            "required_witnesses": {
                str(center): sorted(REQUIRED_WITNESSES[center])
                for center in FRAGILE_CENTERS
            },
        },
        "search_contract": {
            "n": N,
            "added_halo_count": HALO_COUNT,
            "canonical_placement_rule": (
                "nondecreasing three-element multisets of the seven core gaps"
            ),
            "row_size": ROW_SIZE,
            "row_intersection_cap": PAIR_CAP,
            "two_overlap_rule": "the center-pair and witness-pair chords cross",
            "witness_pair_multiplicity_cap": PAIR_CAP,
            "selected_indegree_cap": engine.max_indegree,
            "retained_cover_rules": ["covers_all_labels", "essential_matching"],
            "extension_rule": "one selected four-witness row at every center",
            "vertex_circle_rule": (
                "reject selected-distance quotient self-edges and strict cycles "
                "after every extension row"
            ),
            "search_order": (
                "fixed retained centers, then minimum-remaining-options center "
                "with lexicographic row masks"
            ),
            "search_exhaustive": True,
        },
        "placement_count": len(placements),
        "placements": placements,
        "aggregate": aggregate,
        "representative_obstructions": representatives,
        "catalog_trace_sha256": catalog_digest,
        "summary": {
            "canonical_three_halo_placement_count": len(placements),
            "raw_retained_row_combination_count": aggregate[
                "raw_row_combination_count"
            ],
            "essential_retained_cover_count": aggregate["essential_cover_count"],
            "full_vertex_circle_survivor_count": aggregate[
                "full_vertex_circle_survivor_count"
            ],
            "all_three_halo_placements_exhausted": len(placements)
            == EXPECTED_PLACEMENT_COUNT,
            "fixed_three_halo_slice_closed": aggregate[
                "full_vertex_circle_survivor_count"
            ]
            == 0,
        },
        "limitations": [
            "The scan assumes the retained 23=27 quotient core and exactly three formal halo roles.",
            "It does not force that core or its retained rows from minimal-counterexample geometry.",
            "It does not cover four or more halo roles or arbitrary genuine halo incidence.",
            "Vertex-circle obstruction is an abstract necessary-condition diagnostic, not Euclidean realizability.",
            "No proof of n=10, general proof, counterexample, or official/global status update is claimed.",
        ],
        "conclusion": CONCLUSION,
        "provenance": PROVENANCE,
    }


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Check the stable bounded-claim anchors of a generated or stored payload."""

    assert payload["schema"] == SCHEMA
    assert payload["status"] == STATUS
    assert payload["trust"] == TRUST
    assert payload["claim_scope"] == CLAIM_SCOPE
    assert payload["placement_count"] == EXPECTED_PLACEMENT_COUNT
    aggregate = payload["aggregate"]
    assert (
        aggregate["raw_row_combination_count"]
        == EXPECTED_RAW_ROW_COMBINATION_COUNT
    )
    assert aggregate["essential_cover_count"] == EXPECTED_ESSENTIAL_COVER_COUNT
    assert (
        aggregate["pair_and_crossing_compatible_count"]
        == EXPECTED_PAIR_AND_CROSSING_COUNT
    )
    assert (
        aggregate["pair_capacity_compatible_count"]
        == EXPECTED_PAIR_AND_CROSSING_COUNT
    )
    assert aggregate["cover_count"] == EXPECTED_ESSENTIAL_COVER_COUNT
    for status, expected in EXPECTED_RETAINED_COVER_STATUS_COUNTS.items():
        assert aggregate[f"retained_cover_{status}_count"] == expected
    assert (
        aggregate["extension_candidate_count"]
        == EXPECTED_EXTENSION_CANDIDATE_COUNT
    )
    assert aggregate["extension_dead_end_count"] == EXPECTED_EXTENSION_DEAD_END_COUNT
    assert (
        aggregate["extension_candidate_status_counts"]
        == EXPECTED_EXTENSION_STATUS_COUNTS
    )
    assert (
        aggregate["full_vertex_circle_survivor_count"]
        == EXPECTED_FULL_SURVIVOR_COUNT
    )
    assert payload["summary"]["all_three_halo_placements_exhausted"] is True
    assert payload["summary"]["fixed_three_halo_slice_closed"] is True
    assert payload["catalog_trace_sha256"] == EXPECTED_CATALOG_TRACE_SHA256
    assert set(payload["representative_obstructions"]) == {
        "self_edge",
        "strict_cycle",
    }
    for status, representative in payload["representative_obstructions"].items():
        assert representative["optimized_status"] == status
        assert representative["independent_replay"]["status"] == status
        assert representative["independent_replay"]["obstructed"] is True
    assert payload["conclusion"] == CONCLUSION
    assert payload["provenance"] == PROVENANCE
