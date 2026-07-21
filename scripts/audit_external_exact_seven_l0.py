#!/usr/bin/env python3
"""Audit the pinned external exact-seven L0 schema frontier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from erdos97.external_exact_seven_l0_audit import (
    audit_external_exact_seven_l0,
)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path, help="external repository checkout")
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="fail unless the checkout matches the pinned L0 snapshot",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    audit = audit_external_exact_seven_l0(args.checkout)
    payload = audit.to_json()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            f"commit={audit.commit or 'UNKNOWN'} "
            f"schemas={audit.schema_summary['schema_count']} "
            f"issues={len(audit.validation_issues)} "
            f"expected_snapshot_match="
            f"{str(audit.expected_snapshot_match).lower()}"
        )

    if args.assert_expected and not audit.expected_snapshot_match:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
