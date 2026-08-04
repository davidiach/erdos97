from __future__ import annotations

from pathlib import Path

from erdos97.fragile_cycle_halo_lift_frontier import (
    EXPECTED_ASSIGNMENT_IDS,
    assert_expected_payload,
    cyclic_order_for_gaps,
    enumerate_fragile_covers,
)
from erdos97.json_io import load_json


ROOT = Path(__file__).resolve().parents[1]


def _source(name: str) -> dict[str, object]:
    payload = load_json(ROOT / "data" / "certificates" / name)
    assert isinstance(payload, dict)
    return payload


def test_zero_halo_core_has_no_four_row_lift() -> None:
    result = enumerate_fragile_covers(cyclic_order_for_gaps(()))
    assert result["raw_row_combination_count"] == 1296
    assert result["pair_and_crossing_compatible_count"] == 0
    assert result["essential_cover_count"] == 0


def test_stored_halo_lift_payload_expected() -> None:
    payload = _source("fragile_cycle_halo_lift_frontier.json")
    assert_expected_payload(payload)
    assert payload["summary"]["minimum_added_halos_for_fragile_cover"] == 1
    assert payload["summary"]["minimum_added_halos_for_full_selected_extension"] == 2
    assert payload["two_halos"]["assignment_ids"] == EXPECTED_ASSIGNMENT_IDS
    assert all(
        witness["positive_circuit"]["identity_balance"] == []
        for witness in payload["two_halos"]["extension_witnesses"]
    )
