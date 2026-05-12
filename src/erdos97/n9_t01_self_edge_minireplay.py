"""Minimal replay for the n=9 T01 self-edge local lemma packet.

This module treats the focused T01 packet as input data and checks only the
small local proof skeleton: selected-distance equality steps plus one strict
vertex-circle chord containment. It is proof-mining scaffolding only.
"""

from __future__ import annotations

from typing import Any

SCHEMA = "erdos97.n9_t01_self_edge_minireplay.v1"
STATUS = "REVIEW_PENDING_T01_SELF_EDGE_MINIREPLAY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SOURCE_PACKET_SCHEMA = "erdos97.n9_vertex_circle_t01_self_edge_lemma_packet.v1"
SOURCE_PACKET = "data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json"


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


def _rows(packet: dict[str, Any], errors: list[str]) -> dict[int, list[int]]:
    raw_rows = packet.get("core_selected_rows")
    if not isinstance(raw_rows, list):
        errors.append("core_selected_rows must be a list")
        return {}
    rows: dict[int, list[int]] = {}
    for index, raw_row in enumerate(raw_rows):
        if not isinstance(raw_row, list) or len(raw_row) != 5:
            errors.append(f"core_selected_rows[{index}] must have center plus four witnesses")
            continue
        try:
            center = int(raw_row[0])
            witnesses = [int(value) for value in raw_row[1:]]
        except (TypeError, ValueError):
            errors.append(f"core_selected_rows[{index}] must contain integer labels")
            continue
        if center in rows:
            errors.append(f"duplicate core row for center {center}")
        if center in witnesses:
            errors.append(f"core row {center} contains its own center")
        if len(set(witnesses)) != 4:
            errors.append(f"core row {center} has duplicate witnesses")
        rows[center] = witnesses
    return rows


def _other_endpoint(pair_value: list[int], center: int) -> int | None:
    if center == pair_value[0]:
        return pair_value[1]
    if center == pair_value[1]:
        return pair_value[0]
    return None


