from __future__ import annotations

from pathlib import Path

from erdos97.fragile_cycle_three_halo_motif_crosswalk import (
    EXPECTED_CATALOG_SHA256,
    assert_expected_payload,
)
from erdos97.json_io import load_json


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "fragile_cycle_three_halo_motif_crosswalk.json"
)


def _payload() -> dict[str, object]:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)
    return payload


def test_stored_motif_crosswalk_matches_expected() -> None:
    payload = _payload()
    assert_expected_payload(payload)
    assert payload["motif_crosswalk_catalog_sha256"] == EXPECTED_CATALOG_SHA256
    assert payload["motif_class_counts"] == {
        "equilateral_hinge": 11,
        "five_role_K2_K1_splice": 1,
        "six_role_K1_K2_splice": 1,
    }


def test_each_source_state_has_exactly_one_motif_embedding() -> None:
    payload = _payload()
    records = payload["state_motif_crosswalk"]
    assert isinstance(records, list)
    assert len(records) == 13
    assert len({record["state_id"] for record in records}) == 13
    assert all(record["motif_embedding"] for record in records)
    assert all(
        record["source_certificate_replay"]["zero_sum_verified"] is True
        for record in records
    )


def test_hinge_free_states_are_the_two_unique_splice_types() -> None:
    payload = _payload()
    records = payload["state_motif_crosswalk"]
    splices = [record for record in records if "splice" in record["motif_class"]]
    assert [(record["state_id"], record["motif_class"]) for record in splices] == [
        ("S08", "six_role_K1_K2_splice"),
        ("S11", "five_role_K2_K1_splice"),
    ]
