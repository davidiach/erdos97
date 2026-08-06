from __future__ import annotations

from pathlib import Path

from erdos97.fragile_cycle_halo_motif_forcing import (
    assert_expected_payload,
    halo_motif_forcing_payload,
    hinge_free_full_extension_search,
)
from erdos97.json_io import load_json


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "fragile_cycle_halo_motif_forcing.json"
SOURCE = ROOT / "data" / "certificates" / "fragile_cycle_halo_lift_frontier.json"


def _object(path: Path) -> dict[str, object]:
    payload = load_json(path)
    assert isinstance(payload, dict)
    return payload


def test_stored_packet_matches_complete_regeneration() -> None:
    stored = _object(ARTIFACT)
    source = _object(SOURCE)

    assert_expected_payload(stored)
    assert stored == halo_motif_forcing_payload(source)


def test_first_complete_boundary_forces_a_hinge() -> None:
    payload = _object(ARTIFACT)

    assert payload["one_halo"]["essential_cover_count"] == 38
    assert payload["one_halo"]["motif_free_cover_count"] == 0
    assert payload["two_halos"]["essential_cover_count"] == 7708
    assert payload["two_halos"]["source_extendable_cover_count"] == 6
    assert payload["two_halos"]["hinge_free_extendable_cover_count"] == 0
    assert payload["two_halos"]["all_full_extensions_force_hinge"] is True


def test_hinge_free_search_replays_first_extendable_cover() -> None:
    source = _object(SOURCE)
    witness = source["two_halos"]["extension_witnesses"][0]
    rows = {
        int(raw[0]): tuple(int(value) for value in raw[1:])
        for raw in witness["fragile_rows"]
    }

    replay = hinge_free_full_extension_search(witness["cyclic_order"], rows)
    assert replay["hinge_free_full_extension_exists"] is False
    assert replay["search_exhausted"] is True
    assert replay["search_counts"] == {
        "states_visited": 13,
        "branches_visited": 12,
        "dead_ends": 2,
        "hinge_prunes": 7,
    }
