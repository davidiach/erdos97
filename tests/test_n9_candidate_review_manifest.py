from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from scripts.check_n9_candidate_review_manifest import (
    flatten_route_commands,
    load_manifest,
    make_target_commands,
    validate_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "metadata" / "n9_candidate_review.yaml"


def test_n9_candidate_review_manifest_is_valid() -> None:
    payload = load_manifest(MANIFEST)

    errors = validate_manifest(payload)

    assert errors == []


def test_n9_candidate_review_manifest_commands_match_make_target() -> None:
    payload = load_manifest(MANIFEST)

    assert flatten_route_commands(payload) == make_target_commands("verify-n9-candidate")


def test_n9_candidate_review_manifest_rejects_makefile_drift() -> None:
    payload = load_manifest(MANIFEST)
    drifted_commands = make_target_commands("verify-n9-candidate")[:-1]

    errors = validate_manifest(payload, makefile_commands=drifted_commands)

    assert "manifest route commands do not match Makefile verify-n9-candidate commands" in errors


def test_n9_candidate_review_manifest_requires_forbidden_promotions() -> None:
    payload = deepcopy(load_manifest(MANIFEST))
    payload["forbidden_promotions"] = ["general proof of Erdos Problem #97"]

    errors = validate_manifest(payload)

    assert any("forbidden_promotions missing" in error for error in errors)


def test_n9_candidate_review_manifest_requires_review_gate_ledger() -> None:
    payload = deepcopy(load_manifest(MANIFEST))
    payload["review_gate_ledger"] = "metadata/other.yaml"

    errors = validate_manifest(payload)

    assert "review_gate_ledger must be 'metadata/n9_review_gate_ledger.yaml'" in errors


def test_n9_candidate_review_manifest_requires_review_evidence_matrix() -> None:
    payload = deepcopy(load_manifest(MANIFEST))
    payload["review_evidence_matrix"] = "metadata/other.yaml"

    errors = validate_manifest(payload)

    assert (
        "review_evidence_matrix must be 'metadata/n9_review_evidence_matrix.yaml'"
        in errors
    )


def test_n9_candidate_review_manifest_requires_review_dossier() -> None:
    payload = deepcopy(load_manifest(MANIFEST))
    payload["review_dossier"] = "metadata/other.yaml"

    errors = validate_manifest(payload)

    assert "review_dossier must be 'metadata/n9_review_dossier.yaml'" in errors


def test_n9_candidate_review_manifest_requires_review_run_bundle() -> None:
    payload = deepcopy(load_manifest(MANIFEST))
    payload["review_run_bundle"] = "metadata/other.yaml"

    errors = validate_manifest(payload)

    assert (
        "review_run_bundle must be 'metadata/n9_review_run_bundle.yaml'"
        in errors
    )


def test_n9_candidate_review_manifest_pins_summary_json_review_surfaces() -> None:
    payload = deepcopy(load_manifest(MANIFEST))
    command = payload["routes"][2]["commands"][1]
    command["command"] = command["command"].replace(" --summary-json", " --json")

    errors = validate_manifest(payload)

    assert any("must use --summary-json" in error for error in errors)
