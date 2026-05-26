#!/usr/bin/env python3
"""Cross-check aggregate n=9 local-lemma coverage against simple replay."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n9_vertex_circle_local_lemma_simple_replay import (  # noqa: E402
    assert_expected_simple_packet_replay,
)
from erdos97.n9_vertex_circle_local_lemmas import (  # noqa: E402
    NESTED_SPOKE_LEMMA,
    SHARED_ENDPOINT_LEMMA,
    T03_SELECTED_PATH_SELF_EDGE,
    T04_SELECTED_PATH_SELF_EDGE,
    T10_STRICT_CYCLE_LEMMA,
    T11_STRICT_CYCLE_LEMMA,
    T12_STRICT_CYCLE_LEMMA,
    assert_expected_local_lemma_scan,
)
from erdos97.path_display import display_path  # noqa: E402

SCHEMA = "erdos97.n9_vertex_circle_local_lemma_replay_crosswalk.v1"
STATUS = "REVIEW_PENDING_PACKET_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Cross-artifact audit joining the aggregate n=9 vertex-circle local-lemma "
    "scan to the simple packet replay. This is not a proof of n=9, not a "
    "counterexample, not an independent review of the exhaustive checker, and "
    "not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py",
    "command": (
        "python scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py "
        "--check --assert-expected --json"
    ),
}

DEFAULT_AGGREGATE = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_local_lemmas.json"
)
DEFAULT_SIMPLE_REPLAY = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_local_lemma_simple_replay.json"
)

SELF_EDGE_LEMMAS = {
    SHARED_ENDPOINT_LEMMA,
    NESTED_SPOKE_LEMMA,
    T03_SELECTED_PATH_SELF_EDGE,
    T04_SELECTED_PATH_SELF_EDGE,
}
STRICT_CYCLE_LEMMAS = {
    T10_STRICT_CYCLE_LEMMA,
    T11_STRICT_CYCLE_LEMMA,
    T12_STRICT_CYCLE_LEMMA,
}
EXPECTED_FAMILY_IDS = [f"F{index:02d}" for index in range(1, 17)]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def crosswalk_payload(
    aggregate: Mapping[str, Any],
    simple_replay: Mapping[str, Any],
    *,
    aggregate_path: Path = DEFAULT_AGGREGATE,
    simple_replay_path: Path = DEFAULT_SIMPLE_REPLAY,
) -> dict[str, Any]:
    """Return a family-level crosswalk between aggregate and replay artifacts."""

    errors: list[str] = []
    _append_expected_errors(errors, aggregate, simple_replay)

    aggregate_families = _aggregate_family_map(aggregate, errors)
    simple_families = _simple_family_map(simple_replay, errors)
    family_crosswalk = _family_crosswalk(aggregate_families, simple_families, errors)
    focused_summary = _focused_crosscheck_summary(aggregate, simple_families, errors)

    self_edge_records = [
        item for item in family_crosswalk if item.get("obstruction_group") == "self_edge"
    ]
    strict_cycle_records = [
        item
        for item in family_crosswalk
        if item.get("obstruction_group") == "strict_cycle"
    ]
    coverage = {
        "aggregate_family_count": len(aggregate_families),
        "simple_replay_family_count": len(simple_families),
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

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": _common_value("n", aggregate, simple_replay, errors),
        "cyclic_order": _common_value("cyclic_order", aggregate, simple_replay, errors),
        "source_artifacts": [
            {
                "path": display_path(aggregate_path, ROOT),
                "role": "aggregate local-lemma scan",
                "schema": aggregate.get("schema"),
                "status": aggregate.get("status"),
                "trust": aggregate.get("trust"),
            },
            {
                "path": display_path(simple_replay_path, ROOT),
                "role": "simple packet replay audit",
                "schema": simple_replay.get("schema"),
                "status": simple_replay.get("status"),
                "trust": simple_replay.get("trust"),
            },
        ],
        "coverage_summary": coverage,
        "focused_crosscheck_summary": focused_summary,
        "family_crosswalk": family_crosswalk,
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed crosswalk says the aggregate quotient-helper scan and the "
            "simple packet replay agree on the stored n=9 local-template family "
            "coverage. It does not certify that the local-template packets are "
            "complete for n=9."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_replay_crosswalk(payload: Mapping[str, Any]) -> None:
    """Assert the expected cross-artifact local-lemma replay counts."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    if payload.get("provenance") != PROVENANCE:
        raise AssertionError(f"provenance mismatch: {payload.get('provenance')!r}")
    if payload.get("claim_scope") != CLAIM_SCOPE:
        raise AssertionError(f"claim_scope mismatch: {payload.get('claim_scope')!r}")
    claim_scope = CLAIM_SCOPE
    for forbidden in ("proof of n=9", "counterexample", "global status update"):
        if (
            f"not a {forbidden}" not in claim_scope
            and f"not an {forbidden}" not in claim_scope
        ):
            raise AssertionError(f"claim_scope must explicitly reject {forbidden!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")

    coverage = payload.get("coverage_summary")
    if not isinstance(coverage, Mapping):
        raise AssertionError("coverage_summary must be an object")
    expected_coverage = {
        "aggregate_family_count": 16,
        "simple_replay_family_count": 16,
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

    focused = payload.get("focused_crosscheck_summary")
    if not isinstance(focused, Mapping):
        raise AssertionError("focused_crosscheck_summary must be an object")
    if focused.get("focused_family_count") != 16:
        raise AssertionError("focused family count mismatch")
    if focused.get("focused_assignment_count") != 184:
        raise AssertionError("focused assignment count mismatch")


def _append_expected_errors(
    errors: list[str],
    aggregate: Mapping[str, Any],
    simple_replay: Mapping[str, Any],
) -> None:
    try:
        assert_expected_local_lemma_scan(dict(aggregate))
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"aggregate expected-check failed: {exc}")
    try:
        assert_expected_simple_packet_replay(simple_replay)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"simple replay expected-check failed: {exc}")


