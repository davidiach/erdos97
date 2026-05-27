import pytest

from scripts.check_n9_base_apex_d3_p20_residue_obstruction import (
    CLAIM_SCOPE,
    DEFAULT_PACKET,
    assert_expected_p20_residue_obstruction,
    load_json,
    p20_residue_obstruction_payload,
)


def test_n9_base_apex_d3_p20_residue_obstruction_artifact():
    packet = load_json(DEFAULT_PACKET)
    payload = p20_residue_obstruction_payload(packet, packet_path=DEFAULT_PACKET)
    assert_expected_p20_residue_obstruction(payload)


def test_n9_base_apex_d3_p20_residue_obstruction_rejects_claim_scope_overclaim():
    packet = load_json(DEFAULT_PACKET)
    payload = p20_residue_obstruction_payload(packet, packet_path=DEFAULT_PACKET)
    payload["claim_scope"] = f"{CLAIM_SCOPE} This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_p20_residue_obstruction(payload)
