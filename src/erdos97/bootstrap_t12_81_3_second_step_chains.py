"""Distinct-intermediate chain CSP for the bootstrap/T12 81:3 escape.

The first-supply-chain packet leaves exactly three basic-filter survivor
prefixes.  All of them start by activating center 8 from deletion seed
[0, 1, 4], and none admits an immediate center-6 supply support.

This packet asks the next finite question: after one of those stored center-8
prefixes, can a chain of distinct intermediate centers from {2, 5, 7} appear
before center 6 supplies label 6?  Each intermediate center gets one auxiliary
rich support containing at least three labels already in the closure.  Center 6
then gets one supply support containing at least three labels from the final
closure.  The center-3 connector-avoiding support is the one stored in the
source prefix.

The search uses the same exact incidence/crossing bookkeeping filters as the
first-supply-chain packet.  It is not a Euclidean realizability theorem and not
a proof of the bootstrap bridge.
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
from erdos97.bootstrap_t12_81_3_escape_rich_support_csp import (
    _bit_labels,
    _build_pair_centers,
    _support_pair_compatible,
)
from erdos97.bootstrap_t12_81_3_escape_two_row_drop import LABELS, _row_mask
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


SCHEMA = "erdos97.bootstrap_t12_81_3_second_step_chains.v1"
STATUS = "BOOTSTRAP_T12_81_3_SECOND_STEP_CHAINS_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "NO_DISTINCT_INTERMEDIATE_CENTER8_TO_LABEL6_CHAINS"
CLAIM_SCOPE = (
    "Distinct-intermediate continuation CSP for the 81:3 pre-3 label-6 "
    "escape. It treats the three stored center-8 prefix survivors from the "
    "first-supply-chain packet as inputs, allows a chain of distinct "
    "intermediate centers from {2,5,7}, gives each intermediate center one "
    "rich support containing at least three labels already in the closure, and "
    "then asks whether center 6 can supply label 6 through one support before "
    "the stored connector-avoiding center-3 support. Exact backtracking finds "
    "no surviving chain under the same basic filters used by the source "
    "packet. This is not a proof of genuine rich-class order, not a proof of "
    "row forcing, not a proof of n=9, not a proof of the bridge, and not a "
    "counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_3_second_step_chains.json"
)
FIRST_STEP_CENTER = 8
MAX_DISTINCT_INTERMEDIATE_CHAIN_LENGTH = 3
INTERMEDIATE_CENTERS_AFTER_CENTER8 = [
    label
    for label in CYCLIC_ORDER
    if label
    not in set(TARGET_DELETION_SEED)
    | {FIRST_STEP_CENTER, TARGET_ROW_CENTER, SUPPLY_CENTER}
]

AGGREGATE_COUNTER_KEYS = (
    "support_prefix_pruned_count",
    "label_6_supply_candidate_count",
    "initial_auxiliary_catalogue_incompatible_count",
    "initial_auxiliary_catalogue_searched_count",
    "search_node_count",
    "empty_domain_count",
    "detected_solution_count",
)
TERMINAL_COUNTER_KEYS = tuple(
    key for key in AGGREGATE_COUNTER_KEYS if key != "support_prefix_pruned_count"
)


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _counter_dict(
    counter: Counter[str],
    *,
    keys: Sequence[str] = AGGREGATE_COUNTER_KEYS,
) -> dict[str, int]:
    return {key: int(counter.get(key, 0)) for key in keys}


def _support_masks_meeting_activation(
    center: int,
    activation_labels: Sequence[int],
) -> list[int]:
    activation_mask = _row_mask(activation_labels)
    universe = [label for label in CYCLIC_ORDER if label != center]
    masks: list[int] = []
    for support_size in range(4, len(universe) + 1):
        for support in combinations(universe, support_size):
            support_mask = _row_mask(support)
            if (support_mask & activation_mask).bit_count() >= 3:
                masks.append(support_mask)
    return masks


def _auxiliary_support_catalogue_compatible(
    auxiliary_supports: Mapping[int, int],
) -> bool:
    centers = sorted(auxiliary_supports)
    for index, center_a in enumerate(centers):
        for center_b in centers[index + 1 :]:
            if not _support_pair_compatible(
                center_a,
                auxiliary_supports[center_a],
                center_b,
                auxiliary_supports[center_b],
            ):
                return False

    pair_centers = _build_pair_centers(auxiliary_supports, {})
    return all(len(centers_for_pair) <= 2 for centers_for_pair in pair_centers.values())


def _source_prefix_survivors(
    first_supply_artifact: Path = FIRST_SUPPLY_ARTIFACT,
) -> list[dict[str, object]]:
    payload = load_first_supply_artifact(first_supply_artifact)
    assert_first_supply_payload(payload)
    survivors = payload.get("survivors")
    if not isinstance(survivors, Sequence):
        raise AssertionError("first-supply-chain survivors must be a sequence")

    records: list[dict[str, object]] = []
    for index, survivor in enumerate(survivors):
        if not isinstance(survivor, Mapping):
            raise AssertionError("first-supply-chain survivor records must be mappings")
        first_center = int(survivor.get("first_step_center", -1))
        if first_center != FIRST_STEP_CENTER:
            raise AssertionError("second-step scan expects only center-8 prefixes")
        first_support = _int_list(survivor["first_step_support"])
        target_support = _int_list(survivor["auxiliary_target_support"])
        records.append(
            {
                "source_prefix_survivor_index": index,
                "first_step_center": first_center,
                "first_step_support": first_support,
                "first_step_support_size": len(first_support),
                "auxiliary_target_support": target_support,
                "auxiliary_target_support_size": len(target_support),
                "target_center_activation_triple": _int_list(
                    survivor["target_center_activation_triple"]
                ),
                "target_center_forbidden_connector_endpoint": int(
                    survivor["target_center_forbidden_connector_endpoint"]
                ),
            }
        )
    return records


def _increment_search_counters(
    counters: Sequence[Counter[str]],
    stats: Mapping[str, object],
) -> None:
    for counter in counters:
        counter["label_6_supply_candidate_count"] += 1
        if stats["initial_status"] == "INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE":
            counter["initial_auxiliary_catalogue_incompatible_count"] += 1
        else:
            counter["initial_auxiliary_catalogue_searched_count"] += 1
        counter["search_node_count"] += int(stats["search_node_count"])
        counter["empty_domain_count"] += int(stats["empty_domain_count"])
        counter["detected_solution_count"] += int(stats["detected_solution_count"])


def _scan_distinct_intermediate_chains(
    source_prefixes: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    aggregate: Counter[str] = Counter()
    per_chain_length: dict[str, Counter[str]] = {
        str(length): Counter()
        for length in range(MAX_DISTINCT_INTERMEDIATE_CHAIN_LENGTH + 1)
    }
    per_source_prefix: dict[str, Counter[str]] = {
        str(index): Counter() for index in range(len(source_prefixes))
    }
    per_terminal_center: dict[str, Counter[str]] = {
        str(center): Counter() for center in INTERMEDIATE_CENTERS_AFTER_CENTER8
    }
    survivors: list[dict[str, object]] = []

    def scan_label_6_supply(
        *,
        source_prefix_index: int,
        chain: Sequence[tuple[int, int]],
        auxiliary_supports: Mapping[int, int],
        active_labels: Sequence[int],
    ) -> None:
        chain_length = len(chain)
        chain_key = str(chain_length)
        source_key = str(source_prefix_index)
        terminal_key = str(chain[-1][0]) if chain else None
        for supply_support in _support_masks_meeting_activation(
            SUPPLY_CENTER,
            active_labels,
        ):
            full_auxiliary_supports = dict(auxiliary_supports)
            full_auxiliary_supports[SUPPLY_CENTER] = supply_support
            stats = _search_auxiliary_support_catalogue(
                full_auxiliary_supports,
                incompatible_status="INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE",
            )
            counters = [aggregate, per_chain_length[chain_key], per_source_prefix[source_key]]
            if terminal_key is not None:
                counters.append(per_terminal_center[terminal_key])
            _increment_search_counters(counters, stats)

            if int(stats["detected_solution_count"]):
                survivors.append(
                    {
                        "source_prefix_survivor_index": source_prefix_index,
                        "intermediate_chain": [
                            {"center": center, "support": _bit_labels(support)}
                            for center, support in chain
                        ],
                        "label_6_supply_support": _bit_labels(supply_support),
                        **stats,
                    }
                )

    def extend_chain(
        *,
        source_prefix_index: int,
        chain: list[tuple[int, int]],
        remaining_centers: Sequence[int],
        auxiliary_supports: Mapping[int, int],
        active_labels: Sequence[int],
    ) -> None:
        scan_label_6_supply(
            source_prefix_index=source_prefix_index,
            chain=chain,
            auxiliary_supports=auxiliary_supports,
            active_labels=active_labels,
        )
        if len(chain) >= MAX_DISTINCT_INTERMEDIATE_CHAIN_LENGTH:
            return

        next_chain_length = len(chain) + 1
        chain_key = str(next_chain_length)
        source_key = str(source_prefix_index)
        for center in remaining_centers:
            for support in _support_masks_meeting_activation(center, active_labels):
                next_auxiliary_supports = dict(auxiliary_supports)
                next_auxiliary_supports[center] = support
                if not _auxiliary_support_catalogue_compatible(next_auxiliary_supports):
                    aggregate["support_prefix_pruned_count"] += 1
                    per_chain_length[chain_key]["support_prefix_pruned_count"] += 1
                    per_source_prefix[source_key]["support_prefix_pruned_count"] += 1
                    continue
                next_active_labels = sorted(set(active_labels) | {center})
                next_remaining = [
                    next_center
                    for next_center in remaining_centers
                    if next_center != center
                ]
                extend_chain(
                    source_prefix_index=source_prefix_index,
                    chain=[*chain, (center, support)],
                    remaining_centers=next_remaining,
                    auxiliary_supports=next_auxiliary_supports,
                    active_labels=next_active_labels,
                )

    for prefix in source_prefixes:
        source_prefix_index = int(prefix["source_prefix_survivor_index"])
        first_support = _row_mask(_int_list(prefix["first_step_support"]))
        target_support = _row_mask(_int_list(prefix["auxiliary_target_support"]))
        base_auxiliary_supports = {
            FIRST_STEP_CENTER: first_support,
            TARGET_ROW_CENTER: target_support,
        }
        if not _auxiliary_support_catalogue_compatible(base_auxiliary_supports):
            raise AssertionError("stored first-supply prefix is internally incompatible")
        extend_chain(
            source_prefix_index=source_prefix_index,
            chain=[],
            remaining_centers=INTERMEDIATE_CENTERS_AFTER_CENTER8,
            auxiliary_supports=base_auxiliary_supports,
            active_labels=sorted(set(TARGET_DELETION_SEED) | {FIRST_STEP_CENTER}),
        )

    return {
        "aggregate": _counter_dict(aggregate),
        "per_chain_length": {
            key: _counter_dict(counter)
            for key, counter in sorted(per_chain_length.items())
        },
        "per_source_prefix": {
            key: _counter_dict(counter)
            for key, counter in sorted(per_source_prefix.items())
        },
        "per_terminal_intermediate_center": {
            key: _counter_dict(counter, keys=TERMINAL_COUNTER_KEYS)
            for key, counter in sorted(per_terminal_center.items())
        },
        "survivors": survivors,
    }


def _support_generation_summary() -> dict[str, object]:
    base_closure = sorted(set(TARGET_DELETION_SEED) | {FIRST_STEP_CENTER})
    support_counts_by_center = {
        str(center): len(_support_masks_meeting_activation(center, base_closure))
        for center in INTERMEDIATE_CENTERS_AFTER_CENTER8
    }
    return {
        "base_closure_after_center_8": base_closure,
        "intermediate_centers_after_center8": INTERMEDIATE_CENTERS_AFTER_CENTER8,
        "intermediate_support_count_by_center_from_base_closure": (
            support_counts_by_center
        ),
        "center_6_supply_support_count_from_base_closure": len(
            _support_masks_meeting_activation(SUPPLY_CENTER, base_closure)
        ),
        "labels": LABELS,
    }


def build_t12_81_3_second_step_chains_payload(
    first_supply_artifact: Path = FIRST_SUPPLY_ARTIFACT,
) -> dict[str, object]:
    """Return the deterministic second-step chain CSP packet."""

    source_prefixes = _source_prefix_survivors(first_supply_artifact)
    scan = _scan_distinct_intermediate_chains(source_prefixes)
    aggregate = scan["aggregate"]
    if not isinstance(aggregate, Mapping):
        raise AssertionError("aggregate must be a mapping")
    survivors = scan["survivors"]
    if not isinstance(survivors, Sequence):
        raise AssertionError("survivors must be a sequence")

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            (
                "This packet starts only from the three stored center-8 "
                "survivor prefixes in the first-supply-chain artifact."
            ),
            (
                "Intermediate centers are distinct labels from {2,5,7}; "
                "each gets one auxiliary support."
            ),
            (
                "Support activation means the support contains at least "
                "three labels from the current closure."
            ),
            (
                "The scan uses incidence, crossing, pair-cap, and same-center "
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
            "first_step_center": FIRST_STEP_CENTER,
            "eventual_supply_label": SUPPLY_CENTER,
            "source_prefix_survivor_count": len(source_prefixes),
            "intermediate_centers_after_center8": INTERMEDIATE_CENTERS_AFTER_CENTER8,
            "max_distinct_intermediate_chain_length": (
                MAX_DISTINCT_INTERMEDIATE_CHAIN_LENGTH
            ),
            "support_prefix_pruned_count": aggregate["support_prefix_pruned_count"],
            "label_6_supply_candidate_count": aggregate[
                "label_6_supply_candidate_count"
            ],
            "initial_auxiliary_catalogue_incompatible_count": aggregate[
                "initial_auxiliary_catalogue_incompatible_count"
            ],
            "initial_auxiliary_catalogue_searched_count": aggregate[
                "initial_auxiliary_catalogue_searched_count"
            ],
            "search_node_count": aggregate["search_node_count"],
            "empty_domain_count": aggregate["empty_domain_count"],
            "detected_solution_count": aggregate["detected_solution_count"],
            "surviving_chain_count": len(survivors),
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "No chain remains in this distinct-intermediate, one-support-"
                "per-center model after the stored center-8 prefix survivors. "
                "Repeated or multiple rich supports at one center, richer "
                "catalogues not represented by a single support per activated "
                "center, a theorem forcing genuine rich-class order, and other "
                "bridge targets remain open."
            ),
        },
        "support_generation": _support_generation_summary(),
        "source_prefix_survivors": source_prefixes,
        "chain_scan": scan,
        "source_first_supply_chains": {
            "path": FIRST_SUPPLY_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": FIRST_SUPPLY_SCHEMA,
            "status": FIRST_SUPPLY_STATUS,
            "scan_status": FIRST_SUPPLY_SCAN_STATUS,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_3_second_step_chains.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_3_second_step_chains.py "
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
        "first_step_center": FIRST_STEP_CENTER,
        "eventual_supply_label": SUPPLY_CENTER,
        "source_prefix_survivor_count": 3,
        "intermediate_centers_after_center8": [2, 5, 7],
        "max_distinct_intermediate_chain_length": 3,
        "support_prefix_pruned_count": 4112,
        "label_6_supply_candidate_count": 9528,
        "initial_auxiliary_catalogue_incompatible_count": 9470,
        "initial_auxiliary_catalogue_searched_count": 58,
        "search_node_count": 223,
        "empty_domain_count": 85,
        "detected_solution_count": 0,
        "surviving_chain_count": 0,
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
    if support_generation.get("base_closure_after_center_8") != [0, 1, 4, 8]:
        raise AssertionError("base closure after center 8 drifted")
    if support_generation.get("center_6_supply_support_count_from_base_closure") != 76:
        raise AssertionError("center-6 base-closure supply count drifted")

    expected_per_chain_length = {
        "0": {
            "support_prefix_pruned_count": 0,
            "label_6_supply_candidate_count": 228,
            "initial_auxiliary_catalogue_incompatible_count": 228,
            "initial_auxiliary_catalogue_searched_count": 0,
            "search_node_count": 0,
            "empty_domain_count": 0,
            "detected_solution_count": 0,
        },
        "1": {
            "support_prefix_pruned_count": 678,
            "label_6_supply_candidate_count": 708,
            "initial_auxiliary_catalogue_incompatible_count": 694,
            "initial_auxiliary_catalogue_searched_count": 14,
            "search_node_count": 86,
            "empty_domain_count": 29,
            "detected_solution_count": 0,
        },
        "2": {
            "support_prefix_pruned_count": 1402,
            "label_6_supply_candidate_count": 2072,
            "initial_auxiliary_catalogue_incompatible_count": 2052,
            "initial_auxiliary_catalogue_searched_count": 20,
            "search_node_count": 94,
            "empty_domain_count": 30,
            "detected_solution_count": 0,
        },
        "3": {
            "support_prefix_pruned_count": 2032,
            "label_6_supply_candidate_count": 6520,
            "initial_auxiliary_catalogue_incompatible_count": 6496,
            "initial_auxiliary_catalogue_searched_count": 24,
            "search_node_count": 43,
            "empty_domain_count": 26,
            "detected_solution_count": 0,
        },
    }
    chain_scan = payload.get("chain_scan")
    if not isinstance(chain_scan, Mapping):
        raise AssertionError("chain_scan must be a mapping")
    if chain_scan.get("per_chain_length") != expected_per_chain_length:
        raise AssertionError("per-chain-length counts drifted")

    expected_per_source_prefix = {
        "0": {
            "support_prefix_pruned_count": 228,
            "label_6_supply_candidate_count": 76,
            "initial_auxiliary_catalogue_incompatible_count": 76,
            "initial_auxiliary_catalogue_searched_count": 0,
            "search_node_count": 0,
            "empty_domain_count": 0,
            "detected_solution_count": 0,
        },
        "1": {
            "support_prefix_pruned_count": 1942,
            "label_6_supply_candidate_count": 4726,
            "initial_auxiliary_catalogue_incompatible_count": 4697,
            "initial_auxiliary_catalogue_searched_count": 29,
            "search_node_count": 113,
            "empty_domain_count": 44,
            "detected_solution_count": 0,
        },
        "2": {
            "support_prefix_pruned_count": 1942,
            "label_6_supply_candidate_count": 4726,
            "initial_auxiliary_catalogue_incompatible_count": 4697,
            "initial_auxiliary_catalogue_searched_count": 29,
            "search_node_count": 110,
            "empty_domain_count": 41,
            "detected_solution_count": 0,
        },
    }
    if chain_scan.get("per_source_prefix") != expected_per_source_prefix:
        raise AssertionError("per-source-prefix counts drifted")

    expected_per_terminal_center = {
        "2": {
            "label_6_supply_candidate_count": 708,
            "initial_auxiliary_catalogue_incompatible_count": 694,
            "initial_auxiliary_catalogue_searched_count": 14,
            "search_node_count": 86,
            "empty_domain_count": 29,
            "detected_solution_count": 0,
        },
        "5": {
            "label_6_supply_candidate_count": 2132,
            "initial_auxiliary_catalogue_incompatible_count": 2120,
            "initial_auxiliary_catalogue_searched_count": 12,
            "search_node_count": 80,
            "empty_domain_count": 22,
            "detected_solution_count": 0,
        },
        "7": {
            "label_6_supply_candidate_count": 6460,
            "initial_auxiliary_catalogue_incompatible_count": 6428,
            "initial_auxiliary_catalogue_searched_count": 32,
            "search_node_count": 57,
            "empty_domain_count": 34,
            "detected_solution_count": 0,
        },
    }
    if (
        chain_scan.get("per_terminal_intermediate_center")
        != expected_per_terminal_center
    ):
        raise AssertionError("per-terminal-center counts drifted")
    if chain_scan.get("survivors") != []:
        raise AssertionError("distinct-intermediate chain survivors must be empty")

    source_prefixes = payload.get("source_prefix_survivors")
    if not isinstance(source_prefixes, Sequence) or len(source_prefixes) != 3:
        raise AssertionError("expected three source prefix survivors")
    if {
        tuple(record.get("first_step_support", []))
        for record in source_prefixes
        if isinstance(record, Mapping)
    } != {(0, 1, 4, 5), (0, 1, 4, 7)}:
        raise AssertionError("source first-step support set drifted")

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
        "scripts/check_bootstrap_t12_81_3_second_step_chains.py"
    ):
        raise AssertionError("provenance generator drifted")
