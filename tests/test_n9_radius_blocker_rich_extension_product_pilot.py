from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_n9_radius_blocker_rich_extension_product_pilot import (  # noqa: E402
    build_payload,
    iter_full_product_added_label_variants,
    select_source_record,
    source_product_records,
)
from check_n9_radius_blocker_rich_quotient_sweep import (  # noqa: E402
    DEFAULT_SOURCE,
    load_shape_sweep,
    source_examples,
)


def test_n9_radius_blocker_rich_extension_product_selects_first_maximum() -> None:
    shape_sweep = load_shape_sweep(DEFAULT_SOURCE)
    sources = source_examples(shape_sweep)
    records = source_product_records(sources)
    _selected_source, selected_record = select_source_record(sources)

    assert sum(int(record["product_variant_count"]) for record in records) == 2899968
    assert Counter(int(record["product_variant_count"]) for record in records) == {
        110592: 8,
        147456: 7,
        196608: 5,
    }
    assert (
        selected_record["source_packet_id"]
        == "n9_full_exact_four_radius_blocker_shape_U0135_natural_order:self_edge:0"
    )
    assert selected_record["product_variant_count"] == 196608
    assert selected_record["row_option_counts"] == [3, 4, 4, 4, 4, 4, 4, 4, 4]


def test_n9_radius_blocker_rich_extension_product_variant_iterator() -> None:
    variants = list(
        iter_full_product_added_label_variants(
            baseline=[10, 20, 30],
            alternatives=[[11, 12], [], [31]],
        )
    )

    assert len(variants) == 6
    assert variants[0] == (0, (10, 20, 30))
    assert variants[-1] == (2, (12, 20, 31))
    assert Counter(distance for distance, _labels in variants) == {
        0: 1,
        1: 3,
        2: 2,
    }


def test_n9_radius_blocker_rich_extension_product_limited_replay_smoke() -> None:
    payload = build_payload(max_variants=4)
    summary = payload["summary"]
    selected_packet = payload["selected_packet"]

    assert summary["selected_packet_id"] == (
        "n9_full_exact_four_radius_blocker_shape_U0135_natural_order:self_edge:0"
    )
    assert summary["variant_count"] == 4
    assert summary["quotient_status_counts"] == {"self_edge": 4}
    assert selected_packet["truncated"] is True
