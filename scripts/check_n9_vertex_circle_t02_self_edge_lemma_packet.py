#!/usr/bin/env python3
"""Generate or check the focused T02 n=9 self-edge local lemma packet."""

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

from check_n9_vertex_circle_self_edge_template_packet import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SELF_EDGE_PACKET,
    validate_payload as validate_self_edge_packet,
)
from check_n9_vertex_circle_template_lemma_catalog import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_TEMPLATE_CATALOG,
    validate_payload as validate_template_catalog,
)
from erdos97.n9_vertex_circle_t02_self_edge_lemma_packet import (  # noqa: E402
    CLAIM_SCOPE,
    EXPECTED_ASSIGNMENT_IDS,
    EXPECTED_CORE_SELECTED_ROWS,
    EXPECTED_DISTANCE_EQUALITIES,
    EXPECTED_EQUALITY_CHAINS,
    EXPECTED_FAMILY_ASSIGNMENT_COUNTS,
    EXPECTED_FAMILY_IDS,
    EXPECTED_FAMILY_ORBIT_SIZES,
    EXPECTED_PATH_LENGTH_COUNTS,
    EXPECTED_SELECTED_PATH_SHAPE_COUNTS,
    EXPECTED_SHARED_ENDPOINT_COUNTS,
    EXPECTED_STRICT_INEQUALITIES,
    EXPECTED_TEMPLATE_KEY,
    PROVENANCE,
    SCHEMA,
    STATUS,
    TRUST,
    assert_expected_t02_self_edge_lemma_packet,
    source_artifacts,
    t02_self_edge_lemma_packet_payload,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_t02_self_edge_lemma_packet.json"
)
EXPECTED_TOP_LEVEL_KEYS = {
    "assignment_count",
    "assignment_ids",
    "claim_scope",
    "core_size",
    "cyclic_order",
    "family_assignment_counts",
    "family_count",
    "family_ids",
    "family_orbit_sizes",
    "family_packets",
    "interpretation",
    "n",
    "orbit_size_sum",
    "path_length_counts",
    "provenance",
    "row_size",
    "schema",
    "selected_path_shape_counts",
    "shared_endpoint_counts",
    "source_artifacts",
    "source_catalog_record",
    "source_template_record",
    "status",
    "strict_edge_count",
    "template_id",
    "template_key",
    "trust",
}
EXPECTED_FAMILY_PACKET_KEYS = {
    "assignment_count",
    "core_selected_rows",
    "core_size",
    "distance_equality",
    "equality_chain",
    "family_id",
    "local_lemma",
    "orbit_size",
    "replay",
    "source_family_record",
    "strict_inequality",
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
    template_catalog_path: Path = DEFAULT_TEMPLATE_CATALOG,
) -> dict[str, Any]:
    """Load the source artifacts used by the focused T02 packet."""

    return {
        "self_edge_packet": load_artifact(_resolve(self_edge_packet_path)),
        "template_catalog": load_artifact(_resolve(template_catalog_path)),
    }


def _validate_sources(source_payloads: dict[str, Any], errors: list[str]) -> None:
    self_edge = source_payloads.get("self_edge_packet")
    catalog = source_payloads.get("template_catalog")
    if not isinstance(self_edge, dict):
        errors.append("source self-edge template packet must be an object")
    else:
        errors.extend(
            f"source self-edge template packet invalid: {error}"
            for error in validate_self_edge_packet(self_edge, recompute=False)
        )
    if not isinstance(catalog, dict):
        errors.append("source template lemma catalog must be an object")
    else:
        errors.extend(
            f"source template lemma catalog invalid: {error}"
            for error in validate_template_catalog(catalog, recompute=False)
        )


def _expected_payload(
    source_payloads: dict[str, Any],
    errors: list[str],
) -> dict[str, Any] | None:
    try:
        return t02_self_edge_lemma_packet_payload(
            source_payloads["self_edge_packet"],
            source_payloads["template_catalog"],
        )
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"source-bound T02 self-edge lemma packet failed: {exc}")
        return None


