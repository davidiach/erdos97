from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import check_sparse_order_survivors as sparse_orders  # noqa: E402


def test_registered_sparse_order_survivors_match_artifact() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_sparse_order_survivors.py",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    artifact = json.loads(
        (ROOT / "data" / "certificates" / "sparse_order_survivors.json")
        .read_text(encoding="utf-8")
    )

    assert artifact == payload
    by_case = {row["case"]: row for row in payload["cases"]}
    c13 = by_case["C13_sidon_1_2_4_10:sample_full_filter_survivor"]
    c19 = by_case["C19_skew:vertex_circle_survivor"]

    assert c13["survives_pre_kalmanson_filters"] is True
    assert c13["survives_current_exact_filters"] is False
    assert c13["vertex_circle"]["obstructed"] is False
    assert c13["radius_propagation"]["acyclic_choice_edge_count"] == 4
    assert c13["kalmanson_certificate"]["positive_inequalities"] == 2
    assert c13["kalmanson_certificate"]["max_weight"] == 1
    assert c19["survives_pre_kalmanson_filters"] is True
    assert c19["survives_current_exact_filters"] is False
    assert c19["kalmanson_certificate"]["positive_inequalities"] == 2
    assert c19["kalmanson_certificate"]["max_weight"] == 1
    assert c19["sparse_frontier"]["trivial_empty_radius_choice_exists"] is True


def test_kalmanson_status_rejects_offset_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = ROOT / "data" / "certificates" / "c13_sidon_order_survivor_kalmanson_two_unsat.json"
    tampered = tmp_path / "tampered_certificate.json"
    shutil.copyfile(source, tampered)
    payload = json.loads(tampered.read_text(encoding="utf-8"))
    payload["pattern"]["circulant_offsets"] = [1, 2, 4, 9]
    tampered.write_text(json.dumps(payload), encoding="utf-8")

    case = "C13_sidon_1_2_4_10:sample_full_filter_survivor"
    monkeypatch.setitem(sparse_orders.KALMANSON_CERTIFICATES, case, tampered)
    pattern = sparse_orders.built_in_patterns()["C13_sidon_1_2_4_10"]
    order = sparse_orders.REGISTERED_ORDERS["C13_sidon_1_2_4_10"][
        "sample_full_filter_survivor"
    ]

    with pytest.raises(ValueError, match="circulant offsets"):
        sparse_orders.kalmanson_status(case, pattern, order)
