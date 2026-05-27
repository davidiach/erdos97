from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_n10_turn_row0_combined_closure import (  # noqa: E402
    CLAIM_SCOPE,
    DEFAULT_OUT,
    assert_expected_payload,
    build_payload,
)


def test_n10_turn_row0_combined_closure_matches_expected() -> None:
    payload = build_payload()

    assert_expected_payload(payload)


def test_n10_turn_row0_combined_closure_rejects_appended_claim_scope_overclaim() -> None:
    payload = build_payload()
    payload["claim_scope"] = f"{CLAIM_SCOPE} This proves n=10."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_payload(payload)


def test_n10_turn_row0_combined_closure_artifact_is_current() -> None:
    checked_in = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))

    assert checked_in == build_payload()
