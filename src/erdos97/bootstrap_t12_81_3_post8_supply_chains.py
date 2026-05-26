"""Post-center-8 supply-chain CSP for the bootstrap/T12 81:3 escape.

The first-supply-chain prefix packet leaves three boundary prefixes, all with
center 8 as the first pre-3 activation from seed [0,1,4].  It also checks that
none of those prefixes admits an immediate center-6 supply support.

This packet exhausts the finite continuation model after that center-8 step:
before center 6 activates, the only remaining non-seed, non-target,
non-supply centers are 2, 5, and 7.  The scan therefore tries every ordered
subset of [2,5,7] as intermediate activations, then tries center 6.

The search is exact finite incidence/crossing bookkeeping.  It is not a
Euclidean realizability theorem and not a proof of the bootstrap bridge.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import permutations
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_81_3_escape_candidates import (
    CYCLIC_ORDER,
    SUPPLY_CENTER,
)
from erdos97.bootstrap_t12_81_3_escape_rich_support_csp import (
    _bit_labels,
    _build_pair_centers,
    _support_masks_containing,
    _support_pair_compatible,
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
from erdos97.bootstrap_t12_81_3_second_step_chains import (
    DEFAULT_ARTIFACT as SECOND_STEP_ARTIFACT,
    SCAN_STATUS as SECOND_STEP_SCAN_STATUS,
    SCHEMA as SECOND_STEP_SCHEMA,
    STATUS as SECOND_STEP_STATUS,
)
from erdos97.bootstrap_t12_81_3_order_escape import (
    TARGET_DELETION_SEED,
    TARGET_ROW_CENTER,
    TARGET_ROW_KEY,
)


SCHEMA = "erdos97.bootstrap_t12_81_3_post8_supply_chains.v1"
STATUS = "BOOTSTRAP_T12_81_3_POST8_SUPPLY_CHAINS_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "NO_POST8_PRE6_SUPPLY_CHAIN_SURVIVORS_UNDER_BASIC_FILTERS"
CLAIM_SCOPE = (
    "Post-center-8 supply-chain CSP for the 81:3 pre-3 label-6 escape. It "
    "takes the three first-supply-chain prefix survivors as boundary inputs, "
    "each starting at center 8, and enumerates every ordered continuation "
    "through any subset of the remaining possible intermediate centers [2,5,7] "
    "before center 6. Each auxiliary center may use any rich support of size at "
    "least four containing at least three already-closed labels; selected rows "
    "at auxiliary centers may be 4-subsets of their support or disjoint 4-sets. "
    "All support catalogues that pass the row-pair, crossing, witness-pair, "
    "and same-center disjointness filters are then searched for selected-row "
    "completions. No selected-row survivor is found. This is not a proof of "
    "genuine rich-class order, not a proof of row forcing, not a proof of n=9, "
    "not a proof of the bridge, and not a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_3_post8_supply_chains.json"
)
FIRST_STEP_CENTER = 8
POST8_INTERMEDIATE_CENTERS = [2, 5, 7]
MAX_INTERMEDIATE_CENTER_COUNT = len(POST8_INTERMEDIATE_CENTERS)


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _source_prefix_survivors(
    first_supply_artifact: Path = FIRST_SUPPLY_ARTIFACT,
) -> list[dict[str, object]]:
    source = load_first_supply_artifact(first_supply_artifact)
    assert_first_supply_payload(source)
    survivors = source.get("survivors")
    if not isinstance(survivors, Sequence):
        raise AssertionError("source first-supply survivors must be a sequence")
    out: list[dict[str, object]] = []
    for survivor in survivors:
        if not isinstance(survivor, Mapping):
            raise AssertionError("source survivor entries must be mappings")
        if int(survivor.get("first_step_center", -1)) != FIRST_STEP_CENTER:
            raise AssertionError("all source survivors should start at center 8")
        out.append(dict(survivor))
    return out


def _support_options_for_activation(center: int, closure: set[int]) -> list[int]:
    closure_mask = _row_mask(closure)
    return [
        support_mask
        for support_mask in _support_masks_containing(center, [])
        if (support_mask & closure_mask).bit_count() >= 3
    ]


def _initial_auxiliary_supports_compatible(
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


def _support_candidate_count_for_order(order: Sequence[int]) -> int:
    closure = set(TARGET_DELETION_SEED) | {FIRST_STEP_CENTER}
    count = 1
    for center in order:
        count *= len(_support_options_for_activation(center, closure))
        closure.add(center)
    count *= len(_support_options_for_activation(SUPPLY_CENTER, closure))
    return count


def _enumerate_initially_compatible_catalogues(
    prefix: Mapping[str, object],
    order: Sequence[int],
) -> list[dict[str, object]]:
    first_support = _row_mask(
        _int_list(prefix["first_step_support"])  # type: ignore[index]
    )
    target_support = _row_mask(
        _int_list(prefix["auxiliary_target_support"])  # type: ignore[index]
    )
    base_auxiliary = {
        FIRST_STEP_CENTER: first_support,
        TARGET_ROW_CENTER: target_support,
    }
    if not _initial_auxiliary_supports_compatible(base_auxiliary):
        raise AssertionError("source prefix support catalogue should be compatible")

    records: list[dict[str, object]] = []
    initial_closure = set(TARGET_DELETION_SEED) | {FIRST_STEP_CENTER}

    def search_prefix(
        position: int,
        auxiliary_supports: dict[int, int],
        closure: set[int],
        intermediate_supports: dict[int, int],
    ) -> None:
        if position == len(order):
            for supply_support in _support_options_for_activation(
                SUPPLY_CENTER,
                closure,
            ):
                next_auxiliary = dict(auxiliary_supports)
                next_auxiliary[SUPPLY_CENTER] = supply_support
                if not _initial_auxiliary_supports_compatible(next_auxiliary):
                    continue
                records.append(
                    {
                        "auxiliary_supports": next_auxiliary,
                        "intermediate_supports": dict(intermediate_supports),
                        "supply_support": supply_support,
                    }
                )
            return

        center = int(order[position])
        for support in _support_options_for_activation(center, closure):
            next_auxiliary = dict(auxiliary_supports)
            next_auxiliary[center] = support
            if not _initial_auxiliary_supports_compatible(next_auxiliary):
                continue
            next_intermediate_supports = dict(intermediate_supports)
            next_intermediate_supports[center] = support
            next_closure = set(closure)
            next_closure.add(center)
            search_prefix(
                position + 1,
                next_auxiliary,
                next_closure,
                next_intermediate_supports,
            )

    search_prefix(0, base_auxiliary, initial_closure, {})
    return records


def _order_key(order: Sequence[int]) -> str:
    return "immediate" if not order else ",".join(str(center) for center in order)


def _scan_post8_supply_chains(
    prefix_survivors: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    length_summaries: dict[str, object] = {}
    compatible_catalogue_records: list[dict[str, object]] = []
    summary_counts = {
        "raw_by_length": {},
        "initial_compatible_by_length": {},
        "nodes_by_length": {},
        "empty_by_length": {},
        "solutions_by_length": {},
    }

    for length in range(MAX_INTERMEDIATE_CENTER_COUNT + 1):
        orders = (
            [()]
            if length == 0
            else list(permutations(POST8_INTERMEDIATE_CENTERS, length))
        )
        support_candidate_count = len(prefix_survivors) * sum(
            _support_candidate_count_for_order(order) for order in orders
        )

        aggregate: Counter[str] = Counter()
        empty_depths: Counter[str] = Counter()
        per_prefix: dict[int, Counter[str]] = defaultdict(Counter)
        per_order: dict[str, Counter[str]] = defaultdict(Counter)

        for prefix_index, prefix in enumerate(prefix_survivors):
            for order in orders:
                compatible_catalogues = _enumerate_initially_compatible_catalogues(
                    prefix,
                    order,
                )
                for compatible in compatible_catalogues:
                    auxiliary_supports = compatible["auxiliary_supports"]
                    if not isinstance(auxiliary_supports, Mapping):
                        raise AssertionError("auxiliary_supports must be a mapping")
                    stats = _search_auxiliary_support_catalogue(
                        auxiliary_supports,
                        incompatible_status=(
                            "INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE"
                        ),
                    )
                    aggregate["initial_compatible_count"] += 1
                    aggregate["search_node_count"] += int(stats["search_node_count"])
                    aggregate["empty_domain_count"] += int(stats["empty_domain_count"])
                    aggregate["detected_solution_count"] += int(
                        stats["detected_solution_count"]
                    )
                    aggregate[f"solution_status:{stats['solution_search_status']}"] += 1

                    per_prefix[prefix_index]["initial_compatible_count"] += 1
                    per_prefix[prefix_index]["search_node_count"] += int(
                        stats["search_node_count"]
                    )
                    per_prefix[prefix_index]["empty_domain_count"] += int(
                        stats["empty_domain_count"]
                    )
                    per_prefix[prefix_index]["detected_solution_count"] += int(
                        stats["detected_solution_count"]
                    )

                    key = _order_key(order)
                    per_order[key]["initial_compatible_count"] += 1
                    per_order[key]["search_node_count"] += int(
                        stats["search_node_count"]
                    )
                    per_order[key]["empty_domain_count"] += int(
                        stats["empty_domain_count"]
                    )
                    per_order[key]["detected_solution_count"] += int(
                        stats["detected_solution_count"]
                    )

                    for depth, count in dict(
                        stats["empty_domain_depth_histogram"]
                    ).items():
                        empty_depths[str(depth)] += int(count)

                    intermediate_supports = compatible["intermediate_supports"]
                    if not isinstance(intermediate_supports, Mapping):
                        raise AssertionError("intermediate_supports must be a mapping")
                    supply_support = int(compatible["supply_support"])
                    compatible_catalogue_records.append(
                        {
                            "intermediate_center_count": length,
                            "prefix_survivor_index": prefix_index,
                            "first_step_center": FIRST_STEP_CENTER,
                            "first_step_support": prefix["first_step_support"],
                            "target_center": TARGET_ROW_CENTER,
                            "target_support": prefix["auxiliary_target_support"],
                            "intermediate_order": list(order),
                            "intermediate_supports": {
                                str(center): _bit_labels(int(support))
                                for center, support in sorted(
                                    intermediate_supports.items()
                                )
                            },
                            "supply_center": SUPPLY_CENTER,
                            "supply_support": _bit_labels(supply_support),
                            "search_node_count": stats["search_node_count"],
                            "empty_domain_count": stats["empty_domain_count"],
                            "empty_domain_depth_histogram": stats[
                                "empty_domain_depth_histogram"
                            ],
                            "detected_solution_count": stats[
                                "detected_solution_count"
                            ],
                            "solution_search_status": stats[
                                "solution_search_status"
                            ],
                        }
                    )

        length_key = str(length)
        summary_counts["raw_by_length"][length_key] = support_candidate_count
        summary_counts["initial_compatible_by_length"][length_key] = aggregate[
            "initial_compatible_count"
        ]
        summary_counts["nodes_by_length"][length_key] = aggregate["search_node_count"]
        summary_counts["empty_by_length"][length_key] = aggregate["empty_domain_count"]
        summary_counts["solutions_by_length"][length_key] = aggregate[
            "detected_solution_count"
        ]

        length_summaries[length_key] = {
            "intermediate_center_count": length,
            "support_catalogue_candidate_count": support_candidate_count,
            "initially_incompatible_support_catalogue_count": (
                support_candidate_count - aggregate["initial_compatible_count"]
            ),
            "initially_compatible_support_catalogue_count": aggregate[
                "initial_compatible_count"
            ],
            "selected_search_node_count": aggregate["search_node_count"],
            "selected_empty_domain_count": aggregate["empty_domain_count"],
            "selected_detected_solution_count": aggregate["detected_solution_count"],
            "selected_empty_domain_depth_histogram": dict(
                sorted(empty_depths.items(), key=lambda item: int(item[0]))
            ),
            "per_prefix_survivor": {
                str(prefix_index): dict(sorted(counter.items()))
                for prefix_index, counter in sorted(per_prefix.items())
            },
            "per_intermediate_order": {
                key: dict(sorted(counter.items()))
                for key, counter in sorted(per_order.items())
            },
        }

    return {
        "length_summaries": length_summaries,
        "initially_compatible_catalogues": compatible_catalogue_records,
        "summary_counts": summary_counts,
    }


def build_t12_81_3_post8_supply_chains_payload(
    first_supply_artifact: Path = FIRST_SUPPLY_ARTIFACT,
) -> dict[str, object]:
    """Return the deterministic post-center-8 supply-chain CSP packet."""

    prefix_survivors = _source_prefix_survivors(first_supply_artifact)
    scan = _scan_post8_supply_chains(prefix_survivors)
    summary_counts = scan["summary_counts"]
    if not isinstance(summary_counts, Mapping):
        raise AssertionError("summary_counts must be a mapping")

    raw_by_length = summary_counts["raw_by_length"]
    initial_compatible_by_length = summary_counts["initial_compatible_by_length"]
    nodes_by_length = summary_counts["nodes_by_length"]
    empty_by_length = summary_counts["empty_by_length"]
    solutions_by_length = summary_counts["solutions_by_length"]

    if not all(
        isinstance(value, Mapping)
        for value in (
            raw_by_length,
            initial_compatible_by_length,
            nodes_by_length,
            empty_by_length,
            solutions_by_length,
        )
    ):
        raise AssertionError("summary count fields must be mappings")

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            (
                "The packet closes only the finite post-center-8 chain model "
                "built on the three stored first-step prefix survivors."
            ),
            (
                "Intermediate chains use distinct centers from [2,5,7]; length "
                "3 exhausts all possible remaining pre-6 centers in this model."
            ),
            (
                "The scan uses incidence, crossing, pair-cap, and same-center "
                "disjointness filters only, not Euclidean realizability."
            ),
            (
                "It does not prove that any audited support exists as a genuine "
                "rich distance class."
            ),
            (
                "It does not model additional simultaneous auxiliary supports "
                "beyond the activation chain and target connector support."
            ),
            (
                "No n=9 finite-case status, bridge status, official status, or "
                "counterexample status changes."
            ),
        ],
        "summary": {
            "target_row_key": TARGET_ROW_KEY,
            "source_record_ids": [81],
            "cyclic_order": CYCLIC_ORDER,
            "deletion_seed": TARGET_DELETION_SEED,
            "first_step_center": FIRST_STEP_CENTER,
            "post_first_step_closure": sorted(
                set(TARGET_DELETION_SEED) | {FIRST_STEP_CENTER}
            ),
            "eventual_supply_center": SUPPLY_CENTER,
            "target_center": TARGET_ROW_CENTER,
            "intermediate_center_universe": POST8_INTERMEDIATE_CENTERS,
            "max_intermediate_center_count": MAX_INTERMEDIATE_CENTER_COUNT,
            "source_first_supply_survivor_count": len(prefix_survivors),
            "source_first_supply_survivor_centers": sorted(
                {
                    int(prefix["first_step_center"])
                    for prefix in prefix_survivors
                }
            ),
            "support_catalogue_candidate_count_by_length": dict(raw_by_length),
            "initially_compatible_support_catalogue_count_by_length": dict(
                initial_compatible_by_length
            ),
            "selected_search_node_count_by_length": dict(nodes_by_length),
            "selected_empty_domain_count_by_length": dict(empty_by_length),
            "selected_detected_solution_count_by_length": dict(solutions_by_length),
            "total_support_catalogue_candidate_count": sum(
                int(value) for value in raw_by_length.values()
            ),
            "total_initially_compatible_support_catalogue_count": sum(
                int(value) for value in initial_compatible_by_length.values()
            ),
            "total_selected_search_node_count": sum(
                int(value) for value in nodes_by_length.values()
            ),
            "total_selected_empty_domain_count": sum(
                int(value) for value in empty_by_length.values()
            ),
            "total_selected_detected_solution_count": sum(
                int(value) for value in solutions_by_length.values()
            ),
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "Within the same finite support-chain model, the three stored "
                "center-8 prefixes no longer leave a longer-chain route to "
                "center 6. Any remaining 81:3 escape must use a hypothesis or "
                "catalogue outside this audited chain model, such as additional "
                "simultaneous rich supports, a different rich-class/minimality "
                "forcing step, or geometry not represented by these basic filters."
            ),
        },
        "length_summaries": scan["length_summaries"],
        "initially_compatible_catalogues": scan["initially_compatible_catalogues"],
        "source_first_supply_chains": {
            "path": FIRST_SUPPLY_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": FIRST_SUPPLY_SCHEMA,
            "status": FIRST_SUPPLY_STATUS,
            "scan_status": FIRST_SUPPLY_SCAN_STATUS,
        },
        "source_second_step_chains": {
            "path": SECOND_STEP_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": SECOND_STEP_SCHEMA,
            "status": SECOND_STEP_STATUS,
            "scan_status": SECOND_STEP_SCAN_STATUS,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_3_post8_supply_chains.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_3_post8_supply_chains.py "
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
        "first_step_center": FIRST_STEP_CENTER,
        "post_first_step_closure": [0, 1, 4, 8],
        "eventual_supply_center": SUPPLY_CENTER,
        "target_center": TARGET_ROW_CENTER,
        "intermediate_center_universe": POST8_INTERMEDIATE_CENTERS,
        "max_intermediate_center_count": 3,
        "source_first_supply_survivor_count": 3,
        "source_first_supply_survivor_centers": [8],
        "support_catalogue_candidate_count_by_length": {
            "0": 228,
            "1": 80712,
            "2": 23890752,
            "3": 3894192576,
        },
        "initially_compatible_support_catalogue_count_by_length": {
            "0": 0,
            "1": 14,
            "2": 20,
            "3": 24,
        },
        "selected_search_node_count_by_length": {
            "0": 0,
            "1": 86,
            "2": 94,
            "3": 43,
        },
        "selected_empty_domain_count_by_length": {
            "0": 0,
            "1": 29,
            "2": 30,
            "3": 26,
        },
        "selected_detected_solution_count_by_length": {
            "0": 0,
            "1": 0,
            "2": 0,
            "3": 0,
        },
        "total_support_catalogue_candidate_count": 3918164268,
        "total_initially_compatible_support_catalogue_count": 58,
        "total_selected_search_node_count": 223,
        "total_selected_empty_domain_count": 85,
        "total_selected_detected_solution_count": 0,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    length_summaries = payload.get("length_summaries")
    if not isinstance(length_summaries, Mapping):
        raise AssertionError("length_summaries must be a mapping")
    expected_initial_orders = {
        "1": {"2": 14},
        "2": {"2,5": 12, "2,7": 8},
        "3": {"2,5,7": 24},
    }
    for length, expected_orders in expected_initial_orders.items():
        length_summary = length_summaries.get(length)
        if not isinstance(length_summary, Mapping):
            raise AssertionError(f"length {length} summary missing")
        orders = length_summary.get("per_intermediate_order")
        if not isinstance(orders, Mapping):
            raise AssertionError(f"length {length} per-order summary missing")
        observed = {
            key: int(value.get("initial_compatible_count", -1))
            for key, value in orders.items()
            if isinstance(value, Mapping)
        }
        if observed != expected_orders:
            raise AssertionError(
                f"length {length} initial-compatible order map is "
                f"{observed!r}, expected {expected_orders!r}"
            )

    records = payload.get("initially_compatible_catalogues")
    if not isinstance(records, Sequence):
        raise AssertionError("initially_compatible_catalogues must be a sequence")
    if len(records) != 58:
        raise AssertionError("expected 58 initially compatible catalogues")
    if any(
        isinstance(record, Mapping) and record.get("detected_solution_count") != 0
        for record in records
    ):
        raise AssertionError("no initially compatible catalogue should solve")

    source = payload.get("source_first_supply_chains")
    if not isinstance(source, Mapping):
        raise AssertionError("source_first_supply_chains must be a mapping")
    if source.get("schema") != FIRST_SUPPLY_SCHEMA:
        raise AssertionError("source first-supply schema drifted")
    if source.get("scan_status") != FIRST_SUPPLY_SCAN_STATUS:
        raise AssertionError("source first-supply scan status drifted")

    second_step = payload.get("source_second_step_chains")
    if not isinstance(second_step, Mapping):
        raise AssertionError("source_second_step_chains must be a mapping")
    if second_step.get("schema") != SECOND_STEP_SCHEMA:
        raise AssertionError("source second-step schema drifted")
    if second_step.get("scan_status") != SECOND_STEP_SCAN_STATUS:
        raise AssertionError("source second-step scan status drifted")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_3_post8_supply_chains.py"
    ):
        raise AssertionError("provenance generator drifted")
