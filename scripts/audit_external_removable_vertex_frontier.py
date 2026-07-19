#!/usr/bin/env python3
"""Audit the source shape of an external Problem 97 formalization checkout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.external_frontier_audit import audit_external_frontier  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path, help="external repository checkout")
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="fail unless the audited source matches the dated 12/32 snapshot",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    audit = audit_external_frontier(args.checkout)
    payload = audit.to_json()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            f"commit={audit.commit or 'UNKNOWN'} "
            f"declarations={len(audit.direct_open_declarations)} "
            f"holes={audit.textual_holes} "
            f"readme_source_agree={str(audit.readme_source_agree).lower()} "
            f"expected_snapshot_match={str(audit.expected_snapshot_match).lower()}"
        )

    if args.assert_expected and not (
        audit.expected_snapshot_match and audit.readme_source_agree
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
