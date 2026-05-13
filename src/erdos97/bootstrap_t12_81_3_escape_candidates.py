"""Relaxed candidate scan for the bootstrap/T12 81:3 escape.

This packet relaxes the fixed-row-preservation guard from the order-escape
packet by allowing rows 3 and 6 of source 81 to be replaced:

* row 6 must supply label 6 before center 3 from the deletion seed [0,1,4];
* row 3 must then activate through a connector-avoiding triple using label 6.

The other seven source-81 selected rows are preserved.  The scan is purely
incidence/crossing bookkeeping; it is not a Euclidean realization theorem and
does not prove the bootstrap bridge.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_81_3_order_escape import (
    DEFAULT_ARTIFACT as ORDER_ESCAPE_ARTIFACT,
    GENUINE_ESCAPE_STATUS,
    SCHEMA as ORDER_ESCAPE_SCHEMA,
    STATUS as ORDER_ESCAPE_STATUS,
    TARGET_DELETION_SEED,
    TARGET_ROW_CENTER,
    TARGET_ROW_KEY,
    build_t12_81_3_order_escape_payload,
)
from erdos97.incidence_filters import crossing_bisector_violations


SCHEMA = "erdos97.bootstrap_t12_81_3_escape_candidates.v1"
STATUS = "BOOTSTRAP_T12_81_3_ESCAPE_CANDIDATE_SCAN_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "NO_BASIC_FILTER_SURVIVORS_UNDER_SOURCE81_OTHER_ROWS_PRESERVED"
CLAIM_SCOPE = (
    "Relaxed 81:3 escape-candidate scan preserving the seven source-81 rows "
    "outside centers 3 and 6. It enumerates the 40 basic ways to supply label "
    "6 before center 3 and then activate center 3 through a connector-avoiding "
    "triple; all fail row-pair, witness-pair, or crossing filters. This is not "
    "a proof of genuine rich-class order, not a proof of row forcing, not a "
    "proof of n=9, not a proof of the bridge, and not a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT / "data" / "certificates" / "bootstrap_t12_81_3_escape_candidates.json"
)

N = 9
CYCLIC_ORDER = list(range(N))
SUPPLY_CENTER = 6
PRESERVED_ROW_CENTERS = [0, 1, 2, 4, 5, 7, 8]
REPLACED_ROW_CENTERS = [TARGET_ROW_CENTER, SUPPLY_CENTER]
CONNECTOR_PAIR = [0, 1]
CONNECTOR_AVOIDING_TRIPLES = [[0, 4, 6], [1, 4, 6]]
EXPECTED_REJECTION_COUNTS = {
    "crossing": 2,
    "row_pair+witness_pair+crossing": 33,
    "witness_pair+crossing": 5,
}


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _base_selected_rows() -> list[list[int]]:
    payload = build_t12_81_3_order_escape_payload()
    audit = payload["fixed_singleton_order_audit"]
    if not isinstance(audit, Mapping):
        raise AssertionError("order-escape audit must be a mapping")
    rows = audit["selected_rows"]
    if not isinstance(rows, Sequence):
        raise AssertionError("selected_rows must be a sequence")
    return [_int_list(row) for row in rows]


def _row_pair_cap_violations(rows: Sequence[Sequence[int]]) -> list[dict[str, object]]:
    violations: list[dict[str, object]] = []
    row_sets = [set(row) for row in rows]
    for i, j in combinations(range(len(rows)), 2):
        intersection = sorted(row_sets[i] & row_sets[j])
        if len(intersection) > 2:
            violations.append(
                {
                    "centers": [i, j],
                    "intersection": intersection,
                    "intersection_size": len(intersection),
                }
            )
    return violations


def _witness_pair_cap_violations(
    rows: Sequence[Sequence[int]],
) -> list[dict[str, object]]:
    pair_to_centers: dict[tuple[int, int], list[int]] = {}
    for center, row in enumerate(rows):
        for pair in combinations(sorted(row), 2):
            pair_to_centers.setdefault(pair, []).append(center)
    return [
        {"pair": list(pair), "centers": centers, "center_count": len(centers)}
        for pair, centers in sorted(pair_to_centers.items())
        if len(centers) > 2
    ]


def _crossing_violations(rows: Sequence[Sequence[int]]) -> list[dict[str, object]]:
    return [
        {"source_chord": list(source), "witness_chord": list(target)}
        for source, target in crossing_bisector_violations(rows, CYCLIC_ORDER)
    ]


def _supply_classes() -> list[list[int]]:
    seed = set(TARGET_DELETION_SEED)
    fourths = [
        label for label in CYCLIC_ORDER if label not in seed and label != SUPPLY_CENTER
    ]
    return [sorted([*TARGET_DELETION_SEED, fourth]) for fourth in fourths]


def _center_3_connector_avoiding_classes() -> list[dict[str, object]]:
    classes: list[dict[str, object]] = []
    for triple in CONNECTOR_AVOIDING_TRIPLES:
        triple_set = set(triple)
        fourths = [
            label
            for label in CYCLIC_ORDER
            if label not in triple_set
            and label != TARGET_ROW_CENTER
            and set([*triple, label]) & set(CONNECTOR_PAIR) != set(CONNECTOR_PAIR)
        ]
        for fourth in fourths:
            classes.append(
                {
                    "activation_triple": triple,
                    "fourth": fourth,
                    "rich_class": sorted([*triple, fourth]),
                }
            )
    return classes


def _candidate_records(base_rows: Sequence[Sequence[int]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for supply_class in _supply_classes():
        supply_fourth = next(label for label in supply_class if label not in TARGET_DELETION_SEED)
        for center_3_data in _center_3_connector_avoiding_classes():
            center_3_class = _int_list(center_3_data["rich_class"])  # type: ignore[arg-type]
            rows = [list(row) for row in base_rows]
            rows[SUPPLY_CENTER] = supply_class
            rows[TARGET_ROW_CENTER] = center_3_class

            row_pair_violations = _row_pair_cap_violations(rows)
            witness_pair_violations = _witness_pair_cap_violations(rows)
            crossing_violations = _crossing_violations(rows)
            rejection_reasons = []
            if row_pair_violations:
                rejection_reasons.append("row_pair")
            if witness_pair_violations:
                rejection_reasons.append("witness_pair")
            if crossing_violations:
                rejection_reasons.append("crossing")
            category = "+".join(rejection_reasons) if rejection_reasons else "survive"

            records.append(
                {
                    "supply_center": SUPPLY_CENTER,
                    "supply_class": supply_class,
                    "supply_fourth": supply_fourth,
                    "target_center": TARGET_ROW_CENTER,
                    "target_center_activation_triple": center_3_data[
                        "activation_triple"
                    ],
                    "target_center_fourth": center_3_data["fourth"],
                    "target_center_class": center_3_class,
                    "preserved_row_centers": PRESERVED_ROW_CENTERS,
                    "row_pair_cap_violations": row_pair_violations,
                    "witness_pair_cap_violations": witness_pair_violations,
                    "crossing_violations": crossing_violations,
                    "rejection_reasons": rejection_reasons,
                    "rejection_category": category,
                    "passes_basic_incidence_crossing_filters": not rejection_reasons,
                }
            )
    return records


def build_t12_81_3_escape_candidate_payload() -> dict[str, object]:
    """Return the deterministic relaxed 81:3 escape-candidate scan."""

    base_rows = _base_selected_rows()
    candidates = _candidate_records(base_rows)
    rejection_counts = dict(sorted(Counter(c["rejection_category"] for c in candidates).items()))
    survivors = [
        candidate
        for candidate in candidates
        if candidate["passes_basic_incidence_crossing_filters"]
    ]
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This scan preserves only the seven source-81 rows outside centers 3 and 6.",
            "Rows 3 and 6 are replaced by one candidate rich class each.",
            "The scan uses incidence and crossing filters only, not Euclidean realizability.",
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
            "preserved_row_centers": PRESERVED_ROW_CENTERS,
            "replaced_row_centers": REPLACED_ROW_CENTERS,
            "center_6_supply_class_count": len(_supply_classes()),
            "center_3_connector_avoiding_class_count": len(
                _center_3_connector_avoiding_classes()
            ),
            "candidate_count": len(candidates),
            "surviving_candidate_count": len(survivors),
            "rejection_category_counts": rejection_counts,
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This does not rule out escape mechanisms that fail to preserve "
                "the other source-81 rows, use richer catalogues than one "
                "replacement class at centers 3 and 6, or require additional "
                "minimal/rich-class hypotheses."
            ),
        },
        "preserved_source_rows": {
            str(center): base_rows[center] for center in PRESERVED_ROW_CENTERS
        },
        "candidate_generation": {
            "center_6_supply_classes": _supply_classes(),
            "center_3_connector_avoiding_classes": _center_3_connector_avoiding_classes(),
        },
        "candidates": candidates,
        "survivors": survivors,
        "source_order_escape": {
            "path": ORDER_ESCAPE_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": ORDER_ESCAPE_SCHEMA,
            "status": ORDER_ESCAPE_STATUS,
            "genuine_escape_status": GENUINE_ESCAPE_STATUS,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_3_escape_candidates.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_3_escape_candidates.py "
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
        "preserved_row_centers": PRESERVED_ROW_CENTERS,
        "replaced_row_centers": REPLACED_ROW_CENTERS,
        "center_6_supply_class_count": 5,
        "center_3_connector_avoiding_class_count": 8,
        "candidate_count": 40,
        "surviving_candidate_count": 0,
        "rejection_category_counts": EXPECTED_REJECTION_COUNTS,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    warnings = payload.get("interpretation_warnings")
    if not isinstance(warnings, Sequence):
        raise AssertionError("interpretation_warnings must be a sequence")
    if not any("preserves only the seven source-81 rows" in str(w) for w in warnings):
        raise AssertionError("warnings must preserve the row-preservation scope")
    if not any("not Euclidean realizability" in str(w) for w in warnings):
        raise AssertionError("warnings must preserve the non-realizability scope")

    candidates = payload.get("candidates")
    if not isinstance(candidates, Sequence) or len(candidates) != 40:
        raise AssertionError("expected exactly 40 escape candidates")
    if any(
        isinstance(candidate, Mapping)
        and candidate.get("passes_basic_incidence_crossing_filters")
        for candidate in candidates
    ):
        raise AssertionError("no candidate should pass the basic filters")

    survivors = payload.get("survivors")
    if survivors != []:
        raise AssertionError("survivors must be empty")

    source = payload.get("source_order_escape")
    if not isinstance(source, Mapping):
        raise AssertionError("source_order_escape must be a mapping")
    if source.get("schema") != ORDER_ESCAPE_SCHEMA:
        raise AssertionError("source order-escape schema drifted")
    if source.get("genuine_escape_status") != GENUINE_ESCAPE_STATUS:
        raise AssertionError("source genuine escape status drifted")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_3_escape_candidates.py"
    ):
        raise AssertionError("provenance generator drifted")
