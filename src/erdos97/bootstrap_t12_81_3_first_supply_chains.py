"""First-step prefix CSP for the bootstrap/T12 81:3 escape.

The rich-support CSP rules out a direct pre-3 supply object at center 6 plus a
connector-avoiding support at center 3.  This packet widens the first step of a
possible pre-3 chain: before label 6 is supplied, the first activation from the
seed [0,1,4] may be any non-seed, non-3 center.  If even that first-step
support cannot coexist with a connector-avoiding center-3 support under the
same basic support filters, then longer chains in this model have no admissible
prefix.

The search is exact finite incidence/crossing bookkeeping.  It is not a
Euclidean realizability theorem and not a proof of the bootstrap bridge.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_81_3_escape_candidates import (
    CONNECTOR_PAIR,
    CYCLIC_ORDER,
    SUPPLY_CENTER,
)
from erdos97.bootstrap_t12_81_3_escape_rich_support_csp import (
    DEFAULT_ARTIFACT as RICH_SUPPORT_ARTIFACT,
    SCAN_STATUS as RICH_SUPPORT_SCAN_STATUS,
    SCHEMA as RICH_SUPPORT_SCHEMA,
    STATUS as RICH_SUPPORT_STATUS,
    _bit_labels,
    _build_pair_centers,
    _compatible_with_catalogue,
    _connector_support_records,
    _selected_row_choices_for_support,
    _support_masks_containing,
    _support_pair_compatible,
)
from erdos97.bootstrap_t12_81_3_escape_two_row_drop import (
    LABELS,
    _all_replacement_row_masks,
    _row_mask,
)
from erdos97.bootstrap_t12_81_3_order_escape import (
    TARGET_DELETION_SEED,
    TARGET_ROW_CENTER,
    TARGET_ROW_KEY,
)
from erdos97.bootstrap_t12_81_3_trigger_uniqueness import (
    DEFAULT_ARTIFACT as TRIGGER_UNIQUENESS_ARTIFACT,
    SCAN_STATUS as TRIGGER_UNIQUENESS_SCAN_STATUS,
    SCHEMA as TRIGGER_UNIQUENESS_SCHEMA,
    STATUS as TRIGGER_UNIQUENESS_STATUS,
)


SCHEMA = "erdos97.bootstrap_t12_81_3_first_supply_chains.v1"
STATUS = "BOOTSTRAP_T12_81_3_FIRST_SUPPLY_CHAINS_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "PREFIX_SURVIVORS_FOUND_BUT_NO_IMMEDIATE_LABEL6_SUPPLY_EXTENSION"
CLAIM_SCOPE = (
    "First-step prefix CSP for the 81:3 pre-3 label-6 escape. The first "
    "activation from seed [0,1,4] may be any non-seed, non-3 center, with a "
    "rich support of size 4 through 8 containing the seed. The center-3 "
    "connector-avoiding object is any rich support from the previous "
    "rich-support CSP. Selected rows at auxiliary centers may be 4-subsets of "
    "their support or disjoint 4-sets; all other selected rows are arbitrary "
    "4-sets. Exact backtracking finds three first-step prefix survivors, all "
    "with first activation at center 8, and then proves none of those prefixes "
    "admits an immediate center-6 label-6 supply support under the same basic "
    "filters. This is not a proof of genuine rich-class order, not a proof of "
    "row forcing, not a proof of n=9, not a proof of the bridge, and not a "
    "counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_3_first_supply_chains.json"
)

FIRST_STEP_CENTERS = [
    label
    for label in CYCLIC_ORDER
    if label not in set(TARGET_DELETION_SEED) | {TARGET_ROW_CENTER}
]
FREE_ROW_REPLACEMENT_COUNT_PER_NON_AUXILIARY_CENTER = 70


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _first_step_support_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for center in FIRST_STEP_CENTERS:
        for support_mask in _support_masks_containing(center, TARGET_DELETION_SEED):
            records.append(
                {
                    "first_step_center": center,
                    "first_step_kind": (
                        "direct_label_6_supply"
                        if center == SUPPLY_CENTER
                        else "intermediate_before_label_6"
                    ),
                    "support": _bit_labels(support_mask),
                    "support_mask": support_mask,
                    "support_size": support_mask.bit_count(),
                    "activation_trigger": TARGET_DELETION_SEED,
                }
            )
    return records


def _search_prefix_pair(
    first_step_center: int,
    first_step_support: int,
    connector_support: int,
) -> dict[str, object]:
    return _search_auxiliary_support_catalogue(
        {
            first_step_center: first_step_support,
            TARGET_ROW_CENTER: connector_support,
        },
        incompatible_status="INITIAL_AUXILIARY_SUPPORT_PAIR_INCOMPATIBLE",
    )


def _search_auxiliary_support_catalogue(
    auxiliary_supports: Mapping[int, int],
    *,
    incompatible_status: str,
) -> dict[str, object]:
    centers = sorted(auxiliary_supports)
    for index, center_a in enumerate(centers):
        for center_b in centers[index + 1 :]:
            if not _support_pair_compatible(
                center_a,
                auxiliary_supports[center_a],
                center_b,
                auxiliary_supports[center_b],
            ):
                return {
                    "initial_status": incompatible_status,
                    "search_node_count": 0,
                    "empty_domain_count": 0,
                    "detected_solution_count": 0,
                    "max_depth": 0,
                    "empty_domain_depth_histogram": {},
                    "first_solution_selected_rows": None,
                    "solution_search_status": "NOT_SEARCHED_INITIAL_PAIR_INCOMPATIBLE",
                }

    pair_centers = _build_pair_centers(auxiliary_supports, {})
    if any(len(centers_for_pair) > 2 for centers_for_pair in pair_centers.values()):
        return {
            "initial_status": incompatible_status,
            "search_node_count": 0,
            "empty_domain_count": 0,
            "detected_solution_count": 0,
            "max_depth": 0,
            "empty_domain_depth_histogram": {},
            "first_solution_selected_rows": None,
            "solution_search_status": "NOT_SEARCHED_INITIAL_PAIR_INCOMPATIBLE",
        }

    selected: dict[int, list[int]] = {}
    choices = {
        center: _all_replacement_row_masks(center) for center in CYCLIC_ORDER
    }
    for center, support in auxiliary_supports.items():
        choices[center] = _selected_row_choices_for_support(center, support)

    stats = {
        "search_node_count": 0,
        "empty_domain_count": 0,
        "detected_solution_count": 0,
        "max_depth": 0,
    }
    empty_depths: Counter[int] = Counter()
    first_solution: dict[str, list[list[int]]] | None = None
    stopped_after_solution = False

    def search() -> bool:
        nonlocal first_solution, pair_centers, stopped_after_solution
        stats["search_node_count"] += 1
        depth = len(selected)
        stats["max_depth"] = max(int(stats["max_depth"]), depth)
        if len(selected) == len(LABELS):
            stats["detected_solution_count"] += 1
            first_solution = {
                str(center): [_bit_labels(row_mask) for row_mask in row_masks]
                for center, row_masks in sorted(selected.items())
            }
            stopped_after_solution = True
            return True

        best_center: int | None = None
        best_options: list[int] | None = None
        for center in LABELS:
            if center in selected:
                continue
            options = [
                row_mask
                for row_mask in choices[center]
                if _compatible_with_catalogue(
                    center,
                    row_mask,
                    auxiliary_supports,
                    selected,
                    pair_centers,
                )
            ]
            if best_options is None or len(options) < len(best_options):
                best_center = center
                best_options = options
            if not options:
                stats["empty_domain_count"] += 1
                empty_depths[depth] += 1
                return False

        if best_center is None or best_options is None:
            raise AssertionError("search reached inconsistent assignment state")
        for row_mask in best_options:
            selected[best_center] = [row_mask]
            pair_centers = _build_pair_centers(auxiliary_supports, selected)
            if search():
                return True
            del selected[best_center]
            pair_centers = _build_pair_centers(auxiliary_supports, selected)
        return False

    search()
    stats["initial_status"] = "SEARCH_EXHAUSTED"
    stats["empty_domain_depth_histogram"] = {
        str(depth): count for depth, count in sorted(empty_depths.items())
    }
    stats["first_solution_selected_rows"] = first_solution
    stats["solution_search_status"] = (
        "STOPPED_AFTER_FIRST_SOLUTION"
        if stopped_after_solution
        else "EXHAUSTED_NO_SOLUTION"
    )
    return stats


def _scan_csp() -> dict[str, object]:
    first_step_records = _first_step_support_records()
    connector_records = _connector_support_records()
    connector_supports = [int(record["support_mask"]) for record in connector_records]

    prefix_summaries: list[dict[str, object]] = []
    aggregate = Counter()
    per_first_center: dict[int, Counter[str]] = {
        center: Counter() for center in FIRST_STEP_CENTERS
    }
    empty_depths: Counter[str] = Counter()
    survivors: list[dict[str, object]] = []

    for first_record in first_step_records:
        first_center = int(first_record["first_step_center"])
        first_support = int(first_record["support_mask"])
        for connector_record, connector_support in zip(
            connector_records, connector_supports, strict=True
        ):
            stats = _search_prefix_pair(
                first_center,
                first_support,
                connector_support,
            )
            aggregate["search_node_count"] += int(stats["search_node_count"])
            aggregate["empty_domain_count"] += int(stats["empty_domain_count"])
            aggregate["detected_solution_count"] += int(
                stats["detected_solution_count"]
            )
            aggregate[f"initial_status:{stats['initial_status']}"] += 1
            aggregate[f"solution_search_status:{stats['solution_search_status']}"] += 1
            per_first_center[first_center]["prefix_pair_count"] += 1
            per_first_center[first_center][f"initial_status:{stats['initial_status']}"] += 1
            per_first_center[first_center][
                f"solution_search_status:{stats['solution_search_status']}"
            ] += 1
            per_first_center[first_center]["detected_solution_count"] += int(
                stats["detected_solution_count"]
            )
            for depth, count in dict(stats["empty_domain_depth_histogram"]).items():
                empty_depths[str(depth)] += int(count)

            summary = {
                "first_step_center": first_center,
                "first_step_kind": first_record["first_step_kind"],
                "first_step_support": first_record["support"],
                "first_step_support_size": first_record["support_size"],
                "first_step_activation_trigger": first_record[
                    "activation_trigger"
                ],
                "auxiliary_target_support": connector_record["support"],
                "auxiliary_target_support_size": connector_record[
                    "support_size"
                ],
                "target_center_activation_triple": connector_record[
                    "activation_triple"
                ],
                "target_center_forbidden_connector_endpoint": connector_record[
                    "forbidden_connector_endpoint"
                ],
                "selected_row_choice_count_at_first_step_center": len(
                    _selected_row_choices_for_support(
                        first_center,
                        first_support,
                    )
                ),
                "selected_row_choice_count_at_target_center": len(
                    _selected_row_choices_for_support(
                        TARGET_ROW_CENTER,
                        connector_support,
                    )
                ),
                **stats,
            }
            prefix_summaries.append(summary)
            if int(stats["detected_solution_count"]):
                survivors.append(summary)

    return {
        "prefix_pair_summaries": prefix_summaries,
        "aggregate": dict(sorted(aggregate.items())),
        "per_first_step_center": {
            str(center): dict(sorted(counter.items()))
            for center, counter in per_first_center.items()
        },
        "empty_domain_depth_histogram": dict(sorted(empty_depths.items())),
        "survivors": survivors,
    }


def _label_6_supply_supports_after(first_step_center: int) -> list[int]:
    closure_mask = _row_mask([*TARGET_DELETION_SEED, first_step_center])
    return [
        support
        for support in _support_masks_containing(SUPPLY_CENTER, [])
        if (support & closure_mask).bit_count() >= 3
    ]


def _immediate_label_6_extension_scan(
    prefix_survivors: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    extension_summaries: list[dict[str, object]] = []
    extension_survivors: list[dict[str, object]] = []
    aggregate = Counter()
    empty_depths: Counter[str] = Counter()

    for prefix_index, prefix in enumerate(prefix_survivors):
        first_center = int(prefix["first_step_center"])
        if first_center == SUPPLY_CENTER:
            continue
        first_support = _row_mask(_int_list(prefix["first_step_support"]))
        connector_support = _row_mask(_int_list(prefix["auxiliary_target_support"]))
        for label_6_support in _label_6_supply_supports_after(first_center):
            stats = _search_auxiliary_support_catalogue(
                {
                    first_center: first_support,
                    SUPPLY_CENTER: label_6_support,
                    TARGET_ROW_CENTER: connector_support,
                },
                incompatible_status=(
                    "INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE"
                ),
            )
            aggregate["extension_candidate_count"] += 1
            aggregate["search_node_count"] += int(stats["search_node_count"])
            aggregate["empty_domain_count"] += int(stats["empty_domain_count"])
            aggregate["detected_solution_count"] += int(
                stats["detected_solution_count"]
            )
            aggregate[f"initial_status:{stats['initial_status']}"] += 1
            aggregate[f"solution_search_status:{stats['solution_search_status']}"] += 1
            for depth, count in dict(stats["empty_domain_depth_histogram"]).items():
                empty_depths[str(depth)] += int(count)

            summary = {
                "prefix_survivor_index": prefix_index,
                "first_step_center": first_center,
                "first_step_support": prefix["first_step_support"],
                "auxiliary_target_support": prefix["auxiliary_target_support"],
                "label_6_supply_support": _bit_labels(label_6_support),
                "label_6_supply_support_size": label_6_support.bit_count(),
                "label_6_supply_trigger_options_inside_closure": [
                    label
                    for label in _bit_labels(label_6_support)
                    if label in set(TARGET_DELETION_SEED) | {first_center}
                ],
                **stats,
            }
            extension_summaries.append(summary)
            if int(stats["detected_solution_count"]):
                extension_survivors.append(summary)

    return {
        "extension_summaries": extension_summaries,
        "aggregate": dict(sorted(aggregate.items())),
        "empty_domain_depth_histogram": dict(sorted(empty_depths.items())),
        "survivors": extension_survivors,
    }


def _support_generation_summary() -> dict[str, object]:
    first_records = _first_step_support_records()
    connector_records = _connector_support_records()
    first_choice_counts = [
        len(
            _selected_row_choices_for_support(
                int(record["first_step_center"]),
                int(record["support_mask"]),
            )
        )
        for record in first_records
    ]
    connector_choice_counts = [
        len(_selected_row_choices_for_support(TARGET_ROW_CENTER, int(record["support_mask"])))
        for record in connector_records
    ]
    return {
        "first_step_centers": FIRST_STEP_CENTERS,
        "first_step_supports": [
            {
                key: value
                for key, value in record.items()
                if key not in {"support_mask"}
            }
            for record in first_records
        ],
        "center_3_connector_avoiding_supports": [
            {
                key: value
                for key, value in record.items()
                if key not in {"support_mask"}
            }
            for record in connector_records
        ],
        "first_step_support_count_by_center": {
            str(center): sum(
                1
                for record in first_records
                if int(record["first_step_center"]) == center
            )
            for center in FIRST_STEP_CENTERS
        },
        "first_step_support_size_histogram": {
            str(size): count
            for size, count in sorted(
                Counter(int(record["support_size"]) for record in first_records).items()
            )
        },
        "center_3_connector_support_size_histogram": {
            str(size): count
            for size, count in sorted(
                Counter(int(record["support_size"]) for record in connector_records).items()
            )
        },
        "first_step_selected_row_choice_count_histogram": {
            str(size): count
            for size, count in sorted(Counter(first_choice_counts).items())
        },
        "center_3_selected_row_choice_count_histogram": {
            str(size): count
            for size, count in sorted(Counter(connector_choice_counts).items())
        },
        "first_step_total_selected_row_choices_over_supports": sum(
            first_choice_counts
        ),
        "center_3_total_selected_row_choices_over_supports": sum(
            connector_choice_counts
        ),
    }


def build_t12_81_3_first_supply_chains_payload() -> dict[str, object]:
    """Return the deterministic first-step prefix CSP packet."""

    support_generation = _support_generation_summary()
    scan = _scan_csp()
    extension_scan = _immediate_label_6_extension_scan(scan["survivors"])
    aggregate = scan["aggregate"]
    if not isinstance(aggregate, Mapping):
        raise AssertionError("aggregate must be a mapping")
    extension_aggregate = extension_scan["aggregate"]
    if not isinstance(extension_aggregate, Mapping):
        raise AssertionError("extension aggregate must be a mapping")
    implicit_space = (
        int(support_generation["first_step_total_selected_row_choices_over_supports"])
        * int(support_generation["center_3_total_selected_row_choices_over_supports"])
        * (FREE_ROW_REPLACEMENT_COUNT_PER_NON_AUXILIARY_CENTER ** 7)
    )

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This CSP audits the first pre-3 activation support from seed [0,1,4], not a full arbitrary rich-class catalogue.",
            "The connector-avoiding center-3 object is a rich support containing [0,4,6] without 1 or [1,4,6] without 0.",
            "The scan finds three first-step prefix survivors, all starting at center 8; they are boundary cases, not full label-6 supply chains.",
            "No prefix survivor admits an immediate center-6 label-6 supply support under the same filters.",
            "The CSP uses incidence, crossing, pair-cap, and same-center disjointness filters only, not Euclidean realizability.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "target_row_key": TARGET_ROW_KEY,
            "source_record_ids": [81],
            "cyclic_order": CYCLIC_ORDER,
            "deletion_seed": TARGET_DELETION_SEED,
            "connector_pair": CONNECTOR_PAIR,
            "target_center": TARGET_ROW_CENTER,
            "eventual_supply_label": SUPPLY_CENTER,
            "first_step_centers": FIRST_STEP_CENTERS,
            "first_step_support_count": len(_first_step_support_records()),
            "center_3_connector_avoiding_support_count": len(
                _connector_support_records()
            ),
            "fixed_prefix_support_pair_count": len(
                scan["prefix_pair_summaries"]
            ),
            "free_row_replacement_count_per_non_auxiliary_center": (
                FREE_ROW_REPLACEMENT_COUNT_PER_NON_AUXILIARY_CENTER
            ),
            "implicit_selected_assignment_space_size": implicit_space,
            "search_node_count": aggregate["search_node_count"],
            "empty_domain_count": aggregate["empty_domain_count"],
            "initial_auxiliary_support_pair_incompatible_count": aggregate[
                "initial_status:INITIAL_AUXILIARY_SUPPORT_PAIR_INCOMPATIBLE"
            ],
            "initial_auxiliary_support_pair_searched_count": aggregate[
                "initial_status:SEARCH_EXHAUSTED"
            ],
            "detected_solution_count": aggregate["detected_solution_count"],
            "surviving_prefix_pair_count": len(scan["survivors"]),
            "surviving_prefix_first_step_centers": sorted(
                {
                    int(survivor["first_step_center"])
                    for survivor in scan["survivors"]
                }
            ),
            "immediate_label_6_extension_candidate_count": extension_aggregate[
                "extension_candidate_count"
            ],
            "immediate_label_6_extension_detected_solution_count": (
                extension_aggregate["detected_solution_count"]
            ),
            "surviving_immediate_label_6_extension_count": len(
                extension_scan["survivors"]
            ),
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "The three first-step prefix survivors are not full pre-3 "
                "label-6 supply chains: none admits an immediate center-6 "
                "supply support under the same filters. Longer chains after "
                "the first center-8 activation, richer catalogues with "
                "additional auxiliary supports, and a minimality theorem "
                "forcing supports into the audited catalogue remain open."
            ),
        },
        "support_generation": support_generation,
        "prefix_pair_audit": {
            "aggregate": scan["aggregate"],
            "per_first_step_center": scan["per_first_step_center"],
            "empty_domain_depth_histogram": scan["empty_domain_depth_histogram"],
            "stored_prefix_pair_summary_count": 0,
            "omitted_prefix_pair_summary_count": len(scan["prefix_pair_summaries"]),
            "omission_reason": (
                "Failed prefix-pair summaries are regenerated by the checker; "
                "the artifact stores only aggregate counts plus survivor records "
                "to keep the certificate compact."
            ),
        },
        "survivors": scan["survivors"],
        "immediate_label_6_extension_scan": {
            "aggregate": extension_scan["aggregate"],
            "empty_domain_depth_histogram": extension_scan[
                "empty_domain_depth_histogram"
            ],
            "stored_extension_summary_count": 0,
            "omitted_extension_summary_count": len(
                extension_scan["extension_summaries"]
            ),
            "omission_reason": (
                "Failed immediate-extension summaries are regenerated by the "
                "checker; the artifact stores only aggregate counts because "
                "there are no extension survivors."
            ),
            "survivors": extension_scan["survivors"],
        },
        "source_rich_support_csp": {
            "path": RICH_SUPPORT_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": RICH_SUPPORT_SCHEMA,
            "status": RICH_SUPPORT_STATUS,
            "scan_status": RICH_SUPPORT_SCAN_STATUS,
        },
        "source_trigger_uniqueness_audit": {
            "path": TRIGGER_UNIQUENESS_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": TRIGGER_UNIQUENESS_SCHEMA,
            "status": TRIGGER_UNIQUENESS_STATUS,
            "scan_status": TRIGGER_UNIQUENESS_SCAN_STATUS,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_3_first_supply_chains.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_3_first_supply_chains.py "
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
        "target_center": TARGET_ROW_CENTER,
        "eventual_supply_label": SUPPLY_CENTER,
        "first_step_centers": FIRST_STEP_CENTERS,
        "first_step_support_count": 155,
        "center_3_connector_avoiding_support_count": 30,
        "fixed_prefix_support_pair_count": 4650,
        "free_row_replacement_count_per_non_auxiliary_center": 70,
        "implicit_selected_assignment_space_size": 4983670464500000000,
        "search_node_count": 8852,
        "empty_domain_count": 5339,
        "initial_auxiliary_support_pair_incompatible_count": 3958,
        "initial_auxiliary_support_pair_searched_count": 692,
        "detected_solution_count": 3,
        "surviving_prefix_pair_count": 3,
        "surviving_prefix_first_step_centers": [8],
        "immediate_label_6_extension_candidate_count": 228,
        "immediate_label_6_extension_detected_solution_count": 0,
        "surviving_immediate_label_6_extension_count": 0,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    support_generation = payload.get("support_generation")
    if not isinstance(support_generation, Mapping):
        raise AssertionError("support_generation must be a mapping")
    expected_generation = {
        "first_step_support_count_by_center": {
            "2": 31,
            "5": 31,
            "6": 31,
            "7": 31,
            "8": 31,
        },
        "first_step_support_size_histogram": {
            "4": 25,
            "5": 50,
            "6": 50,
            "7": 25,
            "8": 5,
        },
        "center_3_connector_support_size_histogram": {
            "4": 8,
            "5": 12,
            "6": 8,
            "7": 2,
        },
        "first_step_selected_row_choice_count_histogram": {
            "2": 25,
            "5": 50,
            "15": 50,
            "35": 25,
            "70": 5,
        },
        "center_3_selected_row_choice_count_histogram": {
            "2": 8,
            "5": 12,
            "15": 8,
            "35": 2,
        },
        "first_step_total_selected_row_choices_over_supports": 2275,
        "center_3_total_selected_row_choices_over_supports": 266,
    }
    for key, expected in expected_generation.items():
        if support_generation.get(key) != expected:
            raise AssertionError(
                f"support_generation {key} is {support_generation.get(key)!r}, expected {expected!r}"
            )

    prefix_audit = payload.get("prefix_pair_audit")
    if not isinstance(prefix_audit, Mapping):
        raise AssertionError("prefix_pair_audit must be a mapping")
    if prefix_audit.get("stored_prefix_pair_summary_count") != 0:
        raise AssertionError("failed prefix summaries should stay omitted")
    if prefix_audit.get("omitted_prefix_pair_summary_count") != 4650:
        raise AssertionError("expected 4650 omitted prefix summaries")
    prefix_aggregate = prefix_audit.get("aggregate")
    if not isinstance(prefix_aggregate, Mapping):
        raise AssertionError("prefix aggregate must be a mapping")
    expected_prefix_aggregate = {
        "search_node_count": 8852,
        "empty_domain_count": 5339,
        "detected_solution_count": 3,
        "initial_status:INITIAL_AUXILIARY_SUPPORT_PAIR_INCOMPATIBLE": 3958,
        "initial_status:SEARCH_EXHAUSTED": 692,
        "solution_search_status:EXHAUSTED_NO_SOLUTION": 689,
        "solution_search_status:NOT_SEARCHED_INITIAL_PAIR_INCOMPATIBLE": 3958,
        "solution_search_status:STOPPED_AFTER_FIRST_SOLUTION": 3,
    }
    for key, expected in expected_prefix_aggregate.items():
        if prefix_aggregate.get(key) != expected:
            raise AssertionError(
                f"prefix aggregate {key} is {prefix_aggregate.get(key)!r}, expected {expected!r}"
            )

    survivors = payload.get("survivors")
    if not isinstance(survivors, Sequence) or len(survivors) != 3:
        raise AssertionError("expected three first-step prefix survivors")
    if {
        int(record.get("first_step_center", -1))
        for record in survivors
        if isinstance(record, Mapping)
    } != {8}:
        raise AssertionError("all first-step prefix survivors should start at center 8")

    extension = payload.get("immediate_label_6_extension_scan")
    if not isinstance(extension, Mapping):
        raise AssertionError("immediate_label_6_extension_scan must be a mapping")
    extension_aggregate = extension.get("aggregate")
    if not isinstance(extension_aggregate, Mapping):
        raise AssertionError("extension aggregate must be a mapping")
    expected_extension = {
        "extension_candidate_count": 228,
        "initial_status:INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE": 228,
        "solution_search_status:NOT_SEARCHED_INITIAL_PAIR_INCOMPATIBLE": 228,
        "search_node_count": 0,
        "empty_domain_count": 0,
        "detected_solution_count": 0,
    }
    for key, expected in expected_extension.items():
        if extension_aggregate.get(key) != expected:
            raise AssertionError(
                f"extension aggregate {key} is {extension_aggregate.get(key)!r}, expected {expected!r}"
            )
    if extension.get("survivors") != []:
        raise AssertionError("immediate label-6 extension survivors must be empty")

    source = payload.get("source_rich_support_csp")
    if not isinstance(source, Mapping):
        raise AssertionError("source_rich_support_csp must be a mapping")
    if source.get("schema") != RICH_SUPPORT_SCHEMA:
        raise AssertionError("source rich-support schema drifted")
    if source.get("scan_status") != RICH_SUPPORT_SCAN_STATUS:
        raise AssertionError("source rich-support scan status drifted")

    trigger_source = payload.get("source_trigger_uniqueness_audit")
    if not isinstance(trigger_source, Mapping):
        raise AssertionError("source_trigger_uniqueness_audit must be a mapping")
    if trigger_source.get("schema") != TRIGGER_UNIQUENESS_SCHEMA:
        raise AssertionError("source trigger-uniqueness schema drifted")
    if trigger_source.get("scan_status") != TRIGGER_UNIQUENESS_SCAN_STATUS:
        raise AssertionError("source trigger-uniqueness scan status drifted")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_3_first_supply_chains.py"
    ):
        raise AssertionError("provenance generator drifted")
