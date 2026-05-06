#!/usr/bin/env python3
"""Generate or check the n=9 self-edge equality-path join diagnostic."""

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

from check_n9_vertex_circle_frontier_motif_classification import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_CLASSIFICATION,
    validate_payload as validate_classification_payload,
)
from erdos97.n9_vertex_circle_obstruction_shapes import (  # noqa: E402
    assert_expected_local_core_counts,
)
from erdos97.n9_vertex_circle_self_edge_path_join import (  # noqa: E402
    CLAIM_SCOPE,
    PROVENANCE,
    SCHEMA,
    STATUS,
    TRUST,
    assert_expected_self_edge_path_join_counts,
    self_edge_path_join_payload,
    self_edge_path_join_record,
    self_edge_path_join_source_artifacts,
    validate_equality_path,
    validate_label_map,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_self_edge_path_join.json"
)
DEFAULT_LOCAL_CORES = ROOT / "data" / "certificates" / "n9_vertex_circle_local_cores.json"
EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "core_size_assignment_counts",
    "cyclic_order",
    "families",
    "family_assignment_counts",
    "interpretation",
    "n",
    "path_length_counts",
    "provenance",
    "records",
    "row_size",
    "schema",
    "self_edge_assignment_count",
    "self_edge_family_count",
    "self_edge_template_count",
    "shared_endpoint_counts",
    "source_artifacts",
    "source_assignment_count",
    "status",
    "strict_cycle_assignment_count",
    "template_assignment_counts",
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
    classification_path: Path = DEFAULT_CLASSIFICATION,
) -> dict[str, Any]:
    """Load the source artifacts used by the self-edge path join."""

    return {
        "local_cores": load_artifact(_resolve(local_cores_path)),
        "classification": load_artifact(_resolve(classification_path)),
    }


def _validate_sources(source_payloads: dict[str, Any], errors: list[str]) -> None:
    local_cores = source_payloads.get("local_cores")
    classification = source_payloads.get("classification")
    if not isinstance(local_cores, dict):
        errors.append("source local-core payload must be an object")
    else:
        try:
            assert_expected_local_core_counts(local_cores)
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"source local-core artifact invalid: {exc}")
    if not isinstance(classification, dict):
        errors.append("source classification payload must be an object")
    else:
        classification_errors = validate_classification_payload(
            classification,
            recompute=False,
        )
        if classification_errors:
            errors.extend(
                f"source frontier classification invalid: {error}"
                for error in classification_errors
            )


