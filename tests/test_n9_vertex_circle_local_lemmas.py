from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_vertex_circle_local_lemmas import (
    NESTED_SPOKE_LEMMA,
    SHARED_ENDPOINT_LEMMA,
    T10_STRICT_CYCLE_LEMMA,
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
        "covered_assignment_count": 154,
        "covered_family_count": 11,
        "covered_family_ids": [
            "F01",
            "F02",
            "F03",
            "F04",
            "F06",
            "F08",
            "F09",
            "F10",
            "F11",
            "F12",
            "F14",
        ],
        "family_to_lemmas": {
            "F01": [SHARED_ENDPOINT_LEMMA],
            "F02": [NESTED_SPOKE_LEMMA],
            "F03": [NESTED_SPOKE_LEMMA],
            "F04": [SHARED_ENDPOINT_LEMMA],
            "F06": [NESTED_SPOKE_LEMMA],
            "F08": [SHARED_ENDPOINT_LEMMA],
            "F09": [NESTED_SPOKE_LEMMA],
            "F10": [NESTED_SPOKE_LEMMA],
            "F11": [NESTED_SPOKE_LEMMA],
            "F12": [T10_STRICT_CYCLE_LEMMA],
            "F14": [SHARED_ENDPOINT_LEMMA],
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


def test_assert_expected_rejects_count_drift(payload: dict[str, object]) -> None:
    tampered = json.loads(json.dumps(payload))
    tampered["coverage_summary"]["covered_assignment_count"] = 153

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
    assert parsed["coverage_summary"]["covered_assignment_count"] == 154
