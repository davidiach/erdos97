"""Synthetic policy fixtures: no fixture is mathematical evidence or a review."""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import pytest

from scripts import check_status_consistency as checker
from scripts.status_transitions import (
    load_reviewed_transition, proposal_digest, remove_approved_paragraphs,
    validate_transition_metadata,
)


def store(root: Path, path: str, data):
    content = data.encode() if isinstance(data, str) else json.dumps(data).encode()
    destination = root / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return {"path": path, "sha256": hashlib.sha256(content).hexdigest()}


def fixture_proposal(root: Path, kind="none"):
    proof = store(root, "proof.md", "SYNTHETIC TEST ONLY. This is not a proof.\n")
    overall = ("No general proof and no counterexample are claimed." if kind == "none"
               else ("We prove Erdos Problem #97." if kind == "proof"
                     else "We have a counterexample to Erdos Problem #97."))
    strongest = "Reviewed finite theorem for n <= 11." if kind == "none" else overall
    official = {"official_status": "falsifiable/open", "official_page": "https://example.invalid/97",
                "official_status_last_checked": date.today().isoformat()}
    local = {"overall_claim": overall, "strongest_result": strongest,
             "strongest_result_proof": proof["path"],
             "strongest_result_review_status": "Synthetic independent review fixture only."}
    proposal = {
        "schema": 1, "local_claim": kind, "finite_bound": 11 if kind == "none" else None,
        "problem": official, "local_repo": local,
        "evidence": {
            "proof": proof,
            "verification": store(root, "verification.json", {
                "status": "passed", "proof_sha256": proof["sha256"],
                "method": "exact_certificate", "details": "Synthetic validation fixture only."}),
            "official_source": store(root, "official.json", official),
        },
        "approved_statements": {} if kind == "none" else {name: [overall] for name in
            ("README.md", "STATE.md", "RESULTS.md", "docs/claims.md")},
    }
    save_reviewed(root, proposal)
    return proposal


def save_reviewed(root, proposal, **changes):
    review = {"decision": "accepted", "independent": True, "reviewer": "TEST FIXTURE, not a reviewer",
              "review_url": "https://example.invalid/synthetic-review",
              "reviewed_on": date.today().isoformat(), "proposal_sha256": proposal_digest(proposal)}
    review.update(changes)
    proposal["review"] = store(root, "review.json", review)
    store(root, "metadata/status_transition.json", proposal)


def test_absent_transition_does_not_promote(tmp_path):
    assert load_reviewed_transition(tmp_path) is None


@pytest.mark.parametrize("kind", ["none", "proof", "counterexample"])
def test_evidence_bound_transition_not_frozen_to_n8_or_no_solution(tmp_path, kind):
    proposal = fixture_proposal(tmp_path, kind)
    checked = load_reviewed_transition(tmp_path)
    assert checked == proposal
    validate_transition_metadata(checked, {"problem": proposal["problem"], "local_repo": proposal["local_repo"]})


@pytest.mark.parametrize("changes", [{"decision": "pending"}, {"independent": False},
                                     {"reviewer": ""}, {"review_url": ""},
                                     {"proposal_sha256": "0" * 64}])
def test_unaccepted_or_unbound_review_fails_closed(tmp_path, changes):
    proposal = fixture_proposal(tmp_path)
    save_reviewed(tmp_path, proposal, **changes)
    with pytest.raises(ValueError):
        load_reviewed_transition(tmp_path)


def test_changed_proof_rejected(tmp_path):
    fixture_proposal(tmp_path)
    (tmp_path / "proof.md").write_text("changed")
    with pytest.raises(ValueError, match="hash mismatch"):
        load_reviewed_transition(tmp_path)


def test_changed_proposal_needs_new_review(tmp_path):
    proposal = fixture_proposal(tmp_path)
    proposal["finite_bound"] = 12
    proposal["local_repo"]["strongest_result"] = "Reviewed finite theorem for n <= 12."
    store(tmp_path, "metadata/status_transition.json", proposal)
    with pytest.raises(ValueError, match="not bound"):
        load_reviewed_transition(tmp_path)


