"""Auxiliary-rich-class CSP for the bootstrap/T12 81:3 escape.

The full-neighborhood CSP keeps the center-3 connector class and center-6
supply class as the selected rows at those centers.  This packet allows those
two classes to be auxiliary rich classes instead.  The selected rows at centers
3 and 6 may either be the auxiliary class itself or a disjoint selected 4-set,
as required for distinct distance classes at the same center.

The search is an exact finite CSP over selected/rich-class incidence and cyclic
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
from erdos97.bootstrap_t12_81_3_escape_full_neighborhood import (
    DEFAULT_ARTIFACT as FULL_NEIGHBORHOOD_ARTIFACT,
    SCAN_STATUS as FULL_NEIGHBORHOOD_SCAN_STATUS,
    SCHEMA as FULL_NEIGHBORHOOD_SCHEMA,
    STATUS as FULL_NEIGHBORHOOD_STATUS,
)
from erdos97.bootstrap_t12_81_3_escape_two_row_drop import (
    CROSS_OK,
    LABELS,
    MASK_TO_PAIR_INDEX,
    ROW_PAIR_INDICES,
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


SCHEMA = "erdos97.bootstrap_t12_81_3_escape_auxiliary_csp.v1"
STATUS = "BOOTSTRAP_T12_81_3_ESCAPE_AUXILIARY_CSP_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "NO_BASIC_FILTER_SURVIVORS_WITH_AUXILIARY_SUPPLY_AND_CONNECTOR_CLASSES"
CLAIM_SCOPE = (
    "Auxiliary-rich-class CSP relaxation of the 81:3 escape scan. The center-6 "
    "pre-3 supply class and center-3 connector-avoiding class are allowed to "
    "exist as auxiliary rich classes, while the selected rows at centers 3 and "
    "6 may be the same classes or disjoint classes. All seven other selected "
    "rows are arbitrary 4-sets. The implicit space has 1,317,668,800,000,000 "
    "selected-row assignments, and exact backtracking proves none satisfy the "
    "row-pair, witness-pair, crossing, and same-center disjointness filters. "
    "This is not a proof of genuine rich-class order, not a proof of row "
    "forcing, not a proof of n=9, not a proof of the bridge, and not a "
    "counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_3_escape_auxiliary_csp.json"
)

FIXED_AUXILIARY_PAIR_COUNT = 40
FREE_ROW_REPLACEMENT_COUNT_PER_CENTER = 70
SELECTED_ROW_OPTIONS_AT_AUXILIARY_CENTERS = 2
IMPLICIT_SELECTED_ASSIGNMENT_SPACE_SIZE = (
    FIXED_AUXILIARY_PAIR_COUNT
    * (FREE_ROW_REPLACEMENT_COUNT_PER_CENTER ** len(PRESERVED_ROW_CENTERS))
    * (SELECTED_ROW_OPTIONS_AT_AUXILIARY_CENTERS ** 2)
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


def _auxiliary_selected_choices(center: int, auxiliary_row: int) -> list[int]:
    choices = []
    for row_mask in _all_replacement_row_masks(center):
        if row_mask == auxiliary_row or not (row_mask & auxiliary_row):
            choices.append(row_mask)
    return choices


def _add_pair_centers(
    center: int,
    row_mask: int,
    pair_centers: dict[int, set[int]],
) -> None:
    for pair_index in ROW_PAIR_INDICES[row_mask]:
        pair_centers.setdefault(pair_index, set()).add(center)


def _build_pair_centers(
    auxiliary: Mapping[int, int],
    selected: Mapping[int, Sequence[int]],
) -> dict[int, set[int]]:
    pair_centers: dict[int, set[int]] = {}
    for center, row_mask in auxiliary.items():
        _add_pair_centers(center, row_mask, pair_centers)
    for center, row_masks in selected.items():
        for row_mask in row_masks:
            _add_pair_centers(center, row_mask, pair_centers)
    return pair_centers


def _compatible_with_catalogue(
    center: int,
    row_mask: int,
    auxiliary: Mapping[int, int],
    selected: Mapping[int, Sequence[int]],
    pair_centers: Mapping[int, set[int]],
) -> bool:
    if center in auxiliary:
        auxiliary_row = auxiliary[center]
        if row_mask != auxiliary_row and row_mask & auxiliary_row:
            return False

    for pair_index in ROW_PAIR_INDICES[row_mask]:
        centers = pair_centers.get(pair_index, set())
        if center not in centers and len(centers) >= 2:
            return False

    for other_center, other_row in auxiliary.items():
        if other_center != center and not _row_pair_compatible(
            center, row_mask, other_center, other_row
        ):
            return False

    for other_center, other_rows in selected.items():
        if other_center == center:
            continue
        for other_row in other_rows:
            if not _row_pair_compatible(center, row_mask, other_center, other_row):
                return False
    return True


def _search_auxiliary_pair(
    supply_mask: int,
    center_3_mask: int,
) -> dict[str, object]:
    auxiliary = {
        SUPPLY_CENTER: supply_mask,
        TARGET_ROW_CENTER: center_3_mask,
    }
    if not _row_pair_compatible(SUPPLY_CENTER, supply_mask, TARGET_ROW_CENTER, center_3_mask):
        return {
            "initial_status": "INITIAL_AUXILIARY_PAIR_INCOMPATIBLE",
            "search_node_count": 0,
            "empty_domain_count": 0,
            "complete_solution_count": 0,
            "max_depth": 0,
            "empty_domain_depth_histogram": {},
        }

    selected: dict[int, list[int]] = {}
    pair_centers = _build_pair_centers(auxiliary, selected)
    choices = {
        center: _all_replacement_row_masks(center) for center in PRESERVED_ROW_CENTERS
    }
    choices[TARGET_ROW_CENTER] = _auxiliary_selected_choices(
        TARGET_ROW_CENTER, center_3_mask
    )
    choices[SUPPLY_CENTER] = _auxiliary_selected_choices(SUPPLY_CENTER, supply_mask)

    stats = {
        "search_node_count": 0,
        "empty_domain_count": 0,
        "complete_solution_count": 0,
        "max_depth": 0,
    }
    empty_depths: Counter[int] = Counter()

    def search() -> None:
        nonlocal pair_centers
        stats["search_node_count"] += 1
        depth = len(selected)
        stats["max_depth"] = max(int(stats["max_depth"]), depth)
        if len(selected) == len(LABELS):
            stats["complete_solution_count"] += 1
            return

        best_center: int | None = None
        best_options: list[int] | None = None
        for center in LABELS:
            if center in selected:
                continue
            options = [
                row_mask
                for row_mask in choices[center]
                if _compatible_with_catalogue(
                    center, row_mask, auxiliary, selected, pair_centers
                )
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
            selected[best_center] = [row_mask]
            pair_centers = _build_pair_centers(auxiliary, selected)
            search()
            del selected[best_center]
            pair_centers = _build_pair_centers(auxiliary, selected)

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

    fixed_summaries: list[dict[str, object]] = []
    aggregate = Counter()
    for supply_class, supply_mask in zip(supply_classes, supply_masks, strict=True):
        for center_3_data, center_3_mask in zip(
            center_3_classes, center_3_masks, strict=True
        ):
            stats = _search_auxiliary_pair(supply_mask, center_3_mask)
            aggregate["search_node_count"] += int(stats["search_node_count"])
            aggregate["empty_domain_count"] += int(stats["empty_domain_count"])
            aggregate["complete_solution_count"] += int(stats["complete_solution_count"])
            aggregate[f"initial_status:{stats['initial_status']}"] += 1
            fixed_summaries.append(
                {
                    "auxiliary_supply_center_class": supply_class,
                    "auxiliary_target_center_class": _int_list(
                        center_3_data["rich_class"]
                    ),
                    "target_center_activation_triple": center_3_data[
                        "activation_triple"
                    ],
                    "selected_row_choice_count_at_supply_center": len(
                        _auxiliary_selected_choices(SUPPLY_CENTER, supply_mask)
                    ),
                    "selected_row_choice_count_at_target_center": len(
                        _auxiliary_selected_choices(TARGET_ROW_CENTER, center_3_mask)
                    ),
                    **stats,
                }
            )

    return {
        "fixed_auxiliary_pair_summaries": fixed_summaries,
        "aggregate": dict(sorted(aggregate.items())),
    }


def build_t12_81_3_escape_auxiliary_csp_payload() -> dict[str, object]:
    """Return the deterministic auxiliary-rich-class escape CSP packet."""

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
            "This CSP treats the center-6 supply class and center-3 connector class as auxiliary rich classes.",
            "Selected rows at centers 3 and 6 may equal their auxiliary class or be disjoint from it.",
            "The CSP uses incidence, crossing, pair-cap, and same-center disjointness filters only, not Euclidean realizability.",
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
            "free_selected_row_centers": CYCLIC_ORDER,
            "auxiliary_class_centers": [TARGET_ROW_CENTER, SUPPLY_CENTER],
            "center_6_supply_class_count": len(_supply_classes()),
            "center_3_connector_avoiding_class_count": len(
                _center_3_connector_avoiding_classes()
            ),
            "fixed_auxiliary_pair_count": FIXED_AUXILIARY_PAIR_COUNT,
            "free_row_replacement_count_per_non_auxiliary_center": FREE_ROW_REPLACEMENT_COUNT_PER_CENTER,
            "selected_row_options_at_auxiliary_centers": SELECTED_ROW_OPTIONS_AT_AUXILIARY_CENTERS,
            "implicit_selected_assignment_space_size": IMPLICIT_SELECTED_ASSIGNMENT_SPACE_SIZE,
            "search_node_count": aggregate["search_node_count"],
            "empty_domain_count": aggregate["empty_domain_count"],
            "initial_auxiliary_pair_incompatible_count": aggregate[
                "initial_status:INITIAL_AUXILIARY_PAIR_INCOMPATIBLE"
            ],
            "initial_auxiliary_pair_searched_count": aggregate[
                "initial_status:SEARCH_EXHAUSTED"
            ],
            "complete_solution_count": aggregate["complete_solution_count"],
            "surviving_assignment_count": aggregate["complete_solution_count"],
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This does not rule out richer catalogues with more than one "
                "auxiliary supply/connector class, replacement classes outside "
                "the specified center-3 and center-6 spaces, or additional "
                "minimal/rich-class hypotheses."
            ),
        },
        "candidate_generation": {
            "center_6_supply_classes": _supply_classes(),
            "center_3_connector_avoiding_classes": _center_3_connector_avoiding_classes(),
            "free_row_choice_count_per_non_auxiliary_center": {
                str(center): len(_all_replacement_row_masks(center))
                for center in PRESERVED_ROW_CENTERS
            },
        },
        "fixed_auxiliary_pair_summaries": scan["fixed_auxiliary_pair_summaries"],
        "survivors": [],
        "source_full_neighborhood_scan": {
            "path": FULL_NEIGHBORHOOD_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": FULL_NEIGHBORHOOD_SCHEMA,
            "status": FULL_NEIGHBORHOOD_STATUS,
            "scan_status": FULL_NEIGHBORHOOD_SCAN_STATUS,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_3_escape_auxiliary_csp.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_3_escape_auxiliary_csp.py "
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
        "free_selected_row_centers": CYCLIC_ORDER,
        "auxiliary_class_centers": [TARGET_ROW_CENTER, SUPPLY_CENTER],
        "center_6_supply_class_count": 5,
        "center_3_connector_avoiding_class_count": 8,
        "fixed_auxiliary_pair_count": 40,
        "free_row_replacement_count_per_non_auxiliary_center": 70,
        "selected_row_options_at_auxiliary_centers": 2,
        "implicit_selected_assignment_space_size": 1317668800000000,
        "search_node_count": 1287,
        "empty_domain_count": 730,
        "initial_auxiliary_pair_incompatible_count": 8,
        "initial_auxiliary_pair_searched_count": 32,
        "complete_solution_count": 0,
        "surviving_assignment_count": 0,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    fixed_summaries = payload.get("fixed_auxiliary_pair_summaries")
    if not isinstance(fixed_summaries, Sequence) or len(fixed_summaries) != 40:
        raise AssertionError("expected 40 fixed-auxiliary-pair summaries")
    if any(
        isinstance(record, Mapping) and record.get("complete_solution_count") != 0
        for record in fixed_summaries
    ):
        raise AssertionError("no fixed auxiliary pair should have a complete solution")

    survivors = payload.get("survivors")
    if survivors != []:
        raise AssertionError("survivors must be empty")

    source = payload.get("source_full_neighborhood_scan")
    if not isinstance(source, Mapping):
        raise AssertionError("source_full_neighborhood_scan must be a mapping")
    if source.get("schema") != FULL_NEIGHBORHOOD_SCHEMA:
        raise AssertionError("source full-neighborhood schema drifted")
    if source.get("scan_status") != FULL_NEIGHBORHOOD_SCAN_STATUS:
        raise AssertionError("source full-neighborhood scan status drifted")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_3_escape_auxiliary_csp.py"
    ):
        raise AssertionError("provenance generator drifted")
