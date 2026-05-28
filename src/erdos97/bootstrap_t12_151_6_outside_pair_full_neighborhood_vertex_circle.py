"""Full-neighborhood vertex-circle packet for bootstrap/T12 source 151 row 6.

The earlier source-151 row-6 outside-pair audit keeps the surrounding
selected-row neighborhood fixed, or allows one or two additional rows to move.
This packet widens that boundary: it fixes center 6 to each
bootstrap-core-plus-outside-pair activation row while every other center may
choose an arbitrary selected 4-set.

Basic incidence/crossing/cap filters leave complete assignments, including
assignments with non-original row 6. The packet records that all such
full-neighborhood survivors are then killed by the exact vertex-circle quotient
self-edge/strict-cycle replay. It is proof-mining bookkeeping only, not a
Euclidean realizability theorem and not a proof of row forcing.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_151_6_outside_pair_audit import (
    BOOTSTRAP_CORE_WITNESSES,
    DEFAULT_ARTIFACT as OUTSIDE_PAIR_AUDIT_ARTIFACT,
    ORIGINAL_ROW,
    OUTSIDE_SUPPORT_PAIRS,
    SCAN_STATUS as OUTSIDE_PAIR_AUDIT_SCAN_STATUS,
    SCHEMA as OUTSIDE_PAIR_AUDIT_SCHEMA,
    SOURCE_RECORD_ID,
    STATUS as OUTSIDE_PAIR_AUDIT_STATUS,
    TARGET_ROW_CENTER,
    TARGET_ROW_KEY,
    _target_row_candidates,
)
from erdos97.n9_vertex_circle_exhaustive import (
    MASK_BITS,
    MAX_INDEGREE,
    N,
    OPTIONS,
    PAIR_CAP,
    PAIRS,
    ROW_PAIR_INDICES,
    rows_compatible,
    vertex_circle_status,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.v1"
STATUS = (
    "BOOTSTRAP_T12_151_6_OUTSIDE_PAIR_FULL_NEIGHBORHOOD_VERTEX_CIRCLE_"
    "DIAGNOSTIC_ONLY"
)
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "FULL_NEIGHBORHOOD_BASIC_SURVIVORS_ALL_VERTEX_CIRCLE_OBSTRUCTED"
CLAIM_SCOPE = (
    "Full-neighborhood vertex-circle diagnostic for the source-151 row-6 "
    "outside-pair target. It fixes center 6 to each 4-set containing "
    "bootstrap-core witness [0] and at least one outside support pair from "
    "[3,5], [3,8], or [5,8], lets all other centers use arbitrary selected "
    "4-sets, and applies row-pair, witness-pair, selected-indegree, crossing, "
    "and exact vertex-circle quotient replay. Basic filters leave 28 complete "
    "assignments, including 21 with non-original row 6, but all 28 are killed "
    "by vertex-circle self-edge or strict-cycle obstructions. This is not a "
    "proof of outside-pair support existence, not a proof of row forcing, not "
    "a proof of n=9, not a proof of the bridge, and not a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.json"
)

FREE_ROW_CENTERS = [center for center in range(N) if center != TARGET_ROW_CENTER]
ROW_REPLACEMENT_COUNT_PER_CENTER = 70
IMPLICIT_ASSIGNMENT_SPACE_SIZE = len(_target_row_candidates()) * (
    ROW_REPLACEMENT_COUNT_PER_CENTER ** len(FREE_ROW_CENTERS)
)
EXPECTED_VERTEX_CIRCLE_STATUS_COUNTS = {"self_edge": 20, "strict_cycle": 8}
EXPECTED_EMPTY_DOMAIN_DEPTH_HISTOGRAM = {
    "1": 39,
    "2": 538,
    "3": 1459,
    "4": 2366,
    "5": 1580,
    "6": 883,
    "7": 232,
}
EXPECTED_PER_TARGET_ROW: dict[str, dict[str, object]] = {
    "0,1,3,5": {
        "search_node_count": 364,
        "empty_domain_count": 198,
        "basic_filter_complete_assignment_count": 0,
        "vertex_circle_status_counts": {},
        "empty_domain_depth_histogram": {
            "1": 5,
            "2": 27,
            "3": 72,
            "4": 51,
            "5": 33,
            "6": 5,
            "7": 5,
        },
    },
    "0,1,3,8": {
        "search_node_count": 315,
        "empty_domain_count": 160,
        "basic_filter_complete_assignment_count": 0,
        "vertex_circle_status_counts": {},
        "empty_domain_depth_histogram": {
            "1": 5,
            "2": 21,
            "3": 51,
            "4": 65,
            "5": 10,
            "6": 8,
        },
    },
    "0,1,5,8": {
        "search_node_count": 451,
        "empty_domain_count": 269,
        "basic_filter_complete_assignment_count": 0,
        "vertex_circle_status_counts": {},
        "empty_domain_depth_histogram": {
            "1": 2,
            "2": 60,
            "3": 72,
            "4": 108,
            "5": 17,
            "6": 9,
            "7": 1,
        },
    },
    "0,2,3,5": {
        "search_node_count": 391,
        "empty_domain_count": 206,
        "basic_filter_complete_assignment_count": 0,
        "vertex_circle_status_counts": {},
        "empty_domain_depth_histogram": {
            "1": 5,
            "2": 29,
            "3": 60,
            "4": 51,
            "5": 38,
            "6": 22,
            "7": 1,
        },
    },
    "0,2,3,8": {
        "search_node_count": 272,
        "empty_domain_count": 153,
        "basic_filter_complete_assignment_count": 0,
        "vertex_circle_status_counts": {},
        "empty_domain_depth_histogram": {
            "1": 5,
            "2": 31,
            "3": 54,
            "4": 53,
            "5": 5,
            "6": 3,
            "7": 2,
        },
    },
    "0,2,5,8": {
        "search_node_count": 786,
        "empty_domain_count": 418,
        "basic_filter_complete_assignment_count": 3,
        "vertex_circle_status_counts": {"self_edge": 2, "strict_cycle": 1},
        "empty_domain_depth_histogram": {
            "1": 1,
            "2": 44,
            "3": 94,
            "4": 150,
            "5": 87,
            "6": 40,
            "7": 2,
        },
    },
    "0,3,4,5": {
        "search_node_count": 477,
        "empty_domain_count": 231,
        "basic_filter_complete_assignment_count": 0,
        "vertex_circle_status_counts": {},
        "empty_domain_depth_histogram": {
            "1": 5,
            "2": 27,
            "3": 55,
            "4": 45,
            "5": 55,
            "6": 29,
            "7": 15,
        },
    },
    "0,3,4,8": {
        "search_node_count": 586,
        "empty_domain_count": 315,
        "basic_filter_complete_assignment_count": 0,
        "vertex_circle_status_counts": {},
        "empty_domain_depth_histogram": {
            "1": 1,
            "2": 46,
            "3": 102,
            "4": 87,
            "5": 45,
            "6": 24,
            "7": 10,
        },
    },
    "0,3,5,7": {
        "search_node_count": 5150,
        "empty_domain_count": 2729,
        "basic_filter_complete_assignment_count": 12,
        "vertex_circle_status_counts": {"self_edge": 10, "strict_cycle": 2},
        "empty_domain_depth_histogram": {
            "1": 1,
            "2": 66,
            "3": 360,
            "4": 885,
            "5": 807,
            "6": 492,
            "7": 118,
        },
    },
    "0,3,5,8": {
        "search_node_count": 894,
        "empty_domain_count": 452,
        "basic_filter_complete_assignment_count": 7,
        "vertex_circle_status_counts": {"self_edge": 3, "strict_cycle": 4},
        "empty_domain_depth_histogram": {
            "1": 1,
            "2": 44,
            "3": 93,
            "4": 146,
            "5": 91,
            "6": 57,
            "7": 20,
        },
    },
    "0,3,7,8": {
        "search_node_count": 484,
        "empty_domain_count": 228,
        "basic_filter_complete_assignment_count": 0,
        "vertex_circle_status_counts": {},
        "empty_domain_depth_histogram": {
            "1": 5,
            "2": 12,
            "3": 57,
            "4": 61,
            "5": 54,
            "6": 28,
            "7": 11,
        },
    },
    "0,4,5,8": {
        "search_node_count": 915,
        "empty_domain_count": 448,
        "basic_filter_complete_assignment_count": 3,
        "vertex_circle_status_counts": {"self_edge": 2, "strict_cycle": 1},
        "empty_domain_depth_histogram": {
            "1": 1,
            "2": 42,
            "3": 94,
            "4": 139,
            "5": 104,
            "6": 44,
            "7": 24,
        },
    },
    "0,5,7,8": {
        "search_node_count": 2354,
        "empty_domain_count": 1290,
        "basic_filter_complete_assignment_count": 3,
        "vertex_circle_status_counts": {"self_edge": 3},
        "empty_domain_depth_histogram": {
            "1": 2,
            "2": 89,
            "3": 295,
            "4": 525,
            "5": 234,
            "6": 122,
            "7": 23,
        },
    },
}


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AssertionError(f"{name} must be a mapping")
    return value


def _require_sequence(value: Any, name: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise AssertionError(f"{name} must be a sequence")
    return value


def _validate_source_outside_pair_artifact(
    source_artifact: Path = OUTSIDE_PAIR_AUDIT_ARTIFACT,
) -> None:
    payload = _load_json(source_artifact)
    if payload.get("schema") != OUTSIDE_PAIR_AUDIT_SCHEMA:
        raise AssertionError("source outside-pair artifact schema drifted")
    if payload.get("status") != OUTSIDE_PAIR_AUDIT_STATUS:
        raise AssertionError("source outside-pair artifact status drifted")

    summary = _require_mapping(payload.get("summary"), "source summary")
    if summary.get("scan_status") != OUTSIDE_PAIR_AUDIT_SCAN_STATUS:
        raise AssertionError("source outside-pair scan status drifted")
    if summary.get("source_record_ids") != [SOURCE_RECORD_ID]:
        raise AssertionError("source outside-pair record ids drifted")
    if summary.get("target_row_key") != TARGET_ROW_KEY:
        raise AssertionError("source outside-pair target key drifted")
    if summary.get("target_center") != TARGET_ROW_CENTER:
        raise AssertionError("source outside-pair center drifted")
    if summary.get("bootstrap_core_witnesses") != BOOTSTRAP_CORE_WITNESSES:
        raise AssertionError("source outside-pair bootstrap core drifted")
    if summary.get("outside_support_pairs") != OUTSIDE_SUPPORT_PAIRS:
        raise AssertionError("source outside-pair supports drifted")
    if summary.get("original_target_center_class") != ORIGINAL_ROW:
        raise AssertionError("source outside-pair original row drifted")

    generation = _require_mapping(
        payload.get("candidate_generation"), "candidate_generation"
    )
    source_candidates = [
        _int_list(row)
        for row in _require_sequence(
            generation.get("target_center_candidate_classes"),
            "target_center_candidate_classes",
        )
    ]
    if source_candidates != _target_row_candidates():
        raise AssertionError("source outside-pair candidates drifted")


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _row_key(row: Sequence[int]) -> str:
    return ",".join(str(label) for label in row)


def _row_mask(row: Iterable[int]) -> int:
    mask = 0
    for label in row:
        mask |= 1 << int(label)
    return mask


def _mask_to_row(row_mask: int) -> list[int]:
    return _int_list(MASK_BITS[row_mask])


def _update_counts(
    row_mask: int,
    column_counts: list[int],
    witness_pair_counts: list[int],
    delta: int,
) -> None:
    for witness in MASK_BITS[row_mask]:
        column_counts[witness] += delta
    for pair_index in ROW_PAIR_INDICES[row_mask]:
        witness_pair_counts[pair_index] += delta


def _compatible_with_assignment(
    center: int,
    row_mask: int,
    assigned: Mapping[int, int],
    column_counts: Sequence[int],
    witness_pair_counts: Sequence[int],
) -> bool:
    if any(column_counts[witness] >= MAX_INDEGREE for witness in MASK_BITS[row_mask]):
        return False
    if any(
        witness_pair_counts[pair_index] >= PAIR_CAP
        for pair_index in ROW_PAIR_INDICES[row_mask]
    ):
        return False
    return all(
        rows_compatible(center, row_mask, other_center, other_row)
        for other_center, other_row in assigned.items()
    )


def _search_with_fixed_target(target_row: Sequence[int]) -> dict[str, object]:
    target_mask = _row_mask(target_row)
    assigned: dict[int, int] = {TARGET_ROW_CENTER: target_mask}
    column_counts = [0] * N
    witness_pair_counts = [0] * len(PAIRS)
    _update_counts(target_mask, column_counts, witness_pair_counts, 1)

    stats: Counter[str] = Counter()
    empty_depths: Counter[int] = Counter()
    survivors: list[dict[str, object]] = []

    def search() -> None:
        stats["search_node_count"] += 1
        if len(assigned) == N:
            status = vertex_circle_status(assigned)
            stats["basic_filter_complete_assignment_count"] += 1
            stats[f"vertex_circle_status:{status}"] += 1
            survivors.append(
                {
                    "target_center_class": list(target_row),
                    "target_center_class_is_original": list(target_row) == ORIGINAL_ROW,
                    "vertex_circle_status": status,
                    "selected_rows": {
                        str(center): _mask_to_row(assigned[center])
                        for center in range(N)
                    },
                }
            )
            return

        best_center: int | None = None
        best_options: list[int] | None = None
        for center in FREE_ROW_CENTERS:
            if center in assigned:
                continue
            options = [
                row_mask
                for row_mask in OPTIONS[center]
                if _compatible_with_assignment(
                    center,
                    row_mask,
                    assigned,
                    column_counts,
                    witness_pair_counts,
                )
            ]
            if best_options is None or len(options) < len(best_options):
                best_center = center
                best_options = options
            if not options:
                stats["empty_domain_count"] += 1
                empty_depths[len(assigned) - 1] += 1
                return

        if best_center is None or best_options is None:
            raise AssertionError("search reached inconsistent assignment state")
        for row_mask in best_options:
            assigned[best_center] = row_mask
            _update_counts(row_mask, column_counts, witness_pair_counts, 1)
            search()
            _update_counts(row_mask, column_counts, witness_pair_counts, -1)
            del assigned[best_center]

    search()
    vertex_circle_counts = {
        key.removeprefix("vertex_circle_status:"): value
        for key, value in sorted(stats.items())
        if key.startswith("vertex_circle_status:")
    }
    return {
        "target_center_class": list(target_row),
        "target_center_class_is_original": list(target_row) == ORIGINAL_ROW,
        "search_node_count": stats["search_node_count"],
        "empty_domain_count": stats["empty_domain_count"],
        "empty_domain_depth_histogram": _json_counter(empty_depths),
        "basic_filter_complete_assignment_count": stats[
            "basic_filter_complete_assignment_count"
        ],
        "non_original_target_basic_assignment_count": (
            0
            if list(target_row) == ORIGINAL_ROW
            else stats["basic_filter_complete_assignment_count"]
        ),
        "vertex_circle_status_counts": vertex_circle_counts,
        "vertex_circle_surviving_assignment_count": vertex_circle_counts.get("ok", 0),
        "basic_filter_survivors": survivors,
    }


def _scan_payload() -> dict[str, object]:
    per_target = [_search_with_fixed_target(row) for row in _target_row_candidates()]
    aggregate: Counter[str] = Counter()
    empty_depths: Counter[str] = Counter()
    vertex_circle_counts: Counter[str] = Counter()
    survivors: list[dict[str, object]] = []
    for record in per_target:
        aggregate["search_node_count"] += int(record["search_node_count"])
        aggregate["empty_domain_count"] += int(record["empty_domain_count"])
        aggregate["basic_filter_complete_assignment_count"] += int(
            record["basic_filter_complete_assignment_count"]
        )
        aggregate["non_original_target_basic_assignment_count"] += int(
            record["non_original_target_basic_assignment_count"]
        )
        for depth, count in dict(record["empty_domain_depth_histogram"]).items():
            empty_depths[str(depth)] += int(count)
        for status, count in dict(record["vertex_circle_status_counts"]).items():
            vertex_circle_counts[str(status)] += int(count)
        basic_survivors = record["basic_filter_survivors"]
        if not isinstance(basic_survivors, Sequence):
            raise AssertionError("basic_filter_survivors must be a sequence")
        survivors.extend(list(basic_survivors))

    return {
        "per_target_center_class": per_target,
        "aggregate": dict(sorted(aggregate.items())),
        "empty_domain_depth_histogram": dict(sorted(empty_depths.items())),
        "vertex_circle_status_counts": dict(sorted(vertex_circle_counts.items())),
        "basic_filter_survivors": survivors,
    }


def build_t12_151_6_outside_pair_full_neighborhood_vertex_circle_payload(
) -> dict[str, object]:
    """Return the deterministic source-151 row-6 full-neighborhood packet."""

    _validate_source_outside_pair_artifact()
    scan = _scan_payload()
    aggregate = scan["aggregate"]
    if not isinstance(aggregate, Mapping):
        raise AssertionError("aggregate must be a mapping")
    vertex_circle_counts = scan["vertex_circle_status_counts"]
    if not isinstance(vertex_circle_counts, Mapping):
        raise AssertionError("vertex_circle_status_counts must be a mapping")

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            (
                "Full-neighborhood basic filters leave non-original source-151 "
                "row-6 survivors."
            ),
            (
                "All recorded full-neighborhood survivors close only after exact "
                "vertex-circle quotient replay."
            ),
            (
                "The packet does not prove outside-pair support existence or "
                "row/rich-class forcing."
            ),
            (
                "No n=9 finite-case status, bridge status, official status, "
                "or counterexample status changes."
            ),
        ],
        "summary": {
            "target_row_key": TARGET_ROW_KEY,
            "source_record_ids": [SOURCE_RECORD_ID],
            "cyclic_order": list(range(N)),
            "target_center": TARGET_ROW_CENTER,
            "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
            "outside_support_pairs": OUTSIDE_SUPPORT_PAIRS,
            "original_target_center_class": ORIGINAL_ROW,
            "target_center_candidate_count": len(_target_row_candidates()),
            "free_row_centers": FREE_ROW_CENTERS,
            "free_row_replacement_count_per_center": ROW_REPLACEMENT_COUNT_PER_CENTER,
            "implicit_assignment_space_size": IMPLICIT_ASSIGNMENT_SPACE_SIZE,
            "search_node_count": aggregate["search_node_count"],
            "empty_domain_count": aggregate["empty_domain_count"],
            "basic_filter_complete_assignment_count": aggregate[
                "basic_filter_complete_assignment_count"
            ],
            "basic_filter_non_original_row6_assignment_count": aggregate[
                "non_original_target_basic_assignment_count"
            ],
            "vertex_circle_status_counts": dict(vertex_circle_counts),
            "vertex_circle_surviving_assignment_count": int(
                vertex_circle_counts.get("ok", 0)
            ),
            "non_original_vertex_circle_surviving_assignment_count": 0,
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This does not prove outside-pair support existence, does not "
                "prove the row is forced by minimal or rich-class geometry, "
                "does not model additional auxiliary rich supports, and does "
                "not promote the review-pending n=9 checker."
            ),
        },
        "candidate_generation": {
            "target_center_candidate_classes": _target_row_candidates(),
            "candidate_rule": (
                "4-sets at center 6 containing bootstrap-core witness [0] "
                "and at least one outside support pair from [3,5], [3,8], "
                "or [5,8]."
            ),
        },
        "empty_domain_depth_histogram": scan["empty_domain_depth_histogram"],
        "per_target_center_class": scan["per_target_center_class"],
        "basic_filter_survivors": scan["basic_filter_survivors"],
        "source_outside_pair_audit": {
            "path": OUTSIDE_PAIR_AUDIT_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": OUTSIDE_PAIR_AUDIT_SCHEMA,
            "status": OUTSIDE_PAIR_AUDIT_STATUS,
            "scan_status": OUTSIDE_PAIR_AUDIT_SCAN_STATUS,
        },
        "provenance": {
            "generator": (
                "scripts/check_bootstrap_t12_151_6_outside_pair_full_neighborhood_"
                "vertex_circle.py"
            ),
            "command": (
                "python "
                "scripts/check_bootstrap_t12_151_6_outside_pair_full_neighborhood_"
                "vertex_circle.py --write --assert-expected"
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
        "cyclic_order": list(range(N)),
        "target_center": TARGET_ROW_CENTER,
        "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
        "outside_support_pairs": OUTSIDE_SUPPORT_PAIRS,
        "original_target_center_class": ORIGINAL_ROW,
        "target_center_candidate_count": 13,
        "free_row_centers": FREE_ROW_CENTERS,
        "free_row_replacement_count_per_center": ROW_REPLACEMENT_COUNT_PER_CENTER,
        "implicit_assignment_space_size": 7_494_241_300_000_000,
        "search_node_count": 13_439,
        "empty_domain_count": 7_097,
        "basic_filter_complete_assignment_count": 28,
        "basic_filter_non_original_row6_assignment_count": 21,
        "vertex_circle_status_counts": EXPECTED_VERTEX_CIRCLE_STATUS_COUNTS,
        "vertex_circle_surviving_assignment_count": 0,
        "non_original_vertex_circle_surviving_assignment_count": 0,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    if (
        payload.get("empty_domain_depth_histogram")
        != EXPECTED_EMPTY_DOMAIN_DEPTH_HISTOGRAM
    ):
        raise AssertionError("empty-domain depth histogram drifted")

    records = payload.get("per_target_center_class")
    if not isinstance(records, Sequence) or len(records) != 13:
        raise AssertionError("expected thirteen target-center class summaries")
    for record in records:
        if not isinstance(record, Mapping):
            raise AssertionError("target-center class summaries must be mappings")
        target_class = record.get("target_center_class")
        if not isinstance(target_class, Sequence):
            raise AssertionError("target_center_class must be a sequence")
        key = _row_key(_int_list(target_class))
        expected = EXPECTED_PER_TARGET_ROW.get(key)
        if expected is None:
            raise AssertionError(f"unexpected target-center class {key!r}")
        for expected_key, expected_value in expected.items():
            if record.get(expected_key) != expected_value:
                raise AssertionError(
                    f"target {key} {expected_key} is "
                    f"{record.get(expected_key)!r}, expected {expected_value!r}"
                )
        if record.get("vertex_circle_surviving_assignment_count") != 0:
            raise AssertionError(f"target {key} has vertex-circle survivors")

    survivors = payload.get("basic_filter_survivors")
    if not isinstance(survivors, Sequence) or len(survivors) != 28:
        raise AssertionError("expected 28 full-neighborhood basic-filter survivors")
    if any(
        isinstance(survivor, Mapping) and survivor.get("vertex_circle_status") == "ok"
        for survivor in survivors
    ):
        raise AssertionError("all basic-filter survivors must be vertex-circle obstructed")
    non_original_survivors = [
        survivor
        for survivor in survivors
        if isinstance(survivor, Mapping)
        and not survivor.get("target_center_class_is_original")
    ]
    if len(non_original_survivors) != 21:
        raise AssertionError("expected 21 non-original row-6 basic-filter survivors")

    source = payload.get("source_outside_pair_audit")
    if not isinstance(source, Mapping):
        raise AssertionError("source_outside_pair_audit must be a mapping")
    if source.get("schema") != OUTSIDE_PAIR_AUDIT_SCHEMA:
        raise AssertionError("source outside-pair schema drifted")
    if source.get("scan_status") != OUTSIDE_PAIR_AUDIT_SCAN_STATUS:
        raise AssertionError("source outside-pair scan status drifted")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_151_6_outside_pair_full_neighborhood_"
        "vertex_circle.py"
    ):
        raise AssertionError("provenance generator drifted")
