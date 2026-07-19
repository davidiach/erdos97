from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from scripts.check_n9_candidate_review_manifest import load_manifest
from scripts.check_n9_review_gate_ledger import load_ledger, validate_ledger


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "metadata" / "n9_review_gate_ledger.yaml"
MANIFEST = ROOT / "metadata" / "n9_candidate_review.yaml"


def test_n9_review_gate_ledger_is_valid() -> None:
    payload = load_ledger(LEDGER)

    errors = validate_ledger(payload)

    assert errors == []


def test_n9_review_gate_ledger_rejects_outcome_drift() -> None:
    payload = deepcopy(load_ledger(LEDGER))
    payload["review_outcomes"][0]["required_gates"] = ["frontier_enumeration"]

    errors = validate_ledger(payload)

    assert any("accepted_vertex_circle_route" in error for error in errors)


def test_n9_review_gate_ledger_pins_kalmanson_primary_route() -> None:
    payload = deepcopy(load_ledger(LEDGER))
    outcome = next(
        item
        for item in payload["review_outcomes"]
        if item["id"] == "accepted_kalmanson_route"
    )
    outcome["required_gates"].remove("kalmanson_geometry")

    errors = validate_ledger(payload)

    assert any("accepted_kalmanson_route" in error for error in errors)


def test_n9_review_gate_ledger_rejects_unknown_reduction_step() -> None:
    payload = deepcopy(load_ledger(LEDGER))
    payload["review_gates"][0]["reduction_steps"].append("A12")

    errors = validate_ledger(payload)

    assert any("references missing 'A12'" in error for error in errors)


def test_n9_review_gate_ledger_rejects_unknown_evidence_command() -> None:
    payload = deepcopy(load_ledger(LEDGER))
    payload["review_gates"][0]["evidence_commands"].append("missing_command")

    errors = validate_ledger(payload)

    assert any("references unknown command 'missing_command'" in error for error in errors)


def test_n9_review_gate_ledger_covers_manifest_review_gates() -> None:
    payload = load_ledger(LEDGER)
    manifest = deepcopy(load_manifest(MANIFEST))
    manifest["review_gates"].append(
        {
            "id": "new_review_gate",
            "review_requirement": "Synthetic test gate.",
            "still_open": True,
        }
    )

    errors = validate_ledger(payload, candidate_manifest=manifest)

    assert "candidate manifest review gate 'new_review_gate' is not covered" in errors
