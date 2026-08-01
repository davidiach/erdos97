#!/usr/bin/env python3
"""Generate or check exact dual identities for n=9 relation skeletons."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]

from erdos97.json_io import write_json  # noqa: E402
from erdos97.n9_vertex_circle_template_duals import (  # noqa: E402
    SCHEMA,
    assert_expected_template_dual_counts,
    template_dual_payload,
)
from erdos97.path_display import display_path  # noqa: E402


DEFAULT_RELATION_SKELETONS = (
    ROOT / "data" / "certificates" / "relation_skeleton_catalog.json"
)
DEFAULT_FRONTIER_CLASSIFICATION = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)
DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_template_duals.json"
)


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _summary(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    record = payload if isinstance(payload, dict) else {}
    coverage = record.get("assignment_coverage")
    coverage = coverage if isinstance(coverage, dict) else {}
    return {
        "ok": not errors,
        "artifact": display_path(path, ROOT),
        "schema": record.get("schema"),
        "status": record.get("status"),
        "trust": record.get("trust"),
        "skeleton_count": record.get("skeleton_count"),
        "template_count": record.get("template_count"),
        "family_count": record.get("family_count"),
        "covered_assignment_count": record.get("covered_assignment_count"),
        "strict_term_count_counts": record.get("strict_term_count_counts"),
        "equality_term_count_counts": record.get("equality_term_count_counts"),
        "maximum_active_pair_count": record.get("maximum_active_pair_count"),
        "total_active_pair_quotient_partitions_checked": record.get(
            "total_active_pair_quotient_partitions_checked"
        ),
        "transformed_certificate_sha256": coverage.get(
            "transformed_certificate_sha256"
        ),
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--relation-skeletons",
        type=Path,
        default=DEFAULT_RELATION_SKELETONS,
    )
    parser.add_argument(
        "--frontier-classification",
        type=Path,
        default=DEFAULT_FRONTIER_CLASSIFICATION,
    )
    parser.add_argument("--artifact", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    out = _resolve(args.out)
    artifact = _resolve(args.artifact) if args.artifact is not None else DEFAULT_ARTIFACT
    if args.write and args.check:
        if args.artifact is not None and artifact != out:
            print(
                "--write --check requires matching --artifact/--out or omitted --artifact",
                file=sys.stderr,
            )
            return 2
        artifact = out

    try:
        relation_skeletons = _load(_resolve(args.relation_skeletons))
        frontier_classification = _load(_resolve(args.frontier_classification))
        generated = template_dual_payload(
            relation_skeletons,
            frontier_classification,
        )
        if args.assert_expected:
            assert_expected_template_dual_counts(generated)
    except (AssertionError, KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        summary = _summary(artifact, {}, [str(exc)])
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True))
        else:
            print(f"FAILED: {exc}", file=sys.stderr)
        return 1

    if args.write:
        write_json(generated, out)
        if not args.check:
            summary = _summary(out, generated, [])
            if args.json:
                print(json.dumps(summary, indent=2, sort_keys=True))
            else:
                print(f"wrote {display_path(out, ROOT)}")
            return 0

    payload = generated
    errors: list[str] = []
    if args.check:
        try:
            payload = _load(artifact)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
            payload = {}
        if isinstance(payload, dict):
            if payload.get("schema") != SCHEMA:
                errors.append(
                    f"schema mismatch: expected {SCHEMA!r}, got {payload.get('schema')!r}"
                )
            if payload != generated:
                errors.append("artifact does not match regenerated exact dual payload")
            if args.assert_expected:
                try:
                    assert_expected_template_dual_counts(payload)
                except (AssertionError, KeyError, TypeError, ValueError) as exc:
                    errors.append(f"stored expected-count check failed: {exc}")
        else:
            errors.append("artifact top level must be an object")

    summary = _summary(artifact if args.check else out, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        for error in errors:
            print(f"FAILED: {error}", file=sys.stderr)
    else:
        print(
            "OK: exact template duals verified "
            f"({summary['skeleton_count']} skeletons, "
            f"{summary['covered_assignment_count']} transformed assignments)"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
