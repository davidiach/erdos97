from __future__ import annotations

from pathlib import Path

from erdos97.fragile_cycle_three_halo_kalmanson_endgame import (
    EXPECTED_CATALOG_SHA256,
    N,
    assert_expected_payload,
    partial_distance_quotient,
    replay_kalmanson_certificate,
)
from erdos97.json_io import load_json


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "fragile_cycle_three_halo_kalmanson_endgame.json"
)


def _payload() -> dict[str, object]:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)
    return payload


def test_stored_kalmanson_endgame_matches_expected() -> None:
    payload = _payload()
    assert_expected_payload(payload)
    assert payload["kalmanson_endgame_catalog_sha256"] == EXPECTED_CATALOG_SHA256
    assert payload["strict_support_histogram"] == {"1": 11, "2": 2}
    assert payload["selected_core_width_histogram"] == {"3": 13}
    assert "arbitrary wider positive combinations" in payload[
        "certificate_contract"
    ]["selected_core_minimality_scope"]


def test_every_selected_certificate_replays_from_three_partial_rows() -> None:
    payload = _payload()
    certificates = payload["state_certificates"]
    assert isinstance(certificates, list)
    assert len(certificates) == 13
    for certificate in certificates:
        replay = replay_kalmanson_certificate(N, certificate)
        assert replay == certificate["independent_replay"]
        assert replay["selected_core_row_count"] == 3
        assert replay["zero_sum_verified"] is True


def test_inverse_pair_states_have_no_single_strict_self_edge() -> None:
    payload = _payload()
    certificates = payload["state_certificates"]
    inverse_pairs = [
        certificate
        for certificate in certificates
        if certificate["obstruction_type"] == "strict_kalmanson_inverse_pair"
    ]
    assert [certificate["state_id"] for certificate in inverse_pairs] == [
        "S08",
        "S11",
    ]
    for certificate in inverse_pairs:
        assert certificate["strict_row_count"] == 2
        assert all(item["weight"] == 1 for item in certificate["strict_rows"])


def test_partial_quotient_does_not_require_rows_at_every_center() -> None:
    quotient = partial_distance_quotient(
        6,
        (
            (0, (1, 2, 3, 4)),
            (3, (0, 1, 4, 5)),
        ),
    )
    assert quotient.n == 6
    assert quotient.class_count == 9
