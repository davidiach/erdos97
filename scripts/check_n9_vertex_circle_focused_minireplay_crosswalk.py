#!/usr/bin/env python3
"""Cross-check focused n=9 local-lemma packets against mini-replay artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.path_display import display_path  # noqa: E402

EXPECTED_TEMPLATE_IDS = [f"T{index:02d}" for index in range(1, 13)]
SELF_EDGE_TEMPLATE_IDS = [f"T{index:02d}" for index in range(1, 10)]
STRICT_CYCLE_TEMPLATE_IDS = [f"T{index:02d}" for index in range(10, 13)]

DEFAULT_PACKET_PATHS = {
    **{
        template_id: (
            ROOT
            / "data"
            / "certificates"
            / f"n9_vertex_circle_t{index:02d}_self_edge_lemma_packet.json"
        )
        for index, template_id in enumerate(SELF_EDGE_TEMPLATE_IDS, start=1)
    },
    **{
        template_id: (
            ROOT
            / "data"
            / "certificates"
            / f"n9_vertex_circle_t{index:02d}_strict_cycle_lemma_packet.json"
        )
        for index, template_id in enumerate(STRICT_CYCLE_TEMPLATE_IDS, start=10)
    },
}
DEFAULT_MINIREPLAY_PATHS = {
    **{
        template_id: (
            ROOT / "data" / "certificates" / f"n9_t{index:02d}_self_edge_minireplay.json"
        )
        for index, template_id in enumerate(SELF_EDGE_TEMPLATE_IDS, start=1)
    },
    **{
        template_id: (
            ROOT
            / "data"
            / "certificates"
            / f"n9_t{index:02d}_strict_cycle_minireplay.json"
        )
        for index, template_id in enumerate(STRICT_CYCLE_TEMPLATE_IDS, start=10)
    },
}

SCHEMA = "erdos97.n9_vertex_circle_focused_minireplay_crosswalk.v1"
STATUS = "REVIEW_PENDING_FOCUSED_MINIREPLAY_CROSSWALK"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "JSON-only cross-artifact audit joining the 12 focused n=9 local-lemma "
    "packets to their packet-specific mini-replay artifacts. It checks "
    "identity, source schema, family coverage, obstruction flags, and local "
    "shape counts only. It does not prove mini-replay soundness, packet "
    "soundness, local-lemma completeness, frontier coverage, n=9, a "
    "counterexample, or any official/global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py",
    "command": (
        "python scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py "
        "--check --assert-expected --json"
    ),
}

EXPECTED_STATUS_COUNTS = {"self_edge": 9, "strict_cycle": 3}
EXPECTED_STATUS_ASSIGNMENT_COUNTS = {"self_edge": 158, "strict_cycle": 26}
EXPECTED_FAMILY_COUNT = 16
EXPECTED_ASSIGNMENT_COUNT = 184
EXPECTED_REPEATED_ASSIGNMENT_COUNT = 184
EXPECTED_SOURCE_ONLY_ASSIGNMENT_COUNT = 0
EXPECTED_SOURCE_ONLY_TEMPLATES: list[str] = []
EXPECTED_SELF_EDGE_PATH_LENGTH_COUNTS = {"3": 9, "4": 2, "5": 1, "6": 1}
EXPECTED_STRICT_CYCLE_LENGTH_COUNTS = {"2": 1, "3": 2}


def load_json(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def focused_minireplay_crosswalk_payload(
    *,
    packet_paths: Mapping[str, Path] | None = None,
    minireplay_paths: Mapping[str, Path] | None = None,
) -> dict[str, Any]:
    """Return a JSON-only packet/minireplay crosswalk payload."""

    resolved_packets = {
        template_id: _resolve(path)
        for template_id, path in (packet_paths or DEFAULT_PACKET_PATHS).items()
    }
    resolved_minireplays = {
        template_id: _resolve(path)
        for template_id, path in (minireplay_paths or DEFAULT_MINIREPLAY_PATHS).items()
    }
    packet_payloads = {
        template_id: load_json(path) for template_id, path in resolved_packets.items()
    }
    minireplay_payloads = {
        template_id: load_json(path) for template_id, path in resolved_minireplays.items()
    }
    errors: list[str] = []
    summary = _audit(
        packet_payloads,
        minireplay_payloads,
        resolved_packets,
        resolved_minireplays,
        errors,
    )
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": 9,
        "row_size": 4,
        "focused_minireplay_crosswalk": summary,
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed crosswalk says the stored focused packets and the "
            "small packet-specific mini-replays agree on identity, families, "
            "source schemas, obstruction flags, and compact local shapes. "
            "This is bookkeeping only."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_focused_minireplay_crosswalk(payload: Mapping[str, Any]) -> None:
    """Assert stable counts for the focused packet/minireplay crosswalk."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    if payload.get("provenance") != PROVENANCE:
        raise AssertionError(f"provenance mismatch: {payload.get('provenance')!r}")
    claim_scope = str(payload.get("claim_scope", ""))
    for required in (
        "does not prove mini-replay soundness",
        "packet soundness",
        "local-lemma completeness",
        "frontier coverage",
        "n=9",
        "counterexample",
        "official/global status update",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")

    summary = payload.get("focused_minireplay_crosswalk")
    if not isinstance(summary, Mapping):
        raise AssertionError("focused_minireplay_crosswalk missing")
    expected = {
        "packet_count": 12,
        "minireplay_count": 12,
        "template_ids": EXPECTED_TEMPLATE_IDS,
        "status_counts": EXPECTED_STATUS_COUNTS,
        "status_assignment_counts": EXPECTED_STATUS_ASSIGNMENT_COUNTS,
        "source_assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "source_family_count": EXPECTED_FAMILY_COUNT,
        "obstruction_flagged_count": 12,
        "assignment_count_repeated_template_count": 12,
        "assignment_count_source_only_template_count": 0,
        "assignment_count_repeated_total": EXPECTED_REPEATED_ASSIGNMENT_COUNT,
        "assignment_count_source_only_total": EXPECTED_SOURCE_ONLY_ASSIGNMENT_COUNT,
        "assignment_count_source_only_templates": EXPECTED_SOURCE_ONLY_TEMPLATES,
        "source_packet_mismatch_count": 0,
        "source_schema_mismatch_count": 0,
        "family_mismatch_count": 0,
        "assignment_count_mismatch_count": 0,
        "obstruction_flag_mismatch_count": 0,
        "self_edge_path_length_family_counts": EXPECTED_SELF_EDGE_PATH_LENGTH_COUNTS,
        "strict_cycle_length_family_counts": EXPECTED_STRICT_CYCLE_LENGTH_COUNTS,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise AssertionError(f"{key} mismatch: {summary.get(key)!r} != {value!r}")


def _audit(
    packets: Mapping[str, Any],
    minireplays: Mapping[str, Any],
    packet_paths: Mapping[str, Path],
    minireplay_paths: Mapping[str, Path],
    errors: list[str],
) -> dict[str, Any]:
    missing_packets = sorted(set(EXPECTED_TEMPLATE_IDS) - set(packets))
    missing_minireplays = sorted(set(EXPECTED_TEMPLATE_IDS) - set(minireplays))
    extra_packets = sorted(set(packets) - set(EXPECTED_TEMPLATE_IDS))
    extra_minireplays = sorted(set(minireplays) - set(EXPECTED_TEMPLATE_IDS))
    for label, values in (
        ("missing focused packets", missing_packets),
        ("missing mini-replays", missing_minireplays),
        ("extra focused packets", extra_packets),
        ("extra mini-replays", extra_minireplays),
    ):
        if values:
            errors.append(f"{label}: {values!r}")

    records: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    status_assignment_counts: Counter[str] = Counter()
    self_edge_path_lengths: Counter[str] = Counter()
    strict_cycle_lengths: Counter[str] = Counter()
    source_packet_mismatch_count = 0
    source_schema_mismatch_count = 0
    family_mismatch_count = 0
    assignment_count_mismatch_count = 0
    obstruction_flag_mismatch_count = 0
    assignment_count_repeated_total = 0
    assignment_count_source_only_total = 0
    assignment_count_source_only_templates: list[str] = []
    family_ids: list[str] = []

    for template_id in EXPECTED_TEMPLATE_IDS:
        packet = packets.get(template_id)
        minireplay = minireplays.get(template_id)
        if not isinstance(packet, Mapping):
            errors.append(f"{template_id}: focused packet must be an object")
            continue
        if not isinstance(minireplay, Mapping):
            errors.append(f"{template_id}: mini-replay must be an object")
            continue
        source = _source_record(template_id, packet, packet_paths.get(template_id), errors)
        record = _minireplay_record(
            template_id,
            source,
            minireplay,
            minireplay_paths.get(template_id),
            errors,
        )
        records.append(record)
        status_counts[source["status"]] += 1
        status_assignment_counts[source["status"]] += source["assignment_count"]
        family_ids.extend(source["family_ids"])

        if record["source_packet_matches"] is not True:
            source_packet_mismatch_count += 1
        if record["source_schema_matches"] is not True:
            source_schema_mismatch_count += 1
        if record["family_ids_match"] is not True:
            family_mismatch_count += 1
        if record["assignment_count_matches"] is False:
            assignment_count_mismatch_count += 1
        if record["obstruction_confirmed"] is not True:
            obstruction_flag_mismatch_count += 1

        if record["assignment_count_repeated"]:
            assignment_count_repeated_total += source["assignment_count"]
        else:
            assignment_count_source_only_total += source["assignment_count"]
            assignment_count_source_only_templates.append(template_id)

        if source["status"] == "self_edge":
            self_edge_path_lengths.update(record["shape_counts"])
        elif source["status"] == "strict_cycle":
            strict_cycle_lengths.update(record["shape_counts"])

    return {
        "packet_count": len([item for item in packets.values() if isinstance(item, Mapping)]),
        "minireplay_count": len(
            [item for item in minireplays.values() if isinstance(item, Mapping)]
        ),
        "template_ids": [record["template_id"] for record in records],
        "status_counts": dict(sorted(status_counts.items())),
        "status_assignment_counts": dict(sorted(status_assignment_counts.items())),
        "source_assignment_count": sum(status_assignment_counts.values()),
        "source_family_count": len(set(family_ids)),
        "obstruction_flagged_count": sum(
            1 for record in records if record["obstruction_confirmed"] is True
        ),
        "assignment_count_repeated_template_count": sum(
            1 for record in records if record["assignment_count_repeated"] is True
        ),
        "assignment_count_source_only_template_count": len(
            assignment_count_source_only_templates
        ),
        "assignment_count_repeated_total": assignment_count_repeated_total,
        "assignment_count_source_only_total": assignment_count_source_only_total,
        "assignment_count_source_only_templates": assignment_count_source_only_templates,
        "source_packet_mismatch_count": source_packet_mismatch_count,
        "source_schema_mismatch_count": source_schema_mismatch_count,
        "family_mismatch_count": family_mismatch_count,
        "assignment_count_mismatch_count": assignment_count_mismatch_count,
        "obstruction_flag_mismatch_count": obstruction_flag_mismatch_count,
        "self_edge_path_length_family_counts": dict(sorted(self_edge_path_lengths.items())),
        "strict_cycle_length_family_counts": dict(sorted(strict_cycle_lengths.items())),
        "records": records,
    }


def _source_record(
    template_id: str,
    packet: Mapping[str, Any],
    path: Path | None,
    errors: list[str],
) -> dict[str, Any]:
    if packet.get("template_id") != template_id:
        errors.append(f"{template_id}: focused packet template_id mismatch")
    status = "unknown"
    source_catalog = packet.get("source_catalog_record")
    if isinstance(source_catalog, Mapping):
        status = str(source_catalog.get("status"))
    family_ids = _family_ids(packet)
    assignment_count = int(packet.get("assignment_count", -1))
    family_assignment_counts = _family_assignment_counts(packet, family_ids, assignment_count)
    return {
        "template_id": template_id,
        "path": _relative_posix(path),
        "schema": packet.get("schema"),
        "status": status,
        "family_ids": family_ids,
        "family_assignment_counts": family_assignment_counts,
        "assignment_count": assignment_count,
    }


def _minireplay_record(
    template_id: str,
    source: Mapping[str, Any],
    minireplay: Mapping[str, Any],
    path: Path | None,
    errors: list[str],
) -> dict[str, Any]:
    replay = minireplay.get("replay")
    if not isinstance(replay, Mapping):
        errors.append(f"{template_id}: mini-replay replay must be an object")
        replay = {}
    expected_status_suffix = (
        "SELF_EDGE_MINIREPLAY" if source["status"] == "self_edge" else "STRICT_CYCLE_MINIREPLAY"
    )
    expected_status = f"REVIEW_PENDING_{template_id}_{expected_status_suffix}"
    if minireplay.get("status") != expected_status:
        errors.append(f"{template_id}: mini-replay status mismatch")
    if minireplay.get("trust") != TRUST:
        errors.append(f"{template_id}: mini-replay trust mismatch")
    if minireplay.get("ok") is not True:
        errors.append(f"{template_id}: mini-replay ok flag is not true")
    if minireplay.get("validation_errors") != []:
        errors.append(f"{template_id}: mini-replay validation_errors is not empty")

    source_packet_matches = minireplay.get("source_packet") == source["path"]
    if not source_packet_matches:
        errors.append(f"{template_id}: mini-replay source_packet mismatch")
    source_schema_matches = minireplay.get("source_packet_schema") == source["schema"]
    if not source_schema_matches:
        errors.append(f"{template_id}: mini-replay source schema mismatch")
    if replay.get("source_template_id") != template_id:
        errors.append(f"{template_id}: mini-replay source_template_id mismatch")

    replay_family_ids = _replay_family_ids(replay)
    family_ids_match = replay_family_ids == source["family_ids"]
    if not family_ids_match:
        errors.append(f"{template_id}: mini-replay family ids mismatch")

    assignment_count_matches: bool | None = None
    assignment_count_repeated = isinstance(replay.get("assignment_count"), int)
    if assignment_count_repeated:
        assignment_count_matches = replay.get("assignment_count") == source["assignment_count"]
        if not assignment_count_matches:
            errors.append(f"{template_id}: mini-replay assignment_count mismatch")
    replay_assignment_counts = _int_map(replay.get("assignment_counts"))
    if replay_assignment_counts and replay_assignment_counts != source["family_assignment_counts"]:
        assignment_count_matches = False
        errors.append(f"{template_id}: mini-replay assignment_counts mismatch")

    obstruction_confirmed = _obstruction_confirmed(source["status"], replay)
    if not obstruction_confirmed:
        errors.append(f"{template_id}: mini-replay obstruction flag mismatch")
    shape_counts = _shape_counts(source["status"], replay, template_id, errors)
    return {
        "template_id": template_id,
        "status": source["status"],
        "source_packet_path": source["path"],
        "minireplay_path": _relative_posix(path),
        "family_ids": source["family_ids"],
        "source_assignment_count": source["assignment_count"],
        "assignment_count_repeated": assignment_count_repeated,
        "assignment_count_matches": assignment_count_matches,
        "source_packet_matches": source_packet_matches,
        "source_schema_matches": source_schema_matches,
        "family_ids_match": family_ids_match,
        "obstruction_confirmed": obstruction_confirmed,
        "shape_counts": shape_counts,
    }


def _family_ids(packet: Mapping[str, Any]) -> list[str]:
    family_ids = packet.get("family_ids")
    if isinstance(family_ids, list):
        return [str(item) for item in family_ids]
    family_id = packet.get("family_id")
    return [str(family_id)] if isinstance(family_id, str) else []


def _family_assignment_counts(
    packet: Mapping[str, Any],
    family_ids: Sequence[str],
    assignment_count: int,
) -> dict[str, int]:
    counts = _int_map(packet.get("family_assignment_counts"))
    if counts:
        return counts
    if len(family_ids) == 1:
        return {family_ids[0]: assignment_count}
    return {}


def _replay_family_ids(replay: Mapping[str, Any]) -> list[str]:
    family_ids = replay.get("family_ids")
    if isinstance(family_ids, list):
        return [str(item) for item in family_ids]
    family_id = replay.get("source_family_id")
    return [str(family_id)] if isinstance(family_id, str) else []


def _obstruction_confirmed(status: str, replay: Mapping[str, Any]) -> bool:
    if status == "self_edge":
        if "all_self_edge_contradictions" in replay:
            return replay.get("all_self_edge_contradictions") is True
        return replay.get("self_edge_contradiction") is True
    if status == "strict_cycle":
        return replay.get("strict_cycle_contradiction") is True
    return False


def _shape_counts(
    status: str,
    replay: Mapping[str, Any],
    template_id: str,
    errors: list[str],
) -> dict[str, int]:
    if status == "self_edge":
        path_counts = _int_map(replay.get("path_length_counts"))
        if path_counts:
            return path_counts
        try:
            return {str(int(replay["equality_step_count"])): 1}
        except (KeyError, TypeError, ValueError):
            errors.append(f"{template_id}: missing self-edge equality path length")
            return {}
    if status == "strict_cycle":
        try:
            return {str(int(replay["cycle_length"])): 1}
        except (KeyError, TypeError, ValueError):
            errors.append(f"{template_id}: missing strict-cycle length")
            return {}
    errors.append(f"{template_id}: unknown source status {status!r}")
    return {}


def _int_map(value: Any) -> dict[str, int]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): int(item) for key, item in value.items()}


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _relative_posix(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return display_path(path, ROOT).replace("\\", "/")


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    summary = payload["focused_minireplay_crosswalk"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"mini-replays checked: {summary['minireplay_count']}",
        f"source assignments covered: {summary['source_assignment_count']}",
        f"source families covered: {summary['source_family_count']}",
        f"obstruction flags checked: {summary['obstruction_flagged_count']}",
        f"assignment counts repeated directly: {summary['assignment_count_repeated_total']}",
    ]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the crosswalk")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="emit JSON payload")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = focused_minireplay_crosswalk_payload()
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
        assert_expected_focused_minireplay_crosswalk(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 focused mini-replay crosswalk")
        for line in summary_lines(payload):
            print(line)
        print("OK: focused mini-replay crosswalk checks passed")
    else:
        print("FAILED: n=9 focused mini-replay crosswalk", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
