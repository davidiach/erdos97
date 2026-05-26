"""Second-step prefix CSP for the bootstrap/T12 81:3 escape.

The first-supply-chain packet leaves three first-step prefix survivors, all
starting with center 8 activated from seed [0,1,4].  This packet widens that
boundary by allowing one more non-target, non-supply center to activate from
the enlarged closure [0,1,4,8], then checks whether the remaining second-step
survivor admits an immediate center-6 label-6 supply support.

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
    _bit_labels,
    _selected_row_choices_for_support,
    _support_masks_containing,
)
from erdos97.bootstrap_t12_81_3_escape_two_row_drop import _row_mask
from erdos97.bootstrap_t12_81_3_first_supply_chains import (
    DEFAULT_ARTIFACT as FIRST_SUPPLY_ARTIFACT,
    SCAN_STATUS as FIRST_SUPPLY_SCAN_STATUS,
    SCHEMA as FIRST_SUPPLY_SCHEMA,
    STATUS as FIRST_SUPPLY_STATUS,
    _search_auxiliary_support_catalogue,
    assert_expected_payload as assert_first_supply_payload,
    load_artifact as load_first_supply_artifact,
)
from erdos97.bootstrap_t12_81_3_order_escape import (
    TARGET_DELETION_SEED,
    TARGET_ROW_CENTER,
    TARGET_ROW_KEY,
)


SCHEMA = "erdos97.bootstrap_t12_81_3_second_supply_chains.v1"
STATUS = "BOOTSTRAP_T12_81_3_SECOND_SUPPLY_CHAINS_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "ONE_SECOND_STEP_PREFIX_SURVIVOR_BUT_NO_IMMEDIATE_LABEL6_EXTENSION"
CLAIM_SCOPE = (
    "Second-step prefix CSP for the 81:3 pre-3 label-6 escape. Starting from "
    "the three stored first-step prefix survivors, all of which activate "
    "center 8 from seed [0,1,4], the scan allows one additional non-target, "
    "non-supply center to activate from the enlarged closure [0,1,4,8]. The "
    "additional support may be any rich support of size 4 through 8 containing "
    "at least three closure labels. Selected rows at auxiliary centers may be "
    "4-subsets of their support or disjoint 4-sets; all other selected rows "
    "are arbitrary 4-sets. Exact backtracking leaves one second-step prefix "
    "survivor, with second center 2 and support [1,3,4,8], and then proves "
    "this survivor admits no immediate center-6 label-6 supply support under "
    "the same basic filters. This is not a proof of genuine rich-class order, "
    "not a proof of row forcing, not a proof of n=9, not a proof of the "
    "bridge, and not a counterexample. Companion second-step and post-8 "
    "packets audit longer distinct-center continuations of the same model."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_3_second_supply_chains.json"
)
FREE_ROW_REPLACEMENT_COUNT_PER_NON_AUXILIARY_CENTER = 70


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _activation_support_masks_after(center: int, closure: Sequence[int]) -> list[int]:
    """Return supports at ``center`` enabled by at least three closure labels."""

    closure_mask = _row_mask(closure)
    return [
        support
        for support in _support_masks_containing(center, [])
        if (support & closure_mask).bit_count() >= 3
    ]


def _prefix_survivors(
    first_supply_artifact: Path = FIRST_SUPPLY_ARTIFACT,
) -> list[dict[str, object]]:
    first_payload = load_first_supply_artifact(first_supply_artifact)
    assert_first_supply_payload(first_payload)
    survivors = first_payload.get("survivors")
    if not isinstance(survivors, Sequence):
        raise AssertionError("first-supply survivors must be a sequence")
    records: list[dict[str, object]] = []
    for index, survivor in enumerate(survivors):
        if not isinstance(survivor, Mapping):
            raise AssertionError("first-supply survivor records must be mappings")
        records.append(
            {
                "prefix_survivor_index": index,
                "first_step_center": int(survivor["first_step_center"]),
                "first_step_support": _int_list(survivor["first_step_support"]),
                "auxiliary_target_support": _int_list(
                    survivor["auxiliary_target_support"]
                ),
                "target_center_activation_triple": _int_list(
                    survivor["target_center_activation_triple"]
                ),
            }
        )
    return records


def _second_step_centers_after(prefix: Mapping[str, object]) -> list[int]:
    closure = set(TARGET_DELETION_SEED) | {int(prefix["first_step_center"])}
    excluded = closure | {TARGET_ROW_CENTER, SUPPLY_CENTER}
    return [label for label in CYCLIC_ORDER if label not in excluded]


def _prefix_auxiliary_supports(prefix: Mapping[str, object]) -> dict[int, int]:
    return {
        int(prefix["first_step_center"]): _row_mask(
            _int_list(prefix["first_step_support"])
        ),
        TARGET_ROW_CENTER: _row_mask(_int_list(prefix["auxiliary_target_support"])),
    }


def _search_second_step_prefix(
    prefix: Mapping[str, object],
    second_step_center: int,
    second_step_support: int,
) -> dict[str, object]:
    auxiliary_supports = _prefix_auxiliary_supports(prefix)
    auxiliary_supports[second_step_center] = second_step_support
    return _search_auxiliary_support_catalogue(
        auxiliary_supports,
        incompatible_status="INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE",
    )


def _scan_second_step_prefixes(
    prefixes: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    prefix_summaries: list[dict[str, object]] = []
    aggregate = Counter()
    per_prefix: dict[int, Counter[str]] = {
        int(prefix["prefix_survivor_index"]): Counter() for prefix in prefixes
    }
    per_prefix_second_center: dict[str, Counter[str]] = {}
    empty_depths: Counter[str] = Counter()
    survivors: list[dict[str, object]] = []

    for prefix in prefixes:
        prefix_index = int(prefix["prefix_survivor_index"])
        closure = sorted(set(TARGET_DELETION_SEED) | {int(prefix["first_step_center"])})
        for second_center in _second_step_centers_after(prefix):
            key = f"{prefix_index}:{second_center}"
            per_prefix_second_center[key] = Counter()
            for second_support in _activation_support_masks_after(second_center, closure):
                stats = _search_second_step_prefix(
                    prefix,
                    second_center,
                    second_support,
                )
                aggregate["candidate_count"] += 1
                aggregate["search_node_count"] += int(stats["search_node_count"])
                aggregate["empty_domain_count"] += int(stats["empty_domain_count"])
                aggregate["detected_solution_count"] += int(
                    stats["detected_solution_count"]
                )
                aggregate[f"initial_status:{stats['initial_status']}"] += 1
                aggregate[
                    f"solution_search_status:{stats['solution_search_status']}"
                ] += 1

                per_prefix[prefix_index]["second_step_support_candidate_count"] += 1
                per_prefix[prefix_index]["search_node_count"] += int(
                    stats["search_node_count"]
                )
                per_prefix[prefix_index]["empty_domain_count"] += int(
                    stats["empty_domain_count"]
                )
                per_prefix[prefix_index]["detected_solution_count"] += int(
                    stats["detected_solution_count"]
                )
                per_prefix[prefix_index][f"initial_status:{stats['initial_status']}"] += 1
                per_prefix[prefix_index][
                    f"solution_search_status:{stats['solution_search_status']}"
                ] += 1

                per_prefix_second_center[key]["support_candidate_count"] += 1
                per_prefix_second_center[key]["search_node_count"] += int(
                    stats["search_node_count"]
                )
                per_prefix_second_center[key]["empty_domain_count"] += int(
                    stats["empty_domain_count"]
                )
                per_prefix_second_center[key]["detected_solution_count"] += int(
                    stats["detected_solution_count"]
                )
                per_prefix_second_center[key][
                    f"initial_status:{stats['initial_status']}"
                ] += 1
                per_prefix_second_center[key][
                    f"solution_search_status:{stats['solution_search_status']}"
                ] += 1

                for depth, count in dict(stats["empty_domain_depth_histogram"]).items():
                    empty_depths[str(depth)] += int(count)

                summary = {
                    "prefix_survivor_index": prefix_index,
                    "first_step_center": prefix["first_step_center"],
                    "first_step_support": prefix["first_step_support"],
                    "auxiliary_target_support": prefix["auxiliary_target_support"],
                    "second_step_center": second_center,
                    "second_step_support": _bit_labels(second_support),
                    "second_step_support_size": second_support.bit_count(),
                    "second_step_closure_before_activation": closure,
                    "selected_row_choice_count_at_first_step_center": len(
                        _selected_row_choices_for_support(
                            int(prefix["first_step_center"]),
                            _row_mask(_int_list(prefix["first_step_support"])),
                        )
                    ),
                    "selected_row_choice_count_at_target_center": len(
                        _selected_row_choices_for_support(
                            TARGET_ROW_CENTER,
                            _row_mask(_int_list(prefix["auxiliary_target_support"])),
                        )
                    ),
                    "selected_row_choice_count_at_second_step_center": len(
                        _selected_row_choices_for_support(
                            second_center,
                            second_support,
                        )
                    ),
                    **stats,
                }
                prefix_summaries.append(summary)
                if int(stats["detected_solution_count"]):
                    survivors.append(summary)

    return {
        "second_step_prefix_summaries": prefix_summaries,
        "aggregate": dict(sorted(aggregate.items())),
        "per_prefix_survivor": {
            str(prefix_index): dict(sorted(counter.items()))
            for prefix_index, counter in per_prefix.items()
        },
        "per_prefix_second_center": {
            key: dict(sorted(counter.items()))
            for key, counter in sorted(per_prefix_second_center.items())
        },
        "empty_domain_depth_histogram": dict(
            sorted(empty_depths.items(), key=lambda item: int(item[0]))
        ),
        "survivors": survivors,
    }


def _immediate_label_6_extension_scan(
    second_step_survivors: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    extension_summaries: list[dict[str, object]] = []
    extension_survivors: list[dict[str, object]] = []
    aggregate = Counter()
    empty_depths: Counter[str] = Counter()

    for survivor_index, survivor in enumerate(second_step_survivors):
        first_center = int(survivor["first_step_center"])
        second_center = int(survivor["second_step_center"])
        closure = sorted(set(TARGET_DELETION_SEED) | {first_center, second_center})
        auxiliary_supports = {
            first_center: _row_mask(_int_list(survivor["first_step_support"])),
            TARGET_ROW_CENTER: _row_mask(
                _int_list(survivor["auxiliary_target_support"])
            ),
            second_center: _row_mask(_int_list(survivor["second_step_support"])),
        }
        for label_6_support in _activation_support_masks_after(SUPPLY_CENTER, closure):
            stats = _search_auxiliary_support_catalogue(
                {**auxiliary_supports, SUPPLY_CENTER: label_6_support},
                incompatible_status=(
                    "INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE"
                ),
            )
            aggregate["candidate_count"] += 1
            aggregate["search_node_count"] += int(stats["search_node_count"])
            aggregate["empty_domain_count"] += int(stats["empty_domain_count"])
            aggregate["detected_solution_count"] += int(
                stats["detected_solution_count"]
            )
            aggregate[f"initial_status:{stats['initial_status']}"] += 1
            aggregate[
                f"solution_search_status:{stats['solution_search_status']}"
            ] += 1
            for depth, count in dict(stats["empty_domain_depth_histogram"]).items():
                empty_depths[str(depth)] += int(count)

            summary = {
                "second_step_prefix_survivor_index": survivor_index,
                "prefix_survivor_index": survivor["prefix_survivor_index"],
                "first_step_center": first_center,
                "second_step_center": second_center,
                "closure_before_label_6": closure,
                "label_6_supply_support": _bit_labels(label_6_support),
                "label_6_supply_support_size": label_6_support.bit_count(),
                "label_6_supply_trigger_options_inside_closure": [
                    label for label in _bit_labels(label_6_support) if label in closure
                ],
                **stats,
            }
            extension_summaries.append(summary)
            if int(stats["detected_solution_count"]):
                extension_survivors.append(summary)

    return {
        "extension_summaries": extension_summaries,
        "aggregate": dict(sorted(aggregate.items())),
        "empty_domain_depth_histogram": dict(
            sorted(empty_depths.items(), key=lambda item: int(item[0]))
        ),
        "survivors": extension_survivors,
    }


def _support_generation_summary(
    prefixes: Sequence[Mapping[str, object]],
    second_survivors: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    second_total_choices = 0
    support_counts: dict[str, int] = {}
    support_histograms: dict[str, dict[str, int]] = {}
    choice_histograms: dict[str, dict[str, int]] = {}
    centers_by_prefix: dict[str, list[int]] = {}

    for prefix in prefixes:
        prefix_index = int(prefix["prefix_survivor_index"])
        closure = sorted(set(TARGET_DELETION_SEED) | {int(prefix["first_step_center"])})
        centers = _second_step_centers_after(prefix)
        centers_by_prefix[str(prefix_index)] = centers
        for center in centers:
            key = f"{prefix_index}:{center}"
            supports = _activation_support_masks_after(center, closure)
            choice_counts = [
                len(_selected_row_choices_for_support(center, support))
                for support in supports
            ]
            support_counts[key] = len(supports)
            support_histograms[key] = {
                str(size): count
                for size, count in sorted(
                    Counter(support.bit_count() for support in supports).items()
                )
            }
            choice_histograms[key] = {
                str(size): count
                for size, count in sorted(Counter(choice_counts).items())
            }
            second_total_choices += sum(choice_counts)

    extension_supports: list[dict[str, object]] = []
    extension_total_choices = 0
    for survivor_index, survivor in enumerate(second_survivors):
        closure = sorted(
            set(TARGET_DELETION_SEED)
            | {int(survivor["first_step_center"]), int(survivor["second_step_center"])}
        )
        supports = _activation_support_masks_after(SUPPLY_CENTER, closure)
        choice_counts = [
            len(_selected_row_choices_for_support(SUPPLY_CENTER, support))
            for support in supports
        ]
        extension_total_choices += sum(choice_counts)
        extension_supports.append(
            {
                "second_step_prefix_survivor_index": survivor_index,
                "closure_before_label_6": closure,
                "label_6_supply_support_count": len(supports),
                "label_6_supply_support_size_histogram": {
                    str(size): count
                    for size, count in sorted(
                        Counter(support.bit_count() for support in supports).items()
                    )
                },
                "label_6_supply_selected_row_choice_count_histogram": {
                    str(size): count
                    for size, count in sorted(Counter(choice_counts).items())
                },
                "label_6_supply_total_selected_row_choices_over_supports": sum(
                    choice_counts
                ),
            }
        )

    return {
        "first_step_prefix_survivor_count": len(prefixes),
        "first_step_survivors_used": [
            {
                "prefix_survivor_index": int(prefix["prefix_survivor_index"]),
                "first_step_center": int(prefix["first_step_center"]),
                "first_step_support": prefix["first_step_support"],
                "auxiliary_target_support": prefix["auxiliary_target_support"],
                "target_center_activation_triple": prefix[
                    "target_center_activation_triple"
                ],
            }
            for prefix in prefixes
        ],
        "second_step_centers_by_prefix": centers_by_prefix,
        "second_step_support_count_by_prefix_center": support_counts,
        "second_step_support_size_histogram_by_prefix_center": support_histograms,
        "second_step_selected_row_choice_count_histogram_by_prefix_center": (
            choice_histograms
        ),
        "first_step_selected_row_choice_count_per_survivor": [
            len(
                _selected_row_choices_for_support(
                    int(prefix["first_step_center"]),
                    _row_mask(_int_list(prefix["first_step_support"])),
                )
            )
            for prefix in prefixes
        ],
        "target_center_selected_row_choice_count_per_survivor": [
            len(
                _selected_row_choices_for_support(
                    TARGET_ROW_CENTER,
                    _row_mask(_int_list(prefix["auxiliary_target_support"])),
                )
            )
            for prefix in prefixes
        ],
        "second_step_total_selected_row_choices_over_supports": second_total_choices,
        "immediate_label_6_extension_support_generation": extension_supports,
        "immediate_label_6_total_selected_row_choices_over_supports": (
            extension_total_choices
        ),
    }


def build_t12_81_3_second_supply_chains_payload() -> dict[str, object]:
    """Return the deterministic second-step prefix CSP packet."""

    prefixes = _prefix_survivors()
    second_scan = _scan_second_step_prefixes(prefixes)
    second_survivors = second_scan["survivors"]
    if not isinstance(second_survivors, Sequence):
        raise AssertionError("second-step survivors must be a sequence")
    extension_scan = _immediate_label_6_extension_scan(second_survivors)
    support_generation = _support_generation_summary(prefixes, second_survivors)

    aggregate = second_scan["aggregate"]
    if not isinstance(aggregate, Mapping):
        raise AssertionError("second-step aggregate must be a mapping")
    extension_aggregate = extension_scan["aggregate"]
    if not isinstance(extension_aggregate, Mapping):
        raise AssertionError("extension aggregate must be a mapping")

    implicit_space = (
        sum(
            len(
                _selected_row_choices_for_support(
                    int(prefix["first_step_center"]),
                    _row_mask(_int_list(prefix["first_step_support"])),
                )
            )
            * len(
                _selected_row_choices_for_support(
                    TARGET_ROW_CENTER,
                    _row_mask(_int_list(prefix["auxiliary_target_support"])),
                )
            )
            * sum(
                len(_selected_row_choices_for_support(center, support))
                for center in _second_step_centers_after(prefix)
                for support in _activation_support_masks_after(
                    center,
                    sorted(
                        set(TARGET_DELETION_SEED)
                        | {int(prefix["first_step_center"])}
                    ),
                )
            )
            for prefix in prefixes
        )
        * (FREE_ROW_REPLACEMENT_COUNT_PER_NON_AUXILIARY_CENTER ** 6)
    )
    extension_implicit_space = (
        sum(
            len(
                _selected_row_choices_for_support(
                    int(survivor["first_step_center"]),
                    _row_mask(_int_list(survivor["first_step_support"])),
                )
            )
            * len(
                _selected_row_choices_for_support(
                    TARGET_ROW_CENTER,
                    _row_mask(_int_list(survivor["auxiliary_target_support"])),
                )
            )
            * len(
                _selected_row_choices_for_support(
                    int(survivor["second_step_center"]),
                    _row_mask(_int_list(survivor["second_step_support"])),
                )
            )
            * sum(
                len(_selected_row_choices_for_support(SUPPLY_CENTER, support))
                for support in _activation_support_masks_after(
                    SUPPLY_CENTER,
                    sorted(
                        set(TARGET_DELETION_SEED)
                        | {
                            int(survivor["first_step_center"]),
                            int(survivor["second_step_center"]),
                        }
                    ),
                )
            )
            for survivor in second_survivors
        )
        * (FREE_ROW_REPLACEMENT_COUNT_PER_NON_AUXILIARY_CENTER ** 5)
    )

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            (
                "This CSP starts from the three stored first-step prefix "
                "survivors; it is not a full arbitrary rich-class catalogue."
            ),
            (
                "The second activation is one non-target, non-supply center "
                "after center 8, not an arbitrary-length chain."
            ),
            (
                "The connector-avoiding center-3 object is inherited from each "
                "first-step prefix survivor."
            ),
            (
                "No surviving second-step prefix admits an immediate center-6 "
                "label-6 supply support under the same filters."
            ),
            (
                "The companion second-step and post-8 packets audit longer "
                "distinct-center continuations of this same support-chain model."
            ),
            (
                "The CSP uses incidence, crossing, pair-cap, and same-center "
                "disjointness filters only, not Euclidean realizability."
            ),
            (
                "No n=9 finite-case status, bridge status, official status, "
                "or counterexample status changes."
            ),
        ],
        "summary": {
            "target_row_key": TARGET_ROW_KEY,
            "source_record_ids": [81],
            "cyclic_order": CYCLIC_ORDER,
            "deletion_seed": TARGET_DELETION_SEED,
            "connector_pair": CONNECTOR_PAIR,
            "target_center": TARGET_ROW_CENTER,
            "eventual_supply_label": SUPPLY_CENTER,
            "first_step_survivor_count": len(prefixes),
            "second_step_centers_per_prefix": [2, 5, 7],
            "second_step_support_count_per_prefix_center": 76,
            "fixed_second_step_prefix_count": aggregate["candidate_count"],
            "free_row_replacement_count_per_non_auxiliary_center": (
                FREE_ROW_REPLACEMENT_COUNT_PER_NON_AUXILIARY_CENTER
            ),
            "implicit_selected_assignment_space_size": implicit_space,
            "search_node_count": aggregate["search_node_count"],
            "empty_domain_count": aggregate["empty_domain_count"],
            "initial_auxiliary_support_catalogue_incompatible_count": aggregate[
                "initial_status:INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE"
            ],
            "initial_auxiliary_support_catalogue_searched_count": aggregate[
                "initial_status:SEARCH_EXHAUSTED"
            ],
            "detected_solution_count": aggregate["detected_solution_count"],
            "surviving_second_step_prefix_count": len(second_survivors),
            "surviving_second_step_prefix_indices": [
                int(survivor["prefix_survivor_index"])
                for survivor in second_survivors
            ],
            "surviving_second_step_centers": sorted(
                {int(survivor["second_step_center"]) for survivor in second_survivors}
            ),
            "immediate_label_6_extension_candidate_count": extension_aggregate[
                "candidate_count"
            ],
            "immediate_label_6_extension_implicit_selected_assignment_space_size": (
                extension_implicit_space
            ),
            "immediate_label_6_extension_detected_solution_count": (
                extension_aggregate["detected_solution_count"]
            ),
            "surviving_immediate_label_6_extension_count": len(
                extension_scan["survivors"]
            ),
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "Within this packet, the remaining second-step prefix survivor "
                "is not a full pre-3 label-6 supply chain: it has no immediate "
                "center-6 supply support under the same filters. Companion "
                "second-step and post-8 packets audit longer distinct-center "
                "continuations. Repeated or multiple supports, richer catalogues "
                "with additional auxiliary supports, and a minimality theorem "
                "forcing supports into the audited catalogue remain outside "
                "this support-chain model."
            ),
        },
        "support_generation": support_generation,
        "second_step_prefix_audit": {
            "aggregate": second_scan["aggregate"],
            "per_prefix_survivor": second_scan["per_prefix_survivor"],
            "per_prefix_second_center": second_scan["per_prefix_second_center"],
            "empty_domain_depth_histogram": second_scan[
                "empty_domain_depth_histogram"
            ],
            "stored_second_step_summary_count": 0,
            "omitted_second_step_summary_count": len(
                second_scan["second_step_prefix_summaries"]
            ),
            "omission_reason": (
                "Failed second-step prefix summaries are regenerated by the "
                "checker; the artifact stores only aggregate counts plus "
                "survivor records to keep the certificate compact."
            ),
        },
        "survivors": second_survivors,
        "immediate_label_6_extension_scan": {
            "aggregate": extension_scan["aggregate"],
            "support_generation": support_generation[
                "immediate_label_6_extension_support_generation"
            ],
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
        "source_first_supply_chains": {
            "path": FIRST_SUPPLY_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": FIRST_SUPPLY_SCHEMA,
            "status": FIRST_SUPPLY_STATUS,
            "scan_status": FIRST_SUPPLY_SCAN_STATUS,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_3_second_supply_chains.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_3_second_supply_chains.py "
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
        "first_step_survivor_count": 3,
        "second_step_centers_per_prefix": [2, 5, 7],
        "second_step_support_count_per_prefix_center": 76,
        "fixed_second_step_prefix_count": 684,
        "free_row_replacement_count_per_non_auxiliary_center": 70,
        "implicit_selected_assignment_space_size": 3617000856000000,
        "search_node_count": 303,
        "empty_domain_count": 135,
        "initial_auxiliary_support_catalogue_incompatible_count": 678,
        "initial_auxiliary_support_catalogue_searched_count": 6,
        "detected_solution_count": 1,
        "surviving_second_step_prefix_count": 1,
        "surviving_second_step_prefix_indices": [1],
        "surviving_second_step_centers": [2],
        "immediate_label_6_extension_candidate_count": 118,
        "immediate_label_6_extension_implicit_selected_assignment_space_size": 14386792000000,
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
    if support_generation.get("first_step_prefix_survivor_count") != 3:
        raise AssertionError("expected three first-step prefix survivors")
    if support_generation.get("second_step_total_selected_row_choices_over_supports") != 7686:
        raise AssertionError("second-step selected-row choice total drifted")
    expected_support_histogram = {"4": 17, "5": 28, "6": 22, "7": 8, "8": 1}
    histograms = support_generation.get(
        "second_step_support_size_histogram_by_prefix_center"
    )
    if not isinstance(histograms, Mapping):
        raise AssertionError("second-step support histograms must be a mapping")
    if set(histograms) != {
        "0:2",
        "0:5",
        "0:7",
        "1:2",
        "1:5",
        "1:7",
        "2:2",
        "2:5",
        "2:7",
    }:
        raise AssertionError("second-step prefix/center keys drifted")
    if any(value != expected_support_histogram for value in histograms.values()):
        raise AssertionError("second-step support-size histogram drifted")

    prefix_audit = payload.get("second_step_prefix_audit")
    if not isinstance(prefix_audit, Mapping):
        raise AssertionError("second_step_prefix_audit must be a mapping")
    if prefix_audit.get("stored_second_step_summary_count") != 0:
        raise AssertionError("failed second-step summaries should stay omitted")
    if prefix_audit.get("omitted_second_step_summary_count") != 684:
        raise AssertionError("expected 684 omitted second-step summaries")
    prefix_aggregate = prefix_audit.get("aggregate")
    if not isinstance(prefix_aggregate, Mapping):
        raise AssertionError("second-step aggregate must be a mapping")
    expected_prefix_aggregate = {
        "candidate_count": 684,
        "search_node_count": 303,
        "empty_domain_count": 135,
        "detected_solution_count": 1,
        "initial_status:INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE": 678,
        "initial_status:SEARCH_EXHAUSTED": 6,
        "solution_search_status:EXHAUSTED_NO_SOLUTION": 5,
        "solution_search_status:NOT_SEARCHED_INITIAL_PAIR_INCOMPATIBLE": 678,
        "solution_search_status:STOPPED_AFTER_FIRST_SOLUTION": 1,
    }
    for key, expected in expected_prefix_aggregate.items():
        if prefix_aggregate.get(key) != expected:
            actual = prefix_aggregate.get(key)
            raise AssertionError(
                f"second-step aggregate {key} is {actual!r}, "
                f"expected {expected!r}"
            )

    survivors = payload.get("survivors")
    if not isinstance(survivors, Sequence) or len(survivors) != 1:
        raise AssertionError("expected one second-step prefix survivor")
    survivor = survivors[0]
    if not isinstance(survivor, Mapping):
        raise AssertionError("survivor must be a mapping")
    expected_survivor = {
        "prefix_survivor_index": 1,
        "first_step_center": 8,
        "first_step_support": [0, 1, 4, 7],
        "auxiliary_target_support": [0, 2, 4, 6],
        "second_step_center": 2,
        "second_step_support": [1, 3, 4, 8],
        "second_step_support_size": 4,
        "detected_solution_count": 1,
        "solution_search_status": "STOPPED_AFTER_FIRST_SOLUTION",
    }
    for key, expected in expected_survivor.items():
        if survivor.get(key) != expected:
            raise AssertionError(
                f"survivor {key} is {survivor.get(key)!r}, expected {expected!r}"
            )

    extension = payload.get("immediate_label_6_extension_scan")
    if not isinstance(extension, Mapping):
        raise AssertionError("immediate_label_6_extension_scan must be a mapping")
    extension_aggregate = extension.get("aggregate")
    if not isinstance(extension_aggregate, Mapping):
        raise AssertionError("extension aggregate must be a mapping")
    expected_extension = {
        "candidate_count": 118,
        "initial_status:INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE": 115,
        "initial_status:SEARCH_EXHAUSTED": 3,
        "solution_search_status:EXHAUSTED_NO_SOLUTION": 3,
        "solution_search_status:NOT_SEARCHED_INITIAL_PAIR_INCOMPATIBLE": 115,
        "search_node_count": 34,
        "empty_domain_count": 12,
        "detected_solution_count": 0,
    }
    for key, expected in expected_extension.items():
        if extension_aggregate.get(key) != expected:
            actual = extension_aggregate.get(key)
            raise AssertionError(
                f"extension aggregate {key} is {actual!r}, "
                f"expected {expected!r}"
            )
    if extension.get("survivors") != []:
        raise AssertionError("immediate label-6 extension survivors must be empty")

    source = payload.get("source_first_supply_chains")
    if not isinstance(source, Mapping):
        raise AssertionError("source_first_supply_chains must be a mapping")
    if source.get("schema") != FIRST_SUPPLY_SCHEMA:
        raise AssertionError("source first-supply schema drifted")
    if source.get("scan_status") != FIRST_SUPPLY_SCAN_STATUS:
        raise AssertionError("source first-supply scan status drifted")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_3_second_supply_chains.py"
    ):
        raise AssertionError("provenance generator drifted")
