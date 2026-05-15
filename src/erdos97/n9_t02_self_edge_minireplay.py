"""Minimal replay for the n=9 T02 self-edge local lemma packet.

This module treats the focused T02 packet as input data and checks only the
small local proof skeleton for its four family packets: selected-distance
equality steps plus one strict vertex-circle chord containment. It is
proof-mining scaffolding only.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

SCHEMA = "erdos97.n9_t02_self_edge_minireplay.v1"
STATUS = "REVIEW_PENDING_T02_SELF_EDGE_MINIREPLAY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SOURCE_PACKET_SCHEMA = "erdos97.n9_vertex_circle_t02_self_edge_lemma_packet.v1"
SOURCE_PACKET = "data/certificates/n9_vertex_circle_t02_self_edge_lemma_packet.json"

EXPECTED_FAMILY_IDS = ["F01", "F04", "F08", "F14"]
EXPECTED_ASSIGNMENT_COUNT = 40
EXPECTED_ASSIGNMENT_COUNTS = {"F01": 18, "F04": 18, "F08": 2, "F14": 2}
EXPECTED_STRICT_ROWS = {"F01": 0, "F04": 1, "F08": 0, "F14": 0}
EXPECTED_OUTER_PAIRS = {
    "F01": [1, 8],
    "F04": [0, 2],
    "F08": [1, 8],
    "F14": [1, 8],
}
EXPECTED_INNER_PAIRS = {
    "F01": [1, 2],
    "F04": [2, 3],
    "F08": [1, 2],
    "F14": [1, 2],
}


def _pair(value: Any, label: str, errors: list[str]) -> list[int]:
    if not isinstance(value, list) or len(value) != 2:
        errors.append(f"{label} must be a two-element list")
        return []
    try:
        left, right = sorted(int(item) for item in value)
    except (TypeError, ValueError):
        errors.append(f"{label} must contain integer labels")
        return []
    if left == right:
        errors.append(f"{label} must contain two distinct labels")
    return [left, right]


def _rows(packet: dict[str, Any], family_id: str, errors: list[str]) -> dict[int, list[int]]:
    raw_rows = packet.get("core_selected_rows")
    if not isinstance(raw_rows, list):
        errors.append(f"{family_id}: core_selected_rows must be a list")
        return {}
    rows: dict[int, list[int]] = {}
    for index, raw_row in enumerate(raw_rows):
        if not isinstance(raw_row, list) or len(raw_row) != 5:
            errors.append(
                f"{family_id}: core_selected_rows[{index}] must have center plus four witnesses"
            )
            continue
        try:
            center = int(raw_row[0])
            witnesses = [int(value) for value in raw_row[1:]]
        except (TypeError, ValueError):
            errors.append(f"{family_id}: core_selected_rows[{index}] must contain integer labels")
            continue
        if center in rows:
            errors.append(f"{family_id}: duplicate core row for center {center}")
        if center in witnesses:
            errors.append(f"{family_id}: core row {center} contains its own center")
        if len(set(witnesses)) != 4:
            errors.append(f"{family_id}: core row {center} has duplicate witnesses")
        rows[center] = witnesses
    return rows


def _other_endpoint(pair_value: list[int], center: int) -> int | None:
    if len(pair_value) != 2:
        return None
    if center == pair_value[0]:
        return pair_value[1]
    if center == pair_value[1]:
        return pair_value[0]
    return None


def _replay_equality_chain(
    packet: dict[str, Any],
    rows: dict[int, list[int]],
    family_id: str,
    errors: list[str],
) -> tuple[list[list[int]], list[dict[str, object]]]:
    equality = packet.get("distance_equality")
    if not isinstance(equality, dict):
        errors.append(f"{family_id}: distance_equality must be an object")
        return [], []
    current = _pair(
        equality.get("start_pair"),
        f"{family_id}: distance_equality.start_pair",
        errors,
    )
    end_pair = _pair(
        equality.get("end_pair"),
        f"{family_id}: distance_equality.end_pair",
        errors,
    )
    path = equality.get("path")
    if not isinstance(path, list):
        errors.append(f"{family_id}: distance_equality.path must be a list")
        return [], []

    chain = [current]
    steps: list[dict[str, object]] = []
    for step_index, step in enumerate(path):
        if not isinstance(step, dict):
            errors.append(f"{family_id}: distance_equality.path[{step_index}] must be an object")
            continue
        try:
            row = int(step["row"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"{family_id}: distance_equality.path[{step_index}].row must be an integer")
            continue
        next_pair = _pair(
            step.get("next_pair"),
            f"{family_id}: distance_equality.path[{step_index}].next_pair",
            errors,
        )
        witnesses = rows.get(row)
        if witnesses is None:
            errors.append(f"{family_id}: equality step {step_index} uses missing row {row}")
            continue
        current_other = _other_endpoint(current, row)
        next_other = _other_endpoint(next_pair, row)
        if current_other is None:
            errors.append(f"{family_id}: equality step {step_index} does not start at row center {row}")
        elif current_other not in witnesses:
            errors.append(
                f"{family_id}: equality step {step_index} current endpoint {current_other} "
                f"is not selected by row {row}"
            )
        if next_other is None:
            errors.append(f"{family_id}: equality step {step_index} does not end at row center {row}")
        elif next_other not in witnesses:
            errors.append(
                f"{family_id}: equality step {step_index} next endpoint {next_other} "
                f"is not selected by row {row}"
            )
        steps.append(
            {
                "row": row,
                "left_pair": current,
                "right_pair": next_pair,
            }
        )
        current = next_pair
        chain.append(current)

    if current != end_pair:
        errors.append(f"{family_id}: equality chain ends at {current}, not {end_pair}")
    stored_chain = packet.get("equality_chain")
    if stored_chain != chain:
        errors.append(f"{family_id}: stored equality_chain mismatch: {stored_chain!r} != {chain!r}")
    return chain, steps


def _interval_for_pair(witness_order: list[int], pair_value: list[int]) -> list[int]:
    positions = sorted(witness_order.index(endpoint) for endpoint in pair_value)
    return [int(positions[0]), int(positions[1])]


def _replay_strict_inequality(
    packet: dict[str, Any],
    rows: dict[int, list[int]],
    equality_chain: list[list[int]],
    family_id: str,
    errors: list[str],
) -> dict[str, object]:
    strict = packet.get("strict_inequality")
    if not isinstance(strict, dict):
        errors.append(f"{family_id}: strict_inequality must be an object")
        return {}
    try:
        row = int(strict["row"])
        witness_order = [int(value) for value in strict["witness_order"]]
    except (KeyError, TypeError, ValueError):
        errors.append(f"{family_id}: strict_inequality row and witness_order must be present")
        return {}
    row_witnesses = rows.get(row)
    if row_witnesses is None:
        errors.append(f"{family_id}: strict_inequality uses missing row {row}")
    elif sorted(row_witnesses) != sorted(witness_order):
        errors.append(f"{family_id}: strict_inequality witness_order must list the row witnesses")

    outer_pair = _pair(strict.get("outer_pair"), f"{family_id}: strict_inequality.outer_pair", errors)
    inner_pair = _pair(strict.get("inner_pair"), f"{family_id}: strict_inequality.inner_pair", errors)
    for label, pair_value in (("outer", outer_pair), ("inner", inner_pair)):
        for endpoint in pair_value:
            if endpoint not in witness_order:
                errors.append(
                    f"{family_id}: strict_inequality {label}_pair endpoint {endpoint} is not a witness"
                )
    if errors:
        return {}

    outer_interval = _interval_for_pair(witness_order, outer_pair)
    inner_interval = _interval_for_pair(witness_order, inner_pair)
    if strict.get("outer_interval") != outer_interval:
        errors.append(f"{family_id}: strict_inequality outer_interval mismatch")
    if strict.get("inner_interval") != inner_interval:
        errors.append(f"{family_id}: strict_inequality inner_interval mismatch")
    if not (
        outer_interval[0] <= inner_interval[0]
        and inner_interval[1] <= outer_interval[1]
        and outer_interval != inner_interval
    ):
        errors.append(f"{family_id}: strict outer interval must properly contain inner interval")
    if strict.get("outer_span") != outer_interval[1] - outer_interval[0]:
        errors.append(f"{family_id}: strict_inequality outer_span mismatch")
    if strict.get("inner_span") != inner_interval[1] - inner_interval[0]:
        errors.append(f"{family_id}: strict_inequality inner_span mismatch")
    if equality_chain and (equality_chain[0] != outer_pair or equality_chain[-1] != inner_pair):
        errors.append(f"{family_id}: equality chain endpoints must match strict outer and inner pairs")

    return {
        "row": row,
        "witness_order": witness_order,
        "outer_pair": outer_pair,
        "inner_pair": inner_pair,
        "outer_interval": outer_interval,
        "inner_interval": inner_interval,
        "outer_span": outer_interval[1] - outer_interval[0],
        "inner_span": inner_interval[1] - inner_interval[0],
    }


def replay_family(packet: dict[str, Any]) -> tuple[dict[str, object], list[str]]:
    """Replay one T02 family packet and return a compact summary plus errors."""
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
    """Replay the T02 packet and return a compact summary plus errors."""
    errors: list[str] = []
    if packet.get("schema") != SOURCE_PACKET_SCHEMA:
        errors.append(f"unexpected source schema: {packet.get('schema')!r}")
    if packet.get("template_id") != "T02":
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
        errors.append("family assignment counts do not sum to expected T02 count")
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
        errors.append("not every T02 family replay closed a self-edge contradiction")
    return summary, errors


def minireplay_payload(packet: dict[str, Any]) -> dict[str, object]:
    """Build the stable mini-replay artifact payload."""
    replay, errors = replay_packet(packet)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Minimal input-data replay of the focused T02 multi-family self-edge "
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
            "Each T02 family packet identifies the strict outer and inner chord "
            "pairs by selected-distance equality steps, while its listed "
            "vertex-circle row makes the outer chord strictly longer than the "
            "inner chord."
        ),
        "provenance": {
            "generator": "scripts/check_n9_t02_self_edge_minireplay.py",
            "command": "python scripts/check_n9_t02_self_edge_minireplay.py --write --assert-expected",
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
    """Assert the stable expected T02 mini-replay facts."""
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected schema")
    if payload.get("ok") is not True:
        raise AssertionError(f"mini-replay is not ok: {payload.get('validation_errors')!r}")
    replay = payload.get("replay")
    if not isinstance(replay, dict):
        raise AssertionError("missing replay object")
    expected = {
        "source_template_id": "T02",
        "family_count": 4,
        "family_ids": EXPECTED_FAMILY_IDS,
        "assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "assignment_counts": EXPECTED_ASSIGNMENT_COUNTS,
        "path_length_counts": {"3": 4},
        "strict_rows": EXPECTED_STRICT_ROWS,
        "all_self_edge_contradictions": True,
    }
    for key, expected_value in expected.items():
        if replay.get(key) != expected_value:
            raise AssertionError(
                f"unexpected replay {key}: {replay.get(key)!r} != {expected_value!r}"
            )
    family_replays = replay.get("family_replays")
    if not isinstance(family_replays, list) or len(family_replays) != 4:
        raise AssertionError("unexpected family_replays")
    for family in family_replays:
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
