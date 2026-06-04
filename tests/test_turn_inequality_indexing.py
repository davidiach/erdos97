from __future__ import annotations

import pytest

from erdos97.turn_inequality_indexing import (
    assert_expected_payload,
    audit_turn_inequality_indexing,
    expected_turn_terms_for_offsets,
    row_from_offsets,
    summary_payload,
)


def test_turn_inequality_indexing_matches_expected_invariants() -> None:
    payload = audit_turn_inequality_indexing()
    assert_expected_payload(payload)
    assert payload["validation_status"] == "passed"
    assert payload["mismatch_count"] == 0


def test_turn_inequality_indexing_summary_omits_large_records() -> None:
    payload = audit_turn_inequality_indexing()
    summary = summary_payload(payload)
    assert "index_records" not in summary
    assert "first_mismatches" not in summary
    assert summary["expected_term_count"] == 7560


def test_expected_terms_pin_forward_and_reverse_supports() -> None:
    terms = expected_turn_terms_for_offsets(center=7, offsets=[1, 4, 6, 8], n=9)
    first_forward = terms[0]
    first_reverse = terms[1]
    assert first_forward == {
        "center": 7,
        "selected_offsets": [1, 4],
        "support": [0, 1, 8],
        "bound": 1,
        "orientation": "forward",
    }
    assert first_reverse == {
        "center": 7,
        "selected_offsets": [1, 4],
        "support": [0, 1, 2, 3, 4, 5, 6],
        "bound": 1,
        "orientation": "reverse",
    }


def test_row_from_offsets_wraps_modulo_n() -> None:
    assert row_from_offsets(7, [1, 4, 6, 8], n=9) == [2, 4, 6, 8]


def test_turn_inequality_indexing_rejects_term_support_drift() -> None:
    def tampered_terms(rows: list[list[int]], n: int) -> list[dict[str, object]]:
        terms = expected_turn_terms_for_offsets(0, [1, 2, 3, 4], n=n)
        for center in range(1, n):
            terms.extend(expected_turn_terms_for_offsets(center, [1, 2, 3, 4], n=n))
        terms[0] = {**terms[0], "support": [0]}
        return terms

    payload = audit_turn_inequality_indexing(term_generator=tampered_terms)
    assert payload["validation_status"] == "failed"
    assert payload["mismatch_count"] > 0
    with pytest.raises(AssertionError):
        assert_expected_payload(payload)
