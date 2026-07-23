from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "exploration" / "run_sparse_full_cone_seeded_cegar.py"
SPEC = importlib.util.spec_from_file_location("sparse_full_cone_seeded_cegar", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
SEEDED = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SEEDED
SPEC.loader.exec_module(SEEDED)

SEED_SOURCE = (
    ROOT / "data" / "runs" / "sparse_full_cone_compression_2026-07-23" / "summary.json"
)
ARTIFACT = (
    ROOT / "data" / "runs" / "sparse_full_cone_seeded_cegar_2026-07-23" / "summary.json"
)


def test_quotient_automorphisms_reject_nonpreserving_reflection() -> None:
    assert SEEDED.quotient_automorphism_multipliers(25, [2, 5, 9, 14]) == [1]
    assert SEEDED.quotient_automorphism_multipliers(29, [1, 3, 7, 15]) == [1]


def test_translated_certificate_remains_exact_and_reanchored() -> None:
    payload = json.loads(SEED_SOURCE.read_text(encoding="utf-8"))
    certificate = payload["runs"][0]["compressed_models"][0]["compressed_certificate"]

    transformed = SEEDED.transform_certificate(
        certificate,
        multiplier=1,
        translation=7,
    )
    checked = SEEDED.check_certificate_dict(transformed)

    assert transformed["cyclic_order"][0] == 0
    assert checked.zero_sum_verified
    assert checked.positive_inequalities == len(certificate["inequalities"])


def test_seed_orbits_are_exact_and_have_stable_canonical_hashes() -> None:
    orbits = SEEDED.load_seed_orbits(SEED_SOURCE)

    assert [orbit.source_model_index for orbit in orbits["C25_sidon_2_5_9_14"]] == [2]
    assert [orbit.source_model_index for orbit in orbits["C29_sidon_1_3_7_15"]] == [
        0,
        1,
        2,
    ]
    for name, pattern_orbits in orbits.items():
        n = SEEDED.PATTERNS[name][0]
        for orbit in pattern_orbits:
            assert orbit.affine_map_count == n
            assert 1 <= len(orbit.clauses) <= orbit.affine_map_count
            assert len(orbit.canonical_clause_sha256) == 64


def test_probe_summary_counts_seed_source_overlap() -> None:
    orbit = SEEDED.ClauseOrbit(
        pattern="toy",
        source_model_index=4,
        source_order=(0, 1, 2, 3, 4),
        source_certificate={},
        multipliers=(1,),
        affine_map_count=1,
        clauses=(((0, 1, 2, 3),),),
        canonical_clause_sha256="0" * 64,
    )
    models = [
        {
            "lightweight_filters": {"survives": True},
            "seed_orbit_matches": [
                {
                    "source_model_index": 4,
                    "matching_orbit_clause_count": 1,
                }
            ],
        },
        {
            "lightweight_filters": {"survives": False},
            "seed_orbit_matches": [],
        },
    ]

    summary = SEEDED.probe_coverage_summary(models, [orbit])

    assert summary["covered_probe_order_count"] == 1
    assert summary["covered_strong_probe_order_count"] == 1
    assert summary["seed_source_overlap_histogram"] == {"0": 1, "1": 1}


def test_stored_seeded_cegar_packet_replays_exactly() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert SEEDED.check_payload(payload) == {
        "status": "OK",
        "verified_counterfactual_inverse_pair_escape_orders": 32,
        "verified_new_exact_full_cone_certificates": 16,
        "verified_exact_affine_certificate_images": 544,
    }
