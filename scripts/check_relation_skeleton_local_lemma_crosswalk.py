#!/usr/bin/env python3
"""Cross-check relation skeletons against n=9 local-lemma replay coverage."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPT_DIR = ROOT / "scripts"
for path in (SRC, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_n9_vertex_circle_local_lemma_replay_crosswalk import (  # noqa: E402
    assert_expected_replay_crosswalk,
    crosswalk_payload as local_replay_crosswalk_payload,
)
from erdos97.path_display import display_path  # noqa: E402
from erdos97.relation_skeleton_catalog import (  # noqa: E402
    assert_expected_relation_skeleton_catalog,
)

SCHEMA = "erdos97.relation_skeleton_local_lemma_crosswalk.v1"
STATUS = "REVIEW_PENDING_PACKET_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Cross-artifact audit joining the relation-skeleton catalog to the "
    "aggregate n=9 vertex-circle local-lemma scan and simple replay. This is "
    "not a proof of n=9, not a counterexample, not an independent review of "
    "the exhaustive checker, and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_relation_skeleton_local_lemma_crosswalk.py",
    "command": (
        "python scripts/check_relation_skeleton_local_lemma_crosswalk.py "
        "--check --assert-expected --json"
    ),
}

DEFAULT_RELATION_SKELETONS = (
    ROOT / "data" / "certificates" / "relation_skeleton_catalog.json"
)
DEFAULT_AGGREGATE = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_local_lemmas.json"
)
DEFAULT_SIMPLE_REPLAY = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_local_lemma_simple_replay.json"
)

EXPECTED_FAMILY_IDS = [f"F{index:02d}" for index in range(1, 17)]
CONTRADICTION_MAP = {
    "strict_self_edge": ("self_edge", "reflexive_strict_edge"),
    "strict_directed_cycle": ("strict_cycle", "directed_strict_cycle"),
}


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def crosswalk_payload(
    relation_skeletons: Mapping[str, Any],
    aggregate: Mapping[str, Any],
    simple_replay: Mapping[str, Any],
    *,
    relation_skeletons_path: Path = DEFAULT_RELATION_SKELETONS,
    aggregate_path: Path = DEFAULT_AGGREGATE,
    simple_replay_path: Path = DEFAULT_SIMPLE_REPLAY,
) -> dict[str, Any]:
    """Return a family-level audit between skeletons and local lemmas."""

    errors: list[str] = []
    _append_expected_errors(errors, relation_skeletons)
    local_crosswalk = local_replay_crosswalk_payload(
        aggregate,
        simple_replay,
        aggregate_path=aggregate_path,
        simple_replay_path=simple_replay_path,
    )
    try:
        assert_expected_replay_crosswalk(local_crosswalk)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"local replay crosswalk failed: {exc}")

    relation_families = _relation_family_map(relation_skeletons, errors)
    local_families = _local_family_map(local_crosswalk, errors)
    family_crosswalk = _family_crosswalk(relation_families, local_families, errors)
    coverage = _coverage_summary(relation_families, local_families, family_crosswalk)

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": _common_value("n", relation_skeletons, local_crosswalk, errors),
        "cyclic_order": _common_value(
            "cyclic_order",
            relation_skeletons,
            local_crosswalk,
            errors,
        ),
        "source_artifacts": [
            _source_summary(
                relation_skeletons_path,
                "relation-skeleton catalog",
                relation_skeletons,
            ),
            _source_summary(
                aggregate_path,
                "aggregate local-lemma scan",
                aggregate,
            ),
            _source_summary(
                simple_replay_path,
                "simple local-lemma replay audit",
                simple_replay,
            ),
        ],
        "coverage_summary": coverage,
        "family_crosswalk": family_crosswalk,
        "local_replay_crosswalk_summary": local_crosswalk.get("coverage_summary"),
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed crosswalk says the checked relation skeletons and the "
            "stored local-lemma replay accounting agree family by family. It "
            "does not certify that the local-lemma packets are complete for "
            "n=9 and does not review the exhaustive brancher."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_relation_local_crosswalk(payload: Mapping[str, Any]) -> None:
    """Assert the expected relation-skeleton/local-lemma crosswalk counts."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    if payload.get("provenance") != PROVENANCE:
        raise AssertionError(f"provenance mismatch: {payload.get('provenance')!r}")
    claim_scope = str(payload.get("claim_scope", ""))
    for forbidden in ("proof of n=9", "counterexample", "global status update"):
        if f"not a {forbidden}" not in claim_scope and f"not an {forbidden}" not in claim_scope:
            raise AssertionError(f"claim_scope must explicitly reject {forbidden!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")

    coverage = payload.get("coverage_summary")
    if not isinstance(coverage, Mapping):
        raise AssertionError("coverage_summary must be an object")
    expected_coverage = {
        "relation_skeleton_count": 16,
        "local_family_count": 16,
        "matched_family_count": 16,
        "matched_assignment_count": 184,
        "self_edge_family_count": 13,
        "self_edge_assignment_count": 158,
        "strict_cycle_family_count": 3,
        "strict_cycle_assignment_count": 26,
        "expected_family_count": 16,
        "expected_assignment_count": 184,
    }
    for key, value in expected_coverage.items():
        if coverage.get(key) != value:
            raise AssertionError(
                f"coverage_summary[{key!r}] mismatch: expected {value}, "
                f"got {coverage.get(key)!r}"
            )

    family_ids = [
        str(item.get("family_id"))
        for item in payload.get("family_crosswalk", [])
        if isinstance(item, Mapping)
    ]
    if family_ids != EXPECTED_FAMILY_IDS:
        raise AssertionError(f"family ids mismatch: {family_ids!r}")


