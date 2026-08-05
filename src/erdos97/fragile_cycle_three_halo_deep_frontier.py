"""Compact deep-frontier certificate for the fixed three-halo closure.

The complete three-halo search has only thirteen vertex-circle-clean states
with eight selected rows.  This module extracts those states exactly and
replays the final search layer: eleven have an incidence-dead remaining
center, while two force one ninth row and immediately expose a three-row
vertex-circle obstruction.

This is a compression of one bounded abstract search.  It does not force the
source quotient from geometry, handle arbitrary halos, or prove n=10.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import combinations, combinations_with_replacement
import json
from typing import Any, Mapping, Sequence

from erdos97.fragile_cycle_halo_lift_frontier import cyclic_order_for_gaps
from erdos97.fragile_cycle_three_halo_vertex_circle import (
    EXPECTED_CATALOG_TRACE_SHA256 as SOURCE_CATALOG_TRACE_SHA256,
    N,
    SCHEMA as SOURCE_SCHEMA,
    _placement_scan,
)
from erdos97.generic_vertex_search import Assignment, GenericVertexSearch
from erdos97.vertex_circle_quotient_replay import (
    SelectedRow,
    replay_vertex_circle_quotient,
    result_to_json,
)


SCHEMA = "erdos97.fragile_cycle_three_halo_deep_frontier.v1"
STATUS = "EXACT_BOUNDED_THREE_HALO_DEEP_FRONTIER_COMPRESSION"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact bounded compression of the final two search layers in the fixed "
    "three-halo n=10 scan for the 23=27 seven-role quotient core. It extracts "
    "all vertex-circle-clean eight-row states, certifies incidence dead ends "
    "or forced ninth rows, and independently replays the resulting minimum "
    "three-row quotient obstructions. Not Euclidean realizability, not a "
    "fragile-cycle forcing lemma, not a proof of n=10, not a general proof, "
    "not a counterexample, and not an official/global status update."
)
CONCLUSION = (
    "The complete fixed three-halo search has exactly thirteen clean eight-row "
    "frontier states in seven placements. Eleven have a remaining center with "
    "no incidence-admissible row. Each of the other two has a unique "
    "minimum-remaining-options ninth row, and that row creates an exact "
    "vertex-circle obstruction containing a three-row core. This replaces the "
    "last two opaque search layers by a compact replayable packet but does not "
    "supply the missing geometric forcing lemma."
)
PROVENANCE = {
    "generator": "scripts/check_fragile_cycle_three_halo_deep_frontier.py",
    "command": (
        "python scripts/check_fragile_cycle_three_halo_deep_frontier.py "
        "--write --assert-expected"
    ),
}

EXPECTED_DEPTH_STATUS_PROFILE = {
    "4": {"ok": 120_690, "self_edge": 5_544, "strict_cycle": 15_516},
    "5": {"ok": 116_374, "self_edge": 28_179, "strict_cycle": 87_592},
    "6": {"ok": 27_054, "self_edge": 53_837, "strict_cycle": 80_165},
    "7": {"ok": 1_273, "self_edge": 13_584, "strict_cycle": 11_992},
    "8": {"ok": 13, "self_edge": 406, "strict_cycle": 211},
    "9": {"ok": 0, "self_edge": 2, "strict_cycle": 0},
}
EXPECTED_DEEP_STATE_COUNT = 13
EXPECTED_DEEP_PLACEMENT_COUNT = 7
EXPECTED_DIHEDRAL_CLASS_COUNT = 13
EXPECTED_INCIDENCE_DEAD_STATE_COUNT = 11
EXPECTED_FORCED_NINTH_STATE_COUNT = 2
EXPECTED_MINIMUM_CORE_WIDTH = 3
EXPECTED_MINIMUM_CORE_COUNT = 6
EXPECTED_MINIMUM_CORE_STATUS_COUNTS = {"self_edge": 2, "strict_cycle": 4}
EXPECTED_INCIDENCE_REJECTION_TOTALS = {
    "row_intersection_or_crossing": 1_386,
    "selected_indegree_capacity": 0,
    "witness_pair_capacity": 0,
    "viable": 0,
}

EXPECTED_DEEP_FRONTIER_SHA256 = (
    "73e1cabd1670fddd3452bba72c80880f3eeebbc574a4873de3905a1c33781765"
)

StateKey = tuple[tuple[int, int], ...]


def _state_key(assignment: Mapping[int, int]) -> StateKey:
    return tuple(sorted((int(center), int(mask)) for center, mask in assignment.items()))


def _mask(values: Sequence[int]) -> int:
    out = 0
    for value in values:
        out |= 1 << int(value)
    return out


def _selected_rows(
    engine: GenericVertexSearch,
    assignment: Mapping[int, int],
) -> list[SelectedRow]:
    rows: list[SelectedRow] = []
    for center, mask in sorted(assignment.items()):
        bits = engine.mask_bits[mask]
        if len(bits) != 4:
            raise AssertionError("selected row must contain four witnesses")
        rows.append(
            SelectedRow(
                center=center,
                witnesses=(bits[0], bits[1], bits[2], bits[3]),
            )
        )
    return rows


def _compact_rows(rows: Sequence[SelectedRow]) -> list[list[int]]:
    return [[row.center, *row.witnesses] for row in rows]


def _original_rows(
    engine: GenericVertexSearch,
    assignment: Mapping[int, int],
    order: Sequence[int],
) -> list[list[int]]:
    return [
        [
            int(order[center]),
            *sorted(int(order[witness]) for witness in engine.mask_bits[mask]),
        ]
        for center, mask in sorted(assignment.items())
    ]


def _counts_for_assignment(
    engine: GenericVertexSearch,
    assignment: Mapping[int, int],
) -> tuple[list[int], list[int]]:
    column_counts = [0] * engine.n
    witness_pair_counts = [0] * len(engine.pairs)
    for mask in assignment.values():
        for target in engine.mask_bits[mask]:
            column_counts[target] += 1
        for pair_index in engine.row_pair_indices[mask]:
            witness_pair_counts[pair_index] += 1
    return column_counts, witness_pair_counts


def _option_rejection_ledger(
    engine: GenericVertexSearch,
    center: int,
    assignment: Mapping[int, int],
    column_counts: Sequence[int],
    witness_pair_counts: Sequence[int],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for mask in engine.options[center]:
        if not all(
            engine.rows_compatible(center, mask, other, other_mask)
            for other, other_mask in assignment.items()
        ):
            counts["row_intersection_or_crossing"] += 1
        elif any(
            column_counts[target] >= engine.max_indegree
            for target in engine.mask_bits[mask]
        ):
            counts["selected_indegree_capacity"] += 1
        elif any(
            witness_pair_counts[pair_index] >= engine.pair_cap
            for pair_index in engine.row_pair_indices[mask]
        ):
            counts["witness_pair_capacity"] += 1
        else:
            counts["viable"] += 1
    return {
        key: counts[key]
        for key in (
            "row_intersection_or_crossing",
            "selected_indegree_capacity",
            "witness_pair_capacity",
            "viable",
        )
    }


def _base_status(
    engine: GenericVertexSearch,
    assignment: Mapping[int, int],
) -> str:
    return GenericVertexSearch.vertex_circle_status(engine, dict(assignment))


def _minimum_obstruction_cores(
    engine: GenericVertexSearch,
    assignment: Mapping[int, int],
) -> list[dict[str, Any]]:
    centers = sorted(assignment)
    for width in range(1, len(centers) + 1):
        cores: list[dict[str, Any]] = []
        for subset in combinations(centers, width):
            core = {center: assignment[center] for center in subset}
            status = _base_status(engine, core)
            if status == "ok":
                continue
            rows = _selected_rows(engine, core)
            replay = replay_vertex_circle_quotient(N, tuple(range(N)), rows)
            if replay.status != status:
                raise AssertionError("optimized/minimum-core replay mismatch")
            cores.append(
                {
                    "centers": list(subset),
                    "status": status,
                    "selected_rows": _compact_rows(rows),
                    "independent_replay": result_to_json(replay),
                }
            )
        if cores:
            return cores
    raise AssertionError("obstructed assignment has no obstructed row subset")


def _dihedral_state_key(engine: GenericVertexSearch, state: StateKey) -> StateKey:
    candidates: list[StateKey] = []
    for direction in (1, -1):
        for shift in range(engine.n):
            transformed: list[tuple[int, int]] = []
            for center, mask in state:
                new_center = (direction * center + shift) % engine.n
                new_witnesses = [
                    (direction * witness + shift) % engine.n
                    for witness in engine.mask_bits[mask]
                ]
                transformed.append((new_center, _mask(new_witnesses)))
            candidates.append(tuple(sorted(transformed)))
    return min(candidates)


class _DeepFrontierSearch(GenericVertexSearch):
    def __init__(self) -> None:
        super().__init__(N)
        self.current_gaps: tuple[int, ...] = ()
        self.status_by_depth: Counter[tuple[int, str]] = Counter()
        self.clean_eight_states: dict[StateKey, tuple[int, ...]] = {}
        self.obstructed_nine_states: dict[StateKey, tuple[tuple[int, ...], str]] = {}

    def vertex_circle_status(self, assign: Assignment) -> str:
        status = super().vertex_circle_status(assign)
        self.status_by_depth[(len(assign), status)] += 1
        state = _state_key(assign)
        if len(assign) == 8 and status == "ok":
            previous = self.clean_eight_states.setdefault(state, self.current_gaps)
            if previous != self.current_gaps:
                raise AssertionError("deep state reached in two halo placements")
        if len(assign) == 9 and status != "ok":
            value = (self.current_gaps, status)
            previous = self.obstructed_nine_states.setdefault(state, value)
            if previous != value:
                raise AssertionError("ninth-row obstruction replay drift")
        return status


def _validate_source(source: Mapping[str, Any]) -> None:
    if source.get("schema") != SOURCE_SCHEMA:
        raise ValueError("unexpected three-halo source schema")
    if source.get("catalog_trace_sha256") != SOURCE_CATALOG_TRACE_SHA256:
        raise ValueError("unexpected three-halo source trace")
    summary = source.get("summary")
    if not isinstance(summary, Mapping):
        raise ValueError("three-halo source summary must be an object")
    if summary.get("fixed_three_halo_slice_closed") is not True:
        raise ValueError("three-halo source slice is not recorded closed")


def deep_frontier_payload(source: Mapping[str, Any]) -> dict[str, Any]:
    """Regenerate the exact deep frontier and its compact terminal packets."""

    _validate_source(source)
    engine = _DeepFrontierSearch()
    placement_results: list[dict[str, Any]] = []
    representatives: dict[str, dict[str, Any]] = {}
    for gaps in combinations_with_replacement(range(7), 3):
        engine.current_gaps = gaps
        placement_results.append(_placement_scan(engine, gaps, representatives))

    reproduced_source_trace = sha256(
        "\n".join(
            f"{','.join(map(str, placement['halo_gaps']))}:{placement['trace_sha256']}"
            for placement in placement_results
        ).encode()
    ).hexdigest()
    if reproduced_source_trace != SOURCE_CATALOG_TRACE_SHA256:
        raise AssertionError("instrumented scan differs from source trace")

    canonical_keys = sorted(
        {_dihedral_state_key(engine, state) for state in engine.clean_eight_states}
    )
    class_id_by_key = {
        key: f"D{index:02d}" for index, key in enumerate(canonical_keys, start=1)
    }

    records: list[dict[str, Any]] = []
    all_minimum_cores: list[dict[str, Any]] = []
    incidence_rejection_totals: Counter[str] = Counter()
    ordered_states = sorted(
        engine.clean_eight_states.items(), key=lambda item: (item[1], item[0])
    )
    for index, (state, gaps) in enumerate(ordered_states, start=1):
        assignment = dict(state)
        order = cyclic_order_for_gaps(gaps)
        rows = _selected_rows(engine, assignment)
        replay = replay_vertex_circle_quotient(N, tuple(range(N)), rows)
        if replay.status != "ok":
            raise AssertionError("stored deep state is not independently clean")
        column_counts, witness_pair_counts = _counts_for_assignment(
            engine, assignment
        )
        remaining = sorted(set(range(N)) - set(assignment))
        options = {
            center: engine.valid_options_for_center(
                center,
                assignment,
                column_counts,
                witness_pair_counts,
            )
            for center in remaining
        }
        option_counts = {str(center): len(options[center]) for center in remaining}
        dead_centers = [center for center in remaining if not options[center]]
        record: dict[str, Any] = {
            "state_id": f"S{index:02d}",
            "dihedral_class_id": class_id_by_key[
                _dihedral_state_key(engine, state)
            ],
            "halo_gaps": list(gaps),
            "cyclic_order": list(order),
            "selected_rows_natural_order": _compact_rows(rows),
            "selected_rows_original_labels": _original_rows(
                engine, assignment, order
            ),
            "remaining_centers_natural_order": remaining,
            "remaining_centers_original_labels": [order[center] for center in remaining],
            "admissible_row_option_counts": option_counts,
            "independent_clean_replay": result_to_json(replay),
        }
        if dead_centers:
            center = dead_centers[0]
            ledger = _option_rejection_ledger(
                engine,
                center,
                assignment,
                column_counts,
                witness_pair_counts,
            )
            if ledger["viable"] != 0 or sum(ledger.values()) != len(
                engine.options[center]
            ):
                raise AssertionError("incidence dead-end ledger mismatch")
            incidence_rejection_totals.update(ledger)
            record.update(
                {
                    "terminal_type": "incidence_dead_end",
                    "dead_centers_natural_order": dead_centers,
                    "dead_centers_original_labels": [
                        order[dead_center] for dead_center in dead_centers
                    ],
                    "certificate_center_natural_order": center,
                    "certificate_center_original_label": order[center],
                    "certificate_option_count": len(engine.options[center]),
                    "option_rejection_ledger": ledger,
                }
            )
        else:
            forced_center = min(remaining, key=lambda center: (len(options[center]), center))
            forced_options = options[forced_center]
            if len(forced_options) != 1:
                raise AssertionError("deep live state does not force one MRV row")
            attempted = dict(assignment)
            attempted[forced_center] = forced_options[0]
            status = _base_status(engine, attempted)
            if status == "ok":
                raise AssertionError("forced ninth row unexpectedly remains clean")
            attempted_state = _state_key(attempted)
            captured = engine.obstructed_nine_states.get(attempted_state)
            if captured != (gaps, status):
                raise AssertionError("forced ninth row missing from source traversal")
            attempted_rows = _selected_rows(engine, attempted)
            attempted_replay = replay_vertex_circle_quotient(
                N, tuple(range(N)), attempted_rows
            )
            if attempted_replay.status != status:
                raise AssertionError("forced ninth-row replay mismatch")
            minimum_cores = _minimum_obstruction_cores(engine, attempted)
            for core_index, core in enumerate(minimum_cores, start=1):
                core_record = {
                    "core_id": f"{record['state_id']}-C{core_index:02d}",
                    "source_state_id": record["state_id"],
                    **core,
                }
                all_minimum_cores.append(core_record)
            record.update(
                {
                    "terminal_type": "forced_ninth_row_obstruction",
                    "forced_center_natural_order": forced_center,
                    "forced_center_original_label": order[forced_center],
                    "forced_row_natural_order": [
                        forced_center,
                        *engine.mask_bits[forced_options[0]],
                    ],
                    "forced_row_original_labels": [
                        order[forced_center],
                        *sorted(order[witness] for witness in engine.mask_bits[forced_options[0]]),
                    ],
                    "forced_assignment_status": status,
                    "forced_assignment_replay": result_to_json(attempted_replay),
                    "minimum_obstruction_width": len(minimum_cores[0]["centers"]),
                    "minimum_obstruction_core_ids": [
                        core["core_id"] for core in all_minimum_cores if core["source_state_id"] == record["state_id"]
                    ],
                }
            )
        records.append(record)

    profile = {
        str(depth): {
            status: engine.status_by_depth[(depth, status)]
            for status in ("ok", "self_edge", "strict_cycle")
        }
        for depth in range(4, 10)
    }
    terminal_counts = Counter(record["terminal_type"] for record in records)
    core_status_counts = Counter(core["status"] for core in all_minimum_cores)
    deep_placements = sorted({tuple(record["halo_gaps"]) for record in records})
    catalog_material = {
        "depth_status_profile": profile,
        "deep_frontier_states": records,
        "minimum_obstruction_cores": all_minimum_cores,
    }
    catalog_digest = sha256(
        json.dumps(
            catalog_material,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifact": {
            "path": "data/certificates/fragile_cycle_three_halo_vertex_circle.json",
            "schema": SOURCE_SCHEMA,
            "catalog_trace_sha256": SOURCE_CATALOG_TRACE_SHA256,
            "instrumented_replay_trace_sha256": reproduced_source_trace,
        },
        "search_contract": {
            "deep_frontier_depth": 8,
            "terminal_replay_depth": 9,
            "natural_cyclic_order": list(range(N)),
            "incidence_filters": [
                "row_intersection_and_two_overlap_crossing",
                "selected_indegree_capacity",
                "witness_pair_capacity",
            ],
            "remaining_center_rule": "minimum option count, then center label",
            "minimum_core_rule": (
                "exhaust row subsets in increasing width and retain every "
                "obstructed subset at the first nonempty width"
            ),
            "search_exhaustive": True,
        },
        "depth_status_profile": profile,
        "deep_placement_count": len(deep_placements),
        "deep_placements": [list(gaps) for gaps in deep_placements],
        "deep_frontier_state_count": len(records),
        "dihedral_class_count": len(canonical_keys),
        "deep_frontier_states": records,
        "minimum_obstruction_core_count": len(all_minimum_cores),
        "minimum_obstruction_core_status_counts": {
            status: core_status_counts[status]
            for status in ("self_edge", "strict_cycle")
        },
        "minimum_obstruction_cores": all_minimum_cores,
        "incidence_rejection_totals": {
            key: incidence_rejection_totals[key]
            for key in (
                "row_intersection_or_crossing",
                "selected_indegree_capacity",
                "witness_pair_capacity",
                "viable",
            )
        },
        "deep_frontier_catalog_sha256": catalog_digest,
        "summary": {
            "clean_eight_row_state_count": len(records),
            "clean_eight_row_placement_count": len(deep_placements),
            "clean_eight_row_dihedral_class_count": len(canonical_keys),
            "incidence_dead_state_count": terminal_counts["incidence_dead_end"],
            "forced_ninth_row_state_count": terminal_counts[
                "forced_ninth_row_obstruction"
            ],
            "minimum_forced_obstruction_core_width": min(
                len(core["centers"]) for core in all_minimum_cores
            ),
            "maximum_forced_obstruction_core_width": max(
                len(core["centers"]) for core in all_minimum_cores
            ),
            "all_deep_states_terminal": len(records)
            == terminal_counts["incidence_dead_end"]
            + terminal_counts["forced_ninth_row_obstruction"],
            "all_forced_ninth_rows_obstructed": all(
                record["forced_assignment_status"] != "ok"
                for record in records
                if record["terminal_type"] == "forced_ninth_row_obstruction"
            ),
            "all_minimum_cores_independently_replayed": all(
                core["independent_replay"]["status"] == core["status"]
                for core in all_minimum_cores
            ),
        },
        "limitations": [
            "The packet compresses only the fixed three-halo source search and inherits its assumptions.",
            "It does not force the 23=27 quotient core or any selected row from geometry.",
            "The thirteen deep states are dihedrally distinct; the packet is a local catalog, not one universal row template.",
            "Incidence dead ends use the selected-row filters of the source search, not Euclidean realizability.",
            "No proof of n=10, general proof, counterexample, or official/global status update is claimed.",
        ],
        "conclusion": CONCLUSION,
        "provenance": PROVENANCE,
    }


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Check the stable exact anchors of the generated or stored packet."""

    assert payload["schema"] == SCHEMA
    assert payload["status"] == STATUS
    assert payload["trust"] == TRUST
    assert payload["claim_scope"] == CLAIM_SCOPE
    assert payload["depth_status_profile"] == EXPECTED_DEPTH_STATUS_PROFILE
    assert payload["deep_frontier_state_count"] == EXPECTED_DEEP_STATE_COUNT
    assert payload["deep_placement_count"] == EXPECTED_DEEP_PLACEMENT_COUNT
    assert payload["dihedral_class_count"] == EXPECTED_DIHEDRAL_CLASS_COUNT
    summary = payload["summary"]
    assert (
        summary["incidence_dead_state_count"]
        == EXPECTED_INCIDENCE_DEAD_STATE_COUNT
    )
    assert (
        summary["forced_ninth_row_state_count"]
        == EXPECTED_FORCED_NINTH_STATE_COUNT
    )
    assert summary["minimum_forced_obstruction_core_width"] == EXPECTED_MINIMUM_CORE_WIDTH
    assert summary["maximum_forced_obstruction_core_width"] == EXPECTED_MINIMUM_CORE_WIDTH
    assert payload["minimum_obstruction_core_count"] == EXPECTED_MINIMUM_CORE_COUNT
    assert (
        payload["minimum_obstruction_core_status_counts"]
        == EXPECTED_MINIMUM_CORE_STATUS_COUNTS
    )
    assert (
        payload["incidence_rejection_totals"]
        == EXPECTED_INCIDENCE_REJECTION_TOTALS
    )
    assert summary["all_deep_states_terminal"] is True
    assert summary["all_forced_ninth_rows_obstructed"] is True
    assert summary["all_minimum_cores_independently_replayed"] is True
    assert (
        payload["deep_frontier_catalog_sha256"] == EXPECTED_DEEP_FRONTIER_SHA256
    )
    assert payload["conclusion"] == CONCLUSION
    assert payload["provenance"] == PROVENANCE