def _self_edge_certificates(local_core_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    certificates = local_core_payload.get("certificates")
    if not isinstance(certificates, list):
        raise ValueError("local-core payload must contain certificates")
    return {
        str(certificate["family_id"]): certificate
        for certificate in certificates
        if isinstance(certificate, dict) and certificate.get("status") == "self_edge"
    }


def _self_edge_assignments(
    classification_payload: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    assignments = classification_payload.get("assignments")
    if not isinstance(assignments, list):
        raise ValueError("classification payload must contain assignments")
    return {
        str(assignment["assignment_id"]): assignment
        for assignment in assignments
        if isinstance(assignment, dict) and assignment.get("status") == "self_edge"
    }


def _validate_family_rows(
    payload: dict[str, Any],
    records: Sequence[dict[str, Any]],
    source_payloads: dict[str, Any],
    errors: list[str],
) -> None:
    raw_families = payload.get("families")
    if not isinstance(raw_families, list):
        errors.append("families must be a list")
        return
    certificates = _self_edge_certificates(source_payloads["local_cores"])
    record_counts = Counter(str(record.get("family_id")) for record in records)
    seen: set[str] = set()
    for index, raw_family in enumerate(raw_families):
        if not isinstance(raw_family, dict):
            errors.append(f"family {index} must be an object")
            continue
        family_id = str(raw_family.get("family_id"))
        if family_id in seen:
            errors.append(f"duplicate family id {family_id}")
        seen.add(family_id)
        certificate = certificates.get(family_id)
        if certificate is None:
            errors.append(f"family {family_id} missing from source local cores")
            continue
        expected = {
            "assignment_count": int(record_counts[family_id]),
            "core_size": int(certificate["core_size"]),
            "family_id": family_id,
            "orbit_size": int(certificate["orbit_size"]),
            "path_length": len(certificate["distance_equality"]["path"]),
            "status": "self_edge",
        }
        for key, value in expected.items():
            if raw_family.get(key) != value:
                errors.append(
                    f"family {family_id} {key} mismatch: "
                    f"expected {value!r}, got {raw_family.get(key)!r}"
                )
        if raw_family.get("template_id") not in {
            str(record.get("template_id"))
            for record in records
            if str(record.get("family_id")) == family_id
        }:
            errors.append(f"family {family_id} template_id does not match records")
    if len(seen) != payload.get("self_edge_family_count"):
        errors.append("self_edge_family_count does not match family rows")


def _validate_record_rows(
    payload: dict[str, Any],
    source_payloads: dict[str, Any],
    errors: list[str],
) -> None:
    records = payload.get("records")
    if not isinstance(records, list):
        errors.append("records must be a list")
        return
    try:
        certificates = _self_edge_certificates(source_payloads["local_cores"])
        assignments = _self_edge_assignments(source_payloads["classification"])
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"could not prepare source maps: {exc}")
        return

    record_ids: list[str] = []
    family_counts: Counter[str] = Counter()
    template_counts: Counter[str] = Counter()
    path_lengths: Counter[int] = Counter()
    core_sizes: Counter[int] = Counter()
    shared_endpoints: Counter[int] = Counter()
    typed_records: list[dict[str, Any]] = []
    for index, raw_record in enumerate(records):
        if not isinstance(raw_record, dict):
            errors.append(f"record {index} must be an object")
            continue
        typed_records.append(raw_record)
        assignment_id = raw_record.get("assignment_id")
        if isinstance(assignment_id, str):
            record_ids.append(assignment_id)
        assignment = assignments.get(str(assignment_id))
        if assignment is None:
            errors.append(f"record {assignment_id or index} missing source assignment")
            continue
        family_id = str(assignment["family_id"])
        certificate = certificates.get(family_id)
        if certificate is None:
            errors.append(f"record {assignment_id} missing source family {family_id}")
            continue
        try:
            validate_label_map(raw_record["to_canonical_label_map"])
            validate_equality_path(
                raw_record["core_selected_rows"],
                raw_record["distance_equality"],
            )
            expected_record = self_edge_path_join_record(assignment, certificate)
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"record {assignment_id or index} invalid: {exc}")
            continue
        expect_equal(errors, f"record {assignment_id}", raw_record, expected_record)
        family_counts[str(raw_record["family_id"])] += 1
        template_counts[str(raw_record["template_id"])] += 1
        path_lengths[int(raw_record["path_length"])] += 1
        core_sizes[int(raw_record["core_size"])] += 1
        shared_endpoints[int(raw_record["shared_endpoint_count"])] += 1

    if len(record_ids) != len(set(record_ids)):
        errors.append("duplicate record assignment ids")
    expect_equal(
        errors,
        "family_assignment_counts",
        payload.get("family_assignment_counts"),
        {family_id: int(family_counts[family_id]) for family_id in sorted(family_counts)},
    )
    expect_equal(
        errors,
        "template_assignment_counts",
        payload.get("template_assignment_counts"),
        {
            template_id: int(template_counts[template_id])
            for template_id in sorted(template_counts)
        },
    )
    expect_equal(
        errors,
        "path_length_counts",
        payload.get("path_length_counts"),
        {str(length): int(path_lengths[length]) for length in sorted(path_lengths)},
    )
    expect_equal(
        errors,
        "core_size_assignment_counts",
        payload.get("core_size_assignment_counts"),
        {str(size): int(core_sizes[size]) for size in sorted(core_sizes)},
    )
    expect_equal(
        errors,
        "shared_endpoint_counts",
        payload.get("shared_endpoint_counts"),
        {
            str(count): int(shared_endpoints[count])
            for count in sorted(shared_endpoints)
        },
    )
    _validate_family_rows(payload, typed_records, source_payloads, errors)


def validate_payload(
    payload: Any,
    *,
    source_payloads: dict[str, Any] | None = None,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a self-edge path-join artifact."""

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
            self_edge_path_join_source_artifacts(
                source_payloads["local_cores"],
                source_payloads["classification"],
            ),
        )
        _validate_record_rows(payload, source_payloads, errors)

    try:
        assert_expected_self_edge_path_join_counts(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected self-edge path-join counts failed: {exc}")

    if recompute and not errors:
        try:
            expected_payload = self_edge_path_join_payload(
                source_payloads["local_cores"],
                source_payloads["classification"],
            )
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"recomputed self-edge path join failed: {exc}")
        else:
            expect_equal(errors, "self-edge path join", payload, expected_payload)
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
        "source_assignment_count": object_payload.get("source_assignment_count"),
        "self_edge_assignment_count": object_payload.get("self_edge_assignment_count"),
        "strict_cycle_assignment_count": object_payload.get(
            "strict_cycle_assignment_count"
        ),
        "self_edge_family_count": object_payload.get("self_edge_family_count"),
        "self_edge_template_count": object_payload.get("self_edge_template_count"),
        "path_length_counts": object_payload.get("path_length_counts"),
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
    parser.add_argument("--classification", type=Path, default=DEFAULT_CLASSIFICATION)
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
            classification_path=args.classification,
        )
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAILED: could not load source artifacts: {exc}", file=sys.stderr)
        return 1

    if args.write:
        payload = self_edge_path_join_payload(
            sources["local_cores"],
            sources["classification"],
        )
        if args.assert_expected:
            assert_expected_self_edge_path_join_counts(payload)
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
        print("n=9 vertex-circle self-edge equality-path join")
        print(f"artifact: {summary['artifact']}")
        print(f"self-edge assignments: {summary['self_edge_assignment_count']}")
        print(f"self-edge families: {summary['self_edge_family_count']}")
        print(f"self-edge templates: {summary['self_edge_template_count']}")
        print(f"path lengths: {summary['path_length_counts']}")
        if args.check or args.assert_expected:
            print("OK: self-edge path-join checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
