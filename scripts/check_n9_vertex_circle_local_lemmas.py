#!/usr/bin/env python3
"""Scan n=9 vertex-circle packets for reusable local lemma instances."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n9_vertex_circle_local_lemmas import (  # noqa: E402
    CLAIM_SCOPE,
    PROVENANCE,
    SCHEMA,
    STATUS,
    TRUST,
    assert_expected_local_lemma_scan,
    local_lemma_scan_payload,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_SELF_EDGE_PACKET = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_self_edge_template_packet.json"
)
DEFAULT_STRICT_CYCLE_PACKET = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_strict_cycle_template_packet.json"
)
DEFAULT_T02_PACKET = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_t02_self_edge_lemma_packet.json"
)
DEFAULT_T03_PACKET = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_t03_self_edge_lemma_packet.json"
)
DEFAULT_T04_PACKET = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_t04_self_edge_lemma_packet.json"
)
DEFAULT_T10_PACKET = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_t10_strict_cycle_lemma_packet.json"
)
DEFAULT_T11_PACKET = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_t11_strict_cycle_lemma_packet.json"
)
DEFAULT_T12_PACKET = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_t12_strict_cycle_lemma_packet.json"
)
DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "n9_vertex_circle_local_lemmas.json"


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def scan_payload(
    *,
    self_edge_packet_path: Path = DEFAULT_SELF_EDGE_PACKET,
    strict_cycle_packet_path: Path = DEFAULT_STRICT_CYCLE_PACKET,
    t02_packet_path: Path = DEFAULT_T02_PACKET,
    t03_packet_path: Path = DEFAULT_T03_PACKET,
    t04_packet_path: Path = DEFAULT_T04_PACKET,
    t10_packet_path: Path = DEFAULT_T10_PACKET,
    t11_packet_path: Path = DEFAULT_T11_PACKET,
    t12_packet_path: Path = DEFAULT_T12_PACKET,
) -> dict[str, Any]:
    """Load source artifacts and return the local-lemma scan payload."""

    return local_lemma_scan_payload(
        load_artifact(self_edge_packet_path),
        load_artifact(strict_cycle_packet_path),
        focused_packets={
            "T02": load_artifact(t02_packet_path),
            "T03": load_artifact(t03_packet_path),
            "T04": load_artifact(t04_packet_path),
            "T10": load_artifact(t10_packet_path),
            "T11": load_artifact(t11_packet_path),
            "T12": load_artifact(t12_packet_path),
        },
    )


def validate_payload(payload: Any, expected_payload: dict[str, Any]) -> list[str]:
    """Return validation errors for a stored local-lemma scan artifact."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    errors: list[str] = []
    expected_meta = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": 9,
        "cyclic_order": list(range(9)),
        "provenance": PROVENANCE,
    }
    for key, expected in expected_meta.items():
        if payload.get(key) != expected:
            errors.append(f"{key} mismatch: expected {expected!r}, got {payload.get(key)!r}")

    try:
        assert_expected_local_lemma_scan(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected local-lemma scan failed: {exc}")

    if payload != expected_payload:
        errors.append("local-lemma scan payload mismatch")
    return errors


def summary_payload(path: Path, payload: Any, errors: list[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    coverage = object_payload.get("coverage_summary", {})
    if not isinstance(coverage, dict):
        coverage = {}
    lemmas = object_payload.get("lemmas", [])
    return {
        "ok": not errors,
        "artifact": display_path(path, ROOT),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "lemma_count": len(lemmas) if isinstance(lemmas, list) else None,
        "source_family_count": coverage.get("source_family_count"),
        "source_assignment_count": coverage.get("source_assignment_count"),
        "covered_family_count": coverage.get("covered_family_count"),
        "covered_assignment_count": coverage.get("covered_assignment_count"),
        "uncovered_family_count": coverage.get("uncovered_family_count"),
        "uncovered_assignment_count": coverage.get("uncovered_assignment_count"),
        "validation_errors": errors,
    }


def summary_lines(payload: dict[str, Any]) -> list[str]:
    """Return human-readable scan summary lines."""

    coverage = payload["coverage_summary"]
    lines = [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"source families: {coverage['source_family_count']}",
        f"source assignments: {coverage['source_assignment_count']}",
        f"covered families: {coverage['covered_family_count']}",
        f"covered assignments: {coverage['covered_assignment_count']}",
        f"uncovered families: {coverage['uncovered_family_count']}",
        f"uncovered assignments: {coverage['uncovered_assignment_count']}",
        f"uncovered family ids: {','.join(coverage['uncovered_family_ids'])}",
    ]
    for lemma in payload["lemmas"]:
        lines.append(
            f"{lemma['lemma_id']}: "
            f"{lemma['instance_count']} instances, "
            f"{lemma['covered_assignment_count']} assignments, "
            f"families {','.join(lemma['family_ids'])}"
        )
    for item in payload["focused_note_crosscheck"]:
        lines.append(
            f"focused {item['template_id']}: {item['check_status']} "
            f"against {item['proof_note_path']} "
            f"families {','.join(item['family_ids'])}"
        )
    special = payload["direct_two_row_nested_spoke_special_case"]
    lines.append(
        f"{special['lemma_id']}: {special['instance_count']} exact direct instances"
    )
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write generated artifact")
    parser.add_argument("--check", action="store_true", help="validate an existing artifact")
    parser.add_argument(
        "--self-edge-packet",
        type=Path,
        default=DEFAULT_SELF_EDGE_PACKET,
        help="Path to n9 self-edge template packet JSON.",
    )
    parser.add_argument(
        "--strict-cycle-packet",
        type=Path,
        default=DEFAULT_STRICT_CYCLE_PACKET,
        help="Path to n9 strict-cycle template packet JSON.",
    )
    parser.add_argument(
        "--t02-packet",
        type=Path,
        default=DEFAULT_T02_PACKET,
        help="Path to focused T02 self-edge lemma packet JSON.",
    )
    parser.add_argument(
        "--t03-packet",
        type=Path,
        default=DEFAULT_T03_PACKET,
        help="Path to focused T03 self-edge lemma packet JSON.",
    )
    parser.add_argument(
        "--t10-packet",
        type=Path,
        default=DEFAULT_T10_PACKET,
        help="Path to focused T10 strict-cycle lemma packet JSON.",
    )
    parser.add_argument(
        "--t04-packet",
        type=Path,
        default=DEFAULT_T04_PACKET,
        help="Path to focused T04 self-edge lemma packet JSON.",
    )
    parser.add_argument(
        "--t11-packet",
        type=Path,
        default=DEFAULT_T11_PACKET,
        help="Path to focused T11 strict-cycle lemma packet JSON.",
    )
    parser.add_argument(
        "--t12-packet",
        type=Path,
        default=DEFAULT_T12_PACKET,
        help="Path to focused T12 strict-cycle lemma packet JSON.",
    )
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="Assert the currently expected local-lemma scan counts.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args(argv)

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

    payload = scan_payload(
        self_edge_packet_path=_resolve(args.self_edge_packet),
        strict_cycle_packet_path=_resolve(args.strict_cycle_packet),
        t02_packet_path=_resolve(args.t02_packet),
        t03_packet_path=_resolve(args.t03_packet),
        t04_packet_path=_resolve(args.t04_packet),
        t10_packet_path=_resolve(args.t10_packet),
        t11_packet_path=_resolve(args.t11_packet),
        t12_packet_path=_resolve(args.t12_packet),
    )
    if args.assert_expected:
        assert_expected_local_lemma_scan(payload)

    if args.write:
        write_json(payload, out)
        if not args.check:
            if args.json:
                print(json.dumps(summary_payload(out, payload, []), indent=2, sort_keys=True))
            else:
                print(f"wrote {display_path(out, ROOT)}")
            return 0

    if args.check:
        try:
            stored_payload = load_artifact(artifact)
            errors = validate_payload(stored_payload, payload)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            stored_payload = {}
            errors = [str(exc)]

        summary = summary_payload(artifact, stored_payload, errors)
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True))
        elif errors:
            print(f"FAILED: {display_path(artifact, ROOT)}", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
        else:
            print("n=9 vertex-circle local-lemma scan artifact")
            print(f"artifact: {summary['artifact']}")
            print(f"covered assignments: {summary['covered_assignment_count']}")
            print(f"covered families: {summary['covered_family_count']}")
            print(f"lemmas: {summary['lemma_count']}")
            print("OK: local-lemma scan artifact checks passed")
        return 1 if errors else 0

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("\n".join(summary_lines(payload)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