def _replay_equality_chain(
    packet: dict[str, Any],
    rows: dict[int, list[int]],
    errors: list[str],
) -> tuple[list[list[int]], list[dict[str, object]]]:
    equality = packet.get("distance_equality")
    if not isinstance(equality, dict):
        errors.append("distance_equality must be an object")
        return [], []
    current = _pair(equality.get("start_pair"), "distance_equality.start_pair", errors)
    end_pair = _pair(equality.get("end_pair"), "distance_equality.end_pair", errors)
    path = equality.get("path")
    if not isinstance(path, list):
        errors.append("distance_equality.path must be a list")
        return [], []

    chain = [current]
    steps: list[dict[str, object]] = []
    for step_index, step in enumerate(path):
        if not isinstance(step, dict):
            errors.append(f"distance_equality.path[{step_index}] must be an object")
            continue
        try:
            row = int(step["row"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"distance_equality.path[{step_index}].row must be an integer")
            continue
        next_pair = _pair(
            step.get("next_pair"),
            f"distance_equality.path[{step_index}].next_pair",
            errors,
        )
        witnesses = rows.get(row)
        if witnesses is None:
            errors.append(f"equality step {step_index} uses missing row {row}")
            continue
        current_other = _other_endpoint(current, row)
        next_other = _other_endpoint(next_pair, row)
        if current_other is None:
            errors.append(f"equality step {step_index} does not start at row center {row}")
        elif current_other not in witnesses:
            errors.append(
                f"equality step {step_index} current endpoint {current_other} "
                f"is not selected by row {row}"
            )
        if next_other is None:
            errors.append(f"equality step {step_index} does not end at row center {row}")
        elif next_other not in witnesses:
            errors.append(
                f"equality step {step_index} next endpoint {next_other} "
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
        errors.append(f"equality chain ends at {current}, not {end_pair}")
    stored_chain = packet.get("equality_chain")
    if stored_chain != chain:
        errors.append(f"stored equality_chain mismatch: {stored_chain!r} != {chain!r}")
    return chain, steps


def _interval_for_pair(witness_order: list[int], pair_value: list[int]) -> list[int]:
    positions = sorted(witness_order.index(endpoint) for endpoint in pair_value)
    return [int(positions[0]), int(positions[1])]


def _replay_strict_inequality(
    packet: dict[str, Any],
    rows: dict[int, list[int]],
    equality_chain: list[list[int]],
    errors: list[str],
) -> dict[str, object]:
    strict = packet.get("strict_inequality")
    if not isinstance(strict, dict):
        errors.append("strict_inequality must be an object")
        return {}
    try:
        row = int(strict["row"])
        witness_order = [int(value) for value in strict["witness_order"]]
    except (KeyError, TypeError, ValueError):
        errors.append("strict_inequality row and witness_order must be present")
        return {}
    row_witnesses = rows.get(row)
    if row_witnesses is None:
        errors.append(f"strict_inequality uses missing row {row}")
    elif sorted(row_witnesses) != sorted(witness_order):
        errors.append("strict_inequality witness_order must list the row witnesses")

    outer_pair = _pair(strict.get("outer_pair"), "strict_inequality.outer_pair", errors)
    inner_pair = _pair(strict.get("inner_pair"), "strict_inequality.inner_pair", errors)
    for label, pair_value in (("outer", outer_pair), ("inner", inner_pair)):
        for endpoint in pair_value:
            if endpoint not in witness_order:
                errors.append(f"strict_inequality {label}_pair endpoint {endpoint} is not a witness")
    if errors:
        return {}

    outer_interval = _interval_for_pair(witness_order, outer_pair)
    inner_interval = _interval_for_pair(witness_order, inner_pair)
    if strict.get("outer_interval") != outer_interval:
        errors.append("strict_inequality outer_interval mismatch")
    if strict.get("inner_interval") != inner_interval:
        errors.append("strict_inequality inner_interval mismatch")
    if not (
        outer_interval[0] <= inner_interval[0]
        and inner_interval[1] <= outer_interval[1]
        and outer_interval != inner_interval
    ):
        errors.append("strict outer interval must properly contain inner interval")
    if strict.get("outer_span") != outer_interval[1] - outer_interval[0]:
        errors.append("strict_inequality outer_span mismatch")
    if strict.get("inner_span") != inner_interval[1] - inner_interval[0]:
        errors.append("strict_inequality inner_span mismatch")
    if equality_chain and (equality_chain[0] != outer_pair or equality_chain[-1] != inner_pair):
        errors.append("equality chain endpoints must match strict outer and inner pairs")

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


def replay_packet(packet: dict[str, Any]) -> tuple[dict[str, object], list[str]]:
    """Replay the local T01 packet and return a compact summary plus errors."""
    errors: list[str] = []
    if packet.get("schema") != SOURCE_PACKET_SCHEMA:
        errors.append(f"unexpected source schema: {packet.get('schema')!r}")
    if packet.get("template_id") != "T01":
        errors.append(f"unexpected template_id: {packet.get('template_id')!r}")
    if packet.get("family_id") != "F09":
        errors.append(f"unexpected family_id: {packet.get('family_id')!r}")
    if packet.get("cyclic_order") != list(range(9)):
        errors.append("cyclic_order must be the natural nonagon order")

    rows = _rows(packet, errors)
    equality_chain, equality_steps = _replay_equality_chain(packet, rows, errors)
    strict_summary = _replay_strict_inequality(packet, rows, equality_chain, errors)
    summary = {
        "source_template_id": packet.get("template_id"),
        "source_family_id": packet.get("family_id"),
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
    if not summary["self_edge_contradiction"]:
        errors.append("strict inequality does not close on an equality-chain self-edge")
    return summary, errors


def minireplay_payload(packet: dict[str, Any]) -> dict[str, object]:
    """Build the stable mini-replay artifact payload."""
    replay, errors = replay_packet(packet)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Minimal input-data replay of the focused T01/F09 self-edge local "
            "lemma packet; not a proof of n=9, not an independent review of the "
            "full checker, not a counterexample, and not a global status update."
        ),
        "source_packet": SOURCE_PACKET,
        "source_packet_schema": SOURCE_PACKET_SCHEMA,
        "ok": not errors,
        "validation_errors": errors,
        "replay": replay,
        "interpretation": (
            "The selected rows identify the strict outer and inner chord pairs, "
            "while the row-0 vertex-circle order makes the outer chord strictly "
            "longer than the inner chord."
        ),
        "provenance": {
            "generator": "scripts/check_n9_t01_self_edge_minireplay.py",
            "command": "python scripts/check_n9_t01_self_edge_minireplay.py --write --assert-expected",
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
    """Assert the stable expected T01 mini-replay facts."""
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected schema")
    if payload.get("ok") is not True:
        raise AssertionError(f"mini-replay is not ok: {payload.get('validation_errors')!r}")
    replay = payload.get("replay")
    if not isinstance(replay, dict):
        raise AssertionError("missing replay object")
    expected = {
        "source_template_id": "T01",
        "source_family_id": "F09",
        "core_row_count": 3,
        "core_centers": [0, 1, 2],
        "equality_chain": [[1, 8], [0, 1], [0, 2], [1, 2]],
        "equality_step_count": 3,
        "self_edge_contradiction": True,
    }
    for key, expected_value in expected.items():
        if replay.get(key) != expected_value:
            raise AssertionError(
                f"unexpected replay {key}: {replay.get(key)!r} != {expected_value!r}"
            )
    strict = replay.get("strict_inequality")
    if not isinstance(strict, dict):
        raise AssertionError("missing strict_inequality summary")
    if strict.get("outer_pair") != [1, 8] or strict.get("inner_pair") != [1, 2]:
        raise AssertionError("unexpected strict chord pairs")
