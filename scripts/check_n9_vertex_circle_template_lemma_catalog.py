#!/usr/bin/env python3
"""Generate or check the n=9 vertex-circle template lemma-candidate catalog."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_n9_vertex_circle_core_templates import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_CORE_TEMPLATES,
    validate_payload as validate_core_template_payload,
)
from check_n9_vertex_circle_self_edge_template_packet import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SELF_EDGE_PACKET,
    validate_payload as validate_self_edge_packet,
)
from check_n9_vertex_circle_strict_cycle_template_packet import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_STRICT_CYCLE_PACKET,
    validate_payload as validate_strict_cycle_packet,
)
from erdos97.n9_vertex_circle_template_lemma_catalog import (  # noqa: E402
    CLAIM_SCOPE,
    PROVENANCE,
    SCHEMA,
    STATUS,
    TRUST,
    assert_expected_template_lemma_catalog_counts,
    template_lemma_catalog_payload,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_template_lemma_catalog.json"
)
EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "covered_assignment_count",
    "cyclic_order",
    "family_core_size_counts",
    "family_count",
    "family_status_counts",
    "interpretation",
    "n",
    "provenance",
    "row_size",
    "schema",
    "self_edge_assignment_count",
    "self_edge_family_count",
    "self_edge_template_count",
    "source_artifacts",
    "source_assignment_count",
    "status",
    "status_assignment_counts",
    "strict_cycle_assignment_count",
    "strict_cycle_family_count",
    "strict_cycle_template_count",
    "template_assignment_counts",
    "template_core_size_counts",
    "template_count",
    "template_family_counts",
    "template_status_counts",
    "templates",
    "trust",
}


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


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a mismatch error when values differ."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def load_source_payloads(
    *,
    self_edge_packet_path: Path = DEFAULT_SELF_EDGE_PACKET,
    strict_cycle_packet_path: Path = DEFAULT_STRICT_CYCLE_PACKET,
    core_templates_path: Path = DEFAULT_CORE_TEMPLATES,
) -> dict[str, Any]:
    """Load the source artifacts used by the template catalog."""

    return {
        "self_edge_packet": load_artifact(_resolve(self_edge_packet_path)),
        "strict_cycle_packet": load_artifact(_resolve(strict_cycle_packet_path)),
        "core_templates": load_artifact(_resolve(core_templates_path)),
    }


def _validate_sources(source_payloads: dict[str, Any], errors: list[str]) -> None:
    self_edge = source_payloads.get("self_edge_packet")
    strict_cycle = source_payloads.get("strict_cycle_packet")
    core_templates = source_payloads.get("core_templates")
    if not isinstance(self_edge, dict):
        errors.append("source self-edge template packet must be an object")
    else:
        errors.extend(
            f"source self-edge template packet invalid: {error}"
            for error in validate_self_edge_packet(self_edge, recompute=False)
        )
    if not isinstance(strict_cycle, dict):
        errors.append("source strict-cycle template packet must be an object")
    else:
        errors.extend(
            f"source strict-cycle template packet invalid: {error}"
            for error in validate_strict_cycle_packet(strict_cycle, recompute=False)
        )
    if not isinstance(core_templates, dict):
        errors.append("source core-template payload must be an object")
    else:
        errors.extend(
            f"source core templates invalid: {error}"
            for error in validate_core_template_payload(core_templates, recompute=False)
        )


def _expected_payload(
    source_payloads: dict[str, Any],
    errors: list[str],
) -> dict[str, Any] | None:
    try:
        return template_lemma_catalog_payload(
            source_payloads["self_edge_packet"],
            source_payloads["strict_cycle_packet"],
            source_payloads["core_templates"],
        )
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"source-bound template lemma catalog failed: {exc}")
        return None


def _validate_catalog_rows(
    payload: dict[str, Any],
    expected_payload: dict[str, Any],
    errors: list[str],
) -> None:
    templates = payload.get("templates")
    expected_templates = expected_payload.get("templates")
    if not isinstance(templates, list):
        errors.append("templates must be a list")
        return
    if not isinstance(expected_templates, list):
        errors.append("expected templates must be a list")
        return
    expect_equal(errors, "templates", templates, expected_templates)

    template_ids: list[str] = []
    assignment_ids: list[str] = []
    family_ids: list[str] = []
    assignment_counts: dict[str, int] = {}
    family_counts: dict[str, int] = {}
    status_assignment_counts: dict[str, int] = {"self_edge": 0, "strict_cycle": 0}
    for index, record in enumerate(templates):
        if not isinstance(record, dict):
            errors.append(f"template record {index} must be an object")
            continue
        template_id = str(record.get("template_id"))
        template_ids.append(template_id)
        status = str(record.get("status"))
        if status not in status_assignment_counts:
            errors.append(f"template {template_id} has unexpected status {status!r}")
            continue
        coverage = record.get("coverage")
        if not isinstance(coverage, dict):
            errors.append(f"template {template_id} coverage must be an object")
            continue
        ids = coverage.get("assignment_ids")
        if not isinstance(ids, list) or not all(isinstance(item, str) for item in ids):
            errors.append(f"template {template_id} assignment_ids must be a string list")
            ids = []
        assignment_count = int(coverage.get("assignment_count", -1))
        if len(ids) != assignment_count:
            errors.append(f"template {template_id} assignment_ids count mismatch")
        assignment_ids.extend(ids)
        assignment_counts[template_id] = assignment_count
        status_assignment_counts[status] += assignment_count
        families = coverage.get("families")
        if not isinstance(families, list) or not all(
            isinstance(item, str) for item in families
        ):
            errors.append(f"template {template_id} families must be a string list")
            families = []
        family_counts[template_id] = int(coverage.get("family_count", -1))
        family_summaries = record.get("family_summaries")
        if not isinstance(family_summaries, list):
            errors.append(f"template {template_id} family_summaries must be a list")
            continue
        if sorted(families) != sorted(
            str(summary.get("family_id"))
            for summary in family_summaries
            if isinstance(summary, dict)
        ):
            errors.append(f"template {template_id} family summary list mismatch")
        family_ids.extend(families)
        conclusion = record.get("conclusion_shape")
        if not isinstance(conclusion, dict) or conclusion.get("kind") != status:
            errors.append(f"template {template_id} conclusion kind mismatch")
    if len(template_ids) != len(set(template_ids)):
        errors.append("duplicate template ids")
    if len(assignment_ids) != len(set(assignment_ids)):
        errors.append("duplicate assignment ids across catalog")
    if len(family_ids) != len(set(family_ids)):
        errors.append("duplicate families across catalog")
    expect_equal(
        errors,
        "covered_assignment_count",
        payload.get("covered_assignment_count"),
        len(assignment_ids),
    )
    expect_equal(
        errors,
        "family_count",
        payload.get("family_count"),
        len(family_ids),
    )
    expect_equal(
        errors,
        "template_assignment_counts",
        payload.get("template_assignment_counts"),
        assignment_counts,
    )
    expect_equal(
        errors,
        "template_family_counts",
        payload.get("template_family_counts"),
        family_counts,
    )
    expect_equal(
        errors,
        "status_assignment_counts",
        payload.get("status_assignment_counts"),
        status_assignment_counts,
    )


def validate_payload(
    payload: Any,
    *,
    source_payloads: dict[str, Any] | None = None,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a template lemma-candidate catalog."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    if source_payloads is None:
        try:
            source_payloads = load_source_payloads()
        except (OSError, json.JSONDecodeError) as exc:
            return [f"could not load source artifacts: {exc}"]

    errors: list[str] = []
    if set(payload) != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(payload)!r}"
        )

    expected_meta = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": 9,
        "row_size": 4,
        "cyclic_order": list(range(9)),
        "source_assignment_count": 184,
        "covered_assignment_count": 184,
        "self_edge_assignment_count": 158,
        "strict_cycle_assignment_count": 26,
        "template_count": 12,
        "self_edge_template_count": 9,
        "strict_cycle_template_count": 3,
        "family_count": 16,
        "self_edge_family_count": 13,
        "strict_cycle_family_count": 3,
        "template_status_counts": {"self_edge": 9, "strict_cycle": 3},
        "family_status_counts": {"self_edge": 13, "strict_cycle": 3},
        "status_assignment_counts": {"self_edge": 158, "strict_cycle": 26},
        "template_core_size_counts": {"3": 2, "4": 5, "5": 2, "6": 3},
        "family_core_size_counts": {"3": 5, "4": 6, "5": 2, "6": 3},
        "provenance": PROVENANCE,
    }
    for key, expected in expected_meta.items():
        expect_equal(errors, key, payload.get(key), expected)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list) or not all(
        isinstance(item, str) for item in interpretation
    ):
        errors.append("interpretation must be a list of strings")
    else:
        if "No proof of the n=9 case is claimed." not in interpretation:
            errors.append("interpretation must preserve the no-proof statement")
        if not any("not theorem names" in item for item in interpretation):
            errors.append("interpretation must say template records are not theorem names")

    _validate_sources(source_payloads, errors)
    expected_payload = None if errors else _expected_payload(source_payloads, errors)
    if expected_payload is not None:
        expect_equal(errors, "source_artifacts", payload.get("source_artifacts"), expected_payload["source_artifacts"])
        _validate_catalog_rows(payload, expected_payload, errors)

    try:
        assert_expected_template_lemma_catalog_counts(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected template lemma catalog counts failed: {exc}")

    if recompute and expected_payload is not None and not errors:
        expect_equal(errors, "template lemma catalog", payload, expected_payload)
    return errors


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    return {
        "ok": not errors,
        "artifact": display_path(path, ROOT),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "covered_assignment_count": object_payload.get("covered_assignment_count"),
        "template_count": object_payload.get("template_count"),
        "family_count": object_payload.get("family_count"),
        "template_status_counts": object_payload.get("template_status_counts"),
        "status_assignment_counts": object_payload.get("status_assignment_counts"),
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write generated artifact")
    parser.add_argument("--check", action="store_true", help="validate an existing artifact")
    parser.add_argument("--json", action="store_true", help="print stable JSON summary")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--self-edge-packet", type=Path, default=DEFAULT_SELF_EDGE_PACKET)
    parser.add_argument("--strict-cycle-packet", type=Path, default=DEFAULT_STRICT_CYCLE_PACKET)
    parser.add_argument("--core-templates", type=Path, default=DEFAULT_CORE_TEMPLATES)
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
        sources = load_source_payloads(
            self_edge_packet_path=args.self_edge_packet,
            strict_cycle_packet_path=args.strict_cycle_packet,
            core_templates_path=args.core_templates,
        )
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAILED: could not load source artifacts: {exc}", file=sys.stderr)
        return 1

    if args.write:
        payload = template_lemma_catalog_payload(
            sources["self_edge_packet"],
            sources["strict_cycle_packet"],
            sources["core_templates"],
        )
        if args.assert_expected:
            assert_expected_template_lemma_catalog_counts(payload)
        write_json(payload, out)
        if not args.check:
            if args.json:
                print(json.dumps(summary_payload(out, payload, []), indent=2, sort_keys=True))
            else:
                print(f"wrote {display_path(out, ROOT)}")
            return 0

    try:
        payload = load_artifact(artifact)
        errors = validate_payload(
            payload,
            source_payloads=sources,
            recompute=args.check or args.assert_expected,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact, ROOT)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 vertex-circle template lemma-candidate catalog")
        print(f"artifact: {summary['artifact']}")
        print(f"covered assignments: {summary['covered_assignment_count']}")
        print(f"templates: {summary['template_count']}")
        print(f"families: {summary['family_count']}")
        print(f"template statuses: {summary['template_status_counts']}")
        if args.check or args.assert_expected:
            print("OK: template lemma-candidate catalog checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
