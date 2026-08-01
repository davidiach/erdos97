#!/usr/bin/env python3
"""Generate or check the exact fragile-cycle quotient hierarchy pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from erdos97.fragile_cycle_quotient_hierarchy import (
    assert_expected_payload,
    hierarchy_payload,
    validate_payload,
)
from erdos97.json_io import load_json, write_json
from erdos97.path_display import display_path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "fragile_cycle_quotient_hierarchy.json"
)


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _load_object(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"expected object payload in {display_path(path, ROOT)}")
    return payload


def summary_json_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing hierarchy summary."""

    return {
        "schema": payload["schema"],
        "status": payload["status"],
        "trust": payload["trust"],
        "claim_scope": payload["claim_scope"],
        "hierarchy_definition": payload["hierarchy_definition"],
        "templates": [
            {
                "name": template["name"],
                "strict_inequality_support": template[
                    "strict_inequality_support"
                ],
                "selected_center_support": template["selected_center_support"],
                "support_minimality": template["support_minimality"],
                "partition_accounting": template["partition_accounting"],
                "admissible_vertex_count_histogram": template[
                    "admissible_vertex_count_histogram"
                ],
                "nontrivial_role_blocks": [
                    record["role_blocks"]
                    for record in template["quotients"]
                    if record["vertex_count"] < len(template["formal_labels"])
                ],
            }
            for template in payload["templates"]
        ],
        "summary": payload["summary"],
        "limitations": payload["limitations"],
        "conclusion": payload["conclusion"],
        "provenance": payload["provenance"],
    }


def _print_summary(payload: dict[str, Any], elapsed: float) -> None:
    print("exact fragile-cycle quotient hierarchy pilot")
    for template in payload["templates"]:
        accounting = template["partition_accounting"]
        print(
            f"{template['name']}: strict={template['strict_inequality_support']} "
            f"admissible={accounting['admissible_partitions']} "
            f"nontrivial={accounting['nontrivial_admissible_partitions']}"
        )
    print(
        "all quotient certificates zero-sum: "
        f"{payload['summary']['all_quotient_certificates_zero_sum']}"
    )
    print(f"quotient catalog sha256: {payload['summary']['quotient_catalog_sha256']}")
    print(f"elapsed_seconds: {elapsed:.6f}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print compact hierarchy JSON",
    )
    parser.add_argument("--write", action="store_true", help="write stable JSON artifact")
    parser.add_argument("--check", action="store_true", help="check a stored artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    artifact_path = _resolve(args.artifact)
    out_path = _resolve(args.out)
    if args.write and args.check and artifact_path != out_path:
        raise SystemExit("--write --check requires --artifact and --out to match")

    start = perf_counter()
    payload = _load_object(artifact_path) if args.check else hierarchy_payload()
    errors = validate_payload(payload) if args.check else []
    if errors:
        raise SystemExit("; ".join(errors[:5]))
    if args.assert_expected:
        assert_expected_payload(payload)
    if args.write:
        write_json(payload, out_path)
    elapsed = perf_counter() - start

    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_summary(payload, elapsed)
        if args.assert_expected:
            print("OK: fragile-cycle quotient hierarchy matches expected data")
        if args.check:
            print(f"checked {display_path(artifact_path, ROOT)}")
        if args.write:
            print(f"wrote {display_path(out_path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
