from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_n9_radius_blocker_rich_extension_product_sweep import (  # noqa: E402
    build_payload,
)
from check_n9_radius_blocker_rich_extension_product_pilot import (  # noqa: E402
    source_product_records,
)
from check_n9_radius_blocker_rich_quotient_sweep import (  # noqa: E402
    DEFAULT_SOURCE,
    load_shape_sweep,
    source_examples,
)


def test_n9_radius_blocker_rich_extension_product_sweep_catalog_counts() -> None:
    shape_sweep = load_shape_sweep(DEFAULT_SOURCE)
    sources = source_examples(shape_sweep)
    records = source_product_records(sources)

    assert len(records) == 20
    assert Counter(record["source_status"] for record in records) == {
        "self_edge": 10,
        "strict_cycle": 10,
    }
    assert sum(int(record["product_variant_count"]) for record in records) == 2899968
    assert Counter(int(record["product_variant_count"]) for record in records) == {
        110592: 8,
        147456: 7,
        196608: 5,
    }
    assert Counter(
        count for record in records for count in record["row_option_counts"]
    ) == {3: 43, 4: 137}


def test_n9_radius_blocker_rich_extension_product_sweep_limited_replay() -> None:
    payload = build_payload(max_packets=2, max_variants_per_packet=3)
    summary = payload["summary"]

    assert payload["debug_limits"] == {
        "max_packets": 2,
        "max_variants_per_packet": 3,
    }
    assert len(payload["source_packets"]) == 2
    assert summary["variant_count"] == 6
    assert summary["quotient_status_counts"] == {"self_edge": 6}
    assert summary["all_variants_obstructed"] is True
    assert all(packet["truncated"] is True for packet in payload["source_packets"])
