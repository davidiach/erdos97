from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from erdos97.bridge_lemma_frontier import assert_expected_payload


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_bridge_lemma_frontier import DEFAULT_OUT, build_payload_from_repo  # noqa: E402


pytestmark = [pytest.mark.artifact, pytest.mark.exhaustive]


@pytest.fixture(scope="module")
def bridge_payload() -> dict[str, object]:
    return build_payload_from_repo(ROOT)


def test_bridge_lemma_frontier_counts_match_expected(
    bridge_payload: dict[str, object],
) -> None:
    assert_expected_payload(bridge_payload)


def test_bridge_lemma_frontier_artifact_is_current(
    bridge_payload: dict[str, object],
) -> None:
    checked_in = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))

    assert checked_in == bridge_payload
