"""Exact indexing audit for the turn-inequality convention.

This module is review scaffolding for the proof-facing turn lemma. It checks
only indexing conventions for the weak turn inequalities; it does not prove
the geometric lemma, the n=9 finite case, or Erdos Problem #97.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence
from itertools import combinations
from math import comb
from typing import Any

N = 9
ROW_SIZE = 4
STATUS = "REVIEW_PENDING_TURN_INEQUALITY_INDEXING_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Indexing-convention audit for the review-pending n=9 turn-inequality "
    "frontier replay. It checks the two weak interval supports emitted for "
    "each selected offset pair; it does not prove the geometric turn lemma, "
    "does not prove n=9, is not a counterexample, and is not a global status "
    "update."
)

TermGenerator = Callable[[Sequence[Sequence[int]], int], list[dict[str, object]]]


def row_from_offsets(center: int, offsets: Sequence[int], *, n: int = N) -> list[int]:
    """Return one selected row from positive cyclic offsets."""

    return sorted((center + int(offset)) % n for offset in offsets)


def expected_turn_terms_for_offsets(
    center: int,
    offsets: Sequence[int],
    *,
    n: int = N,
) -> list[dict[str, object]]:
    """Return the two expected weak turn terms for every offset pair.

    For ``1 <= a < b <= n-1`` at center ``i``, the convention is:

    - forward support: ``{i+1, ..., i+b-1}``;
    - reverse support: ``{i+a+1, ..., i+n-1}``.

    Supports are sorted because the stored replay treats them as sums of turn
    variables, while this audit records cyclic supports separately in
    ``index_records``.
    """

    sorted_offsets = sorted(int(offset) for offset in offsets)
    terms: list[dict[str, object]] = []
    for a, b in combinations(sorted_offsets, 2):
        forward = sorted((center + h) % n for h in range(1, b))
        reverse = sorted((center + h) % n for h in range(a + 1, n))
        terms.append(
            {
                "center": center,
                "selected_offsets": [a, b],
                "support": forward,
                "bound": 1,
                "orientation": "forward",
            }
        )
        terms.append(
            {
                "center": center,
                "selected_offsets": [a, b],
                "support": reverse,
                "bound": 1,
                "orientation": "reverse",
            }
        )
    return terms


def index_records(*, n: int = N) -> list[dict[str, object]]:
    """Return the unique center/offset-pair/orientation indexing table."""

    records: list[dict[str, object]] = []
    for center in range(n):
        for a, b in combinations(range(1, n), 2):
            forward_cyclic = [(center + h) % n for h in range(1, b)]
            reverse_cyclic = [(center + h) % n for h in range(a + 1, n)]
            records.append(
                {
                    "center": center,
                    "selected_offsets": [a, b],
                    "orientation": "forward",
                    "cyclic_support": forward_cyclic,
                    "stored_support": sorted(forward_cyclic),
                    "support_size": len(forward_cyclic),
                    "includes_left_witness_turn": (center + a) % n in forward_cyclic,
                    "includes_right_witness_turn": (center + b) % n in forward_cyclic,
                }
            )
            records.append(
                {
                    "center": center,
                    "selected_offsets": [a, b],
                    "orientation": "reverse",
                    "cyclic_support": reverse_cyclic,
                    "stored_support": sorted(reverse_cyclic),
                    "support_size": len(reverse_cyclic),
                    "includes_left_witness_turn": (center + a) % n in reverse_cyclic,
                    "includes_right_witness_turn": (center + b) % n in reverse_cyclic,
                }
            )
    return records


def _normalise_term(term: dict[str, object]) -> dict[str, object]:
    return {
        "center": int(term["center"]),
        "selected_offsets": [int(value) for value in term["selected_offsets"]],  # type: ignore[index]
        "support": sorted(int(value) for value in term["support"]),  # type: ignore[index]
        "bound": int(term["bound"]),
        "orientation": str(term["orientation"]),
    }


def _default_term_generator(
    rows: Sequence[Sequence[int]],
    n: int,
) -> list[dict[str, object]]:
    from erdos97.n9_turn_inequality_frontier import (  # noqa: PLC0415
        turn_inequality_terms_for_pattern,
    )

    return turn_inequality_terms_for_pattern(rows, n=n)


def _validate_index_records(records: Sequence[dict[str, object]], *, n: int) -> list[str]:
    errors: list[str] = []
    for record_index, record in enumerate(records):
        center = int(record["center"])
        a, b = [int(value) for value in record["selected_offsets"]]  # type: ignore[index]
        orientation = str(record["orientation"])
        cyclic_support = [int(value) for value in record["cyclic_support"]]  # type: ignore[index]
        stored_support = [int(value) for value in record["stored_support"]]  # type: ignore[index]
        support_set = set(cyclic_support)
        if not cyclic_support:
            errors.append(f"record {record_index}: empty support")
        if sorted(cyclic_support) != stored_support:
            errors.append(f"record {record_index}: stored support is not sorted cyclic support")
        if center in support_set:
            errors.append(f"record {record_index}: support includes center")
        if orientation == "forward":
            if len(cyclic_support) != b - 1:
                errors.append(f"record {record_index}: wrong forward support length")
            if (center + a) % n not in support_set:
                errors.append(f"record {record_index}: forward support omits left witness turn")
            if (center + b) % n in support_set:
                errors.append(f"record {record_index}: forward support includes right endpoint")
        elif orientation == "reverse":
            if len(cyclic_support) != n - a - 1:
                errors.append(f"record {record_index}: wrong reverse support length")
            if (center + a) % n in support_set:
                errors.append(f"record {record_index}: reverse support includes left endpoint")
            if (center + b) % n not in support_set:
                errors.append(f"record {record_index}: reverse support omits right witness turn")
        else:
            errors.append(f"record {record_index}: unknown orientation {orientation!r}")
    return errors


def audit_turn_inequality_indexing(
    *,
    n: int = N,
    row_size: int = ROW_SIZE,
    term_generator: TermGenerator | None = None,
) -> dict[str, Any]:
    """Compare the independent indexing table with the frontier term emitter."""

    if n != N or row_size != ROW_SIZE:
        raise ValueError("this audit currently has expected invariants only for n=9, row_size=4")
    generator = term_generator or _default_term_generator
    records = index_records(n=n)
    validation_errors = _validate_index_records(records, n=n)
    mismatches: list[dict[str, object]] = []
    orientation_counts: Counter[str] = Counter()
    support_size_histogram: Counter[str] = Counter()
    expected_term_count = 0
    observed_term_count = 0

    for offsets in combinations(range(1, n), row_size):
        rows = [row_from_offsets(center, offsets, n=n) for center in range(n)]
        expected_terms: list[dict[str, object]] = []
        for center in range(n):
            expected_terms.extend(expected_turn_terms_for_offsets(center, offsets, n=n))
        observed_terms = [_normalise_term(term) for term in generator(rows, n)]
        expected_terms = [_normalise_term(term) for term in expected_terms]
        expected_term_count += len(expected_terms)
        observed_term_count += len(observed_terms)

        for term in observed_terms:
            orientation_counts[str(term["orientation"])] += 1
            support_size_histogram[str(len(term["support"]))] += 1

        if expected_terms != observed_terms:
            mismatches.append(
                {
                    "offsets": list(offsets),
                    "expected_term_count": len(expected_terms),
                    "observed_term_count": len(observed_terms),
                    "first_expected": expected_terms[:4],
                    "first_observed": observed_terms[:4],
                }
            )

    payload: dict[str, Any] = {
        "schema": "erdos97.turn_inequality_indexing.v1",
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n,
        "row_size": row_size,
        "center_count": n,
        "offset_count": n - 1,
        "offset_pair_count": comb(n - 1, 2),
        "row_offset_subset_count": comb(n - 1, row_size),
        "row_instance_count": n * comb(n - 1, row_size),
        "unique_center_pair_orientation_count": len(records),
        "expected_term_count": expected_term_count,
        "observed_term_count": observed_term_count,
        "orientation_counts": dict(sorted(orientation_counts.items())),
        "support_size_histogram": dict(sorted(support_size_histogram.items())),
        "mismatch_count": len(mismatches),
        "first_mismatches": mismatches[:5],
        "validation_errors": validation_errors,
        "validation_status": (
            "passed" if not mismatches and not validation_errors else "failed"
        ),
        "weak_inequality_template": [
            "sum_{h=1}^{b-1} t_{i+h} >= 1",
            "sum_{h=a+1}^{n-1} t_{i+h} >= 1",
        ],
        "index_record_count": len(records),
        "index_records": records,
    }
    return payload


def summary_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return compact JSON for reviewer-facing command output."""

    return {
        key: value
        for key, value in payload.items()
        if key not in {"index_records", "first_mismatches"}
    }


def assert_expected_payload(payload: dict[str, Any]) -> None:
    """Assert stable n=9 indexing invariants."""

    expected_values: dict[str, object] = {
        "n": 9,
        "row_size": 4,
        "center_count": 9,
        "offset_count": 8,
        "offset_pair_count": 28,
        "row_offset_subset_count": 70,
        "row_instance_count": 630,
        "unique_center_pair_orientation_count": 504,
        "expected_term_count": 7560,
        "observed_term_count": 7560,
        "orientation_counts": {"forward": 3780, "reverse": 3780},
        "support_size_histogram": {
            "1": 270,
            "2": 540,
            "3": 810,
            "4": 1080,
            "5": 1350,
            "6": 1620,
            "7": 1890,
        },
        "mismatch_count": 0,
        "validation_status": "passed",
        "index_record_count": 504,
    }
    for key, expected in expected_values.items():
        observed = payload.get(key)
        if observed != expected:
            raise AssertionError(f"{key}: expected {expected!r}, observed {observed!r}")
    if payload.get("validation_errors") != []:
        raise AssertionError(f"validation_errors: {payload.get('validation_errors')!r}")
