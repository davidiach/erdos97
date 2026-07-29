from __future__ import annotations

import copy
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
    / "compress_sparse_full_cone_seeded_certificates.py"
)
SPEC = importlib.util.spec_from_file_location(
    "sparse_full_cone_seeded_compression", SCRIPT
)
assert SPEC is not None and SPEC.loader is not None
COMPRESSION = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COMPRESSION
SPEC.loader.exec_module(COMPRESSION)

SOURCE = (
    ROOT / "data" / "runs" / "sparse_full_cone_seeded_cegar_2026-07-23" / "summary.json"
)
ARTIFACT = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_seeded_compression_2026-07-29"
    / "summary.json"
)


def source_payload() -> dict[str, object]:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def test_target_orders_collect_all_48_fresh_orders() -> None:
    payload = source_payload()
    targets = [COMPRESSION.target_orders(run) for run in payload["runs"]]

    assert [len(rows) for rows in targets] == [24, 24]
    assert sum(len(rows) for rows in targets) == 48
    for rows in targets:
        assert [row["target_id"] for row in rows[:2]] == ["probe:0", "probe:1"]
        assert [row["target_id"] for row in rows[-2:]] == [
            "seeded:6",
            "seeded:7",
        ]


def test_quotient_vector_hashes_are_stable_and_deduplicated() -> None:
    payload = source_payload()
    model = payload["runs"][0]["seeded_cegar"]["models"][0]
    certificate = model["full_kalmanson"]["certificate"]

    first = COMPRESSION.quotient_vector_hashes(certificate)
    second = COMPRESSION.quotient_vector_hashes(certificate)

    assert first == second
    assert first == sorted(set(first))
    assert all(len(value) == 64 for value in first)
    assert len(first) <= len(certificate["inequalities"])


def test_clause_coverage_contains_its_source_order() -> None:
    payload = source_payload()
    run = payload["runs"][0]
    model = run["seeded_cegar"]["models"][0]
    certificate = model["full_kalmanson"]["certificate"]
    orbit = COMPRESSION.build_clause_orbit(
        str(run["pattern"]),
        int(model["model_index"]),
        certificate,
    )

    coverage = COMPRESSION.clause_coverage(
        certificate,
        orbit,
        COMPRESSION.target_orders(run),
        source_target_id="seeded:0",
    )

    assert "seeded:0" in coverage["direct_covered_target_ids"]
    assert "seeded:0" in {
        row["target_id"] for row in coverage["translated_orbit_covered_targets"]
    }


def test_quotient_vector_reuse_records_pairwise_overlap() -> None:
    rows = [
        {
            "source_target_id": "seeded:0",
            "quotient_vector_support": {"hashes": ["a", "b"]},
        },
        {
            "source_target_id": "seeded:1",
            "quotient_vector_support": {"hashes": ["b", "c"]},
        },
    ]

    summary = COMPRESSION.quotient_vector_reuse(rows)

    assert summary["distinct_vector_count"] == 3
    assert summary["shared_vector_count"] == 1
    assert summary["max_certificate_frequency"] == 2
    assert summary["nonzero_pairwise_overlaps"] == [
        {
            "left_source_target_id": "seeded:0",
            "right_source_target_id": "seeded:1",
            "shared_vector_count": 1,
            "jaccard_fraction": 1 / 3,
        }
    ]


def test_stored_seeded_compression_packet_replays_exactly() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert COMPRESSION.check_payload(payload) == {
        "status": "OK",
        "verified_target_orders": 48,
        "verified_compressed_exact_certificates": 16,
        "verified_exact_affine_certificate_images": 432,
    }


def test_checker_rejects_duplicate_source_model() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    mutated = copy.deepcopy(payload)
    rows = mutated["runs"][0]["compressed_models"]
    rows[1] = copy.deepcopy(rows[0])

    with pytest.raises(AssertionError, match="duplicate source model index"):
        COMPRESSION.check_payload(mutated)
