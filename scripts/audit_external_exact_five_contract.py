#!/usr/bin/env python3
"""Audit the pinned external exact-five occurrence contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.external_exact_five_contract import (  # noqa: E402
    audit_external_exact_five_contract,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path, help="external repository checkout")
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="fail unless the checkout matches the pinned contract snapshot",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    audit = audit_external_exact_five_contract(args.checkout)
    payload = audit.to_json()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            f"commit={audit.commit or 'UNKNOWN'} "
            f"sources={len(audit.source_sha256)} "
            f"missing_markers={sum(map(len, audit.missing_markers.values()))} "
            f"expected_snapshot_match="
            f"{str(audit.expected_snapshot_match).lower()}"
        )

    if args.assert_expected and not audit.expected_snapshot_match:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
