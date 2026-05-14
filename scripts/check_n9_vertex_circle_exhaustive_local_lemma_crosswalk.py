#!/usr/bin/env python3
"""Cross-check n=9 exhaustive counts against local-lemma replay coverage."""

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
from erdos97.n9_vertex_circle_exhaustive import assert_expected_counts  # noqa: E402
from erdos97.n9_vertex_circle_frontier_motif_classification import (  # noqa: E402
    assert_expected_classification_counts,
)
from erdos97.path_display import display_path  # noqa: E402

SCHEMA = "erdos97.n9_vertex_circle_exhaustive_local_lemma_crosswalk.v1"
STATUS = "REVIEW_PENDING_PACKET_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Cross-artifact audit joining the review-pending n=9 exhaustive count "
    "artifact, frontier motif classification, aggregate local-lemma scan, and "
    "simple replay audit. This is not a proof of n=9, not a counterexample, "
    "not an independent review of the exhaustive checker, and not a global "
    "status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py",
    "command": (
        "python scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py "
        "--check --assert-expected --json"
    ),
}

DEFAULT_EXHAUSTIVE = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_exhaustive.json"
)
DEFAULT_CLASSIFICATION = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)
DEFAULT_LOCAL_LEMMAS = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_local_lemmas.json"
)
DEFAULT_SIMPLE_REPLAY = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_local_lemma_simple_replay.json"
)
EXPECTED_FAMILY_IDS = [f"F{index:02d}" for index in range(1, 17)]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def exhaustive_local_lemma_crosswalk_payload(
    exhaustive: Mapping[str, Any],
    classification: Mapping[str, Any],
    local_lemmas: Mapping[str, Any],
    simple_replay: Mapping[str, Any],
    *,
    exhaustive_path: Path = DEFAULT_EXHAUSTIVE,
    classification_path: Path = DEFAULT_CLASSIFICATION,
    local_lemmas_path: Path = DEFAULT_LOCAL_LEMMAS,
    simple_replay_path: Path = DEFAULT_SIMPLE_REPLAY,
) -> dict[str, Any]:
    """Return a cross-artifact accounting audit for the n=9 local lemmas."""

    errors: list[str] = []
    _append_expected_errors(errors, exhaustive, classification)
    local_crosswalk = local_replay_crosswalk_payload(
        local_lemmas,
        simple_replay,
        aggregate_path=local_lemmas_path,
        simple_replay_path=simple_replay_path,
    )
    try:
        assert_expected_replay_crosswalk(local_crosswalk)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"local replay crosswalk failed: {exc}")

    family_crosswalk = _family_crosswalk(classification, local_crosswalk, errors)
    coverage = _coverage_summary(exhaustive, classification, local_crosswalk, errors)

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": _common_value("n", exhaustive, classification, errors),
        "cyclic_order": _common_value("cyclic_order", exhaustive, classification, errors),
        "source_artifacts": [
            _source_summary(
                exhaustive_path,
                "review-pending exhaustive n=9 count artifact",
                exhaustive,
                schema_key="type",
            ),
            _source_summary(
                classification_path,
                "frontier assignment motif classification",
                classification,
            ),
            _source_summary(
                local_lemmas_path,
                "aggregate local-lemma scan",
                local_lemmas,
            ),
            _source_summary(
                simple_replay_path,
                "simple local-lemma replay audit",
                simple_replay,
            ),
        ],
        "coverage_summary": coverage,
        "family_crosswalk": family_crosswalk,
        "local_replay_crosswalk_summary": local_crosswalk["coverage_summary"],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed crosswalk says the stored exhaustive n=9 count artifact, "
            "the 184-assignment motif classification, and the local-template "
            "replay packets agree on the same review-pending accounting. It "
            "does not review the exhaustive brancher or prove n=9."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_exhaustive_local_lemma_crosswalk(payload: Mapping[str, Any]) -> None:
    """Assert the expected exhaustive-to-local-lemma crosswalk counts."""

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
    expected = {
        "exhaustive_frontier_assignment_count": 184,
        "classification_assignment_count": 184,
        "local_matched_assignment_count": 184,
        "family_count": 16,
        "self_edge_assignment_count": 158,
        "strict_cycle_assignment_count": 26,
    }
    for key, value in expected.items():
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
    exhaustive: Mapping[str, Any],
    classification: Mapping[str, Any],
) -> None:
    try:
        assert_expected_counts(dict(exhaustive))
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"exhaustive expected-check failed: {exc}")
    try:
        assert_expected_classification_counts(dict(classification))
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"classification expected-check failed: {exc}")


