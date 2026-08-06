from __future__ import annotations

from pathlib import Path

from erdos97.fragile_cycle_halo_endpoint_reuse import (
    assert_expected_payload,
    find_endpoint_reuse_witness,
)
from erdos97.json_io import load_json


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "fragile_cycle_halo_endpoint_reuse.json"
)


def _rows(raw_rows: list[list[int]]) -> dict[int, tuple[int, ...]]:
    return {row[0]: tuple(row[1:]) for row in raw_rows}


def test_stored_representatives_replay_deterministic_witnesses() -> None:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)
    checked = 0
    for section_name in ("four_halos", "five_halos"):
        representatives = payload[section_name]["representatives"]
        for representative in representatives.values():
            witness = find_endpoint_reuse_witness(
                representative["cyclic_order"],
                _rows(representative["retained_rows"]),
                representative["retained_exclusive_pair"],
            )
            assert witness == representative["endpoint_reuse_witness"]
            assert witness["vertex_circle_status"] == "ok"
            checked += 1
    assert checked >= 6


def test_stored_packet_has_expected_negative_control_boundary() -> None:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)
    assert_expected_payload(payload)
    assert payload["summary"] == {
        "alternate_center_survivor_count": 9265,
        "checked_constraints_force_richer_profile": False,
        "endpoint_reuse_survivor_count": 310320,
        "exclusive_trigger_cover_count": 310320,
        "no_survivor_count": 0,
        "preferred_center_survivor_count": 301055,
    }


def test_source_crosswalk_counts_are_preserved() -> None:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)
    assert payload["four_halos"]["exclusive_pair_identity_histogram"] == {
        "1-3": 41760,
        "1-6": 52920,
        "3-6": 49320,
    }
    assert payload["five_halos"]["exclusive_pair_identity_histogram"] == {
        "1-3": 55440,
        "1-6": 55440,
        "3-6": 55440,
    }
