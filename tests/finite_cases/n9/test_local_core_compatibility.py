from erdos97.finite_cases.n9 import local_core_packet
from scripts import check_n9_vertex_circle_local_core_packet as cli


def test_old_script_api_uses_the_grouped_validator():
    assert cli.validate_payload is local_core_packet.validate_payload
    assert cli.DEFAULT_ARTIFACT == local_core_packet.DEFAULT_ARTIFACT
    assert cli.DEFAULT_ARTIFACT.is_file()
