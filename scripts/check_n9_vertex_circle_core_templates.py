#!/usr/bin/env python3
"""Generate or check n=9 vertex-circle local-core template diagnostics."""

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

from check_n9_vertex_circle_local_core_packet import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_PACKET,
    load_artifact,
    validate_payload as validate_packet_payload,
)
from erdos97.path_display import display_path  # noqa: E402
from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    LocalCoreReplay,
    StrictInequality,
    replay_local_core_bundle,
)

DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "n9_vertex_circle_core_templates.json"
SCHEMA = "erdos97.n9_vertex_circle_core_templates.v1"
STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Template diagnostic for the 16 n=9 vertex-circle local-core motif "
    "representatives; not a proof of n=9, not a counterexample, not an "
    "independent review of the exhaustive checker, and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_core_templates.py",
    "command": (
        "python scripts/check_n9_vertex_circle_core_templates.py "
        "--assert-expected --write"
    ),
}
EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "core_size_counts",
    "cyclic_order",
    "families",
    "family_count",
    "interpretation",
    "max_core_size",
    "n",
    "orbit_size_sum",
    "provenance",
    "row_size",
    "schema",
    "source_artifacts",
    "source_packet",
    "status",
    "status_core_size_counts",
    "status_template_counts",
    "template_family_count_distribution",
    "template_count",
    "templates",
    "trust",
}
EXPECTED_STATUS_TEMPLATE_COUNTS = {"self_edge": 9, "strict_cycle": 3}
EXPECTED_TEMPLATE_FAMILY_COUNT_DISTRIBUTION = {"1": 10, "2": 1, "4": 1}


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


def _edge_span(edge: StrictInequality) -> tuple[int, int]:
    return (
        int(edge.outer_interval[1] - edge.outer_interval[0]),
        int(edge.inner_interval[1] - edge.inner_interval[0]),
    )


def _shared_endpoint_count(edge: StrictInequality) -> int:
    return len(set(edge.outer_pair) & set(edge.inner_pair))


def _shape_rows(counter: Counter[tuple[int, int, int]]) -> list[dict[str, int]]:
    return [
        {
            "outer_span": outer_span,
            "inner_span": inner_span,
            "shared_endpoint_count": shared,
            "count": counter[(outer_span, inner_span, shared)],
        }
        for outer_span, inner_span, shared in sorted(counter)
    ]


def _cycle_span_rows(counter: Counter[tuple[int, int]]) -> list[dict[str, int]]:
    return [
        {
            "outer_span": outer_span,
            "inner_span": inner_span,
            "count": counter[(outer_span, inner_span)],
        }
        for outer_span, inner_span in sorted(counter)
    ]


