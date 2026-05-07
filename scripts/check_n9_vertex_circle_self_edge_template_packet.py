#!/usr/bin/env python3
"""Generate or check the n=9 self-edge template packet diagnostic."""

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
    DEFAULT_ARTIFACT as DEFAULT_TEMPLATES,
    validate_payload as validate_template_payload,
)
from check_n9_vertex_circle_self_edge_path_join import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_PATH_JOIN,
    validate_payload as validate_path_join_payload,
)
from erdos97.n9_vertex_circle_obstruction_shapes import (  # noqa: E402
    assert_expected_local_core_counts,
)
from erdos97.n9_vertex_circle_self_edge_path_join import (  # noqa: E402
    validate_equality_path,
)
from erdos97.n9_vertex_circle_self_edge_template_packet import (  # noqa: E402
    CLAIM_SCOPE,
    PROVENANCE,
    SCHEMA,
    STATUS,
    TRUST,
    assert_expected_self_edge_template_packet_counts,
    self_edge_template_packet_payload,
    self_edge_template_packet_source_artifacts,
)
from erdos97.path_display import display_path  # noqa: E402
from erdos97.vertex_circle_quotient_replay import pair  # noqa: E402

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_self_edge_template_packet.json"
)
DEFAULT_LOCAL_CORES = ROOT / "data" / "certificates" / "n9_vertex_circle_local_cores.json"
EXPECTED_TOP_LEVEL_KEYS = {
    "assignment_core_size_counts",
    "claim_scope",
    "cyclic_order",
    "interpretation",
    "n",
    "provenance",
    "row_size",
    "schema",
    "self_edge_assignment_count",
    "self_edge_family_count",
    "self_edge_template_count",
    "path_length_counts",
    "shared_endpoint_counts",
    "source_artifacts",
    "source_assignment_count",
    "status",
    "strict_cycle_assignment_count",
    "template_assignment_counts",
    "template_core_size_counts",
    "template_family_count_distribution",
    "template_family_counts",
    "template_path_length_counts",
    "template_strict_edge_count_counts",
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
    local_cores_path: Path = DEFAULT_LOCAL_CORES,
    path_join_path: Path = DEFAULT_PATH_JOIN,
    templates_path: Path = DEFAULT_TEMPLATES,
) -> dict[str, Any]:
    """Load the source artifacts used by the self-edge template packet."""

    return {
        "local_cores": load_artifact(_resolve(local_cores_path)),
        "path_join": load_artifact(_resolve(path_join_path)),
        "templates": load_artifact(_resolve(templates_path)),
    }


def _validate_sources(source_payloads: dict[str, Any], errors: list[str]) -> None:
    local_cores = source_payloads.get("local_cores")
    path_join = source_payloads.get("path_join")
    templates = source_payloads.get("templates")
    if not isinstance(local_cores, dict):
        errors.append("source local-core payload must be an object")
    else:
        try:
            assert_expected_local_core_counts(local_cores)
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"source local-core artifact invalid: {exc}")
    if not isinstance(path_join, dict):
        errors.append("source self-edge path-join payload must be an object")
    else:
        path_join_errors = validate_path_join_payload(path_join, recompute=False)
        if path_join_errors:
            errors.extend(
                f"source self-edge path join invalid: {error}"
                for error in path_join_errors
            )
    if not isinstance(templates, dict):
        errors.append("source template payload must be an object")
    else:
        template_errors = validate_template_payload(templates, recompute=False)
        if template_errors:
            errors.extend(f"source core templates invalid: {error}" for error in template_errors)


def _validate_family_record(record: dict[str, Any]) -> None:
    if record.get("status") != "self_edge":
        raise AssertionError("family record status must be self_edge")
    equality = record["distance_equality"]
    edge = record["strict_inequality"]
    if pair(*equality["start_pair"]) != pair(*edge["outer_pair"]):
        raise AssertionError("family equality must start at outer pair")
    if pair(*equality["end_pair"]) != pair(*edge["inner_pair"]):
        raise AssertionError("family equality must end at inner pair")
    validate_equality_path(record["core_selected_rows"], equality)


