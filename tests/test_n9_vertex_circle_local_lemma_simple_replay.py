from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from erdos97.n9_vertex_circle_local_lemma_simple_replay import (
    assert_expected_simple_packet_replay,
    simple_packet_replay_payload,
)
from scripts.check_n9_vertex_circle_local_lemma_simple_replay import (
    DEFAULT_SELF_EDGE_PACKET,
    DEFAULT_STRICT_CYCLE_PACKET,
    load_artifact,
    replay_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_simple_packet_replay_expected_counts_and_scope() -> None:
    payload = replay_payload()

    assert_expected_simple_packet_replay(payload)
    assert payload["validation_status"] == "passed"
    assert payload["coverage_summary"] == {
        "covered_family_count": 16,
        "covered_assignment_count": 184,
        "self_edge_family_count": 13,
        "self_edge_assignment_count": 158,
        "strict_cycle_family_count": 3,
        "strict_cycle_assignment_count": 26,
        "expected_family_count": 16,
        "expected_assignment_count": 184,
    }
    assert payload["self_edge"]["records"][0]["obstruction_kind"] == (
        "reflexive_strict_edge"
    )
    assert payload["strict_cycle"]["records"][0]["obstruction_kind"] == (
        "directed_strict_cycle"
    )
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]


def test_simple_packet_replay_does_not_import_quotient_helper() -> None:
    source = (ROOT / "src" / "erdos97" / "n9_vertex_circle_local_lemma_simple_replay.py")
    text = source.read_text(encoding="utf-8")

    assert "from erdos97.vertex_circle_quotient_replay import" not in text
    assert "import erdos97.vertex_circle_quotient_replay" not in text


def test_simple_packet_replay_rejects_self_edge_path_drift() -> None:
    self_edge_packet = load_artifact(DEFAULT_SELF_EDGE_PACKET)
    strict_cycle_packet = load_artifact(DEFAULT_STRICT_CYCLE_PACKET)
    self_edge_packet["templates"][0]["family_records"][0]["distance_equality"]["path"][
        0
    ]["row"] = 4

    payload = simple_packet_replay_payload(self_edge_packet, strict_cycle_packet)

    assert payload["validation_status"] == "failed"
    assert (
        {"scope": "T01/F09", "error": "equality path row 4 is not selected"}
        in payload["validation_errors"]
    )
    assert any(
        error["scope"] == "self-edge coverage"
        and error["error"] == "family count 12 != 13"
        for error in payload["validation_errors"]
    )


def test_simple_packet_replay_rejects_strict_cycle_interval_drift() -> None:
    self_edge_packet = load_artifact(DEFAULT_SELF_EDGE_PACKET)
    strict_cycle_packet = load_artifact(DEFAULT_STRICT_CYCLE_PACKET)
    strict_cycle_packet["templates"][0]["family_records"][0]["cycle_steps"][0][
        "strict_inequality"
    ]["inner_interval"] = [0, 2]

    payload = simple_packet_replay_payload(self_edge_packet, strict_cycle_packet)

    assert payload["validation_status"] == "failed"
    assert (
        {
            "scope": "T10/F12",
            "error": "inner_pair does not match inner_interval",
        }
        in payload["validation_errors"]
    )
    assert any(
        error["scope"] == "strict-cycle coverage"
        and error["error"] == "family count 2 != 3"
        for error in payload["validation_errors"]
    )


def test_simple_packet_replay_reports_packet_count_drift() -> None:
    self_edge_packet = load_artifact(DEFAULT_SELF_EDGE_PACKET)
    strict_cycle_packet = load_artifact(DEFAULT_STRICT_CYCLE_PACKET)
    self_edge_packet["self_edge_family_count"] = "many"

    payload = simple_packet_replay_payload(self_edge_packet, strict_cycle_packet)

    assert payload["validation_status"] == "failed"
    assert {
        "scope": "self-edge coverage",
        "error": "packet family count is not an integer",
    } in payload["validation_errors"]


def test_simple_packet_replay_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_local_lemma_simple_replay.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert '"validation_status": "passed"' in result.stdout
    assert '"covered_assignment_count": 184' in result.stdout
