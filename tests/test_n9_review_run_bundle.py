from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from scripts.check_n9_review_run_bundle import (
    build_bundle_payload,
    load_bundle,
    render_markdown,
    run_manifest_commands,
    summary_payload,
    validate_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "metadata" / "n9_review_run_bundle.yaml"


def test_n9_review_run_bundle_is_valid() -> None:
    payload = load_bundle(BUNDLE)

    errors = validate_bundle(payload)

    assert errors == []


def test_n9_review_run_bundle_payload_contains_expected_layers() -> None:
    payload = load_bundle(BUNDLE)

    bundle = build_bundle_payload(payload)

    assert len(bundle["routes"]) == 5
    assert len(bundle["command_records"]) == 19
    assert len(bundle["review_gates"]) == 6
    assert len(bundle["infrastructure_gates"]) == 2
    assert len(bundle["evidence_records"]) == 19


def test_n9_review_run_bundle_rejects_missing_capture_field() -> None:
    payload = deepcopy(load_bundle(BUNDLE))
    payload["capture_contract"]["required_record_fields"].remove("stdout_sha256")

    errors = validate_bundle(payload)

    assert (
        "capture_contract.required_record_fields missing 'stdout_sha256'"
        in errors
    )


def test_n9_review_run_bundle_rejects_manifest_without_pointer() -> None:
    payload = load_bundle(BUNDLE)
    manifest = deepcopy(build_bundle_payload(payload)["routes"])
    candidate_manifest = {
        "schema": "ignored",
        "routes": manifest,
    }

    errors = validate_bundle(payload, candidate_manifest=candidate_manifest)

    assert (
        "candidate manifest must reference metadata/n9_review_run_bundle.yaml"
        in errors
    )


def test_n9_review_run_bundle_summary_is_static_by_default() -> None:
    payload = load_bundle(BUNDLE)

    summary = summary_payload(payload, [], run_capture_enabled=False)

    assert summary["command_count"] == 19
    assert summary["evidence_record_count"] == 19
    assert summary["run_capture_enabled"] is False
    assert summary["run_record_count"] == 0


def test_n9_review_run_bundle_renders_markdown() -> None:
    payload = load_bundle(BUNDLE)

    markdown = render_markdown(payload, [])

    assert "# n=9 Review Run Bundle" in markdown
    assert "## Run Capture Contract" in markdown
    assert "`n9_review_run_bundle`" in markdown


def test_n9_review_run_bundle_can_capture_a_small_command() -> None:
    payload = load_bundle(BUNDLE)
    manifest = {
        "routes": [
            {
                "id": "sample_route",
                "title": "Sample route",
                "commands": [
                    {
                        "id": "sample_command",
                        "command": (
                            "python -c \"import json; "
                            "print(json.dumps({'validation_status': 'passed'}))\""
                        ),
                    }
                ],
            }
        ]
    }
    matrix = {
        "evidence_records": [
            {
                "id": "sample_command",
                "command_id": "sample_command",
                "output_format": "json",
                "expectations": [
                    {"path": "validation_status", "equals": "passed"},
                ],
            }
        ]
    }

    records, errors = run_manifest_commands(
        payload,
        candidate_manifest=manifest,
        evidence_matrix=matrix,
    )

    assert errors == []
    assert len(records) == 1
    assert records[0]["validation_status"] == "passed"
    assert len(records[0]["stdout_sha256"]) == 64
