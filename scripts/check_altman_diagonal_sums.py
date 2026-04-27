#!/usr/bin/env python3
"""Check natural-order Altman diagonal-sum obstructions."""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.altman_diagonal_sums import check_altman  # noqa: E402
from erdos97.search import built_in_patterns  # noqa: E402

PATTERN_LEDGER = ROOT / "data" / "patterns" / "candidate_patterns.json"

EXPECTED: dict[str, dict[str, object]] = {
    "C19_skew": {
        "offsets": [-8, -3, 5, 9],
        "chord_orders": [8, 3, 5, 9],
        "forced_equal_U": [3, 5, 8, 9],
        "altman_contradiction": True,
        "status": "NATURAL_ORDER_EXACT_OBSTRUCTION",
        "abstract_incidence_status": "LIVE",
    }
}


def abstract_status_from_ledger(pattern_name: str) -> str:
    data = json.loads(PATTERN_LEDGER.read_text(encoding="utf-8"))
    by_name = {str(row["name"]): row for row in data}
    if pattern_name not in by_name:
        return "UNTOUCHED"
    status = str(by_name[pattern_name].get("status", ""))
    marker = "abstract-incidence status:"
    if marker not in status:
        return "UNTOUCHED"
    abstract_status = status.split(marker, 1)[1].strip()
    normalized = abstract_status.lower()
    if normalized.startswith("live"):
        return "LIVE"
    if normalized.startswith("survives"):
        return "SURVIVES_CURRENT_FILTERS"
    if normalized.startswith("killed"):
        return "EXACT_OBSTRUCTION"
    return abstract_status or "UNTOUCHED"


def decorate_row(row: dict[str, object]) -> dict[str, object]:
    return {
        **row,
        "abstract_incidence_status": abstract_status_from_ledger(str(row["pattern"])),
    }


def assert_expected(rows: list[dict[str, object]]) -> None:
    by_pattern = {str(row["pattern"]): row for row in rows}
    missing = sorted(set(EXPECTED) - set(by_pattern))
    if missing:
        raise AssertionError(f"missing expected pattern(s): {', '.join(missing)}")
    for pattern, expected in EXPECTED.items():
        row = by_pattern[pattern]
        for key, value in expected.items():
            if row[key] != value:
                raise AssertionError(f"{pattern}: {key} {row[key]} != {value}")


def assert_natural_killed(rows: list[dict[str, object]]) -> None:
    for row in rows:
        if not row["altman_contradiction"]:
            raise AssertionError(f"{row['pattern']}: expected an Altman contradiction")


def print_table(rows: list[dict[str, object]]) -> None:
    headers = ["pattern", "n", "offsets", "orders", "forced U", "status", "abstract"]
    table = [
        [
            str(row["pattern"]),
            str(row["n"]),
            str(row["offsets"]),
            str(row["chord_orders"]),
            str(row["forced_equal_U"]),
            str(row["status"]),
            str(row["abstract_incidence_status"]),
        ]
        for row in rows
    ]
    widths = [
        max(len(headers[col]), *(len(row[col]) for row in table))
        for col in range(len(headers))
    ]
    print("  ".join(headers[col].ljust(widths[col]) for col in range(len(headers))))
    print("  ".join("-" * widths[col] for col in range(len(headers))))
    for row in table:
        print("  ".join(row[col].ljust(widths[col]) for col in range(len(headers))))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print JSON instead of a table")
    parser.add_argument("--pattern", help="limit checks to one built-in pattern")
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="assert every registered expected output is selected and correct",
    )
    parser.add_argument(
        "--assert-natural-killed",
        action="store_true",
        help="assert every selected pattern has an Altman contradiction",
    )
    args = parser.parse_args()

    patterns = built_in_patterns()
    if args.pattern:
        if args.pattern not in patterns:
            raise SystemExit(f"unknown pattern {args.pattern}; known: {', '.join(patterns)}")
        selected = [patterns[args.pattern]]
    else:
        selected = list(patterns.values())

    rows = [decorate_row(dataclasses.asdict(check_altman(pattern))) for pattern in selected]
    if args.assert_expected:
        assert_expected(rows)
    if args.assert_natural_killed:
        assert_natural_killed(rows)

    if args.json:
        output: object = rows[0] if args.pattern and len(rows) == 1 else rows
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print_table(rows)
        if args.assert_expected or args.assert_natural_killed:
            print("OK: Altman diagonal-sum expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
