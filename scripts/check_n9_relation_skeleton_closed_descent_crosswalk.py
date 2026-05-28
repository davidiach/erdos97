#!/usr/bin/env python3
"""Generate or check the n=9 relation-skeleton/closed-descent crosswalk."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPT_DIR = ROOT / "scripts"
for path in (SRC, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_n9_vertex_circle_closed_descent_packet import (  # noqa: E402
    assert_expected_closed_descent_packet_counts,
)
from erdos97.path_display import display_path  # noqa: E402
from erdos97.relation_skeleton_catalog import (  # noqa: E402
    assert_expected_relation_skeleton_catalog,
)

SCHEMA = "erdos97.n9_relation_skeleton_closed_descent_crosswalk.v1"
STATUS = "REVIEW_PENDING_PACKET_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Cross-artifact audit joining the 16 relation-skeleton entries to the "
    "closed-descent reformulation of the stored n=9 vertex-circle local-core "
    "quotient obstructions. This is not a proof of n=9, not a counterexample, "
    "not local-lemma completeness, not a bridge proof, and not a global "
    "status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_relation_skeleton_closed_descent_crosswalk.py",
    "command": (
        "python scripts/check_n9_relation_skeleton_closed_descent_crosswalk.py "
        "--assert-expected --write"
    ),
}

DEFAULT_RELATION_SKELETONS = (
    ROOT / "data" / "certificates" / "relation_skeleton_catalog.json"
)
DEFAULT_CLOSED_DESCENT = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_closed_descent_packet.json"
)
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "n9_relation_skeleton_closed_descent_crosswalk.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "contradiction_type_counts",
    "cyclic_order",
    "family_count",
    "family_crosswalk",
    "interpretation",
    "n",
    "orbit_size_sum",
    "provenance",
    "region_class_count_counts",
    "schema",
    "source_artifacts",
    "status",
    "trust",
    "validation_errors",
    "validation_status",
}
EXPECTED_CONTRADICTION_TYPE_COUNTS = {
    "strict_directed_cycle": 3,
    "strict_self_edge": 13,
}
EXPECTED_REGION_CLASS_COUNT_COUNTS = {"1": 13, "2": 1, "3": 2}
EXPECTED_FAMILY_IDS = [f"F{index:02d}" for index in range(1, 17)]
EXPECTED_FAMILY_REGION_CLASS_COUNTS = {
    "F01": 1,
    "F02": 1,
    "F03": 1,
    "F04": 1,
    "F05": 1,
    "F06": 1,
    "F07": 3,
    "F08": 1,
    "F09": 1,
    "F10": 1,
    "F11": 1,
    "F12": 2,
    "F13": 1,
    "F14": 1,
    "F15": 1,
    "F16": 3,
}
CONTRADICTION_STATUS_MAP = {
    "strict_self_edge": "self_edge",
    "strict_directed_cycle": "strict_cycle",
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


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def relation_closed_descent_crosswalk_payload(
    relation_skeletons: Mapping[str, Any],
    closed_descent: Mapping[str, Any],
    *,
    relation_skeletons_path: Path = DEFAULT_RELATION_SKELETONS,
    closed_descent_path: Path = DEFAULT_CLOSED_DESCENT,
) -> dict[str, Any]:
    """Return a crosswalk between skeleton families and descent regions."""

    assert_expected_relation_skeleton_catalog(relation_skeletons)
    assert_expected_closed_descent_packet_counts(dict(closed_descent))

    errors: list[str] = []
    relation_by_family = _relation_family_map(relation_skeletons, errors)
    descent_by_family = _descent_family_map(closed_descent, errors)
    family_crosswalk = _family_crosswalk(relation_by_family, descent_by_family, errors)
    contradiction_counts = Counter(
        item["relation_contradiction_type"] for item in family_crosswalk
    )
    region_counts = Counter(int(item["descent_region_class_count"]) for item in family_crosswalk)

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": _same_value("n", relation_skeletons, closed_descent, errors),
        "cyclic_order": relation_skeletons.get("cyclic_order"),
        "family_count": len(family_crosswalk),
        "orbit_size_sum": sum(
            int(item["assignment_count"]) for item in family_crosswalk
        ),
        "contradiction_type_counts": _json_counter(contradiction_counts),
        "region_class_count_counts": _json_counter(region_counts),
        "family_crosswalk": family_crosswalk,
        "source_artifacts": [
            _source_summary(
                relation_skeletons_path,
                "relation-skeleton catalog",
                relation_skeletons,
            ),
            _source_summary(
                closed_descent_path,
                "closed-descent packet",
                closed_descent,
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": [
            "Every relation skeleton maps to exactly one closed-descent packet family.",
            "Strict self-edge skeletons map to one-class closed-descent regions.",
            "Strict directed-cycle skeletons map to multi-class closed-descent regions.",
            "The crosswalk is packet bookkeeping only and does not certify local-lemma completeness.",
        ],
        "provenance": PROVENANCE,
    }
    assert_expected_relation_closed_descent_crosswalk(payload)
    return payload


def assert_expected_relation_closed_descent_crosswalk(
    payload: Mapping[str, Any],
) -> None:
    """Assert the expected relation-skeleton/closed-descent crosswalk."""

    if set(payload) != EXPECTED_TOP_LEVEL_KEYS:
        raise AssertionError(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(payload)!r}"
        )
    expected_meta = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": 9,
        "family_count": 16,
        "orbit_size_sum": 184,
        "contradiction_type_counts": EXPECTED_CONTRADICTION_TYPE_COUNTS,
        "region_class_count_counts": EXPECTED_REGION_CLASS_COUNT_COUNTS,
        "validation_status": "passed",
        "validation_errors": [],
        "provenance": PROVENANCE,
    }
    for key, expected in expected_meta.items():
        if payload.get(key) != expected:
            raise AssertionError(
                f"{key} mismatch: expected {expected!r}, got {payload.get(key)!r}"
            )
    claim_scope = payload.get("claim_scope")
    for phrase in (
        "not a proof of n=9",
        "not a counterexample",
        "not local-lemma completeness",
        "not a bridge proof",
        "not a global status update",
    ):
        if phrase not in claim_scope:
            raise AssertionError(f"claim_scope must contain {phrase!r}")

    records = payload.get("family_crosswalk")
    if not isinstance(records, list):
        raise AssertionError("family_crosswalk must be a list")
    family_ids = [
        str(record.get("family_id"))
        for record in records
        if isinstance(record, Mapping)
    ]
    if family_ids != EXPECTED_FAMILY_IDS:
        raise AssertionError(f"family ids mismatch: {family_ids!r}")
    for record in records:
        if not isinstance(record, Mapping):
            raise AssertionError("family_crosswalk entries must be objects")
        relation_type = str(record.get("relation_contradiction_type"))
        descent_status = str(record.get("descent_source_status"))
        expected_status = CONTRADICTION_STATUS_MAP.get(relation_type)
        if descent_status != expected_status:
            raise AssertionError(
                f"{record.get('family_id')} status mismatch: "
                f"{relation_type!r} maps to {descent_status!r}"
            )
        region_class_count = int(record.get("descent_region_class_count", 0))
        cycle_length = int(record.get("descent_cycle_length", 0))
        if relation_type == "strict_self_edge" and (
            region_class_count != 1 or cycle_length != 1
        ):
            raise AssertionError(
                f"{record.get('family_id')} self-edge must have a one-class region"
            )
        if relation_type == "strict_directed_cycle" and (
            region_class_count <= 1 or cycle_length <= 1
        ):
            raise AssertionError(
                f"{record.get('family_id')} strict cycle must have a multi-class region"
            )
        family_id = str(record.get("family_id"))
        expected_region_count = EXPECTED_FAMILY_REGION_CLASS_COUNTS.get(family_id)
        if region_class_count != expected_region_count:
            raise AssertionError(
                f"{family_id} region class count mismatch: expected "
                f"{expected_region_count}, got {region_class_count}"
            )
        if region_class_count != cycle_length:
            raise AssertionError(
                f"{family_id} region class count must match cycle length"
            )
        if int(record.get("relation_strict_edge_count", 0)) != cycle_length:
            raise AssertionError(
                f"{record.get('family_id')} strict-edge/cycle-length mismatch"
            )
        if int(record.get("assignment_count", 0)) != int(
            record.get("descent_orbit_size", -1)
        ):
            raise AssertionError(
                f"{record.get('family_id')} assignment/orbit-size mismatch"
            )


def validate_payload(
    payload: Any,
    *,
    relation_skeletons_path: Path = DEFAULT_RELATION_SKELETONS,
    closed_descent_path: Path = DEFAULT_CLOSED_DESCENT,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a checked-in crosswalk artifact."""

    if not isinstance(payload, Mapping):
        return ["artifact top level must be a JSON object"]
    errors: list[str] = []
    try:
        assert_expected_relation_closed_descent_crosswalk(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected crosswalk check failed: {exc}")

    if recompute:
        try:
            expected_payload = relation_closed_descent_crosswalk_payload(
                load_artifact(relation_skeletons_path),
                load_artifact(closed_descent_path),
                relation_skeletons_path=relation_skeletons_path,
                closed_descent_path=closed_descent_path,
            )
        except (AssertionError, OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"recomputed crosswalk failed: {exc}")
        else:
            if payload != expected_payload:
                errors.append("crosswalk artifact does not match regenerated payload")
    return errors


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, Mapping) else {}
    return {
        "ok": not errors,
        "artifact": display_path(path, ROOT),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "family_count": object_payload.get("family_count"),
        "orbit_size_sum": object_payload.get("orbit_size_sum"),
        "contradiction_type_counts": object_payload.get("contradiction_type_counts"),
        "region_class_count_counts": object_payload.get("region_class_count_counts"),
        "validation_status": object_payload.get("validation_status"),
        "validation_errors": list(errors),
    }


