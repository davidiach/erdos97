from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts"
    / "exploration"
    / "probe_sparse_full_cone_c25_residual_seed_augmentation.py"
)
SPEC = importlib.util.spec_from_file_location(
    "sparse_full_cone_c25_residual_seed_augmentation",
    SCRIPT,
)
assert SPEC is not None and SPEC.loader is not None
PROBE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PROBE
SPEC.loader.exec_module(PROBE)

SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_transfer_residual_compression_2026-07-29"
    / "summary.json"
)
ARTIFACT = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_residual_seed_probe_2026-07-29"
    / "summary.json"
)


def source_chain() -> tuple[object, ...]:
    return PROBE.load_source_chain(SOURCE)


def artifact_payload() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_augmented_history_has_112_distinct_dihedral_orders() -> None:
    compression, cegar_path, cegar, transfer_path, transfer, first_path, first = (
        source_chain()
    )
    del compression, cegar_path, transfer_path, first_path

    history = PROBE.augmented_history(transfer, first, cegar)

    assert len(history) == 112
    assert Counter(record["packet"] for record in history) == {
        "prior": 24,
        "first_fresh": 32,
        "second_fresh": 32,
        "transfer_cegar_probe": 16,
        "transfer_cegar_residual": 8,
    }
    assert len({PROBE.dihedral_order_key(record["order"]) for record in history}) == 112


def test_seed_packets_have_three_transferred_and_eight_residual_orbits() -> None:
    compression, _, _, _, transfer, _, _ = source_chain()
    transferred_records, transferred_orbits, residual_records, residual_orbits = (
        PROBE.seed_packets(compression, transfer)
    )
    packets = PROBE.packet_definitions(
        transferred_orbits,
        residual_records,
        residual_orbits,
    )

    assert [record["ordered_quad_count"] for record in transferred_records] == [
        3,
        5,
        14,
    ]
    assert [record["ordered_quad_count"] for record in residual_records] == [
        7,
        9,
        5,
        3,
        7,
        4,
        6,
        4,
    ]
    assert {name: len(orbits) for name, orbits in packets.items()} == {
        "transferred_only": 3,
        "transferred_plus_width3": 4,
        "transferred_plus_all_residuals": 11,
    }
    assert sum(orbit.affine_map_count for orbit in packets["transferred_only"]) == 75
    assert (
        sum(
            orbit.affine_map_count
            for orbit in packets["transferred_plus_all_residuals"]
        )
        == 275
    )


def test_stored_probe_has_no_residual_seed_coverage_marginal() -> None:
    payload = artifact_payload()
    by_packet = {record["packet_id"]: record for record in payload["packet_coverage"]}
    by_seed = {
        (record["seed_family"], record["ordered_quad_count"], record["seed_id"]): record
        for record in payload["per_seed_coverage"]
    }

    assert {
        packet_id: record["covered_probe_order_count"]
        for packet_id, record in by_packet.items()
    } == {
        "transferred_only": 32,
        "transferred_plus_width3": 32,
        "transferred_plus_all_residuals": 32,
    }
    assert by_packet["transferred_only"]["matching_orbit_clause_occurrences"] == 280
    assert (
        by_packet["transferred_plus_width3"]["matching_orbit_clause_occurrences"] == 417
    )
    assert (
        by_packet["transferred_plus_all_residuals"]["matching_orbit_clause_occurrences"]
        == 809
    )
    assert sorted(
        record["covered_probe_order_count"]
        for (family, width, _), record in by_seed.items()
        if family == "transferred" and width in (3, 14)
    ) == [32, 32]
    assert payload["comparison"] == {
        "width3_marginal_over_transferred_probe_model_indices": [],
        "width3_marginal_over_transferred_order_count": 0,
        "other_residuals_marginal_over_width3_probe_model_indices": [],
        "other_residuals_marginal_over_width3_order_count": 0,
        "full_packet_uncovered_probe_model_indices": [],
        "decision": "STOP_C25_RESIDUAL_SEED_AUGMENTATION_AFTER_BOUNDED_PROBE",
    }


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_stored_c25_residual_seed_probe_replays_exactly() -> None:
    assert PROBE.check_payload(artifact_payload()) == {
        "status": "OK",
        "verified_blocked_history_orders": 112,
        "verified_probe_orders": 32,
        "verified_transferred_seed_certificates": 3,
        "verified_residual_seed_certificates": 8,
        "verified_exact_affine_seed_images": 275,
        "decision": "STOP_C25_RESIDUAL_SEED_AUGMENTATION_AFTER_BOUNDED_PROBE",
    }

def test_checker_rejects_fabricated_probe_configuration() -> None:
    payload = artifact_payload()
    payload["configuration"]["random_seed"] += 1

    with pytest.raises(AssertionError, match="configuration drifted"):
        PROBE.check_payload(payload)


def test_checker_rejects_substituted_source_artifact(tmp_path: Path) -> None:
    substitute = tmp_path / "summary.json"
    substitute.write_bytes(SOURCE.read_bytes())
    payload = artifact_payload()
    payload["source_compression_artifact"] = str(substitute)
    payload["source_compression_sha256"] = PROBE.file_sha256(substitute)

    with pytest.raises(AssertionError, match="source artifact drifted"):
        PROBE.check_payload(payload)