def _expected_template_rows(
    source_payloads: dict[str, Any],
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    try:
        expected_payload = self_edge_template_packet_payload(
            source_payloads["local_cores"],
            source_payloads["path_join"],
            source_payloads["templates"],
        )
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"source-bound self-edge template packet failed: {exc}")
        return {}
    return {
        str(template["template_id"]): template
        for template in expected_payload.get("templates", [])
        if isinstance(template, dict)
    }


def _validate_source_bound_template(
    template: dict[str, Any],
    expected_template: dict[str, Any],
    errors: list[str],
) -> None:
    template_id = str(template.get("template_id"))
    for key in (
        "template_key",
        "status",
        "core_size",
        "strict_edge_count",
        "family_count",
        "assignment_count",
        "orbit_size_sum",
        "assignment_ids",
        "families",
        "path_length_counts",
        "shared_endpoint_counts",
        "selected_path_shape_counts",
        "self_edge_shape_counts",
    ):
        expect_equal(
            errors,
            f"template {template_id} {key}",
            template.get(key),
            expected_template.get(key),
        )

    expected_families = {
        str(record["family_id"]): record
        for record in expected_template.get("family_records", [])
        if isinstance(record, dict)
    }
    for family_record in template.get("family_records", []):
        if not isinstance(family_record, dict):
            continue
        family_id = str(family_record.get("family_id"))
        expected_family = expected_families.get(family_id)
        if expected_family is None:
            errors.append(f"template {template_id} unexpected family record {family_id}")
            continue
        for key in (
            "template_id",
            "status",
            "assignment_count",
            "orbit_size",
            "core_size",
            "path_length",
            "core_selected_rows",
            "strict_inequality",
            "distance_equality",
            "contradiction",
        ):
            expect_equal(
                errors,
                f"template {template_id} family {family_id} {key}",
                family_record.get(key),
                expected_family.get(key),
            )


def _validate_template_rows(
    payload: dict[str, Any],
    errors: list[str],
    *,
    source_payloads: dict[str, Any],
) -> None:
    templates = payload.get("templates")
    if not isinstance(templates, list):
        errors.append("templates must be a list")
        return
    expected_templates = _expected_template_rows(source_payloads, errors)
    template_ids: list[str] = []
    assignment_counts: dict[str, int] = {}
    family_counts: dict[str, int] = {}
    path_length_counts: dict[str, Any] = {}
    all_assignment_ids: list[str] = []
    for index, template in enumerate(templates):
        if not isinstance(template, dict):
            errors.append(f"template {index} must be an object")
            continue
        template_id = str(template.get("template_id"))
        template_ids.append(template_id)
        expected_template = expected_templates.get(template_id)
        if expected_template is None:
            errors.append(f"unexpected template id {template_id}")
        else:
            _validate_source_bound_template(template, expected_template, errors)
        family_records = template.get("family_records")
        if not isinstance(family_records, list):
            errors.append(f"template {template_id} family_records must be a list")
            continue
        if sorted(template.get("families", [])) != sorted(
            record.get("family_id") for record in family_records
        ):
            errors.append(f"template {template_id} family list mismatch")
        assignment_ids = template.get("assignment_ids")
        if not isinstance(assignment_ids, list) or not all(
            isinstance(item, str) for item in assignment_ids
        ):
            errors.append(f"template {template_id} assignment_ids must be a string list")
            assignment_ids = []
        if len(assignment_ids) != template.get("assignment_count"):
            errors.append(f"template {template_id} assignment_ids count mismatch")
        if len(assignment_ids) != len(set(assignment_ids)):
            errors.append(f"template {template_id} duplicate assignment ids")
        all_assignment_ids.extend(assignment_ids)
        family_assignment_sum = 0
        for family_record in family_records:
            if not isinstance(family_record, dict):
                errors.append(f"template {template_id} family record must be an object")
                continue
            try:
                _validate_family_record(family_record)
            except (AssertionError, KeyError, TypeError, ValueError) as exc:
                errors.append(f"template {template_id} family invalid: {exc}")
            else:
                family_assignment_sum += int(family_record["assignment_count"])
        if family_assignment_sum != template.get("assignment_count"):
            errors.append(f"template {template_id} assignment count mismatch")
        assignment_counts[template_id] = int(template.get("assignment_count", 0))
        family_counts[template_id] = int(template.get("family_count", 0))
        path_length_counts[template_id] = template.get("path_length_counts")
    if len(template_ids) != len(set(template_ids)):
        errors.append("duplicate template ids")
    if len(all_assignment_ids) != len(set(all_assignment_ids)):
        errors.append("duplicate assignment ids across templates")
    if len(all_assignment_ids) != payload.get("self_edge_assignment_count"):
        errors.append("assignment_ids do not cover self-edge assignment count")
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
        "template_path_length_counts",
        payload.get("template_path_length_counts"),
        path_length_counts,
    )


