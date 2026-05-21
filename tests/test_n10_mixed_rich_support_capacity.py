from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_n10_mixed_rich_support_capacity import (  # noqa: E402
    SIZE_FIVE_WITNESS,
    assignment_is_valid,
    assert_expected_payload,
    build_payload,
    dihedral_representatives,
    pair_budget_max_size_five_centers,
    support_size_counts,
)


def test_pair_budget_and_dihedral_representative_counts() -> None:
    assert pair_budget_max_size_five_centers() == 7
    assert {
        q: len(dihedral_representatives(q))
        for q in range(3, 8)
    } == {
        3: 8,
        4: 16,
        5: 16,
        6: 16,
        7: 8,
    }


def test_q2_witness_shape_and_filters_are_pinned() -> None:
    witness = {
        int(center): tuple(row)
        for center, row in SIZE_FIVE_WITNESS.items()
    }

    assert support_size_counts(witness) == {"4": 8, "5": 2}
    assert assignment_is_valid(witness)


def test_expected_payload_counts() -> None:
    payload = build_payload()
    assert_expected_payload(payload)

    summary = payload["summary"]
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert summary["q_summaries"]["3"]["total_nodes_visited"] == 133778
    assert summary["q_summaries"]["7"]["total_nodes_visited"] == 13792


def test_debug_payload_is_not_an_expected_artifact() -> None:
    payload = build_payload(max_nodes=1)

    assert payload["summary"]["debug_max_nodes"] == 1
    with pytest.raises(AssertionError, match="debug node limits"):
        assert_expected_payload(payload)
