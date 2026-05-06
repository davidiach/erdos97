from __future__ import annotations

import json
from pathlib import Path

from scripts.check_artifact_provenance import load_manifest, validate_manifest


def test_generated_artifact_manifest_is_valid() -> None:
    repo = Path(__file__).resolve().parents[1]
    manifest = repo / "metadata" / "generated_artifacts.yaml"

    errors = validate_manifest(load_manifest(manifest))

    assert errors == []


def test_manifest_rejects_mismatched_expected_json(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.json"
    generator = tmp_path / "generator.py"
    artifact.write_text(json.dumps({"status": "BAD"}), encoding="utf-8")
    generator.write_text("print('ok')\n", encoding="utf-8")
    manifest = {
        "schema": "erdos97.generated_artifacts.v1",
        "claim_scope": "test manifest only",
        "artifacts": [
            {
                "id": "sample",
                "path": str(artifact),
                "kind": "test",
                "generator": str(generator),
                "command": f"python {generator}",
                "direct_edit_allowed": False,
                "provenance_mode": "manifest_only_legacy",
                "trust": "EXACT_OBSTRUCTION",
                "claim_scope": "test artifact only",
                "json_top_level_type": "object",
                "expected_json": {"status": "GOOD"},
                "forbidden_claims": ["general proof"],
            }
        ],
    }

    errors = validate_manifest(manifest)

    assert any("'status' is 'BAD', expected 'GOOD'" in error for error in errors)


def test_manifest_rejects_ambiguous_review_forbidden_claim(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.json"
    generator = tmp_path / "generator.py"
    artifact.write_text(json.dumps({"status": "GOOD"}), encoding="utf-8")
    generator.write_text("print('ok')\n", encoding="utf-8")
    manifest = {
        "schema": "erdos97.generated_artifacts.v1",
        "claim_scope": "test manifest only",
        "artifacts": [
            {
                "id": "sample",
                "path": str(artifact),
                "kind": "test",
                "generator": str(generator),
                "command": f"python {generator}",
                "direct_edit_allowed": False,
                "provenance_mode": "manifest_only_legacy",
                "trust": "EXACT_OBSTRUCTION",
                "claim_scope": "test artifact only",
                "json_top_level_type": "object",
                "forbidden_claims": ["independent external review"],
            }
        ],
    }

    errors = validate_manifest(manifest)

    assert any("ambiguous" in error for error in errors)


def test_manifest_rejects_missing_optional_checker(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.json"
    generator = tmp_path / "generator.py"
    artifact.write_text(json.dumps({"status": "GOOD"}), encoding="utf-8")
    generator.write_text("print('ok')\n", encoding="utf-8")
    manifest = {
        "schema": "erdos97.generated_artifacts.v1",
        "claim_scope": "test manifest only",
        "artifacts": [
            {
                "id": "sample",
                "path": str(artifact),
                "kind": "test",
                "generator": str(generator),
                "command": f"python {generator}",
                "checker": str(tmp_path / "missing_checker.py"),
                "check_command": "python missing_checker.py --check",
                "direct_edit_allowed": False,
                "provenance_mode": "manifest_only_legacy",
                "trust": "EXACT_OBSTRUCTION",
                "claim_scope": "test artifact only",
                "json_top_level_type": "object",
                "forbidden_claims": ["general proof"],
            }
        ],
    }

    errors = validate_manifest(manifest)

    assert any("checker does not exist" in error for error in errors)
