"""Ordered chain-closure CSP for the bootstrap/T12 81:3 escape.

The first-supply-chain packet leaves three first-step prefix survivors, all
starting at center 8, and proves no survivor admits an immediate center-6
label-6 supply support.  This packet follows those prefix survivors as ordered
support chains: the closure starts at the deletion seed [0,1,4], every next
activation support must contain at least three currently closed labels, center 3
is held back as the connector target, and center 6 is the eventual label-6
supply target.

The search is exact finite incidence/crossing bookkeeping.  It is not a
Euclidean realizability theorem and not a proof of the bootstrap bridge.
"""

from __future__ import annotations

from collections import Counter, defaultdict
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
    _connector_support_records,
)
from erdos97.bootstrap_t12_81_3_escape_two_row_drop import _row_mask
from erdos97.bootstrap_t12_81_3_first_supply_chains import (
    DEFAULT_ARTIFACT as FIRST_SUPPLY_ARTIFACT,
    SCAN_STATUS as FIRST_SUPPLY_SCAN_STATUS,
    SCHEMA as FIRST_SUPPLY_SCHEMA,
    STATUS as FIRST_SUPPLY_STATUS,
    _search_auxiliary_support_catalogue,
)
from erdos97.bootstrap_t12_81_3_order_escape import (
    TARGET_DELETION_SEED,
    TARGET_ROW_CENTER,
    TARGET_ROW_KEY,
)


SCHEMA = "erdos97.bootstrap_t12_81_3_chain_closure_csp.v1"
STATUS = "BOOTSTRAP_T12_81_3_CHAIN_CLOSURE_CSP_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "NO_LABEL_6_SUPPLY_CHAIN_SURVIVORS_IN_SEQUENTIAL_SUPPORT_MODEL"
CLAIM_SCOPE = (
    "Ordered chain-closure CSP for the 81:3 pre-3 label-6 escape. Starting "
    "from deletion seed [0,1,4], with the center-3 connector-avoiding support "
    "fixed as in the rich-support CSP, each later auxiliary support must be "
    "centered at a not-yet-closed non-seed/non-3 label and must contain at "
    "least three currently closed labels. The scan follows every exact "
    "incidence/crossing-compatible prefix and finds no surviving prefix whose "
    "next activated center is 6. This closes only the sequential support-chain "
    "model; it is not a proof of genuine rich-class order, not a proof of row "
    "forcing, not a proof of n=9, not a proof of the bridge, and not a "
    "counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_3_chain_closure_csp.json"
)
ACTIVATION_CENTERS = [
    label
    for label in CYCLIC_ORDER
    if label not in set(TARGET_DELETION_SEED) | {TARGET_ROW_CENTER}
]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _activation_support_masks(center: int, closure: Iterable[int]) -> list[int]:
    """Return rich-support masks at ``center`` using at least 3 closed labels."""

    closure_set = set(closure)
    universe = [label for label in CYCLIC_ORDER if label != center]
    support_masks: list[int] = []
    for mask in range(1 << len(universe)):
        support = [label for bit, label in enumerate(universe) if mask & (1 << bit)]
        if len(support) < 4:
            continue
        if len(closure_set & set(support)) < 3:
            continue
        support_masks.append(_row_mask(support))
    return sorted(support_masks, key=lambda value: (value.bit_count(), _bit_labels(value)))