def _append_expected_errors(
    errors: list[str],
    relation_skeletons: Mapping[str, Any],
) -> None:
    try:
        assert_expected_relation_skeleton_catalog(relation_skeletons)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"relation skeleton expected-check failed: {exc}")


def _common_value(
    key: str,
    relation_skeletons: Mapping[str, Any],
    local_crosswalk: Mapping[str, Any],
    errors: list[str],
) -> Any:
    value = relation_skeletons.get(key)
    if local_crosswalk.get(key) != value:
        errors.append(
            f"{key} mismatch: relation {value!r} != local {local_crosswalk.get(key)!r}"
        )
    return value


def _source_summary(path: Path, role: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": display_path(path, ROOT),
        "role": role,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
    }


def _relation_family_map(
    relation_skeletons: Mapping[str, Any],
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    skeletons = relation_skeletons.get("skeletons")
    if not isinstance(skeletons, list):
        errors.append("relation skeletons must be a list")
        return {}

    family_map: dict[str, dict[str, Any]] = {}
    for skeleton in skeletons:
        if not isinstance(skeleton, Mapping):
            errors.append("relation skeleton entries must be objects")
            continue
        family_id = str(skeleton.get("source_family_id"))
        if family_id in family_map:
            errors.append(f"duplicate relation skeleton family {family_id}")
            continue
        coverage = skeleton.get("coverage")
        if not isinstance(coverage, Mapping):
            errors.append(f"{family_id} coverage must be an object")
            coverage = {}
        relation_quotient = skeleton.get("relation_quotient")
        if not isinstance(relation_quotient, Mapping):
            errors.append(f"{family_id} relation_quotient must be an object")
            relation_quotient = {}
        strict_edges = relation_quotient.get("strict_edges", [])
        equality_chains = relation_quotient.get("equality_chains", [])
        if not isinstance(strict_edges, list):
            errors.append(f"{family_id} strict_edges must be a list")
            strict_edges = []
        if not isinstance(equality_chains, list):
            errors.append(f"{family_id} equality_chains must be a list")
            equality_chains = []
        families = coverage.get("families", [])
        if families != [family_id]:
            errors.append(f"{family_id} coverage families mismatch: {families!r}")
        family_map[family_id] = {
            "family_id": family_id,
            "skeleton_id": str(skeleton.get("skeleton_id")),
            "template_id": str(skeleton.get("source_template_id")),
            "contradiction_type": str(skeleton.get("contradiction_type")),
            "assignment_count": int(coverage.get("assignment_count", -1)),
            "orbit_size": int(coverage.get("orbit_size_sum", -1)),
            "family_count": int(coverage.get("family_count", -1)),
            "strict_edge_count": len(strict_edges),
            "equality_chain_count": len(equality_chains),
            "source_packet": str(skeleton.get("source_packet")),
        }
    return family_map


def _local_family_map(
    local_crosswalk: Mapping[str, Any],
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    family_crosswalk = local_crosswalk.get("family_crosswalk")
    if not isinstance(family_crosswalk, list):
        errors.append("local crosswalk family_crosswalk must be a list")
        return {}

    family_map: dict[str, dict[str, Any]] = {}
    for record in family_crosswalk:
        if not isinstance(record, Mapping):
            errors.append("local family crosswalk entries must be objects")
            continue
        family_id = str(record.get("family_id"))
        if family_id in family_map:
            errors.append(f"duplicate local family {family_id}")
            continue
        family_map[family_id] = {
            "family_id": family_id,
            "lemma_id": str(record.get("lemma_id")),
            "obstruction_group": str(record.get("obstruction_group")),
            "template_id": str(record.get("template_id")),
            "assignment_count": int(record.get("assignment_count", -1)),
            "orbit_size": int(record.get("orbit_size", -1)),
            "aggregate_instance_count": int(record.get("aggregate_instance_count", -1)),
            "simple_obstruction_kind": str(record.get("simple_obstruction_kind")),
            "simple_replayed_step_count": int(record.get("simple_replayed_step_count", -1)),
        }
    return family_map


def _family_crosswalk(
    relation_families: Mapping[str, Mapping[str, Any]],
    local_families: Mapping[str, Mapping[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    relation_ids = set(relation_families)
    local_ids = set(local_families)
    if relation_ids != local_ids:
        errors.append(
            "family id mismatch: "
            f"relation-only={sorted(relation_ids - local_ids)!r}, "
            f"local-only={sorted(local_ids - relation_ids)!r}"
        )

    records: list[dict[str, Any]] = []
    for family_id in sorted(relation_ids & local_ids):
        relation = relation_families[family_id]
        local = local_families[family_id]
        record = {
            "family_id": family_id,
            "skeleton_id": relation["skeleton_id"],
            "lemma_id": local["lemma_id"],
            "template_id": local["template_id"],
            "relation_contradiction_type": relation["contradiction_type"],
            "local_obstruction_group": local["obstruction_group"],
            "assignment_count": local["assignment_count"],
            "orbit_size": local["orbit_size"],
            "relation_source_packet": relation["source_packet"],
            "relation_equality_chain_count": relation["equality_chain_count"],
            "relation_strict_edge_count": relation["strict_edge_count"],
            "simple_obstruction_kind": local["simple_obstruction_kind"],
            "simple_replayed_step_count": local["simple_replayed_step_count"],
        }
        for key in ("template_id", "assignment_count", "orbit_size"):
            if relation[key] != local[key]:
                errors.append(
                    f"{family_id} {key} mismatch: "
                    f"relation {relation[key]!r} != local {local[key]!r}"
                )
        if relation["family_count"] != 1:
            errors.append(f"{family_id} relation family_count must be 1")

        expected_group = CONTRADICTION_MAP.get(str(relation["contradiction_type"]))
        if expected_group is None:
            errors.append(
                f"{family_id} unknown relation contradiction type: "
                f"{relation['contradiction_type']!r}"
            )
        else:
            expected_obstruction_group, expected_kind = expected_group
            if local["obstruction_group"] != expected_obstruction_group:
                errors.append(
                    f"{family_id} obstruction group mismatch: "
                    f"relation expects {expected_obstruction_group!r}, "
                    f"local has {local['obstruction_group']!r}"
                )
            if local["simple_obstruction_kind"] != expected_kind:
                errors.append(
                    f"{family_id} simple obstruction mismatch: "
                    f"relation expects {expected_kind!r}, "
                    f"local has {local['simple_obstruction_kind']!r}"
                )
        if (
            local["obstruction_group"] == "strict_cycle"
            and relation["strict_edge_count"] != local["simple_replayed_step_count"]
        ):
            errors.append(
                f"{family_id} strict-cycle edge count mismatch: "
                f"relation {relation['strict_edge_count']} != "
                f"simple replay {local['simple_replayed_step_count']}"
            )
        records.append(record)
    return records


def _coverage_summary(
    relation_families: Mapping[str, Mapping[str, Any]],
    local_families: Mapping[str, Mapping[str, Any]],
    family_crosswalk: list[Mapping[str, Any]],
) -> dict[str, int]:
    self_edge_records = [
        item
        for item in family_crosswalk
        if item.get("local_obstruction_group") == "self_edge"
    ]
    strict_cycle_records = [
        item
        for item in family_crosswalk
        if item.get("local_obstruction_group") == "strict_cycle"
    ]
    return {
        "relation_skeleton_count": len(relation_families),
        "local_family_count": len(local_families),
        "matched_family_count": len(family_crosswalk),
        "matched_assignment_count": sum(
            int(item.get("assignment_count", 0)) for item in family_crosswalk
        ),
        "self_edge_family_count": len(self_edge_records),
        "self_edge_assignment_count": sum(
            int(item.get("assignment_count", 0)) for item in self_edge_records
        ),
        "strict_cycle_family_count": len(strict_cycle_records),
        "strict_cycle_assignment_count": sum(
            int(item.get("assignment_count", 0)) for item in strict_cycle_records
        ),
        "expected_family_count": 16,
        "expected_assignment_count": 184,
    }


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    coverage = payload["coverage_summary"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        (
            "matched families: "
            f"{coverage['matched_family_count']}/{coverage['expected_family_count']}"
        ),
        (
            "matched assignments: "
            f"{coverage['matched_assignment_count']}/"
            f"{coverage['expected_assignment_count']}"
        ),
        (
            "self-edge: "
            f"{coverage['self_edge_family_count']} families, "
            f"{coverage['self_edge_assignment_count']} assignments"
        ),
        (
            "strict-cycle: "
            f"{coverage['strict_cycle_family_count']} families, "
            f"{coverage['strict_cycle_assignment_count']} assignments"
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--relation-skeletons",
        type=Path,
        default=DEFAULT_RELATION_SKELETONS,
    )
    parser.add_argument("--aggregate", type=Path, default=DEFAULT_AGGREGATE)
    parser.add_argument("--simple-replay", type=Path, default=DEFAULT_SIMPLE_REPLAY)
    parser.add_argument("--check", action="store_true", help="validate the crosswalk")
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="Assert the expected relation/local-lemma counts.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON payload.")
    args = parser.parse_args(argv)

    relation_skeletons_path = _resolve(args.relation_skeletons)
    aggregate_path = _resolve(args.aggregate)
    simple_replay_path = _resolve(args.simple_replay)
    try:
        relation_skeletons = load_artifact(relation_skeletons_path)
        aggregate = load_artifact(aggregate_path)
        simple_replay = load_artifact(simple_replay_path)
        if not isinstance(relation_skeletons, Mapping):
            raise TypeError("relation skeleton artifact top level must be an object")
        if not isinstance(aggregate, Mapping):
            raise TypeError("aggregate artifact top level must be an object")
        if not isinstance(simple_replay, Mapping):
            raise TypeError("simple replay artifact top level must be an object")
        payload = crosswalk_payload(
            relation_skeletons,
            aggregate,
            simple_replay,
            relation_skeletons_path=relation_skeletons_path,
            aggregate_path=aggregate_path,
            simple_replay_path=simple_replay_path,
        )
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        payload = {
            "schema": SCHEMA,
            "status": STATUS,
            "trust": TRUST,
            "claim_scope": CLAIM_SCOPE,
            "validation_status": "failed",
            "validation_errors": [str(exc)],
            "provenance": dict(PROVENANCE),
        }

    if args.assert_expected:
        assert_expected_relation_local_crosswalk(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("relation-skeleton/local-lemma crosswalk")
        for line in summary_lines(payload):
            print(line)
        print("OK: relation-skeleton/local-lemma crosswalk checks passed")
    else:
        print("FAILED: relation-skeleton/local-lemma crosswalk", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
