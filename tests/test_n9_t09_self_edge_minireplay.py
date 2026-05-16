from __future__ import annotations

import json
from pathlib import Path

import pytest

from erdos97.n9_t09_self_edge_minireplay import (
    assert_expected_payload,
    minireplay_payload,
    replay_packet,
    validate_payload,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "certificates" / "n9_vertex_circle_t09_self_edge_lemma_packet.json"


def _source_packet() -> dict[str, object]:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_t09_minireplay_replays_f03_local_self_edge() -> None:
    packet = _source_packet()
    replay, errors = replay_packet(packet)

    assert errors == []
    assert replay["family_ids"] == ["F03"]
    assert replay["assignment_count"] == 18
    assert replay["assignment_counts"] == {"F03": 18}
    assert replay["path_length_counts"] == {"6": 1}
    assert replay["all_self_edge_contradictions"] is True
    family = replay["family_replays"][0]
    assert family["equality_chain"] == [
        [1, 3],
        [0, 1],
        [0, 8],
        [4, 8],
        [3, 4],
        [2, 3],
        [1, 2],
    ]
    assert family["strict_inequality"] == {
        "row": 0,
        "witness_order": [1, 2, 3, 8],
        "outer_pair": [1, 3],
        "inner_pair": [1, 2],
        "outer_interval": [0, 2],
        "inner_interval": [0, 1],
        "outer_span": 2,
        "inner_span": 1,
    }


def test_t09_minireplay_rejects_broken_equality_step() -> None:
    packet = _source_packet()
    families = packet["family_packets"]
    assert isinstance(families, list)
    family = families[0]
    assert isinstance(family, dict)
    equality = family["distance_equality"]
    assert isinstance(equality, dict)
    path = equality["path"]
    assert isinstance(path, list)
    bad_step = dict(path[0])
    bad_step["next_pair"] = [0, 7]
    path[0] = bad_step

    _, errors = replay_packet(packet)

    assert any("F03: equality step 0 does not end at row center 1" in error for error in errors)
    assert any("F03: stored equality_chain mismatch" in error for error in errors)


def test_t09_minireplay_rejects_reordered_strict_witnesses() -> None:
    packet = _source_packet()
    families = packet["family_packets"]
    assert isinstance(families, list)
    family = families[0]
    assert isinstance(family, dict)
    strict = family["strict_inequality"]
    assert isinstance(strict, dict)
    strict["witness_order"] = [1, 3, 2, 8]

    _, errors = replay_packet(packet)

    assert "F03: strict_inequality outer_interval mismatch" in errors
    assert "F03: strict outer interval must properly contain inner interval" in errors


@pytest.mark.artifact
def test_t09_minireplay_payload_validates_against_source() -> None:
    packet = _source_packet()
    payload = minireplay_payload(packet)

    assert validate_payload(payload, packet) == []
    assert_expected_payload(payload)
