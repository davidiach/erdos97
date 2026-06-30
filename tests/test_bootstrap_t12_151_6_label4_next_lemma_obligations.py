from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_bootstrap_t12_151_6_label4_next_lemma_obligations import (
    build_payload,
    validate_payload,
)


def test_next_lemma_obligations_check() -> None:
    root = Path(__file__).resolve().parents[1]
    script = (
        root
        / "scripts"
        / "check_bootstrap_t12_151_6_label4_next_lemma_obligations.py"
    )
    result = subprocess.run(
        [sys.executable, str(script), "--check", "--assert-expected", "--json"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["target_row_key"] == "151:6"
    assert payload["open_obligation_count"] == 3
    assert payload["open_obligation_ids"] == [
        "private_halo_endpoint8_exclusion",
        "center8_migration_or_source",
        "target_sparse_order_or_geometry",
    ]
    assert payload["private_halo_only_basic_survivor_count"] == 12
    assert payload["support_requirement_center8_count"] == 0
    assert payload["current_row_family_all_order_route_ready"] is False
    assert payload["all_order_obstruction_proved"] is False
    assert payload["solves_n9"] is False
    assert payload["solves_erdos97"] is False


def test_next_lemma_obligations_artifact_is_deterministic() -> None:
    root = Path(__file__).resolve().parents[1]
    artifact = (
        root
        / "data"
        / "certificates"
        / "bootstrap_t12_151_6_label4_next_lemma_obligations.json"
    )
    stored = json.loads(artifact.read_text(encoding="utf-8"))
    assert stored == build_payload()
    assert validate_payload(stored) == []


def test_next_lemma_obligations_rejects_bridge_overclaim() -> None:
    payload = build_payload()
    payload["summary"]["solves_n9"] = True
    errors = validate_payload(payload)
    assert "summary solves_n9 mismatch" in errors
    assert "stored artifact is stale relative to source packets" not in errors
