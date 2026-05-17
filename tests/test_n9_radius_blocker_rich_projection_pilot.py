from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_n9_radius_blocker_rich_projection_pilot import (  # noqa: E402
    DEFAULT_OUT,
    assert_expected_payload,
    build_payload,
)


def test_n9_radius_blocker_rich_projection_pilot_matches_expected() -> None:
    payload = build_payload()

    assert_expected_payload(payload)


def test_n9_radius_blocker_rich_projection_pilot_artifact_is_current() -> None:
    checked_in = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))

    assert checked_in == build_payload()
