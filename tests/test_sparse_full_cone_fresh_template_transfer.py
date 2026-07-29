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
    / "probe_sparse_full_cone_fresh_template_transfer.py"
)
SPEC = importlib.util.spec_from_file_location(
    "sparse_full_cone_fresh_template_transfer",
    SCRIPT,
)
assert SPEC is not None and SPEC.loader is not None
TRANSFER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = TRANSFER
SPEC.loader.exec_module(TRANSFER)

SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_fresh_compression_2026-07-29"
    / "summary.json"
)
PRIOR = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_seeded_compression_2026-07-29"
    / "summary.json"
)
FIRST = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_small_template_fresh_stream_2026-07-29"
    / "summary.json"
)
ARTIFACT = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_fresh_template_transfer_2026-07-29"
    / "summary.json"
)


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_transfer_template_rule_selects_four_distinct_exact_orbits() -> None:
    templates, orbits = TRANSFER.build_transfer_templates(
        load(SOURCE),
        max_small_width=12,
        broad_source_coverage_min=24,
    )

    assert {name: len(rows) for name, rows in templates.items()} == {
        "C25_sidon_2_5_9_14": 3,
        "C29_sidon_1_3_7_15": 1,
    }
    assert sorted(
        int(row["ordered_quad_count"]) for rows in templates.values() for row in rows
    ) == [3, 5, 7, 14]
    assert (
        sum(orbit.affine_map_count for rows in orbits.values() for orbit in rows) == 104
    )


def test_combined_history_has_112_dihedrally_distinct_orders() -> None:
    prior = TRANSFER.historical_orders_by_pattern(load(PRIOR))
    first = TRANSFER.first_stream_orders_by_pattern(load(FIRST))

    counts = []
    for name in prior:
        orders = [*prior[name], *first[name]]
        keys = {TRANSFER.dihedral_order_key(order) for order in orders}
        assert len(keys) == len(orders)
        counts.append(len(orders))
    assert counts == [56, 56]
    assert sum(counts) == 112


def test_transfer_coverage_summary_counts_exact_hits() -> None:
    templates = [{"template_id": "t0"}, {"template_id": "t1"}]
    records = [
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

    summary = TRANSFER.coverage_summary(records, templates)

    assert summary["covered_order_count"] == 1
    assert summary["covered_strong_order_count"] == 1
    assert summary["template_hit_count_histogram"] == {"0": 1, "1": 1}
    assert summary["by_template"][0]["matching_orbit_clause_occurrences"] == 2


def test_transfer_decision_stops_only_after_two_zero_hit_packets() -> None:
    zero = {"covered_order_count": 0}
    hit = {"covered_order_count": 1}

    assert (
        TRANSFER.transfer_decision(zero, zero)["decision"]
        == "STOP_PACKET_SPECIFIC_TEMPLATE_MINING"
    )
    assert (
        TRANSFER.transfer_decision(hit, zero)["decision"]
        == "CONTINUE_EXACT_TEMPLATE_TRANSFER"
    )


def test_stored_transfer_packet_replays_exactly() -> None:
    if not ARTIFACT.exists():
        return
    result = TRANSFER.check_payload(load(ARTIFACT))

    assert result == {
        "status": "OK",
        "verified_canonical_exact_templates": 4,
        "verified_exact_affine_template_images": 104,
        "verified_source_packet_orders": 63,
        "verified_prior_packet_orders": 48,
        "verified_second_history_disjoint_orders": 64,
        "verified_outside_source_packet_covered_orders": 32,
        "transfer_decisions": [
            "CONTINUE_EXACT_TEMPLATE_TRANSFER",
            "STOP_PACKET_SPECIFIC_TEMPLATE_MINING",
        ],
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
def test_checker_rejects_fabricated_second_stream_provenance(
    field: str,
    value: object,
) -> None:
    payload = load(ARTIFACT)
    mutated = copy.deepcopy(payload)
    mutated["runs"][0]["second_fresh_stream"][field] = value

    with pytest.raises(AssertionError):
        TRANSFER.check_payload(mutated)


def test_checker_rejects_fabricated_second_stream_iteration() -> None:
    payload = load(ARTIFACT)
    mutated = copy.deepcopy(payload)
    models = mutated["runs"][0]["second_fresh_stream"]["models"]
    models[0]["z3_iteration"] = -999

    with pytest.raises(AssertionError, match="iteration provenance drifted"):
        TRANSFER.check_payload(mutated)