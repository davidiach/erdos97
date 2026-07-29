from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "exploration" / "probe_sparse_full_cone_small_templates.py"
SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_seeded_compression_2026-07-29"
    / "summary.json"
)
ARTIFACT = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_small_template_fresh_stream_2026-07-29"
    / "summary.json"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "probe_sparse_full_cone_small_templates",
        SCRIPT,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_dihedral_order_key_is_rotation_and_reversal_invariant() -> None:
    module = load_module()
    order = [0, 3, 1, 4, 2]
    rotation = [1, 4, 2, 0, 3]
    reversal = [0, 2, 4, 1, 3]
    assert module.dihedral_order_key(order) == module.dihedral_order_key(rotation)
    assert module.dihedral_order_key(order) == module.dihedral_order_key(reversal)


def test_small_template_packet_has_seven_distinct_exact_orbits() -> None:
    module = load_module()
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    templates, orbits = module.build_small_templates(source, max_width=8)
    assert {name: len(rows) for name, rows in templates.items()} == {
        "C25_sidon_2_5_9_14": 4,
        "C29_sidon_1_3_7_15": 3,
    }
    widths = sorted(
        int(row["ordered_quad_count"]) for rows in templates.values() for row in rows
    )
    assert widths == [3, 4, 4, 5, 5, 7, 8]
    hashes = {
        str(row["canonical_clause_sha256"])
        for rows in templates.values()
        for row in rows
    }
    assert len(hashes) == 7
    assert (
        sum(orbit.affine_map_count for rows in orbits.values() for orbit in rows) == 187
    )


def test_historical_packet_has_48_dihedrally_distinct_orders() -> None:
    module = load_module()
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    history = module.historical_orders_by_pattern(source)
    assert sum(len(orders) for orders in history.values()) == 48
    assert all(
        len({module.dihedral_order_key(order) for order in orders}) == len(orders)
        for orders in history.values()
    )


def test_template_coverage_summary_counts_hits() -> None:
    module = load_module()
    templates = [
        {"template_id": "t0"},
        {"template_id": "t1"},
    ]
    models = [
        {
            "lightweight_filters": {"survives": True},
            "template_matches": [
                {"template_id": "t0", "matching_orbit_clause_count": 2}
            ],
        },
        {
            "lightweight_filters": {"survives": False},
            "template_matches": [],
        },
    ]
    summary = module.coverage_summary(models, templates)
    assert summary["covered_fresh_order_count"] == 1
    assert summary["covered_strong_fresh_order_count"] == 1
    assert summary["template_hit_count_histogram"] == {"0": 1, "1": 1}
    assert summary["by_template"][0]["matching_orbit_clause_occurrences"] == 2


def test_stored_fresh_stream_artifact_replays_exactly() -> None:
    module = load_module()
    if not ARTIFACT.exists():
        return
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    result = module.check_payload(payload)
    assert result == {
        "status": "OK",
        "verified_canonical_exact_templates": 7,
        "verified_exact_affine_template_images": 187,
        "verified_history_disjoint_fresh_orders": 64,
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("status", "FABRICATED"),
        ("solver_result", "fabricated"),
        ("iterations", -999),
        ("random_seed", -999),
        ("inverse_pair_clause_count", -999),
    ],
)
def test_checker_rejects_fabricated_solver_provenance(
    field: str,
    value: object,
) -> None:
    module = load_module()
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    mutated = copy.deepcopy(payload)
    mutated["runs"][0]["fresh_stream"][field] = value

    with pytest.raises(AssertionError):
        module.check_payload(mutated)


def test_checker_rejects_fabricated_model_iteration() -> None:
    module = load_module()
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    mutated = copy.deepcopy(payload)
    mutated["runs"][0]["fresh_stream"]["models"][0]["z3_iteration"] = -999

    with pytest.raises(AssertionError, match="model iteration provenance drifted"):
        module.check_payload(mutated)