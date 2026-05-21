"""Two-row-drop audit for the bootstrap/T12 source-151 singleton targets.

This replay treats ``data/certificates/bootstrap_t12_151_singleton_support_audit.json``
as input data.  For each source-151 singleton-support target row, it keeps the
target row inside the previously audited bootstrap-core-plus-singleton-support
candidate family, lets two non-target selected rows move arbitrarily, and checks
only the basic selected-row filters: row-pair cap, witness-pair cap, and the
natural-order two-overlap crossing condition.

The result is a proof-mining diagnostic, not a Euclidean realization theorem and
not a proof of row/rich-class forcing.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA = "erdos97.bootstrap_t12_151_singleton_two_row_drop.v1"
STATUS = "BOOTSTRAP_T12_151_SINGLETON_TWO_ROW_DROP_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "ONLY_ORIGINAL_SOURCE151_ROWS_SURVIVE_TWO_ROW_DROP_SUPPORT_AUDIT"
CLAIM_SCOPE = (
    "Two-row-drop singleton-support stress test for source 151 rows 5 and 8. "
    "It treats the existing source-151 singleton-support audit packet as input, "
    "keeps each target row in the bootstrap-core-plus-singleton-support "
    "candidate family, allows two non-target selected rows to move arbitrarily, "
    "and checks only row-pair, witness-pair, and two-overlap crossing filters. "
    "The only survivors keep the original target row and both dropped rows "
    "equal to their source-151 rows. This does not prove singleton support "
    "existence, row forcing, n=9, the bootstrap bridge, Erdos Problem #97, or "
    "any counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_singleton_support_audit.json"
)
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_singleton_two_row_drop.json"
)
SOURCE_SCHEMA = "erdos97.bootstrap_t12_151_singleton_support_audit.v1"
SOURCE_STATUS = "BOOTSTRAP_T12_151_SINGLETON_SUPPORT_AUDIT_DIAGNOSTIC_ONLY"

EXPECTED_BY_KEY: dict[str, dict[str, object]] = {
    "151:5": {
        "target_center": 5,
        "candidate_count": 1_234_800,
        "surviving_candidate_count": 28,
        "non_original_survivor_count": 0,
        "rejection_category_counts": {
            "crossing": 1_871,
            "row_pair+crossing": 1_063,
            "row_pair+witness_pair": 1_277,
            "row_pair+witness_pair+crossing": 1_214_683,
            "survive": 28,
            "witness_pair+crossing": 15_878,
        },
    },
    "151:8": {
        "target_center": 8,
        "candidate_count": 1_234_800,
        "surviving_candidate_count": 28,
        "non_original_survivor_count": 0,
        "rejection_category_counts": {
            "crossing": 3_059,
            "row_pair+crossing": 1_146,
            "row_pair+witness_pair": 1_135,
            "row_pair+witness_pair+crossing": 1_215_556,
            "survive": 28,
            "witness_pair+crossing": 13_876,
        },
    },
}


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


def _extract_target_candidates(record: Mapping[str, Any]) -> list[int]:
    raw = record.get("target_center_candidate_classes")
    if raw is None:
        # Defensive fallback for older input packets: the fixed-neighborhood
        # candidate table contains exactly the same target-row family.
        fixed = _require_sequence(
            record.get("fixed_neighborhood_candidates"),
            "fixed_neighborhood_candidates",
        )
        raw = [
            _require_mapping(candidate, "fixed_neighborhood_candidate")[
                "target_center_class"
            ]
            for candidate in fixed
        ]
    return sorted({_mask(_int_list(row)) for row in _require_sequence(raw, "candidates")})


def _support_packet_input(
    source_artifact: Path = DEFAULT_SOURCE_ARTIFACT,
) -> tuple[list[int], list[list[int]], list[dict[str, object]], dict[str, object]]:
    payload = _load_json(source_artifact)
    if payload.get("schema") != SOURCE_SCHEMA:
        raise AssertionError("source singleton-support artifact schema drifted")
    if payload.get("status") != SOURCE_STATUS:
        raise AssertionError("source singleton-support artifact status drifted")

    summary = _require_mapping(payload.get("summary"), "source summary")
    cyclic_order = _int_list(_require_sequence(summary.get("cyclic_order"), "cyclic_order"))
    if cyclic_order != list(range(len(cyclic_order))):
        raise AssertionError(
            "two-row-drop replay currently expects the natural source-151 order"
        )

    source_rows_raw = _require_mapping(payload.get("source_rows"), "source_rows")
    source_rows = [_int_list(source_rows_raw[str(center)]) for center in cyclic_order]

    records_raw = _require_sequence(payload.get("target_audits"), "target_audits")
    targets: list[dict[str, object]] = []
    for raw_record in records_raw:
        record = _require_mapping(raw_record, "target_audit")
        key = str(record["target_row_key"])
        if key not in EXPECTED_BY_KEY:
            continue
        targets.append(
            {
                "target_row_key": key,
                "target_center": int(record["target_center"]),
                "bootstrap_core_witnesses": _int_list(record["bootstrap_core_witnesses"]),
                "singleton_support_labels": _int_list(record["singleton_support_labels"]),
                "original_target_center_class": _int_list(
                    record["original_target_center_class"]
                ),
                "target_center_candidate_classes": [
                    _row_from_mask(mask, len(cyclic_order))
                    for mask in _extract_target_candidates(record)
                ],
            }
        )
    if sorted(str(target["target_row_key"]) for target in targets) != sorted(EXPECTED_BY_KEY):
        raise AssertionError("source singleton-support target rows drifted")

    source_packet = {
        "path": source_artifact.relative_to(REPO_ROOT).as_posix()
        if source_artifact.is_relative_to(REPO_ROOT)
        else str(source_artifact),
        "schema": SOURCE_SCHEMA,
        "status": SOURCE_STATUS,
    }
    return (
        cyclic_order,
        source_rows,
        sorted(targets, key=lambda target: str(target["target_row_key"])),
        source_packet,
    )


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
            center: _all_replacement_masks(center, cyclic_order) for center in cyclic_order
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
    target_key = str(target["target_row_key"])
    target_candidate_rows = _require_sequence(
        target["target_center_candidate_classes"],
        "target_center_candidate_classes",
    )
    target_masks = [_mask(_int_list(row)) for row in target_candidate_rows]
    original_target_mask = _mask(target["original_target_center_class"])  # type: ignore[arg-type]
    dropped_centers = [label for label in cyclic_order if label != center]

    total_counts: Counter[str] = Counter()
    per_pair_counts: dict[tuple[int, int], Counter[str]] = {
        pair: Counter() for pair in combinations(dropped_centers, 2)
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
        "target_row_key": target_key,
        "target_center": center,
        "bootstrap_core_witnesses": list(target["bootstrap_core_witnesses"]),
        "singleton_support_labels": list(target["singleton_support_labels"]),
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


def build_t12_151_singleton_two_row_drop_payload(
    source_artifact: Path = DEFAULT_SOURCE_ARTIFACT,
) -> dict[str, object]:
    """Return the deterministic two-row-drop singleton-support audit payload."""

    cyclic_order, source_rows, targets, source_packet = _support_packet_input(
        source_artifact
    )
    context = _build_context(cyclic_order, source_rows)
    target_audits = [
        _scan_target(cyclic_order, source_rows, target, context) for target in targets
    ]
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
            "source_record_ids": [151],
            "cyclic_order": cyclic_order,
            "target_row_keys": [str(record["target_row_key"]) for record in target_audits],
            "target_centers": [int(record["target_center"]) for record in target_audits],
            "target_count": len(target_audits),
            "target_center_candidate_count_by_key": {
                str(record["target_row_key"]): int(
                    record["target_center_candidate_count"]
                )
                for record in target_audits
            },
            "two_row_drop_candidate_count": sum(
                int(record["two_row_drop_candidate_count"])
                for record in target_audits
            ),
            "two_row_drop_surviving_candidate_count": sum(
                int(record["two_row_drop_surviving_candidate_count"])
                for record in target_audits
            ),
            "two_row_drop_non_original_survivor_count": sum(
                int(record["two_row_drop_non_original_survivor_count"])
                for record in target_audits
            ),
            "two_row_drop_survivors_all_original_rows": all(
                bool(record["two_row_drop_survivors_all_original_rows"])
                for record in target_audits
            ),
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This does not prove singleton support existence, does not "
                "prove the rows are forced by minimal or rich-class geometry, "
                "does not allow three or more other rows to move, and does not "
                "model additional auxiliary rich supports."
            ),
        },
        "source_rows": {str(center): source_rows[center] for center in cyclic_order},
        "target_audits": target_audits,
        "source_singleton_support_packet": source_packet,
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_151_singleton_two_row_drop.py",
            "command": (
                "python scripts/check_bootstrap_t12_151_singleton_two_row_drop.py "
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
        "source_record_ids": [151],
        "cyclic_order": list(range(9)),
        "target_row_keys": ["151:5", "151:8"],
        "target_centers": [5, 8],
        "target_count": 2,
        "target_center_candidate_count_by_key": {"151:5": 9, "151:8": 9},
        "two_row_drop_candidate_count": 2_469_600,
        "two_row_drop_surviving_candidate_count": 56,
        "two_row_drop_non_original_survivor_count": 0,
        "two_row_drop_survivors_all_original_rows": True,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    records = _require_sequence(payload.get("target_audits"), "target_audits")
    if len(records) != 2:
        raise AssertionError("expected two source-151 singleton two-row audits")
    by_key = {
        str(_require_mapping(record, "target_audit")["target_row_key"]): _require_mapping(
            record, "target_audit"
        )
        for record in records
    }
    if sorted(by_key) != sorted(EXPECTED_BY_KEY):
        raise AssertionError("unexpected source-151 singleton two-row audit keys")

    for key, expected in EXPECTED_BY_KEY.items():
        record = by_key[key]
        if record.get("target_center") != expected["target_center"]:
            raise AssertionError(f"{key} target center drifted")
        if record.get("target_center_candidate_count") != 9:
            raise AssertionError(f"{key} target candidate count drifted")
        if record.get("two_row_drop_dropped_center_pair_count") != 28:
            raise AssertionError(f"{key} dropped-center-pair count drifted")
        if record.get("two_row_drop_replacement_count_per_center") != 70:
            raise AssertionError(f"{key} replacement count drifted")
        if record.get("two_row_drop_candidate_count") != expected["candidate_count"]:
            raise AssertionError(f"{key} candidate count drifted")
        if (
            record.get("two_row_drop_surviving_candidate_count")
            != expected["surviving_candidate_count"]
        ):
            raise AssertionError(f"{key} survivor count drifted")
        if (
            record.get("two_row_drop_non_original_survivor_count")
            != expected["non_original_survivor_count"]
        ):
            raise AssertionError(f"{key} non-original survivor count drifted")
        if record.get("two_row_drop_survivors_all_original_rows") is not True:
            raise AssertionError(f"{key} survivor originality drifted")
        if (
            record.get("two_row_drop_rejection_category_counts")
            != expected["rejection_category_counts"]
        ):
            raise AssertionError(f"{key} rejection category counts drifted")

        per_pair = _require_sequence(
            record.get("two_row_drop_per_dropped_center_pair"),
            "two_row_drop_per_dropped_center_pair",
        )
        if len(per_pair) != 28:
            raise AssertionError(f"{key} per-pair table length drifted")
        for item in per_pair:
            row = _require_mapping(item, "per_pair_row")
            if row.get("candidate_count") != 44_100:
                raise AssertionError(f"{key} per-pair candidate count drifted")
            if row.get("surviving_candidate_count") != 1:
                raise AssertionError(f"{key} per-pair survivor count drifted")

        survivors = _require_sequence(
            record.get("two_row_drop_survivors"), "two_row_drop_survivors"
        )
        if len(survivors) != 28:
            raise AssertionError(f"{key} survivor list length drifted")
        for survivor in survivors:
            survivor_map = _require_mapping(survivor, "survivor")
            if survivor_map.get("target_center_class_is_original") is not True:
                raise AssertionError(f"{key} target survivor should be original")
            if survivor_map.get("dropped_center_classes_are_original") != [True, True]:
                raise AssertionError(f"{key} dropped-row survivors should be original")

    source_packet = _require_mapping(
        payload.get("source_singleton_support_packet"), "source_singleton_support_packet"
    )
    if source_packet.get("schema") != SOURCE_SCHEMA:
        raise AssertionError("source singleton packet schema drifted")
    if source_packet.get("status") != SOURCE_STATUS:
        raise AssertionError("source singleton packet status drifted")
