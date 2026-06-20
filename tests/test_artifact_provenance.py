from __future__ import annotations

import json
from pathlib import Path

from scripts.check_artifact_provenance import (
    TRACKED_ARTIFACT_COVERAGE_GLOBS,
    command_mentions_path,
    command_outputs_path,
    command_replays_path,
    load_manifest,
    sha256_file,
    validate_manifest,
)

ROOT = Path(__file__).resolve().parents[1]


def test_generated_artifact_manifest_is_valid() -> None:
    manifest = ROOT / "metadata" / "generated_artifacts.yaml"

    errors = validate_manifest(load_manifest(manifest), check_tracked_coverage=True)

    assert errors == []


def test_tracked_artifact_coverage_includes_legacy_certificate_root() -> None:
    assert "data/certificates/**/*.json" in TRACKED_ARTIFACT_COVERAGE_GLOBS
    assert "certificates/**/*.json" in TRACKED_ARTIFACT_COVERAGE_GLOBS


def artifact_metadata(path: Path) -> dict[str, object]:
    return {"sha256": sha256_file(path), "size_bytes": path.stat().st_size}


def replay_manifest(
    tmp_path: Path,
    *,
    command: str,
    check_command: str | None,
) -> dict[str, object]:
    artifact = tmp_path / "artifact.json"
    generator = tmp_path / "generator.py"
    checker = tmp_path / "checker.py"
    artifact.write_text(json.dumps({"status": "GOOD"}) + "\n", encoding="utf-8")
    generator.write_text("print('ok')\n", encoding="utf-8")
    checker.write_text("print('ok')\n", encoding="utf-8")
    entry = {
        "id": "sample",
        "path": str(artifact),
        "kind": "test",
        "generator": str(generator),
        "command": command,
        "checker": str(checker),
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
    if check_command is not None:
        entry["check_command"] = check_command
    return {
        "schema": "erdos97.generated_artifacts.v1",
        "claim_scope": "test manifest only",
        "artifacts": [entry],
    }


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


def test_manifest_rejects_explicit_write_path_without_check_replay(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.json"
    generator = tmp_path / "generator.py"
    checker = tmp_path / "checker.py"
    manifest = replay_manifest(
        tmp_path,
        command=f"python {generator} --out {artifact}",
        check_command=f"python {checker} --check",
    )

    errors = validate_manifest(manifest)

    assert any("must replay explicitly generated artifact path" in error for error in errors)


def test_manifest_rejects_equals_write_path_without_check_replay(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.json"
    generator = tmp_path / "generator.py"
    checker = tmp_path / "checker.py"
    manifest = replay_manifest(
        tmp_path,
        command=f"python {generator} --out={artifact}",
        check_command=f"python {checker} --check",
    )

    errors = validate_manifest(manifest)

    assert any("must replay explicitly generated artifact path" in error for error in errors)


def test_manifest_rejects_explicit_write_path_without_check_command(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.json"
    generator = tmp_path / "generator.py"
    manifest = replay_manifest(
        tmp_path,
        command=f"python {generator} --out {artifact}",
        check_command=None,
    )

    errors = validate_manifest(manifest)

    assert any("must replay explicitly generated artifact path" in error for error in errors)


def test_manifest_rejects_check_path_without_replay_flag(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.json"
    generator = tmp_path / "generator.py"
    checker = tmp_path / "checker.py"
    manifest = replay_manifest(
        tmp_path,
        command=f"python {generator} --out {artifact}",
        check_command=f"python {checker} --baseline {artifact} --check",
    )

    errors = validate_manifest(manifest)

    assert any("must replay explicitly generated artifact path" in error for error in errors)


def test_manifest_accepts_explicit_write_path_with_check_replay(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.json"
    generator = tmp_path / "generator.py"
    checker = tmp_path / "checker.py"
    manifest = replay_manifest(
        tmp_path,
        command=f"python {generator} --out {artifact}",
        check_command=f"python {checker} --artifact={artifact} --check",
    )

    errors = validate_manifest(manifest)

    assert errors == []


def test_command_path_detection_accepts_common_artifact_path_forms() -> None:
    artifact = ROOT / "data/certificates/example.json"

    assert command_mentions_path(
        "python generator.py --out=data/certificates/example.json",
        "data/certificates/example.json",
    )
    assert command_outputs_path(
        "python generator.py --out=data/certificates/example.json",
        "data/certificates/example.json",
    )
    assert command_outputs_path(
        "python generator.py --out ./data/certificates/example.json",
        "data/certificates/example.json",
    )
    assert command_outputs_path(
        f"python generator.py --out {artifact}",
        "data/certificates/example.json",
    )
    assert command_outputs_path(
        "python generator.py >data/certificates/example.json",
        "data/certificates/example.json",
    )
    assert not command_outputs_path(
        "python checker.py --artifact data/certificates/example.json --check",
        "data/certificates/example.json",
    )
    assert command_replays_path(
        "python checker.py --artifact=./data/certificates/example.json --check",
        "data/certificates/example.json",
    )
    assert command_replays_path(
        f"python checker.py --artifact {artifact} --check",
        "data/certificates/example.json",
    )
    assert not command_replays_path(
        "python checker.py --baseline data/certificates/example.json --check",
        "data/certificates/example.json",
    )


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
