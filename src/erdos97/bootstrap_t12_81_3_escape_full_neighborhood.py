"""Full-neighborhood CSP for the bootstrap/T12 81:3 escape.

The one- and two-row-drop scans relax a fixed source-81 neighborhood by moving
one or two rows outside centers 3 and 6.  This packet lets all seven of those
other rows move at once.  Centers 3 and 6 still use the same one-class
replacement spaces from the escape-candidate scan:

* center 6 supplies label 6 before center 3 from seed [0,1,4];
* center 3 activates through a connector-avoiding class using label 6.

The search is an exact finite CSP over selected-row incidence and cyclic
crossing filters.  It is not a Euclidean realizability theorem and not a proof
of the bootstrap bridge.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_81_3_escape_candidates import (
    _center_3_connector_avoiding_classes,
    _supply_classes,
)
from erdos97.bootstrap_t12_81_3_escape_two_row_drop import (
    ALL_PAIRS,
    CROSS_OK,
    DEFAULT_ARTIFACT as TWO_ROW_DROP_ARTIFACT,
    LABELS,
    MASK_TO_PAIR_INDEX,
    ROW_PAIR_INDICES,
    SCAN_STATUS as TWO_ROW_DROP_SCAN_STATUS,
    SCHEMA as TWO_ROW_DROP_SCHEMA,
    STATUS as TWO_ROW_DROP_STATUS,
    _all_replacement_row_masks,
    _row_mask,
)
from erdos97.bootstrap_t12_81_3_escape_candidates import (
    CONNECTOR_PAIR,
    CYCLIC_ORDER,
    PRESERVED_ROW_CENTERS,
    SUPPLY_CENTER,
)
from erdos97.bootstrap_t12_81_3_order_escape import (
    TARGET_DELETION_SEED,
    TARGET_ROW_CENTER,
    TARGET_ROW_KEY,
)


SCHEMA = "erdos97.bootstrap_t12_81_3_escape_full_neighborhood.v1"
STATUS = "BOOTSTRAP_T12_81_3_ESCAPE_FULL_NEIGHBORHOOD_CSP_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "NO_BASIC_FILTER_SURVIVORS_WHEN_ALL_OTHER_SOURCE81_ROWS_MOVE"
CLAIM_SCOPE = (
    "Full-neighborhood CSP relaxation of the 81:3 escape-candidate scan. The "
    "search keeps the one-class replacement spaces at centers 3 and 6, but "
    "allows all seven source-81 rows outside centers 3 and 6 to be arbitrary "
    "4-sets. The implicit space has 329,417,200,000,000 assignments, and exact "
    "backtracking proves none satisfy the row-pair, witness-pair, and crossing "
    "filters. This is not a proof of genuine rich-class order, not a proof of "
    "row forcing, not a proof of n=9, not a proof of the bridge, and not a "
    "counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_3_escape_full_neighborhood.json"
)

REPLACED_ROW_CENTERS = [TARGET_ROW_CENTER, SUPPLY_CENTER]
ROW_REPLACEMENT_COUNT_PER_CENTER = 70
FIXED_REPLACEMENT_PAIR_COUNT = 40
IMPLICIT_ASSIGNMENT_SPACE_SIZE = (
    FIXED_REPLACEMENT_PAIR_COUNT
    * (ROW_REPLACEMENT_COUNT_PER_CENTER ** len(PRESERVED_ROW_CENTERS))
)


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _row_pair_compatible(
    center_a: int,
    row_a: int,
    center_b: int,
    row_b: int,
) -> bool:
    source_a, source_b = sorted((center_a, center_b))
    intersection = row_a & row_b
    intersection_size = intersection.bit_count()
    if intersection_size > 2:
        return False
    if intersection_size == 2:
        pair_index = MASK_TO_PAIR_INDEX[intersection]
        return bool(CROSS_OK[(source_a, source_b, pair_index)])
    return True


def _compatible_with_assignment(
    center: int,
    row_mask: int,
    assigned: Mapping[int, int],
    pair_counts: Sequence[int],
) -> bool:
    for pair_index in ROW_PAIR_INDICES[row_mask]:
        if pair_counts[pair_index] >= 2:
            return False
    return all(
        _row_pair_compatible(center, row_mask, other_center, other_row)
        for other_center, other_row in assigned.items()
    )


def _update_pair_counts(row_mask: int, pair_counts: list[int], delta: int) -> None:
    for pair_index in ROW_PAIR_INDICES[row_mask]:
        pair_counts[pair_index] += delta


def _search_fixed_pair(
    supply_mask: int,
    center_3_mask: int,
    replacement_masks: Mapping[int, Sequence[int]],
) -> dict[str, object]:
    assigned = {
        TARGET_ROW_CENTER: center_3_mask,
        SUPPLY_CENTER: supply_mask,
    }
    pair_counts = [0] * len(ALL_PAIRS)
    for row_mask in assigned.values():
        _update_pair_counts(row_mask, pair_counts, 1)

    if not _row_pair_compatible(TARGET_ROW_CENTER, center_3_mask, SUPPLY_CENTER, supply_mask):
        return {
            "initial_status": "INITIAL_FIXED_PAIR_INCOMPATIBLE",
            "search_node_count": 0,
            "empty_domain_count": 0,
            "complete_solution_count": 0,
            "max_depth": 0,
            "empty_domain_depth_histogram": {},
        }

    stats = {
        "search_node_count": 0,
        "empty_domain_count": 0,
        "complete_solution_count": 0,
        "max_depth": 0,
    }
    empty_depths: Counter[int] = Counter()

    def search() -> None:
        stats["search_node_count"] += 1
        depth = len(assigned) - len(REPLACED_ROW_CENTERS)
        stats["max_depth"] = max(int(stats["max_depth"]), depth)
        if len(assigned) == len(LABELS):
            stats["complete_solution_count"] += 1
            return

        best_center: int | None = None
        best_options: list[int] | None = None
        for center in PRESERVED_ROW_CENTERS:
            if center in assigned:
                continue
            options = [
                row_mask
                for row_mask in replacement_masks[center]
                if _compatible_with_assignment(center, row_mask, assigned, pair_counts)
            ]
            if best_options is None or len(options) < len(best_options):
                best_center = center
                best_options = options
            if not options:
                stats["empty_domain_count"] += 1
                empty_depths[depth] += 1
                return

        if best_center is None or best_options is None:
            raise AssertionError("search reached inconsistent assignment state")
        for row_mask in best_options:
            assigned[best_center] = row_mask
            _update_pair_counts(row_mask, pair_counts, 1)
            search()
            _update_pair_counts(row_mask, pair_counts, -1)
            del assigned[best_center]

    search()
    stats["initial_status"] = "SEARCH_EXHAUSTED"
    stats["empty_domain_depth_histogram"] = {
        str(depth): count for depth, count in sorted(empty_depths.items())
    }
    return stats


def _scan_csp() -> dict[str, object]:
    supply_classes = _supply_classes()
    center_3_classes = _center_3_connector_avoiding_classes()
    supply_masks = [_row_mask(row) for row in supply_classes]
    center_3_masks = [
        _row_mask(_int_list(record["rich_class"])) for record in center_3_classes
    ]
    replacement_masks = {
        center: _all_replacement_row_masks(center) for center in PRESERVED_ROW_CENTERS
    }

    fixed_summaries: list[dict[str, object]] = []
    aggregate = Counter()
    for supply_class, supply_mask in zip(supply_classes, supply_masks, strict=True):
        for center_3_data, center_3_mask in zip(
            center_3_classes, center_3_masks, strict=True
        ):
            stats = _search_fixed_pair(supply_mask, center_3_mask, replacement_masks)
            aggregate["search_node_count"] += int(stats["search_node_count"])
            aggregate["empty_domain_count"] += int(stats["empty_domain_count"])
            aggregate["complete_solution_count"] += int(stats["complete_solution_count"])
            aggregate[f"initial_status:{stats['initial_status']}"] += 1
            fixed_summaries.append(
                {
                    "supply_center_class": supply_class,
                    "target_center_class": _int_list(center_3_data["rich_class"]),
                    "target_center_activation_triple": center_3_data[
                        "activation_triple"
                    ],
                    **stats,
                }
            )

    return {
        "fixed_pair_summaries": fixed_summaries,
        "aggregate": dict(sorted(aggregate.items())),
    }


def build_t12_81_3_escape_full_neighborhood_payload() -> dict[str, object]:
    """Return the deterministic full-neighborhood escape CSP packet."""

    scan = _scan_csp()
    aggregate = scan["aggregate"]
    if not isinstance(aggregate, Mapping):
        raise AssertionError("aggregate must be a mapping")

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This CSP keeps the one-class replacement spaces at centers 3 and 6.",
            "All seven source-81 rows outside centers 3 and 6 may move as arbitrary selected 4-sets.",
            "The CSP uses incidence and crossing filters only, not Euclidean realizability.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "target_row_key": TARGET_ROW_KEY,
            "source_record_ids": [81],
            "cyclic_order": CYCLIC_ORDER,
            "deletion_seed": TARGET_DELETION_SEED,
            "connector_pair": CONNECTOR_PAIR,
            "supply_center": SUPPLY_CENTER,
            "target_center": TARGET_ROW_CENTER,
            "free_row_centers": PRESERVED_ROW_CENTERS,
            "fixed_replacement_row_centers": REPLACED_ROW_CENTERS,
            "center_6_supply_class_count": len(_supply_classes()),
            "center_3_connector_avoiding_class_count": len(
                _center_3_connector_avoiding_classes()
            ),
            "fixed_replacement_pair_count": FIXED_REPLACEMENT_PAIR_COUNT,
            "free_row_replacement_count_per_center": ROW_REPLACEMENT_COUNT_PER_CENTER,
            "implicit_assignment_space_size": IMPLICIT_ASSIGNMENT_SPACE_SIZE,
            "search_node_count": aggregate["search_node_count"],
            "empty_domain_count": aggregate["empty_domain_count"],
            "initial_fixed_pair_incompatible_count": aggregate[
                "initial_status:INITIAL_FIXED_PAIR_INCOMPATIBLE"
            ],
            "initial_fixed_pair_searched_count": aggregate[
                "initial_status:SEARCH_EXHAUSTED"
            ],
            "complete_solution_count": aggregate["complete_solution_count"],
            "surviving_assignment_count": aggregate["complete_solution_count"],
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This does not rule out richer catalogues than one replacement "
                "class at centers 3 and 6, multiple simultaneous rich classes "
                "per center, or additional minimal/rich-class hypotheses."
            ),
        },
        "candidate_generation": {
            "center_6_supply_classes": _supply_classes(),
            "center_3_connector_avoiding_classes": _center_3_connector_avoiding_classes(),
            "free_row_choice_count_per_center": {
                str(center): len(_all_replacement_row_masks(center))
                for center in PRESERVED_ROW_CENTERS
            },
        },
        "fixed_pair_summaries": scan["fixed_pair_summaries"],
        "survivors": [],
        "source_two_row_drop_scan": {
            "path": TWO_ROW_DROP_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": TWO_ROW_DROP_SCHEMA,
            "status": TWO_ROW_DROP_STATUS,
            "scan_status": TWO_ROW_DROP_SCAN_STATUS,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_3_escape_full_neighborhood.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_3_escape_full_neighborhood.py "
                "--write --assert-expected"
            ),
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    expected_top = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
    }
    for key, expected in expected_top.items():
        if payload.get(key) != expected:
            raise AssertionError(f"{key} mismatch: expected {expected!r}")

    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("summary must be a mapping")
    expected_summary = {
        "target_row_key": TARGET_ROW_KEY,
        "source_record_ids": [81],
        "cyclic_order": CYCLIC_ORDER,
        "deletion_seed": TARGET_DELETION_SEED,
        "connector_pair": CONNECTOR_PAIR,
        "supply_center": SUPPLY_CENTER,
        "target_center": TARGET_ROW_CENTER,
        "free_row_centers": PRESERVED_ROW_CENTERS,
        "fixed_replacement_row_centers": REPLACED_ROW_CENTERS,
        "center_6_supply_class_count": 5,
        "center_3_connector_avoiding_class_count": 8,
        "fixed_replacement_pair_count": 40,
        "free_row_replacement_count_per_center": 70,
        "implicit_assignment_space_size": 329417200000000,
        "search_node_count": 1177,
        "empty_domain_count": 684,
        "initial_fixed_pair_incompatible_count": 8,
        "initial_fixed_pair_searched_count": 32,
        "complete_solution_count": 0,
        "surviving_assignment_count": 0,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    fixed_summaries = payload.get("fixed_pair_summaries")
    if not isinstance(fixed_summaries, Sequence) or len(fixed_summaries) != 40:
        raise AssertionError("expected 40 fixed-pair summaries")
    if any(
        isinstance(record, Mapping) and record.get("complete_solution_count") != 0
        for record in fixed_summaries
    ):
        raise AssertionError("no fixed pair should have a complete solution")

    survivors = payload.get("survivors")
    if survivors != []:
        raise AssertionError("survivors must be empty")

    source = payload.get("source_two_row_drop_scan")
    if not isinstance(source, Mapping):
        raise AssertionError("source_two_row_drop_scan must be a mapping")
    if source.get("schema") != TWO_ROW_DROP_SCHEMA:
        raise AssertionError("source two-row-drop schema drifted")
    if source.get("scan_status") != TWO_ROW_DROP_SCAN_STATUS:
        raise AssertionError("source two-row-drop scan status drifted")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_3_escape_full_neighborhood.py"
    ):
        raise AssertionError("provenance generator drifted")
