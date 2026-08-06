"""Exact motif forcing at the first complete 23=27 halo boundary.

This module derives a smaller local endgame from the stored halo-lift
frontier. It does not force the quotient core or bound arbitrary halo systems.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from typing import Any, Mapping, Sequence

from erdos97.fragile_cycle_halo_lift_frontier import (
    FRONTIER_SCHEMA as SOURCE_FRONTIER_SCHEMA,
    _pair,
    _pair_counts,
    _selected_indegrees,
    assert_expected_payload as assert_expected_source,
    cyclic_order_for_gaps,
    enumerate_fragile_covers,
)
from erdos97.fragile_hypergraph import _selected_pair_ok
from erdos97.kalmanson_equilateral_hinge import find_hinge_instances
from erdos97.kalmanson_splice import find_dihedral_splice_embeddings


SCHEMA = "erdos97.fragile_cycle_halo_motif_forcing.v1"
STATUS = "EXACT_BOUNDED_ACTIVE_HALO_MOTIF_FORCING"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
SOURCE_SCHEMA = "erdos97.fragile_cycle_halo_lift_frontier.v1"
SOURCE_CANONICAL_SHA256 = (
    "2668919cfbe2fd505a29121553ae9f3d850baa0a05cf0e11edf3d659c37a0520"
)
CLAIM_SCOPE = (
    "Exact bounded consequence for the stored 23=27 quotient core with one or "
    "two canonical added halo roles. All 38 one-halo essential fragile covers "
    "contain an equilateral hinge or a generic Kalmanson splice. At the "
    "two-halo first-full-extension boundary, the source frontier proves that "
    "only six of 7,708 essential covers extend, and an exhaustive hinge-pruned "
    "search proves that none of those six has a hinge-free full selected-row "
    "extension. This does not force the quotient core, control three or more "
    "or arbitrary halo roles, prove Euclidean realizability, n=9, n=10, Erdos "
    "Problem #97, or a counterexample."
)
CONCLUSION = (
    "The first complete 23=27 core-plus-halo boundary has a native generic "
    "endgame: every admissible two-halo full selected-row extension contains "
    "an equilateral hinge. The one-halo boundary is already covered by the "
    "hinge/splice alternatives but has no full extension. The remaining bridge "
    "gap is to force this bounded core/halo regime or control larger halos."
)
PROVENANCE = {
    "generator": "scripts/check_fragile_cycle_halo_motif_forcing.py",
    "command": (
        "python scripts/check_fragile_cycle_halo_motif_forcing.py "
        "--write --assert-expected --summary-json"
    ),
}

EXPECTED_ONE_HALO = {
    "essential_cover_count": 38,
    "hinge_cover_count": 29,
    "splice_cover_count": 22,
    "hinge_only_cover_count": 16,
    "splice_only_cover_count": 9,
    "both_motifs_cover_count": 13,
    "motif_free_cover_count": 0,
    "source_extendable_cover_count": 0,
}
EXPECTED_ASSIGNMENTS = ("A138", "A008", "A079", "A121", "A179", "A069")
EXPECTED_SEARCH_COUNTS = {
    "A138": {
        "states_visited": 13,
        "branches_visited": 12,
        "dead_ends": 2,
        "hinge_prunes": 7,
    },
    "A008": {
        "states_visited": 7,
        "branches_visited": 6,
        "dead_ends": 0,
        "hinge_prunes": 3,
    },
    "A079": {
        "states_visited": 3,
        "branches_visited": 2,
        "dead_ends": 0,
        "hinge_prunes": 1,
    },
    "A121": {
        "states_visited": 3,
        "branches_visited": 2,
        "dead_ends": 0,
        "hinge_prunes": 1,
    },
    "A179": {
        "states_visited": 4,
        "branches_visited": 3,
        "dead_ends": 1,
        "hinge_prunes": 1,
    },
    "A069": {
        "states_visited": 6,
        "branches_visited": 5,
        "dead_ends": 0,
        "hinge_prunes": 4,
    },
}


def _rows_json(rows: Mapping[int, Sequence[int]]) -> list[list[int]]:
    return [[center, *sorted(rows[center])] for center in sorted(rows)]


def _rows_from_json(
    raw_rows: Sequence[Sequence[int]],
) -> dict[int, tuple[int, ...]]:
    return {
        int(raw[0]): tuple(sorted(int(witness) for witness in raw[1:]))
        for raw in raw_rows
    }


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded).hexdigest()


def _one_halo_payload() -> dict[str, Any]:
    placements: list[dict[str, Any]] = []
    totals: Counter[str] = Counter()
    representatives: dict[str, dict[str, Any]] = {}
    for gap in range(7):
        order = cyclic_order_for_gaps((gap,))
        enumeration = enumerate_fragile_covers(order)
        covers = enumeration["covers"]
        placement_counts: Counter[str] = Counter()
        for cover_index, rows in enumerate(covers):
            hinges = find_hinge_instances(rows, order)
            splices = find_dihedral_splice_embeddings(rows, order)
            has_hinge = bool(hinges)
            has_splice = bool(splices)
            classification = (
                "both"
                if has_hinge and has_splice
                else "hinge_only"
                if has_hinge
                else "splice_only"
                if has_splice
                else "motif_free"
            )
            placement_counts[classification] += 1
            placement_counts["hinge"] += has_hinge
            placement_counts["splice"] += has_splice
            representatives.setdefault(
                classification,
                {
                    "gaps_after_core_roles": [gap],
                    "cover_index": cover_index,
                    "cyclic_order": list(order),
                    "fragile_rows": _rows_json(rows),
                    "hinge_count": len(hinges),
                    "splice_count": len(splices),
                    "first_hinge": hinges[0].as_dict() if hinges else None,
                    "first_splice": splices[0].as_dict() if splices else None,
                },
            )
        cover_count = len(covers)
        totals["essential_cover_count"] += cover_count
        totals["hinge_cover_count"] += placement_counts["hinge"]
        totals["splice_cover_count"] += placement_counts["splice"]
        totals["hinge_only_cover_count"] += placement_counts["hinge_only"]
        totals["splice_only_cover_count"] += placement_counts["splice_only"]
        totals["both_motifs_cover_count"] += placement_counts["both"]
        totals["motif_free_cover_count"] += placement_counts["motif_free"]
        placements.append(
            {
                "gaps_after_core_roles": [gap],
                "cyclic_order": list(order),
                "essential_cover_count": cover_count,
                "hinge_cover_count": placement_counts["hinge"],
                "splice_cover_count": placement_counts["splice"],
                "hinge_only_cover_count": placement_counts["hinge_only"],
                "splice_only_cover_count": placement_counts["splice_only"],
                "both_motifs_cover_count": placement_counts["both"],
                "motif_free_cover_count": placement_counts["motif_free"],
            }
        )
    return {
        "placement_count": 7,
        **dict(totals),
        "placements": placements,
        "classification_representatives": representatives,
    }


def hinge_free_full_extension_search(
    order: Sequence[int],
    fixed_rows: Mapping[int, Sequence[int]],
) -> dict[str, Any]:
    """Exhaust the full-extension branch while pruning monotone hinges."""

    labels = set(int(label) for label in order)
    n = len(labels)
    indegree_cap = 2 * (n - 1) // 3
    candidates = {
        center: list(combinations(sorted(labels - {center}), 4))
        for center in labels
        if center not in fixed_rows
    }
    assigned = {
        int(center): tuple(sorted(int(witness) for witness in row))
        for center, row in fixed_rows.items()
    }
    pair_counts = _pair_counts(assigned)
    indegrees = _selected_indegrees(assigned)
    counts: Counter[str] = Counter()
    witness: dict[int, tuple[int, ...]] | None = None

    def viable(center: int, row: Sequence[int]) -> bool:
        if any(indegrees[witness_label] >= indegree_cap for witness_label in row):
            return False
        if any(
            pair_counts[_pair(left, right)] >= 2 for left, right in combinations(row, 2)
        ):
            return False
        return all(
            _selected_pair_ok(center, row, other, other_row, order)
            for other, other_row in assigned.items()
        )

    def search() -> bool:
        nonlocal witness
        counts["states_visited"] += 1
        if find_hinge_instances(assigned, order):
            counts["hinge_prunes"] += 1
            return False
        if len(assigned) == n:
            counts["hinge_free_full_extensions_found"] += 1
            witness = dict(assigned)
            return True
        best_center: int | None = None
        best_options: list[tuple[int, ...]] | None = None
        for center in sorted(labels - set(assigned)):
            options = [row for row in candidates[center] if viable(center, row)]
            if not options:
                counts["dead_ends"] += 1
                return False
            if best_options is None or len(options) < len(best_options):
                best_center = center
                best_options = options
        assert best_center is not None and best_options is not None
        for row in best_options:
            counts["branches_visited"] += 1
            assigned[best_center] = row
            row_pairs = list(combinations(row, 2))
            for witness_label in row:
                indegrees[witness_label] += 1
            for left, right in row_pairs:
                pair_counts[_pair(left, right)] += 1
            if search():
                return True
            for left, right in row_pairs:
                pair_counts[_pair(left, right)] -= 1
            for witness_label in row:
                indegrees[witness_label] -= 1
            del assigned[best_center]
        return False

    exists = search()
    stable_counts = {
        key: counts[key]
        for key in (
            "states_visited",
            "branches_visited",
            "dead_ends",
            "hinge_prunes",
        )
    }
    return {
        "hinge_free_full_extension_exists": exists,
        "hinge_free_full_extension": _rows_json(witness) if witness else None,
        "search_exhausted": not exists,
        "search_counts": stable_counts,
    }


def _two_halo_payload(source: Mapping[str, Any]) -> dict[str, Any]:
    raw_two_halos = source["two_halos"]
    witnesses = raw_two_halos["extension_witnesses"]
    records: list[dict[str, Any]] = []
    seen_cover_keys: set[tuple[tuple[int, ...], int]] = set()
    for source_witness in witnesses:
        gaps = tuple(int(gap) for gap in source_witness["gaps_after_core_roles"])
        cover_index = int(source_witness["cover_index"])
        cover_key = (gaps, cover_index)
        if cover_key in seen_cover_keys:
            raise AssertionError("duplicate extendable cover in source frontier")
        seen_cover_keys.add(cover_key)
        order = cyclic_order_for_gaps(gaps)
        enumeration = enumerate_fragile_covers(order)
        covers = enumeration["covers"]
        if cover_index >= len(covers):
            raise AssertionError("source extendable cover index is out of range")
        fragile_rows = covers[cover_index]
        if _rows_json(fragile_rows) != source_witness["fragile_rows"]:
            raise AssertionError("source extendable cover does not replay")
        assignment = source_witness["n9_frontier_assignment"]
        assignment_id = str(assignment["assignment_id"])
        full_rows = _rows_from_json(source_witness["selected_rows"])
        hinges = find_hinge_instances(full_rows, order)
        if not hinges:
            raise AssertionError("source full-extension witness has no hinge")
        search = hinge_free_full_extension_search(order, fragile_rows)
        records.append(
            {
                "assignment_id": assignment_id,
                "source_template_id": str(assignment["template_id"]),
                "source_frontier_status": str(assignment["status"]),
                "gaps_after_core_roles": list(gaps),
                "cover_index": cover_index,
                "cyclic_order": list(order),
                "fragile_rows": _rows_json(fragile_rows),
                "source_first_full_extension": _rows_json(full_rows),
                "source_first_full_extension_hinge_count": len(hinges),
                "source_first_full_extension_first_hinge": hinges[0].as_dict(),
                **search,
            }
        )
    aggregate_counts: Counter[str] = Counter()
    for record in records:
        aggregate_counts.update(record["search_counts"])
    return {
        "essential_cover_count": int(raw_two_halos["essential_cover_count"]),
        "source_extendable_cover_count": int(
            raw_two_halos["extendable_partial_cover_count"]
        ),
        "extendable_cover_hinge_exhaustions": records,
        "aggregate_hinge_free_search_counts": dict(aggregate_counts),
        "hinge_free_extendable_cover_count": sum(
            bool(record["hinge_free_full_extension_exists"]) for record in records
        ),
        "all_full_extensions_force_hinge": all(
            record["search_exhausted"]
            and not record["hinge_free_full_extension_exists"]
            for record in records
        )
        and len(records) == int(raw_two_halos["extendable_partial_cover_count"]),
    }


def halo_motif_forcing_payload(source: Mapping[str, Any]) -> dict[str, Any]:
    """Build the deterministic active-halo motif-forcing packet."""

    assert_expected_source(source)
    if source.get("schema") != SOURCE_SCHEMA:
        raise ValueError("unexpected halo-lift source schema")
    source_sha = _canonical_sha256(source)
    if source_sha != SOURCE_CANONICAL_SHA256:
        raise ValueError("unexpected halo-lift source digest")
    one_halo = _one_halo_payload()
    one_halo["source_extendable_cover_count"] = int(
        source["one_halo"]["extendable_partial_cover_count"]
    )
    two_halos = _two_halo_payload(source)
    catalog_sha = _canonical_sha256({"one_halo": one_halo, "two_halos": two_halos})
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifact": {
            "path": "data/certificates/fragile_cycle_halo_lift_frontier.json",
            "schema": SOURCE_SCHEMA,
            "canonical_json_sha256": source_sha,
            "frontier_schema": SOURCE_FRONTIER_SCHEMA,
        },
        "one_halo": one_halo,
        "two_halos": two_halos,
        "summary": {
            "one_halo_essential_covers": one_halo["essential_cover_count"],
            "one_halo_motif_free_covers": one_halo["motif_free_cover_count"],
            "two_halo_essential_covers": two_halos["essential_cover_count"],
            "two_halo_extendable_covers": two_halos["source_extendable_cover_count"],
            "two_halo_hinge_free_extendable_covers": two_halos[
                "hinge_free_extendable_cover_count"
            ],
            "first_full_boundary_forces_equilateral_hinge": two_halos[
                "all_full_extensions_force_hinge"
            ],
        },
        "catalog_sha256": catalog_sha,
        "limitations": [
            "The 23=27 quotient core is assumed, not forced from a minimal counterexample.",
            "The one- and two-halo labels are canonical formal roles, not a bound on arbitrary active halos.",
            "The conclusion uses the source frontier's exhaustive six-of-7708 extendability classification.",
            "No statement is made for three or more halos, Euclidean realizability, n=9, n=10, the general problem, or a counterexample.",
        ],
        "conclusion": CONCLUSION,
        "provenance": PROVENANCE,
    }


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable counts and the exact bounded claim boundary."""

    for key, expected in (
        ("schema", SCHEMA),
        ("status", STATUS),
        ("trust", TRUST),
        ("claim_scope", CLAIM_SCOPE),
        ("conclusion", CONCLUSION),
        ("provenance", PROVENANCE),
    ):
        if payload.get(key) != expected:
            raise AssertionError(
                f"{key}: expected {expected!r}, got {payload.get(key)!r}"
            )
    source = payload.get("source_artifact")
    if (
        not isinstance(source, Mapping)
        or source.get("canonical_json_sha256") != SOURCE_CANONICAL_SHA256
    ):
        raise AssertionError("unexpected source artifact digest")
    one_halo = payload.get("one_halo")
    if not isinstance(one_halo, Mapping):
        raise AssertionError("one_halo must be an object")
    for key, expected in EXPECTED_ONE_HALO.items():
        if one_halo.get(key) != expected:
            raise AssertionError(f"one_halo.{key}: expected {expected}")
    two_halos = payload.get("two_halos")
    if not isinstance(two_halos, Mapping):
        raise AssertionError("two_halos must be an object")
    if two_halos.get("essential_cover_count") != 7708:
        raise AssertionError("expected 7,708 two-halo essential covers")
    if two_halos.get("source_extendable_cover_count") != 6:
        raise AssertionError("expected six two-halo extendable covers")
    records = two_halos.get("extendable_cover_hinge_exhaustions")
    if not isinstance(records, list):
        raise AssertionError("missing hinge-exhaustion records")
    if tuple(record["assignment_id"] for record in records) != EXPECTED_ASSIGNMENTS:
        raise AssertionError("unexpected extendable-cover assignment order")
    for record in records:
        assignment_id = str(record["assignment_id"])
        if record.get("search_counts") != EXPECTED_SEARCH_COUNTS[assignment_id]:
            raise AssertionError(f"{assignment_id}: hinge-free counts changed")
        if record.get("hinge_free_full_extension_exists") is not False:
            raise AssertionError(f"{assignment_id}: hinge-free extension found")
        if record.get("search_exhausted") is not True:
            raise AssertionError(f"{assignment_id}: search incomplete")
    if two_halos.get("hinge_free_extendable_cover_count") != 0:
        raise AssertionError("unexpected hinge-free extendable cover")
    if two_halos.get("all_full_extensions_force_hinge") is not True:
        raise AssertionError("first full boundary does not force a hinge")
    summary = payload.get("summary")
    if (
        not isinstance(summary, Mapping)
        or summary.get("first_full_boundary_forces_equilateral_hinge") is not True
    ):
        raise AssertionError("summary hinge-forcing flag is absent")


__all__ = [
    "CLAIM_SCOPE",
    "CONCLUSION",
    "PROVENANCE",
    "SCHEMA",
    "STATUS",
    "TRUST",
    "assert_expected_payload",
    "halo_motif_forcing_payload",
    "hinge_free_full_extension_search",
]