def test_metadata_drift_rejected(tmp_path):
    proposal = fixture_proposal(tmp_path)
    metadata = {"problem": dict(proposal["problem"]), "local_repo": dict(proposal["local_repo"])}
    metadata["local_repo"]["strongest_result"] = "unreviewed stronger statement"
    with pytest.raises(ValueError, match="differs"):
        validate_transition_metadata(proposal, metadata)


def test_official_status_separate_from_local_proof(tmp_path):
    proposal = fixture_proposal(tmp_path, "proof")
    assert load_reviewed_transition(tmp_path)["problem"]["official_status"] == "falsifiable/open"
    proposal["problem"]["official_status"] = "proved"
    save_reviewed(tmp_path, proposal)
    with pytest.raises(ValueError, match="separate source record"):
        load_reviewed_transition(tmp_path)
    proposal["evidence"]["official_source"] = store(tmp_path, "official.json", proposal["problem"])
    save_reviewed(tmp_path, proposal)
    assert load_reviewed_transition(tmp_path)["problem"]["official_status"] == "proved"


def test_finite_only_transition_cannot_exempt_global_claims(tmp_path):
    proposal = fixture_proposal(tmp_path)
    proposal["approved_statements"] = {"README.md": ["We prove Erdos Problem #97."]}
    save_reviewed(tmp_path, proposal)
    with pytest.raises(ValueError, match="cannot exempt"):
        load_reviewed_transition(tmp_path)


def test_counterexample_requires_exact_verification(tmp_path):
    proposal = fixture_proposal(tmp_path, "counterexample")
    proposal["evidence"]["verification"] = store(tmp_path, "verification.json", {
        "status": "passed", "method": "paper_review", "details": "synthetic",
        "proof_sha256": proposal["evidence"]["proof"]["sha256"]})
    save_reviewed(tmp_path, proposal)
    with pytest.raises(ValueError, match="insufficient"):
        load_reviewed_transition(tmp_path)


def test_reviewed_text_exemption_is_whole_paragraph_and_file_scoped(tmp_path):
    proposal = fixture_proposal(tmp_path, "proof")
    approved = proposal["local_repo"]["overall_claim"]
    assert not checker.find_forbidden_overclaim_lines(remove_approved_paragraphs(
        approved, "README.md", proposal))
    extra = approved + " This also solves the problem."
    assert checker.find_forbidden_overclaim_lines(remove_approved_paragraphs(extra, "README.md", proposal))
    assert remove_approved_paragraphs(approved, "unrelated.md", proposal) == approved


def test_top_level_status_uses_reviewed_finite_bound(tmp_path, monkeypatch):
    proposal = fixture_proposal(tmp_path)
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    summary = (proposal["local_repo"]["overall_claim"] + "\n\n"
               + proposal["local_repo"]["strongest_result"] + "\n\nfalsifiable/open\n\nmetadata/erdos97.yaml")
    for name in ("README.md", "STATE.md", "RESULTS.md"):
        (tmp_path / name).write_text(summary)
    checker.validate_top_level_status()
    (tmp_path / "STATE.md").write_text(summary.replace("n <= 11", "n <= 12"))
    with pytest.raises(SystemExit):
        checker.validate_top_level_status()


def test_without_transition_original_overclaim_detector_still_applies():
    assert checker.find_forbidden_overclaim_lines("We prove Erdos Problem #97.")
    assert not checker.find_forbidden_overclaim_lines("We do not prove Erdos Problem #97.")


def test_path_escape_rejected(tmp_path):
    proposal = fixture_proposal(tmp_path)
    proposal["evidence"]["proof"]["path"] = "../outside.md"
    save_reviewed(tmp_path, proposal)
    with pytest.raises(ValueError, match="repo-relative"):
        load_reviewed_transition(tmp_path)


def test_reviewed_status_cannot_be_a_prefix_of_a_stronger_paragraph(tmp_path, monkeypatch, capsys):
    proposal = fixture_proposal(tmp_path)
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    reviewed = proposal["local_repo"]["strongest_result"]
    text = "\n\n".join([proposal["local_repo"]["overall_claim"], reviewed,
                           proposal["problem"]["official_status"]])
    checker.check_transition_text("README.md", text, proposal)
    stronger = text.replace(reviewed, reviewed + " The accepted theorem actually holds for n <= 12.")
    with pytest.raises(SystemExit):
        checker.check_transition_text("README.md", stronger, proposal)
    assert "whole paragraph" in capsys.readouterr().err
