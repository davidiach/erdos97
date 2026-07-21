#!/usr/bin/env python3
"""Generate or check the focused relation-skeleton catalog."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]

SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from erdos97.json_io import write_json  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402
from erdos97.relation_skeleton_catalog import (  # noqa: E402
    CLAIM_SCOPE,
    EXPECTED_CONTRADICTION_TYPE_COUNTS,
    EXPECTED_FAMILY_DETAILS,
    EXPECTED_SKELETON_IDS,
    EXPECTED_SOURCE_ARTIFACTS,
    FOCUSED_TEMPLATE_IDS,
    PROVENANCE,
    SCHEMA,
    STATUS,
    TRUST,
    assert_expected_relation_skeleton_catalog,
    relation_skeleton_catalog_payload,
)

DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "relation_skeleton_catalog.json"
FOCUSED_CHECKERS: dict[str, ModuleType] = {
    template_id: importlib.import_module(
        "check_n9_vertex_circle_"
        f"t{int(template_id[1:]):02d}_"
        f"{'self_edge' if int(template_id[1:]) < 10 else 'strict_cycle'}"
        "_lemma_packet"
    )
    for template_id in FOCUSED_TEMPLATE_IDS
}
DEFAULT_FOCUSED_PACKET_PATHS = {
    template_id: checker.DEFAULT_ARTIFACT
    for template_id, checker in FOCUSED_CHECKERS.items()
}

EXPECTED_TOP_LEVEL_KEYS = {
    "catalog_scope",
    "claim_scope",
    "contradiction_type_counts",
    "cyclic_order",
    "interpretation",
    "n",
    "provenance",
    "row_size",
    "schema",
    "skeleton_count",
    "skeleton_ids",
    "skeletons",
    "source_artifacts",
    "status",
    "trust",
}
EXPECTED_SKELETON_KEYS = {
    "conclusion",
    "contradiction_type",
    "coverage",
    "does_not_prove",
    "hypotheses",
    "obstruction_system",
    "relation_quotient",
    "review_status",
    "skeleton_id",
    "source_family_id",
    "source_packet",
    "source_template_id",
    "verifier",
}


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a mismatch error when values differ."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def load_source_payloads(
    *,
    packet_paths: Mapping[str, Path] | None = None,
) -> dict[str, Any]:
    """Load source packets used by the relation-skeleton catalog."""

    paths = dict(DEFAULT_FOCUSED_PACKET_PATHS)
    if packet_paths is not None:
        paths.update(packet_paths)
    return {
        f"{template_id.lower()}_packet": load_artifact(_resolve(paths[template_id]))
        for template_id in FOCUSED_TEMPLATE_IDS
    }


def _validate_sources(source_payloads: dict[str, Any], errors: list[str]) -> None:
    for label in FOCUSED_TEMPLATE_IDS:
        key = f"{label.lower()}_packet"
        checker = FOCUSED_CHECKERS[label]
        load_sources = checker.load_source_payloads
        validate = checker.validate_payload
        packet = source_payloads.get(key)
        if not isinstance(packet, dict):
            errors.append(f"source {label} packet must be an object")
            continue
        try:
            packet_sources = load_sources()
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"could not load {label} source packets: {exc}")
            continue
        errors.extend(
            f"source {label} packet invalid: {error}"
            for error in validate(packet, source_payloads=packet_sources, recompute=False)
        )


def _expected_payload(
    source_payloads: dict[str, Any],
    errors: list[str],
) -> dict[str, Any] | None:
    try:
        return relation_skeleton_catalog_payload(
            {
                template_id: source_payloads[f"{template_id.lower()}_packet"]
                for template_id in FOCUSED_TEMPLATE_IDS
            }
        )
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"source-bound relation skeleton catalog failed: {exc}")
        return None


def _skeletons_by_id(payload: dict[str, Any], errors: list[str]) -> dict[str, dict[str, Any]]:
    skeletons = payload.get("skeletons")
    if not isinstance(skeletons, list):
        errors.append("skeletons must be a list")
        return {}
    if len(skeletons) != len(EXPECTED_SKELETON_IDS):
        errors.append(
            f"skeletons length mismatch: expected {len(EXPECTED_SKELETON_IDS)}, "
            f"got {len(skeletons)}"
        )
    by_id: dict[str, dict[str, Any]] = {}
    for skeleton in skeletons:
        if not isinstance(skeleton, dict):
            errors.append("skeleton entries must be objects")
            continue
        if set(skeleton) != EXPECTED_SKELETON_KEYS:
            errors.append(
                f"{skeleton.get('skeleton_id', '<unknown>')} keys mismatch: "
                f"expected {sorted(EXPECTED_SKELETON_KEYS)!r}, got {sorted(skeleton)!r}"
            )
        skeleton_id = str(skeleton.get("skeleton_id"))
        if skeleton_id in by_id:
            errors.append(f"duplicate skeleton id: {skeleton_id}")
        by_id[skeleton_id] = skeleton
    if set(by_id) != set(EXPECTED_SKELETON_IDS):
        errors.append(
            f"skeleton ids mismatch: expected {list(EXPECTED_SKELETON_IDS)!r}, "
            f"got {sorted(by_id)!r}"
        )
    return {
        skeleton_id: by_id[skeleton_id]
        for skeleton_id in EXPECTED_SKELETON_IDS
        if skeleton_id in by_id
    }


def _validate_source_artifacts(payload: dict[str, Any], errors: list[str]) -> None:
    artifacts = payload.get("source_artifacts")
    if not isinstance(artifacts, list):
        errors.append("source_artifacts must be a list")
        return
    paths = [artifact.get("path") for artifact in artifacts if isinstance(artifact, dict)]
    expect_equal(errors, "source_artifact paths", paths, list(EXPECTED_SOURCE_ARTIFACTS))


def _validate_t01_skeleton(skeleton: dict[str, Any], errors: list[str]) -> None:
    expect_equal(errors, "T01 contradiction_type", skeleton.get("contradiction_type"), "strict_self_edge")
    expect_equal(errors, "T01 source_packet", skeleton.get("source_packet"), EXPECTED_SOURCE_ARTIFACTS[0])
    expect_equal(errors, "T01 source_template_id", skeleton.get("source_template_id"), "T01")
    expect_equal(errors, "T01 source_family_id", skeleton.get("source_family_id"), "F09")
    coverage = skeleton.get("coverage")
    if not isinstance(coverage, dict):
        errors.append("T01 coverage must be an object")
    else:
        expect_equal(errors, "T01 assignment_count", coverage.get("assignment_count"), 6)
        expect_equal(errors, "T01 families", coverage.get("families"), ["F09"])
    relation = skeleton.get("relation_quotient")
    if not isinstance(relation, dict):
        errors.append("T01 relation_quotient must be an object")
    else:
        strict_edges = relation.get("strict_edges")
        if not isinstance(strict_edges, list) or len(strict_edges) != 1:
            errors.append("T01 must record exactly one displayed strict edge")
        expect_equal(
            errors,
            "T01 equality_chains",
            relation.get("equality_chains"),
            [[[1, 8], [0, 1], [0, 2], [1, 2]]],
        )
    conclusion = skeleton.get("conclusion")
    if not isinstance(conclusion, dict):
        errors.append("T01 conclusion must be an object")
    else:
        expect_equal(errors, "T01 conclusion kind", conclusion.get("kind"), "strict_self_edge")
        expect_equal(errors, "T01 quotient_class", conclusion.get("quotient_class"), [0, 1])
        if "itself" not in str(conclusion.get("obstruction", "")):
            errors.append("T01 obstruction must describe a self-edge")


def _validate_t10_skeleton(skeleton: dict[str, Any], errors: list[str]) -> None:
    expect_equal(
        errors,
        "T10 contradiction_type",
        skeleton.get("contradiction_type"),
        "strict_directed_cycle",
    )
    expect_equal(errors, "T10 source_packet", skeleton.get("source_packet"), EXPECTED_SOURCE_ARTIFACTS[9])
    expect_equal(errors, "T10 source_template_id", skeleton.get("source_template_id"), "T10")
    expect_equal(errors, "T10 source_family_id", skeleton.get("source_family_id"), "F12")
    coverage = skeleton.get("coverage")
    if not isinstance(coverage, dict):
        errors.append("T10 coverage must be an object")
    else:
        expect_equal(errors, "T10 assignment_count", coverage.get("assignment_count"), 18)
        expect_equal(errors, "T10 families", coverage.get("families"), ["F12"])
    relation = skeleton.get("relation_quotient")
    if not isinstance(relation, dict):
        errors.append("T10 relation_quotient must be an object")
    else:
        strict_edges = relation.get("strict_edges")
        if not isinstance(strict_edges, list) or len(strict_edges) != 2:
            errors.append("T10 must record exactly two displayed strict edges")
        expect_equal(
            errors,
            "T10 equality_chains",
            relation.get("equality_chains"),
            [[[0, 3], [3, 6], [1, 6]], [[0, 1], [0, 6]]],
        )
    conclusion = skeleton.get("conclusion")
    if not isinstance(conclusion, dict):
        errors.append("T10 conclusion must be an object")
    else:
        expect_equal(errors, "T10 conclusion kind", conclusion.get("kind"), "strict_directed_cycle")
        expect_equal(errors, "T10 cycle_length", conclusion.get("cycle_length"), 2)
        quotient_cycle = conclusion.get("quotient_cycle")
        if not isinstance(quotient_cycle, list) or len(quotient_cycle) != 2:
            errors.append("T10 quotient_cycle must contain two cycle steps")


def _validate_skeletons(payload: dict[str, Any], errors: list[str]) -> None:
    skeletons = _skeletons_by_id(payload, errors)
    if EXPECTED_SKELETON_IDS[0] in skeletons:
        _validate_t01_skeleton(skeletons[EXPECTED_SKELETON_IDS[0]], errors)
    if "VC-T10-F12-strict-directed-cycle" in skeletons:
        _validate_t10_skeleton(skeletons["VC-T10-F12-strict-directed-cycle"], errors)
    source_by_template = dict(zip(FOCUSED_TEMPLATE_IDS, EXPECTED_SOURCE_ARTIFACTS, strict=True))
    for skeleton_id, (
        template_id,
        family_id,
        contradiction_type,
        assignment_count,
        strict_edge_count,
    ) in EXPECTED_FAMILY_DETAILS.items():
        skeleton = skeletons.get(skeleton_id)
        if skeleton is None:
            continue
        source_packet = source_by_template[template_id]
        expect_equal(errors, f"{skeleton_id} source_packet", skeleton.get("source_packet"), source_packet)
        expect_equal(errors, f"{skeleton_id} source_template_id", skeleton.get("source_template_id"), template_id)
        expect_equal(errors, f"{skeleton_id} source_family_id", skeleton.get("source_family_id"), family_id)
        expect_equal(errors, f"{skeleton_id} contradiction_type", skeleton.get("contradiction_type"), contradiction_type)
        coverage = skeleton.get("coverage")
        if not isinstance(coverage, dict):
            errors.append(f"{skeleton_id} coverage must be an object")
        else:
            expect_equal(errors, f"{skeleton_id} assignment_count", coverage.get("assignment_count"), assignment_count)
            expect_equal(errors, f"{skeleton_id} families", coverage.get("families"), [family_id])
        relation = skeleton.get("relation_quotient")
        if not isinstance(relation, dict):
            errors.append(f"{skeleton_id} relation_quotient must be an object")
        else:
            strict_edges = relation.get("strict_edges")
            if not isinstance(strict_edges, list) or len(strict_edges) != strict_edge_count:
                errors.append(f"{skeleton_id} strict edge count must be {strict_edge_count}")
    for skeleton_id, skeleton in skeletons.items():
        expect_equal(errors, f"{skeleton_id} review_status", skeleton.get("review_status"), "review_pending")
        expect_equal(
            errors,
            f"{skeleton_id} obstruction_system",
            skeleton.get("obstruction_system"),
            "vertex_circle_selected_distance_quotient",
        )
        does_not_prove = skeleton.get("does_not_prove")
        if not isinstance(does_not_prove, list) or "Erdos Problem #97" not in does_not_prove:
            errors.append(f"{skeleton_id} must preserve the global no-proof guardrail")


def validate_payload(
    payload: Any,
    *,
    source_payloads: dict[str, Any] | None = None,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for the relation-skeleton catalog."""

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
        "catalog_scope": "vertex-circle selected-distance quotient skeletons",
        "n": 9,
        "row_size": 4,
        "cyclic_order": list(range(9)),
        "skeleton_count": len(EXPECTED_SKELETON_IDS),
        "skeleton_ids": list(EXPECTED_SKELETON_IDS),
        "contradiction_type_counts": EXPECTED_CONTRADICTION_TYPE_COUNTS,
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
            errors.append("interpretation must preserve the n=9 no-proof statement")
        if not any("No proof of Erdos Problem #97" in item for item in interpretation):
            errors.append("interpretation must preserve the global no-proof statement")

    _validate_source_artifacts(payload, errors)
    _validate_skeletons(payload, errors)
    _validate_sources(source_payloads, errors)
    expected_payload = None if errors else _expected_payload(source_payloads, errors)
    if expected_payload is not None:
        expect_equal(
            errors,
            "source_artifacts",
            payload.get("source_artifacts"),
            expected_payload["source_artifacts"],
        )

    try:
        assert_expected_relation_skeleton_catalog(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected relation skeleton catalog constants failed: {exc}")

    if recompute and expected_payload is not None and not errors:
        expect_equal(errors, "relation skeleton catalog", payload, expected_payload)
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
        "skeleton_count": object_payload.get("skeleton_count"),
        "skeleton_ids": object_payload.get("skeleton_ids"),
        "contradiction_type_counts": object_payload.get("contradiction_type_counts"),
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
    for template_id in FOCUSED_TEMPLATE_IDS:
        parser.add_argument(
            f"--{template_id.lower()}-packet",
            type=Path,
            default=DEFAULT_FOCUSED_PACKET_PATHS[template_id],
            help=f"Path to focused {template_id} local lemma packet JSON.",
        )
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
            packet_paths={
                template_id: getattr(args, f"{template_id.lower()}_packet")
                for template_id in FOCUSED_TEMPLATE_IDS
            }
        )
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAILED: could not load source artifacts: {exc}", file=sys.stderr)
        return 1

    if args.write:
        payload = relation_skeleton_catalog_payload(
            {
                template_id: sources[f"{template_id.lower()}_packet"]
                for template_id in FOCUSED_TEMPLATE_IDS
            }
        )
        if args.assert_expected:
            assert_expected_relation_skeleton_catalog(payload)
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
        print("relation-skeleton catalog")
        print(f"artifact: {summary['artifact']}")
        print(f"skeletons: {summary['skeleton_count']}")
        print(f"types: {summary['contradiction_type_counts']}")
        if args.check or args.assert_expected:
            print("OK: relation-skeleton catalog checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