def _self_edge_template(
    result: LocalCoreReplay,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    shape_counter = Counter(
        (
            *_edge_span(edge),
            _shared_endpoint_count(edge),
        )
        for edge in result.result.self_edge_conflicts
    )
    tokens = [
        f"{row['outer_span']}:{row['inner_span']}:{row['shared_endpoint_count']}x{row['count']}"
        for row in _shape_rows(shape_counter)
    ]
    template_key = (
        f"self_edge|rows={result.result.selected_row_count}|"
        f"strict_edges={result.result.strict_edge_count}|conflicts={','.join(tokens)}"
    )
    family_obstruction = {
        "self_edge_conflict_count": len(result.result.self_edge_conflicts),
        "self_edge_shape_counts": _shape_rows(shape_counter),
    }
    template_fields = {
        "self_edge_shape_counts": _shape_rows(shape_counter),
    }
    return template_key, family_obstruction, template_fields


def _strict_cycle_template(
    result: LocalCoreReplay,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    span_counter = Counter(_edge_span(edge) for edge in result.result.cycle_edges)
    tokens = [
        f"{row['outer_span']}:{row['inner_span']}x{row['count']}"
        for row in _cycle_span_rows(span_counter)
    ]
    cycle_length = len(result.result.cycle_edges)
    template_key = (
        f"strict_cycle|rows={result.result.selected_row_count}|"
        f"strict_edges={result.result.strict_edge_count}|"
        f"cycle={cycle_length}|spans={','.join(tokens)}"
    )
    family_obstruction = {
        "cycle_length": cycle_length,
        "cycle_span_counts": _cycle_span_rows(span_counter),
    }
    template_fields = {
        "cycle_length": cycle_length,
        "cycle_span_counts": _cycle_span_rows(span_counter),
    }
    return template_key, family_obstruction, template_fields


def _template_for_replay(
    replay: LocalCoreReplay,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    if replay.result.status == "self_edge":
        return _self_edge_template(replay)
    if replay.result.status == "strict_cycle":
        return _strict_cycle_template(replay)
    raise AssertionError(f"unexpected local-core replay status {replay.result.status!r}")


def _family_orbit_sizes(families: Sequence[dict[str, Any]]) -> dict[str, int]:
    return {str(family["family_id"]): int(family["orbit_size"]) for family in families}


def core_template_payload(packet: dict[str, Any]) -> dict[str, Any]:
    """Return the replay-derived template diagnostic for a compact packet."""

    replays = replay_local_core_bundle(packet)
    raw_families = packet.get("certificates")
    if not isinstance(raw_families, list):
        raise ValueError("source packet must contain certificate list")
    if len(raw_families) != len(replays):
        raise ValueError("source packet certificate count does not match replay count")
    orbit_sizes = _family_orbit_sizes(raw_families)

    template_acc: dict[str, dict[str, Any]] = {}
    family_rows = []
    for replay in replays:
        template_key, family_obstruction, template_fields = _template_for_replay(replay)
        family_id = replay.family_id
        orbit_size = orbit_sizes[family_id]
        family_rows.append(
            {
                "family_id": family_id,
                "orbit_size": orbit_size,
                "status": replay.result.status,
                "core_size": replay.result.selected_row_count,
                "strict_edge_count": replay.result.strict_edge_count,
                "template_key": template_key,
                "obstruction_summary": family_obstruction,
            }
        )
        template = template_acc.setdefault(
            template_key,
            {
                "template_key": template_key,
                "status": replay.result.status,
                "core_size": replay.result.selected_row_count,
                "strict_edge_count": replay.result.strict_edge_count,
                "families": [],
                "family_count": 0,
                "orbit_size_sum": 0,
                **template_fields,
            },
        )
        template["families"].append(family_id)
        template["family_count"] = int(template["family_count"]) + 1
        template["orbit_size_sum"] = int(template["orbit_size_sum"]) + orbit_size

    templates = []
    template_id_by_key = {}
    for idx, key in enumerate(sorted(template_acc), start=1):
        template_id = f"T{idx:02d}"
        template = dict(template_acc[key])
        template["template_id"] = template_id
        template["families"] = sorted(template["families"])
        templates.append(template)
        template_id_by_key[key] = template_id

    families = []
    for family in sorted(family_rows, key=lambda row: row["family_id"]):
        row = dict(family)
        row["template_id"] = template_id_by_key[row.pop("template_key")]
        families.append(row)

    status_template_counts = Counter(str(template["status"]) for template in templates)
    family_count_distribution = Counter(int(template["family_count"]) for template in templates)

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": packet["n"],
        "row_size": packet["row_size"],
        "cyclic_order": packet["cyclic_order"],
        "family_count": len(families),
        "orbit_size_sum": sum(int(family["orbit_size"]) for family in families),
        "template_count": len(templates),
        "status_template_counts": {
            status: status_template_counts[status] for status in sorted(status_template_counts)
        },
        "template_family_count_distribution": {
            str(count): family_count_distribution[count] for count in sorted(family_count_distribution)
        },
        "core_size_counts": packet["core_size_counts"],
        "status_core_size_counts": packet["status_core_size_counts"],
        "max_core_size": packet["max_core_size"],
        "templates": templates,
        "families": families,
        "interpretation": [
            "Templates are replay-derived shape buckets for the compact local cores.",
            "Template ids are deterministic artifact labels, not intrinsic theorem names.",
            "Each template covers only the listed n=9 motif-family representatives under the recorded cyclic order.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_packet": {
            "path": "data/certificates/n9_vertex_circle_local_core_packet.json",
            "schema": packet["schema"],
            "status": packet["status"],
            "trust": packet["trust"],
        },
        "source_artifacts": packet["source_artifacts"],
        "provenance": PROVENANCE,
    }
    assert_expected_core_template_counts(payload)
    return payload


def assert_expected_core_template_counts(payload: dict[str, Any]) -> None:
    """Assert stable headline counts for the local-core template diagnostic."""

    if payload["schema"] != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload['schema']}")
    if payload["status"] != STATUS:
        raise AssertionError(f"unexpected status: {payload['status']}")
    if payload["trust"] != TRUST:
        raise AssertionError(f"unexpected trust: {payload['trust']}")
    if payload["claim_scope"] != CLAIM_SCOPE:
        raise AssertionError("claim scope changed")
    if payload["family_count"] != 16:
        raise AssertionError(f"unexpected family count: {payload['family_count']}")
    if payload["orbit_size_sum"] != 184:
        raise AssertionError(f"unexpected orbit-size sum: {payload['orbit_size_sum']}")
    if payload["template_count"] != 12:
        raise AssertionError(f"unexpected template count: {payload['template_count']}")
    if payload["status_template_counts"] != EXPECTED_STATUS_TEMPLATE_COUNTS:
        raise AssertionError("unexpected status/template counts")
    if payload["template_family_count_distribution"] != EXPECTED_TEMPLATE_FAMILY_COUNT_DISTRIBUTION:
        raise AssertionError("unexpected template family-count distribution")
    if payload["core_size_counts"] != {"3": 5, "4": 6, "5": 2, "6": 3}:
        raise AssertionError("unexpected core-size counts")
    if payload["status_core_size_counts"] != {
        "self_edge": {"3": 5, "4": 4, "5": 2, "6": 2},
        "strict_cycle": {"4": 2, "6": 1},
    }:
        raise AssertionError("unexpected status/core-size counts")
    templates = payload["templates"]
    families = payload["families"]
    if not isinstance(templates, list) or len(templates) != 12:
        raise AssertionError("unexpected template rows")
    if not isinstance(families, list) or len(families) != 16:
        raise AssertionError("unexpected family rows")
    if [family["family_id"] for family in families] != [f"F{idx:02d}" for idx in range(1, 17)]:
        raise AssertionError("unexpected family id sequence")
    family_template_ids = {str(family["template_id"]) for family in families}
    template_ids = {str(template["template_id"]) for template in templates}
    if family_template_ids - template_ids:
        raise AssertionError("family row references unknown template id")
    multi_family_templates = sorted(
        int(template["family_count"]) for template in templates if int(template["family_count"]) > 1
    )
    if multi_family_templates != [2, 4]:
        raise AssertionError("unexpected multi-family template sizes")


def _int_from_row(
    errors: list[str],
    row: dict[str, Any],
    key: str,
    label: str,
) -> int | None:
    try:
        return int(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"{label} has invalid {key}: {exc}")
        return None


def _validate_template_family_links(payload: dict[str, Any], errors: list[str]) -> None:
    raw_templates = payload.get("templates")
    raw_families = payload.get("families")
    if not isinstance(raw_templates, list):
        errors.append("templates must be a list")
        return
    if not isinstance(raw_families, list):
        errors.append("families must be a list")
        return

    templates_by_id: dict[str, dict[str, Any]] = {}
    for index, raw_template in enumerate(raw_templates):
        if not isinstance(raw_template, dict):
            errors.append(f"template {index} must be an object")
            continue
        template_id = raw_template.get("template_id")
        if not isinstance(template_id, str) or not template_id:
            errors.append(f"template {index} has invalid template_id")
            continue
        if template_id in templates_by_id:
            errors.append(f"duplicate template id {template_id}")
        templates_by_id[template_id] = raw_template

    families_by_template: dict[str, list[str]] = {template_id: [] for template_id in templates_by_id}
    orbit_by_template: Counter[str] = Counter()
    family_ids: list[str] = []
    total_orbit_size = 0
    for index, raw_family in enumerate(raw_families):
        if not isinstance(raw_family, dict):
            errors.append(f"family {index} must be an object")
            continue
        family_id = raw_family.get("family_id")
        template_id = raw_family.get("template_id")
        if not isinstance(family_id, str) or not family_id:
            errors.append(f"family {index} has invalid family_id")
            continue
        if not isinstance(template_id, str) or template_id not in templates_by_id:
            errors.append(f"family {family_id} references unknown template {template_id!r}")
            continue
        template = templates_by_id[template_id]
        for key in ("status", "core_size", "strict_edge_count"):
            if raw_family.get(key) != template.get(key):
                errors.append(
                    f"family {family_id} {key} does not match template {template_id}: "
                    f"{raw_family.get(key)!r} != {template.get(key)!r}"
                )
        orbit_size = _int_from_row(errors, raw_family, "orbit_size", f"family {family_id}")
        if orbit_size is None:
            continue
        families_by_template[template_id].append(family_id)
        orbit_by_template[template_id] += orbit_size
        family_ids.append(family_id)
        total_orbit_size += orbit_size

    if len(family_ids) != len(set(family_ids)):
        errors.append("duplicate family ids in family rows")
    if len(raw_families) != payload.get("family_count"):
        errors.append("family_count does not match family row count")
    if total_orbit_size != payload.get("orbit_size_sum"):
        errors.append("orbit_size_sum does not match family rows")

    status_template_counts: Counter[str] = Counter()
    family_count_distribution: Counter[int] = Counter()
    for template_id, template in templates_by_id.items():
        status = template.get("status")
        if isinstance(status, str):
            status_template_counts[status] += 1
        listed_families = template.get("families")
        if not isinstance(listed_families, list) or not all(
            isinstance(item, str) for item in listed_families
        ):
            errors.append(f"template {template_id} families must be a list of strings")
            continue
        expected_families = sorted(families_by_template[template_id])
        if sorted(listed_families) != expected_families:
            errors.append(
                f"template {template_id} family list mismatch: "
                f"expected {expected_families!r}, got {sorted(listed_families)!r}"
            )
        family_count = _int_from_row(errors, template, "family_count", f"template {template_id}")
        orbit_sum = _int_from_row(errors, template, "orbit_size_sum", f"template {template_id}")
        if family_count is not None:
            family_count_distribution[family_count] += 1
            if family_count != len(expected_families):
                errors.append(f"template {template_id} family_count does not match family rows")
        if orbit_sum is not None and orbit_sum != orbit_by_template[template_id]:
            errors.append(f"template {template_id} orbit_size_sum does not match family rows")

    expected_status_counts = {
        status: status_template_counts[status] for status in sorted(status_template_counts)
    }
    if payload.get("status_template_counts") != expected_status_counts:
        errors.append("status_template_counts does not match template rows")
    expected_family_distribution = {
        str(count): family_count_distribution[count] for count in sorted(family_count_distribution)
    }
    if payload.get("template_family_count_distribution") != expected_family_distribution:
        errors.append("template_family_count_distribution does not match template rows")


def _validate_packet(packet: Any) -> list[str]:
    if not isinstance(packet, dict):
        return ["source packet top level must be a JSON object"]
    return validate_packet_payload(packet, recompute=False)


def validate_payload(
    payload: Any,
    *,
    packet: Any | None = None,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a local-core template diagnostic."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

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
        "family_count": 16,
        "orbit_size_sum": 184,
        "template_count": 12,
        "status_template_counts": EXPECTED_STATUS_TEMPLATE_COUNTS,
        "template_family_count_distribution": EXPECTED_TEMPLATE_FAMILY_COUNT_DISTRIBUTION,
        "max_core_size": 6,
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

    try:
        assert_expected_core_template_counts(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected template counts failed: {exc}")
    _validate_template_family_links(payload, errors)

    if recompute:
        if packet is None:
            try:
                packet = load_artifact(DEFAULT_PACKET)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"failed to load source packet: {exc}")
                packet = None
        packet_errors = _validate_packet(packet)
        if packet_errors:
            errors.extend(f"source packet invalid: {error}" for error in packet_errors)
        elif isinstance(packet, dict):
            try:
                expected_payload = core_template_payload(packet)
            except (AssertionError, TypeError, ValueError) as exc:
                errors.append(f"recomputed template diagnostic failed: {exc}")
            else:
                expect_equal(errors, "core-template diagnostic", payload, expected_payload)
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
        "family_count": object_payload.get("family_count"),
        "template_count": object_payload.get("template_count"),
        "status_template_counts": object_payload.get("status_template_counts"),
        "template_family_count_distribution": object_payload.get(
            "template_family_count_distribution"
        ),
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write generated diagnostic")
    parser.add_argument("--check", action="store_true", help="validate an existing diagnostic")
    parser.add_argument("--json", action="store_true", help="print stable JSON summary")
    parser.add_argument("--assert-expected", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact
    packet_path = args.packet if args.packet.is_absolute() else ROOT / args.packet
    out = args.out if args.out.is_absolute() else ROOT / args.out

    try:
        packet = load_artifact(packet_path)
    except (OSError, json.JSONDecodeError) as exc:
        packet = {}
        packet_errors = [str(exc)]
    else:
        packet_errors = _validate_packet(packet)

    if args.write:
        if packet_errors:
            for error in packet_errors:
                print(f"source packet invalid: {error}", file=sys.stderr)
            return 1
        payload = core_template_payload(packet)
        if args.assert_expected:
            assert_expected_core_template_counts(payload)
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
            packet=packet,
            recompute=args.check or args.assert_expected,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]
    if packet_errors:
        errors.extend(f"source packet invalid: {error}" for error in packet_errors)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact, ROOT)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 vertex-circle local-core template diagnostic")
        print(f"artifact: {summary['artifact']}")
        print(f"families: {summary['family_count']}")
        print(f"templates: {summary['template_count']}")
        print(f"status/template counts: {summary['status_template_counts']}")
        if args.check or args.assert_expected:
            print("OK: local-core template diagnostic checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
