"""Two-row-drop scan for the bootstrap/T12 81:3 escape.

This packet relaxes the 81:3 escape-candidate neighborhood one step beyond the
one-row-drop scan.  For each pair of source-81 rows outside centers 3 and 6, it
allows both rows to be replaced by arbitrary 4-sets while also replacing
centers 3 and 6 as in the escape-candidate scan.

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
    _base_selected_rows,
    _center_3_connector_avoiding_classes,
    _supply_classes,
)
from erdos97.bootstrap_t12_81_3_escape_one_row_drop import (
    DEFAULT_ARTIFACT as ONE_ROW_DROP_ARTIFACT,
    SCAN_STATUS as ONE_ROW_DROP_SCAN_STATUS,
    SCHEMA as ONE_ROW_DROP_SCHEMA,
    STATUS as ONE_ROW_DROP_STATUS,
)
from erdos97.bootstrap_t12_81_3_escape_candidates import (
    CONNECTOR_PAIR,
    CYCLIC_ORDER,
    PRESERVED_ROW_CENTERS,
    SUPPLY_CENTER,
)
from erdos97.bootstrap_t12_81_3_order_escape import (
    TARGET_DELETION_SEED,
    TARGET_ROW_CENTER,
    TARGET_ROW_KEY,
)


SCHEMA = "erdos97.bootstrap_t12_81_3_escape_two_row_drop.v1"
STATUS = "BOOTSTRAP_T12_81_3_ESCAPE_TWO_ROW_DROP_SCAN_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "NO_BASIC_FILTER_SURVIVORS_WHEN_ANY_TWO_OTHER_SOURCE81_ROWS_DROP"
CLAIM_SCOPE = (
    "Two-row-drop relaxation of the 81:3 escape-candidate scan. For each pair "
    "of the seven source-81 rows outside centers 3 and 6, it allows both rows "
    "to be replaced by arbitrary 4-sets while also replacing centers 3 and 6 "
    "by one candidate class each. All 4,116,000 candidates fail row-pair, "
    "witness-pair, or crossing filters. This is not a proof of genuine "
    "rich-class order, not a proof of row forcing, not a proof of n=9, not a "
    "proof of the bridge, and not a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_3_escape_two_row_drop.json"
)

N = len(CYCLIC_ORDER)
LABELS = list(CYCLIC_ORDER)
ALL_PAIRS = list(combinations(LABELS, 2))
REPLACED_ROW_CENTERS = [TARGET_ROW_CENTER, SUPPLY_CENTER]
EXPECTED_REJECTION_COUNTS = {
    "crossing": 2393,
    "row_pair+crossing": 1476,
    "row_pair+witness_pair": 59,
    "row_pair+witness_pair+crossing": 4074937,
    "witness_pair+crossing": 37135,
}
EXPECTED_PER_DROPPED_PAIR_REJECTION_COUNTS = {
    "0,1": {
        "crossing": 58,
        "row_pair+crossing": 48,
        "row_pair+witness_pair+crossing": 194506,
        "witness_pair+crossing": 1388,
    },
    "0,2": {
        "crossing": 58,
        "row_pair+crossing": 54,
        "row_pair+witness_pair+crossing": 194287,
        "witness_pair+crossing": 1601,
    },
    "0,4": {
        "crossing": 99,
        "row_pair+crossing": 9,
        "row_pair+witness_pair+crossing": 193975,
        "witness_pair+crossing": 1917,
    },
    "0,5": {
        "crossing": 71,
        "row_pair+crossing": 62,
        "row_pair+witness_pair+crossing": 193649,
        "witness_pair+crossing": 2218,
    },
    "0,7": {
        "crossing": 150,
        "row_pair+crossing": 68,
        "row_pair+witness_pair+crossing": 193416,
        "witness_pair+crossing": 2366,
    },
    "0,8": {
        "crossing": 65,
        "row_pair+crossing": 37,
        "row_pair+witness_pair+crossing": 193911,
        "witness_pair+crossing": 1987,
    },
    "1,2": {
        "crossing": 59,
        "row_pair+crossing": 84,
        "row_pair+witness_pair+crossing": 194566,
        "witness_pair+crossing": 1291,
    },
    "1,4": {
        "crossing": 83,
        "row_pair+crossing": 41,
        "row_pair+witness_pair+crossing": 194919,
        "witness_pair+crossing": 957,
    },
    "1,5": {
        "crossing": 103,
        "row_pair+crossing": 71,
        "row_pair+witness_pair+crossing": 194332,
        "witness_pair+crossing": 1494,
    },
    "1,7": {
        "crossing": 131,
        "row_pair+crossing": 14,
        "row_pair+witness_pair+crossing": 193330,
        "witness_pair+crossing": 2525,
    },
    "1,8": {
        "crossing": 111,
        "row_pair+crossing": 118,
        "row_pair+witness_pair+crossing": 194223,
        "witness_pair+crossing": 1548,
    },
    "2,4": {
        "crossing": 45,
        "row_pair+crossing": 86,
        "row_pair+witness_pair+crossing": 194912,
        "witness_pair+crossing": 957,
    },
    "2,5": {
        "crossing": 43,
        "row_pair+crossing": 44,
        "row_pair+witness_pair": 9,
        "row_pair+witness_pair+crossing": 194869,
        "witness_pair+crossing": 1035,
    },
    "2,7": {
        "crossing": 374,
        "row_pair+crossing": 95,
        "row_pair+witness_pair": 10,
        "row_pair+witness_pair+crossing": 191823,
        "witness_pair+crossing": 3698,
    },
    "2,8": {
        "crossing": 88,
        "row_pair+crossing": 11,
        "row_pair+witness_pair+crossing": 193986,
        "witness_pair+crossing": 1915,
    },
    "4,5": {
        "crossing": 27,
        "row_pair+crossing": 77,
        "row_pair+witness_pair+crossing": 195359,
        "witness_pair+crossing": 537,
    },
    "4,7": {
        "crossing": 151,
        "row_pair+crossing": 43,
        "row_pair+witness_pair+crossing": 194071,
        "witness_pair+crossing": 1735,
    },
    "4,8": {
        "crossing": 215,
        "row_pair+crossing": 133,
        "row_pair+witness_pair": 31,
        "row_pair+witness_pair+crossing": 193524,
        "witness_pair+crossing": 2097,
    },
    "5,7": {
        "crossing": 114,
        "row_pair+crossing": 163,
        "row_pair+witness_pair+crossing": 193914,
        "witness_pair+crossing": 1809,
    },
    "5,8": {
        "crossing": 74,
        "row_pair+crossing": 59,
        "row_pair+witness_pair": 9,
        "row_pair+witness_pair+crossing": 194476,
        "witness_pair+crossing": 1382,
    },
    "7,8": {
        "crossing": 274,
        "row_pair+crossing": 159,
        "row_pair+witness_pair+crossing": 192889,
        "witness_pair+crossing": 2678,
    },
}


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _row_mask(row: Iterable[int]) -> int:
    mask = 0
    for label in row:
        mask |= 1 << int(label)
    return mask


def _mask_to_row(mask: int) -> list[int]:
    return [label for label in LABELS if (mask >> label) & 1]


def _all_replacement_row_masks(center: int) -> list[int]:
    labels = [label for label in LABELS if label != center]
    return [_row_mask(row) for row in combinations(labels, 4)]


def _between_cyclic(a: int, x: int, b: int) -> bool:
    if a < b:
        return a < x < b
    return x > a or x < b


def _crosses_pair(i: int, j: int, a: int, b: int) -> bool:
    if len({i, j, a, b}) < 4:
        return False
    return (
        _between_cyclic(i, a, j) != _between_cyclic(i, b, j)
        and _between_cyclic(a, i, b) != _between_cyclic(a, j, b)
    )


PAIR_INDEX = {pair: index for index, pair in enumerate(ALL_PAIRS)}
MASK_TO_PAIR_INDEX = {
    (1 << a) | (1 << b): PAIR_INDEX[(a, b)] for a, b in ALL_PAIRS
}
CROSS_OK = {
    (i, j, PAIR_INDEX[(a, b)]): _crosses_pair(i, j, a, b)
    for i, j in ALL_PAIRS
    for a, b in ALL_PAIRS
}
ROW_PAIR_INDICES = {
    row_mask: [
        PAIR_INDEX[(a, b)]
        for a, b in combinations(_mask_to_row(row_mask), 2)
    ]
    for row_mask in [_row_mask(row) for row in combinations(LABELS, 4)]
}


def _scan_candidate_category(row_masks: Sequence[int]) -> str:
    row_pair_violation = False
    crossing_violation = False
    for i, j in ALL_PAIRS:
        intersection = row_masks[i] & row_masks[j]
        intersection_size = intersection.bit_count()
        if intersection_size > 2:
            row_pair_violation = True
        elif intersection_size == 2:
            pair_index = MASK_TO_PAIR_INDEX[intersection]
            if not CROSS_OK[(i, j, pair_index)]:
                crossing_violation = True

    witness_pair_violation = False
    pair_counts = [0] * len(ALL_PAIRS)
    for row_mask in row_masks:
        for pair_index in ROW_PAIR_INDICES[row_mask]:
            pair_counts[pair_index] += 1
            if pair_counts[pair_index] > 2:
                witness_pair_violation = True

    rejection_reasons = []
    if row_pair_violation:
        rejection_reasons.append("row_pair")
    if witness_pair_violation:
        rejection_reasons.append("witness_pair")
    if crossing_violation:
        rejection_reasons.append("crossing")
    return "+".join(rejection_reasons) if rejection_reasons else "survive"


def _scan_candidates(base_rows: Sequence[Sequence[int]]) -> dict[str, object]:
    base_masks = [_row_mask(row) for row in base_rows]
    supply_masks = [_row_mask(row) for row in _supply_classes()]
    center_3_masks = [
        _row_mask(_int_list(record["rich_class"]))
        for record in _center_3_connector_avoiding_classes()
    ]
    replacement_masks = {
        center: _all_replacement_row_masks(center) for center in PRESERVED_ROW_CENTERS
    }

    total_counts: Counter[str] = Counter()
    dropped_pair_summaries: list[dict[str, object]] = []
    survivors: list[dict[str, object]] = []

    for dropped_a, dropped_b in combinations(PRESERVED_ROW_CENTERS, 2):
        dropped_counts: Counter[str] = Counter()
        for supply_mask in supply_masks:
            for center_3_mask in center_3_masks:
                base_candidate = list(base_masks)
                base_candidate[SUPPLY_CENTER] = supply_mask
                base_candidate[TARGET_ROW_CENTER] = center_3_mask
                for row_a in replacement_masks[dropped_a]:
                    candidate_a = list(base_candidate)
                    candidate_a[dropped_a] = row_a
                    for row_b in replacement_masks[dropped_b]:
                        row_masks = list(candidate_a)
                        row_masks[dropped_b] = row_b
                        category = _scan_candidate_category(row_masks)
                        dropped_counts[category] += 1
                        total_counts[category] += 1
                        if category == "survive":
                            survivors.append(
                                {
                                    "dropped_centers": [dropped_a, dropped_b],
                                    "dropped_center_classes": {
                                        str(dropped_a): _mask_to_row(row_a),
                                        str(dropped_b): _mask_to_row(row_b),
                                    },
                                    "supply_center_class": _mask_to_row(supply_mask),
                                    "target_center_class": _mask_to_row(center_3_mask),
                                }
                            )

        dropped_pair_summaries.append(
            {
                "dropped_centers": [dropped_a, dropped_b],
                "source_rows": {
                    str(dropped_a): list(base_rows[dropped_a]),
                    str(dropped_b): list(base_rows[dropped_b]),
                },
                "replacement_row_count_per_center": 70,
                "candidate_count": sum(dropped_counts.values()),
                "surviving_candidate_count": dropped_counts.get("survive", 0),
                "rejection_category_counts": dict(sorted(dropped_counts.items())),
            }
        )

    return {
        "candidate_count": sum(total_counts.values()),
        "survivors": survivors,
        "rejection_category_counts": dict(sorted(total_counts.items())),
        "per_dropped_pair": dropped_pair_summaries,
    }


def build_t12_81_3_escape_two_row_drop_payload() -> dict[str, object]:
    """Return the deterministic two-row-drop escape scan."""

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
            "This scan drops exactly two of the seven source-81 rows that were preserved in the original escape-candidate scan.",
            "Rows 3 and 6 are also replaced by one candidate rich class each, as in the previous scans.",
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
            "two_row_drop_centers": PRESERVED_ROW_CENTERS,
            "also_replaced_row_centers": REPLACED_ROW_CENTERS,
            "center_6_supply_class_count": len(_supply_classes()),
            "center_3_connector_avoiding_class_count": len(
                _center_3_connector_avoiding_classes()
            ),
            "dropped_pair_count": len(list(combinations(PRESERVED_ROW_CENTERS, 2))),
            "dropped_row_replacement_count_per_center": 70,
            "candidate_count": scan["candidate_count"],
            "surviving_candidate_count": len(survivors),
            "rejection_category_counts": scan["rejection_category_counts"],
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This does not rule out escape mechanisms that move three or "
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
                str(center): len(_all_replacement_row_masks(center))
                for center in PRESERVED_ROW_CENTERS
            },
        },
        "per_dropped_pair": scan["per_dropped_pair"],
        "survivors": survivors,
        "source_one_row_drop_scan": {
            "path": ONE_ROW_DROP_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": ONE_ROW_DROP_SCHEMA,
            "status": ONE_ROW_DROP_STATUS,
            "scan_status": ONE_ROW_DROP_SCAN_STATUS,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_3_escape_two_row_drop.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_3_escape_two_row_drop.py "
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
        "two_row_drop_centers": PRESERVED_ROW_CENTERS,
        "also_replaced_row_centers": REPLACED_ROW_CENTERS,
        "center_6_supply_class_count": 5,
        "center_3_connector_avoiding_class_count": 8,
        "dropped_pair_count": 21,
        "dropped_row_replacement_count_per_center": 70,
        "candidate_count": 4116000,
        "surviving_candidate_count": 0,
        "rejection_category_counts": EXPECTED_REJECTION_COUNTS,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    per_dropped = payload.get("per_dropped_pair")
    if not isinstance(per_dropped, Sequence) or len(per_dropped) != 21:
        raise AssertionError("expected 21 dropped-pair summaries")
    for record in per_dropped:
        if not isinstance(record, Mapping):
            raise AssertionError("dropped-pair summaries must be mappings")
        centers = record.get("dropped_centers")
        if not isinstance(centers, Sequence) or len(centers) != 2:
            raise AssertionError("dropped_centers must be a pair")
        key = f"{centers[0]},{centers[1]}"
        if key not in EXPECTED_PER_DROPPED_PAIR_REJECTION_COUNTS:
            raise AssertionError(f"unexpected dropped pair {key!r}")
        if record.get("replacement_row_count_per_center") != 70:
            raise AssertionError(f"dropped pair {key!r} has bad row count")
        if record.get("candidate_count") != 196000:
            raise AssertionError(f"dropped pair {key!r} has bad candidate count")
        if record.get("surviving_candidate_count") != 0:
            raise AssertionError(f"dropped pair {key!r} should have no survivors")
        expected_counts = EXPECTED_PER_DROPPED_PAIR_REJECTION_COUNTS[key]
        if record.get("rejection_category_counts") != expected_counts:
            raise AssertionError(f"dropped pair {key!r} rejection counts drifted")

    survivors = payload.get("survivors")
    if survivors != []:
        raise AssertionError("survivors must be empty")

    source = payload.get("source_one_row_drop_scan")
    if not isinstance(source, Mapping):
        raise AssertionError("source_one_row_drop_scan must be a mapping")
    if source.get("schema") != ONE_ROW_DROP_SCHEMA:
        raise AssertionError("source one-row-drop schema drifted")
    if source.get("scan_status") != ONE_ROW_DROP_SCAN_STATUS:
        raise AssertionError("source one-row-drop scan status drifted")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_3_escape_two_row_drop.py"
    ):
        raise AssertionError("provenance generator drifted")
