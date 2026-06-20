from __future__ import annotations

import json
from pathlib import Path

from scripts.check_artifact_provenance import (
    TRACKED_ARTIFACT_COVERAGE_GLOBS,
    load_manifest,
    sha256_file,
    validate_manifest,
)


def test_generated_artifact_manifest_is_valid() -> None:
    repo = Path(__file__).resolve().parents[1]
    manifest = repo / "metadata" / "generated_artifacts.yaml"

    errors = validate_manifest(load_manifest(manifest), check_tracked_coverage=True)

    assert errors == []


def test_tracked_artifact_coverage_includes_legacy_certificate_root() -> None:
    assert "data/certificates/**/*.json" in TRACKED_ARTIFACT_COVERAGE_GLOBS
    assert "certificates/**/*.json" in TRACKED_ARTIFACT_COVERAGE_GLOBS


def artifact_metadata(path: Path) -> dict[str, object]:
    return {"sha256": sha256_file(path), "size_bytes": path.stat().st_size}


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
                **artifact_metadata(artifact),
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
                **artifact_metadata(artifact),
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
                **artifact_metadata(artifact),
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


def test_manifest_accepts_exact_certificate_diagnostic_trust(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.json"
    generator = tmp_path / "generator.py"
    artifact.write_text(json.dumps({"type": "diagnostic"}), encoding="utf-8")
    generator.write_text("print('ok')\n", encoding="utf-8")
    manifest = {
        "schema": "erdos97.generated_artifacts.v1",
        "claim_scope": "test manifest only",
        "artifacts": [
            {
                "id": "sample",
                "path": str(artifact),
                **artifact_metadata(artifact),
                "kind": "certificate_diagnostic_artifact",
                "generator": str(generator),
                "command": f"python {generator}",
                "direct_edit_allowed": False,
                "provenance_mode": "manifest_only_legacy",
                "trust": "EXACT_CERTIFICATE_DIAGNOSTIC",
                "claim_scope": "test diagnostic only",
                "json_top_level_type": "object",
                "expected_json": {"type": "diagnostic"},
                "forbidden_claims": ["general proof"],
            }
        ],
    }

    errors = validate_manifest(manifest)

    assert errors == []


def test_manifest_accepts_matching_file_metadata(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.json"
    generator = tmp_path / "generator.py"
    artifact.write_text(json.dumps({"status": "GOOD"}) + "\n", encoding="utf-8")
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
                "sha256": sha256_file(artifact),
                "size_bytes": artifact.stat().st_size,
                "expected_json": {"status": "GOOD"},
                "forbidden_claims": ["general proof"],
            }
        ],
    }

    errors = validate_manifest(manifest)

    assert errors == []


def test_manifest_rejects_mismatched_file_metadata(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.json"
    generator = tmp_path / "generator.py"
    artifact.write_text(json.dumps({"status": "GOOD"}) + "\n", encoding="utf-8")
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
                "sha256": "0" * 64,
                "size_bytes": artifact.stat().st_size + 1,
                "expected_json": {"status": "GOOD"},
                "forbidden_claims": ["general proof"],
            }
        ],
    }

    errors = validate_manifest(manifest)

    assert any(".sha256 is" in error for error in errors)
    assert any(".size_bytes is" in error for error in errors)
