#!/usr/bin/env python3
"""Generate or check the n=9 frontier motif-classification diagnostic."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
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
    DEFAULT_ARTIFACT as DEFAULT_TEMPLATES,
    validate_payload as validate_template_payload,
)
from check_n9_vertex_circle_local_core_packet import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_PACKET,
    validate_payload as validate_packet_payload,
)
from erdos97.n9_vertex_circle_frontier_motif_classification import (  # noqa: E402
    CLAIM_SCOPE,
    PROVENANCE,
    SCHEMA,
    STATUS,
    TRUST,
    assert_expected_classification_counts,
    classification_source_artifacts,
    compact_to_indexed_rows,
    frontier_motif_classification_payload,
    replay_status,
    transform_compact_rows,
)
from erdos97.n9_vertex_circle_obstruction_shapes import (  # noqa: E402
    assert_expected_motif_family_counts,
    canonical_dihedral_rows_with_map,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)
DEFAULT_MOTIF_FAMILIES = ROOT / "data" / "certificates" / "n9_vertex_circle_motif_families.json"
EXPECTED_TOP_LEVEL_KEYS = {
    "assignment_count",
    "assignments",
    "claim_scope",
    "core_size_assignment_counts",
    "cyclic_order",
    "families",
    "family_count",
    "family_orbit_size_counts",
    "family_status_counts",
    "interpretation",
    "n",
    "orbit_size_sum",
    "pre_vertex_circle_search",
    "provenance",
    "row_size",
    "schema",
    "source_artifacts",
    "status",
    "status_counts",
    "template_assignment_counts",
    "template_count",
    "template_status_counts",
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
    motif_path: Path = DEFAULT_MOTIF_FAMILIES,
    packet_path: Path = DEFAULT_PACKET,
    templates_path: Path = DEFAULT_TEMPLATES,
) -> dict[str, Any]:
    """Load the source artifacts used by the classification checker."""

    return {
        "motif": load_artifact(_resolve(motif_path)),
        "packet": load_artifact(_resolve(packet_path)),
        "templates": load_artifact(_resolve(templates_path)),
    }


def _validate_sources(source_payloads: dict[str, Any], errors: list[str]) -> None:
    motif = source_payloads.get("motif")
    packet = source_payloads.get("packet")
    templates = source_payloads.get("templates")
    if not isinstance(motif, dict):
        errors.append("source motif payload must be an object")
    else:
        try:
            assert_expected_motif_family_counts(motif)
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"source motif-family artifact invalid: {exc}")
    if not isinstance(packet, dict):
        errors.append("source packet payload must be an object")
    else:
        packet_errors = validate_packet_payload(packet, recompute=False)
        if packet_errors:
            errors.extend(f"source local-core packet invalid: {error}" for error in packet_errors)
    if not isinstance(templates, dict):
        errors.append("source template payload must be an object")
    else:
        template_errors = validate_template_payload(
            templates,
            packet=packet,
            recompute=False,
        )
        if template_errors:
            errors.extend(f"source template artifact invalid: {error}" for error in template_errors)


def _family_maps(
    source_payloads: dict[str, Any],
) -> tuple[dict[Any, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    motif = source_payloads["motif"]
    packet = source_payloads["packet"]
    templates = source_payloads["templates"]
    family_rows = motif["dihedral_incidence_families"]["families"]
    family_by_canonical = {
        tuple(tuple(row) for row in family["representative_selected_rows"]): family
        for family in family_rows
    }
    packet_by_family = {
        str(certificate["family_id"]): certificate
        for certificate in packet["certificates"]
    }
    template_by_family = {
        str(family["family_id"]): family
        for family in templates["families"]
    }
    return family_by_canonical, packet_by_family, template_by_family


def _validate_family_rows(
    payload: dict[str, Any],
    source_payloads: dict[str, Any],
    errors: list[str],
) -> None:
    raw_families = payload.get("families")
    raw_assignments = payload.get("assignments")
    if not isinstance(raw_families, list):
        errors.append("families must be a list")
        return
    if not isinstance(raw_assignments, list):
        errors.append("assignments must be a list")
        return
    _, packet_by_family, template_by_family = _family_maps(source_payloads)
    assignment_counts = Counter(
        str(row.get("family_id"))
        for row in raw_assignments
        if isinstance(row, dict)
    )
    seen_family_ids: set[str] = set()
    total_orbit_size = 0
    for index, raw_family in enumerate(raw_families):
        if not isinstance(raw_family, dict):
            errors.append(f"family {index} must be an object")
            continue
        family_id = str(raw_family.get("family_id"))
        if family_id in seen_family_ids:
            errors.append(f"duplicate family id {family_id}")
        seen_family_ids.add(family_id)
        packet = packet_by_family.get(family_id)
        template = template_by_family.get(family_id)
        if packet is None:
            errors.append(f"family {family_id} missing from source packet")
            continue
        if template is None:
            errors.append(f"family {family_id} missing from source template artifact")
            continue
        for key, expected in (
            ("status", packet["status"]),
            ("core_size", int(packet["core_size"])),
            ("template_id", template["template_id"]),
        ):
            if raw_family.get(key) != expected:
                errors.append(
                    f"family {family_id} {key} mismatch: "
                    f"expected {expected!r}, got {raw_family.get(key)!r}"
                )
        assignment_count = int(raw_family.get("assignment_count", -1))
        orbit_size = int(raw_family.get("orbit_size", -1))
        total_orbit_size += orbit_size
        if assignment_count != assignment_counts[family_id]:
            errors.append(f"family {family_id} assignment_count does not match rows")
        if assignment_count != orbit_size:
            errors.append(f"family {family_id} assignment_count does not match orbit_size")
    if len(seen_family_ids) != payload.get("family_count"):
        errors.append("family_count does not match family rows")
    if total_orbit_size != payload.get("orbit_size_sum"):
        errors.append("orbit_size_sum does not match family rows")


def _assignment_row_map(row: dict[str, Any]) -> dict[int, list[int]]:
    return {int(item[0]): sorted(int(witness) for witness in item[1:]) for item in row["selected_rows"]}


def _validate_assignment_rows(
    payload: dict[str, Any],
    source_payloads: dict[str, Any],
    errors: list[str],
) -> None:
    raw_assignments = payload.get("assignments")
    if not isinstance(raw_assignments, list):
        errors.append("assignments must be a list")
        return
    family_by_canonical, packet_by_family, template_by_family = _family_maps(source_payloads)
    status_counts: Counter[str] = Counter()
    template_counts: Counter[str] = Counter()
    core_size_counts: Counter[int] = Counter()
    assignment_ids: list[str] = []
    for index, raw_assignment in enumerate(raw_assignments, start=1):
        if not isinstance(raw_assignment, dict):
            errors.append(f"assignment {index} must be an object")
            continue
        assignment_id = raw_assignment.get("assignment_id")
        expected_assignment_id = f"A{index:03d}"
        if assignment_id != expected_assignment_id:
            errors.append(
                f"assignment id mismatch at row {index}: "
                f"expected {expected_assignment_id}, got {assignment_id!r}"
            )
        if isinstance(assignment_id, str):
            assignment_ids.append(assignment_id)
        try:
            selected_rows = compact_to_indexed_rows(raw_assignment["selected_rows"])
            canonical_rows, label_map = canonical_dihedral_rows_with_map(selected_rows)
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{assignment_id or index} selected rows invalid: {exc}")
            continue
        family = family_by_canonical.get(canonical_rows)
        if family is None:
            errors.append(f"{assignment_id or index} does not match a source family")
            continue
        family_id = str(family["family_id"])
        packet = packet_by_family[family_id]
        template = template_by_family[family_id]
        expected_core_rows = transform_compact_rows(
            packet["compact_selected_rows"],
            _inverse_map(label_map),
        )
        selected_row_map = _assignment_row_map(raw_assignment)
        core_rows = raw_assignment.get("core_selected_rows")
        if core_rows != expected_core_rows:
            errors.append(f"{assignment_id or index} core rows do not match source family map")
        elif any(
            selected_row_map.get(int(row[0])) != sorted(int(witness) for witness in row[1:])
            for row in core_rows
        ):
            errors.append(f"{assignment_id or index} core rows are not selected rows")
        expected_values = {
            "family_id": family_id,
            "template_id": template["template_id"],
            "status": family["status"],
            "core_size": int(packet["core_size"]),
            "to_canonical_label_map": [int(label) for label in label_map],
        }
        for key, expected in expected_values.items():
            if raw_assignment.get(key) != expected:
                errors.append(
                    f"{assignment_id or index} {key} mismatch: "
                    f"expected {expected!r}, got {raw_assignment.get(key)!r}"
                )
        try:
            full_status = replay_status(raw_assignment["selected_rows"])
            core_status = replay_status(core_rows)
        except (TypeError, ValueError) as exc:
            errors.append(f"{assignment_id or index} replay failed: {exc}")
            continue
        status = str(raw_assignment.get("status"))
        if full_status != status:
            errors.append(f"{assignment_id or index} full replay status mismatch")
        if core_status != status:
            errors.append(f"{assignment_id or index} core replay status mismatch")
        status_counts[status] += 1
        template_counts[str(raw_assignment.get("template_id"))] += 1
        core_size_counts[int(raw_assignment.get("core_size", -1))] += 1
    if len(assignment_ids) != len(set(assignment_ids)):
        errors.append("duplicate assignment ids")
    expected_status_counts = {
        status: int(status_counts[status]) for status in sorted(status_counts)
    }
    if payload.get("status_counts") != expected_status_counts:
        errors.append("status_counts does not match assignment rows")
    expected_template_counts = {
        template_id: int(template_counts[template_id])
        for template_id in sorted(template_counts)
    }
    if payload.get("template_assignment_counts") != expected_template_counts:
        errors.append("template_assignment_counts does not match assignment rows")
    expected_core_counts = {
        str(size): int(core_size_counts[size])
        for size in sorted(core_size_counts)
        if size >= 0
    }
    if payload.get("core_size_assignment_counts") != expected_core_counts:
        errors.append("core_size_assignment_counts does not match assignment rows")


def _inverse_map(label_map: Sequence[int]) -> list[int]:
    inverse = [0] * len(label_map)
    for source, target in enumerate(label_map):
        inverse[int(target)] = int(source)
    return inverse


def validate_payload(
    payload: Any,
    *,
    source_payloads: dict[str, Any] | None = None,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a frontier motif-classification artifact."""

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
        "assignment_count": 184,
        "family_count": 16,
        "orbit_size_sum": 184,
        "template_count": 12,
        "provenance": PROVENANCE,
    }
    for key, expected in expected_meta.items():
        expect_equal(errors, key, payload.get(key), expected)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list) or not all(
        isinstance(item, str) for item in interpretation
    ):
        errors.append("interpretation must be a list of strings")
    elif "No proof of the n=9 case is claimed." not in interpretation:
        errors.append("interpretation must preserve the no-proof statement")

    _validate_sources(source_payloads, errors)
    if not errors:
        expect_equal(
            errors,
            "source_artifacts",
            payload.get("source_artifacts"),
            classification_source_artifacts(
                source_payloads["motif"],
                source_payloads["packet"],
                source_payloads["templates"],
            ),
        )
        _validate_family_rows(payload, source_payloads, errors)
        _validate_assignment_rows(payload, source_payloads, errors)

    try:
        assert_expected_classification_counts(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected classification counts failed: {exc}")

    if recompute and not errors:
        try:
            expected_payload = frontier_motif_classification_payload(
                source_payloads["motif"],
                source_payloads["packet"],
                source_payloads["templates"],
            )
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"recomputed classification failed: {exc}")
        else:
            expect_equal(errors, "frontier motif classification", payload, expected_payload)
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
        "assignment_count": object_payload.get("assignment_count"),
        "family_count": object_payload.get("family_count"),
        "template_count": object_payload.get("template_count"),
        "status_counts": object_payload.get("status_counts"),
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
    parser.add_argument("--motif-families", type=Path, default=DEFAULT_MOTIF_FAMILIES)
    parser.add_argument("--local-core-packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--core-templates", type=Path, default=DEFAULT_TEMPLATES)
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
            motif_path=args.motif_families,
            packet_path=args.local_core_packet,
            templates_path=args.core_templates,
        )
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAILED: could not load source artifacts: {exc}", file=sys.stderr)
        return 1

    if args.write:
        payload = frontier_motif_classification_payload(
            sources["motif"],
            sources["packet"],
            sources["templates"],
        )
        if args.assert_expected:
            assert_expected_classification_counts(payload)
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
        print("n=9 vertex-circle frontier motif classification")
        print(f"artifact: {summary['artifact']}")
        print(f"assignments: {summary['assignment_count']}")
        print(f"families: {summary['family_count']}")
        print(f"templates: {summary['template_count']}")
        print(f"status counts: {summary['status_counts']}")
        if args.check or args.assert_expected:
            print("OK: frontier motif classification checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
