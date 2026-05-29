"""Repeated-support catalogue audit for the bootstrap/T12 81:3 escape.

The ordered chain-closure CSP leaves four non-supply prefix survivors in a
sequential one-support-per-center model.  This packet tests the smallest
non-sequential widening: add one disjoint same-center support to one already
activated prefix center, then ask whether a center-6 supply support can coexist
under the same exact incidence/crossing bookkeeping.

This is finite proof-mining bookkeeping only.  It is not a Euclidean
realizability theorem and not a proof of the bootstrap bridge.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from erdos97.bootstrap_t12_81_3_chain_closure_csp import (
    DEFAULT_ARTIFACT as CHAIN_CLOSURE_ARTIFACT,
    SCAN_STATUS as CHAIN_CLOSURE_SCAN_STATUS,
    SCHEMA as CHAIN_CLOSURE_SCHEMA,
    STATUS as CHAIN_CLOSURE_STATUS,
    _activation_support_masks,
    build_t12_81_3_chain_closure_csp_payload,
)
from erdos97.bootstrap_t12_81_3_escape_candidates import (
    CONNECTOR_PAIR,
    CYCLIC_ORDER,
    SUPPLY_CENTER,
)
from erdos97.bootstrap_t12_81_3_escape_rich_support_csp import (
    _add_pair_centers,
    _bit_labels,
    _pair_indices,
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


SCHEMA = "erdos97.bootstrap_t12_81_3_repeated_support_catalogue_audit.v1"
STATUS = "BOOTSTRAP_T12_81_3_REPEATED_SUPPORT_CATALOGUE_AUDIT_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "NO_LABEL_6_SUPPLY_EXTENSION_AFTER_ONE_REPEATED_SUPPORT"
CLAIM_SCOPE = (
    "Repeated-support catalogue audit for the 81:3 pre-3 label-6 escape. "
    "Starting from the four ordered chain-closure prefix survivors, the scan "
    "adds one disjoint same-center support at one already activated prefix "
    "center, then tests every eligible center-6 activation support containing "
    "at least three currently closed labels. Selected rows at centers with "
    "auxiliary supports may be 4-subsets of one support or disjoint from every "
    "support at that center. The exact incidence, crossing, witness-pair, and "
    "same-center-disjointness search leaves no complete selected-row "
    "assignment after the center-6 supply extension. This audits only one "
    "repeated-support layer after the stored prefix survivors; it is not a "
    "proof of support existence, not a proof of genuine rich-class order, not "
    "a proof of row forcing, not a proof of n=9, not a proof of the bridge, "
    "and not a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_3_repeated_support_catalogue_audit.json"
)

SUPPORT_CATALOGUE_INCOMPATIBLE = "INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE"
SEARCH_EXHAUSTED = "SEARCH_EXHAUSTED"
NOT_SEARCHED_INCOMPATIBLE = "NOT_SEARCHED_INITIAL_CATALOGUE_INCOMPATIBLE"
STOPPED_AFTER_FIRST_SOLUTION = "STOPPED_AFTER_FIRST_SOLUTION"
EXHAUSTED_NO_SOLUTION = "EXHAUSTED_NO_SOLUTION"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _selected_row_choices_for_supports(
    center: int,
    support_masks: Sequence[int],
) -> list[int]:
    """Rows compatible with every auxiliary support at ``center``."""

    choices = _all_replacement_row_masks(center)
    for support_mask in support_masks:
        choices = [
            row_mask
            for row_mask in choices
            if (row_mask & ~support_mask) == 0 or not (row_mask & support_mask)
        ]
    return sorted(set(choices), key=lambda mask: (mask.bit_count(), _bit_labels(mask)))


def _build_multi_pair_centers(
    auxiliary_supports: Mapping[int, Sequence[int]],
    selected: Mapping[int, Sequence[int]],
) -> dict[int, set[int]]:
    pair_centers: dict[int, set[int]] = {}
    for center, support_masks in auxiliary_supports.items():
        for support_mask in support_masks:
            _add_pair_centers(center, support_mask, pair_centers)
    for center, row_masks in selected.items():
        for row_mask in row_masks:
            _add_pair_centers(center, row_mask, pair_centers)
    return pair_centers


def _initial_catalogue_compatible(
    auxiliary_supports: Mapping[int, Sequence[int]],
) -> bool:
    for center, support_masks in auxiliary_supports.items():
        for left_index, left_support in enumerate(support_masks):
            for right_support in support_masks[left_index + 1 :]:
                if left_support & right_support:
                    return False

    centers = sorted(auxiliary_supports)
    for left_index, center_a in enumerate(centers):
        for center_b in centers[left_index + 1 :]:
            for support_a in auxiliary_supports[center_a]:
                for support_b in auxiliary_supports[center_b]:
                    if not _support_pair_compatible(
                        center_a,
                        support_a,
                        center_b,
                        support_b,
                    ):
                        return False

    pair_centers = _build_multi_pair_centers(auxiliary_supports, {})
    return all(len(centers_for_pair) <= 2 for centers_for_pair in pair_centers.values())


def _compatible_with_multisupport_catalogue(
    center: int,
    row_mask: int,
    auxiliary_supports: Mapping[int, Sequence[int]],
    selected: Mapping[int, Sequence[int]],
    pair_centers: Mapping[int, set[int]],
) -> bool:
    for pair_index in _pair_indices(row_mask):
        centers = pair_centers.get(pair_index, set())
        if center not in centers and len(centers) >= 2:
            return False

    for other_center, support_masks in auxiliary_supports.items():
        if other_center == center:
            continue
        for support_mask in support_masks:
            if not _support_pair_compatible(
                center,
                row_mask,
                other_center,
                support_mask,
            ):
                return False

    for other_center, row_masks in selected.items():
        if other_center == center:
            continue
        for other_row in row_masks:
            if not _support_pair_compatible(center, row_mask, other_center, other_row):
                return False
    return True


def _search_multi_support_catalogue(
    auxiliary_supports: Mapping[int, Sequence[int]],
) -> dict[str, object]:
    normalized_supports = {
        center: sorted(set(support_masks), key=lambda mask: (mask.bit_count(), _bit_labels(mask)))
        for center, support_masks in auxiliary_supports.items()
    }
    if not _initial_catalogue_compatible(normalized_supports):
        return {
            "initial_status": SUPPORT_CATALOGUE_INCOMPATIBLE,
            "search_node_count": 0,
            "empty_domain_count": 0,
            "detected_solution_count": 0,
            "max_depth": 0,
            "empty_domain_depth_histogram": {},
            "first_solution_selected_rows": None,
            "solution_search_status": NOT_SEARCHED_INCOMPATIBLE,
        }

    selected: dict[int, list[int]] = {}
    pair_centers = _build_multi_pair_centers(normalized_supports, selected)
    choices = {center: _all_replacement_row_masks(center) for center in CYCLIC_ORDER}
    for center, support_masks in normalized_supports.items():
        choices[center] = _selected_row_choices_for_supports(center, support_masks)

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
                str(row_center): [_bit_labels(row_mask) for row_mask in row_masks]
                for row_center, row_masks in sorted(selected.items())
            }
            stopped_after_solution = True
            return True

        best_center: int | None = None
        best_options: list[int] | None = None
        for candidate_center in LABELS:
            if candidate_center in selected:
                continue
            options = [
                row_mask
                for row_mask in choices[candidate_center]
                if _compatible_with_multisupport_catalogue(
                    candidate_center,
                    row_mask,
                    normalized_supports,
                    selected,
                    pair_centers,
                )
            ]
            if best_options is None or len(options) < len(best_options):
                best_center = candidate_center
                best_options = options
            if not options:
                stats["empty_domain_count"] += 1
                empty_depths[depth] += 1
                return False

        if best_center is None or best_options is None:
            raise AssertionError("search reached inconsistent assignment state")
        for row_mask in best_options:
            selected[best_center] = [row_mask]
            pair_centers = _build_multi_pair_centers(normalized_supports, selected)
            if search():
                return True
            del selected[best_center]
            pair_centers = _build_multi_pair_centers(normalized_supports, selected)
        return False

    search()
    stats["initial_status"] = SEARCH_EXHAUSTED
    stats["empty_domain_depth_histogram"] = {
        str(depth): count for depth, count in sorted(empty_depths.items())
    }
    stats["first_solution_selected_rows"] = first_solution
    stats["solution_search_status"] = (
        STOPPED_AFTER_FIRST_SOLUTION if stopped_after_solution else EXHAUSTED_NO_SOLUTION
    )
    return stats


def _compact_catalogue(
    auxiliary_supports: Mapping[int, Sequence[int]],
) -> dict[str, list[list[int]]]:
    return {
        str(center): [_bit_labels(mask) for mask in support_masks]
        for center, support_masks in sorted(auxiliary_supports.items())
    }


def _prefix_auxiliary_supports(
    prefix: Mapping[str, object],
) -> dict[int, list[int]]:
    supports: dict[int, list[int]] = {
        TARGET_ROW_CENTER: [_row_mask(prefix["connector_support"])]
    }
    chain = prefix.get("chain")
    if not isinstance(chain, Sequence):
        raise AssertionError("prefix chain must be a sequence")
    for step in chain:
        if not isinstance(step, Mapping):
            raise AssertionError("prefix chain step must be a mapping")
        center = int(step["center"])
        supports.setdefault(center, []).append(_row_mask(step["support"]))
    return supports


def _prefix_closure(prefix: Mapping[str, object]) -> frozenset[int]:
    chain_centers = prefix.get("chain_centers")
    if not isinstance(chain_centers, Sequence):
        raise AssertionError("chain_centers must be a sequence")
    return frozenset({*TARGET_DELETION_SEED, *(int(center) for center in chain_centers)})


def _repeated_support_masks(center: int, existing_supports: Sequence[int]) -> list[int]:
    used_mask = 0
    for support_mask in existing_supports:
        used_mask |= support_mask
    available = [label for label in CYCLIC_ORDER if label != center and not (used_mask & (1 << label))]
    if len(available) < 4:
        return []
    repeated_masks: list[int] = []
    for mask in range(1 << len(available)):
        support = [label for bit, label in enumerate(available) if mask & (1 << bit)]
        if len(support) >= 4:
            repeated_masks.append(_row_mask(support))
    return sorted(repeated_masks, key=lambda value: (value.bit_count(), _bit_labels(value)))


def _repeated_support_candidates(
    prefix_index: int,
    prefix: Mapping[str, object],
) -> list[dict[str, object]]:
    base_supports = _prefix_auxiliary_supports(prefix)
    records: list[dict[str, object]] = []
    for center in sorted(base_supports):
        if center == TARGET_ROW_CENTER:
            continue
        existing_supports = base_supports[center]
        for repeated_support in _repeated_support_masks(center, existing_supports):
            candidate_supports = {
                support_center: list(support_masks)
                for support_center, support_masks in base_supports.items()
            }
            candidate_supports[center].append(repeated_support)
            records.append(
                {
                    "prefix_survivor_index": prefix_index,
                    "connector_support": prefix["connector_support"],
                    "chain_centers": prefix["chain_centers"],
                    "chain": prefix["chain"],
                    "repeated_center": center,
                    "existing_supports_at_repeated_center": [
                        _bit_labels(mask) for mask in existing_supports
                    ],
                    "repeated_support": _bit_labels(repeated_support),
                    "repeated_support_size": repeated_support.bit_count(),
                    "closure_before_supply": sorted(_prefix_closure(prefix)),
                    "auxiliary_support_catalogue": _compact_catalogue(
                        candidate_supports
                    ),
                    "_support_masks": candidate_supports,
                }
            )
    return records


def _record_stats(
    aggregate: Counter[str],
    empty_depths: Counter[str],
    stats: Mapping[str, object],
) -> None:
    aggregate["search_node_count"] += int(stats["search_node_count"])
    aggregate["empty_domain_count"] += int(stats["empty_domain_count"])
    aggregate["detected_solution_count"] += int(stats["detected_solution_count"])
    aggregate[f"initial_status:{stats['initial_status']}"] += 1
    aggregate[f"solution_search_status:{stats['solution_search_status']}"] += 1
    for depth, count in dict(stats["empty_domain_depth_histogram"]).items():
        empty_depths[str(depth)] += int(count)


def _strip_internal_masks(record: Mapping[str, object]) -> dict[str, object]:
    return {key: value for key, value in record.items() if key != "_support_masks"}


def _scan_repeated_support_catalogues() -> dict[str, object]:
    chain_payload = build_t12_81_3_chain_closure_csp_payload()
    prefix_survivors = chain_payload.get("prefix_survivors")
    if not isinstance(prefix_survivors, Sequence):
        raise AssertionError("prefix_survivors must be a sequence")

    repeated_records: list[dict[str, object]] = []
    repeated_survivors: list[dict[str, object]] = []
    repeated_aggregate: Counter[str] = Counter()
    repeated_empty_depths: Counter[str] = Counter()
    supply_records: list[dict[str, object]] = []
    supply_initially_compatible: list[dict[str, object]] = []
    supply_survivors: list[dict[str, object]] = []
    supply_aggregate: Counter[str] = Counter()
    supply_empty_depths: Counter[str] = Counter()
    supply_size_histogram: Counter[str] = Counter()
    per_repeated_center: dict[int, Counter[str]] = {}

    for prefix_index, prefix in enumerate(prefix_survivors):
        if not isinstance(prefix, Mapping):
            raise AssertionError("prefix survivor must be a mapping")
        for candidate in _repeated_support_candidates(prefix_index, prefix):
            support_catalogue = candidate["_support_masks"]
            if not isinstance(support_catalogue, Mapping):
                raise AssertionError("support catalogue must be a mapping")
            repeated_stats = _search_multi_support_catalogue(support_catalogue)
            _record_stats(repeated_aggregate, repeated_empty_depths, repeated_stats)
            repeated_center = int(candidate["repeated_center"])
            per_center = per_repeated_center.setdefault(repeated_center, Counter())
            per_center["repeated_support_candidate_count"] += 1
            per_center[f"initial_status:{repeated_stats['initial_status']}"] += 1
            per_center[
                f"solution_search_status:{repeated_stats['solution_search_status']}"
            ] += 1
            repeated_record = {
                **_strip_internal_masks(candidate),
                **repeated_stats,
            }
            repeated_records.append(repeated_record)
            if int(repeated_stats["detected_solution_count"]):
                repeated_survivors.append(repeated_record)

            closure = _prefix_closure(prefix)
            for supply_support in _activation_support_masks(SUPPLY_CENTER, closure):
                supply_size_histogram[str(supply_support.bit_count())] += 1
                supply_catalogue = {
                    center: list(support_masks)
                    for center, support_masks in support_catalogue.items()
                }
                supply_catalogue[SUPPLY_CENTER] = [supply_support]
                supply_stats = _search_multi_support_catalogue(supply_catalogue)
                _record_stats(supply_aggregate, supply_empty_depths, supply_stats)
                per_center["supply_extension_candidate_count"] += 1
                per_center[f"supply_initial_status:{supply_stats['initial_status']}"] += 1
                per_center[
                    f"supply_solution_search_status:{supply_stats['solution_search_status']}"
                ] += 1
                supply_record = {
                    **_strip_internal_masks(candidate),
                    "center_6_supply_support": _bit_labels(supply_support),
                    "center_6_supply_support_size": supply_support.bit_count(),
                    "center_6_supply_trigger_options_inside_closure": [
                        label for label in _bit_labels(supply_support) if label in closure
                    ],
                    "auxiliary_support_catalogue_with_supply": _compact_catalogue(
                        supply_catalogue
                    ),
                    **supply_stats,
                }
                supply_records.append(supply_record)
                if supply_stats["initial_status"] == SEARCH_EXHAUSTED:
                    supply_initially_compatible.append(supply_record)
                if int(supply_stats["detected_solution_count"]):
                    supply_survivors.append(supply_record)

    return {
        "source_prefix_survivor_count": len(prefix_survivors),
        "repeated_support_records": repeated_records,
        "repeated_support_survivors": repeated_survivors,
        "repeated_support_aggregate": dict(sorted(repeated_aggregate.items())),
        "repeated_support_empty_domain_depth_histogram": dict(
            sorted(repeated_empty_depths.items())
        ),
        "supply_extension_records": supply_records,
        "supply_extension_initially_compatible_catalogues": supply_initially_compatible,
        "supply_extension_survivors": supply_survivors,
        "supply_extension_aggregate": dict(sorted(supply_aggregate.items())),
        "supply_extension_empty_domain_depth_histogram": dict(
            sorted(supply_empty_depths.items())
        ),
        "supply_support_size_histogram": dict(sorted(supply_size_histogram.items())),
        "per_repeated_center": {
            str(center): dict(sorted(counter.items()))
            for center, counter in sorted(per_repeated_center.items())
        },
    }


def build_t12_81_3_repeated_support_catalogue_audit_payload() -> dict[str, object]:
    """Return the deterministic repeated-support catalogue audit packet."""

    scan = _scan_repeated_support_catalogues()
    repeated_aggregate = scan["repeated_support_aggregate"]
    supply_aggregate = scan["supply_extension_aggregate"]
    if not isinstance(repeated_aggregate, Mapping):
        raise AssertionError("repeated aggregate must be a mapping")
    if not isinstance(supply_aggregate, Mapping):
        raise AssertionError("supply aggregate must be a mapping")

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This audit starts only from the four stored chain-closure prefix survivors.",
            "It adds exactly one disjoint repeated support at one already activated prefix center.",
            "The center-6 supply support is eligible only when it contains at least three currently closed labels.",
            "The scan uses incidence, crossing, witness-pair, and same-center disjointness filters only, not Euclidean realizability.",
            "No support-existence, row-forcing, n=9 finite-case, bridge, official-status, or counterexample status changes.",
        ],
        "summary": {
            "target_row_key": TARGET_ROW_KEY,
            "source_record_ids": [81],
            "cyclic_order": CYCLIC_ORDER,
            "deletion_seed": TARGET_DELETION_SEED,
            "connector_pair": CONNECTOR_PAIR,
            "target_center": TARGET_ROW_CENTER,
            "eventual_supply_label": SUPPLY_CENTER,
            "source_prefix_survivor_count": scan["source_prefix_survivor_count"],
            "repeated_support_candidate_count": len(scan["repeated_support_records"]),
            "repeated_support_detected_solution_count": repeated_aggregate[
                "detected_solution_count"
            ],
            "repeated_support_survivor_count": len(
                scan["repeated_support_survivors"]
            ),
            "repeated_support_search_node_count": repeated_aggregate[
                "search_node_count"
            ],
            "repeated_support_empty_domain_count": repeated_aggregate[
                "empty_domain_count"
            ],
            "supply_extension_candidate_count": len(scan["supply_extension_records"]),
            "supply_extension_support_size_histogram": scan[
                "supply_support_size_histogram"
            ],
            "supply_extension_initially_compatible_count": supply_aggregate[
                "initial_status:SEARCH_EXHAUSTED"
            ],
            "supply_extension_initially_incompatible_count": supply_aggregate[
                f"initial_status:{SUPPORT_CATALOGUE_INCOMPATIBLE}"
            ],
            "supply_extension_detected_solution_count": supply_aggregate[
                "detected_solution_count"
            ],
            "supply_extension_survivor_count": len(scan["supply_extension_survivors"]),
            "supply_extension_search_node_count": supply_aggregate[
                "search_node_count"
            ],
            "supply_extension_empty_domain_count": supply_aggregate[
                "empty_domain_count"
            ],
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This rules out only one disjoint same-center repeated-support "
                "layer attached to the stored chain-closure prefix survivors, "
                "followed by one center-6 activation support. It does not prove "
                "support existence, genuine rich-class order, row forcing, n=9, "
                "the bridge, or Erdos Problem #97."
            ),
        },
        "repeated_support_catalogue_scan": {
            "aggregate": scan["repeated_support_aggregate"],
            "empty_domain_depth_histogram": scan[
                "repeated_support_empty_domain_depth_histogram"
            ],
            "per_repeated_center": scan["per_repeated_center"],
            "records": scan["repeated_support_records"],
            "survivors": scan["repeated_support_survivors"],
        },
        "supply_extension_scan": {
            "aggregate": scan["supply_extension_aggregate"],
            "empty_domain_depth_histogram": scan[
                "supply_extension_empty_domain_depth_histogram"
            ],
            "stored_extension_summary_count": 0,
            "omitted_extension_summary_count": len(scan["supply_extension_records"]),
            "omission_reason": (
                "Failed supply-extension summaries are regenerated by the "
                "checker; the artifact stores only aggregate counts, the "
                "initially compatible catalogue, and survivor records because "
                "there are no supply-extension selected-row completions."
            ),
            "initially_compatible_catalogues": scan[
                "supply_extension_initially_compatible_catalogues"
            ],
            "survivors": scan["supply_extension_survivors"],
        },
        "source_chain_closure_csp": {
            "path": CHAIN_CLOSURE_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": CHAIN_CLOSURE_SCHEMA,
            "status": CHAIN_CLOSURE_STATUS,
            "scan_status": CHAIN_CLOSURE_SCAN_STATUS,
        },
        "provenance": {
            "generator": (
                "scripts/check_bootstrap_t12_81_3_repeated_support_catalogue_audit.py"
            ),
            "command": (
                "python scripts/check_bootstrap_t12_81_3_repeated_support_catalogue_audit.py "
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
        "source_prefix_survivor_count": 4,
        "repeated_support_candidate_count": 5,
        "supply_extension_candidate_count": 464,
        "supply_extension_initially_compatible_count": 1,
        "supply_extension_initially_incompatible_count": 463,
        "supply_extension_detected_solution_count": 0,
        "supply_extension_survivor_count": 0,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    repeated_scan = payload.get("repeated_support_catalogue_scan")
    if not isinstance(repeated_scan, Mapping):
        raise AssertionError("repeated_support_catalogue_scan must be a mapping")
    repeated_records = repeated_scan.get("records")
    if not isinstance(repeated_records, Sequence) or len(repeated_records) != 5:
        raise AssertionError("expected five repeated-support records")
    compact_repeated = [
        {
            "prefix": record.get("prefix_survivor_index"),
            "repeated_center": record.get("repeated_center"),
            "repeated_support": record.get("repeated_support"),
        }
        for record in repeated_records
        if isinstance(record, Mapping)
    ]
    expected_repeated = [
        {"prefix": 0, "repeated_center": 8, "repeated_support": [2, 3, 5, 6]},
        {"prefix": 1, "repeated_center": 2, "repeated_support": [0, 5, 6, 7]},
        {"prefix": 1, "repeated_center": 8, "repeated_support": [2, 3, 5, 6]},
        {"prefix": 2, "repeated_center": 8, "repeated_support": [2, 3, 5, 6]},
        {"prefix": 3, "repeated_center": 8, "repeated_support": [2, 3, 6, 7]},
    ]
    if compact_repeated != expected_repeated:
        raise AssertionError(f"repeated-support records drifted: {compact_repeated!r}")

    supply_scan = payload.get("supply_extension_scan")
    if not isinstance(supply_scan, Mapping):
        raise AssertionError("supply_extension_scan must be a mapping")
    initially_compatible = supply_scan.get("initially_compatible_catalogues")
    if not isinstance(initially_compatible, Sequence) or len(initially_compatible) != 1:
        raise AssertionError("expected one initially compatible supply catalogue")
    compatible = initially_compatible[0]
    if not isinstance(compatible, Mapping):
        raise AssertionError("compatible supply catalogue must be a mapping")
    expected_compatible = {
        "prefix_survivor_index": 1,
        "repeated_center": 8,
        "repeated_support": [2, 3, 5, 6],
        "center_6_supply_support": [2, 4, 7, 8],
        "detected_solution_count": 0,
    }
    for key, expected in expected_compatible.items():
        if compatible.get(key) != expected:
            raise AssertionError(
                f"compatible supply {key} is {compatible.get(key)!r}, "
                f"expected {expected!r}"
            )
    if supply_scan.get("survivors") != []:
        raise AssertionError("supply extension survivors must be empty")

    source = payload.get("source_chain_closure_csp")
    if not isinstance(source, Mapping):
        raise AssertionError("source_chain_closure_csp must be a mapping")
    if source.get("schema") != CHAIN_CLOSURE_SCHEMA:
        raise AssertionError("source chain-closure schema drifted")
    if source.get("scan_status") != CHAIN_CLOSURE_SCAN_STATUS:
        raise AssertionError("source chain-closure scan status drifted")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_3_repeated_support_catalogue_audit.py"
    ):
        raise AssertionError("provenance generator drifted")
