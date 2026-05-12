from __future__ import annotations

import json
from pathlib import Path

import pytest

from erdos97.n9_t01_self_edge_minireplay import (
    assert_expected_payload,
    minireplay_payload,
    replay_packet,
    validate_payload,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "certificates" / "n9_vertex_circle_t01_self_edge_lemma_packet.json"


def _source_packet() -> dict[str, object]:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_t01_minireplay_replays_local_self_edge() -> None:
    packet = _source_packet()
    replay, errors = replay_packet(packet)

    assert errors == []
    assert replay["equality_chain"] == [[1, 8], [0, 1], [0, 2], [1, 2]]
    assert replay["self_edge_contradiction"] is True
    assert replay["strict_inequality"] == {
        "row": 0,
        "witness_order": [1, 2, 4, 8],
        "outer_pair": [1, 8],
        "inner_pair": [1, 2],
        "outer_interval": [0, 3],
        "inner_interval": [0, 1],
        "outer_span": 3,
        "inner_span": 1,
    }


def test_t01_minireplay_rejects_broken_equality_step() -> None:
    packet = _source_packet()
    equality = packet["distance_equality"]
    assert isinstance(equality, dict)
    path = equality["path"]
    assert isinstance(path, list)
    bad_step = dict(path[0])
    bad_step["next_pair"] = [3, 5]
    path[0] = bad_step

    _, errors = replay_packet(packet)

    assert any("does not end at row center 1" in error for error in errors)
    assert any("stored equality_chain mismatch" in error for error in errors)


def test_t01_minireplay_reports_malformed_pairs_without_crashing() -> None:
    packet = _source_packet()
    equality = packet["distance_equality"]
    assert isinstance(equality, dict)
    equality["start_pair"] = [1]

    _, errors = replay_packet(packet)

    assert "distance_equality.start_pair must be a two-element list" in errors
    assert any("does not start at row center" in error for error in errors)


@pytest.mark.artifact
def test_t01_minireplay_payload_validates_against_source() -> None:
    packet = _source_packet()
    payload = minireplay_payload(packet)

    assert validate_payload(payload, packet) == []
    assert_expected_payload(payload)