def _same_value(
    key: str,
    relation_skeletons: Mapping[str, Any],
    closed_descent: Mapping[str, Any],
    errors: list[str],
) -> Any:
    value = relation_skeletons.get(key)
    if closed_descent.get(key) != value:
        errors.append(
            f"{key} mismatch: relation {value!r} != closed descent {closed_descent.get(key)!r}"
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
        family_map[family_id] = {
            "family_id": family_id,
            "skeleton_id": str(skeleton.get("skeleton_id")),
            "template_id": str(skeleton.get("source_template_id")),
            "relation_contradiction_type": str(skeleton.get("contradiction_type")),
            "assignment_count": int(coverage.get("assignment_count", 0)),
            "relation_source_packet": str(skeleton.get("source_packet")),
            "relation_equality_chain_count": len(
                relation_quotient.get("equality_chains", [])
            ),
            "relation_strict_edge_count": len(relation_quotient.get("strict_edges", [])),
        }
    return family_map


def _descent_family_map(
    closed_descent: Mapping[str, Any],
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    certificates = closed_descent.get("certificates")
    if not isinstance(certificates, list):
        errors.append("closed-descent certificates must be a list")
        return {}

    family_map: dict[str, dict[str, Any]] = {}
    for certificate in certificates:
        if not isinstance(certificate, Mapping):
            errors.append("closed-descent certificates must be objects")
            continue
        family_id = str(certificate.get("family_id"))
        if family_id in family_map:
            errors.append(f"duplicate closed-descent family {family_id}")
            continue
        cycle = certificate.get("closed_descent_cycle")
        if not isinstance(cycle, Mapping):
            errors.append(f"{family_id} closed_descent_cycle must be an object")
            cycle = {}
        family_map[family_id] = {
            "family_id": family_id,
            "descent_source_status": str(certificate.get("source_status")),
            "descent_orbit_size": int(certificate.get("orbit_size", 0)),
            "descent_core_size": int(certificate.get("core_size", 0)),
            "descent_strict_edge_count": int(certificate.get("strict_edge_count", 0)),
            "descent_region_class_count": int(
                certificate.get("region_class_count", 0)
            ),
            "descent_cycle_length": int(cycle.get("cycle_length", 0)),
        }
    return family_map


def _family_crosswalk(
    relation_by_family: Mapping[str, Mapping[str, Any]],
    descent_by_family: Mapping[str, Mapping[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if set(relation_by_family) != set(descent_by_family):
        errors.append(
            "family id set mismatch: "
            f"relation {sorted(relation_by_family)!r} != descent {sorted(descent_by_family)!r}"
        )

    for family_id in sorted(set(relation_by_family) & set(descent_by_family)):
        relation = relation_by_family[family_id]
        descent = descent_by_family[family_id]
        expected_status = CONTRADICTION_STATUS_MAP.get(
            str(relation["relation_contradiction_type"])
        )
        if descent["descent_source_status"] != expected_status:
            errors.append(
                f"{family_id} status mismatch: relation "
                f"{relation['relation_contradiction_type']!r} expects "
                f"{expected_status!r}, descent has {descent['descent_source_status']!r}"
            )
        if relation["assignment_count"] != descent["descent_orbit_size"]:
            errors.append(
                f"{family_id} assignment count mismatch: relation "
                f"{relation['assignment_count']} != descent "
                f"{descent['descent_orbit_size']}"
            )
        records.append({**relation, **descent})
    return records


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--relation-skeletons", type=Path, default=DEFAULT_RELATION_SKELETONS)
    parser.add_argument("--closed-descent", type=Path, default=DEFAULT_CLOSED_DESCENT)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write generated crosswalk")
    parser.add_argument("--check", action="store_true", help="validate an existing crosswalk")
    parser.add_argument("--json", action="store_true", help="print stable JSON summary")
    parser.add_argument("--assert-expected", action="store_true")
    return parser.parse_args(argv)


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = _resolve(args.artifact)
    relation_skeletons_path = _resolve(args.relation_skeletons)
    closed_descent_path = _resolve(args.closed_descent)
    out = _resolve(args.out)

    if args.write:
        payload = relation_closed_descent_crosswalk_payload(
            load_artifact(relation_skeletons_path),
            load_artifact(closed_descent_path),
            relation_skeletons_path=relation_skeletons_path,
            closed_descent_path=closed_descent_path,
        )
        if args.assert_expected:
            assert_expected_relation_closed_descent_crosswalk(payload)
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
            relation_skeletons_path=relation_skeletons_path,
            closed_descent_path=closed_descent_path,
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
        print("n=9 relation-skeleton/closed-descent crosswalk")
        print(f"artifact: {summary['artifact']}")
        print(f"families: {summary['family_count']}")
        print(f"orbit-size sum: {summary['orbit_size_sum']}")
        print(f"contradiction counts: {summary['contradiction_type_counts']}")
        print(f"region class counts: {summary['region_class_count_counts']}")
        if args.check or args.assert_expected:
            print("OK: relation-skeleton/closed-descent crosswalk checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
