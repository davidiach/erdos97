"""Outside-pair audit for the bootstrap/T12 151:6 target.

The outside-pair packet says source 151 row 6 has bootstrap-core witness [0]
and outside-pair supports [3,5], [3,8], and [5,8].  This audit asks a narrow
proof-mining question: if center 6 is activated by one of those outside pairs,
can its selected row differ from the fixed source-151 row while the surrounding
source-151 selected rows are preserved, or while one additional row is allowed
to move?

The answer is no under the basic selected-row incidence and crossing filters.
This is not a Euclidean realizability theorem and not a proof of row forcing.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_81_3_escape_candidates import (
    CYCLIC_ORDER,
    _crossing_violations,
    _row_pair_cap_violations,
    _witness_pair_cap_violations,
)
from erdos97.bootstrap_t12_outside_pair import (
    DEFAULT_ARTIFACT as OUTSIDE_PAIR_ARTIFACT,
    SCHEMA as OUTSIDE_PAIR_SCHEMA,
    STATUS as OUTSIDE_PAIR_STATUS,
    build_t12_outside_pair_payload,
)
from erdos97.bootstrap_vertex_circle_overlay import (
    SCHEMA as OVERLAY_SCHEMA,
    STATUS as OVERLAY_STATUS,
    build_overlay_payload,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_outside_pair_audit.v1"
STATUS = "BOOTSTRAP_T12_151_6_OUTSIDE_PAIR_AUDIT_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "ONLY_ORIGINAL_ROW6_SURVIVES_FIXED_AND_ONE_ROW_DROP_SUPPORT_AUDITS"
CLAIM_SCOPE = (
    "Fixed selected-row-neighborhood outside-pair audit for source 151 row 6. "
    "It enumerates the thirteen center-6 selected rows containing "
    "bootstrap-core witness [0] and one outside support pair from [3,5], "
    "[3,8], or [5,8], then checks the fixed source-151 neighborhood and a "
    "one-row-drop relaxation by row-pair, witness-pair, and crossing filters. "
    "The only survivors keep the original row 6 and, in the one-row-drop scan, "
    "also keep the dropped row equal to its original source-151 row. This does "
    "not prove outside-pair support existence, row forcing, does not prove "
    "n=9, does not prove the bridge, and is not a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_outside_pair_audit.json"
)

SOURCE_RECORD_ID = 151
TARGET_ROW_KEY = "151:6"
TARGET_ROW_CENTER = 6
BOOTSTRAP_CORE_WITNESSES = [0]
OUTSIDE_SUPPORT_PAIRS = [[3, 5], [3, 8], [5, 8]]
ORIGINAL_ROW = [0, 3, 5, 8]
ONE_ROW_DROP_CENTERS = [0, 1, 2, 3, 4, 5, 7, 8]

EXPECTED_FIXED_REJECTION_COUNTS = {
    "crossing": 2,
    "row_pair+witness_pair+crossing": 9,
    "survive": 1,
    "witness_pair+crossing": 1,
}
EXPECTED_ONE_ROW_DROP_REJECTION_COUNTS = {
    "crossing": 118,
    "row_pair+crossing": 15,
    "row_pair+witness_pair": 36,
    "row_pair+witness_pair+crossing": 6824,
    "survive": 8,
    "witness_pair+crossing": 279,
}
EXPECTED_ONE_ROW_DROP_PER_ROW6 = {
    "0,1,3,5": {
        "crossing": 4,
        "row_pair+witness_pair+crossing": 472,
        "witness_pair+crossing": 84,
    },
    "0,1,3,8": {
        "crossing": 36,
        "row_pair+crossing": 3,
        "row_pair+witness_pair+crossing": 477,
        "witness_pair+crossing": 44,
    },
    "0,1,5,8": {
        "crossing": 4,
        "row_pair+crossing": 1,
        "row_pair+witness_pair+crossing": 550,
        "witness_pair+crossing": 5,
    },
    "0,2,3,5": {
        "crossing": 5,
        "row_pair+witness_pair+crossing": 550,
        "witness_pair+crossing": 5,
    },
    "0,2,3,8": {
        "crossing": 4,
        "row_pair+crossing": 1,
        "row_pair+witness_pair+crossing": 549,
        "witness_pair+crossing": 6,
    },
    "0,2,5,8": {
        "row_pair+witness_pair+crossing": 553,
        "witness_pair+crossing": 7,
    },
    "0,3,4,5": {
        "crossing": 3,
        "row_pair+crossing": 1,
        "row_pair+witness_pair+crossing": 552,
        "witness_pair+crossing": 4,
    },
    "0,3,4,8": {
        "row_pair+witness_pair+crossing": 549,
        "witness_pair+crossing": 11,
    },
    "0,3,5,7": {
        "crossing": 1,
        "row_pair+crossing": 3,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 546,
        "witness_pair+crossing": 6,
    },
    "0,3,5,8": {
        "crossing": 24,
        "row_pair+witness_pair": 32,
        "row_pair+witness_pair+crossing": 448,
        "survive": 8,
        "witness_pair+crossing": 48,
    },
    "0,3,7,8": {
        "crossing": 4,
        "row_pair+witness_pair+crossing": 552,
        "witness_pair+crossing": 4,
    },
    "0,4,5,8": {
        "row_pair+witness_pair+crossing": 548,
        "witness_pair+crossing": 12,
    },
    "0,5,7,8": {
        "crossing": 33,
        "row_pair+crossing": 6,
        "row_pair+witness_pair+crossing": 478,
        "witness_pair+crossing": 43,
    },
}
EXPECTED_ONE_ROW_DROP_PER_DROPPED = {
    0: {
        "crossing": 16,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 850,
        "survive": 1,
        "witness_pair+crossing": 39,
    },
    1: {
        "crossing": 22,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 826,
        "survive": 1,
        "witness_pair+crossing": 57,
    },
    2: {
        "crossing": 21,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 839,
        "survive": 1,
        "witness_pair+crossing": 45,
    },
    3: {
        "crossing": 17,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 849,
        "survive": 1,
        "witness_pair+crossing": 39,
    },
    4: {
        "crossing": 10,
        "row_pair+crossing": 4,
        "row_pair+witness_pair": 8,
        "row_pair+witness_pair+crossing": 861,
        "survive": 1,
        "witness_pair+crossing": 26,
    },
    5: {
        "crossing": 11,
        "row_pair+crossing": 4,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 868,
        "survive": 1,
        "witness_pair+crossing": 22,
    },
    7: {
        "crossing": 11,
        "row_pair+crossing": 5,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 863,
        "survive": 1,
        "witness_pair+crossing": 26,
    },
    8: {
        "crossing": 10,
        "row_pair+crossing": 2,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 868,
        "survive": 1,
        "witness_pair+crossing": 25,
    },
}


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


def _source_151_rows() -> list[list[int]]:
    overlay = build_overlay_payload()
    records = overlay.get("records")
    if not isinstance(records, Sequence):
        raise AssertionError("overlay records must be a sequence")
    for record in records:
        if not isinstance(record, Mapping):
            raise AssertionError("overlay records must be mappings")
        if int(record["source_record_id"]) == SOURCE_RECORD_ID:
            return [_int_list(row) for row in record["selected_rows"]]
    raise AssertionError("could not find source 151 in overlay packet")


def _target_outside_pair_record() -> dict[str, object]:
    outside_pair = build_t12_outside_pair_payload()
    records = outside_pair.get("records")
    if not isinstance(records, Sequence):
        raise AssertionError("outside-pair packet records must be a sequence")
    for record in records:
        if not isinstance(record, Mapping):
            raise AssertionError("outside-pair records must be mappings")
        if (
            int(record["source_record_id"]) == SOURCE_RECORD_ID
            and int(record["row_center"]) == TARGET_ROW_CENTER
        ):
            support_pairs = [
                _int_list(option["support_pair"])
                for option in record["support_pair_options"]
            ]
            return {
                "source_record_id": int(record["source_record_id"]),
                "row_center": int(record["row_center"]),
                "witnesses": _int_list(record["witnesses"]),
                "bootstrap_core_witnesses": _int_list(
                    record["bootstrap_core_witnesses"]
                ),
                "outside_witnesses": _int_list(record["outside_witnesses"]),
                "support_pairs": support_pairs,
                "support_pair_modes": record["support_pair_modes"],
                "ledger_private_pair_support_hit_count": int(
                    record["ledger_private_pair_support_hit_count"]
                ),
                "pressure_class": str(record["pressure_class"]),
                "row_center_private_in_all_deletion_closures": bool(
                    record["row_center_private_in_all_deletion_closures"]
                ),
            }
    raise AssertionError("could not find source 151 row 6 in outside-pair packet")


def _target_row_candidates() -> list[list[int]]:
    candidates: set[tuple[int, ...]] = set()
    core = set(BOOTSTRAP_CORE_WITNESSES)
    for support_pair in OUTSIDE_SUPPORT_PAIRS:
        required = core | set(support_pair)
        for fourth in CYCLIC_ORDER:
            if fourth != TARGET_ROW_CENTER and fourth not in required:
                candidates.add(tuple(sorted(required | {fourth})))
    return [list(candidate) for candidate in sorted(candidates)]


def _all_replacement_rows(center: int) -> list[list[int]]:
    labels = [label for label in CYCLIC_ORDER if label != center]
    return [list(row) for row in combinations(labels, 4)]


def _rejection_data(rows: Sequence[Sequence[int]]) -> dict[str, object]:
    row_pair_violations = _row_pair_cap_violations(rows)
    witness_pair_violations = _witness_pair_cap_violations(rows)
    crossing_violations = _crossing_violations(rows)
    reasons = []
    if row_pair_violations:
        reasons.append("row_pair")
    if witness_pair_violations:
        reasons.append("witness_pair")
    if crossing_violations:
        reasons.append("crossing")
    return {
        "row_pair_cap_violations": row_pair_violations,
        "witness_pair_cap_violations": witness_pair_violations,
        "crossing_violations": crossing_violations,
        "rejection_reasons": reasons,
        "rejection_category": "+".join(reasons) if reasons else "survive",
        "passes_basic_incidence_crossing_filters": not reasons,
    }


def _fixed_candidate_records(
    base_rows: Sequence[Sequence[int]],
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for candidate in _target_row_candidates():
        rows = [list(row) for row in base_rows]
        rows[TARGET_ROW_CENTER] = list(candidate)
        rejection = _rejection_data(rows)
        records.append(
            {
                "target_center": TARGET_ROW_CENTER,
                "target_center_class": candidate,
                "is_original_row": candidate == ORIGINAL_ROW,
                **rejection,
            }
        )
    return records


def _scan_one_row_drop(base_rows: Sequence[Sequence[int]]) -> dict[str, object]:
    total_counts: Counter[str] = Counter()
    per_target_row_counts: dict[str, Counter[str]] = {
        _row_key(candidate): Counter() for candidate in _target_row_candidates()
    }
    per_dropped_counts: dict[int, Counter[str]] = {
        center: Counter() for center in ONE_ROW_DROP_CENTERS
    }
    survivors: list[dict[str, object]] = []

    for target_row in _target_row_candidates():
        target_key = _row_key(target_row)
        for dropped_center in ONE_ROW_DROP_CENTERS:
            for replacement_row in _all_replacement_rows(dropped_center):
                rows = [list(row) for row in base_rows]
                rows[TARGET_ROW_CENTER] = list(target_row)
                rows[dropped_center] = list(replacement_row)
                category = str(_rejection_data(rows)["rejection_category"])
                total_counts[category] += 1
                per_target_row_counts[target_key][category] += 1
                per_dropped_counts[dropped_center][category] += 1
                if category == "survive":
                    survivors.append(
                        {
                            "target_center_class": list(target_row),
                            "target_center_class_is_original": (
                                target_row == ORIGINAL_ROW
                            ),
                            "dropped_center": dropped_center,
                            "dropped_center_class": list(replacement_row),
                            "dropped_center_class_is_original": (
                                replacement_row == list(base_rows[dropped_center])
                            ),
                        }
                    )

    return {
        "candidate_count": sum(total_counts.values()),
        "rejection_category_counts": _json_counter(total_counts),
        "per_target_center_class": [
            {
                "target_center_class": list(candidate),
                "target_center_class_is_original": candidate == ORIGINAL_ROW,
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
            for candidate in _target_row_candidates()
        ],
        "per_dropped_center": [
            {
                "dropped_center": center,
                "source_row": list(base_rows[center]),
                "replacement_row_count": len(_all_replacement_rows(center)),
                "candidate_count": sum(per_dropped_counts[center].values()),
                "surviving_candidate_count": per_dropped_counts[center].get(
                    "survive", 0
                ),
                "rejection_category_counts": _json_counter(per_dropped_counts[center]),
            }
            for center in ONE_ROW_DROP_CENTERS
        ],
        "survivors": survivors,
    }


def build_t12_151_6_outside_pair_audit_payload() -> dict[str, object]:
    """Return the deterministic source-151 row-6 outside-pair audit."""

    base_rows = _source_151_rows()
    target_outside_pair_record = _target_outside_pair_record()
    if (
        target_outside_pair_record["bootstrap_core_witnesses"]
        != BOOTSTRAP_CORE_WITNESSES
    ):
        raise AssertionError("source outside-pair bootstrap-core witnesses drifted")
    if target_outside_pair_record["support_pairs"] != OUTSIDE_SUPPORT_PAIRS:
        raise AssertionError("source outside-pair supports drifted")
    if base_rows[TARGET_ROW_CENTER] != ORIGINAL_ROW:
        raise AssertionError("source-151 row 6 drifted")

    fixed_records = _fixed_candidate_records(base_rows)
    fixed_counts = Counter(str(record["rejection_category"]) for record in fixed_records)
    fixed_survivors = [
        record
        for record in fixed_records
        if record["passes_basic_incidence_crossing_filters"]
    ]
    one_row_drop = _scan_one_row_drop(base_rows)
    one_row_drop_survivors = one_row_drop["survivors"]
    if not isinstance(one_row_drop_survivors, Sequence):
        raise AssertionError("one-row-drop survivors must be a sequence")
    non_original_one_drop_survivors = [
        survivor
        for survivor in one_row_drop_survivors
        if not survivor["target_center_class_is_original"]
    ]

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This audit preserves the source-151 selected-row neighborhood, or drops exactly one non-target row in the relaxation.",
            "A row containing bootstrap-core witnesses plus an outside support pair is activation bookkeeping, not a proof that a genuine rich class exists.",
            "The audit uses incidence and crossing filters only, not Euclidean realizability.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "target_row_key": TARGET_ROW_KEY,
            "source_record_ids": [SOURCE_RECORD_ID],
            "cyclic_order": CYCLIC_ORDER,
            "target_center": TARGET_ROW_CENTER,
            "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
            "outside_support_pairs": OUTSIDE_SUPPORT_PAIRS,
            "original_target_center_class": ORIGINAL_ROW,
            "target_center_candidate_count": len(_target_row_candidates()),
            "fixed_neighborhood_candidate_count": len(fixed_records),
            "fixed_neighborhood_surviving_candidate_count": len(fixed_survivors),
            "fixed_neighborhood_non_original_survivor_count": sum(
                1 for survivor in fixed_survivors if not survivor["is_original_row"]
            ),
            "fixed_neighborhood_rejection_category_counts": _json_counter(
                fixed_counts
            ),
            "one_row_drop_centers": ONE_ROW_DROP_CENTERS,
            "one_row_drop_replacement_count_per_center": 70,
            "one_row_drop_candidate_count": one_row_drop["candidate_count"],
            "one_row_drop_surviving_candidate_count": len(one_row_drop_survivors),
            "one_row_drop_non_original_row6_survivor_count": len(
                non_original_one_drop_survivors
            ),
            "one_row_drop_survivors_all_original_rows": all(
                survivor["target_center_class_is_original"]
                and survivor["dropped_center_class_is_original"]
                for survivor in one_row_drop_survivors
            ),
            "one_row_drop_rejection_category_counts": one_row_drop[
                "rejection_category_counts"
            ],
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This does not prove outside-pair support existence, does not "
                "prove the row is forced by minimal or rich-class geometry, "
                "does not allow two or more other rows to move, and does not "
                "model additional auxiliary rich supports."
            ),
        },
        "source_rows": {str(center): base_rows[center] for center in CYCLIC_ORDER},
        "candidate_generation": {
            "target_center_candidate_classes": _target_row_candidates(),
            "candidate_rule": (
                "4-sets at center 6 containing bootstrap-core witness [0] "
                "and at least one outside support pair from [3,5], [3,8], "
                "or [5,8]."
            ),
        },
        "source_outside_pair_record": target_outside_pair_record,
        "fixed_neighborhood_candidates": fixed_records,
        "one_row_drop": one_row_drop,
        "source_outside_pair_packet": {
            "path": OUTSIDE_PAIR_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": OUTSIDE_PAIR_SCHEMA,
            "status": OUTSIDE_PAIR_STATUS,
        },
        "source_overlay_packet": {
            "path": "data/certificates/bootstrap_vertex_circle_overlay.json",
            "schema": OVERLAY_SCHEMA,
            "status": OVERLAY_STATUS,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_151_6_outside_pair_audit.py",
            "command": (
                "python scripts/check_bootstrap_t12_151_6_outside_pair_audit.py "
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
        "outside_support_pairs": OUTSIDE_SUPPORT_PAIRS,
        "original_target_center_class": ORIGINAL_ROW,
        "target_center_candidate_count": 13,
        "fixed_neighborhood_candidate_count": 13,
        "fixed_neighborhood_surviving_candidate_count": 1,
        "fixed_neighborhood_non_original_survivor_count": 0,
        "fixed_neighborhood_rejection_category_counts": (
            EXPECTED_FIXED_REJECTION_COUNTS
        ),
        "one_row_drop_centers": ONE_ROW_DROP_CENTERS,
        "one_row_drop_replacement_count_per_center": 70,
        "one_row_drop_candidate_count": 7280,
        "one_row_drop_surviving_candidate_count": 8,
        "one_row_drop_non_original_row6_survivor_count": 0,
        "one_row_drop_survivors_all_original_rows": True,
        "one_row_drop_rejection_category_counts": (
            EXPECTED_ONE_ROW_DROP_REJECTION_COUNTS
        ),
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    outside_pair = payload.get("source_outside_pair_record")
    if not isinstance(outside_pair, Mapping):
        raise AssertionError("source_outside_pair_record must be a mapping")
    if outside_pair.get("support_pairs") != OUTSIDE_SUPPORT_PAIRS:
        raise AssertionError("source outside-pair support pairs drifted")

    fixed_candidates = payload.get("fixed_neighborhood_candidates")
    if not isinstance(fixed_candidates, Sequence) or len(fixed_candidates) != 13:
        raise AssertionError("expected thirteen fixed-neighborhood candidates")
    fixed_survivors = [
        record
        for record in fixed_candidates
        if isinstance(record, Mapping)
        and record.get("passes_basic_incidence_crossing_filters")
    ]
    if len(fixed_survivors) != 1:
        raise AssertionError("expected exactly one fixed-neighborhood survivor")
    if fixed_survivors[0].get("target_center_class") != ORIGINAL_ROW:
        raise AssertionError("fixed-neighborhood survivor should be the original row")

    one_row_drop = payload.get("one_row_drop")
    if not isinstance(one_row_drop, Mapping):
        raise AssertionError("one_row_drop must be a mapping")
    if one_row_drop.get("rejection_category_counts") != (
        EXPECTED_ONE_ROW_DROP_REJECTION_COUNTS
    ):
        raise AssertionError("one-row-drop rejection counts drifted")

    per_target = one_row_drop.get("per_target_center_class")
    if not isinstance(per_target, Sequence) or len(per_target) != 13:
        raise AssertionError("expected thirteen per-target-center-class summaries")
    for record in per_target:
        if not isinstance(record, Mapping):
            raise AssertionError("per-target-center-class summaries must be mappings")
        row_key = _row_key(_int_list(record["target_center_class"]))
        expected_counts = EXPECTED_ONE_ROW_DROP_PER_ROW6[row_key]
        if record.get("rejection_category_counts") != expected_counts:
            raise AssertionError(f"one-row-drop counts drifted for row {row_key}")

    per_dropped = one_row_drop.get("per_dropped_center")
    if not isinstance(per_dropped, Sequence) or len(per_dropped) != 8:
        raise AssertionError("expected eight dropped-center summaries")
    for record in per_dropped:
        if not isinstance(record, Mapping):
            raise AssertionError("dropped-center summaries must be mappings")
        center = int(record["dropped_center"])
        if record.get("replacement_row_count") != 70:
            raise AssertionError(f"dropped center {center} has bad row count")
        if record.get("candidate_count") != 910:
            raise AssertionError(f"dropped center {center} has bad candidate count")
        if record.get("rejection_category_counts") != (
            EXPECTED_ONE_ROW_DROP_PER_DROPPED[center]
        ):
            raise AssertionError(f"dropped center {center} counts drifted")

    survivors = one_row_drop.get("survivors")
    if not isinstance(survivors, Sequence) or len(survivors) != 8:
        raise AssertionError("expected eight one-row-drop survivors")
    if any(
        not isinstance(survivor, Mapping)
        or not survivor.get("target_center_class_is_original")
        or not survivor.get("dropped_center_class_is_original")
        for survivor in survivors
    ):
        raise AssertionError("one-row-drop survivors should keep original rows")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_151_6_outside_pair_audit.py"
    ):
        raise AssertionError("provenance generator drifted")
