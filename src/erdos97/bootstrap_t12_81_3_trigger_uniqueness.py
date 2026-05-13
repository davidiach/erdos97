"""Trigger-family uniqueness audit for the bootstrap/T12 81:3 escape.

The auxiliary-rich-class CSP lets one center-6 supply class and one center-3
connector-avoiding class exist as auxiliary rich classes.  This packet checks
that, inside those specified trigger families, same-center distance-class
disjointness already permits at most one such class at each center.

The audit is exact finite bookkeeping.  It is not a row-forcing theorem and not
a proof of the bootstrap bridge.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_81_3_escape_auxiliary_csp import (
    DEFAULT_ARTIFACT as AUXILIARY_CSP_ARTIFACT,
    SCAN_STATUS as AUXILIARY_CSP_SCAN_STATUS,
    SCHEMA as AUXILIARY_CSP_SCHEMA,
    STATUS as AUXILIARY_CSP_STATUS,
)
from erdos97.bootstrap_t12_81_3_escape_candidates import (
    CONNECTOR_PAIR,
    CYCLIC_ORDER,
    SUPPLY_CENTER,
    _center_3_connector_avoiding_classes,
    _supply_classes,
)
from erdos97.bootstrap_t12_81_3_order_escape import (
    TARGET_DELETION_SEED,
    TARGET_ROW_CENTER,
    TARGET_ROW_KEY,
)


SCHEMA = "erdos97.bootstrap_t12_81_3_trigger_uniqueness.v1"
STATUS = "BOOTSTRAP_T12_81_3_TRIGGER_UNIQUENESS_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "SPECIFIED_TRIGGER_FAMILIES_ARE_SAME_CENTER_UNIQUE"
CLAIM_SCOPE = (
    "Same-center disjointness audit for the specified 81:3 escape trigger "
    "families. It proves only that the center-6 supply-trigger family contains "
    "no two pairwise disjoint classes, and the center-3 connector-avoiding "
    "trigger family contains no two pairwise disjoint classes. Therefore a "
    "genuine rich-class catalogue at those centers can contain at most one "
    "class from each specified family. This is not a proof of genuine "
    "rich-class order, not a proof of row forcing, not a proof of n=9, not a "
    "proof of the bridge, and not a counterexample."
)
RICH_CLASS_DISJOINTNESS_RULE = (
    "At one fixed center, two distinct rich distance classes are disjoint: if "
    "they shared a witness, the two radii would be equal and the classes would "
    "be the same distance class."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_3_trigger_uniqueness.json"
)


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _max_pairwise_disjoint_family_size(classes: Sequence[Sequence[int]]) -> int:
    class_sets = [set(row) for row in classes]
    for size in range(len(class_sets), 0, -1):
        for indices in combinations(range(len(class_sets)), size):
            if all(
                class_sets[a].isdisjoint(class_sets[b])
                for a, b in combinations(indices, 2)
            ):
                return size
    return 0


def _selected_row_options_for_auxiliary_class(
    center: int,
    auxiliary_class: Sequence[int],
) -> list[list[int]]:
    universe = set(CYCLIC_ORDER) - {center}
    auxiliary_set = set(auxiliary_class)
    if len(auxiliary_set) != 4:
        raise AssertionError("auxiliary classes must be 4-sets")
    if center in auxiliary_set:
        raise AssertionError("an auxiliary class cannot contain its center")
    disjoint_complement = sorted(universe - auxiliary_set)
    if len(disjoint_complement) != 4:
        raise AssertionError("expected a unique disjoint 4-set complement")

    options = []
    for row in combinations(sorted(universe), 4):
        row_set = set(row)
        if row_set == auxiliary_set or row_set.isdisjoint(auxiliary_set):
            options.append(list(row))
    expected_options = [sorted(auxiliary_set), disjoint_complement]
    if {tuple(row) for row in options} != {tuple(row) for row in expected_options}:
        raise AssertionError("unexpected same-center selected-row option set")
    return expected_options


def _class_family_audit(
    *,
    family_name: str,
    center: int,
    classes: Sequence[Sequence[int]],
    common_trigger: Sequence[int],
) -> dict[str, object]:
    class_sets = [set(row) for row in classes]
    common_trigger_set = set(common_trigger)
    if any(len(row) != 4 for row in class_sets):
        raise AssertionError(f"{family_name} classes must be 4-sets")
    if any(center in row for row in class_sets):
        raise AssertionError(f"{family_name} classes cannot contain center {center}")
    if any(not common_trigger_set <= row for row in class_sets):
        raise AssertionError(f"{family_name} classes must contain {common_trigger}")

    pair_records: list[dict[str, object]] = []
    intersection_histogram: Counter[int] = Counter()
    for left, right in combinations(range(len(classes)), 2):
        intersection = sorted(class_sets[left] & class_sets[right])
        intersection_histogram[len(intersection)] += 1
        pair_records.append(
            {
                "class_indices": [left, right],
                "left_class": _int_list(classes[left]),
                "right_class": _int_list(classes[right]),
                "intersection": intersection,
                "intersection_size": len(intersection),
                "pairwise_disjoint": len(intersection) == 0,
            }
        )

    option_records = [
        {
            "auxiliary_class": _int_list(rich_class),
            "selected_row_options_equal_or_disjoint": _selected_row_options_for_auxiliary_class(
                center, rich_class
            ),
        }
        for rich_class in classes
    ]
    option_count_histogram = Counter(
        len(record["selected_row_options_equal_or_disjoint"])
        for record in option_records
    )

    return {
        "family_name": family_name,
        "center": center,
        "common_trigger": _int_list(common_trigger),
        "class_count": len(classes),
        "classes": [_int_list(row) for row in classes],
        "pair_count": len(pair_records),
        "intersection_size_histogram": {
            str(size): count for size, count in sorted(intersection_histogram.items())
        },
        "disjoint_pair_count": sum(
            1 for record in pair_records if record["pairwise_disjoint"]
        ),
        "all_pairs_intersect": all(
            not record["pairwise_disjoint"] for record in pair_records
        ),
        "max_same_center_pairwise_disjoint_family_size": _max_pairwise_disjoint_family_size(
            classes
        ),
        "selected_row_option_count_histogram": {
            str(size): count for size, count in sorted(option_count_histogram.items())
        },
        "selected_row_option_records": option_records,
        "pairwise_intersections": pair_records,
    }


def build_t12_81_3_trigger_uniqueness_payload() -> dict[str, object]:
    """Return the deterministic 81:3 trigger-family uniqueness packet."""

    supply_classes = _supply_classes()
    connector_records = _center_3_connector_avoiding_classes()
    connector_classes = [
        _int_list(record["rich_class"]) for record in connector_records
    ]

    supply_audit = _class_family_audit(
        family_name="center_6_supply_classes_containing_deletion_seed",
        center=SUPPLY_CENTER,
        classes=supply_classes,
        common_trigger=TARGET_DELETION_SEED,
    )
    connector_audit = _class_family_audit(
        family_name="center_3_connector_avoiding_classes_using_label_6",
        center=TARGET_ROW_CENTER,
        classes=connector_classes,
        common_trigger=[4, 6],
    )

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "same_center_disjointness_rule": RICH_CLASS_DISJOINTNESS_RULE,
        "interpretation_warnings": [
            "This audit is internal to the specified center-6 supply-trigger family and center-3 connector-avoiding family.",
            "It does not enumerate rich classes outside those specified trigger families.",
            "It does not prove that either trigger class exists in a genuine counterexample.",
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
            "center_6_supply_class_count": supply_audit["class_count"],
            "center_6_supply_pair_count": supply_audit["pair_count"],
            "center_6_supply_intersection_size_histogram": supply_audit[
                "intersection_size_histogram"
            ],
            "center_6_supply_disjoint_pair_count": supply_audit[
                "disjoint_pair_count"
            ],
            "center_6_supply_max_same_center_pairwise_disjoint_family_size": supply_audit[
                "max_same_center_pairwise_disjoint_family_size"
            ],
            "center_6_selected_row_option_count_histogram": supply_audit[
                "selected_row_option_count_histogram"
            ],
            "center_3_connector_avoiding_class_count": connector_audit[
                "class_count"
            ],
            "center_3_connector_pair_count": connector_audit["pair_count"],
            "center_3_connector_intersection_size_histogram": connector_audit[
                "intersection_size_histogram"
            ],
            "center_3_connector_disjoint_pair_count": connector_audit[
                "disjoint_pair_count"
            ],
            "center_3_connector_max_same_center_pairwise_disjoint_family_size": connector_audit[
                "max_same_center_pairwise_disjoint_family_size"
            ],
            "center_3_selected_row_option_count_histogram": connector_audit[
                "selected_row_option_count_histogram"
            ],
            "same_center_trigger_uniqueness_status": SCAN_STATUS,
            "catalogue_gap_removed": (
                "Within these specified trigger families, a richer catalogue "
                "cannot contain two center-6 supply triggers or two center-3 "
                "connector-avoiding triggers at the same center, because any "
                "two such classes intersect."
            ),
            "remaining_gap": (
                "This does not rule out replacement classes outside the "
                "specified trigger families, does not prove trigger-class "
                "existence, and does not add new minimal/rich-class forcing "
                "hypotheses."
            ),
        },
        "family_audits": {
            "center_6_supply": supply_audit,
            "center_3_connector_avoiding": connector_audit,
        },
        "source_auxiliary_csp": {
            "path": AUXILIARY_CSP_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": AUXILIARY_CSP_SCHEMA,
            "status": AUXILIARY_CSP_STATUS,
            "scan_status": AUXILIARY_CSP_SCAN_STATUS,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_3_trigger_uniqueness.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_3_trigger_uniqueness.py "
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
        "same_center_disjointness_rule": RICH_CLASS_DISJOINTNESS_RULE,
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
        "center_6_supply_class_count": 5,
        "center_6_supply_pair_count": 10,
        "center_6_supply_intersection_size_histogram": {"3": 10},
        "center_6_supply_disjoint_pair_count": 0,
        "center_6_supply_max_same_center_pairwise_disjoint_family_size": 1,
        "center_6_selected_row_option_count_histogram": {"2": 5},
        "center_3_connector_avoiding_class_count": 8,
        "center_3_connector_pair_count": 28,
        "center_3_connector_intersection_size_histogram": {"2": 12, "3": 16},
        "center_3_connector_disjoint_pair_count": 0,
        "center_3_connector_max_same_center_pairwise_disjoint_family_size": 1,
        "center_3_selected_row_option_count_histogram": {"2": 8},
        "same_center_trigger_uniqueness_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    family_audits = payload.get("family_audits")
    if not isinstance(family_audits, Mapping):
        raise AssertionError("family_audits must be a mapping")
    supply = family_audits.get("center_6_supply")
    connector = family_audits.get("center_3_connector_avoiding")
    for name, audit, expected_class_count in (
        ("center_6_supply", supply, 5),
        ("center_3_connector_avoiding", connector, 8),
    ):
        if not isinstance(audit, Mapping):
            raise AssertionError(f"{name} audit must be a mapping")
        if audit.get("class_count") != expected_class_count:
            raise AssertionError(f"{name} class count drifted")
        if audit.get("disjoint_pair_count") != 0:
            raise AssertionError(f"{name} must have no disjoint trigger pairs")
        if audit.get("all_pairs_intersect") is not True:
            raise AssertionError(f"{name} trigger pairs must all intersect")
        if audit.get("max_same_center_pairwise_disjoint_family_size") != 1:
            raise AssertionError(f"{name} must be same-center unique")

    source = payload.get("source_auxiliary_csp")
    if not isinstance(source, Mapping):
        raise AssertionError("source_auxiliary_csp must be a mapping")
    if source.get("schema") != AUXILIARY_CSP_SCHEMA:
        raise AssertionError("source auxiliary-CSP schema drifted")
    if source.get("scan_status") != AUXILIARY_CSP_SCAN_STATUS:
        raise AssertionError("source auxiliary-CSP scan status drifted")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_3_trigger_uniqueness.py"
    ):
        raise AssertionError("provenance generator drifted")
