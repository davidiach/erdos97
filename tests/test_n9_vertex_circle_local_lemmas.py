from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_local_lemmas import (
    NESTED_SPOKE_LEMMA,
    SHARED_ENDPOINT_LEMMA,
    T03_SELECTED_PATH_SELF_EDGE,
    T04_SELECTED_PATH_SELF_EDGE,
    T10_STRICT_CYCLE_LEMMA,
    T11_STRICT_CYCLE_LEMMA,
    T12_STRICT_CYCLE_LEMMA,
    assert_expected_local_lemma_scan,
    local_lemma_scan_payload,
)
from scripts.check_n9_vertex_circle_local_lemmas import (
    DEFAULT_SELF_EDGE_PACKET,
    DEFAULT_STRICT_CYCLE_PACKET,
    DEFAULT_T01_PACKET,
    DEFAULT_T02_PACKET,
    DEFAULT_T03_PACKET,
    DEFAULT_T04_PACKET,
    DEFAULT_T05_PACKET,
    DEFAULT_T06_PACKET,
    DEFAULT_T07_PACKET,
    DEFAULT_T08_PACKET,
    DEFAULT_T09_PACKET,
    DEFAULT_T10_PACKET,
    DEFAULT_T11_PACKET,
    DEFAULT_T12_PACKET,
    load_artifact,
    scan_payload,
    validate_payload,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return scan_payload()


def _lemma(payload: dict[str, object], lemma_id: str) -> dict[str, object]:
    for item in payload["lemmas"]:  # type: ignore[index]
        if item["lemma_id"] == lemma_id:
            return item
    raise AssertionError(f"missing lemma {lemma_id}")


def test_local_lemma_scan_counts_and_scope(payload: dict[str, object]) -> None:
    assert_expected_local_lemma_scan(payload)
    assert payload["status"] == "REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "not a proof of n=9" in payload["claim_scope"]  # type: ignore[operator]
    assert "not a counterexample" in payload["claim_scope"]  # type: ignore[operator]
    assert "not a global status update" in payload["claim_scope"]  # type: ignore[operator]
    assert payload["coverage_summary"] == {  # type: ignore[index]
        "source_assignment_count": 184,
        "source_family_count": 16,
        "covered_assignment_count": 184,
        "covered_family_count": 16,
        "covered_family_ids": [
            "F01",
            "F02",
            "F03",
            "F04",
            "F05",
            "F06",
            "F07",
            "F08",
            "F09",
            "F10",
            "F11",
            "F12",
            "F13",
            "F14",
            "F15",
            "F16",
        ],
        "uncovered_assignment_count": 0,
        "uncovered_family_count": 0,
        "uncovered_family_ids": [],
        "family_to_lemmas": {
            "F01": [SHARED_ENDPOINT_LEMMA],
            "F02": [NESTED_SPOKE_LEMMA],
            "F03": [NESTED_SPOKE_LEMMA],
            "F04": [SHARED_ENDPOINT_LEMMA],
            "F05": [T03_SELECTED_PATH_SELF_EDGE],
            "F06": [NESTED_SPOKE_LEMMA],
            "F07": [T11_STRICT_CYCLE_LEMMA],
            "F08": [SHARED_ENDPOINT_LEMMA],
            "F09": [NESTED_SPOKE_LEMMA],
            "F10": [NESTED_SPOKE_LEMMA],
            "F11": [NESTED_SPOKE_LEMMA],
            "F12": [T10_STRICT_CYCLE_LEMMA],
            "F13": [T04_SELECTED_PATH_SELF_EDGE],
            "F14": [SHARED_ENDPOINT_LEMMA],
            "F15": [T03_SELECTED_PATH_SELF_EDGE],
            "F16": [T12_STRICT_CYCLE_LEMMA],
        },
    }
    assert payload["focused_note_crosscheck"] == [  # type: ignore[index]
        {
            "lemma_id": NESTED_SPOKE_LEMMA,
            "template_id": "T01",
            "family_ids": ["F09"],
            "proof_note_path": "docs/n9-vertex-circle-t01-self-edge-lemma.md",
            "source_kind": "focused_packet",
            "crosscheck_mode": "alternate_self_edge_certificate",
            "packet_key": "T01",
            "packet_path": (
                "data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json"
            ),
            "check_status": "checked",
            "families_checked": [
                {"family_id": "F09", "assignment_count": 6, "orbit_size": 6},
            ],
            "covered_assignment_count": 6,
            "interpretation": (
                "Aggregate scan family rows match the focused packet, and the "
                "focused packet supplies a valid alternate reflexive self-edge "
                "certificate for the same family. The aggregate nested-spoke "
                "strict edge is not required to be the same strict edge as the "
                "proof-facing note; this remains a packet consistency check, not "
                "an independent n=9 completeness proof."
            ),
        },
        {
            "lemma_id": NESTED_SPOKE_LEMMA,
            "template_id": "T05",
            "family_ids": ["F10"],
            "proof_note_path": "docs/n9-vertex-circle-t05-self-edge-lemma.md",
            "source_kind": "focused_packet",
            "crosscheck_mode": "alternate_self_edge_certificate",
            "packet_key": "T05",
            "packet_path": (
                "data/certificates/n9_vertex_circle_t05_self_edge_lemma_packet.json"
            ),
            "check_status": "checked",
            "families_checked": [
                {"family_id": "F10", "assignment_count": 18, "orbit_size": 18},
            ],
            "covered_assignment_count": 18,
            "interpretation": (
                "Aggregate scan family rows match the focused packet, and the "
                "focused packet supplies a valid alternate reflexive self-edge "
                "certificate for the same family. The aggregate nested-spoke "
                "strict edge is not required to be the same strict edge as the "
                "proof-facing note; this remains a packet consistency check, not "
                "an independent n=9 completeness proof."
            ),
        },
        {
            "lemma_id": NESTED_SPOKE_LEMMA,
            "template_id": "T06",
            "family_ids": ["F11"],
            "proof_note_path": "docs/n9-vertex-circle-t06-self-edge-lemma.md",
            "source_kind": "focused_packet",
            "crosscheck_mode": "alternate_self_edge_certificate",
            "aggregate_outer_pair_match_required": False,
            "packet_key": "T06",
            "packet_path": (
                "data/certificates/n9_vertex_circle_t06_self_edge_lemma_packet.json"
            ),
            "check_status": "checked",
            "families_checked": [
                {"family_id": "F11", "assignment_count": 18, "orbit_size": 18},
            ],
            "covered_assignment_count": 18,
            "interpretation": (
                "Aggregate scan family rows match the focused packet, and the "
                "focused packet supplies a valid alternate reflexive self-edge "
                "certificate for the same family. The proof-facing strict edge "
                "and equality path are checked inside the focused packet; they "
                "are not required to share the aggregate nested-spoke strict "
                "edge endpoint. This remains a packet consistency check, not "
                "an independent n=9 completeness proof."
            ),
        },
        {
            "lemma_id": NESTED_SPOKE_LEMMA,
            "template_id": "T07",
            "family_ids": ["F06"],
            "proof_note_path": "docs/n9-vertex-circle-t07-self-edge-lemma.md",
            "source_kind": "focused_packet",
            "crosscheck_mode": "alternate_self_edge_certificate",
            "packet_key": "T07",
            "packet_path": (
                "data/certificates/n9_vertex_circle_t07_self_edge_lemma_packet.json"
            ),
            "check_status": "checked",
            "families_checked": [
                {"family_id": "F06", "assignment_count": 18, "orbit_size": 18},
            ],
            "covered_assignment_count": 18,
            "interpretation": (
                "Aggregate scan family rows match the focused packet, and the "
                "focused packet supplies a valid alternate reflexive self-edge "
                "certificate for the same family. The aggregate nested-spoke "
                "strict edge is not required to be the same strict edge as the "
                "proof-facing note; this remains a packet consistency check, not "
                "an independent n=9 completeness proof."
            ),
        },
        {
            "lemma_id": NESTED_SPOKE_LEMMA,
            "template_id": "T08",
            "family_ids": ["F02"],
            "proof_note_path": "docs/n9-vertex-circle-t08-self-edge-lemma.md",
            "source_kind": "focused_packet",
            "crosscheck_mode": "alternate_self_edge_certificate",
            "packet_key": "T08",
            "packet_path": (
                "data/certificates/n9_vertex_circle_t08_self_edge_lemma_packet.json"
            ),
            "check_status": "checked",
            "families_checked": [
                {"family_id": "F02", "assignment_count": 18, "orbit_size": 18},
            ],
            "covered_assignment_count": 18,
            "interpretation": (
                "Aggregate scan family rows match the focused packet, and the "
                "focused packet supplies a valid alternate reflexive self-edge "
                "certificate for the same family. The aggregate nested-spoke "
                "strict edge is not required to be the same strict edge as the "
                "proof-facing note; this remains a packet consistency check, not "
                "an independent n=9 completeness proof."
            ),
        },
        {
            "lemma_id": NESTED_SPOKE_LEMMA,
            "template_id": "T09",
            "family_ids": ["F03"],
            "proof_note_path": "docs/n9-vertex-circle-t09-self-edge-lemma.md",
            "source_kind": "focused_packet",
            "crosscheck_mode": "alternate_self_edge_certificate",
            "packet_key": "T09",
            "packet_path": (
                "data/certificates/n9_vertex_circle_t09_self_edge_lemma_packet.json"
            ),
            "check_status": "checked",
            "families_checked": [
                {"family_id": "F03", "assignment_count": 18, "orbit_size": 18},
            ],
            "covered_assignment_count": 18,
            "interpretation": (
                "Aggregate scan family rows match the focused packet, and the "
                "focused packet supplies a valid alternate reflexive self-edge "
                "certificate for the same family. The aggregate nested-spoke "
                "strict edge is not required to be the same strict edge as the "
                "proof-facing note; this remains a packet consistency check, not "
                "an independent n=9 completeness proof."
            ),
        },
        {
            "lemma_id": SHARED_ENDPOINT_LEMMA,
            "template_id": "T02",
            "family_ids": ["F01", "F04", "F08", "F14"],
            "proof_note_path": "docs/n9-vertex-circle-t02-self-edge-lemma.md",
            "source_kind": "focused_packet",
            "packet_key": "T02",
            "packet_path": (
                "data/certificates/n9_vertex_circle_t02_self_edge_lemma_packet.json"
            ),
            "check_status": "checked",
            "families_checked": [
                {"family_id": "F01", "assignment_count": 18, "orbit_size": 18},
                {"family_id": "F04", "assignment_count": 18, "orbit_size": 18},
                {"family_id": "F08", "assignment_count": 2, "orbit_size": 2},
                {"family_id": "F14", "assignment_count": 2, "orbit_size": 2},
            ],
            "covered_assignment_count": 40,
            "interpretation": (
                "Aggregate scan instance matches the focused packet used by the "
                "proof-facing note; this is a packet consistency check, not an "
                "independent n=9 completeness proof."
            ),
        },
        {
            "lemma_id": T03_SELECTED_PATH_SELF_EDGE,
            "template_id": "T03",
            "family_ids": ["F05", "F15"],
            "proof_note_path": "docs/n9-vertex-circle-t03-self-edge-lemma.md",
            "source_kind": "focused_packet",
            "packet_key": "T03",
            "packet_path": (
                "data/certificates/n9_vertex_circle_t03_self_edge_lemma_packet.json"
            ),
            "check_status": "checked",
            "families_checked": [
                {"family_id": "F05", "assignment_count": 18, "orbit_size": 18},
                {"family_id": "F15", "assignment_count": 2, "orbit_size": 2},
            ],
            "covered_assignment_count": 20,
            "interpretation": (
                "Aggregate scan instance matches the focused packet used by the "
                "proof-facing note; this is a packet consistency check, not an "
                "independent n=9 completeness proof."
            ),
        },
        {
            "lemma_id": T04_SELECTED_PATH_SELF_EDGE,
            "template_id": "T04",
            "family_ids": ["F13"],
            "proof_note_path": "docs/n9-vertex-circle-t04-self-edge-lemma.md",
            "source_kind": "focused_packet",
            "packet_key": "T04",
            "packet_path": (
                "data/certificates/n9_vertex_circle_t04_self_edge_lemma_packet.json"
            ),
            "check_status": "checked",
            "families_checked": [
                {"family_id": "F13", "assignment_count": 2, "orbit_size": 2},
            ],
            "covered_assignment_count": 2,
            "interpretation": (
                "Aggregate scan instance matches the focused packet used by the "
                "proof-facing note; this is a packet consistency check, not an "
                "independent n=9 completeness proof."
            ),
        },
        {
            "lemma_id": T10_STRICT_CYCLE_LEMMA,
            "template_id": "T10",
            "family_ids": ["F12"],
            "proof_note_path": "docs/n9-vertex-circle-t10-strict-cycle-lemma.md",
            "source_kind": "focused_packet",
            "packet_key": "T10",
            "packet_path": (
                "data/certificates/n9_vertex_circle_t10_strict_cycle_lemma_packet.json"
            ),
            "check_status": "checked",
            "families_checked": [
                {"family_id": "F12", "assignment_count": 18, "orbit_size": 18},
            ],
            "covered_assignment_count": 18,
            "interpretation": (
                "Aggregate scan instance matches the focused packet used by the "
                "proof-facing note; this is a packet consistency check, not an "
                "independent n=9 completeness proof."
            ),
        },
        {
            "lemma_id": T11_STRICT_CYCLE_LEMMA,
            "template_id": "T11",
            "family_ids": ["F07"],
            "proof_note_path": "docs/n9-vertex-circle-t11-strict-cycle-lemma.md",
            "source_kind": "focused_packet",
            "packet_key": "T11",
            "packet_path": (
                "data/certificates/n9_vertex_circle_t11_strict_cycle_lemma_packet.json"
            ),
            "check_status": "checked",
            "families_checked": [
                {"family_id": "F07", "assignment_count": 6, "orbit_size": 6},
            ],
            "covered_assignment_count": 6,
            "interpretation": (
                "Aggregate scan instance matches the focused packet used by the "
                "proof-facing note; this is a packet consistency check, not an "
                "independent n=9 completeness proof."
            ),
        },
        {
            "lemma_id": T12_STRICT_CYCLE_LEMMA,
            "template_id": "T12",
            "family_ids": ["F16"],
            "proof_note_path": "docs/n9-vertex-circle-t12-strict-cycle-lemma.md",
            "source_kind": "focused_packet",
            "packet_key": "T12",
            "packet_path": (
                "data/certificates/n9_vertex_circle_t12_strict_cycle_lemma_packet.json"
            ),
            "check_status": "checked",
            "families_checked": [
                {"family_id": "F16", "assignment_count": 2, "orbit_size": 2},
            ],
            "covered_assignment_count": 2,
            "interpretation": (
                "Aggregate scan instance matches the focused packet used by the "
                "proof-facing note; this is a packet consistency check, not an "
                "independent n=9 completeness proof."
            ),
        },
    ]


def test_shared_endpoint_instances_are_t02_families(payload: dict[str, object]) -> None:
    lemma = _lemma(payload, SHARED_ENDPOINT_LEMMA)

    assert lemma["instance_count"] == 4
    assert lemma["covered_assignment_count"] == 40
    assert lemma["family_ids"] == ["F01", "F04", "F08", "F14"]
    assert lemma["template_ids"] == ["T02"]
    for instance in lemma["instances"]:  # type: ignore[index]
        assert instance["direct_conditions"]["holds"] is True
        assert instance["simple_filter_violations"] == []
        edge = instance["strict_inequality"]
        assert edge["outer_interval"] == [0, 3]
        assert edge["inner_interval"] == [0, 1]
        assert edge["outer_span"] == 3
        assert edge["inner_span"] == 1
        assert edge["outer_class"] == edge["inner_class"]


def test_nested_spoke_instances_use_quotient_not_direct_two_row(
    payload: dict[str, object],
) -> None:
    lemma = _lemma(payload, NESTED_SPOKE_LEMMA)

    assert lemma["instance_count"] == 8
    assert lemma["covered_assignment_count"] == 96
    assert lemma["family_ids"] == ["F02", "F03", "F06", "F09", "F10", "F11"]
    assert lemma["template_ids"] == ["T01", "T05", "T06", "T07", "T08", "T09"]
    for instance in lemma["instances"]:  # type: ignore[index]
        assert instance["simple_filter_violations"] == []
        assert instance["direct_conditions"]["holds"] is False
        edge = instance["strict_inequality"]
        assert edge["outer_interval"] == [0, 3]
        assert edge["inner_interval"] == [1, 2]
        assert edge["outer_span"] == 3
        assert edge["inner_span"] == 1
        assert set(edge["outer_pair"]).isdisjoint(edge["inner_pair"])
        assert edge["outer_class"] == edge["inner_class"]

    special = payload["direct_two_row_nested_spoke_special_case"]  # type: ignore[index]
    assert special["instance_count"] == 0
    assert special["instances"] == []
    assert "no exact direct instances" in special["interpretation"]


def test_t10_strict_cycle_instance(payload: dict[str, object]) -> None:
    lemma = _lemma(payload, T10_STRICT_CYCLE_LEMMA)

    assert lemma["instance_count"] == 1
    assert lemma["covered_assignment_count"] == 18
    assert lemma["family_ids"] == ["F12"]
    assert lemma["template_ids"] == ["T10"]
    instance = lemma["instances"][0]  # type: ignore[index]
    assert instance["replay_status"] == "strict_cycle"
    assert instance["simple_filter_violations"] == []
    assert instance["core_selected_rows"] == [
        [0, 1, 2, 5, 6],
        [3, 0, 1, 4, 6],
        [6, 1, 3, 4, 7],
        [8, 0, 3, 6, 7],
    ]
    assert [edge["outer_pair"] for edge in instance["cycle_edges"]] == [[0, 6], [1, 6]]
    assert [edge["inner_pair"] for edge in instance["cycle_edges"]] == [[0, 3], [0, 1]]


def test_t03_selected_path_self_edge_instances(payload: dict[str, object]) -> None:
    lemma = _lemma(payload, T03_SELECTED_PATH_SELF_EDGE)

    assert lemma["instance_count"] == 2
    assert lemma["covered_assignment_count"] == 20
    assert lemma["family_ids"] == ["F05", "F15"]
    assert lemma["template_ids"] == ["T03"]
    instances = {instance["family_id"]: instance for instance in lemma["instances"]}  # type: ignore[index]

    f05 = instances["F05"]
    assert f05["assignment_count"] == 18
    assert f05["simple_filter_violations"] == []
    assert f05["core_selected_rows"] == [
        [1, 2, 5, 7, 8],
        [2, 1, 3, 4, 8],
        [3, 0, 2, 4, 7],
        [6, 1, 3, 5, 7],
    ]
    assert f05["strict_inequality"]["row"] == 6
    assert f05["strict_inequality"]["outer_pair"] == [3, 7]
    assert f05["strict_inequality"]["inner_pair"] == [1, 7]
    assert f05["direct_conditions"] == {
        "variant": "selected_path_self_edge",
        "start_pair": [3, 7],
        "end_pair": [1, 7],
        "path": [
            {"row": 3, "next_pair": [2, 3]},
            {"row": 2, "next_pair": [1, 2]},
            {"row": 1, "next_pair": [1, 7]},
        ],
        "path_length": 3,
        "holds": True,
    }

    f15 = instances["F15"]
    assert f15["assignment_count"] == 2
    assert f15["simple_filter_violations"] == []
    assert f15["core_selected_rows"] == [
        [0, 1, 3, 4, 8],
        [1, 0, 2, 4, 5],
        [2, 1, 3, 5, 6],
        [3, 2, 4, 6, 7],
    ]
    assert f15["strict_inequality"]["row"] == 0
    assert f15["strict_inequality"]["outer_pair"] == [1, 4]
    assert f15["strict_inequality"]["inner_pair"] == [3, 4]
    assert f15["direct_conditions"] == {
        "variant": "selected_path_self_edge",
        "start_pair": [1, 4],
        "end_pair": [3, 4],
        "path": [
            {"row": 1, "next_pair": [1, 2]},
            {"row": 2, "next_pair": [2, 3]},
            {"row": 3, "next_pair": [3, 4]},
        ],
        "path_length": 3,
        "holds": True,
    }


def test_t04_selected_path_self_edge_instance(payload: dict[str, object]) -> None:
    lemma = _lemma(payload, T04_SELECTED_PATH_SELF_EDGE)

    assert lemma["instance_count"] == 1
    assert lemma["covered_assignment_count"] == 2
    assert lemma["family_ids"] == ["F13"]
    assert lemma["template_ids"] == ["T04"]
    instance = lemma["instances"][0]  # type: ignore[index]
    assert instance["assignment_count"] == 2
    assert instance["simple_filter_violations"] == []
    assert instance["core_selected_rows"] == [
        [0, 1, 2, 5, 7],
        [1, 2, 3, 6, 8],
        [3, 1, 4, 5, 8],
        [5, 1, 3, 6, 7],
    ]
    assert instance["strict_inequality"]["row"] == 0
    assert instance["strict_inequality"]["outer_pair"] == [1, 5]
    assert instance["strict_inequality"]["inner_pair"] == [1, 2]
    assert instance["direct_conditions"] == {
        "variant": "selected_path_self_edge",
        "start_pair": [1, 5],
        "end_pair": [1, 2],
        "path": [
            {"row": 5, "next_pair": [3, 5]},
            {"row": 3, "next_pair": [1, 3]},
            {"row": 1, "next_pair": [1, 2]},
        ],
        "path_length": 3,
        "holds": True,
    }


def test_t11_strict_cycle_instance(payload: dict[str, object]) -> None:
    lemma = _lemma(payload, T11_STRICT_CYCLE_LEMMA)

    assert lemma["instance_count"] == 1
    assert lemma["covered_assignment_count"] == 6
    assert lemma["family_ids"] == ["F07"]
    assert lemma["template_ids"] == ["T11"]
    instance = lemma["instances"][0]  # type: ignore[index]
    assert instance["replay_status"] == "strict_cycle"
    assert instance["simple_filter_violations"] == []
    assert instance["core_selected_rows"] == [
        [0, 1, 2, 4, 8],
        [1, 0, 2, 3, 5],
        [5, 0, 3, 4, 7],
        [6, 1, 5, 7, 8],
    ]
    assert [edge["outer_pair"] for edge in instance["cycle_edges"]] == [
        [0, 2],
        [0, 3],
        [5, 7],
    ]
    assert [edge["inner_pair"] for edge in instance["cycle_edges"]] == [
        [0, 3],
        [0, 5],
        [1, 5],
    ]


def test_t12_strict_cycle_instance(payload: dict[str, object]) -> None:
    lemma = _lemma(payload, T12_STRICT_CYCLE_LEMMA)

    assert lemma["instance_count"] == 1
    assert lemma["covered_assignment_count"] == 2
    assert lemma["family_ids"] == ["F16"]
    assert lemma["template_ids"] == ["T12"]
    instance = lemma["instances"][0]  # type: ignore[index]
    assert instance["replay_status"] == "strict_cycle"
    assert instance["simple_filter_violations"] == []
    assert instance["core_selected_rows"] == [
        [0, 1, 3, 6, 7],
        [1, 2, 4, 7, 8],
        [2, 0, 3, 5, 8],
        [3, 0, 1, 4, 6],
        [4, 1, 2, 5, 7],
        [8, 0, 2, 5, 6],
    ]
    assert [edge["outer_pair"] for edge in instance["cycle_edges"]] == [
        [0, 3],
        [2, 8],
        [1, 7],
    ]
    assert [edge["inner_pair"] for edge in instance["cycle_edges"]] == [
        [0, 8],
        [2, 4],
        [1, 3],
    ]


def test_assert_expected_rejects_count_drift(payload: dict[str, object]) -> None:
    tampered = json.loads(json.dumps(payload))
    tampered["coverage_summary"]["covered_assignment_count"] = 181

    with pytest.raises(AssertionError, match="covered_assignment_count mismatch"):
        assert_expected_local_lemma_scan(tampered)


def test_validate_payload_rejects_provenance_drift(payload: dict[str, object]) -> None:
    tampered = json.loads(json.dumps(payload))
    tampered["provenance"]["command"] = "python changed.py"

    errors = validate_payload(tampered, payload)

    assert any("provenance mismatch" in error for error in errors)
    assert "local-lemma scan payload mismatch" in errors


def test_payload_provenance_is_not_shared_mutable_state() -> None:
    payload = scan_payload()
    payload["provenance"]["command"] = "python changed.py"  # type: ignore[index]

    with pytest.raises(AssertionError, match="provenance mismatch"):
        assert_expected_local_lemma_scan(payload)

    fresh_payload = scan_payload()
    assert fresh_payload["provenance"]["command"] == (  # type: ignore[index]
        "python scripts/check_n9_vertex_circle_local_lemmas.py --assert-expected --write"
    )


def test_focused_packet_crosscheck_rejects_t01_path_drift() -> None:
    self_edge_packet = load_artifact(DEFAULT_SELF_EDGE_PACKET)
    strict_cycle_packet = load_artifact(DEFAULT_STRICT_CYCLE_PACKET)
    t01_packet = load_artifact(DEFAULT_T01_PACKET)
    t01_packet["distance_equality"]["path"][0]["next_pair"] = [0, 3]

    with pytest.raises(AssertionError, match="F09 focused packet equality path step mismatch"):
        local_lemma_scan_payload(
            self_edge_packet,
            strict_cycle_packet,
            focused_packets={
                "T01": t01_packet,
                "T02": load_artifact(DEFAULT_T02_PACKET),
                "T03": load_artifact(DEFAULT_T03_PACKET),
                "T04": load_artifact(DEFAULT_T04_PACKET),
                "T05": load_artifact(DEFAULT_T05_PACKET),
                "T06": load_artifact(DEFAULT_T06_PACKET),
                "T07": load_artifact(DEFAULT_T07_PACKET),
                "T08": load_artifact(DEFAULT_T08_PACKET),
                "T09": load_artifact(DEFAULT_T09_PACKET),
                "T10": load_artifact(DEFAULT_T10_PACKET),
                "T11": load_artifact(DEFAULT_T11_PACKET),
                "T12": load_artifact(DEFAULT_T12_PACKET),
            },
        )


def test_focused_packet_crosscheck_rejects_t05_path_drift() -> None:
    self_edge_packet = load_artifact(DEFAULT_SELF_EDGE_PACKET)
    strict_cycle_packet = load_artifact(DEFAULT_STRICT_CYCLE_PACKET)
    t05_packet = load_artifact(DEFAULT_T05_PACKET)
    t05_packet["family_packets"][0]["distance_equality"]["path"][0]["next_pair"] = [0, 8]

    with pytest.raises(AssertionError, match="F10 focused packet equality path step mismatch"):
        local_lemma_scan_payload(
            self_edge_packet,
            strict_cycle_packet,
            focused_packets={
                "T01": load_artifact(DEFAULT_T01_PACKET),
                "T02": load_artifact(DEFAULT_T02_PACKET),
                "T03": load_artifact(DEFAULT_T03_PACKET),
                "T04": load_artifact(DEFAULT_T04_PACKET),
                "T05": t05_packet,
                "T06": load_artifact(DEFAULT_T06_PACKET),
                "T07": load_artifact(DEFAULT_T07_PACKET),
                "T08": load_artifact(DEFAULT_T08_PACKET),
                "T09": load_artifact(DEFAULT_T09_PACKET),
                "T10": load_artifact(DEFAULT_T10_PACKET),
                "T11": load_artifact(DEFAULT_T11_PACKET),
                "T12": load_artifact(DEFAULT_T12_PACKET),
            },
        )


def test_focused_packet_crosscheck_rejects_t06_path_drift() -> None:
    self_edge_packet = load_artifact(DEFAULT_SELF_EDGE_PACKET)
    strict_cycle_packet = load_artifact(DEFAULT_STRICT_CYCLE_PACKET)
    t06_packet = load_artifact(DEFAULT_T06_PACKET)
    t06_packet["family_packets"][0]["distance_equality"]["path"][0]["next_pair"] = [0, 3]

    with pytest.raises(AssertionError, match="F11 focused packet equality path step mismatch"):
        local_lemma_scan_payload(
            self_edge_packet,
            strict_cycle_packet,
            focused_packets={
                "T01": load_artifact(DEFAULT_T01_PACKET),
                "T02": load_artifact(DEFAULT_T02_PACKET),
                "T03": load_artifact(DEFAULT_T03_PACKET),
                "T04": load_artifact(DEFAULT_T04_PACKET),
                "T05": load_artifact(DEFAULT_T05_PACKET),
                "T06": t06_packet,
                "T07": load_artifact(DEFAULT_T07_PACKET),
                "T08": load_artifact(DEFAULT_T08_PACKET),
                "T09": load_artifact(DEFAULT_T09_PACKET),
                "T10": load_artifact(DEFAULT_T10_PACKET),
                "T11": load_artifact(DEFAULT_T11_PACKET),
                "T12": load_artifact(DEFAULT_T12_PACKET),
            },
        )


def test_focused_packet_crosscheck_rejects_t07_path_drift() -> None:
    self_edge_packet = load_artifact(DEFAULT_SELF_EDGE_PACKET)
    strict_cycle_packet = load_artifact(DEFAULT_STRICT_CYCLE_PACKET)
    t07_packet = load_artifact(DEFAULT_T07_PACKET)
    t07_packet["family_packets"][0]["distance_equality"]["path"][0]["next_pair"] = [0, 1]

    with pytest.raises(AssertionError, match="F06 focused packet equality path step mismatch"):
        local_lemma_scan_payload(
            self_edge_packet,
            strict_cycle_packet,
            focused_packets={
                "T01": load_artifact(DEFAULT_T01_PACKET),
                "T02": load_artifact(DEFAULT_T02_PACKET),
                "T03": load_artifact(DEFAULT_T03_PACKET),
                "T04": load_artifact(DEFAULT_T04_PACKET),
                "T05": load_artifact(DEFAULT_T05_PACKET),
                "T06": load_artifact(DEFAULT_T06_PACKET),
                "T07": t07_packet,
                "T08": load_artifact(DEFAULT_T08_PACKET),
                "T09": load_artifact(DEFAULT_T09_PACKET),
                "T10": load_artifact(DEFAULT_T10_PACKET),
                "T11": load_artifact(DEFAULT_T11_PACKET),
                "T12": load_artifact(DEFAULT_T12_PACKET),
            },
        )


def test_focused_packet_crosscheck_rejects_t08_path_drift() -> None:
    self_edge_packet = load_artifact(DEFAULT_SELF_EDGE_PACKET)
    strict_cycle_packet = load_artifact(DEFAULT_STRICT_CYCLE_PACKET)
    t08_packet = load_artifact(DEFAULT_T08_PACKET)
    t08_packet["family_packets"][0]["distance_equality"]["path"][0]["next_pair"] = [0, 1]

    with pytest.raises(AssertionError, match="F02 focused packet equality path step mismatch"):
        local_lemma_scan_payload(
            self_edge_packet,
            strict_cycle_packet,
            focused_packets={
                "T01": load_artifact(DEFAULT_T01_PACKET),
                "T02": load_artifact(DEFAULT_T02_PACKET),
                "T03": load_artifact(DEFAULT_T03_PACKET),
                "T04": load_artifact(DEFAULT_T04_PACKET),
                "T05": load_artifact(DEFAULT_T05_PACKET),
                "T06": load_artifact(DEFAULT_T06_PACKET),
                "T07": load_artifact(DEFAULT_T07_PACKET),
                "T08": t08_packet,
                "T09": load_artifact(DEFAULT_T09_PACKET),
                "T10": load_artifact(DEFAULT_T10_PACKET),
                "T11": load_artifact(DEFAULT_T11_PACKET),
                "T12": load_artifact(DEFAULT_T12_PACKET),
            },
        )


def test_focused_packet_crosscheck_rejects_t09_path_drift() -> None:
    self_edge_packet = load_artifact(DEFAULT_SELF_EDGE_PACKET)
    strict_cycle_packet = load_artifact(DEFAULT_STRICT_CYCLE_PACKET)
    t09_packet = load_artifact(DEFAULT_T09_PACKET)
    t09_packet["family_packets"][0]["distance_equality"]["path"][0]["next_pair"] = [1, 7]

    with pytest.raises(AssertionError, match="F03 focused packet equality path step mismatch"):
        local_lemma_scan_payload(
            self_edge_packet,
            strict_cycle_packet,
            focused_packets={
                "T01": load_artifact(DEFAULT_T01_PACKET),
                "T02": load_artifact(DEFAULT_T02_PACKET),
                "T03": load_artifact(DEFAULT_T03_PACKET),
                "T04": load_artifact(DEFAULT_T04_PACKET),
                "T05": load_artifact(DEFAULT_T05_PACKET),
                "T06": load_artifact(DEFAULT_T06_PACKET),
                "T07": load_artifact(DEFAULT_T07_PACKET),
                "T08": load_artifact(DEFAULT_T08_PACKET),
                "T09": t09_packet,
                "T10": load_artifact(DEFAULT_T10_PACKET),
                "T11": load_artifact(DEFAULT_T11_PACKET),
                "T12": load_artifact(DEFAULT_T12_PACKET),
            },
        )


def test_focused_packet_crosscheck_rejects_t02_path_drift() -> None:
    self_edge_packet = load_artifact(DEFAULT_SELF_EDGE_PACKET)
    strict_cycle_packet = load_artifact(DEFAULT_STRICT_CYCLE_PACKET)
    t02_packet = load_artifact(DEFAULT_T02_PACKET)
    t02_packet["family_packets"][0]["distance_equality"]["path"][0]["next_pair"] = [0, 7]

    with pytest.raises(AssertionError, match="F01 focused packet distance_equality mismatch"):
        local_lemma_scan_payload(
            self_edge_packet,
            strict_cycle_packet,
            focused_packets={
                "T01": load_artifact(DEFAULT_T01_PACKET),
                "T02": t02_packet,
                "T03": load_artifact(DEFAULT_T03_PACKET),
                "T04": load_artifact(DEFAULT_T04_PACKET),
                "T05": load_artifact(DEFAULT_T05_PACKET),
                "T06": load_artifact(DEFAULT_T06_PACKET),
                "T07": load_artifact(DEFAULT_T07_PACKET),
                "T08": load_artifact(DEFAULT_T08_PACKET),
                "T09": load_artifact(DEFAULT_T09_PACKET),
                "T10": load_artifact(DEFAULT_T10_PACKET),
                "T11": load_artifact(DEFAULT_T11_PACKET),
                "T12": load_artifact(DEFAULT_T12_PACKET),
            },
        )


def test_focused_packet_crosscheck_rejects_t03_row_drift() -> None:
    self_edge_packet = load_artifact(DEFAULT_SELF_EDGE_PACKET)
    strict_cycle_packet = load_artifact(DEFAULT_STRICT_CYCLE_PACKET)
    t03_packet = load_artifact(DEFAULT_T03_PACKET)
    t03_packet["family_packets"][0]["core_selected_rows"][0][1] = 8

    with pytest.raises(AssertionError, match="F05 focused packet core_selected_rows mismatch"):
        local_lemma_scan_payload(
            self_edge_packet,
            strict_cycle_packet,
            focused_packets={
                "T01": load_artifact(DEFAULT_T01_PACKET),
                "T02": load_artifact(DEFAULT_T02_PACKET),
                "T03": t03_packet,
                "T04": load_artifact(DEFAULT_T04_PACKET),
                "T05": load_artifact(DEFAULT_T05_PACKET),
                "T06": load_artifact(DEFAULT_T06_PACKET),
                "T07": load_artifact(DEFAULT_T07_PACKET),
                "T10": load_artifact(DEFAULT_T10_PACKET),
                "T11": load_artifact(DEFAULT_T11_PACKET),
                "T12": load_artifact(DEFAULT_T12_PACKET),
            },
        )


def test_focused_packet_crosscheck_rejects_t10_replay_status_drift() -> None:
    self_edge_packet = load_artifact(DEFAULT_SELF_EDGE_PACKET)
    strict_cycle_packet = load_artifact(DEFAULT_STRICT_CYCLE_PACKET)
    t10_packet = load_artifact(DEFAULT_T10_PACKET)
    t10_packet["family_packets"][0]["replay"]["status"] = "unknown"

    with pytest.raises(AssertionError, match="F12 focused packet replay status mismatch"):
        local_lemma_scan_payload(
            self_edge_packet,
            strict_cycle_packet,
            focused_packets={
                "T01": load_artifact(DEFAULT_T01_PACKET),
                "T02": load_artifact(DEFAULT_T02_PACKET),
                "T03": load_artifact(DEFAULT_T03_PACKET),
                "T04": load_artifact(DEFAULT_T04_PACKET),
                "T05": load_artifact(DEFAULT_T05_PACKET),
                "T06": load_artifact(DEFAULT_T06_PACKET),
                "T07": load_artifact(DEFAULT_T07_PACKET),
                "T08": load_artifact(DEFAULT_T08_PACKET),
                "T09": load_artifact(DEFAULT_T09_PACKET),
                "T10": t10_packet,
                "T11": load_artifact(DEFAULT_T11_PACKET),
                "T12": load_artifact(DEFAULT_T12_PACKET),
            },
        )


def test_local_lemma_scan_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_local_lemmas.py",
            "--self-edge-packet",
            str(DEFAULT_SELF_EDGE_PACKET),
            "--strict-cycle-packet",
            str(DEFAULT_STRICT_CYCLE_PACKET),
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    parsed = json.loads(result.stdout)
    assert parsed["schema"] == "erdos97.n9_vertex_circle_local_lemmas.v1"
    assert parsed["coverage_summary"]["covered_assignment_count"] == 184
    assert parsed["coverage_summary"]["uncovered_family_ids"] == []


def test_local_lemma_scan_cli_write_and_check(tmp_path: Path) -> None:
    artifact = tmp_path / "n9_vertex_circle_local_lemmas.json"
    write_result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_local_lemmas.py",
            "--write",
            "--out",
            str(artifact),
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    write_summary = json.loads(write_result.stdout)
    assert write_summary["ok"] is True
    assert write_summary["covered_assignment_count"] == 184
    stored = json.loads(artifact.read_text(encoding="utf-8"))
    assert stored["provenance"] == {
        "generator": "scripts/check_n9_vertex_circle_local_lemmas.py",
        "command": (
            "python scripts/check_n9_vertex_circle_local_lemmas.py "
            "--assert-expected --write"
        ),
    }

    check_result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_local_lemmas.py",
            "--check",
            "--artifact",
            str(artifact),
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    check_summary = json.loads(check_result.stdout)
    assert check_summary["ok"] is True
    assert check_summary["lemma_count"] == 7
