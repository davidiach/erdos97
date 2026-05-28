"""Two-row-drop audit for the bootstrap/T12 source-151 row-6 target.

This replay treats
``data/certificates/bootstrap_t12_151_6_outside_pair_audit.json`` as input
data.  It keeps source-151 row 6 inside the previously audited
bootstrap-core-plus-outside-pair candidate family, lets two non-target selected
rows move arbitrarily, and checks only the basic selected-row filters:
row-pair cap, witness-pair cap, and the natural-order two-overlap crossing
condition.

The result is a proof-mining diagnostic, not a Euclidean realization theorem
and not a proof of row/rich-class forcing.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA = "erdos97.bootstrap_t12_151_6_outside_pair_two_row_drop.v1"
STATUS = "BOOTSTRAP_T12_151_6_OUTSIDE_PAIR_TWO_ROW_DROP_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "ONLY_ORIGINAL_ROW6_SURVIVES_TWO_ROW_DROP_OUTSIDE_PAIR_AUDIT"
CLAIM_SCOPE = (
    "Two-row-drop outside-pair stress test for source 151 row 6. It treats the "
    "existing source-151 row-6 outside-pair audit packet as input, keeps row 6 "
    "in the bootstrap-core-plus-outside-pair candidate family, allows two "
    "non-target selected rows to move arbitrarily, and checks only row-pair, "
    "witness-pair, and two-overlap crossing filters. The only survivors keep "
    "the original row 6 and both dropped rows equal to their source-151 rows. "
    "This does not prove outside-pair support existence, row forcing, n=9, "
    "the bootstrap bridge, Erdos Problem #97, or any counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_outside_pair_audit.json"
)
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_outside_pair_two_row_drop.json"
)
SOURCE_SCHEMA = "erdos97.bootstrap_t12_151_6_outside_pair_audit.v1"
SOURCE_STATUS = "BOOTSTRAP_T12_151_6_OUTSIDE_PAIR_AUDIT_DIAGNOSTIC_ONLY"
SOURCE_SCAN_STATUS = "ONLY_ORIGINAL_ROW6_SURVIVES_FIXED_AND_ONE_ROW_DROP_SUPPORT_AUDITS"

EXPECTED_REJECTION_COUNTS = {
    "crossing": 3_670,
    "row_pair+crossing": 1_591,
    "row_pair+witness_pair": 1_356,
    "row_pair+witness_pair+crossing": 1_756_671,
    "survive": 28,
    "witness_pair+crossing": 20_284,
}
EXPECTED_PER_PAIR_SURVIVORS = 1


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _json_counter(counter: Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


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


def _mask(row: Iterable[int]) -> int:
    out = 0
    for label in row:
        out |= 1 << int(label)
    return out


def _row_from_mask(mask: int, n: int) -> list[int]:
    return [label for label in range(n) if (mask >> label) & 1]


def _all_replacement_masks(center: int, cyclic_order: Sequence[int]) -> list[int]:
    labels = [label for label in cyclic_order if label != center]
    return [_mask(row) for row in combinations(labels, 4)]


def _source_packet_input(
    source_artifact: Path = DEFAULT_SOURCE_ARTIFACT,
) -> tuple[
    list[int],
    list[list[int]],
    dict[str, object],
    list[int],
    dict[str, object],
]:
    payload = _load_json(source_artifact)
    if payload.get("schema") != SOURCE_SCHEMA:
        raise AssertionError("source outside-pair audit schema drifted")
    if payload.get("status") != SOURCE_STATUS:
        raise AssertionError("source outside-pair audit status drifted")

    summary = _require_mapping(payload.get("summary"), "source summary")
    if summary.get("scan_status") != SOURCE_SCAN_STATUS:
        raise AssertionError("source outside-pair audit scan status drifted")
    cyclic_order = _int_list(_require_sequence(summary.get("cyclic_order"), "cyclic_order"))
    if cyclic_order != list(range(len(cyclic_order))):
        raise AssertionError(
            "two-row-drop replay currently expects the natural source-151 order"
        )
    target_center = int(summary.get("target_center"))
    if target_center != 6:
        raise AssertionError("source outside-pair target center drifted")
    original_target_row = _int_list(
        _require_sequence(
            summary.get("original_target_center_class"),
            "original_target_center_class",
        )
    )

    source_rows_raw = _require_mapping(payload.get("source_rows"), "source_rows")
    source_rows = [_int_list(source_rows_raw[str(center)]) for center in cyclic_order]
    if source_rows[target_center] != original_target_row:
        raise AssertionError("source-151 row 6 drifted")

    candidate_generation = _require_mapping(
        payload.get("candidate_generation"), "candidate_generation"
    )
    target_candidates = [
        _int_list(row)
        for row in _require_sequence(
            candidate_generation.get("target_center_candidate_classes"),
            "target_center_candidate_classes",
        )
    ]
    if len(target_candidates) != 13:
        raise AssertionError("target row-6 candidate family drifted")

    target = {
        "target_row_key": str(summary["target_row_key"]),
        "source_record_ids": _int_list(summary["source_record_ids"]),
        "target_center": target_center,
        "bootstrap_core_witnesses": _int_list(summary["bootstrap_core_witnesses"]),
        "outside_support_pairs": [
            _int_list(pair)
            for pair in _require_sequence(
                summary.get("outside_support_pairs"), "outside_support_pairs"
            )
        ],
        "original_target_center_class": original_target_row,
        "target_center_candidate_classes": target_candidates,
    }
    source_packet = {
        "path": source_artifact.relative_to(REPO_ROOT).as_posix()
        if source_artifact.is_relative_to(REPO_ROOT)
        else str(source_artifact),
        "schema": SOURCE_SCHEMA,
        "status": SOURCE_STATUS,
        "scan_status": SOURCE_SCAN_STATUS,
    }
    return cyclic_order, source_rows, target, original_target_row, source_packet


def _pair_index_data(n: int) -> tuple[dict[tuple[int, int], int], list[tuple[int, int]]]:
    pair_to_index: dict[tuple[int, int], int] = {}
    index_to_pair: list[tuple[int, int]] = []
    for index, pair in enumerate(combinations(range(n), 2)):
        pair_to_index[pair] = index
        index_to_pair.append(pair)
    return pair_to_index, index_to_pair


def _pair_indices_for_mask(
    mask: int,
    n: int,
    pair_to_index: Mapping[tuple[int, int], int],
) -> tuple[int, ...]:
    labels = _row_from_mask(mask, n)
    return tuple(pair_to_index[(a, b)] for a, b in combinations(labels, 2))


def _crosses_in_natural_order(
    source: tuple[int, int], target_mask: int, n: int
) -> bool:
    labels = _row_from_mask(target_mask, n)
    if len(labels) != 2:
        raise ValueError("target_mask must contain exactly two labels")
    a, b = sorted(source)
    c, d = sorted(labels)
    if {a, b} & {c, d}:
        return False
    return (a < c < b) != (a < d < b)


def _affected_center_pairs(
    cyclic_order: Sequence[int], changed_centers: Sequence[int]
) -> tuple[tuple[int, int], ...]:
    changed = set(changed_centers)
    return tuple(
        (i, j)
        for i, j in combinations(cyclic_order, 2)
        if i in changed or j in changed
    )


def _scan_category(
    rows: Sequence[int],
    base_rows: Sequence[int],
    base_pair_counts: Sequence[int],
    row_pair_indices: Mapping[int, tuple[int, ...]],
    affected_pairs: Sequence[tuple[int, int]],
    changed_centers: Sequence[int],
    n: int,
) -> str:
    row_pair = any((rows[i] & rows[j]).bit_count() > 2 for i, j in affected_pairs)

    deltas: dict[int, int] = {}
    for center in changed_centers:
        for pair_index in row_pair_indices[base_rows[center]]:
            deltas[pair_index] = deltas.get(pair_index, 0) - 1
        for pair_index in row_pair_indices[rows[center]]:
            deltas[pair_index] = deltas.get(pair_index, 0) + 1
    witness_pair = any(
        base_pair_counts[pair_index] + delta > 2
        for pair_index, delta in deltas.items()
    )

    crossing = False
    for i, j in affected_pairs:
        intersection = rows[i] & rows[j]
        if intersection.bit_count() == 2 and not _crosses_in_natural_order(
            (i, j), intersection, n
        ):
            crossing = True
            break

    reasons: list[str] = []
    if row_pair:
        reasons.append("row_pair")
    if witness_pair:
        reasons.append("witness_pair")
    if crossing:
        reasons.append("crossing")
    return "+".join(reasons) if reasons else "survive"


def _build_context(
    cyclic_order: Sequence[int],
    source_rows: Sequence[Sequence[int]],
) -> dict[str, object]:
    n = len(cyclic_order)
    base_masks = [_mask(row) for row in source_rows]
    all_four_masks = [_mask(row) for row in combinations(cyclic_order, 4)]
    pair_to_index, index_to_pair = _pair_index_data(n)
    row_pair_indices = {
        mask: _pair_indices_for_mask(mask, n, pair_to_index) for mask in all_four_masks
    }
    base_pair_counts = [0] * len(index_to_pair)
    for base_mask in base_masks:
        for pair_index in row_pair_indices[base_mask]:
            base_pair_counts[pair_index] += 1
    return {
        "n": n,
        "base_masks": base_masks,
        "base_pair_counts": base_pair_counts,
        "row_pair_indices": row_pair_indices,
        "all_replacement_masks": {
            center: _all_replacement_masks(center, cyclic_order)
            for center in cyclic_order
        },
    }


def _scan_target(
    cyclic_order: Sequence[int],
    source_rows: Sequence[Sequence[int]],
    target: Mapping[str, object],
    context: Mapping[str, object],
) -> dict[str, object]:
    n = int(context["n"])
    base_masks = list(_require_sequence(context["base_masks"], "base_masks"))
    base_pair_counts = list(
        _require_sequence(context["base_pair_counts"], "base_pair_counts")
    )
    row_pair_indices = _require_mapping(
        context["row_pair_indices"], "row_pair_indices"
    )
    all_replacements = _require_mapping(
        context["all_replacement_masks"], "all_replacement_masks"
    )

    center = int(target["target_center"])
    target_masks = [
        _mask(_int_list(row))
        for row in _require_sequence(
            target["target_center_candidate_classes"],
            "target_center_candidate_classes",
        )
    ]
    original_target_mask = _mask(target["original_target_center_class"])  # type: ignore[arg-type]
    dropped_centers = [label for label in cyclic_order if label != center]

    total_counts: Counter[str] = Counter()
    per_pair_counts: dict[tuple[int, int], Counter[str]] = {
        pair: Counter() for pair in combinations(dropped_centers, 2)
    }
    per_target_counts: dict[int, Counter[str]] = {
        target_mask: Counter() for target_mask in target_masks
    }
    survivors: list[dict[str, object]] = []
    non_original_survivors: list[dict[str, object]] = []

    for target_mask in target_masks:
        target_is_original = target_mask == original_target_mask
        for dropped_left, dropped_right in combinations(dropped_centers, 2):
            changed_centers = (center, dropped_left, dropped_right)
            affected_pairs = _affected_center_pairs(cyclic_order, changed_centers)
            left_rows = list(all_replacements[dropped_left])
            right_rows = list(all_replacements[dropped_right])
            for left_mask in left_rows:
                left_is_original = left_mask == base_masks[dropped_left]
                for right_mask in right_rows:
                    right_is_original = right_mask == base_masks[dropped_right]
                    rows = list(base_masks)
                    rows[center] = target_mask
                    rows[dropped_left] = left_mask
                    rows[dropped_right] = right_mask
                    category = _scan_category(
                        rows=rows,
                        base_rows=base_masks,
                        base_pair_counts=base_pair_counts,
                        row_pair_indices=row_pair_indices,
                        affected_pairs=affected_pairs,
                        changed_centers=changed_centers,
                        n=n,
                    )
                    total_counts[category] += 1
                    per_pair_counts[(dropped_left, dropped_right)][category] += 1
                    per_target_counts[target_mask][category] += 1
                    if category == "survive":
                        survivor = {
                            "target_center_class": _row_from_mask(target_mask, n),
                            "target_center_class_is_original": bool(target_is_original),
                            "dropped_centers": [int(dropped_left), int(dropped_right)],
                            "dropped_center_classes": [
                                _row_from_mask(left_mask, n),
                                _row_from_mask(right_mask, n),
                            ],
                            "dropped_center_classes_are_original": [
                                bool(left_is_original),
                                bool(right_is_original),
                            ],
                        }
                        survivors.append(survivor)
                        if not (
                            target_is_original
                            and left_is_original
                            and right_is_original
                        ):
                            non_original_survivors.append(survivor)

    return {
        "target_row_key": str(target["target_row_key"]),
        "source_record_ids": list(target["source_record_ids"]),
        "target_center": center,
        "bootstrap_core_witnesses": list(target["bootstrap_core_witnesses"]),
        "outside_support_pairs": list(target["outside_support_pairs"]),
        "original_target_center_class": list(target["original_target_center_class"]),
        "target_center_candidate_classes": [
            _row_from_mask(target_mask, n) for target_mask in target_masks
        ],
        "target_center_candidate_count": len(target_masks),
        "two_row_drop_centers": dropped_centers,
        "two_row_drop_dropped_center_pair_count": len(per_pair_counts),
        "two_row_drop_replacement_count_per_center": len(
            list(all_replacements[dropped_centers[0]])
        ),
        "two_row_drop_candidate_count": sum(total_counts.values()),
        "two_row_drop_surviving_candidate_count": len(survivors),
        "two_row_drop_non_original_survivor_count": len(non_original_survivors),
        "two_row_drop_survivors_all_original_rows": all(
            bool(survivor["target_center_class_is_original"])
            and all(survivor["dropped_center_classes_are_original"])
            for survivor in survivors
        ),
        "two_row_drop_rejection_category_counts": _json_counter(total_counts),
        "two_row_drop_per_target_center_class": [
            {
                "target_center_class": _row_from_mask(target_mask, n),
                "target_center_class_is_original": target_mask == original_target_mask,
                "candidate_count": sum(per_target_counts[target_mask].values()),
                "surviving_candidate_count": per_target_counts[target_mask].get(
                    "survive", 0
                ),
                "rejection_category_counts": _json_counter(
                    per_target_counts[target_mask]
                ),
            }
            for target_mask in target_masks
        ],
        "two_row_drop_per_dropped_center_pair": [
            {
                "dropped_centers": [int(dropped_left), int(dropped_right)],
                "source_rows": [
                    list(source_rows[dropped_left]),
                    list(source_rows[dropped_right]),
                ],
                "candidate_count": sum(
                    per_pair_counts[(dropped_left, dropped_right)].values()
                ),
                "surviving_candidate_count": per_pair_counts[
                    (dropped_left, dropped_right)
                ].get("survive", 0),
                "rejection_category_counts": _json_counter(
                    per_pair_counts[(dropped_left, dropped_right)]
                ),
            }
            for dropped_left, dropped_right in sorted(per_pair_counts)
        ],
        "two_row_drop_survivors": survivors,
    }


def build_t12_151_6_outside_pair_two_row_drop_payload(
    source_artifact: Path = DEFAULT_SOURCE_ARTIFACT,
) -> dict[str, object]:
    """Return the deterministic two-row-drop outside-pair audit payload."""

    cyclic_order, source_rows, target, _original_target_row, source_packet = (
        _source_packet_input(source_artifact)
    )
    context = _build_context(cyclic_order, source_rows)
    target_audit = _scan_target(cyclic_order, source_rows, target, context)
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            (
                "This is a finite proof-mining diagnostic around the fixed "
                "source-151 selected-row neighborhood."
            ),
            (
                "The scan allows exactly two non-target selected rows to move; "
                "it does not model three or more moving rows."
            ),
            (
                "Activation rows are bookkeeping objects; the scan does not "
                "prove a genuine rich class exists."
            ),
            "The scan uses only incidence and crossing filters, not Euclidean realizability.",
            (
                "No n=9 finite-case status, bridge status, official status, "
                "or counterexample status changes."
            ),
        ],
        "summary": {
            "target_row_key": str(target_audit["target_row_key"]),
            "source_record_ids": list(target_audit["source_record_ids"]),
            "cyclic_order": cyclic_order,
            "target_center": int(target_audit["target_center"]),
            "bootstrap_core_witnesses": list(
                target_audit["bootstrap_core_witnesses"]
            ),
            "outside_support_pairs": list(target_audit["outside_support_pairs"]),
            "original_target_center_class": list(
                target_audit["original_target_center_class"]
            ),
            "target_center_candidate_count": int(
                target_audit["target_center_candidate_count"]
            ),
            "two_row_drop_centers": list(target_audit["two_row_drop_centers"]),
            "two_row_drop_dropped_center_pair_count": int(
                target_audit["two_row_drop_dropped_center_pair_count"]
            ),
            "two_row_drop_replacement_count_per_center": int(
                target_audit["two_row_drop_replacement_count_per_center"]
            ),
            "two_row_drop_candidate_count": int(
                target_audit["two_row_drop_candidate_count"]
            ),
            "two_row_drop_surviving_candidate_count": int(
                target_audit["two_row_drop_surviving_candidate_count"]
            ),
            "two_row_drop_non_original_survivor_count": int(
                target_audit["two_row_drop_non_original_survivor_count"]
            ),
            "two_row_drop_survivors_all_original_rows": bool(
                target_audit["two_row_drop_survivors_all_original_rows"]
            ),
            "two_row_drop_rejection_category_counts": target_audit[
                "two_row_drop_rejection_category_counts"
            ],
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This does not prove outside-pair support existence, does not "
                "prove the row is forced by minimal or rich-class geometry, "
                "does not allow three or more other rows to move, and does not "
                "model additional auxiliary rich supports."
            ),
        },
        "source_rows": {str(center): source_rows[center] for center in cyclic_order},
        "target_audit": target_audit,
        "source_outside_pair_audit_packet": source_packet,
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_151_6_outside_pair_two_row_drop.py",
            "command": (
                "python scripts/check_bootstrap_t12_151_6_outside_pair_two_row_drop.py "
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

    summary = _require_mapping(payload.get("summary"), "summary")
    expected_summary = {
        "target_row_key": "151:6",
        "source_record_ids": [151],
        "cyclic_order": list(range(9)),
        "target_center": 6,
        "bootstrap_core_witnesses": [0],
        "outside_support_pairs": [[3, 5], [3, 8], [5, 8]],
        "original_target_center_class": [0, 3, 5, 8],
        "target_center_candidate_count": 13,
        "two_row_drop_centers": [0, 1, 2, 3, 4, 5, 7, 8],
        "two_row_drop_dropped_center_pair_count": 28,
        "two_row_drop_replacement_count_per_center": 70,
        "two_row_drop_candidate_count": 1_783_600,
        "two_row_drop_surviving_candidate_count": 28,
        "two_row_drop_non_original_survivor_count": 0,
        "two_row_drop_survivors_all_original_rows": True,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    if EXPECTED_REJECTION_COUNTS and summary.get(
        "two_row_drop_rejection_category_counts"
    ) != EXPECTED_REJECTION_COUNTS:
        raise AssertionError("two-row-drop rejection counts drifted")

    target_audit = _require_mapping(payload.get("target_audit"), "target_audit")
    if target_audit.get("two_row_drop_candidate_count") != 1_783_600:
        raise AssertionError("target audit candidate count drifted")
    if target_audit.get("two_row_drop_surviving_candidate_count") != 28:
        raise AssertionError("target audit survivor count drifted")
    if target_audit.get("two_row_drop_non_original_survivor_count") != 0:
        raise AssertionError("target audit non-original survivor count drifted")
    if target_audit.get("two_row_drop_survivors_all_original_rows") is not True:
        raise AssertionError("target audit survivor originality drifted")

    per_pair = _require_sequence(
        target_audit.get("two_row_drop_per_dropped_center_pair"),
        "two_row_drop_per_dropped_center_pair",
    )
    if len(per_pair) != 28:
        raise AssertionError("per-pair table length drifted")
    for item in per_pair:
        row = _require_mapping(item, "per_pair_row")
        if row.get("candidate_count") != 63_700:
            raise AssertionError("per-pair candidate count drifted")
        if row.get("surviving_candidate_count") != EXPECTED_PER_PAIR_SURVIVORS:
            raise AssertionError("per-pair survivor count drifted")

    survivors = _require_sequence(
        target_audit.get("two_row_drop_survivors"), "two_row_drop_survivors"
    )
    if len(survivors) != 28:
        raise AssertionError("survivor list length drifted")
    for survivor in survivors:
        survivor_map = _require_mapping(survivor, "survivor")
        if survivor_map.get("target_center_class_is_original") is not True:
            raise AssertionError("target survivor should be original")
        if survivor_map.get("dropped_center_classes_are_original") != [True, True]:
            raise AssertionError("dropped-row survivors should be original")

    source_packet = _require_mapping(
        payload.get("source_outside_pair_audit_packet"),
        "source_outside_pair_audit_packet",
    )
    if source_packet.get("schema") != SOURCE_SCHEMA:
        raise AssertionError("source outside-pair audit schema drifted")
    if source_packet.get("status") != SOURCE_STATUS:
        raise AssertionError("source outside-pair audit status drifted")