def _common_value(
    key: str,
    exhaustive: Mapping[str, Any],
    classification: Mapping[str, Any],
    errors: list[str],
) -> Any:
    value = exhaustive.get(key)
    if classification.get(key) != value:
        errors.append(
            f"{key} mismatch: exhaustive {value!r} != classification {classification.get(key)!r}"
        )
    return value


def _source_summary(
    path: Path,
    role: str,
    payload: Mapping[str, Any],
    *,
    schema_key: str = "schema",
) -> dict[str, Any]:
    return {
        "path": display_path(path, ROOT),
        "role": role,
        "schema": payload.get(schema_key),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
    }


def _coverage_summary(
    exhaustive: Mapping[str, Any],
    classification: Mapping[str, Any],
    local_crosswalk: Mapping[str, Any],
    errors: list[str],
) -> dict[str, int]:
    cross_check = exhaustive.get("cross_check_without_vertex_circle_pruning")
    if not isinstance(cross_check, Mapping):
        errors.append("exhaustive cross_check_without_vertex_circle_pruning must be an object")
        cross_check = {}
    exhaustive_counts = cross_check.get("counts", {})
    if not isinstance(exhaustive_counts, Mapping):
        errors.append("exhaustive cross-check counts must be an object")
        exhaustive_counts = {}
    classification_counts = classification.get("status_counts", {})
    if not isinstance(classification_counts, Mapping):
        errors.append("classification status_counts must be an object")
        classification_counts = {}
    local_counts = local_crosswalk.get("coverage_summary", {})
    if not isinstance(local_counts, Mapping):
        errors.append("local replay coverage_summary must be an object")
        local_counts = {}

    checks = {
        "self_edge": (
            int(exhaustive_counts.get("self_edge", -1)),
            int(classification_counts.get("self_edge", -1)),
            int(local_counts.get("self_edge_assignment_count", -1)),
        ),
        "strict_cycle": (
            int(exhaustive_counts.get("strict_cycle", -1)),
            int(classification_counts.get("strict_cycle", -1)),
            int(local_counts.get("strict_cycle_assignment_count", -1)),
        ),
    }
    for key, values in checks.items():
        if len(set(values)) != 1:
            errors.append(
                f"{key} assignment-count mismatch across artifacts: {values!r}"
            )

    exhaustive_total = int(cross_check.get("full_assignments", -1))
    classification_total = int(classification.get("assignment_count", -1))
    local_total = int(local_counts.get("matched_assignment_count", -1))
    if len({exhaustive_total, classification_total, local_total}) != 1:
        errors.append(
            "frontier assignment-count mismatch across artifacts: "
            f"{(exhaustive_total, classification_total, local_total)!r}"
        )

    family_count = int(classification.get("family_count", -1))
    local_family_count = int(local_counts.get("matched_family_count", -1))
    if family_count != local_family_count:
        errors.append(
            f"family-count mismatch: classification {family_count} != local {local_family_count}"
        )

    return {
        "exhaustive_frontier_assignment_count": exhaustive_total,
        "classification_assignment_count": classification_total,
        "local_matched_assignment_count": local_total,
        "family_count": family_count,
        "self_edge_assignment_count": checks["self_edge"][0],
        "strict_cycle_assignment_count": checks["strict_cycle"][0],
    }


