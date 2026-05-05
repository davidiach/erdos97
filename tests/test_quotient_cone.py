from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from erdos97.quotient_cone import (
    check_quotient_cone_certificate,
    footprint_summary,
)
from erdos97.search import built_in_patterns

ROOT = Path(__file__).resolve().parents[1]
C19_COMPACT = (
    ROOT / "data" / "certificates" / "round2" / "c19_kalmanson_known_order_two_unsat.json"
)
C29 = ROOT / "data" / "certificates" / "c29_sidon_fixed_order_kalmanson_165_unsat.json"


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_quotient_cone_replays_compact_c19_certificate() -> None:
    result = check_quotient_cone_certificate(_load_json(C19_COMPACT))

    assert result.pattern == "C19_skew"
    assert result.n == 19
    assert result.strict_rows == 2
    assert result.distance_classes == 114
    assert result.weight_sum == 2
    assert result.max_weight == 1
    assert result.combined_nonzero_coefficient_count == 0
    assert result.zero_sum_verified is True
    assert result.nonpositive_sum_verified is True


def test_quotient_cone_replays_c29_fixed_order_certificate() -> None:
    result = check_quotient_cone_certificate(_load_json(C29))

    assert result.pattern == "C29_sidon_1_3_7_15"
    assert result.n == 29
    assert result.strict_rows == 165
    assert result.distance_classes == 319
    assert result.weight_sum == 504300794
    assert result.max_weight == 15835921
    assert result.combined_nonzero_coefficient_count == 0
    assert result.zero_sum_verified is True
    assert result.nonpositive_sum_verified is True
    assert "not a proof of Erdos Problem #97" in result.claim_strength


def test_c29_quotient_cone_footprint_records_used_support() -> None:
    footprint = footprint_summary(_load_json(C29))

    assert footprint["type"] == "quotient_cone_equality_footprint_v1"
    assert footprint["pattern"] == "C29_sidon_1_3_7_15"
    assert footprint["strict_rows"] == 165
    assert footprint["distance_classes"] == 319
    assert footprint["source_counts"] == {"kalmanson": 165}
    assert footprint["kind_counts"] == {
        "K1_diag_gt_sides": 65,
        "K2_diag_gt_other": 100,
    }
    assert footprint["label_support_size"] == 29
    assert footprint["label_support"] == list(range(29))
    assert footprint["touched_pair_count"] == 236
    assert footprint["touched_distance_class_count"] == 166
    assert footprint["touched_selected_center_count"] == 29
    assert footprint["distance_class_size_histogram"] == {"1": 290, "4": 29}
    assert footprint["touched_class_size_histogram"] == {"1": 137, "4": 29}
    assert footprint["zero_sum_verified"] is True
    assert "not an all-order obstruction" in str(footprint["semantics"])


def test_generalized_altman_gap_rows_share_the_quotient_cone_checker() -> None:
    pattern = built_in_patterns()["C29_sidon_1_3_7_15"]
    cert = {
        "pattern": {"name": pattern.name, "selected_rows": pattern.S},
        "cyclic_order": list(range(pattern.n)),
        "strict_rows": [
            {"source": "altman_gap", "gap_order": 1, "weight": 1},
            {"source": "altman_gap", "gap_order": 2, "weight": 1},
        ],
    }

    result = check_quotient_cone_certificate(cert)

    assert result.pattern == "C29_sidon_1_3_7_15"
    assert result.strict_rows == 2
    assert result.distance_classes == 319
    assert result.weight_sum == 2
    assert result.max_weight == 1
    assert result.combined_nonzero_coefficient_count == 0
    assert result.zero_sum_verified is True


def test_quotient_cone_checker_cli_outputs_summary_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_quotient_cone_certificate.py",
            str(C29),
            "--summary-json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(result.stdout)

    assert summary["pattern"] == "C29_sidon_1_3_7_15"
    assert summary["strict_rows"] == 165
    assert summary["distance_classes"] == 319
    assert summary["combined_nonzero_coefficient_count"] == 0
    assert summary["zero_sum_verified"] is True


def test_quotient_cone_footprint_miner_cli_asserts_c29() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/mine_quotient_cone_footprints.py",
            "--assert-c29",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(result.stdout)

    assert summary["pattern"] == "C29_sidon_1_3_7_15"
    assert summary["strict_rows"] == 165
    assert summary["distance_classes"] == 319
    assert summary["touched_distance_class_count"] == 166
    assert summary["zero_sum_verified"] is True


def test_quotient_cone_footprint_cover_probe_finds_c29_miss() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_quotient_cone_footprint_cover.py",
            str(C29),
            "--assert-sat",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(result.stdout)

    assert summary["pattern"] == "C29_sidon_1_3_7_15"
    assert summary["solver_result"] == "sat"
    assert summary["certificate_rows"] == 165
    assert summary["unique_order_quads"] == 165
    assert summary["motifs_tested"] == 58
    assert len(summary["candidate_order"]) == 29
