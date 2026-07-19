#!/usr/bin/env python3
"""Check the period-three choice-free four-hit radius reduction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.period_three_radius_partition import (  # noqa: E402
    audit_three_reverse_pair_radius_partitions,
    matches_expected,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="fail unless the exact 203/87 partition census is reproduced",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    audit = audit_three_reverse_pair_radius_partitions()
    if args.json:
        print(json.dumps(audit.to_json(), indent=2, sort_keys=True))
    else:
        print(
            f"partitions={audit.total_partitions} "
            f"occurrence_free={audit.occurrence_free_partitions} "
            f"max_free_class={audit.maximum_occurrence_free_class_size} "
            f"four_hit={str(audit.four_hit_forces_complete_pair).lower()}"
        )

    if args.assert_expected and not matches_expected(audit):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
