from __future__ import annotations

import pytest

from erdos97.bridge_lemma_frontier import (
    EXPECTED_CROSS_TAB,
    EXPECTED_N8_EAR,
    EXPECTED_N8_NON_EAR_IDS,
    EXPECTED_N8_TOTAL,
    EXPECTED_N9_EAR,
    EXPECTED_N9_NON_EAR_INDICES,
    EXPECTED_N9_STATUS_COUNTS,
    EXPECTED_N9_TOTAL,
    SCHEMA,
    STATUS,
    assert_expected_payload,
)


def _expected_summary() -> dict[str, object]:
    return {
        "n8_total": EXPECTED_N8_TOTAL,
        "n8_ear_orderable": EXPECTED_N8_EAR,
        "n8_non_ear_orderable": EXPECTED_N8_TOTAL - EXPECTED_N8_EAR,
        "n8_non_ear_ids": EXPECTED_N8_NON_EAR_IDS,
        "n9_total": EXPECTED_N9_TOTAL,
        "n9_ear_orderable": EXPECTED_N9_EAR,
        "n9_non_ear_orderable": EXPECTED_N9_TOTAL - EXPECTED_N9_EAR,
        "n9_non_ear_indices": EXPECTED_N9_NON_EAR_INDICES,
        "n9_vertex_circle_status_counts": EXPECTED_N9_STATUS_COUNTS,
        "n9_cross_tabulation": EXPECTED_CROSS_TAB,
        "proof_mining_target_count": 6,
    }


def _n9_target(index: int, vertex_status: str = "strict_cycle") -> dict[str, object]:
    return {
        "target_id": f"n9-assignment-{index}",
        "n": 9,
        "vertex_circle_status": vertex_status,
        "exact_obstructions": [
            {
                "method": f"vertex_circle_{vertex_status}",
                "status": "EXACT_OBSTRUCTION_REVIEW_PENDING",
            }
        ],
    }


def test_bridge_frontier_rejects_n9_ok_as_exact_obstruction() -> None:
    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "summary": _expected_summary(),
        "proof_mining_targets": [_n9_target(index) for index in range(6)],
    }
    payload["proof_mining_targets"][0] = _n9_target(0, vertex_status="ok")

    with pytest.raises(AssertionError, match="lacks exact vertex-circle obstruction"):
        assert_expected_payload(payload)