def validate_payload(
    payload: Any,
    *,
    source_payloads: dict[str, Any] | None = None,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a self-edge template packet."""

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
        "self_edge_assignment_count": 158,
        "strict_cycle_assignment_count": 26,
        "self_edge_family_count": 13,
        "self_edge_template_count": 9,
        "path_length_counts": {"3": 86, "4": 36, "5": 18, "6": 18},
        "shared_endpoint_counts": {"1": 158},
        "assignment_core_size_counts": {"3": 46, "4": 40, "5": 36, "6": 36},
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
            self_edge_template_packet_source_artifacts(
                source_payloads["local_cores"],
                source_payloads["path_join"],
                source_payloads["templates"],
            ),
        )
        _validate_template_rows(payload, errors, source_payloads=source_payloads)

    try:
        assert_expected_self_edge_template_packet_counts(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected self-edge template packet counts failed: {exc}")

    if recompute and not errors:
        try:
            expected_payload = self_edge_template_packet_payload(
                source_payloads["local_cores"],
                source_payloads["path_join"],
                source_payloads["templates"],
            )
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"recomputed self-edge template packet failed: {exc}")
        else:
            expect_equal(errors, "self-edge template packet", payload, expected_payload)
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
        "self_edge_assignment_count": object_payload.get("self_edge_assignment_count"),
        "self_edge_family_count": object_payload.get("self_edge_family_count"),
        "self_edge_template_count": object_payload.get("self_edge_template_count"),
        "template_assignment_counts": object_payload.get("template_assignment_counts"),
        "template_family_counts": object_payload.get("template_family_counts"),
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
    parser.add_argument("--local-cores", type=Path, default=DEFAULT_LOCAL_CORES)
    parser.add_argument("--path-join", type=Path, default=DEFAULT_PATH_JOIN)
    parser.add_argument("--templates", type=Path, default=DEFAULT_TEMPLATES)
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
            local_cores_path=args.local_cores,
            path_join_path=args.path_join,
            templates_path=args.templates,
        )
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAILED: could not load source artifacts: {exc}", file=sys.stderr)
        return 1

    if args.write:
        payload = self_edge_template_packet_payload(
            sources["local_cores"],
            sources["path_join"],
            sources["templates"],
        )
        if args.assert_expected:
            assert_expected_self_edge_template_packet_counts(payload)
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
        print("n=9 vertex-circle self-edge template packet")
        print(f"artifact: {summary['artifact']}")
        print(f"self-edge assignments: {summary['self_edge_assignment_count']}")
        print(f"self-edge families: {summary['self_edge_family_count']}")
        print(f"self-edge templates: {summary['self_edge_template_count']}")
        if args.check or args.assert_expected:
            print("OK: self-edge template packet checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