def _family_crosswalk(
    classification: Mapping[str, Any],
    local_crosswalk: Mapping[str, Any],
    errors: list[str],
) -> list[dict[str, Any]]:
    local_by_family = {
        str(item["family_id"]): item
        for item in local_crosswalk.get("family_crosswalk", [])
        if isinstance(item, Mapping) and "family_id" in item
    }
    records = []
    families = classification.get("families")
    if not isinstance(families, list):
        errors.append("classification families must be a list")
        return records
    for family in families:
        if not isinstance(family, Mapping):
            errors.append("classification family entries must be objects")
            continue
        family_id = str(family.get("family_id"))
        local = local_by_family.get(family_id)
        if local is None:
            errors.append(f"{family_id} missing from local replay crosswalk")
            continue
        record = {
            "family_id": family_id,
            "status": str(family.get("status")),
            "template_id": str(family.get("template_id")),
            "assignment_count": int(family.get("assignment_count", -1)),
            "orbit_size": int(family.get("orbit_size", -1)),
            "local_lemma_id": str(local.get("lemma_id")),
            "local_obstruction_group": str(local.get("obstruction_group")),
            "local_aggregate_instance_count": int(
                local.get("aggregate_instance_count", -1)
            ),
        }
        expected_group = "self_edge" if record["status"] == "self_edge" else "strict_cycle"
        for key, local_key in (
            ("template_id", "template_id"),
            ("assignment_count", "assignment_count"),
            ("orbit_size", "orbit_size"),
        ):
            if record[key] != local.get(local_key):
                errors.append(
                    f"{family_id} {key} mismatch: "
                    f"classification {record[key]!r} != local {local.get(local_key)!r}"
                )
        if expected_group != local.get("obstruction_group"):
            errors.append(
                f"{family_id} status/group mismatch: "
                f"classification {record['status']!r} != local {local.get('obstruction_group')!r}"
            )
        records.append(record)

    record_ids = sorted(record["family_id"] for record in records)
    if record_ids != EXPECTED_FAMILY_IDS:
        errors.append(f"family ids mismatch: {record_ids!r}")
    return records


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    coverage = payload["coverage_summary"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        (
            "frontier assignments: "
            f"{coverage['exhaustive_frontier_assignment_count']}"
        ),
        f"families: {coverage['family_count']}",
        f"self-edge assignments: {coverage['self_edge_assignment_count']}",
        f"strict-cycle assignments: {coverage['strict_cycle_assignment_count']}",
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exhaustive", type=Path, default=DEFAULT_EXHAUSTIVE)
    parser.add_argument("--classification", type=Path, default=DEFAULT_CLASSIFICATION)
    parser.add_argument("--local-lemmas", type=Path, default=DEFAULT_LOCAL_LEMMAS)
    parser.add_argument("--simple-replay", type=Path, default=DEFAULT_SIMPLE_REPLAY)
    parser.add_argument("--check", action="store_true", help="validate the crosswalk")
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="Assert the expected exhaustive/local-lemma crosswalk counts.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON payload.")
    args = parser.parse_args(argv)

    exhaustive_path = _resolve(args.exhaustive)
    classification_path = _resolve(args.classification)
    local_lemmas_path = _resolve(args.local_lemmas)
    simple_replay_path = _resolve(args.simple_replay)
    try:
        exhaustive = load_artifact(exhaustive_path)
        classification = load_artifact(classification_path)
        local_lemmas = load_artifact(local_lemmas_path)
        simple_replay = load_artifact(simple_replay_path)
        for name, payload in (
            ("exhaustive", exhaustive),
            ("classification", classification),
            ("local lemmas", local_lemmas),
            ("simple replay", simple_replay),
        ):
            if not isinstance(payload, Mapping):
                raise TypeError(f"{name} artifact top level must be an object")
        payload = exhaustive_local_lemma_crosswalk_payload(
            exhaustive,
            classification,
            local_lemmas,
            simple_replay,
            exhaustive_path=exhaustive_path,
            classification_path=classification_path,
            local_lemmas_path=local_lemmas_path,
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
        assert_expected_exhaustive_local_lemma_crosswalk(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 exhaustive/local-lemma crosswalk")
        for line in summary_lines(payload):
            print(line)
        print("OK: exhaustive/local-lemma crosswalk checks passed")
    else:
        print("FAILED: exhaustive/local-lemma crosswalk", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