def _family_packets_by_id(payload: dict[str, Any], errors: list[str]) -> dict[str, dict[str, Any]]:
    packets = payload.get("family_packets")
    if not isinstance(packets, list):
        errors.append("family_packets must be a list")
        return {}
    by_id: dict[str, dict[str, Any]] = {}
    for packet in packets:
        if not isinstance(packet, dict):
            errors.append("family_packets entries must be objects")
            continue
        family_id = str(packet.get("family_id"))
        by_id[family_id] = packet
    if set(by_id) != set(EXPECTED_FAMILY_IDS):
        errors.append(
            f"family packet ids mismatch: expected {list(EXPECTED_FAMILY_IDS)!r}, "
            f"got {sorted(by_id)!r}"
        )
    return {family_id: by_id[family_id] for family_id in EXPECTED_FAMILY_IDS if family_id in by_id}


def _validate_local_lemma(family_id: str, packet: dict[str, Any], errors: list[str]) -> None:
    lemma = packet.get("local_lemma")
    if not isinstance(lemma, dict):
        errors.append(f"{family_id} local_lemma must be an object")
        return
    expect_equal(errors, f"{family_id} local_lemma review_status", lemma.get("review_status"), "review_pending")
    selected_equalities = lemma.get("selected_distance_equalities")
    if not isinstance(selected_equalities, list) or len(selected_equalities) != 3:
        errors.append(f"{family_id} local_lemma selected_distance_equalities must have three steps")
    strict = EXPECTED_STRICT_INEQUALITIES[family_id]
    statement = str(lemma.get("strict_inequality_statement", ""))
    for pair_value in (strict["outer_pair"], strict["inner_pair"]):
        if str(pair_value) not in statement:
            errors.append(f"{family_id} strict inequality statement must name {pair_value}")
    contradiction = str(lemma.get("contradiction", ""))
    if "reflexive strict edge" not in contradiction:
        errors.append(f"{family_id} local_lemma contradiction must mention a reflexive strict edge")


def _validate_replay(family_id: str, packet: dict[str, Any], errors: list[str]) -> None:
    replay = packet.get("replay")
    if not isinstance(replay, dict):
        errors.append(f"{family_id} replay must be an object")
        return
    expect_equal(errors, f"{family_id} replay status", replay.get("status"), "self_edge")
    expect_equal(errors, f"{family_id} replay selected_row_count", replay.get("selected_row_count"), 3)
    expect_equal(errors, f"{family_id} replay strict_edge_count", replay.get("strict_edge_count"), 27)
    expect_equal(
        errors,
        f"{family_id} replay self_edge_conflict_count",
        replay.get("self_edge_conflict_count"),
        1,
    )
    expect_equal(errors, f"{family_id} replay cycle_edge_count", replay.get("cycle_edge_count"), 0)
    primary = replay.get("primary_self_edge_conflict")
    if not isinstance(primary, dict):
        errors.append(f"{family_id} replay primary_self_edge_conflict must be an object")
        return
    strict = EXPECTED_STRICT_INEQUALITIES[family_id]
    for key in ("row", "witness_order", "outer_pair", "inner_pair"):
        expect_equal(errors, f"{family_id} primary {key}", primary.get(key), strict[key])


def _validate_family_packet(family_id: str, packet: dict[str, Any], errors: list[str]) -> None:
    if set(packet) != EXPECTED_FAMILY_PACKET_KEYS:
        errors.append(
            f"{family_id} keys mismatch: expected {sorted(EXPECTED_FAMILY_PACKET_KEYS)!r}, "
            f"got {sorted(packet)!r}"
        )
    expect_equal(errors, f"{family_id} family_id", packet.get("family_id"), family_id)
    expect_equal(
        errors,
        f"{family_id} assignment_count",
        packet.get("assignment_count"),
        EXPECTED_FAMILY_ASSIGNMENT_COUNTS[family_id],
    )
    expect_equal(
        errors,
        f"{family_id} orbit_size",
        packet.get("orbit_size"),
        EXPECTED_FAMILY_ORBIT_SIZES[family_id],
    )
    expect_equal(errors, f"{family_id} core_size", packet.get("core_size"), 3)
    expect_equal(
        errors,
        f"{family_id} core_selected_rows",
        packet.get("core_selected_rows"),
        [list(row) for row in EXPECTED_CORE_SELECTED_ROWS[family_id]],
    )
    expect_equal(
        errors,
        f"{family_id} strict_inequality",
        packet.get("strict_inequality"),
        EXPECTED_STRICT_INEQUALITIES[family_id],
    )
    expect_equal(
        errors,
        f"{family_id} distance_equality",
        packet.get("distance_equality"),
        EXPECTED_DISTANCE_EQUALITIES[family_id],
    )
    expect_equal(
        errors,
        f"{family_id} equality_chain",
        packet.get("equality_chain"),
        [list(item) for item in EXPECTED_EQUALITY_CHAINS[family_id]],
    )
    _validate_local_lemma(family_id, packet, errors)
    _validate_replay(family_id, packet, errors)


