"""Rich-support auxiliary CSP for the bootstrap/T12 81:3 escape.

The auxiliary-class CSP treats the center-6 supply and center-3
connector-avoiding objects as 4-set rich classes.  This packet allows those
objects to be larger rich distance-class supports.  A selected row at the same
center may be any 4-subset of the support, or any 4-set disjoint from it.

The search is exact finite incidence/crossing bookkeeping.  It is not a
Euclidean realizability theorem and not a proof of the bootstrap bridge.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_81_3_escape_candidates import (
    CONNECTOR_PAIR,
    CYCLIC_ORDER,
    SUPPLY_CENTER,
)
from erdos97.bootstrap_t12_81_3_escape_full_neighborhood import (
    ROW_REPLACEMENT_COUNT_PER_CENTER,
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
from erdos97.bootstrap_t12_81_3_escape_two_row_drop import (
    CROSS_OK,
    LABELS,
    MASK_TO_PAIR_INDEX,
    _all_replacement_row_masks,
    _row_mask,
)


SCHEMA = "erdos97.bootstrap_t12_81_3_escape_rich_support_csp.v1"
STATUS = "BOOTSTRAP_T12_81_3_ESCAPE_RICH_SUPPORT_CSP_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "NO_BASIC_FILTER_SURVIVORS_WITH_RICH_SUPPORT_AUXILIARIES"
CLAIM_SCOPE = (
    "Rich-support auxiliary CSP relaxation of the 81:3 escape scan. The "
    "center-6 pre-3 supply object may be any rich support of size 4 through 8 "
    "containing deletion seed [0,1,4]. The center-3 connector-avoiding object "
    "may be any rich support of size 4 through 7 containing [0,4,6] but not 1, "
    "or [1,4,6] but not 0. Selected rows at those centers may be any 4-subset "
    "of the auxiliary support or any disjoint 4-set; all seven other selected "
    "rows are arbitrary 4-sets. Exact backtracking proves no complete "
    "assignment satisfies the row-pair, witness-pair, crossing, and "
    "same-center disjointness filters. This is not a proof of genuine "
    "rich-class order, not a proof of row forcing, not a proof of n=9, not a "
    "proof of the bridge, and not a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_3_escape_rich_support_csp.json"
)


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _bit_labels(mask: int) -> list[int]:
    return [label for label in CYCLIC_ORDER if mask & (1 << label)]


def _pair_indices(mask: int) -> list[int]:
    indices: list[int] = []
    for left, right in combinations(_bit_labels(mask), 2):
        indices.append(MASK_TO_PAIR_INDEX[(1 << left) | (1 << right)])
    return indices


def _support_masks_containing(
    center: int,
    required: Sequence[int],
    *,
    forbidden: Sequence[int] = (),
) -> list[int]:
    required_set = set(required)
    forbidden_set = set(forbidden)
    universe = [
        label
        for label in CYCLIC_ORDER
        if label != center and label not in forbidden_set
    ]
    optional = [label for label in universe if label not in required_set]
    support_masks: list[int] = []
    for size in range(len(optional) + 1):
        for extra in combinations(optional, size):
            support = sorted(required_set | set(extra))
            if len(support) >= 4:
                support_masks.append(_row_mask(support))
    return support_masks


def _supply_support_masks() -> list[int]:
    return _support_masks_containing(SUPPLY_CENTER, TARGET_DELETION_SEED)


def _connector_support_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for activation_triple, forbidden in (
        ([0, 4, 6], [1]),
        ([1, 4, 6], [0]),
    ):
        for support_mask in _support_masks_containing(
            TARGET_ROW_CENTER,
            activation_triple,
            forbidden=forbidden,
        ):
            records.append(
                {
                    "activation_triple": activation_triple,
                    "forbidden_connector_endpoint": forbidden[0],
                    "support": _bit_labels(support_mask),
                    "support_mask": support_mask,
                    "support_size": support_mask.bit_count(),
                }
            )
    return records


def _selected_row_choices_for_support(center: int, support_mask: int) -> list[int]:
    return [
        row_mask
        for row_mask in _all_replacement_row_masks(center)
        if (row_mask & ~support_mask) == 0 or not (row_mask & support_mask)
    ]


def _support_pair_compatible(
    center_a: int,
    support_a: int,
    center_b: int,
    support_b: int,
) -> bool:
    source_a, source_b = sorted((center_a, center_b))
    intersection = support_a & support_b
    intersection_size = intersection.bit_count()
    if intersection_size > 2:
        return False
    if intersection_size == 2:
        pair_index = MASK_TO_PAIR_INDEX[intersection]
        return bool(CROSS_OK[(source_a, source_b, pair_index)])
    return True


def _add_pair_centers(
    center: int,
    support_mask: int,
    pair_centers: dict[int, set[int]],
) -> None:
    for pair_index in _pair_indices(support_mask):
        pair_centers.setdefault(pair_index, set()).add(center)


def _build_pair_centers(
    auxiliary_supports: Mapping[int, int],
    selected: Mapping[int, Sequence[int]],
) -> dict[int, set[int]]:
    pair_centers: dict[int, set[int]] = {}
    for center, support_mask in auxiliary_supports.items():
        _add_pair_centers(center, support_mask, pair_centers)
    for center, row_masks in selected.items():
        for row_mask in row_masks:
            _add_pair_centers(center, row_mask, pair_centers)
    return pair_centers


def _compatible_with_catalogue(
    center: int,
    row_mask: int,
    auxiliary_supports: Mapping[int, int],
    selected: Mapping[int, Sequence[int]],
    pair_centers: Mapping[int, set[int]],
) -> bool:
    for pair_index in _pair_indices(row_mask):
        centers = pair_centers.get(pair_index, set())
        if center not in centers and len(centers) >= 2:
            return False

    for other_center, other_support in auxiliary_supports.items():
        if other_center != center and not _support_pair_compatible(
            center, row_mask, other_center, other_support
        ):
            return False

    for other_center, other_rows in selected.items():
        if other_center == center:
            continue
        for other_row in other_rows:
            if not _support_pair_compatible(center, row_mask, other_center, other_row):
                return False
    return True


def _search_support_pair(
    supply_support: int,
    connector_support: int,
) -> dict[str, object]:
    auxiliary_supports = {
        SUPPLY_CENTER: supply_support,
        TARGET_ROW_CENTER: connector_support,
    }
    if not _support_pair_compatible(
        SUPPLY_CENTER,
        supply_support,
        TARGET_ROW_CENTER,
        connector_support,
    ):
        return {
            "initial_status": "INITIAL_AUXILIARY_SUPPORT_PAIR_INCOMPATIBLE",
            "search_node_count": 0,
            "empty_domain_count": 0,
            "complete_solution_count": 0,
            "max_depth": 0,
            "empty_domain_depth_histogram": {},
        }

    selected: dict[int, list[int]] = {}
    pair_centers = _build_pair_centers(auxiliary_supports, selected)
    choices = {
        center: _all_replacement_row_masks(center) for center in CYCLIC_ORDER
    }
    choices[SUPPLY_CENTER] = _selected_row_choices_for_support(
        SUPPLY_CENTER, supply_support
    )
    choices[TARGET_ROW_CENTER] = _selected_row_choices_for_support(
        TARGET_ROW_CENTER, connector_support
    )

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
                    center, row_mask, auxiliary_supports, selected, pair_centers
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
            pair_centers = _build_pair_centers(auxiliary_supports, selected)
            search()
            del selected[best_center]
            pair_centers = _build_pair_centers(auxiliary_supports, selected)

    search()
    stats["initial_status"] = "SEARCH_EXHAUSTED"
    stats["empty_domain_depth_histogram"] = {
        str(depth): count for depth, count in sorted(empty_depths.items())
    }
    return stats


def _scan_csp() -> dict[str, object]:
    supply_supports = _supply_support_masks()
    connector_records = _connector_support_records()
    connector_supports = [
        int(record["support_mask"]) for record in connector_records
    ]

    support_pair_summaries: list[dict[str, object]] = []
    aggregate = Counter()
    empty_depths: Counter[str] = Counter()
    for supply_support in supply_supports:
        for connector_record, connector_support in zip(
            connector_records, connector_supports, strict=True
        ):
            stats = _search_support_pair(supply_support, connector_support)
            aggregate["search_node_count"] += int(stats["search_node_count"])
            aggregate["empty_domain_count"] += int(stats["empty_domain_count"])
            aggregate["complete_solution_count"] += int(stats["complete_solution_count"])
            aggregate[f"initial_status:{stats['initial_status']}"] += 1
            for depth, count in dict(stats["empty_domain_depth_histogram"]).items():
                empty_depths[str(depth)] += int(count)
            support_pair_summaries.append(
                {
                    "auxiliary_supply_support": _bit_labels(supply_support),
                    "auxiliary_supply_support_size": supply_support.bit_count(),
                    "auxiliary_target_support": connector_record["support"],
                    "auxiliary_target_support_size": connector_record["support_size"],
                    "target_center_activation_triple": connector_record[
                        "activation_triple"
                    ],
                    "target_center_forbidden_connector_endpoint": connector_record[
                        "forbidden_connector_endpoint"
                    ],
                    "selected_row_choice_count_at_supply_center": len(
                        _selected_row_choices_for_support(
                            SUPPLY_CENTER, supply_support
                        )
                    ),
                    "selected_row_choice_count_at_target_center": len(
                        _selected_row_choices_for_support(
                            TARGET_ROW_CENTER, connector_support
                        )
                    ),
                    **stats,
                }
            )

    return {
        "support_pair_summaries": support_pair_summaries,
        "aggregate": dict(sorted(aggregate.items())),
        "empty_domain_depth_histogram": dict(sorted(empty_depths.items())),
    }


def _support_generation_summary() -> dict[str, object]:
    supply_supports = _supply_support_masks()
    connector_records = _connector_support_records()
    connector_supports = [
        int(record["support_mask"]) for record in connector_records
    ]
    supply_choice_counts = [
        len(_selected_row_choices_for_support(SUPPLY_CENTER, support))
        for support in supply_supports
    ]
    connector_choice_counts = [
        len(_selected_row_choices_for_support(TARGET_ROW_CENTER, support))
        for support in connector_supports
    ]
    return {
        "center_6_supply_supports": [
            _bit_labels(support) for support in supply_supports
        ],
        "center_3_connector_avoiding_supports": [
            {
                key: value
                for key, value in record.items()
                if key not in {"support_mask"}
            }
            for record in connector_records
        ],
        "center_6_supply_support_size_histogram": {
            str(size): count
            for size, count in sorted(
                Counter(support.bit_count() for support in supply_supports).items()
            )
        },
        "center_3_connector_support_size_histogram": {
            str(size): count
            for size, count in sorted(
                Counter(support.bit_count() for support in connector_supports).items()
            )
        },
        "center_6_selected_row_choice_count_histogram": {
            str(size): count
            for size, count in sorted(Counter(supply_choice_counts).items())
        },
        "center_3_selected_row_choice_count_histogram": {
            str(size): count
            for size, count in sorted(Counter(connector_choice_counts).items())
        },
        "center_6_total_selected_row_choices_over_supports": sum(
            supply_choice_counts
        ),
        "center_3_total_selected_row_choices_over_supports": sum(
            connector_choice_counts
        ),
    }


def build_t12_81_3_escape_rich_support_csp_payload() -> dict[str, object]:
    """Return the deterministic rich-support auxiliary escape CSP packet."""

    support_generation = _support_generation_summary()
    scan = _scan_csp()
    aggregate = scan["aggregate"]
    if not isinstance(aggregate, Mapping):
        raise AssertionError("aggregate must be a mapping")
    implicit_space = (
        int(support_generation["center_6_total_selected_row_choices_over_supports"])
        * int(support_generation["center_3_total_selected_row_choices_over_supports"])
        * (ROW_REPLACEMENT_COUNT_PER_CENTER ** 7)
    )

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This CSP treats the center-6 supply object and center-3 connector object as auxiliary rich supports, not merely 4-set classes.",
            "Selected rows at centers 3 and 6 may be any 4-subset of the auxiliary support or any disjoint 4-set.",
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
            "auxiliary_support_centers": [TARGET_ROW_CENTER, SUPPLY_CENTER],
            "center_6_supply_support_count": len(_supply_support_masks()),
            "center_3_connector_avoiding_support_count": len(
                _connector_support_records()
            ),
            "fixed_auxiliary_support_pair_count": len(
                scan["support_pair_summaries"]
            ),
            "free_row_replacement_count_per_non_auxiliary_center": ROW_REPLACEMENT_COUNT_PER_CENTER,
            "implicit_selected_assignment_space_size": implicit_space,
            "search_node_count": aggregate["search_node_count"],
            "empty_domain_count": aggregate["empty_domain_count"],
            "initial_auxiliary_support_pair_incompatible_count": aggregate[
                "initial_status:INITIAL_AUXILIARY_SUPPORT_PAIR_INCOMPATIBLE"
            ],
            "initial_auxiliary_support_pair_searched_count": aggregate[
                "initial_status:SEARCH_EXHAUSTED"
            ],
            "complete_solution_count": aggregate["complete_solution_count"],
            "surviving_assignment_count": aggregate["complete_solution_count"],
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This does not prove the supply or connector support exists, "
                "does not model additional auxiliary rich supports at other "
                "centers, and does not add new minimal/rich-class forcing "
                "hypotheses."
            ),
        },
        "support_generation": support_generation,
        "empty_domain_depth_histogram": scan["empty_domain_depth_histogram"],
        "fixed_auxiliary_support_pair_summaries": scan["support_pair_summaries"],
        "survivors": [],
        "source_trigger_uniqueness_audit": {
            "path": TRIGGER_UNIQUENESS_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": TRIGGER_UNIQUENESS_SCHEMA,
            "status": TRIGGER_UNIQUENESS_STATUS,
            "scan_status": TRIGGER_UNIQUENESS_SCAN_STATUS,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_3_escape_rich_support_csp.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_3_escape_rich_support_csp.py "
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
        "auxiliary_support_centers": [TARGET_ROW_CENTER, SUPPLY_CENTER],
        "center_6_supply_support_count": 31,
        "center_3_connector_avoiding_support_count": 30,
        "fixed_auxiliary_support_pair_count": 930,
        "free_row_replacement_count_per_non_auxiliary_center": 70,
        "implicit_selected_assignment_space_size": 996734092900000000,
        "search_node_count": 2169,
        "empty_domain_count": 1268,
        "initial_auxiliary_support_pair_incompatible_count": 700,
        "initial_auxiliary_support_pair_searched_count": 230,
        "complete_solution_count": 0,
        "surviving_assignment_count": 0,
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
        "center_6_supply_support_size_histogram": {
            "4": 5,
            "5": 10,
            "6": 10,
            "7": 5,
            "8": 1,
        },
        "center_3_connector_support_size_histogram": {
            "4": 8,
            "5": 12,
            "6": 8,
            "7": 2,
        },
        "center_6_selected_row_choice_count_histogram": {
            "2": 5,
            "5": 10,
            "15": 10,
            "35": 5,
            "70": 1,
        },
        "center_3_selected_row_choice_count_histogram": {
            "2": 8,
            "5": 12,
            "15": 8,
            "35": 2,
        },
        "center_6_total_selected_row_choices_over_supports": 455,
        "center_3_total_selected_row_choices_over_supports": 266,
    }
    for key, expected in expected_generation.items():
        if support_generation.get(key) != expected:
            raise AssertionError(
                f"support_generation {key} is {support_generation.get(key)!r}, expected {expected!r}"
            )

    fixed_summaries = payload.get("fixed_auxiliary_support_pair_summaries")
    if not isinstance(fixed_summaries, Sequence) or len(fixed_summaries) != 930:
        raise AssertionError("expected 930 fixed-auxiliary-support-pair summaries")
    if any(
        isinstance(record, Mapping) and record.get("complete_solution_count") != 0
        for record in fixed_summaries
    ):
        raise AssertionError("no fixed auxiliary support pair should have a solution")

    survivors = payload.get("survivors")
    if survivors != []:
        raise AssertionError("survivors must be empty")

    source = payload.get("source_trigger_uniqueness_audit")
    if not isinstance(source, Mapping):
        raise AssertionError("source_trigger_uniqueness_audit must be a mapping")
    if source.get("schema") != TRIGGER_UNIQUENESS_SCHEMA:
        raise AssertionError("source trigger-uniqueness schema drifted")
    if source.get("scan_status") != TRIGGER_UNIQUENESS_SCAN_STATUS:
        raise AssertionError("source trigger-uniqueness scan status drifted")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_3_escape_rich_support_csp.py"
    ):
        raise AssertionError("provenance generator drifted")
