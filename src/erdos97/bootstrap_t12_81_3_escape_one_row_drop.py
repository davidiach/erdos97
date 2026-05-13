"""One-row-drop scan for the bootstrap/T12 81:3 escape.

The previous relaxed escape-candidate packet preserves the seven source-81
rows outside centers 3 and 6.  This packet relaxes that guard one step further:
for each of those seven rows, drop that single preserved row and enumerate all
70 possible replacement 4-sets for its center while also replacing centers 3
and 6 as in the escape-candidate scan.

The scan uses only selected-row incidence and cyclic crossing filters.  It is a
proof-mining diagnostic, not a Euclidean realizability theorem and not a proof
of the bootstrap bridge.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_81_3_escape_candidates import (
    CLAIM_SCOPE as ESCAPE_CANDIDATE_CLAIM_SCOPE,
    DEFAULT_ARTIFACT as ESCAPE_CANDIDATE_ARTIFACT,
    SCAN_STATUS as ESCAPE_CANDIDATE_SCAN_STATUS,
    SCHEMA as ESCAPE_CANDIDATE_SCHEMA,
    STATUS as ESCAPE_CANDIDATE_STATUS,
    _base_selected_rows,
    _center_3_connector_avoiding_classes,
    _crossing_violations,
    _row_pair_cap_violations,
    _supply_classes,
    _witness_pair_cap_violations,
)
from erdos97.bootstrap_t12_81_3_order_escape import (
    TARGET_DELETION_SEED,
    TARGET_ROW_CENTER,
    TARGET_ROW_KEY,
)
from erdos97.bootstrap_t12_81_3_escape_candidates import (
    CONNECTOR_PAIR,
    CYCLIC_ORDER,
    PRESERVED_ROW_CENTERS,
    SUPPLY_CENTER,
)


SCHEMA = "erdos97.bootstrap_t12_81_3_escape_one_row_drop.v1"
STATUS = "BOOTSTRAP_T12_81_3_ESCAPE_ONE_ROW_DROP_SCAN_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "NO_BASIC_FILTER_SURVIVORS_WHEN_ANY_ONE_OTHER_SOURCE81_ROW_DROPS"
CLAIM_SCOPE = (
    "One-row-drop relaxation of the 81:3 escape-candidate scan. For each of "
    "the seven source-81 rows outside centers 3 and 6, it allows that one row "
    "to be replaced by an arbitrary 4-set while also replacing centers 3 and "
    "6 by one candidate class each. All 19,600 candidates fail row-pair, "
    "witness-pair, or crossing filters. This is not a proof of genuine "
    "rich-class order, not a proof of row forcing, not a proof of n=9, not a "
    "proof of the bridge, and not a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_3_escape_one_row_drop.json"
)

REPLACED_ROW_CENTERS = [TARGET_ROW_CENTER, SUPPLY_CENTER]
EXPECTED_REJECTION_COUNTS = {
    "crossing": 77,
    "row_pair+crossing": 18,
    "row_pair+witness_pair+crossing": 18889,
    "witness_pair+crossing": 616,
}
EXPECTED_PER_DROPPED_REJECTION_COUNTS = {
    0: {
        "crossing": 8,
        "row_pair+witness_pair+crossing": 2702,
        "witness_pair+crossing": 90,
    },
    1: {
        "crossing": 13,
        "row_pair+crossing": 3,
        "row_pair+witness_pair+crossing": 2706,
        "witness_pair+crossing": 78,
    },
    2: {
        "crossing": 11,
        "row_pair+crossing": 5,
        "row_pair+witness_pair+crossing": 2701,
        "witness_pair+crossing": 83,
    },
    4: {
        "crossing": 8,
        "row_pair+crossing": 3,
        "row_pair+witness_pair+crossing": 2736,
        "witness_pair+crossing": 53,
    },
    5: {
        "crossing": 5,
        "row_pair+crossing": 5,
        "row_pair+witness_pair+crossing": 2731,
        "witness_pair+crossing": 59,
    },
    7: {
        "crossing": 23,
        "row_pair+witness_pair+crossing": 2638,
        "witness_pair+crossing": 139,
    },
    8: {
        "crossing": 9,
        "row_pair+crossing": 2,
        "row_pair+witness_pair+crossing": 2675,
        "witness_pair+crossing": 114,
    },
}


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _all_replacement_rows(center: int) -> list[list[int]]:
    labels = [label for label in CYCLIC_ORDER if label != center]
    return [list(row) for row in combinations(labels, 4)]


def _rejection_category(rows: Sequence[Sequence[int]]) -> str:
    rejection_reasons = []
    if _row_pair_cap_violations(rows):
        rejection_reasons.append("row_pair")
    if _witness_pair_cap_violations(rows):
        rejection_reasons.append("witness_pair")
    if _crossing_violations(rows):
        rejection_reasons.append("crossing")
    return "+".join(rejection_reasons) if rejection_reasons else "survive"


def _scan_candidates(base_rows: Sequence[Sequence[int]]) -> dict[str, object]:
    total_counts: Counter[str] = Counter()
    dropped_summaries: list[dict[str, object]] = []
    survivors: list[dict[str, object]] = []

    supply_classes = _supply_classes()
    center_3_classes = _center_3_connector_avoiding_classes()
    for dropped_center in PRESERVED_ROW_CENTERS:
        dropped_counts: Counter[str] = Counter()
        replacement_rows = _all_replacement_rows(dropped_center)
        for supply_class in supply_classes:
            for center_3_data in center_3_classes:
                center_3_class = _int_list(center_3_data["rich_class"])
                for dropped_row in replacement_rows:
                    rows = [list(row) for row in base_rows]
                    rows[SUPPLY_CENTER] = list(supply_class)
                    rows[TARGET_ROW_CENTER] = center_3_class
                    rows[dropped_center] = dropped_row

                    category = _rejection_category(rows)
                    dropped_counts[category] += 1
                    total_counts[category] += 1
                    if category == "survive":
                        survivors.append(
                            {
                                "dropped_center": dropped_center,
                                "dropped_center_class": dropped_row,
                                "supply_center_class": list(supply_class),
                                "target_center_class": center_3_class,
                                "target_center_activation_triple": center_3_data[
                                    "activation_triple"
                                ],
                            }
                        )

        dropped_summaries.append(
            {
                "dropped_center": dropped_center,
                "source_row": list(base_rows[dropped_center]),
                "replacement_row_count": len(replacement_rows),
                "candidate_count": sum(dropped_counts.values()),
                "surviving_candidate_count": dropped_counts.get("survive", 0),
                "rejection_category_counts": dict(sorted(dropped_counts.items())),
            }
        )

    return {
        "candidate_count": sum(total_counts.values()),
        "survivors": survivors,
        "rejection_category_counts": dict(sorted(total_counts.items())),
        "per_dropped_center": dropped_summaries,
    }


def build_t12_81_3_escape_one_row_drop_payload() -> dict[str, object]:
    """Return the deterministic one-row-drop escape scan."""

    base_rows = _base_selected_rows()
    scan = _scan_candidates(base_rows)
    survivors = scan["survivors"]
    if not isinstance(survivors, Sequence):
        raise AssertionError("survivors must be a sequence")

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This scan drops exactly one of the seven source-81 rows that were preserved in the previous escape-candidate scan.",
            "Rows 3 and 6 are also replaced by one candidate rich class each, as in the previous scan.",
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
            "one_row_drop_centers": PRESERVED_ROW_CENTERS,
            "also_replaced_row_centers": REPLACED_ROW_CENTERS,
            "center_6_supply_class_count": len(_supply_classes()),
            "center_3_connector_avoiding_class_count": len(
                _center_3_connector_avoiding_classes()
            ),
            "dropped_row_replacement_count_per_center": 70,
            "dropped_center_count": len(PRESERVED_ROW_CENTERS),
            "candidate_count": scan["candidate_count"],
            "surviving_candidate_count": len(survivors),
            "rejection_category_counts": scan["rejection_category_counts"],
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This does not rule out escape mechanisms that move two or "
                "more of the other source-81 rows, use richer catalogues than "
                "one replacement class at centers 3 and 6, or require "
                "additional minimal/rich-class hypotheses."
            ),
        },
        "source_rows": {str(center): base_rows[center] for center in CYCLIC_ORDER},
        "candidate_generation": {
            "center_6_supply_classes": _supply_classes(),
            "center_3_connector_avoiding_classes": _center_3_connector_avoiding_classes(),
            "dropped_row_choice_count_per_center": {
                str(center): len(_all_replacement_rows(center))
                for center in PRESERVED_ROW_CENTERS
            },
        },
        "per_dropped_center": scan["per_dropped_center"],
        "survivors": survivors,
        "source_escape_candidate_scan": {
            "path": ESCAPE_CANDIDATE_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": ESCAPE_CANDIDATE_SCHEMA,
            "status": ESCAPE_CANDIDATE_STATUS,
            "scan_status": ESCAPE_CANDIDATE_SCAN_STATUS,
            "claim_scope": ESCAPE_CANDIDATE_CLAIM_SCOPE,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_3_escape_one_row_drop.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_3_escape_one_row_drop.py "
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
        "one_row_drop_centers": PRESERVED_ROW_CENTERS,
        "also_replaced_row_centers": REPLACED_ROW_CENTERS,
        "center_6_supply_class_count": 5,
        "center_3_connector_avoiding_class_count": 8,
        "dropped_row_replacement_count_per_center": 70,
        "dropped_center_count": 7,
        "candidate_count": 19600,
        "surviving_candidate_count": 0,
        "rejection_category_counts": EXPECTED_REJECTION_COUNTS,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    per_dropped = payload.get("per_dropped_center")
    if not isinstance(per_dropped, Sequence) or len(per_dropped) != 7:
        raise AssertionError("expected seven dropped-center summaries")
    for record in per_dropped:
        if not isinstance(record, Mapping):
            raise AssertionError("dropped-center summaries must be mappings")
        center = record.get("dropped_center")
        if center not in EXPECTED_PER_DROPPED_REJECTION_COUNTS:
            raise AssertionError(f"unexpected dropped center {center!r}")
        if record.get("replacement_row_count") != 70:
            raise AssertionError(f"dropped center {center!r} has bad row count")
        if record.get("candidate_count") != 2800:
            raise AssertionError(f"dropped center {center!r} has bad candidate count")
        if record.get("surviving_candidate_count") != 0:
            raise AssertionError(f"dropped center {center!r} should have no survivors")
        expected_counts = EXPECTED_PER_DROPPED_REJECTION_COUNTS[int(center)]
        if record.get("rejection_category_counts") != expected_counts:
            raise AssertionError(
                f"dropped center {center!r} rejection counts drifted"
            )

    survivors = payload.get("survivors")
    if survivors != []:
        raise AssertionError("survivors must be empty")

    source = payload.get("source_escape_candidate_scan")
    if not isinstance(source, Mapping):
        raise AssertionError("source_escape_candidate_scan must be a mapping")
    if source.get("schema") != ESCAPE_CANDIDATE_SCHEMA:
        raise AssertionError("source escape-candidate schema drifted")
    if source.get("scan_status") != ESCAPE_CANDIDATE_SCAN_STATUS:
        raise AssertionError("source escape-candidate scan status drifted")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_3_escape_one_row_drop.py"
    ):
        raise AssertionError("provenance generator drifted")