def validate_payload(
    payload: Any,
    *,
    source_payloads: dict[str, Any] | None = None,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a focused T02 local lemma packet."""

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
        "template_id": "T02",
        "template_key": EXPECTED_TEMPLATE_KEY,
        "assignment_count": 40,
        "assignment_ids": list(EXPECTED_ASSIGNMENT_IDS),
        "family_count": 4,
        "family_ids": list(EXPECTED_FAMILY_IDS),
        "family_assignment_counts": EXPECTED_FAMILY_ASSIGNMENT_COUNTS,
        "family_orbit_sizes": EXPECTED_FAMILY_ORBIT_SIZES,
        "orbit_size_sum": 40,
        "core_size": 3,
        "strict_edge_count": 27,
        "path_length_counts": EXPECTED_PATH_LENGTH_COUNTS,
        "shared_endpoint_counts": EXPECTED_SHARED_ENDPOINT_COUNTS,
        "selected_path_shape_counts": EXPECTED_SELECTED_PATH_SHAPE_COUNTS,
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
        if not any("proof mining" in item for item in interpretation):
            errors.append("interpretation must preserve the proof-mining scope")

    for family_id, packet in _family_packets_by_id(payload, errors).items():
        _validate_family_packet(family_id, packet, errors)

    _validate_sources(source_payloads, errors)
    expected_payload = None if errors else _expected_payload(source_payloads, errors)
    if expected_payload is not None:
        expect_equal(
            errors,
            "source_artifacts",
            payload.get("source_artifacts"),
            source_artifacts(
                source_payloads["self_edge_packet"],
                source_payloads["template_catalog"],
            ),
        )
        expect_equal(
            errors,
            "source_template_record",
            payload.get("source_template_record"),
            expected_payload["source_template_record"],
        )
        expect_equal(
            errors,
            "source_catalog_record",
            payload.get("source_catalog_record"),
            expected_payload["source_catalog_record"],
        )

    try:
        assert_expected_t02_self_edge_lemma_packet(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected T02 self-edge lemma packet counts failed: {exc}")

    if recompute and expected_payload is not None and not errors:
        expect_equal(errors, "T02 self-edge lemma packet", payload, expected_payload)
    return errors


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    family_packets = object_payload.get("family_packets")
    family_packets = family_packets if isinstance(family_packets, list) else []
    replay_statuses = [
        packet.get("replay", {}).get("status")
        for packet in family_packets
        if isinstance(packet, dict) and isinstance(packet.get("replay"), dict)
    ]
    return {
        "ok": not errors,
        "artifact": display_path(path, ROOT),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "template_id": object_payload.get("template_id"),
        "assignment_count": object_payload.get("assignment_count"),
        "family_count": object_payload.get("family_count"),
        "family_ids": object_payload.get("family_ids"),
        "core_size": object_payload.get("core_size"),
        "replay_statuses": replay_statuses,
        "strict_edge_count": object_payload.get("strict_edge_count"),
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
    parser.add_argument("--template-catalog", type=Path, default=DEFAULT_TEMPLATE_CATALOG)
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
            template_catalog_path=args.template_catalog,
        )
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAILED: could not load source artifacts: {exc}", file=sys.stderr)
        return 1

    if args.write:
        payload = t02_self_edge_lemma_packet_payload(
            sources["self_edge_packet"],
            sources["template_catalog"],
        )
        if args.assert_expected:
            assert_expected_t02_self_edge_lemma_packet(payload)
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
        print("n=9 vertex-circle T02 self-edge local lemma packet")
        print(f"artifact: {summary['artifact']}")
        print(f"assignments: {summary['assignment_count']}")
        print(f"families: {summary['family_ids']}")
        print(f"core size: {summary['core_size']}")
        if args.check or args.assert_expected:
            print("OK: T02 self-edge local lemma packet checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
