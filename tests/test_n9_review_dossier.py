from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from scripts.check_n9_review_dossier import (
    build_dossier_payload,
    load_dossier,
    render_markdown,
    validate_dossier,
)


ROOT = Path(__file__).resolve().parents[1]
DOSSIER = ROOT / "metadata" / "n9_review_dossier.yaml"


def test_n9_review_dossier_is_valid() -> None:
    payload = load_dossier(DOSSIER)

    errors = validate_dossier(payload)

    assert errors == []


def test_n9_review_dossier_payload_contains_expected_layers() -> None:
    payload = load_dossier(DOSSIER)

    dossier = build_dossier_payload(payload)

    assert len(dossier["routes"]) == 5
    assert len(dossier["review_gates"]) == 6
    assert len(dossier["infrastructure_gates"]) == 2
    assert len(dossier["evidence_records"]) == 17


def test_n9_review_dossier_rejects_missing_section_id() -> None:
    payload = deepcopy(load_dossier(DOSSIER))
    payload["sections"][2]["required_ids"].append("missing_gate")

    errors = validate_dossier(payload)

    assert any("missing 'missing_gate'" in error for error in errors)


def test_n9_review_dossier_rejects_missing_review_question() -> None:
    payload = deepcopy(load_dossier(DOSSIER))
    payload["review_questions"] = payload["review_questions"][:-1]

    errors = validate_dossier(payload)

    assert "review_questions missing gate 'kalmanson_corroboration'" in errors


def test_n9_review_dossier_rejects_missing_decision_field() -> None:
    payload = deepcopy(load_dossier(DOSSIER))
    payload["decision_fields"].remove("precise_gaps")

    errors = validate_dossier(payload)

    assert "decision_fields missing 'precise_gaps'" in errors


def test_n9_review_dossier_renders_markdown() -> None:
    payload = load_dossier(DOSSIER)

    markdown = render_markdown(payload, [])

    assert "# n=9 Reviewer Dossier" in markdown
    assert "## Review Gate Worksheet" in markdown
    assert "`frontier_enumeration`" in markdown
