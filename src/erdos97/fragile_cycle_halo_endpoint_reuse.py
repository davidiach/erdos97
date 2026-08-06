"""One-row endpoint-reuse negative control for large fragile-cycle halos.

The fixed ``23=27`` core has four retained critical T4 rows.  The deletion
crosswalk finds retained-exclusive mutual pairs in 310,320 of its four- and
five-halo covers.  This module exhausts that triggered branch and asks whether
the pair can be broken by one additional selected four-witness row while
preserving the current incidence, crossing, witness-pair-capacity, and
vertex-circle necessary conditions.

This is a bounded partial-row compatibility test.  A surviving row is not a
full selected extension, an exact rich-class profile, or a Euclidean
realization.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, combinations_with_replacement
import json
from typing import Any, Mapping, Sequence

from erdos97.fragile_cycle_halo_deletion_crosswalk import (
    EXPECTED_CROSSWALK as DELETION_EXPECTED_CROSSWALK,
    retained_exclusive_pairs,
)
from erdos97.fragile_cycle_halo_lift_frontier import (
    CORE_ORDER,
    FRAGILE_CENTERS,
    PAIR_CAP,
    REQUIRED_WITNESSES,
    _pair,
    _selected_pair_ok,
    cyclic_order_for_gaps,
)
from erdos97.fragile_cycle_halo_slot_budget import _coverage_multisets
from erdos97.fragile_hypergraph import essential_row_matching
from erdos97.generic_vertex_search import GenericVertexSearch


SCHEMA = "erdos97.fragile_cycle_halo_endpoint_reuse.v1"
STATUS = "EXACT_BOUNDED_HALO_ENDPOINT_REUSE_NEGATIVE_CONTROL"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact one-row negative control for every retained-exclusive four/five-"
    "halo cover of the fixed 23=27 core. Each of the 310320 triggered covers "
    "admits an outside-center selected four-witness row that contains an "
    "exclusive-pair endpoint and preserves the retained incidence, crossing, "
    "witness-pair-capacity, and natural-order vertex-circle constraints. This "
    "shows those necessary conditions do not force the T5/T44 branch. It does "
    "not construct an exact T4 rich class, a full selected extension, or a "
    "Euclidean realization; force the core; prove n=11, n=12, or the general "
    "problem; give a counterexample; or update official/global status."
)
CONCLUSION = (
    "All 144000 triggered four-halo covers and all 166320 triggered five-halo "
    "covers admit a compatible endpoint-reuse selected row with vertex-circle "
    "status ok. Fixed preferred core centers supply 136043 and 165012 of the "
    "witnesses; alternate outside centers supply the remaining 7957 and 1308. "
    "Thus retained exclusivity plus the checked one-row necessary conditions "
    "cannot force a T5/T44 deletion certifier. Further progress needs full-"
    "extension constraints, exact rich-class information, critical-radius or "
    "ordinary-distance geometry, or a separate forcing lemma."
)
PROVENANCE = {
    "generator": "scripts/check_fragile_cycle_halo_endpoint_reuse.py",
    "command": (
        "python scripts/check_fragile_cycle_halo_endpoint_reuse.py "
        "--write --assert-expected --summary-json"
    ),
}

EXPECTED_CENSUS: dict[int, dict[str, Any]] = {
    4: {
        "placement_count": 210,
        "essential_cover_count": 529_200,
        "exclusive_trigger_cover_count": 144_000,
        "pair_free_cover_count": 385_200,
        "exclusive_pair_identity_histogram": {
            "1-3": 41_760,
            "1-6": 52_920,
            "3-6": 49_320,
        },
        "retained_vertex_circle_ok_count": 144_000,
        "endpoint_reuse_survivor_count": 144_000,
        "preferred_center_survivor_count": 136_043,
        "alternate_center_survivor_count": 7_957,
        "no_survivor_count": 0,
        "chosen_center_histogram": {
            "0": 45_551,
            "2": 95_688,
            "5": 4,
            "7": 2_687,
            "8": 66,
            "9": 4,
        },
        "chosen_endpoint_count_histogram": {"1": 105_041, "2": 38_959},
        "placement_trace_sha256": "364e803294ac55594b1c5a3a9e5145628f7fd32dbecd242d2d7666681983ca30",
    },
    5: {
        "placement_count": 462,
        "essential_cover_count": 512_820,
        "exclusive_trigger_cover_count": 166_320,
        "pair_free_cover_count": 346_500,
        "exclusive_pair_identity_histogram": {
            "1-3": 55_440,
            "1-6": 55_440,
            "3-6": 55_440,
        },
        "retained_vertex_circle_ok_count": 166_320,
        "endpoint_reuse_survivor_count": 166_320,
        "preferred_center_survivor_count": 165_012,
        "alternate_center_survivor_count": 1_308,
        "no_survivor_count": 0,
        "chosen_center_histogram": {"0": 54_132, "2": 111_432, "7": 756},
        "chosen_endpoint_count_histogram": {"1": 143_030, "2": 23_290},
        "placement_trace_sha256": "7aca29fa5bc8bf98c829a6f9d619d395cc91ec535022c50d0ed82eb928b3bd80",
    },
}

PREFERRED_CENTER = {(1, 3): 2, (1, 6): 2, (3, 6): 0}

Rows = dict[int, tuple[int, ...]]
Pair = tuple[int, int]
Candidate = tuple[tuple[int, ...], int, tuple[Pair, ...]]


@lru_cache(maxsize=2)
def _vertex_engine(n: int) -> GenericVertexSearch:
    return GenericVertexSearch(n, row_size=4, pair_cap=PAIR_CAP)


def _row_mask(row: Sequence[int], positions: Mapping[int, int]) -> int:
    return sum(1 << positions[int(label)] for label in row)


def _rows_json(rows: Mapping[int, Sequence[int]]) -> list[list[int]]:
    return [
        [center, *sorted(int(label) for label in rows[center])]
        for center in sorted(rows)
    ]


def _candidate_catalog(
    order: Sequence[int],
    positions: Mapping[int, int],
    pair: Pair,
) -> dict[int, tuple[Candidate, ...]]:
    labels = set(int(label) for label in order)
    endpoints = set(pair)
    catalog: dict[int, tuple[Candidate, ...]] = {}
    for center in order:
        if center in FRAGILE_CENTERS:
            continue
        records: list[Candidate] = []
        for row in combinations(sorted(labels - {center}), 4):
            if endpoints.isdisjoint(row):
                continue
            records.append(
                (
                    row,
                    _row_mask(row, positions),
                    tuple(_pair(left, right) for left, right in combinations(row, 2)),
                )
            )
        catalog[int(center)] = tuple(records)
    return catalog


def _endpoint_reuse_witness(
    engine: GenericVertexSearch,
    order: Sequence[int],
    rows: Mapping[int, Sequence[int]],
    pair_counts: Mapping[Pair, int],
    exclusive_pair: Pair,
    catalog: Mapping[int, Sequence[Candidate]],
) -> dict[str, Any] | None:
    positions = {int(label): index for index, label in enumerate(order)}
    assignment = {
        positions[int(center)]: _row_mask(row, positions)
        for center, row in rows.items()
    }
    preferred = PREFERRED_CENTER[exclusive_pair]
    centers = [preferred, *(
        int(center)
        for center in order
        if center not in FRAGILE_CENTERS and center != preferred
    )]
    endpoints = set(exclusive_pair)
    for center in centers:
        center_position = positions[center]
        for row, mask, row_pairs in catalog[center]:
            if not all(
                engine.rows_compatible(
                    center_position,
                    mask,
                    positions[int(other)],
                    assignment[positions[int(other)]],
                )
                for other in rows
            ):
                continue
            if any(pair_counts.get(pair, 0) >= PAIR_CAP for pair in row_pairs):
                continue
            extended = dict(assignment)
            extended[center_position] = mask
            if engine.vertex_circle_status(extended) != "ok":
                continue
            return {
                "center": center,
                "row": list(row),
                "selection_kind": (
                    "preferred_core_center"
                    if center == preferred
                    else "alternate_outside_center"
                ),
                "exclusive_endpoint_count": len(endpoints.intersection(row)),
                "vertex_circle_status": "ok",
            }
    return None


def find_endpoint_reuse_witness(
    order: Sequence[int],
    rows: Mapping[int, Sequence[int]],
    exclusive_pair: Sequence[int],
) -> dict[str, Any] | None:
    """Return the deterministic first compatible endpoint-reuse row, if any."""

    normalized_pair = tuple(sorted(int(label) for label in exclusive_pair))
    if normalized_pair not in PREFERRED_CENTER:
        raise ValueError("exclusive_pair must be one of 1-3, 1-6, or 3-6")
    normalized_rows = {
        int(center): tuple(sorted(int(label) for label in row))
        for center, row in rows.items()
    }
    if retained_exclusive_pairs(normalized_rows, order) != (normalized_pair,):
        raise ValueError("rows do not have the supplied unique retained-exclusive pair")
    positions = {int(label): index for index, label in enumerate(order)}
    engine = _vertex_engine(len(order))
    pair_counts: Counter[Pair] = Counter(
        _pair(left, right)
        for row in normalized_rows.values()
        for left, right in combinations(row, 2)
    )
    return _endpoint_reuse_witness(
        engine,
        order,
        normalized_rows,
        pair_counts,
        normalized_pair,
        _candidate_catalog(order, positions, normalized_pair),
    )


def _representative(
    gaps: Sequence[int],
    order: Sequence[int],
    rows: Mapping[int, Sequence[int]],
    exclusive_pair: Pair,
    witness: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "halo_gaps": list(gaps),
        "cyclic_order": list(order),
        "retained_rows": _rows_json(rows),
        "retained_exclusive_pair": list(exclusive_pair),
        "endpoint_reuse_witness": dict(witness),
    }


def _placement_scan(
    gaps: tuple[int, ...], engine: GenericVertexSearch
) -> dict[str, Any]:
    order = cyclic_order_for_gaps(gaps)
    positions = {int(label): index for index, label in enumerate(order)}
    labels = frozenset(order)
    assigned: Rows = {}
    pair_counts: Counter[Pair] = Counter()
    counts: Counter[str] = Counter()
    pair_histogram: Counter[str] = Counter()
    center_histogram: Counter[str] = Counter()
    endpoint_count_histogram: Counter[str] = Counter()
    representatives: dict[str, dict[str, Any]] = {}
    catalogs: dict[Pair, dict[int, tuple[Candidate, ...]]] = {}

    def record() -> None:
        _, unmatched = essential_row_matching(len(order), assigned)
        if unmatched:
            return
        counts["essential_cover_count"] += 1
        exclusive = retained_exclusive_pairs(assigned, order)
        if not exclusive:
            counts["pair_free_cover_count"] += 1
            return
        pair = exclusive[0]
        counts["exclusive_trigger_cover_count"] += 1
        pair_histogram[f"{pair[0]}-{pair[1]}"] += 1
        if pair not in catalogs:
            catalogs[pair] = _candidate_catalog(order, positions, pair)
        catalog = catalogs[pair]
        witness = _endpoint_reuse_witness(
            engine, order, assigned, pair_counts, pair, catalog
        )
        if witness is None:
            counts["no_survivor_count"] += 1
            return
        counts["retained_vertex_circle_ok_count"] += 1
        counts["endpoint_reuse_survivor_count"] += 1
        selection_kind = str(witness["selection_kind"])
        counts[
            "preferred_center_survivor_count"
            if selection_kind == "preferred_core_center"
            else "alternate_center_survivor_count"
        ] += 1
        center_histogram[str(witness["center"])] += 1
        endpoint_count_histogram[str(witness["exclusive_endpoint_count"])] += 1
        key = f"{selection_kind}_pair_{pair[0]}_{pair[1]}"
        representatives.setdefault(
            key, _representative(gaps, order, assigned, pair, witness)
        )

    def search(index: int, remaining: Counter[int]) -> None:
        if index == len(FRAGILE_CENTERS):
            record()
            return
        center = FRAGILE_CENTERS[index]
        available = sorted(
            label
            for label, multiplicity in remaining.items()
            if multiplicity
            and label != center
            and label not in REQUIRED_WITNESSES[center]
        )
        for left, right in combinations(available, 2):
            row = tuple(sorted((*REQUIRED_WITNESSES[center], left, right)))
            if not all(
                _selected_pair_ok(center, row, other, other_row, order)
                for other, other_row in assigned.items()
            ):
                continue
            row_pairs = [_pair(a, b) for a, b in combinations(row, 2)]
            if any(pair_counts[pair] >= PAIR_CAP for pair in row_pairs):
                continue
            remaining[left] -= 1
            remaining[right] -= 1
            assigned[center] = row
            for row_pair in row_pairs:
                pair_counts[row_pair] += 1
            search(index + 1, remaining)
            for row_pair in row_pairs:
                pair_counts[row_pair] -= 1
            del assigned[center]
            remaining[left] += 1
            remaining[right] += 1

    for _, multiset in _coverage_multisets(labels, len(gaps)):
        search(0, multiset)
    return {
        "halo_gaps": list(gaps),
        "counts": dict(sorted(counts.items())),
        "exclusive_pair_identity_histogram": dict(sorted(pair_histogram.items())),
        "chosen_center_histogram": dict(sorted(center_histogram.items())),
        "chosen_endpoint_count_histogram": dict(
            sorted(endpoint_count_histogram.items())
        ),
        "representatives": representatives,
    }


def _aggregate_halo_count(halo_count: int) -> dict[str, Any]:
    engine = _vertex_engine(7 + halo_count)
    aggregate_counts: Counter[str] = Counter()
    pair_histogram: Counter[str] = Counter()
    center_histogram: Counter[str] = Counter()
    endpoint_count_histogram: Counter[str] = Counter()
    representatives: dict[str, dict[str, Any]] = {}
    trace = sha256()
    placement_count = 0
    for gaps in combinations_with_replacement(CORE_ORDER, halo_count):
        placement = _placement_scan(gaps, engine)
        placement_count += 1
        aggregate_counts.update(placement["counts"])
        pair_histogram.update(placement["exclusive_pair_identity_histogram"])
        center_histogram.update(placement["chosen_center_histogram"])
        endpoint_count_histogram.update(
            placement["chosen_endpoint_count_histogram"]
        )
        for key, representative in placement["representatives"].items():
            representatives.setdefault(key, representative)
        trace.update(
            json.dumps(
                {
                    "gaps": placement["halo_gaps"],
                    "counts": placement["counts"],
                    "pairs": placement["exclusive_pair_identity_histogram"],
                    "centers": placement["chosen_center_histogram"],
                    "endpoint_counts": placement[
                        "chosen_endpoint_count_histogram"
                    ],
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        )
    result = {
        "halo_count": halo_count,
        "placement_count": placement_count,
        **{
            key: aggregate_counts[key]
            for key in (
                "essential_cover_count",
                "exclusive_trigger_cover_count",
                "pair_free_cover_count",
                "retained_vertex_circle_ok_count",
                "endpoint_reuse_survivor_count",
                "preferred_center_survivor_count",
                "alternate_center_survivor_count",
                "no_survivor_count",
            )
        },
        "exclusive_pair_identity_histogram": dict(sorted(pair_histogram.items())),
        "chosen_center_histogram": dict(sorted(center_histogram.items())),
        "chosen_endpoint_count_histogram": dict(
            sorted(endpoint_count_histogram.items())
        ),
        "placement_trace_sha256": trace.hexdigest(),
        "representatives": representatives,
    }
    source = DELETION_EXPECTED_CROSSWALK[halo_count]
    for key in (
        "placement_count",
        "essential_cover_count",
        "exclusive_trigger_cover_count",
        "pair_free_cover_count",
        "exclusive_pair_identity_histogram",
    ):
        if result[key] != source[key]:
            raise AssertionError(f"deletion-crosswalk source drift at {key}")
    return result


def halo_endpoint_reuse_payload() -> dict[str, Any]:
    """Build the complete deterministic endpoint-reuse negative control."""

    four = _aggregate_halo_count(4)
    five = _aggregate_halo_count(5)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_contract": {
            "quotient_identification": "23=27",
            "retained_centers": list(FRAGILE_CENTERS),
            "halo_counts": [4, 5],
            "exclusive_pairs": [list(pair) for pair in sorted(PREFERRED_CENTER)],
            "source_deletion_crosswalk_schema": (
                "erdos97.fragile_cycle_halo_deletion_crosswalk.v1"
            ),
        },
        "candidate_contract": {
            "candidate_center": "outside the four retained centers",
            "candidate_row_size": 4,
            "endpoint_reuse": "candidate row contains at least one endpoint",
            "checked_constraints": [
                "center excluded from its own row",
                "row intersection at most two",
                "two-overlap chords cross in the supplied cyclic order",
                "witness-pair multiplicity at most two",
                "natural-order vertex-circle quotient has no strict self-edge or cycle",
            ],
            "selected_indegree_note": (
                "automatic for a five-row partial system: indegree is at most "
                "five, below the n=11 cap six and n=12 cap seven"
            ),
            "preferred_centers": {
                f"{left}-{right}": center
                for (left, right), center in sorted(PREFERRED_CENTER.items())
            },
            "witness_selection": (
                "try the pair's preferred core center first, then remaining "
                "outside centers in cyclic order; within a center use the "
                "lexicographically first surviving four-set"
            ),
        },
        "four_halos": four,
        "five_halos": five,
        "summary": {
            "exclusive_trigger_cover_count": (
                four["exclusive_trigger_cover_count"]
                + five["exclusive_trigger_cover_count"]
            ),
            "endpoint_reuse_survivor_count": (
                four["endpoint_reuse_survivor_count"]
                + five["endpoint_reuse_survivor_count"]
            ),
            "preferred_center_survivor_count": (
                four["preferred_center_survivor_count"]
                + five["preferred_center_survivor_count"]
            ),
            "alternate_center_survivor_count": (
                four["alternate_center_survivor_count"]
                + five["alternate_center_survivor_count"]
            ),
            "no_survivor_count": (
                four["no_survivor_count"] + five["no_survivor_count"]
            ),
            "checked_constraints_force_richer_profile": False,
        },
        "limitations": [
            "The fixed 23=27 core and its four retained rows are assumed.",
            "A selected four-witness row is only a necessary combinatorial shadow of an exact T4 rich class.",
            "Only one added row is checked; no full selected-row extension is constructed.",
            "Vertex-circle feasibility is necessary, not a Euclidean realization certificate.",
            "The 731700 pair-free covers are outside this triggered-branch packet.",
            "No n=11, n=12, general-proof, counterexample, or official-status claim is made.",
        ],
        "conclusion": CONCLUSION,
        "provenance": PROVENANCE,
    }


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable census totals and the negative-control claim boundary."""

    for key, expected in (
        ("schema", SCHEMA),
        ("status", STATUS),
        ("trust", TRUST),
        ("claim_scope", CLAIM_SCOPE),
        ("conclusion", CONCLUSION),
        ("provenance", PROVENANCE),
    ):
        if payload.get(key) != expected:
            raise AssertionError(f"{key} changed")
    for halo_count, expected in EXPECTED_CENSUS.items():
        section = payload.get("four_halos" if halo_count == 4 else "five_halos")
        if not isinstance(section, Mapping):
            raise AssertionError(f"missing {halo_count}-halo section")
        for key, value in expected.items():
            if section.get(key) != value:
                raise AssertionError(f"{halo_count}-halo {key} changed")
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("missing summary")
    expected_summary = {
        "exclusive_trigger_cover_count": 310_320,
        "endpoint_reuse_survivor_count": 310_320,
        "preferred_center_survivor_count": 301_055,
        "alternate_center_survivor_count": 9_265,
        "no_survivor_count": 0,
        "checked_constraints_force_richer_profile": False,
    }
    if dict(summary) != expected_summary:
        raise AssertionError("combined summary changed")


__all__ = [
    "CLAIM_SCOPE",
    "CONCLUSION",
    "EXPECTED_CENSUS",
    "PROVENANCE",
    "SCHEMA",
    "STATUS",
    "TRUST",
    "assert_expected_payload",
    "find_endpoint_reuse_witness",
    "halo_endpoint_reuse_payload",
]
