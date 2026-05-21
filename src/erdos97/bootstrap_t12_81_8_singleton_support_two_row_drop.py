"""Two-row-drop audit for the bootstrap/T12 81:8 singleton-support target.

This packet relaxes the source-81 row-8 singleton-support audit one step beyond
the one-row-drop scan.  For each pair of source-81 rows outside center 8, it
allows both rows to be replaced by arbitrary 4-sets while row 8 ranges over the
nine singleton-support activation rows.

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

from erdos97.bootstrap_t12_81_8_singleton_support_audit import (
    BOOTSTRAP_CORE_WITNESSES,
    CYCLIC_ORDER,
    DEFAULT_ARTIFACT as ONE_ROW_DROP_ARTIFACT,
    ORIGINAL_ROW,
    SCAN_STATUS as ONE_ROW_DROP_SCAN_STATUS,
    SCHEMA as ONE_ROW_DROP_SCHEMA,
    SINGLETON_SUPPORT_LABELS,
    SOURCE_RECORD_ID,
    STATUS as ONE_ROW_DROP_STATUS,
    TARGET_ROW_CENTER,
    TARGET_ROW_KEY,
    _base_selected_rows,
    _target_row_candidates,
)


SCHEMA = "erdos97.bootstrap_t12_81_8_singleton_support_two_row_drop.v1"
STATUS = "BOOTSTRAP_T12_81_8_SINGLETON_SUPPORT_TWO_ROW_DROP_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "ONLY_ORIGINAL_ROW8_SURVIVES_WHEN_ANY_TWO_OTHER_SOURCE81_ROWS_DROP"
CLAIM_SCOPE = (
    "Two-row-drop relaxation of the source-81 row-8 singleton-support audit. "
    "For each pair of the eight source-81 rows outside center 8, it allows both "
    "rows to be replaced by arbitrary 4-sets while row 8 uses one of the nine "
    "singleton-support activation rows. The only 28 survivors are the trivial "
    "original-neighborhood survivors: row 8 is the original [0,2,5,6] row and "
    "both dropped rows are also original. This does not prove singleton "
    "support existence, row forcing, n=9, the bootstrap bridge, or Erdos "
    "Problem #97, and is not a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_8_singleton_support_two_row_drop.json"
)

LABELS = list(CYCLIC_ORDER)
TWO_ROW_DROP_CENTERS = [
    center for center in CYCLIC_ORDER if center != TARGET_ROW_CENTER
]
ALL_PAIRS = list(combinations(LABELS, 2))
EXPECTED_REJECTION_COUNTS = {'crossing': 1871,
 'row_pair+crossing': 1063,
 'row_pair+witness_pair': 1277,
 'row_pair+witness_pair+crossing': 1214683,
 'survive': 28,
 'witness_pair+crossing': 15878}
EXPECTED_PER_DROPPED_PAIR_REJECTION_COUNTS = {'0,1': {'crossing': 23,
         'row_pair+crossing': 48,
         'row_pair+witness_pair': 132,
         'row_pair+witness_pair+crossing': 43641,
         'survive': 1,
         'witness_pair+crossing': 255},
 '0,2': {'crossing': 46,
         'row_pair+crossing': 47,
         'row_pair+witness_pair': 45,
         'row_pair+witness_pair+crossing': 43523,
         'survive': 1,
         'witness_pair+crossing': 438},
 '0,3': {'crossing': 91,
         'row_pair+crossing': 14,
         'row_pair+witness_pair': 22,
         'row_pair+witness_pair+crossing': 43407,
         'survive': 1,
         'witness_pair+crossing': 565},
 '0,4': {'crossing': 124,
         'row_pair+crossing': 43,
         'row_pair+witness_pair': 59,
         'row_pair+witness_pair+crossing': 42945,
         'survive': 1,
         'witness_pair+crossing': 928},
 '0,5': {'crossing': 49,
         'row_pair+crossing': 16,
         'row_pair+witness_pair': 32,
         'row_pair+witness_pair+crossing': 43208,
         'survive': 1,
         'witness_pair+crossing': 794},
 '0,6': {'crossing': 37,
         'row_pair+crossing': 38,
         'row_pair+witness_pair': 46,
         'row_pair+witness_pair+crossing': 43649,
         'survive': 1,
         'witness_pair+crossing': 329},
 '0,7': {'crossing': 21,
         'row_pair+crossing': 35,
         'row_pair+witness_pair': 45,
         'row_pair+witness_pair+crossing': 43663,
         'survive': 1,
         'witness_pair+crossing': 335},
 '1,2': {'crossing': 36,
         'row_pair+crossing': 60,
         'row_pair+witness_pair': 50,
         'row_pair+witness_pair+crossing': 43507,
         'survive': 1,
         'witness_pair+crossing': 446},
 '1,3': {'crossing': 96,
         'row_pair+crossing': 73,
         'row_pair+witness_pair': 85,
         'row_pair+witness_pair+crossing': 43377,
         'survive': 1,
         'witness_pair+crossing': 468},
 '1,4': {'crossing': 76,
         'row_pair+crossing': 17,
         'row_pair+witness_pair': 43,
         'row_pair+witness_pair+crossing': 43447,
         'survive': 1,
         'witness_pair+crossing': 516},
 '1,5': {'crossing': 68,
         'row_pair+crossing': 29,
         'row_pair+witness_pair': 60,
         'row_pair+witness_pair+crossing': 43106,
         'survive': 1,
         'witness_pair+crossing': 836},
 '1,6': {'crossing': 81,
         'row_pair+crossing': 67,
         'row_pair+witness_pair': 91,
         'row_pair+witness_pair+crossing': 43433,
         'survive': 1,
         'witness_pair+crossing': 427},
 '1,7': {'crossing': 45,
         'row_pair+crossing': 30,
         'row_pair+witness_pair': 35,
         'row_pair+witness_pair+crossing': 43673,
         'survive': 1,
         'witness_pair+crossing': 316},
 '2,3': {'crossing': 110,
         'row_pair+crossing': 24,
         'row_pair+witness_pair': 30,
         'row_pair+witness_pair+crossing': 43190,
         'survive': 1,
         'witness_pair+crossing': 745},
 '2,4': {'crossing': 55,
         'row_pair+crossing': 52,
         'row_pair+witness_pair': 45,
         'row_pair+witness_pair+crossing': 43219,
         'survive': 1,
         'witness_pair+crossing': 728},
 '2,5': {'crossing': 63,
         'row_pair+witness_pair': 22,
         'row_pair+witness_pair+crossing': 43378,
         'survive': 1,
         'witness_pair+crossing': 636},
 '2,6': {'crossing': 95,
         'row_pair+crossing': 40,
         'row_pair+witness_pair': 32,
         'row_pair+witness_pair+crossing': 43264,
         'survive': 1,
         'witness_pair+crossing': 668},
 '2,7': {'crossing': 93,
         'row_pair+crossing': 18,
         'row_pair+witness_pair': 32,
         'row_pair+witness_pair+crossing': 43098,
         'survive': 1,
         'witness_pair+crossing': 858},
 '3,4': {'crossing': 129,
         'row_pair+crossing': 64,
         'row_pair+witness_pair': 30,
         'row_pair+witness_pair+crossing': 43125,
         'survive': 1,
         'witness_pair+crossing': 751},
 '3,5': {'crossing': 47,
         'row_pair+crossing': 30,
         'row_pair+witness_pair': 45,
         'row_pair+witness_pair+crossing': 43263,
         'survive': 1,
         'witness_pair+crossing': 714},
 '3,6': {'crossing': 79,
         'row_pair+crossing': 26,
         'row_pair+witness_pair': 22,
         'row_pair+witness_pair+crossing': 43462,
         'survive': 1,
         'witness_pair+crossing': 510},
 '3,7': {'crossing': 119,
         'row_pair+crossing': 46,
         'row_pair+witness_pair': 58,
         'row_pair+witness_pair+crossing': 42920,
         'survive': 1,
         'witness_pair+crossing': 956},
 '4,5': {'crossing': 58,
         'row_pair+crossing': 20,
         'row_pair+witness_pair': 30,
         'row_pair+witness_pair+crossing': 43315,
         'survive': 1,
         'witness_pair+crossing': 676},
 '4,6': {'crossing': 82,
         'row_pair+crossing': 84,
         'row_pair+witness_pair': 45,
         'row_pair+witness_pair+crossing': 43519,
         'survive': 1,
         'witness_pair+crossing': 369},
 '4,7': {'crossing': 77,
         'row_pair+crossing': 18,
         'row_pair+witness_pair': 22,
         'row_pair+witness_pair+crossing': 43421,
         'survive': 1,
         'witness_pair+crossing': 561},
 '5,6': {'crossing': 28,
         'row_pair+crossing': 46,
         'row_pair+witness_pair': 44,
         'row_pair+witness_pair+crossing': 43683,
         'survive': 1,
         'witness_pair+crossing': 298},
 '5,7': {'crossing': 21,
         'row_pair+crossing': 33,
         'row_pair+witness_pair': 45,
         'row_pair+witness_pair+crossing': 43505,
         'survive': 1,
         'witness_pair+crossing': 495},
 '6,7': {'crossing': 22,
         'row_pair+crossing': 45,
         'row_pair+witness_pair': 30,
         'row_pair+witness_pair+crossing': 43742,
         'survive': 1,
         'witness_pair+crossing': 260}}
EXPECTED_PER_TARGET_CENTER_CLASS_REJECTION_COUNTS = {'0,1,2,5': {'crossing': 138,
             'row_pair+crossing': 123,
             'row_pair+witness_pair': 26,
             'row_pair+witness_pair+crossing': 136360,
             'witness_pair+crossing': 553},
 '0,1,2,6': {'crossing': 161,
             'row_pair+crossing': 164,
             'row_pair+witness_pair': 27,
             'row_pair+witness_pair+crossing': 136232,
             'witness_pair+crossing': 616},
 '0,2,3,5': {'crossing': 198,
             'row_pair+crossing': 123,
             'row_pair+witness_pair': 14,
             'row_pair+witness_pair+crossing': 136119,
             'witness_pair+crossing': 746},
 '0,2,3,6': {'crossing': 10,
             'row_pair+crossing': 5,
             'row_pair+witness_pair': 24,
             'row_pair+witness_pair+crossing': 136325,
             'witness_pair+crossing': 836},
 '0,2,4,5': {'crossing': 183,
             'row_pair+crossing': 43,
             'row_pair+witness_pair+crossing': 132500,
             'witness_pair+crossing': 4474},
 '0,2,4,6': {'crossing': 122,
             'row_pair+crossing': 219,
             'row_pair+witness_pair': 27,
             'row_pair+witness_pair+crossing': 136209,
             'witness_pair+crossing': 623},
 '0,2,5,6': {'crossing': 819,
             'row_pair+crossing': 175,
             'row_pair+witness_pair': 903,
             'row_pair+witness_pair+crossing': 132216,
             'survive': 28,
             'witness_pair+crossing': 3059},
 '0,2,5,7': {'crossing': 92,
             'row_pair+crossing': 156,
             'row_pair+witness_pair': 181,
             'row_pair+witness_pair+crossing': 136136,
             'witness_pair+crossing': 635},
 '0,2,6,7': {'crossing': 148,
             'row_pair+crossing': 55,
             'row_pair+witness_pair': 75,
             'row_pair+witness_pair+crossing': 132586,
             'witness_pair+crossing': 4336}}


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _row_key(row: Sequence[int]) -> str:
    return ",".join(str(label) for label in row)


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
    target_rows = _target_row_candidates()
    target_masks = [_row_mask(row) for row in target_rows]
    replacement_masks = {
        center: _all_replacement_row_masks(center) for center in TWO_ROW_DROP_CENTERS
    }

    total_counts: Counter[str] = Counter()
    per_target_row_counts: dict[str, Counter[str]] = {
        _row_key(candidate): Counter() for candidate in target_rows
    }
    dropped_pair_summaries: list[dict[str, object]] = []
    survivors: list[dict[str, object]] = []

    for dropped_a, dropped_b in combinations(TWO_ROW_DROP_CENTERS, 2):
        dropped_counts: Counter[str] = Counter()
        for target_row, target_mask in zip(target_rows, target_masks, strict=True):
            target_key = _row_key(target_row)
            base_candidate = list(base_masks)
            base_candidate[TARGET_ROW_CENTER] = target_mask
            for row_a in replacement_masks[dropped_a]:
                candidate_a = list(base_candidate)
                candidate_a[dropped_a] = row_a
                for row_b in replacement_masks[dropped_b]:
                    row_masks = list(candidate_a)
                    row_masks[dropped_b] = row_b
                    category = _scan_candidate_category(row_masks)
                    dropped_counts[category] += 1
                    total_counts[category] += 1
                    per_target_row_counts[target_key][category] += 1
                    if category == "survive":
                        dropped_classes = {
                            str(dropped_a): _mask_to_row(row_a),
                            str(dropped_b): _mask_to_row(row_b),
                        }
                        survivors.append(
                            {
                                "target_center_class": list(target_row),
                                "target_center_class_is_original": (
                                    list(target_row) == ORIGINAL_ROW
                                ),
                                "dropped_centers": [dropped_a, dropped_b],
                                "dropped_center_classes": dropped_classes,
                                "dropped_center_classes_are_original": (
                                    dropped_classes[str(dropped_a)]
                                    == list(base_rows[dropped_a])
                                    and dropped_classes[str(dropped_b)]
                                    == list(base_rows[dropped_b])
                                ),
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
                "rejection_category_counts": _json_counter(dropped_counts),
            }
        )

    return {
        "candidate_count": sum(total_counts.values()),
        "rejection_category_counts": _json_counter(total_counts),
        "per_target_center_class": [
            {
                "target_center_class": list(candidate),
                "target_center_class_is_original": list(candidate) == ORIGINAL_ROW,
                "candidate_count": sum(
                    per_target_row_counts[_row_key(candidate)].values()
                ),
                "surviving_candidate_count": per_target_row_counts[
                    _row_key(candidate)
                ].get("survive", 0),
                "rejection_category_counts": _json_counter(
                    per_target_row_counts[_row_key(candidate)]
                ),
            }
            for candidate in target_rows
        ],
        "per_dropped_pair": dropped_pair_summaries,
        "survivors": survivors,
    }


def build_t12_81_8_singleton_support_two_row_drop_payload() -> dict[str, object]:
    """Return the deterministic source-81 row-8 two-row-drop audit."""

    base_rows = _base_selected_rows()
    if base_rows[TARGET_ROW_CENTER] != ORIGINAL_ROW:
        raise AssertionError("source-81 row 8 drifted")

    target_rows = _target_row_candidates()
    scan = _scan_candidates(base_rows)
    survivors = scan["survivors"]
    if not isinstance(survivors, Sequence):
        raise AssertionError("survivors must be a sequence")
    non_original_survivors = [
        survivor
        for survivor in survivors
        if not isinstance(survivor, Mapping)
        or not survivor["target_center_class_is_original"]
        or not survivor["dropped_center_classes_are_original"]
    ]

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This scan drops exactly two of the eight source-81 rows outside center 8.",
            (
                "Center 8 is still restricted to the nine singleton-support "
                "activation rows."
            ),
            (
                "The scan uses incidence and crossing filters only, not "
                "Euclidean realizability."
            ),
            (
                "No n=9 finite-case status, bridge status, official status, "
                "or counterexample status changes."
            ),
        ],
        "summary": {
            "target_row_key": TARGET_ROW_KEY,
            "source_record_ids": [SOURCE_RECORD_ID],
            "cyclic_order": CYCLIC_ORDER,
            "target_center": TARGET_ROW_CENTER,
            "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
            "singleton_support_labels": SINGLETON_SUPPORT_LABELS,
            "original_target_center_class": ORIGINAL_ROW,
            "target_center_candidate_count": len(target_rows),
            "two_row_drop_centers": TWO_ROW_DROP_CENTERS,
            "dropped_pair_count": len(list(combinations(TWO_ROW_DROP_CENTERS, 2))),
            "dropped_row_replacement_count_per_center": 70,
            "candidate_count": scan["candidate_count"],
            "surviving_candidate_count": len(survivors),
            "two_row_drop_non_original_survivor_count": len(non_original_survivors),
            "two_row_drop_survivors_all_original_rows": not non_original_survivors,
            "rejection_category_counts": scan["rejection_category_counts"],
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This does not prove singleton support existence, does not "
                "prove the row is forced by minimal or rich-class geometry, "
                "does not allow three or more other rows to move, and does not "
                "model additional auxiliary rich supports."
            ),
        },
        "source_rows": {str(center): base_rows[center] for center in CYCLIC_ORDER},
        "candidate_generation": {
            "target_center_candidate_classes": target_rows,
            "candidate_rule": (
                "4-sets at center 8 containing bootstrap-core witnesses [0,2] "
                "and at least one singleton support label from [5,6]."
            ),
            "dropped_row_choice_count_per_center": {
                str(center): len(_all_replacement_row_masks(center))
                for center in TWO_ROW_DROP_CENTERS
            },
        },
        "per_target_center_class": scan["per_target_center_class"],
        "per_dropped_pair": scan["per_dropped_pair"],
        "survivors": survivors,
        "source_one_row_drop_scan": {
            "path": ONE_ROW_DROP_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": ONE_ROW_DROP_SCHEMA,
            "status": ONE_ROW_DROP_STATUS,
            "scan_status": ONE_ROW_DROP_SCAN_STATUS,
        },
        "provenance": {
            "generator": (
                "scripts/check_bootstrap_t12_81_8_singleton_support_two_row_drop.py"
            ),
            "command": (
                "python "
                "scripts/check_bootstrap_t12_81_8_singleton_support_two_row_drop.py "
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
        "source_record_ids": [SOURCE_RECORD_ID],
        "cyclic_order": CYCLIC_ORDER,
        "target_center": TARGET_ROW_CENTER,
        "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
        "singleton_support_labels": SINGLETON_SUPPORT_LABELS,
        "original_target_center_class": ORIGINAL_ROW,
        "target_center_candidate_count": 9,
        "two_row_drop_centers": TWO_ROW_DROP_CENTERS,
        "dropped_pair_count": 28,
        "dropped_row_replacement_count_per_center": 70,
        "candidate_count": 1234800,
        "surviving_candidate_count": 28,
        "two_row_drop_non_original_survivor_count": 0,
        "two_row_drop_survivors_all_original_rows": True,
        "rejection_category_counts": EXPECTED_REJECTION_COUNTS,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    per_target = payload.get("per_target_center_class")
    if not isinstance(per_target, Sequence) or len(per_target) != 9:
        raise AssertionError("expected nine per-target-center-class summaries")
    for record in per_target:
        if not isinstance(record, Mapping):
            raise AssertionError("per-target-center-class summaries must be mappings")
        row_key = _row_key(_int_list(record["target_center_class"]))
        expected_counts = EXPECTED_PER_TARGET_CENTER_CLASS_REJECTION_COUNTS[row_key]
        if record.get("candidate_count") != 137200:
            raise AssertionError(f"target row {row_key} has bad candidate count")
        if record.get("rejection_category_counts") != expected_counts:
            raise AssertionError(f"target row {row_key} rejection counts drifted")
        expected_survivors = 28 if record.get("target_center_class_is_original") else 0
        if record.get("surviving_candidate_count") != expected_survivors:
            raise AssertionError(f"target row {row_key} survivor count drifted")

    per_dropped = payload.get("per_dropped_pair")
    if not isinstance(per_dropped, Sequence) or len(per_dropped) != 28:
        raise AssertionError("expected 28 dropped-pair summaries")
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
        if record.get("candidate_count") != 44100:
            raise AssertionError(f"dropped pair {key!r} has bad candidate count")
        if record.get("surviving_candidate_count") != 1:
            raise AssertionError(f"dropped pair {key!r} should have one survivor")
        expected_counts = EXPECTED_PER_DROPPED_PAIR_REJECTION_COUNTS[key]
        if record.get("rejection_category_counts") != expected_counts:
            raise AssertionError(f"dropped pair {key!r} rejection counts drifted")

    survivors = payload.get("survivors")
    if not isinstance(survivors, Sequence) or len(survivors) != 28:
        raise AssertionError("expected 28 two-row-drop survivors")
    if any(
        not isinstance(survivor, Mapping)
        or not survivor.get("target_center_class_is_original")
        or not survivor.get("dropped_center_classes_are_original")
        for survivor in survivors
    ):
        raise AssertionError("two-row-drop survivors should keep original rows")

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
        "scripts/check_bootstrap_t12_81_8_singleton_support_two_row_drop.py"
    ):
        raise AssertionError("provenance generator drifted")
