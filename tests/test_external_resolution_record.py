"""Consistency checks for a dated external report, not mathematical verification."""
from __future__ import annotations

import json
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "metadata/external-resolution-2026-09-14.json"


def load_record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def test_external_record_has_pinned_attributed_sources() -> None:
    record = load_record()
    assert record["schema"] == 1
    assert record["status"] == "EXTERNAL_NEGATIVE_RESOLUTION"
    assert record["problem_number"] == 97
    assert record["released_on"] == "2026-09-13"
    assert record["recorded_on"] == "2026-09-14"
    assert record["authors"] == ["Liam Kruer", "Jensen Kohlmeyer", "Liam Price"]
    assert record["source_repository"] == "https://github.com/Leeham06972452/erdos-96-97"
    assert re.fullmatch(r"[0-9a-f]{40}", record["source_commit"])
    for source in record["sources"].values():
        assert source["path"]
        assert re.fullmatch(r"[0-9a-f]{40}", source["git_blob"])
    assert "Proof.erdos_97_false" in record["formal_entry_points"]


def test_external_record_does_not_invent_local_acceptance() -> None:
    boundary = load_record()["verification_boundary"]
    for key in (
        "independent_local_lean_replay", "independent_mathematical_acceptance_recorded",
        "original_discovery_claimed", "accepted_local_claims_changed",
    ):
        assert boundary[key] is False
    assert boundary["source_identity_and_author_attribution_checked"] is True
    assert boundary["upstream_job_step_status_checked"] is True


def test_unsuccessful_website_refresh_is_not_a_successful_check() -> None:
    record = load_record()
    site = record["canonical_website"]
    assert site["retrieval_succeeded"] is False
    assert site["current_label"] is None
    assert site["last_successful_check_preserved"] < site["refresh_attempted_on"]
    # This dated receipt records the old check without requiring future metadata
    # to remain permanently frozen at the old date.
    assert site["last_successful_check_preserved"] == "2026-07-09"
    metadata = yaml.safe_load((ROOT / record["local_claims_metadata"]).read_text())
    assert metadata["problem"]["official_status_last_checked"] >= site["last_successful_check_preserved"]


def test_current_documents_link_the_external_record() -> None:
    record = load_record()
    note = ROOT / record["documentation"]
    text = note.read_text(encoding="utf-8")
    assert record["source_commit"] in text
    assert record["authors_cardinality_bound"] in text
    for path in ("README.md", "STATE.md", "RESULTS.md", "docs/claims.md"):
        content = (ROOT / path).read_text(encoding="utf-8")
        assert record["status"] in content
        assert note.name in content


def test_agent_scope_preserves_history_without_resuming_old_queue() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "Do not start further affirmative-proof attempts" in text
    assert "Preserve existing proofs" in text
    assert "historical material, not current task authorization" in text
