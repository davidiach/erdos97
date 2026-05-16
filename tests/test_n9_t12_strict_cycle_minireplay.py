from __future__ import annotations

import json
from pathlib import Path

import pytest

from erdos97.n9_t12_strict_cycle_minireplay import (
    assert_expected_payload,
    minireplay_payload,
    replay_packet,
    validate_payload,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "certificates" / "n9_vertex_circle_t12_strict_cycle_lemma_packet.json"


def _source_packet() -> dict[str, object]:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_t12_minireplay_replays_local_strict_cycle() -> None:
    packet = _source_packet()
    replay, errors = replay_packet(packet)

    assert errors == []
    assert replay["family_ids"] == ["F16"]
    assert replay["assignment_count"] == 2
    assert replay["assignment_counts"] == {"F16": 2}
    assert replay["core_centers"] == [0, 1, 2, 3, 4, 8]
    assert replay["cycle_length"] == 3
    assert replay["strict_cycle_contradiction"] is True
    steps = replay["cycle_steps"]
    assert isinstance(steps, list)
    assert [step["equality_chain_to_next_outer_pair"] for step in steps] == [
        [[0, 8], [2, 8]],
        [[2, 4], [1, 4], [1, 7]],
        [[1, 3], [0, 3]],
    ]
    assert steps[0]["strict_inequality"] == {
        "row": 2,
        "witness_order": [3, 5, 8, 0],
        "outer_pair": [0, 3],
        "inner_pair": [0, 8],
        "outer_interval": [0, 3],
        "inner_interval": [2, 3],
        "outer_span": 3,
        "inner_span": 1,
    }
    assert steps[1]["strict_inequality"] == {
        "row": 1,
        "witness_order": [2, 4, 7, 8],
        "outer_pair": [2, 8],
        "inner_pair": [2, 4],
        "outer_interval": [0, 3],
        "inner_interval": [0, 1],
        "outer_span": 3,
        "inner_span": 1,
    }
    assert steps[2]["strict_inequality"] == {
        "row": 0,
        "witness_order": [1, 3, 6, 7],
        "outer_pair": [1, 7],
        "inner_pair": [1, 3],
        "outer_interval": [0, 3],
        "inner_interval": [0, 1],
        "outer_span": 3,
        "inner_span": 1,
    }


def test_t12_minireplay_rejects_broken_cycle_connector() -> None:
    packet = _source_packet()
    family = packet["family_packets"][0]  # type: ignore[index]
    step = family["cycle_steps"][1]  # type: ignore[index]
    equality = step["equality_to_next_outer_pair"]  # type: ignore[index]
    equality["end_pair"] = [1, 8]  # type: ignore[index]

    _, errors = replay_packet(packet)

    assert any("not [1, 8]" in error for error in errors)
    assert "strict inequalities and equality connectors do not close a cycle" in errors


def test_t12_minireplay_reports_malformed_pairs_without_crashing() -> None:
    packet = _source_packet()
    family = packet["family_packets"][0]  # type: ignore[index]
    step = family["cycle_steps"][0]  # type: ignore[index]
    equality = step["equality_to_next_outer_pair"]  # type: ignore[index]
    equality["start_pair"] = [0]  # type: ignore[index]

    _, errors = replay_packet(packet)

    assert any("start_pair must be a two-element list" in error for error in errors)
    assert any("does not start at row center" in error for error in errors)


def test_t12_minireplay_rejects_reordered_strict_witnesses() -> None:
    packet = _source_packet()
    family = packet["family_packets"][0]  # type: ignore[index]
    step = family["cycle_steps"][0]  # type: ignore[index]
    strict = step["strict_inequality"]  # type: ignore[index]
    strict["witness_order"] = [5, 8, 0, 3]  # type: ignore[index]
    strict["outer_interval"] = [0, 3]  # type: ignore[index]
    strict["inner_interval"] = [1, 2]  # type: ignore[index]
    strict["outer_span"] = 3  # type: ignore[index]
    strict["inner_span"] = 1  # type: ignore[index]

    _, errors = replay_packet(packet)

    assert "cycle_steps[0] strict_inequality witness_order changed" in errors
    assert "strict inequalities and equality connectors do not close a cycle" in errors


@pytest.mark.artifact
def test_t12_minireplay_payload_validates_against_source() -> None:
    packet = _source_packet()
    payload = minireplay_payload(packet)

    assert validate_payload(payload, packet) == []
    assert_expected_payload(payload)
