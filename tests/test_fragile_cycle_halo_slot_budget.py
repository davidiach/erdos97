from __future__ import annotations

from pathlib import Path
from itertools import combinations_with_replacement

from erdos97.fragile_cycle_halo_lift_frontier import (
    cyclic_order_for_gaps,
    enumerate_fragile_covers,
)
from erdos97.fragile_cycle_halo_slot_budget import (
    MAX_ACTIVE_HALO_COUNT,
    assert_expected_payload,
    census_placement,
    has_equilateral_hinge,
    has_kalmanson_splice,
    minimum_retained_private_halos,
)
from erdos97.json_io import load_json
from erdos97.kalmanson_equilateral_hinge import find_hinge_instances

import pytest
from erdos97.kalmanson_splice import find_dihedral_splice_embeddings


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "fragile_cycle_halo_slot_budget.json"


def test_slot_budget_caps_active_halos_and_forces_private_roles() -> None:
    assert MAX_ACTIVE_HALO_COUNT == 5
    assert minimum_retained_private_halos(4) == 3
    assert minimum_retained_private_halos(5) == 5


def test_fast_motif_predicates_match_generic_one_halo_scan() -> None:
    checked = 0
    for gap in range(7):
        order = cyclic_order_for_gaps((gap,))
        for rows in enumerate_fragile_covers(order)["covers"]:
            assert has_equilateral_hinge(rows, order) == bool(
                find_hinge_instances(rows, order)
            )
            assert has_kalmanson_splice(rows, order) == bool(
                find_dihedral_splice_embeddings(rows, order)
            )
            checked += 1
    assert checked == 38


@pytest.mark.artifact
def test_fast_motif_predicates_match_generic_two_halo_frontier() -> None:
    checked = 0
    hinge_covers = 0
    splice_covers = 0
    for gaps in combinations_with_replacement(range(7), 2):
        order = cyclic_order_for_gaps(gaps)
        for rows in enumerate_fragile_covers(order)["covers"]:
            hinge = has_equilateral_hinge(rows, order)
            splice = has_kalmanson_splice(rows, order)
            assert hinge == bool(find_hinge_instances(rows, order))
            assert splice == bool(find_dihedral_splice_embeddings(rows, order))
            checked += 1
            hinge_covers += hinge
            splice_covers += splice
    assert (checked, hinge_covers, splice_covers) == (7708, 1682, 3032)


def test_representative_large_halo_placements_replay() -> None:
    four = census_placement((0, 0, 0, 0))
    assert four["counts"]["essential_covers"] == 2364
    assert four["retained_private_halo_histogram"] == {"3": 984, "4": 1380}
    assert four["spare_kind_histogram"] == {
        "duplicated_halo": 984,
        "duplicated_missing_core": 558,
        "required_anchor_reuse": 822,
    }

    five = census_placement((0, 0, 0, 0, 0))
    assert five["counts"]["essential_covers"] == 1110
    assert five["counts"]["motif_free_covers"] == 1110
    assert five["retained_private_halo_histogram"] == {"5": 1110}


def test_stored_packet_has_expected_claim_boundary_and_totals() -> None:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)
    assert_expected_payload(payload)
    assert payload["four_halos"]["aggregate_counts"]["essential_covers"] == 529200
    assert payload["five_halos"]["aggregate_counts"]["essential_covers"] == 512820
