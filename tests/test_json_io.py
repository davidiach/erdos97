from __future__ import annotations

import json
from pathlib import Path

from erdos97.json_io import dumps_stable, load_json, write_json


def test_dumps_stable_sorts_keys_and_ends_with_single_newline() -> None:
    text = dumps_stable({"b": 1, "a": [2, 3]})
    assert text == '{\n  "a": [\n    2,\n    3\n  ],\n  "b": 1\n}\n'


def test_write_json_creates_parents_and_round_trips(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "dir" / "payload.json"
    payload = {"z": {"y": 1}, "a": [1, 2, 3], "text": "ok"}

    write_json(payload, target)

    assert load_json(target) == payload
    raw = target.read_bytes()
    assert raw == dumps_stable(payload).encode("utf-8")
    assert b"\r" not in raw


def test_load_json_matches_stdlib(tmp_path: Path) -> None:
    target = tmp_path / "payload.json"
    target.write_text('{"a": 1, "b": [true, null]}', encoding="utf-8")
    assert load_json(target) == json.loads(target.read_text(encoding="utf-8"))
