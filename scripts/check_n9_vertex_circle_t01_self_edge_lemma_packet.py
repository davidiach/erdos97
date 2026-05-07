#!/usr/bin/env python3
"""Generate or check the focused T01/F09 n=9 self-edge local lemma packet."""

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
from erdos97.n9_vertex_circle_t01_self_edge_lemma_packet import (  # noqa: E402
    CLAIM_SCOPE,
    PROVENANCE,
    SCHEMA,
    STATUS,
    TRUST,
    assert_expected_t01_self_edge_lemma_packet,
    source_artifacts,
    t01_self_edge_lemma_packet_payload,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_t01_self_edge_lemma_packet.json"
)
EXPECTED_TOP_LEVEL_KEYS = {
    "assignment_count",
    "assignment_ids",
    "claim_scope",
    "core_selected_rows",
    "core_size",
    "cyclic_order",
    "distance_equality",
    "equality_chain",
    "family_count",
    "family_id",
    "interpretation",
    "local_lemma",
    "n",
    "orbit_size",
    "provenance",
    "replay",
    "row_size",
    "schema",
    "source_artifacts",
    "source_catalog_record",
    "source_template_record",
    "status",
    "strict_inequality",
    "template_id",
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
    template_catalog_path: Path = DEFAULT_TEMPLATE_CATALOG,
) -> dict[str, Any]:
    """Load the source artifacts used by the focused T01 packet."""

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
        return t01_self_edge_lemma_packet_payload(
            source_payloads["self_edge_packet"],
            source_payloads["template_catalog"],
        )
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"source-bound T01 self-edge lemma packet failed: {exc}")
        return None


def _validate_local_lemma(payload: dict[str, Any], errors: list[str]) -> None:
    lemma = payload.get("local_lemma")
    if not isinstance(lemma, dict):
        errors.append("local_lemma must be an object")
        return
    expect_equal(errors, "local_lemma review_status", lemma.get("review_status"), "review_pending")
    selected_equalities = lemma.get("selected_distance_equalities")
    if not isinstance(selected_equalities, list) or len(selected_equalities) != 3:
        errors.append("local_lemma selected_distance_equalities must have three steps")
    statement = str(lemma.get("strict_inequality_statement", ""))
    if "[1, 8]" not in statement or "[1, 2]" not in statement:
        errors.append("local_lemma strict inequality statement must name [1, 8] and [1, 2]")
    contradiction = str(lemma.get("contradiction", ""))
    if "reflexive strict edge" not in contradiction:
        errors.append("local_lemma contradiction must mention a reflexive strict edge")


def _validate_replay(payload: dict[str, Any], errors: list[str]) -> None:
    replay = payload.get("replay")
    if not isinstance(replay, dict):
        errors.append("replay must be an object")
        return
    expect_equal(errors, "replay status", replay.get("status"), "self_edge")
    expect_equal(errors, "replay selected_row_count", replay.get("selected_row_count"), 3)
    expect_equal(errors, "replay strict_edge_count", replay.get("strict_edge_count"), 27)
    expect_equal(
        errors,
        "replay self_edge_conflict_count",
        replay.get("self_edge_conflict_count"),
        2,
    )
    primary = replay.get("primary_self_edge_conflict")
    if not isinstance(primary, dict):
        errors.append("replay primary_self_edge_conflict must be an object")
        return
    expect_equal(errors, "primary row", primary.get("row"), 0)
    expect_equal(errors, "primary witness_order", primary.get("witness_order"), [1, 2, 4, 8])
    expect_equal(errors, "primary outer_pair", primary.get("outer_pair"), [1, 8])
    expect_equal(errors, "primary inner_pair", primary.get("inner_pair"), [1, 2])


def validate_payload(
    payload: Any,
    *,
    source_payloads: dict[str, Any] | None = None,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a focused T01/F09 local lemma packet."""

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
        "template_id": "T01",
        "family_id": "F09",
        "assignment_count": 6,
        "assignment_ids": ["A014", "A024", "A031", "A140", "A166", "A175"],
        "family_count": 1,
        "orbit_size": 6,
        "core_size": 3,
        "core_selected_rows": [
            [0, 1, 2, 4, 8],
            [1, 0, 3, 5, 8],
            [2, 0, 1, 4, 6],
        ],
        "equality_chain": [[1, 8], [0, 1], [0, 2], [1, 2]],
        "provenance": PROVENANCE,
    }
    for key, expected in expected_meta.items():
        expect_equal(errors, key, payload.get(key), expected)

    strict = payload.get("strict_inequality")
    if not isinstance(strict, dict):
        errors.append("strict_inequality must be an object")
    else:
        expect_equal(errors, "strict row", strict.get("row"), 0)
        expect_equal(errors, "strict witness_order", strict.get("witness_order"), [1, 2, 4, 8])
        expect_equal(errors, "strict outer_pair", strict.get("outer_pair"), [1, 8])
        expect_equal(errors, "strict inner_pair", strict.get("inner_pair"), [1, 2])
        expect_equal(errors, "strict outer_span", strict.get("outer_span"), 3)
        expect_equal(errors, "strict inner_span", strict.get("inner_span"), 1)

    equality = payload.get("distance_equality")
    if not isinstance(equality, dict):
        errors.append("distance_equality must be an object")
    else:
        expect_equal(errors, "equality start_pair", equality.get("start_pair"), [1, 8])
        expect_equal(errors, "equality end_pair", equality.get("end_pair"), [1, 2])
        expect_equal(
            errors,
            "equality path",
            equality.get("path"),
            [
                {"row": 1, "next_pair": [0, 1]},
                {"row": 0, "next_pair": [0, 2]},
                {"row": 2, "next_pair": [1, 2]},
            ],
        )

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

    _validate_local_lemma(payload, errors)
    _validate_replay(payload, errors)
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
        assert_expected_t01_self_edge_lemma_packet(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected T01 self-edge lemma packet counts failed: {exc}")

    if recompute and expected_payload is not None and not errors:
        expect_equal(errors, "T01 self-edge lemma packet", payload, expected_payload)
    return errors


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    replay = object_payload.get("replay")
    replay = replay if isinstance(replay, dict) else {}
    return {
        "ok": not errors,
        "artifact": display_path(path, ROOT),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "template_id": object_payload.get("template_id"),
        "family_id": object_payload.get("family_id"),
        "assignment_count": object_payload.get("assignment_count"),
        "core_size": object_payload.get("core_size"),
        "replay_status": replay.get("status"),
        "strict_edge_count": replay.get("strict_edge_count"),
        "self_edge_conflict_count": replay.get("self_edge_conflict_count"),
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
        payload = t01_self_edge_lemma_packet_payload(
            sources["self_edge_packet"],
            sources["template_catalog"],
        )
        if args.assert_expected:
            assert_expected_t01_self_edge_lemma_packet(payload)
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
        print("n=9 vertex-circle T01/F09 self-edge local lemma packet")
        print(f"artifact: {summary['artifact']}")
        print(f"assignments: {summary['assignment_count']}")
        print(f"core size: {summary['core_size']}")
        print(f"replay status: {summary['replay_status']}")
        if args.check or args.assert_expected:
            print("OK: T01 self-edge local lemma packet checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
