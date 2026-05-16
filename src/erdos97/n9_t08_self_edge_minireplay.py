"""Minimal replay for the n=9 T08/F02 self-edge local lemma packet.

This module treats the focused T08 packet as input data and checks only the
small local proof skeleton for its F02 family packet: selected-distance
equality steps plus one strict vertex-circle chord containment. It is
proof-mining scaffolding only.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from erdos97.n9_t02_self_edge_minireplay import (
    _replay_equality_chain,
    _replay_strict_inequality,
    _rows,
)

SCHEMA = "erdos97.n9_t08_self_edge_minireplay.v1"
STATUS = "REVIEW_PENDING_T08_SELF_EDGE_MINIREPLAY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SOURCE_PACKET_SCHEMA = "erdos97.n9_vertex_circle_t08_self_edge_lemma_packet.v1"
SOURCE_PACKET = "data/certificates/n9_vertex_circle_t08_self_edge_lemma_packet.json"

EXPECTED_FAMILY_IDS = ["F02"]
EXPECTED_ASSIGNMENT_COUNT = 18
EXPECTED_ASSIGNMENT_COUNTS = {"F02": 18}
EXPECTED_STRICT_ROWS = {"F02": 0}
EXPECTED_OUTER_PAIRS = {"F02": [1, 3]}
EXPECTED_INNER_PAIRS = {"F02": [1, 2]}


def replay_family(packet: dict[str, Any]) -> tuple[dict[str, object], list[str]]:
    """Replay the T08/F02 family packet and return a compact summary plus errors."""
    errors: list[str] = []
    family_id = str(packet.get("family_id"))
    if family_id not in EXPECTED_FAMILY_IDS:
        errors.append(f"unexpected family_id: {family_id!r}")
    rows = _rows(packet, family_id, errors)
    equality_chain, equality_steps = _replay_equality_chain(packet, rows, family_id, errors)
    strict_summary = _replay_strict_inequality(packet, rows, equality_chain, family_id, errors)
    summary = {
        "family_id": family_id,
        "assignment_count": packet.get("assignment_count"),
        "core_row_count": len(rows),
        "core_centers": sorted(rows),
        "equality_chain": equality_chain,
        "equality_step_count": len(equality_steps),
        "equality_steps": equality_steps,
        "strict_inequality": strict_summary,
        "self_edge_contradiction": bool(
            equality_chain
            and strict_summary
            and equality_chain[0] == strict_summary.get("outer_pair")
            and equality_chain[-1] == strict_summary.get("inner_pair")
        ),
    }
    if summary["assignment_count"] != EXPECTED_ASSIGNMENT_COUNTS.get(family_id):
        errors.append(
            f"{family_id}: unexpected assignment_count "
            f"{summary['assignment_count']!r}"
        )
    if not summary["self_edge_contradiction"]:
        errors.append(f"{family_id}: strict inequality does not close on an equality-chain self-edge")
    return summary, errors


def replay_packet(packet: dict[str, Any]) -> tuple[dict[str, object], list[str]]:
    """Replay the T08 packet and return a compact summary plus errors."""
    errors: list[str] = []
    if packet.get("schema") != SOURCE_PACKET_SCHEMA:
        errors.append(f"unexpected source schema: {packet.get('schema')!r}")
    if packet.get("template_id") != "T08":
        errors.append(f"unexpected template_id: {packet.get('template_id')!r}")
    if packet.get("cyclic_order") != list(range(9)):
        errors.append("cyclic_order must be the natural nonagon order")
    if packet.get("family_ids") != EXPECTED_FAMILY_IDS:
        errors.append(f"family_ids mismatch: {packet.get('family_ids')!r}")
    family_packets = packet.get("family_packets")
    if not isinstance(family_packets, list):
        errors.append("family_packets must be a list")
        family_packets = []

    families: list[dict[str, object]] = []
    for raw_family in family_packets:
        if not isinstance(raw_family, dict):
            errors.append("family_packets entries must be objects")
            continue
        family_summary, family_errors = replay_family(raw_family)
        families.append(family_summary)
        errors.extend(family_errors)

    family_ids = [str(item.get("family_id")) for item in families]
    if family_ids != EXPECTED_FAMILY_IDS:
        errors.append(f"replayed family order mismatch: {family_ids!r}")
    assignment_counts = {
        str(item["family_id"]): int(item["assignment_count"])
        for item in families
        if isinstance(item.get("assignment_count"), int)
    }
    if sum(assignment_counts.values()) != EXPECTED_ASSIGNMENT_COUNT:
        errors.append("family assignment counts do not sum to expected T08 count")
    path_lengths = Counter(str(item.get("equality_step_count")) for item in families)
    strict_rows = {
        str(item["family_id"]): item.get("strict_inequality", {}).get("row")
        for item in families
        if isinstance(item.get("strict_inequality"), dict)
    }
    summary = {
        "source_template_id": packet.get("template_id"),
        "family_count": len(families),
        "family_ids": family_ids,
        "assignment_count": sum(assignment_counts.values()),
        "assignment_counts": assignment_counts,
        "path_length_counts": dict(sorted(path_lengths.items())),
        "strict_rows": strict_rows,
        "family_replays": families,
        "all_self_edge_contradictions": all(
            bool(item.get("self_edge_contradiction")) for item in families
        ),
    }
    if not summary["all_self_edge_contradictions"]:
        errors.append("not every T08 family replay closed a self-edge contradiction")
    return summary, errors


def minireplay_payload(packet: dict[str, Any]) -> dict[str, object]:
    """Build the stable mini-replay artifact payload."""
    replay, errors = replay_packet(packet)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Minimal input-data replay of the focused T08/F02 self-edge "
            "local lemma packet; not a proof of n=9, not an independent review "
            "of the full checker, not a counterexample, and not a global status "
            "update."
        ),
        "source_packet": SOURCE_PACKET,
        "source_packet_schema": SOURCE_PACKET_SCHEMA,
        "ok": not errors,
        "validation_errors": errors,
        "replay": replay,
        "interpretation": (
            "The T08/F02 family packet identifies the strict outer and inner "
            "chord pairs by selected-distance equality steps, while its listed "
            "vertex-circle row makes the outer chord strictly longer than the "
            "inner chord."
        ),
        "provenance": {
            "generator": "scripts/check_n9_t08_self_edge_minireplay.py",
            "command": "python scripts/check_n9_t08_self_edge_minireplay.py --write --assert-expected",
        },
    }


def validate_payload(payload: dict[str, Any], source_packet: dict[str, Any]) -> list[str]:
    """Validate a stored mini-replay payload against the source packet."""
    errors: list[str] = []
    expected = minireplay_payload(source_packet)
    for key in ("schema", "status", "trust", "source_packet", "source_packet_schema", "ok"):
        if payload.get(key) != expected.get(key):
            errors.append(f"{key} mismatch: {payload.get(key)!r} != {expected.get(key)!r}")
    if payload.get("validation_errors") != expected["validation_errors"]:
        errors.append("validation_errors mismatch")
    if payload.get("replay") != expected["replay"]:
        errors.append("replay mismatch")
    return errors


def assert_expected_payload(payload: dict[str, Any]) -> None:
    """Assert the stable expected T08/F02 mini-replay facts."""
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected schema")
    if payload.get("ok") is not True:
        raise AssertionError(f"mini-replay is not ok: {payload.get('validation_errors')!r}")
    replay = payload.get("replay")
    if not isinstance(replay, dict):
        raise AssertionError("missing replay object")
    expected = {
        "source_template_id": "T08",
        "family_count": 1,
        "family_ids": EXPECTED_FAMILY_IDS,
        "assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "assignment_counts": EXPECTED_ASSIGNMENT_COUNTS,
        "path_length_counts": {"5": 1},
        "strict_rows": EXPECTED_STRICT_ROWS,
        "all_self_edge_contradictions": True,
    }
    for key, expected_value in expected.items():
        if replay.get(key) != expected_value:
            raise AssertionError(
                f"unexpected replay {key}: {replay.get(key)!r} != {expected_value!r}"
            )
    family_replays = replay.get("family_replays")
    if not isinstance(family_replays, list) or len(family_replays) != 1:
        raise AssertionError("unexpected family_replays")
    family = family_replays[0]
    if not isinstance(family, dict):
        raise AssertionError("family replay is not an object")
    family_id = str(family.get("family_id"))
    strict = family.get("strict_inequality")
    if not isinstance(strict, dict):
        raise AssertionError(f"{family_id}: missing strict_inequality")
    if strict.get("outer_pair") != EXPECTED_OUTER_PAIRS[family_id]:
        raise AssertionError(f"{family_id}: unexpected outer_pair")
    if strict.get("inner_pair") != EXPECTED_INNER_PAIRS[family_id]:
        raise AssertionError(f"{family_id}: unexpected inner_pair")
