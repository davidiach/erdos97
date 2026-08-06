from __future__ import annotations

from pathlib import Path

from erdos97.fragile_cycle_halo_deletion_crosswalk import (
    assert_expected_payload,
    retained_exclusive_pairs,
    retained_t4_certifiers,
    retained_uncertified_pairs,
)
from erdos97.fragile_cycle_halo_slot_budget import census_placement
from erdos97.json_io import load_json


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "fragile_cycle_halo_deletion_crosswalk.json"
)


def _rows(raw_rows: list[list[int]]) -> dict[int, tuple[int, ...]]:
    return {row[0]: tuple(row[1:]) for row in raw_rows}


def test_pair_free_and_exclusive_representatives_replay() -> None:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)
    four = payload["four_halos"]["representatives"]

    pair_free = _rows(four["pair_free"]["retained_rows"])
    order = four["pair_free"]["cyclic_order"]
    assert retained_exclusive_pairs(pair_free, order) == ()
    assert retained_uncertified_pairs(pair_free, order) == ()

    triggered = _rows(four["pair_1_3"]["retained_rows"])
    order = four["pair_1_3"]["cyclic_order"]
    assert retained_exclusive_pairs(triggered, order) == ((1, 3),)
    assert retained_uncertified_pairs(triggered, order) == ((1, 3),)
    assert retained_t4_certifiers(triggered, (1, 3)) == ()


def test_representative_placement_counts_match_slot_budget_source() -> None:
    source_four = census_placement((0, 0, 0, 0))
    source_five = census_placement((0, 0, 0, 0, 0))
    assert source_four["counts"]["essential_covers"] == 2364
    assert source_five["counts"]["essential_covers"] == 1110

    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)
    assert payload["four_halos"]["essential_cover_count"] == 529200
    assert payload["five_halos"]["essential_cover_count"] == 512820


def test_stored_crosswalk_has_expected_claim_boundary_and_totals() -> None:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)
    assert_expected_payload(payload)
    assert payload["summary"] == {
        "deletion_profile_trigger_is_universal": False,
        "essential_cover_count": 1042020,
        "exclusive_trigger_cover_count": 310320,
        "pair_free_negative_control_count": 731700,
    }
