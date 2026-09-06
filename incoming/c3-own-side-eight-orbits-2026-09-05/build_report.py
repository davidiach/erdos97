#!/usr/bin/env python3
"""Regenerate summary/inventory from saved evidence; this does not rerun searches."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from c3_eight_check import audit_run_records, require, verify_packet
from c3_eight_controls import audit_controls

ROOT = Path(__file__).resolve().parent
COUNTERS = (
    "nodes", "radius_prunes", "shortcut_prunes", "metric_prunes",
    "pair_dead", "survivors",
)


def build_report() -> dict:
    """Validate saved evidence and regenerate the claim-scoped summary."""
    audit_run_records()
    runs = json.loads((ROOT / "runs.json").read_text())
    totals = {}
    for kind in ("primary", "oracle"):
        selected = [
            record["report"] for record in runs["records"]
            if record["implementation"] == kind and record["report"]["orbits"] == 8
        ]
        totals[kind] = {key: sum(row[key] for row in selected) for key in COUNTERS}
    return {
        "schema": 1,
        "status": "REVIEW_PENDING_RESTRICTED_COMPUTER_ASSISTED_OBSTRUCTION",
        "scope": "own-side C3 systems through eight orbits only",
        "no_unrestricted_solution_claimed": True,
        "source_sha256": runs["source_sha256"],
        "eight_orbit_slices_per_implementation": 21,
        "eight_orbit_totals": totals,
        "certificate_audit": verify_packet(),
        "controls": audit_controls(),
    }


def inventory() -> dict:
    """Inventory packet files, excluding this generated manifest and caches."""
    return {
        "schema": 1,
        "files": {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in sorted(ROOT.iterdir())
            if path.is_file() and path.name != "manifest.json"
        },
        "scope": "byte integrity only; not mathematical validation",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    # The JSON round trip normalizes integer keys in multiplicity distributions.
    normalized = json.loads(json.dumps(report))
    if args.write:
        (ROOT / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        (ROOT / "manifest.json").write_text(json.dumps(inventory(), indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads((ROOT / "report.json").read_text()) == normalized, "report mismatch")
        require(json.loads((ROOT / "manifest.json").read_text()) == inventory(), "inventory mismatch")
    print(json.dumps({"saved_evidence_checked": True, "fresh_enumeration": False}, sort_keys=True))


if __name__ == "__main__":
    main()
