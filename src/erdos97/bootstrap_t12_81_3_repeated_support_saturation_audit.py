"""Repeated-support saturation audit for the bootstrap/T12 81:3 escape.

The one- and two-repeated-support packets test bounded non-sequential
continuations after the stored ordered chain-closure prefix survivors.  This
packet audits the catalogue boundary itself: under the same rule that repeated
supports are attached only to already activated prefix centers and must be
disjoint from all supports already present at that center, the stored prefix
model has no three-repeated-support catalogue.

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
    _bit_labels,
    _compact_catalogue,
    _prefix_auxiliary_supports,
    _prefix_closure,
    _repeated_support_masks,
)
from erdos97.bootstrap_t12_81_3_two_repeated_support_catalogue_audit import (
    DEFAULT_ARTIFACT as TWO_REPEATED_ARTIFACT,
    SCAN_STATUS as TWO_REPEATED_SCAN_STATUS,
    SCHEMA as TWO_REPEATED_SCHEMA,
    STATUS as TWO_REPEATED_STATUS,
)


SCHEMA = "erdos97.bootstrap_t12_81_3_repeated_support_saturation_audit.v1"
STATUS = (
    "BOOTSTRAP_T12_81_3_REPEATED_SUPPORT_SATURATION_AUDIT_DIAGNOSTIC_ONLY"
)
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "NO_THREE_REPEATED_SUPPORT_CATALOGUES_IN_STORED_PREFIX_MODEL"
CLAIM_SCOPE = (
    "Repeated-support saturation audit for the 81:3 pre-3 label-6 escape. "
    "Starting from the four ordered chain-closure prefix survivors, the scan "
    "enumerates every unordered catalogue obtained by repeatedly adding "
    "same-center-disjoint supports at already activated non-target prefix "
    "centers. It finds four base prefix catalogues, five one-repeated-support "
    "catalogues, one deduplicated two-repeated-support catalogue, and no "
    "three-repeated-support catalogue. This audits only saturation of the "
    "stored-prefix repeated-support model; it is not a proof of support "
    "existence, not a proof of genuine rich-class order, not a proof of row "
    "forcing, not a proof of n=9, not a proof of the bridge, and not a "
    "counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_3_repeated_support_saturation_audit.json"
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


def _extension_profile(
    support_catalogue: Mapping[int, Sequence[int]],
) -> dict[str, object]:
    by_center: dict[str, dict[str, object]] = {}
    candidate_count = 0
    for center in sorted(support_catalogue):
        if center == TARGET_ROW_CENTER:
            continue
        support_masks = support_catalogue[center]
        repeated_masks = _repeated_support_masks(center, support_masks)
        candidate_count += len(repeated_masks)
        used_mask = 0
        for support_mask in support_masks:
            used_mask |= support_mask
        available_labels = [
            label
            for label in CYCLIC_ORDER
            if label != center and not (used_mask & (1 << label))
        ]
        by_center[str(center)] = {
            "support_count": len(set(support_masks)),
            "available_label_count": len(available_labels),
            "available_labels": available_labels,
            "next_repeated_support_candidate_count": len(repeated_masks),
        }
    return {
        "next_repeated_support_candidate_count": candidate_count,
        "by_center": by_center,
    }


def _catalogue_record(
    *,
    prefix_index: int,
    prefix: Mapping[str, object],
    base_supports: Mapping[int, Sequence[int]],
    support_catalogue: Mapping[int, Sequence[int]],
    repeated_support_count: int,
    ordered_generation_paths: Sequence[Sequence[Mapping[str, object]]],
) -> dict[str, object]:
    return {
        "prefix_survivor_index": prefix_index,
        "connector_support": prefix["connector_support"],
        "chain_centers": prefix["chain_centers"],
        "chain": prefix["chain"],
        "closure_before_supply": sorted(_prefix_closure(prefix)),
        "repeated_support_count": repeated_support_count,
        "repeated_supports": _added_supports(base_supports, support_catalogue),
        "auxiliary_support_catalogue": _compact_catalogue(support_catalogue),
        "ordered_generation_path_count": len(ordered_generation_paths),
        "ordered_generation_paths": [
            [dict(step) for step in path] for path in ordered_generation_paths
        ],
        "extension_profile": _extension_profile(support_catalogue),
    }


def _enumerate_repeated_support_catalogues() -> dict[str, object]:
    chain_payload = build_t12_81_3_chain_closure_csp_payload()
    prefix_survivors = chain_payload.get("prefix_survivors")
    if not isinstance(prefix_survivors, Sequence):
        raise AssertionError("prefix_survivors must be a sequence")

    levels: dict[
        int,
        dict[tuple[int, tuple[tuple[int, tuple[int, ...]], ...]], dict[str, object]],
    ] = {}
    stack: list[tuple[int, Mapping[str, object], dict[int, list[int]], int]] = []
    ordered_path_counts: Counter[str] = Counter()

    def ensure_level(
        level: int,
    ) -> dict[tuple[int, tuple[tuple[int, tuple[int, ...]], ...]], dict[str, object]]:
        return levels.setdefault(level, {})

    for prefix_index, prefix in enumerate(prefix_survivors):
        if not isinstance(prefix, Mapping):
            raise AssertionError("prefix survivor must be a mapping")
        base_supports = _prefix_auxiliary_supports(prefix)
        key = (prefix_index, _catalogue_key(base_supports))
        ensure_level(0)[key] = {
            "prefix": prefix,
            "base_supports": base_supports,
            "support_catalogue": base_supports,
            "ordered_generation_paths": [[]],
        }
        ordered_path_counts["0"] += 1
        stack.append((prefix_index, prefix, base_supports, 0))

    while stack:
        prefix_index, prefix, support_catalogue, repeated_count = stack.pop()
        for center in sorted(support_catalogue):
            if center == TARGET_ROW_CENTER:
                continue
            for repeated_support in _repeated_support_masks(
                center,
                support_catalogue[center],
            ):
                next_catalogue = {
                    support_center: list(support_masks)
                    for support_center, support_masks in support_catalogue.items()
                }
                next_catalogue[center].append(repeated_support)
                next_level = repeated_count + 1
                key = (prefix_index, _catalogue_key(next_catalogue))
                parent_key = (prefix_index, _catalogue_key(support_catalogue))
                parent = levels[repeated_count][parent_key]
                parent_paths = parent.get("ordered_generation_paths")
                if not isinstance(parent_paths, Sequence):
                    raise AssertionError("ordered_generation_paths must be a sequence")
                extension_step = _support_summary(center, repeated_support)
                new_paths = [
                    [*path, extension_step]
                    for path in parent_paths
                    if isinstance(path, Sequence)
                ]
                ordered_path_counts[str(next_level)] += len(new_paths)
                next_records = ensure_level(next_level)
                if key not in next_records:
                    next_records[key] = {
                        "prefix": prefix,
                        "base_supports": _prefix_auxiliary_supports(prefix),
                        "support_catalogue": next_catalogue,
                        "ordered_generation_paths": [],
                    }
                    stack.append((prefix_index, prefix, next_catalogue, next_level))
                paths = next_records[key]["ordered_generation_paths"]
                if not isinstance(paths, list):
                    raise AssertionError("ordered_generation_paths must be a list")
                paths.extend(new_paths)

    level_summaries: list[dict[str, object]] = []
    level_records: dict[str, list[dict[str, object]]] = {}
    terminal_records: list[dict[str, object]] = []
    max_level = max(levels)
    for level in range(max_level + 2):
        raw_records = levels.get(level, {})
        records: list[dict[str, object]] = []
        for (prefix_index, _), raw_record in sorted(
            raw_records.items(),
            key=lambda item: (item[0][0], item[0][1]),
        ):
            prefix = raw_record["prefix"]
            base_supports = raw_record["base_supports"]
            support_catalogue = raw_record["support_catalogue"]
            ordered_generation_paths = raw_record["ordered_generation_paths"]
            if not isinstance(prefix, Mapping):
                raise AssertionError("prefix must be a mapping")
            if not isinstance(base_supports, Mapping):
                raise AssertionError("base supports must be a mapping")
            if not isinstance(support_catalogue, Mapping):
                raise AssertionError("support catalogue must be a mapping")
            if not isinstance(ordered_generation_paths, Sequence):
                raise AssertionError("ordered generation paths must be a sequence")
            record = _catalogue_record(
                prefix_index=prefix_index,
                prefix=prefix,
                base_supports=base_supports,
                support_catalogue=support_catalogue,
                repeated_support_count=level,
                ordered_generation_paths=ordered_generation_paths,
            )
            records.append(record)
            extension_profile = record["extension_profile"]
            if (
                isinstance(extension_profile, Mapping)
                and extension_profile["next_repeated_support_candidate_count"] == 0
            ):
                terminal_records.append(record)
        level_records[str(level)] = records
        level_summaries.append(
            {
                "repeated_support_count": level,
                "unique_catalogue_count": len(records),
                "ordered_generation_path_count": ordered_path_counts[str(level)],
            }
        )

    return {
        "source_prefix_survivor_count": len(prefix_survivors),
        "max_repeated_support_count": max_level,
        "level_summaries": level_summaries,
        "level_records": level_records,
        "terminal_records": terminal_records,
    }


def build_t12_81_3_repeated_support_saturation_audit_payload() -> dict[str, object]:
    """Return the deterministic repeated-support saturation audit packet."""

    scan = _enumerate_repeated_support_catalogues()
    level_summaries = scan["level_summaries"]
    if not isinstance(level_summaries, Sequence):
        raise AssertionError("level_summaries must be a sequence")
    unique_by_level = {
        str(item["repeated_support_count"]): item["unique_catalogue_count"]
        for item in level_summaries
        if isinstance(item, Mapping)
    }
    path_by_level = {
        str(item["repeated_support_count"]): item["ordered_generation_path_count"]
        for item in level_summaries
        if isinstance(item, Mapping)
    }

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This audit starts only from the four stored chain-closure prefix survivors.",
            "It enumerates repeated supports only at already activated non-target prefix centers.",
            "Every repeated support must be disjoint from all supports already present at its own center.",
            "No three-repeated-support catalogue exists under this stored-prefix repeated-support model.",
            "The scan uses support-catalogue combinatorics only, not Euclidean realizability.",
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
            "unique_catalogue_count_by_repeated_support_count": unique_by_level,
            "ordered_generation_path_count_by_repeated_support_count": path_by_level,
            "max_repeated_support_count": scan["max_repeated_support_count"],
            "terminal_catalogue_count": len(scan["terminal_records"]),
            "three_repeated_support_catalogue_count": unique_by_level["3"],
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This saturates only the stored-prefix same-center-disjoint "
                "repeated-support model. It does not handle genuinely richer "
                "catalogues, new activation provenance, support existence, "
                "row forcing, n=9, the bridge, or Erdos Problem #97."
            ),
        },
        "repeated_support_saturation_scan": {
            "level_summaries": level_summaries,
            "level_records": scan["level_records"],
            "terminal_records": scan["terminal_records"],
        },
        "source_chain_closure_csp": {
            "path": CHAIN_CLOSURE_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": CHAIN_CLOSURE_SCHEMA,
            "status": CHAIN_CLOSURE_STATUS,
            "scan_status": CHAIN_CLOSURE_SCAN_STATUS,
        },
        "source_one_repeated_support_audit": {
            "path": ONE_REPEATED_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": ONE_REPEATED_SCHEMA,
            "status": ONE_REPEATED_STATUS,
            "scan_status": ONE_REPEATED_SCAN_STATUS,
        },
        "source_two_repeated_support_audit": {
            "path": TWO_REPEATED_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": TWO_REPEATED_SCHEMA,
            "status": TWO_REPEATED_STATUS,
            "scan_status": TWO_REPEATED_SCAN_STATUS,
        },
        "provenance": {
            "generator": (
                "scripts/check_bootstrap_t12_81_3_repeated_support_saturation_audit.py"
            ),
            "command": (
                "python scripts/check_bootstrap_t12_81_3_repeated_support_saturation_audit.py "
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
        "unique_catalogue_count_by_repeated_support_count": {
            "0": 4,
            "1": 5,
            "2": 1,
            "3": 0,
        },
        "ordered_generation_path_count_by_repeated_support_count": {
            "0": 4,
            "1": 5,
            "2": 2,
            "3": 0,
        },
        "max_repeated_support_count": 2,
        "terminal_catalogue_count": 4,
        "three_repeated_support_catalogue_count": 0,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    scan = payload.get("repeated_support_saturation_scan")
    if not isinstance(scan, Mapping):
        raise AssertionError("repeated_support_saturation_scan must be a mapping")
    records = scan.get("level_records")
    if not isinstance(records, Mapping):
        raise AssertionError("level_records must be a mapping")
    level_two = records.get("2")
    if not isinstance(level_two, Sequence) or len(level_two) != 1:
        raise AssertionError("expected one two-repeated-support catalogue")
    level_three = records.get("3")
    if level_three != []:
        raise AssertionError("expected no three-repeated-support catalogues")

    terminal_records = scan.get("terminal_records")
    if not isinstance(terminal_records, Sequence) or len(terminal_records) != 4:
        raise AssertionError("expected four terminal repeated-support catalogues")
    if any(
        not isinstance(record, Mapping)
        or not isinstance(record.get("extension_profile"), Mapping)
        or record["extension_profile"]["next_repeated_support_candidate_count"] != 0
        for record in terminal_records
    ):
        raise AssertionError("terminal records must have no next repeated support")

    source = payload.get("source_two_repeated_support_audit")
    if not isinstance(source, Mapping):
        raise AssertionError("source_two_repeated_support_audit must be a mapping")
    if source.get("schema") != TWO_REPEATED_SCHEMA:
        raise AssertionError("source two-repeated schema drifted")
    if source.get("scan_status") != TWO_REPEATED_SCAN_STATUS:
        raise AssertionError("source two-repeated scan status drifted")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_3_repeated_support_saturation_audit.py"
    ):
        raise AssertionError("provenance generator drifted")