def _compact_chain(
    chain: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    compact: list[dict[str, object]] = []
    for step in chain:
        compact.append(
            {
                "center": int(step["center"]),
                "support": list(step["support"]),
                "support_size": int(step["support_size"]),
                "activation_trigger_pool": list(step["activation_trigger_pool"]),
            }
        )
    return compact


def _chain_centers(chain: Sequence[Mapping[str, object]]) -> list[int]:
    return [int(step["center"]) for step in chain]


def _scan_chains() -> dict[str, object]:
    connector_records = _connector_support_records()
    aggregate = Counter()
    candidate_depths: Counter[str] = Counter()
    search_state_depths: Counter[str] = Counter()
    empty_depths: Counter[str] = Counter()
    per_activation_center: dict[int, Counter[str]] = defaultdict(Counter)
    prefix_survivors: list[dict[str, object]] = []
    supply_chain_survivors: list[dict[str, object]] = []

    def record_stats(center: int, depth: int, stats: Mapping[str, object]) -> None:
        aggregate["candidate_extension_count"] += 1
        candidate_depths[str(depth)] += 1
        aggregate["search_node_count"] += int(stats["search_node_count"])
        aggregate["empty_domain_count"] += int(stats["empty_domain_count"])
        aggregate["detected_solution_count"] += int(stats["detected_solution_count"])
        aggregate[f"initial_status:{stats['initial_status']}"] += 1
        aggregate[f"solution_search_status:{stats['solution_search_status']}"] += 1

        center_counter = per_activation_center[center]
        center_counter["candidate_extension_count"] += 1
        center_counter["search_node_count"] += int(stats["search_node_count"])
        center_counter["empty_domain_count"] += int(stats["empty_domain_count"])
        center_counter["detected_solution_count"] += int(stats["detected_solution_count"])
        center_counter[f"initial_status:{stats['initial_status']}"] += 1
        center_counter[f"solution_search_status:{stats['solution_search_status']}"] += 1

        for empty_depth, count in dict(stats["empty_domain_depth_histogram"]).items():
            empty_depths[str(empty_depth)] += int(count)

    def dfs(
        connector_index: int,
        connector_record: Mapping[str, object],
        auxiliary_supports: Mapping[int, int],
        closure: frozenset[int],
        chain: Sequence[Mapping[str, object]],
    ) -> None:
        search_state_depths[str(len(chain))] += 1
        for center in ACTIVATION_CENTERS:
            if center in closure:
                continue
            for support_mask in _activation_support_masks(center, closure):
                depth = len(chain) + 1
                next_supports = dict(auxiliary_supports)
                next_supports[center] = support_mask
                stats = _search_auxiliary_support_catalogue(
                    next_supports,
                    incompatible_status=(
                        "INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE"
                    ),
                )
                record_stats(center, depth, stats)
                if not int(stats["detected_solution_count"]):
                    continue

                step = {
                    "center": center,
                    "support": _bit_labels(support_mask),
                    "support_mask": support_mask,
                    "support_size": support_mask.bit_count(),
                    "activation_trigger_pool": sorted(closure),
                }
                next_chain = [*chain, step]
                record = {
                    "connector_index": connector_index,
                    "connector_support": connector_record["support"],
                    "target_center_activation_triple": connector_record[
                        "activation_triple"
                    ],
                    "target_center_forbidden_connector_endpoint": connector_record[
                        "forbidden_connector_endpoint"
                    ],
                    "chain_length": len(next_chain),
                    "chain_centers": _chain_centers(next_chain),
                    "chain": _compact_chain(next_chain),
                    "search_node_count": stats["search_node_count"],
                    "empty_domain_count": stats["empty_domain_count"],
                    "max_depth": stats["max_depth"],
                    "first_solution_selected_rows": stats[
                        "first_solution_selected_rows"
                    ],
                }
                if center == SUPPLY_CENTER:
                    supply_chain_survivors.append(record)
                    per_activation_center[center]["supply_chain_survivor_count"] += 1
                    continue

                prefix_survivors.append(record)
                per_activation_center[center]["prefix_survivor_count"] += 1
                dfs(
                    connector_index,
                    connector_record,
                    next_supports,
                    frozenset({*closure, center}),
                    next_chain,
                )

    for connector_index, connector_record in enumerate(connector_records):
        connector_support = int(connector_record["support_mask"])
        dfs(
            connector_index,
            connector_record,
            {TARGET_ROW_CENTER: connector_support},
            frozenset(TARGET_DELETION_SEED),
            [],
        )

    prefix_depths = Counter(str(record["chain_length"]) for record in prefix_survivors)
    return {
        "aggregate": dict(sorted(aggregate.items())),
        "candidate_extension_depth_histogram": dict(sorted(candidate_depths.items())),
        "search_state_depth_histogram": dict(sorted(search_state_depths.items())),
        "empty_domain_depth_histogram": dict(sorted(empty_depths.items())),
        "per_activation_center": {
            str(center): dict(sorted(counter.items()))
            for center, counter in sorted(per_activation_center.items())
        },
        "prefix_survivor_depth_histogram": dict(sorted(prefix_depths.items())),
        "prefix_survivors": prefix_survivors,
        "supply_chain_survivors": supply_chain_survivors,
    }


def build_t12_81_3_chain_closure_csp_payload() -> dict[str, object]:
    """Return the deterministic ordered chain-closure CSP packet."""

    chain_scan = _scan_chains()
    aggregate = chain_scan["aggregate"]
    if not isinstance(aggregate, Mapping):
        raise AssertionError("aggregate must be a mapping")
    prefix_survivors = chain_scan["prefix_survivors"]
    supply_survivors = chain_scan["supply_chain_survivors"]
    if not isinstance(prefix_survivors, Sequence):
        raise AssertionError("prefix_survivors must be a sequence")
    if not isinstance(supply_survivors, Sequence):
        raise AssertionError("supply_chain_survivors must be a sequence")

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This CSP audits a sequential support-chain model, not a full arbitrary rich-class catalogue.",
            "The target center 3 is held back; the eventual pre-3 supply target is center/label 6.",
            "A next support is eligible only when it contains at least three currently closed labels.",
            (
                "The scan uses incidence, crossing, pair-cap, and same-center "
                "disjointness filters only, not Euclidean realizability."
            ),
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
            "activation_centers": ACTIVATION_CENTERS,
            "connector_support_count": len(_connector_support_records()),
            "candidate_extension_count": aggregate["candidate_extension_count"],
            "candidate_extension_depth_histogram": chain_scan[
                "candidate_extension_depth_histogram"
            ],
            "search_state_depth_histogram": chain_scan[
                "search_state_depth_histogram"
            ],
            "search_node_count": aggregate["search_node_count"],
            "empty_domain_count": aggregate["empty_domain_count"],
            "initial_auxiliary_support_catalogue_incompatible_count": aggregate[
                "initial_status:INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE"
            ],
            "initial_auxiliary_support_catalogue_searched_count": aggregate[
                "initial_status:SEARCH_EXHAUSTED"
            ],
            "detected_solution_count": aggregate["detected_solution_count"],
            "prefix_survivor_count": len(prefix_survivors),
            "prefix_survivor_depth_histogram": chain_scan[
                "prefix_survivor_depth_histogram"
            ],
            "supply_chain_survivor_count": len(supply_survivors),
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This rules out only the audited sequential support-chain "
                "model. It does not prove that genuine rich-class catalogues "
                "must expose supports in this order, and it does not prove row "
                "forcing, n=9, the bridge, or Erdos Problem #97."
            ),
        },
        "chain_scan": {
            "aggregate": chain_scan["aggregate"],
            "candidate_extension_depth_histogram": chain_scan[
                "candidate_extension_depth_histogram"
            ],
            "search_state_depth_histogram": chain_scan[
                "search_state_depth_histogram"
            ],
            "empty_domain_depth_histogram": chain_scan[
                "empty_domain_depth_histogram"
            ],
            "per_activation_center": chain_scan["per_activation_center"],
            "prefix_survivor_depth_histogram": chain_scan[
                "prefix_survivor_depth_histogram"
            ],
        },
        "prefix_survivors": prefix_survivors,
        "supply_chain_survivors": supply_survivors,
        "source_first_supply_chains": {
            "path": FIRST_SUPPLY_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": FIRST_SUPPLY_SCHEMA,
            "status": FIRST_SUPPLY_STATUS,
            "scan_status": FIRST_SUPPLY_SCAN_STATUS,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_3_chain_closure_csp.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_3_chain_closure_csp.py "
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
        "activation_centers": ACTIVATION_CENTERS,
        "connector_support_count": 30,
        "candidate_extension_count": 5916,
        "candidate_extension_depth_histogram": {"1": 4650, "2": 912, "3": 354},
        "search_state_depth_histogram": {"0": 30, "1": 3, "2": 1},
        "search_node_count": 9214,
        "empty_domain_count": 5498,
        "initial_auxiliary_support_catalogue_incompatible_count": 5213,
        "initial_auxiliary_support_catalogue_searched_count": 703,
        "detected_solution_count": 4,
        "prefix_survivor_count": 4,
        "prefix_survivor_depth_histogram": {"1": 3, "2": 1},
        "supply_chain_survivor_count": 0,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    chain_scan = payload.get("chain_scan")
    if not isinstance(chain_scan, Mapping):
        raise AssertionError("chain_scan must be a mapping")
    aggregate = chain_scan.get("aggregate")
    if not isinstance(aggregate, Mapping):
        raise AssertionError("chain_scan aggregate must be a mapping")
    expected_aggregate = {
        "candidate_extension_count": 5916,
        "search_node_count": 9214,
        "empty_domain_count": 5498,
        "detected_solution_count": 4,
        "initial_status:INITIAL_AUXILIARY_SUPPORT_CATALOGUE_INCOMPATIBLE": 5213,
        "initial_status:SEARCH_EXHAUSTED": 703,
        "solution_search_status:EXHAUSTED_NO_SOLUTION": 699,
        "solution_search_status:NOT_SEARCHED_INITIAL_PAIR_INCOMPATIBLE": 5213,
        "solution_search_status:STOPPED_AFTER_FIRST_SOLUTION": 4,
    }
    for key, expected in expected_aggregate.items():
        if aggregate.get(key) != expected:
            raise AssertionError(
                f"aggregate {key} is {aggregate.get(key)!r}, expected {expected!r}"
            )

    prefix_survivors = payload.get("prefix_survivors")
    if not isinstance(prefix_survivors, Sequence) or len(prefix_survivors) != 4:
        raise AssertionError("expected four prefix survivor records")
    compact = [
        {
            "connector_support": record.get("connector_support"),
            "chain": [
                [step.get("center"), step.get("support")]
                for step in record.get("chain", [])
            ],
        }
        for record in prefix_survivors
        if isinstance(record, Mapping)
    ]
    expected_compact = [
        {
            "connector_support": [0, 2, 4, 6],
            "chain": [[8, [0, 1, 4, 7]]],
        },
        {
            "connector_support": [0, 2, 4, 6],
            "chain": [[8, [0, 1, 4, 7]], [2, [1, 3, 4, 8]]],
        },
        {
            "connector_support": [1, 2, 4, 6],
            "chain": [[8, [0, 1, 4, 7]]],
        },
        {
            "connector_support": [1, 4, 6, 8],
            "chain": [[8, [0, 1, 4, 5]]],
        },
    ]
    if compact != expected_compact:
        raise AssertionError(f"prefix survivor compact records drifted: {compact!r}")

    if payload.get("supply_chain_survivors") != []:
        raise AssertionError("supply chain survivors must be empty")

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
        "scripts/check_bootstrap_t12_81_3_chain_closure_csp.py"
    ):
        raise AssertionError("provenance generator drifted")
