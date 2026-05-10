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
    T10_STRICT_CYCLE_LEMMA,
    T11_STRICT_CYCLE_LEMMA,
    T12_STRICT_CYCLE_LEMMA,
    assert_expected_local_lemma_scan,
)
from scripts.check_n9_vertex_circle_local_lemmas import (
    DEFAULT_SELF_EDGE_PACKET,
    DEFAULT_STRICT_CYCLE_PACKET,
    scan_payload,
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
        "covered_assignment_count": 182,
        "covered_family_count": 15,
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
            "F14",
            "F15",
            "F16",
        ],
        "uncovered_assignment_count": 2,
        "uncovered_family_count": 1,
        "uncovered_family_ids": ["F13"],
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
            "F14": [SHARED_ENDPOINT_LEMMA],
            "F15": [T03_SELECTED_PATH_SELF_EDGE],
            "F16": [T12_STRICT_CYCLE_LEMMA],
        },
    }


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
    assert parsed["coverage_summary"]["covered_assignment_count"] == 182
    assert parsed["coverage_summary"]["uncovered_family_ids"] == ["F13"]
