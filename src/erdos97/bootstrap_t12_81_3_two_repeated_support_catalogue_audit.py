"""Two-repeated-support catalogue audit for the bootstrap/T12 81:3 escape.

The one-layer repeated-support audit leaves no center-6 supply extension
survivor.  This packet checks the next minimal non-sequential widening: add
two repeated supports at already activated prefix centers, each disjoint from
the supports already present at its own center, before testing the same
center-6 supply extension.

This is finite proof-mining bookkeeping only.  It is not a Euclidean
realizability theorem and not a proof of the bootstrap bridge.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from erdos97.bootstrap_t12_81_3_chain_closure_csp import (
    _activation_support_masks,
    build_t12_81_3_chain_closure_csp_payload,
)
from erdos97.bootstrap_t12_81_3_escape_candidates import (
    CONNECTOR_PAIR,
    CYCLIC_ORDER,
    SUPPLY_CENTER,
)
from erdos97.bootstrap_t12_81_3_order_escape import (
    TARGET_DELETION_SEED,
    TARGET_ROW_CENTER,
    TARGET_ROW_KEY,
)
from erdos97.bootstrap_t12_81_3_repeated_support_catalogue_audit import (
    DEFAULT_ARTIFACT as ONE_REPEATED_ARTIFACT,
    SCAN_STATUS as ONE_REPEATED_SCAN_STATUS,
    SCHEMA as ONE_REPEATED_SCHEMA,
    STATUS as ONE_REPEATED_STATUS,
    SUPPORT_CATALOGUE_INCOMPATIBLE,
    SEARCH_EXHAUSTED,
    _bit_labels,
    _compact_catalogue,
    _prefix_auxiliary_supports,
    _prefix_closure,
    _record_stats,
    _repeated_support_candidates,
    _repeated_support_masks,
    _search_multi_support_catalogue,
    _strip_internal_masks,
)


SCHEMA = "erdos97.bootstrap_t12_81_3_two_repeated_support_catalogue_audit.v1"
STATUS = (
    "BOOTSTRAP_T12_81_3_TWO_REPEATED_SUPPORT_CATALOGUE_AUDIT_DIAGNOSTIC_ONLY"
)
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "NO_LABEL_6_SUPPLY_EXTENSION_AFTER_TWO_REPEATED_SUPPORTS"
CLAIM_SCOPE = (
    "Two-repeated-support catalogue audit for the 81:3 pre-3 label-6 escape. "
    "Starting from the four ordered chain-closure prefix survivors, the scan "
    "adds two repeated supports at already activated prefix centers, each "
    "disjoint from the supports already present at its own center, "
    "deduplicates the resulting unordered support catalogues, then tests every "
    "eligible center-6 activation support containing at least three currently "
    "closed labels. The exact incidence, crossing, "
    "witness-pair, and same-center-disjointness search leaves no complete "
    "selected-row assignment after the center-6 supply extension. This audits "
    "only the two-repeated-support layer after the stored prefix survivors; "
    "it is not a proof of support existence, not a proof of genuine "
    "rich-class order, not a proof of row forcing, not a proof of n=9, not a "
    "proof of the bridge, and not a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_3_two_repeated_support_catalogue_audit.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _catalogue_key(
    support_catalogue: Mapping[int, Sequence[int]],
) -> tuple[tuple[int, tuple[int, ...]], ...]:
    return tuple(
        (center, tuple(sorted(set(supports))))
        for center, supports in sorted(support_catalogue.items())
    )


def _support_summary(center: int, support_mask: int) -> dict[str, object]:
    return {
        "center": center,
        "support": _bit_labels(support_mask),
        "support_size": support_mask.bit_count(),
    }


def _added_supports(
    base_supports: Mapping[int, Sequence[int]],
    support_catalogue: Mapping[int, Sequence[int]],
) -> list[dict[str, object]]:
    additions: list[dict[str, object]] = []
    for center, support_masks in sorted(support_catalogue.items()):
        base_masks = set(base_supports.get(center, ()))
        for support_mask in sorted(set(support_masks) - base_masks):
            additions.append(_support_summary(center, support_mask))
    return additions


def _two_repeated_support_candidates() -> dict[str, object]:
    chain_payload = build_t12_81_3_chain_closure_csp_payload()
    prefix_survivors = chain_payload.get("prefix_survivors")
    if not isinstance(prefix_survivors, Sequence):
        raise AssertionError("prefix_survivors must be a sequence")

    records_by_key: dict[tuple[int, tuple[tuple[int, tuple[int, ...]], ...]], dict[str, object]] = {}
    ordered_path_count = 0
    one_repeated_candidate_count = 0

    for prefix_index, prefix in enumerate(prefix_survivors):
        if not isinstance(prefix, Mapping):
            raise AssertionError("prefix survivor must be a mapping")
        base_supports = _prefix_auxiliary_supports(prefix)
        for first_candidate in _repeated_support_candidates(prefix_index, prefix):
            one_repeated_candidate_count += 1
            first_catalogue = first_candidate["_support_masks"]
            if not isinstance(first_catalogue, Mapping):
                raise AssertionError("support catalogue must be a mapping")
            for center in sorted(first_catalogue):
                if center == TARGET_ROW_CENTER:
                    continue
                existing_supports = first_catalogue[center]
                if not isinstance(existing_supports, Sequence):
                    raise AssertionError("existing supports must be a sequence")
                for second_support in _repeated_support_masks(center, existing_supports):
                    support_catalogue = {
                        support_center: list(support_masks)
                        for support_center, support_masks in first_catalogue.items()
                    }
                    support_catalogue.setdefault(center, []).append(second_support)
                    key = (prefix_index, _catalogue_key(support_catalogue))
                    first_path = _support_summary(
                        int(first_candidate["repeated_center"]),
                        sum(
                            1 << label
                            for label in first_candidate["repeated_support"]
                        ),
                    )
                    second_path = _support_summary(center, second_support)
                    ordered_path_count += 1
                    path = [first_path, second_path]
                    if key in records_by_key:
                        record = records_by_key[key]
                        paths = record.get("ordered_generation_paths")
                        if not isinstance(paths, list):
                            raise AssertionError("ordered_generation_paths must be a list")
                        paths.append(path)
                        continue

                    records_by_key[key] = {
                        "prefix_survivor_index": prefix_index,
                        "connector_support": prefix["connector_support"],
                        "chain_centers": prefix["chain_centers"],
                        "chain": prefix["chain"],
                        "closure_before_supply": sorted(_prefix_closure(prefix)),
                        "repeated_support_count": 2,
                        "repeated_supports": _added_supports(
                            base_supports,
                            support_catalogue,
                        ),
                        "auxiliary_support_catalogue": _compact_catalogue(
                            support_catalogue
                        ),
                        "ordered_generation_paths": [path],
                        "_support_masks": support_catalogue,
                    }

    records = sorted(
        records_by_key.values(),
        key=lambda record: (
            int(record["prefix_survivor_index"]),
            [
                (support["center"], support["support"])
                for support in record["repeated_supports"]
                if isinstance(support, Mapping)
            ],
        ),
    )
    return {
        "source_prefix_survivor_count": len(prefix_survivors),
        "one_repeated_candidate_count": one_repeated_candidate_count,
        "ordered_two_repeated_generation_path_count": ordered_path_count,
        "two_repeated_support_records": records,
    }


def _scan_two_repeated_support_catalogues() -> dict[str, object]:
    candidates = _two_repeated_support_candidates()
    two_records: list[dict[str, object]] = []
    two_survivors: list[dict[str, object]] = []
    two_aggregate: Counter[str] = Counter()
    two_empty_depths: Counter[str] = Counter()
    supply_initially_compatible: list[dict[str, object]] = []
    supply_survivors: list[dict[str, object]] = []
    supply_aggregate: Counter[str] = Counter()
    supply_empty_depths: Counter[str] = Counter()
    supply_size_histogram: Counter[str] = Counter()

    candidate_records = candidates["two_repeated_support_records"]
    if not isinstance(candidate_records, Sequence):
        raise AssertionError("candidate records must be a sequence")

    for candidate in candidate_records:
        if not isinstance(candidate, Mapping):
            raise AssertionError("two repeated-support candidate must be a mapping")
        support_catalogue = candidate["_support_masks"]
        if not isinstance(support_catalogue, Mapping):
            raise AssertionError("support catalogue must be a mapping")
        two_stats = _search_multi_support_catalogue(support_catalogue)
        _record_stats(two_aggregate, two_empty_depths, two_stats)
        paths = candidate.get("ordered_generation_paths")
        if not isinstance(paths, Sequence):
            raise AssertionError("ordered_generation_paths must be a sequence")
        two_record = {
            **_strip_internal_masks(candidate),
            "ordered_generation_path_count": len(paths),
            **two_stats,
        }
        two_records.append(two_record)
        if int(two_stats["detected_solution_count"]):
            two_survivors.append(two_record)

        closure = frozenset(int(label) for label in candidate["closure_before_supply"])
        for supply_support in _activation_support_masks(SUPPLY_CENTER, closure):
            supply_size_histogram[str(supply_support.bit_count())] += 1
            supply_catalogue = {
                center: list(support_masks)
                for center, support_masks in support_catalogue.items()
            }
            supply_catalogue[SUPPLY_CENTER] = [supply_support]
            supply_stats = _search_multi_support_catalogue(supply_catalogue)
            _record_stats(supply_aggregate, supply_empty_depths, supply_stats)
            supply_record = {
                **_strip_internal_masks(candidate),
                "ordered_generation_path_count": len(paths),
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
            if supply_stats["initial_status"] == SEARCH_EXHAUSTED:
                supply_initially_compatible.append(supply_record)
            if int(supply_stats["detected_solution_count"]):
                supply_survivors.append(supply_record)

    return {
        **candidates,
        "two_repeated_support_records": two_records,
        "two_repeated_support_survivors": two_survivors,
        "two_repeated_support_aggregate": dict(sorted(two_aggregate.items())),
        "two_repeated_support_empty_domain_depth_histogram": dict(
            sorted(two_empty_depths.items())
        ),
        "supply_extension_initially_compatible_catalogues": supply_initially_compatible,
        "supply_extension_survivors": supply_survivors,
        "supply_extension_aggregate": dict(sorted(supply_aggregate.items())),
        "supply_extension_empty_domain_depth_histogram": dict(
            sorted(supply_empty_depths.items())
        ),
        "supply_support_size_histogram": dict(sorted(supply_size_histogram.items())),
        "supply_extension_candidate_count": sum(supply_size_histogram.values()),
    }


def build_t12_81_3_two_repeated_support_catalogue_audit_payload() -> dict[str, object]:
    """Return the deterministic two-repeated-support catalogue audit packet."""

    scan = _scan_two_repeated_support_catalogues()
    two_aggregate = scan["two_repeated_support_aggregate"]
    supply_aggregate = scan["supply_extension_aggregate"]
    if not isinstance(two_aggregate, Mapping):
        raise AssertionError("two-repeated aggregate must be a mapping")
    if not isinstance(supply_aggregate, Mapping):
        raise AssertionError("supply aggregate must be a mapping")

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This audit starts only from the four stored chain-closure prefix survivors.",
            "It adds exactly two repeated supports at already activated prefix centers, each disjoint from the supports already present at its own center.",
            "The resulting unordered support catalogues are deduplicated before supply-extension testing.",
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
            "source_one_repeated_candidate_count": scan[
                "one_repeated_candidate_count"
            ],
            "ordered_two_repeated_generation_path_count": scan[
                "ordered_two_repeated_generation_path_count"
            ],
            "two_repeated_support_catalogue_count": len(
                scan["two_repeated_support_records"]
            ),
            "two_repeated_support_detected_solution_count": two_aggregate[
                "detected_solution_count"
            ],
            "two_repeated_support_survivor_count": len(
                scan["two_repeated_support_survivors"]
            ),
            "two_repeated_support_search_node_count": two_aggregate[
                "search_node_count"
            ],
            "two_repeated_support_empty_domain_count": two_aggregate[
                "empty_domain_count"
            ],
            "supply_extension_candidate_count": scan[
                "supply_extension_candidate_count"
            ],
            "supply_extension_support_size_histogram": scan[
                "supply_support_size_histogram"
            ],
            "supply_extension_initially_compatible_count": supply_aggregate.get(
                "initial_status:SEARCH_EXHAUSTED",
                0,
            ),
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
                "This rules out only the unique deduplicated two-repeated-support "
                "catalogue attached to the stored chain-closure prefix survivors, "
                "followed by one center-6 activation support. It does not prove "
                "support existence, genuine rich-class order, row forcing, n=9, "
                "the bridge, or Erdos Problem #97."
            ),
        },
        "two_repeated_support_catalogue_scan": {
            "aggregate": scan["two_repeated_support_aggregate"],
            "empty_domain_depth_histogram": scan[
                "two_repeated_support_empty_domain_depth_histogram"
            ],
            "records": scan["two_repeated_support_records"],
            "survivors": scan["two_repeated_support_survivors"],
        },
        "supply_extension_scan": {
            "aggregate": scan["supply_extension_aggregate"],
            "empty_domain_depth_histogram": scan[
                "supply_extension_empty_domain_depth_histogram"
            ],
            "stored_extension_summary_count": 0,
            "omitted_extension_summary_count": scan[
                "supply_extension_candidate_count"
            ],
            "omission_reason": (
                "Failed supply-extension summaries are regenerated by the checker; "
                "the artifact stores only aggregate counts, initially compatible "
                "catalogues, and survivor records because there are no "
                "supply-extension selected-row completions."
            ),
            "initially_compatible_catalogues": scan[
                "supply_extension_initially_compatible_catalogues"
            ],
            "survivors": scan["supply_extension_survivors"],
        },
        "source_one_repeated_support_audit": {
            "path": ONE_REPEATED_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": ONE_REPEATED_SCHEMA,
            "status": ONE_REPEATED_STATUS,
            "scan_status": ONE_REPEATED_SCAN_STATUS,
        },
        "provenance": {
            "generator": (
                "scripts/check_bootstrap_t12_81_3_two_repeated_support_catalogue_audit.py"
            ),
            "command": (
                "python scripts/check_bootstrap_t12_81_3_two_repeated_support_catalogue_audit.py "
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
        "source_one_repeated_candidate_count": 5,
        "ordered_two_repeated_generation_path_count": 2,
        "two_repeated_support_catalogue_count": 1,
        "two_repeated_support_detected_solution_count": 0,
        "two_repeated_support_survivor_count": 0,
        "supply_extension_candidate_count": 118,
        "supply_extension_initially_compatible_count": 0,
        "supply_extension_initially_incompatible_count": 118,
        "supply_extension_detected_solution_count": 0,
        "supply_extension_survivor_count": 0,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    scan = payload.get("two_repeated_support_catalogue_scan")
    if not isinstance(scan, Mapping):
        raise AssertionError("two_repeated_support_catalogue_scan must be a mapping")
    records = scan.get("records")
    if not isinstance(records, Sequence) or len(records) != 1:
        raise AssertionError("expected one two-repeated-support record")
    record = records[0]
    if not isinstance(record, Mapping):
        raise AssertionError("two-repeated-support record must be a mapping")
    expected_record = {
        "prefix_survivor_index": 1,
        "repeated_support_count": 2,
        "ordered_generation_path_count": 2,
        "initial_status": SUPPORT_CATALOGUE_INCOMPATIBLE,
        "detected_solution_count": 0,
    }
    for key, expected in expected_record.items():
        if record.get(key) != expected:
            raise AssertionError(
                f"two-repeated record {key} is {record.get(key)!r}, "
                f"expected {expected!r}"
            )
    if record.get("repeated_supports") != [
        {"center": 2, "support": [0, 5, 6, 7], "support_size": 4},
        {"center": 8, "support": [2, 3, 5, 6], "support_size": 4},
    ]:
        raise AssertionError("two-repeated support list drifted")

    supply_scan = payload.get("supply_extension_scan")
    if not isinstance(supply_scan, Mapping):
        raise AssertionError("supply_extension_scan must be a mapping")
    if supply_scan.get("initially_compatible_catalogues") != []:
        raise AssertionError("expected no initially compatible supply catalogues")
    if supply_scan.get("survivors") != []:
        raise AssertionError("supply extension survivors must be empty")

    source = payload.get("source_one_repeated_support_audit")
    if not isinstance(source, Mapping):
        raise AssertionError("source_one_repeated_support_audit must be a mapping")
    if source.get("schema") != ONE_REPEATED_SCHEMA:
        raise AssertionError("source one-repeated schema drifted")
    if source.get("scan_status") != ONE_REPEATED_SCAN_STATUS:
        raise AssertionError("source one-repeated scan status drifted")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_3_two_repeated_support_catalogue_audit.py"
    ):
        raise AssertionError("provenance generator drifted")
