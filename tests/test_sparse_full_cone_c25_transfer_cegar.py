from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "exploration" / "run_sparse_full_cone_c25_transfer_cegar.py"
SPEC = importlib.util.spec_from_file_location(
    "sparse_full_cone_c25_transfer_cegar",
    SCRIPT,
)
assert SPEC is not None and SPEC.loader is not None
C25 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = C25
SPEC.loader.exec_module(C25)

SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_fresh_template_transfer_2026-08-02"
    / "summary.json"
)
ARTIFACT = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_transfer_cegar_2026-08-03"
    / "summary.json"
)


def source_payload() -> dict[str, object]:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def test_c25_seed_packet_has_two_primary_and_one_secondary_orbit() -> None:
    records, orbits = C25.c25_seed_packet(source_payload())

    assert [record["ordered_quad_count"] for record in records] == [3, 5, 14]
    assert [record["seed_role"] for record in records] == [
        "PRIMARY_CROSS_STREAM_TRANSFER",
        "PRIMARY_CROSS_STREAM_TRANSFER",
        "SECONDARY_PRIOR_PACKET_TRANSFER",
    ]
    assert sum(orbit.affine_map_count for orbit in orbits) == 75


def test_c25_history_has_88_distinct_dihedral_orders() -> None:
    source = source_payload()
    first_path = C25.first_fresh_stream_path(source)
    first = json.loads(first_path.read_text(encoding="utf-8"))

    history = C25.c25_history(source, first)

    assert len(history) == 88
    assert {
        packet: sum(record["packet"] == packet for record in history)
        for packet in ("prior", "first_fresh", "second_fresh")
    } == {"prior": 24, "first_fresh": 32, "second_fresh": 32}
    assert len({C25.dihedral_order_key(record["order"]) for record in history}) == 88


def test_history_identity_omits_full_orders_but_pins_hashes() -> None:
    records = [
        {
            "history_id": "prior:0",
            "packet": "prior",
            "order_sha256": "a" * 64,
            "dihedral_order_sha256": "b" * 64,
            "order": [0, 1, 2],
        }
    ]

    assert C25.history_identity(records) == [
        {
            "history_id": "prior:0",
            "packet": "prior",
            "order_sha256": "a" * 64,
            "dihedral_order_sha256": "b" * 64,
        }
    ]


def test_stored_c25_transfer_cegar_replays_exactly() -> None:
    if not ARTIFACT.exists():
        return
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    result = C25.check_payload(payload)

    assert result == {
        "status": "OK",
        "verified_blocked_history_orders": 88,
        "verified_transferred_seed_certificates": 3,
        "verified_counterfactual_probe_orders": 16,
        "verified_new_exact_full_cone_certificates": 8,
        "verified_exact_affine_certificate_images": 275,
        "seeded_cegar_status": (
            "BOUNDED_C25_TRANSFER_SEEDED_CERTIFICATE_LIMIT_REACHED"
        ),
    }
