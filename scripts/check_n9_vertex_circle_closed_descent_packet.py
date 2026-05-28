#!/usr/bin/env python3
"""Generate or check the n=9 vertex-circle closed-descent packet."""

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

from erdos97.n9_vertex_circle_obstruction_shapes import (  # noqa: E402
    assert_expected_local_core_packet_counts,
)
from erdos97.path_display import display_path  # noqa: E402
from erdos97.vertex_circle_closed_descent import (  # noqa: E402
    closed_descent_cycle_to_json,
)
from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    parse_selected_rows,
    replay_vertex_circle_quotient,
    strict_quotient_edges,
    validate_closed_descent_region,
)

SCHEMA = "erdos97.n9_vertex_circle_closed_descent_packet.v1"
STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Closed-descent reformulation of the 16 stored n=9 vertex-circle local-core "
    "motif representatives; not a proof of n=9, not a counterexample, not an "
    "independent review of the exhaustive checker, not local-lemma completeness, "
    "not a bridge proof, and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_closed_descent_packet.py",
    "command": (
        "python scripts/check_n9_vertex_circle_closed_descent_packet.py "
        "--assert-expected --write"
    ),
}
DEFAULT_SOURCE = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_local_core_packet.json"
)
DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_closed_descent_packet.json"
)
EXPECTED_TOP_LEVEL_KEYS = {
    "certificates",
    "claim_scope",
    "closed_descent_cycle_length_counts",
    "family_count",
    "interpretation",
    "max_region_class_count",
    "n",
    "orbit_size_sum",
    "provenance",
    "region_class_count_counts",
    "row_size",
    "schema",
    "source_artifacts",
    "source_status_counts",
    "status",
    "trust",
}
EXPECTED_SOURCE_STATUS_COUNTS = {"self_edge": 13, "strict_cycle": 3}
EXPECTED_REGION_CLASS_COUNT_COUNTS = {"1": 13, "2": 1, "3": 2}
EXPECTED_CLOSED_DESCENT_CYCLE_LENGTH_COUNTS = {"1": 13, "2": 1, "3": 2}


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


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a mismatch error when values differ."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _descent_classes_for_replay(replay: Any) -> list[tuple[int, int]]:
    if replay.status == "self_edge":
        if not replay.self_edge_conflicts:
            raise AssertionError("self-edge replay did not record a conflict")
        return [replay.self_edge_conflicts[0].outer_class]
    if replay.status == "strict_cycle":
        if not replay.cycle_edges:
            raise AssertionError("strict-cycle replay did not record cycle edges")
        return [edge.outer_class for edge in replay.cycle_edges]
    raise AssertionError(f"local-core replay is unobstructed: {replay.status!r}")


def closed_descent_packet_summary(
    source_path: Path = DEFAULT_SOURCE,
) -> dict[str, object]:
    """Return a closed-descent packet derived from the compact local-core packet."""

    source_payload = load_artifact(source_path)
    if not isinstance(source_payload, dict):
        raise AssertionError("source local-core packet must be a JSON object")
    assert_expected_local_core_packet_counts(source_payload)

    n = int(source_payload["n"])
    row_size = int(source_payload["row_size"])
    order = tuple(int(label) for label in source_payload["cyclic_order"])
    certificates = []
    source_status_counts: Counter[str] = Counter()
    region_class_counts: Counter[int] = Counter()
    cycle_length_counts: Counter[int] = Counter()

    for raw_certificate in source_payload["certificates"]:
        if not isinstance(raw_certificate, dict):
            raise AssertionError("source certificate must be a JSON object")
        rows = parse_selected_rows(raw_certificate["compact_selected_rows"])
        replay = replay_vertex_circle_quotient(n, order, rows)
        expected_status = str(raw_certificate["status"])
        if replay.status != expected_status:
            raise AssertionError(
                f"{raw_certificate['family_id']} replay status mismatch: "
                f"{replay.status!r} != {expected_status!r}"
            )
        edges = strict_quotient_edges(n, order, rows)
        region = validate_closed_descent_region(
            edges,
            _descent_classes_for_replay(replay),
        )
        descent_cycle = closed_descent_cycle_to_json(region)
        source_status_counts[replay.status] += 1
        region_class_counts[int(descent_cycle["class_count"])] += 1
        cycle_length_counts[int(descent_cycle["cycle_length"])] += 1
        certificates.append(
            {
                "family_id": str(raw_certificate["family_id"]),
                "source_status": replay.status,
                "orbit_size": int(raw_certificate["orbit_size"]),
                "core_size": int(raw_certificate["core_size"]),
                "strict_edge_count": replay.strict_edge_count,
                "region_class_count": int(descent_cycle["class_count"]),
                "closed_descent_cycle": descent_cycle,
            }
        )

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n,
        "row_size": row_size,
        "family_count": len(certificates),
        "orbit_size_sum": sum(int(cert["orbit_size"]) for cert in certificates),
        "source_status_counts": _json_counter(source_status_counts),
        "region_class_count_counts": _json_counter(region_class_counts),
        "closed_descent_cycle_length_counts": _json_counter(cycle_length_counts),
        "max_region_class_count": max(region_class_counts),
        "certificates": certificates,
        "interpretation": [
            "Each certificate is a closed-descent reformulation of one stored compact local-core packet certificate.",
            "A one-class region corresponds to a replayed self-edge obstruction.",
            "A multi-class region corresponds to a replayed strict-cycle obstruction.",
            "The packet is a reviewer aid for bridge-facing local lemma work.",
            "No proof of the n=9 case is claimed.",
            "No bridge proof is claimed.",
            "No global status update is claimed.",
        ],
        "source_artifacts": [
            {
                "path": "data/certificates/n9_vertex_circle_local_core_packet.json",
                "schema": source_payload["schema"],
                "role": "compact local-core packet source",
            }
        ],
        "provenance": PROVENANCE,
    }
    assert_expected_closed_descent_packet_counts(payload)
    return payload