def _common_value(
    key: str,
    aggregate: Mapping[str, Any],
    simple_replay: Mapping[str, Any],
    errors: list[str],
) -> Any:
    value = aggregate.get(key)
    if simple_replay.get(key) != value:
        errors.append(
            f"{key} mismatch: aggregate {value!r} != simple {simple_replay.get(key)!r}"
        )
    return value


def _aggregate_family_map(
    aggregate: Mapping[str, Any],
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    family_map: dict[str, dict[str, Any]] = {}
    lemmas = aggregate.get("lemmas")
    if not isinstance(lemmas, list):
        errors.append("aggregate lemmas must be a list")
        return family_map
    for lemma in lemmas:
        if not isinstance(lemma, Mapping):
            errors.append("aggregate lemma entries must be objects")
            continue
        lemma_id = str(lemma.get("lemma_id"))
        if lemma_id in SELF_EDGE_LEMMAS:
            group = "self_edge"
        elif lemma_id in STRICT_CYCLE_LEMMAS:
            group = "strict_cycle"
        else:
            errors.append(f"unknown aggregate lemma id: {lemma_id}")
            continue
        instances = lemma.get("instances")
        if not isinstance(instances, list):
            errors.append(f"{lemma_id} instances must be a list")
            continue
        for instance in instances:
            if not isinstance(instance, Mapping):
                errors.append(f"{lemma_id} instance entries must be objects")
                continue
            family_id = str(instance.get("family_id"))
            if family_id in family_map:
                previous = family_map[family_id]
                for key, value in (
                    ("lemma_id", lemma_id),
                    ("obstruction_group", group),
                    ("template_id", str(instance.get("template_id"))),
                    ("assignment_count", int(instance.get("assignment_count", -1))),
                    ("orbit_size", int(instance.get("orbit_size", -1))),
                ):
                    if previous[key] != value:
                        errors.append(
                            f"duplicate aggregate family {family_id} {key} mismatch: "
                            f"{previous[key]!r} != {value!r}"
                        )
                previous["aggregate_instance_count"] += 1
                continue
            family_map[family_id] = {
                "family_id": family_id,
                "lemma_id": lemma_id,
                "obstruction_group": group,
                "template_id": str(instance.get("template_id")),
                "assignment_count": int(instance.get("assignment_count", -1)),
                "orbit_size": int(instance.get("orbit_size", -1)),
                "aggregate_instance_count": 1,
            }
    return family_map


def _simple_family_map(
    simple_replay: Mapping[str, Any],
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    family_map: dict[str, dict[str, Any]] = {}
    for group, key in (("self_edge", "self_edge"), ("strict_cycle", "strict_cycle")):
        section = simple_replay.get(key)
        if not isinstance(section, Mapping):
            errors.append(f"simple replay {key} section must be an object")
            continue
        records = section.get("records")
        if not isinstance(records, list):
            errors.append(f"simple replay {key} records must be a list")
            continue
        for record in records:
            if not isinstance(record, Mapping):
                errors.append(f"simple replay {key} record entries must be objects")
                continue
            family_id = str(record.get("family_id"))
            if family_id in family_map:
                errors.append(f"duplicate simple replay family {family_id}")
                continue
            family_map[family_id] = {
                "family_id": family_id,
                "obstruction_group": group,
                "template_id": str(record.get("template_id")),
                "assignment_count": int(record.get("assignment_count", -1)),
                "orbit_size": int(record.get("orbit_size", -1)),
                "obstruction_kind": str(record.get("obstruction_kind")),
                "replayed_step_count": int(record.get("replayed_step_count", -1)),
            }
    return family_map


def _family_crosswalk(
    aggregate_families: Mapping[str, Mapping[str, Any]],
    simple_families: Mapping[str, Mapping[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    aggregate_ids = set(aggregate_families)
    simple_ids = set(simple_families)
    if aggregate_ids != simple_ids:
        errors.append(
            "family id mismatch: "
            f"aggregate-only={sorted(aggregate_ids - simple_ids)!r}, "
            f"simple-only={sorted(simple_ids - aggregate_ids)!r}"
        )

    records: list[dict[str, Any]] = []
    for family_id in sorted(aggregate_ids & simple_ids):
        aggregate = aggregate_families[family_id]
        simple = simple_families[family_id]
        record = {
            "family_id": family_id,
            "lemma_id": aggregate["lemma_id"],
            "obstruction_group": aggregate["obstruction_group"],
            "template_id": aggregate["template_id"],
            "assignment_count": aggregate["assignment_count"],
            "orbit_size": aggregate["orbit_size"],
            "aggregate_instance_count": aggregate["aggregate_instance_count"],
            "simple_obstruction_kind": simple["obstruction_kind"],
            "simple_replayed_step_count": simple["replayed_step_count"],
        }
        for key in ("obstruction_group", "template_id", "assignment_count", "orbit_size"):
            if aggregate[key] != simple[key]:
                errors.append(
                    f"{family_id} {key} mismatch: "
                    f"aggregate {aggregate[key]!r} != simple {simple[key]!r}"
                )
        records.append(record)
    return records


def _focused_crosscheck_summary(
    aggregate: Mapping[str, Any],
    simple_families: Mapping[str, Mapping[str, Any]],
    errors: list[str],
) -> dict[str, Any]:
    focused = aggregate.get("focused_note_crosscheck")
    if not isinstance(focused, list):
        errors.append("aggregate focused_note_crosscheck must be a list")
        return {
            "focused_template_count": 0,
            "focused_family_count": 0,
            "focused_assignment_count": 0,
            "focused_family_ids": [],
        }

    focused_family_ids: list[str] = []
    focused_assignment_count = 0
    for item in focused:
        if not isinstance(item, Mapping):
            errors.append("focused crosscheck entries must be objects")
            continue
        if item.get("check_status") != "checked":
            errors.append(f"{item.get('template_id')} focused item is not checked")
        for checked in item.get("families_checked", []):
            if not isinstance(checked, Mapping):
                errors.append(f"{item.get('template_id')} checked family must be an object")
                continue
            family_id = str(checked.get("family_id"))
            focused_family_ids.append(family_id)
            simple = simple_families.get(family_id)
            if simple is None:
                errors.append(f"{family_id} focused family missing from simple replay")
                continue
            assignment_count = int(checked.get("assignment_count", -1))
            focused_assignment_count += assignment_count
            if assignment_count != simple["assignment_count"]:
                errors.append(
                    f"{family_id} focused assignment mismatch: "
                    f"{assignment_count} != simple {simple['assignment_count']}"
                )
    sorted_focused = sorted(focused_family_ids)
    if sorted_focused != EXPECTED_FAMILY_IDS:
        errors.append(f"focused family ids mismatch: {sorted_focused!r}")
    return {
        "focused_template_count": len(focused),
        "focused_family_count": len(focused_family_ids),
        "focused_assignment_count": focused_assignment_count,
        "focused_family_ids": sorted_focused,
    }


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    coverage = payload["coverage_summary"]
    focused = payload["focused_crosscheck_summary"]
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
        (
            "focused packet families: "
            f"{focused['focused_family_count']} families, "
            f"{focused['focused_assignment_count']} assignments"
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aggregate", type=Path, default=DEFAULT_AGGREGATE)
    parser.add_argument("--simple-replay", type=Path, default=DEFAULT_SIMPLE_REPLAY)
    parser.add_argument("--check", action="store_true", help="validate the crosswalk")
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="Assert the expected cross-artifact replay counts.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON payload.")
    args = parser.parse_args(argv)

    aggregate_path = _resolve(args.aggregate)
    simple_replay_path = _resolve(args.simple_replay)
    try:
        aggregate = load_artifact(aggregate_path)
        simple_replay = load_artifact(simple_replay_path)
        if not isinstance(aggregate, Mapping):
            raise TypeError("aggregate artifact top level must be an object")
        if not isinstance(simple_replay, Mapping):
            raise TypeError("simple replay artifact top level must be an object")
        payload = crosswalk_payload(
            aggregate,
            simple_replay,
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
        assert_expected_replay_crosswalk(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 vertex-circle local-lemma replay crosswalk")
        for line in summary_lines(payload):
            print(line)
        print("OK: local-lemma replay crosswalk checks passed")
    else:
        print("FAILED: local-lemma replay crosswalk", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
