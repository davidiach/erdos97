"""Validate the archived secondary n=10 singleton replay artifact.

This is a cross-check helper for an existing draft artifact. It does not rerun
the archived search, does not prove n=10, and does not update the global status.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from erdos97.n10_vertex_circle_singletons import (
    N,
    ROW_SIZE,
    assert_expected_payload as assert_primary_expected_payload,
    row0_witnesses_for_index,
)

TYPE = "n10_secondary_check_v1"
TRUST = "MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING_SECONDARY"
CHECK_SCOPE = (
    "Secondary first-five n=10 singleton replay cross-check with an additional "
    "triple-intersection filter; not a proof of n=10, not all-slice coverage, "
    "and not a global status update."
)
PAIR_CAP = 2
MAX_INDEGREE = 6
TRIPLE_CAP = 1
ROW0_CHOICES_TOTAL = 126
ROW0_CHOICES_COVERED = 5
TOTAL_NODES = 114_144
TOTAL_FULL = 0
TOTAL_COUNTS = {
    "partial_self_edge": 106_827,
    "partial_strict_cycle": 120_823,
}
EXPECTED_FILTERS = [
    "L4: each unordered witness pair appears in <=2 selected rows",
    "L5: |S_i intersect S_j| <= 2 (via pair_cap)",
    "crossing: two-overlap selected chords cross the (i,j) source chord",
    "selected indegree <= floor(2*(n-1)/(row_size-1))",
    "vertex-circle: union-find quotient self-edge or strict cycle in nested chords",
    "TRIPLE: |S_i intersect S_j intersect S_k| <= 1 for distinct rows",
]
EXPECTED_ROWS = [
    {
        "row0_index": 0,
        "row0_witnesses": [1, 2, 3, 4],
        "nodes": 9_759,
        "full": 0,
        "counts": {
            "partial_self_edge": 5_256,
            "partial_strict_cycle": 6_031,
        },
    },
    {
        "row0_index": 1,
        "row0_witnesses": [1, 2, 3, 5],
        "nodes": 13_828,
        "full": 0,
        "counts": {
            "partial_self_edge": 10_487,
            "partial_strict_cycle": 11_871,
        },
    },
    {
        "row0_index": 2,
        "row0_witnesses": [1, 2, 3, 6],
        "nodes": 17_279,
        "full": 0,
        "counts": {
            "partial_self_edge": 16_314,
            "partial_strict_cycle": 19_371,
        },
    },
    {
        "row0_index": 3,
        "row0_witnesses": [1, 2, 3, 7],
        "nodes": 27_792,
        "full": 0,
        "counts": {
            "partial_self_edge": 28_912,
            "partial_strict_cycle": 31_416,
        },
    },
    {
        "row0_index": 4,
        "row0_witnesses": [1, 2, 3, 8],
        "nodes": 45_486,
        "full": 0,
        "counts": {
            "partial_self_edge": 45_858,
            "partial_strict_cycle": 52_134,
        },
    },
]


def load_artifact(path: Path) -> dict[str, Any]:
    """Load a JSON object artifact."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _is_nonnegative_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, int | float) and value >= 0


def _validate_row(
    row: Mapping[str, Any],
    expected: Mapping[str, Any],
    primary_row: Mapping[str, Any] | None,
    errors: list[str],
) -> None:
    idx = int(expected["row0_index"])
    label = f"row {idx}"
    for key in ("row0_index", "row0_witnesses", "nodes", "full", "counts"):
        _expect_equal(errors, f"{label} {key}", row.get(key), expected[key])

    _expect_equal(
        errors,
        f"{label} generic witness order",
        row.get("row0_witnesses"),
        row0_witnesses_for_index(idx),
    )
    _expect_equal(errors, f"{label} full_survivors", row.get("full_survivors"), [])

    elapsed = row.get("elapsed_seconds")
    if not _is_nonnegative_number(elapsed):
        errors.append(f"{label} elapsed_seconds must be nonnegative numeric metadata")

    if primary_row is None:
        return
    for key in ("row0_index", "row0_witnesses", "nodes", "full", "counts"):
        _expect_equal(errors, f"{label} primary-prefix {key}", row.get(key), primary_row.get(key))


