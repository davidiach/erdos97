from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "exploration" / "screen_sparse_full_cone_fresh_orders.py"
SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_small_template_fresh_stream_2026-07-30"
    / "summary.json"
)
ARTIFACT = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_fresh_order_screen_2026-07-31"
    / "summary.json"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "screen_sparse_full_cone_fresh_orders",
        SCRIPT,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_selects_exactly_63_fresh_lightweight_survivors() -> None:
    module = load_module()
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    selected = module.selected_survivors(source)
    assert {name: len(models) for name, models in selected.items()} == {
        "C25_sidon_2_5_9_14": 31,
        "C29_sidon_1_3_7_15": 32,
    }


def test_integer_primitive_normalizes_sign_preservingly() -> None:
    module = load_module()
    assert module.integer_primitive([0, -6, 12]) == [0, -1, 2]


def test_separator_audit_replays_strict_integer_separation() -> None:
    module = load_module()
    rows = [
        module.InequalityRow("K1_diag_gt_sides", (0, 1, 2, 3), (1, 0)),
        module.InequalityRow("K2_diag_gt_other", (0, 1, 2, 3), (0, 1)),
        module.InequalityRow("K1_diag_gt_sides", (0, 1, 2, 4), (1, 1)),
    ]
    audit = module.separator_audit(rows, [1, 1])
    assert audit["all_row_dots_strictly_positive"] is True
    assert audit["minimum_row_dot"] == 1
    assert audit["maximum_row_dot"] == 2


def test_run_summary_keeps_conclusive_outcomes_separate() -> None:
    module = load_module()
    records = [
        {
            "classification": "EXACT_POSITIVE_ZERO_SUM_CERTIFICATE",
            "unique_ordered_quad_count": 3,
            "positive_inequalities": 4,
        },
        {"classification": "EXACT_INTEGER_SEPARATING_POTENTIAL"},
        {"classification": "UNRESOLVED_NUMERICAL_SCREEN"},
    ]
    summary = module.run_summary(records)
    assert summary["exact_positive_certificate_count"] == 1
    assert summary["exact_separating_potential_count"] == 1
    assert summary["unresolved_numerical_screen_count"] == 1


def test_stored_fresh_order_screen_replays_exactly() -> None:
    module = load_module()
    if not ARTIFACT.exists():
        return
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    result = module.check_payload(payload)
    assert result == {
        "status": "OK",
        "verified_selected_fresh_lightweight_survivors": 63,
        "verified_exact_positive_certificates": 63,
        "verified_exact_integer_separators": 0,
        "recorded_unresolved_numerical_screens": 0,
    }
