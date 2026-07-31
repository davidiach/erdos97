from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts"
    / "exploration"
    / "screen_sparse_full_cone_c25_persistent_escapes.py"
)
SPEC = importlib.util.spec_from_file_location(
    "sparse_full_cone_c25_persistent_escape_screen",
    SCRIPT,
)
assert SPEC is not None and SPEC.loader is not None
SCREEN = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SCREEN
SPEC.loader.exec_module(SCREEN)

SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_residual_seed_probe_2026-07-29"
    / "summary.json"
)
ARTIFACT = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_persistent_escape_screen_2026-07-30"
    / "summary.json"
)


def artifact_payload() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_selects_the_two_predeclared_transfer_cegar_targets() -> None:
    _, _, cegar, _ = SCREEN.load_source(SOURCE)
    models = SCREEN.target_models(cegar, SCREEN.DEFAULT_TARGET_INDICES)

    assert [model["probe_model_index"] for model in models] == [0, 1]
    assert all(model["lightweight_filters"]["survives"] for model in models)
    assert all(not model["seed_orbit_matches"] for model in models)


def test_targets_match_none_of_the_eleven_exact_seed_orbits() -> None:
    _, compression, cegar, transfer = SCREEN.load_source(SOURCE)
    _, _, packets = SCREEN.reconstruct_seed_packets(compression, transfer)
    models = SCREEN.target_models(cegar, SCREEN.DEFAULT_TARGET_INDICES)

    assert {name: len(orbits) for name, orbits in packets.items()} == {
        "transferred_only": 3,
        "transferred_plus_width3": 4,
        "transferred_plus_all_residuals": 11,
    }
    for model in models:
        audit = SCREEN.target_seed_audit(model, packets)
        assert audit["all_eleven_seed_orbit_match_count"] == 0
        assert all(not matches for matches in audit["seed_packet_matches"].values())


def test_stored_targets_have_two_exact_positive_circuits() -> None:
    payload = artifact_payload()
    records = payload["records"]

    assert [record["target_id"] for record in records] == ["probe:0", "probe:1"]
    assert [record["classification"] for record in records] == [
        "EXACT_POSITIVE_ZERO_SUM_CERTIFICATE",
        "EXACT_POSITIVE_ZERO_SUM_CERTIFICATE",
    ]
    assert [record["positive_inequalities"] for record in records] == [201, 196]
    assert [record["unique_ordered_quad_count"] for record in records] == [201, 196]
    assert payload["decision"] == (
        "CONTINUE_C25_CLAUSE_ROUTE_WITH_EXACT_POSITIVE_CIRCUITS"
    )


def test_stored_persistent_escape_screen_replays_exactly() -> None:
    assert SCREEN.check_payload(artifact_payload()) == {
        "status": "OK",
        "verified_target_orders": 2,
        "verified_exact_positive_certificates": 2,
        "verified_exact_integer_separators": 0,
        "recorded_unresolved_numerical_screens": 0,
        "verified_seed_orbits": 11,
        "verified_exact_affine_seed_images": 275,
        "decision": "CONTINUE_C25_CLAUSE_ROUTE_WITH_EXACT_POSITIVE_CIRCUITS",
    }

def test_checker_rejects_fabricated_screen_configuration() -> None:
    payload = artifact_payload()
    payload["configuration"]["retry_seed"] += 1

    with pytest.raises(AssertionError, match="screen configuration drifted"):
        SCREEN.check_payload(payload)


def test_checker_rejects_substituted_source_artifact(tmp_path: Path) -> None:
    substitute = tmp_path / "summary.json"
    substitute.write_bytes(SOURCE.read_bytes())
    payload = artifact_payload()
    payload["source_augmentation_artifact"] = str(substitute)
    payload["source_augmentation_sha256"] = SCREEN.file_sha256(substitute)

    with pytest.raises(AssertionError, match="source artifact drifted"):
        SCREEN.check_payload(payload)