def _primary_prefix_rows(
    primary_payload: Mapping[str, Any],
    errors: list[str],
) -> list[Mapping[str, Any]] | None:
    try:
        assert_primary_expected_payload(dict(primary_payload))
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"primary n=10 singleton artifact invalid: {exc}")
        return None

    _expect_equal(errors, "primary n", primary_payload.get("n"), N)
    _expect_equal(errors, "primary row_size", primary_payload.get("row_size"), ROW_SIZE)
    _expect_equal(
        errors,
        "primary row0_choice_count_expected",
        primary_payload.get("row0_choice_count_expected"),
        ROW0_CHOICES_TOTAL,
    )
    rows = primary_payload.get("rows")
    if not isinstance(rows, list) or len(rows) < ROW0_CHOICES_COVERED:
        errors.append("primary n=10 singleton artifact must contain at least five rows")
        return None
    prefix = rows[:ROW0_CHOICES_COVERED]
    if not all(isinstance(row, dict) for row in prefix):
        errors.append("primary n=10 singleton artifact prefix rows must be objects")
        return None
    return prefix


def validate_secondary_payload(
    payload: Any,
    primary_payload: Mapping[str, Any],
) -> list[str]:
    """Return validation errors for the archived secondary n=10 replay artifact."""

    if not isinstance(payload, dict):
        return ["secondary artifact top level must be a JSON object"]

    errors: list[str] = []
    expected_meta = {
        "type": TYPE,
        "trust": TRUST,
        "n": N,
        "row_size": ROW_SIZE,
        "pair_cap": PAIR_CAP,
        "max_indegree": MAX_INDEGREE,
        "triple_cap": TRIPLE_CAP,
        "filters": EXPECTED_FILTERS,
        "row0_choices_total": ROW0_CHOICES_TOTAL,
        "row0_choices_covered": ROW0_CHOICES_COVERED,
        "total_nodes": TOTAL_NODES,
        "total_full": TOTAL_FULL,
        "total_counts": TOTAL_COUNTS,
    }
    for key, expected in expected_meta.items():
        _expect_equal(errors, key, payload.get(key), expected)

    elapsed_total = payload.get("total_elapsed_seconds")
    if not _is_nonnegative_number(elapsed_total):
        errors.append("total_elapsed_seconds must be nonnegative numeric metadata")

    primary_prefix = _primary_prefix_rows(primary_payload, errors)
    rows = payload.get("rows")
    if not isinstance(rows, list):
        errors.append("rows must be a list")
        return errors
    if len(rows) != ROW0_CHOICES_COVERED:
        errors.append(f"rows must contain exactly {ROW0_CHOICES_COVERED} row0 prefix records")

    node_sum = 0
    full_sum = 0
    count_sum: Counter[str] = Counter()
    observed_indices: list[int] = []
    for position, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"row {position} must be an object")
            continue
        if isinstance(row.get("row0_index"), int):
            observed_indices.append(int(row["row0_index"]))
        if position < len(EXPECTED_ROWS):
            primary_row = primary_prefix[position] if primary_prefix is not None else None
            _validate_row(row, EXPECTED_ROWS[position], primary_row, errors)
        try:
            node_sum += int(row["nodes"])
            full_sum += int(row["full"])
            counts = row["counts"]
            if not isinstance(counts, dict):
                raise TypeError("counts must be an object")
            count_sum.update({str(key): int(value) for key, value in counts.items()})
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"row {position} cannot be totaled: {exc}")

    expected_indices = list(range(ROW0_CHOICES_COVERED))
    if observed_indices != expected_indices:
        errors.append(f"row0 indices mismatch: expected {expected_indices!r}, got {observed_indices!r}")
    _expect_equal(errors, "row node sum", node_sum, TOTAL_NODES)
    _expect_equal(errors, "row full sum", full_sum, TOTAL_FULL)
    _expect_equal(errors, "row count sum", dict(sorted(count_sum.items())), TOTAL_COUNTS)
    return errors


def primary_prefix_match(payload: Mapping[str, Any], primary_payload: Mapping[str, Any]) -> bool:
    """Return whether the secondary rows exactly match the primary first-five prefix."""

    return not validate_secondary_payload(payload, primary_payload)
