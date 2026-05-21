from scripts.check_n9_base_apex_d3_p19_degree_obstruction import (
    DEFAULT_PACKET,
    assert_expected_p19_degree_obstruction,
    load_json,
    p19_degree_obstruction_payload,
)


def test_n9_base_apex_d3_p19_degree_obstruction_artifact():
    packet = load_json(DEFAULT_PACKET)
    payload = p19_degree_obstruction_payload(packet, packet_path=DEFAULT_PACKET)
    assert_expected_p19_degree_obstruction(payload)