def assert_expected_closed_descent_packet_counts(payload: dict[str, Any]) -> None:
    """Assert that the packet still matches the known local-core families."""

    if payload["schema"] != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload['schema']}")
    if payload["status"] != STATUS:
        raise AssertionError(f"unexpected status: {payload['status']}")
    if payload["trust"] != TRUST:
        raise AssertionError(f"unexpected trust: {payload['trust']}")
    if payload["source_status_counts"] != EXPECTED_SOURCE_STATUS_COUNTS:
        raise AssertionError(
            f"unexpected source status counts: {payload['source_status_counts']}"
        )
    if payload["region_class_count_counts"] != EXPECTED_REGION_CLASS_COUNT_COUNTS:
        raise AssertionError(
            f"unexpected region class counts: {payload['region_class_count_counts']}"
        )
    if (
        payload["closed_descent_cycle_length_counts"]
        != EXPECTED_CLOSED_DESCENT_CYCLE_LENGTH_COUNTS
    ):
        raise AssertionError(
            "unexpected closed-descent cycle length counts: "
            f"{payload['closed_descent_cycle_length_counts']}"
        )
    if payload["max_region_class_count"] != 3:
        raise AssertionError(
            f"unexpected max region class count: {payload['max_region_class_count']}"
        )
    if payload["family_count"] != 16:
        raise AssertionError(f"unexpected family count: {payload['family_count']}")
    if payload["orbit_size_sum"] != 184:
        raise AssertionError(f"unexpected orbit-size sum: {payload['orbit_size_sum']}")
    certificates = payload["certificates"]
    if len(certificates) != 16:
        raise AssertionError("unexpected certificate count")
    expected_family_ids = [f"F{idx:02d}" for idx in range(1, 17)]
    actual_family_ids = [
        str(certificate["family_id"])
        for certificate in certificates
        if isinstance(certificate, dict)
    ]
    if actual_family_ids != expected_family_ids:
        raise AssertionError(f"unexpected family ids: {actual_family_ids}")
    for certificate in certificates:
        if not isinstance(certificate, dict):
            raise AssertionError("malformed certificate")
        cycle = certificate.get("closed_descent_cycle")
        if not isinstance(cycle, dict):
            raise AssertionError("missing closed descent cycle")
        if cycle.get("type") != "strict_quotient_closed_descent_cycle":
            raise AssertionError(f"unexpected cycle type: {cycle.get('type')!r}")
        if int(certificate["region_class_count"]) != int(cycle["class_count"]):
            raise AssertionError("region class count does not match cycle certificate")
        if int(cycle["cycle_length"]) < 1:
            raise AssertionError("closed descent cycle must be nonempty")


def validate_payload(
    payload: Any,
    *,
    source_path: Path = DEFAULT_SOURCE,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a checked-in closed-descent packet."""

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
        "family_count": 16,
        "orbit_size_sum": 184,
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
        assert_expected_closed_descent_packet_counts(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected closed-descent packet counts failed: {exc}")

    if recompute:
        try:
            expected_payload = closed_descent_packet_summary(source_path)
        except (AssertionError, OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"recomputed closed-descent packet failed: {exc}")
        else:
            expect_equal(errors, "closed-descent packet", payload, expected_payload)
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
        "orbit_size_sum": object_payload.get("orbit_size_sum"),
        "source_status_counts": object_payload.get("source_status_counts"),
        "region_class_count_counts": object_payload.get("region_class_count_counts"),
        "closed_descent_cycle_length_counts": object_payload.get(
            "closed_descent_cycle_length_counts"
        ),
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write generated packet")
    parser.add_argument("--check", action="store_true", help="validate an existing packet")
    parser.add_argument("--json", action="store_true", help="print stable JSON summary")
    parser.add_argument("--assert-expected", action="store_true")
    return parser.parse_args(argv)


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = _resolve(args.artifact)
    source = _resolve(args.source)
    out = _resolve(args.out)

    if args.write:
        payload = closed_descent_packet_summary(source)
        if args.assert_expected:
            assert_expected_closed_descent_packet_counts(payload)
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
            source_path=source,
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
        print("n=9 vertex-circle closed-descent packet")
        print(f"artifact: {summary['artifact']}")
        print(f"families: {summary['family_count']}")
        print(f"orbit-size sum: {summary['orbit_size_sum']}")
        print(f"region class counts: {summary['region_class_count_counts']}")
        print(f"cycle length counts: {summary['closed_descent_cycle_length_counts']}")
        if args.check or args.assert_expected:
            print("OK: closed-descent packet checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
