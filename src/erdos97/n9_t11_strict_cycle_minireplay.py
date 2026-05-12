"""Minimal replay for the n=9 T11 strict-cycle local lemma packet.

This module treats the focused T11 packet as input data and checks only the
small local proof skeleton: three selected-distance connector paths plus three
strict vertex-circle chord containments forming a directed cycle. It is
proof-mining scaffolding only.
"""

from __future__ import annotations

from typing import Any

SCHEMA = "erdos97.n9_t11_strict_cycle_minireplay.v1"
STATUS = "REVIEW_PENDING_T11_STRICT_CYCLE_MINIREPLAY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SOURCE_PACKET_SCHEMA = "erdos97.n9_vertex_circle_t11_strict_cycle_lemma_packet.v1"
SOURCE_PACKET = "data/certificates/n9_vertex_circle_t11_strict_cycle_lemma_packet.json"
TEMPLATE_ID = "T11"
FAMILY_ID = "F07"
EXPECTED_CYCLE_LENGTH = 3
EXPECTED_STRICT_WITNESS_ORDERS = [
    [2, 3, 5, 0],
    [2, 3, 5, 0],
    [7, 8, 1, 5],
]


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


def _rows(raw_rows: Any, errors: list[str]) -> dict[int, list[int]]:
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
    if len(pair_value) != 2:
        return None
    if center == pair_value[0]:
        return pair_value[1]
    if center == pair_value[1]:
        return pair_value[0]
    return None


def _interval_for_pair(witness_order: list[int], pair_value: list[int]) -> list[int]:
    if len(pair_value) != 2:
        return []
    if pair_value[0] not in witness_order or pair_value[1] not in witness_order:
        return []
    positions = sorted(witness_order.index(endpoint) for endpoint in pair_value)
    return [int(positions[0]), int(positions[1])]


def _replay_equality(
    equality: Any,
    rows: dict[int, list[int]],
    label: str,
    errors: list[str],
) -> tuple[list[list[int]], list[dict[str, object]]]:
    if not isinstance(equality, dict):
        errors.append(f"{label} must be an object")
        return [], []
    current = _pair(equality.get("start_pair"), f"{label}.start_pair", errors)
    end_pair = _pair(equality.get("end_pair"), f"{label}.end_pair", errors)
    path = equality.get("path")
    if not isinstance(path, list):
        errors.append(f"{label}.path must be a list")
        return [], []

    chain = [current]
    steps: list[dict[str, object]] = []
    for step_index, step in enumerate(path):
        if not isinstance(step, dict):
            errors.append(f"{label}.path[{step_index}] must be an object")
            continue
        try:
            row = int(step["row"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"{label}.path[{step_index}].row must be an integer")
            continue
        next_pair = _pair(
            step.get("next_pair"),
            f"{label}.path[{step_index}].next_pair",
            errors,
        )
        witnesses = rows.get(row)
        if witnesses is None:
            errors.append(f"{label} step {step_index} uses missing row {row}")
            continue
        current_other = _other_endpoint(current, row)
        next_other = _other_endpoint(next_pair, row)
        if current_other is None:
            errors.append(f"{label} step {step_index} does not start at row center {row}")
        elif current_other not in witnesses:
            errors.append(
                f"{label} step {step_index} current endpoint {current_other} "
                f"is not selected by row {row}"
            )
        if next_other is None:
            errors.append(f"{label} step {step_index} does not end at row center {row}")
        elif next_other not in witnesses:
            errors.append(
                f"{label} step {step_index} next endpoint {next_other} "
                f"is not selected by row {row}"
            )
        steps.append({"row": row, "left_pair": current, "right_pair": next_pair})
        current = next_pair
        chain.append(current)

    if current != end_pair:
        errors.append(f"{label} ends at {current}, not {end_pair}")
    return chain, steps


def _replay_strict(
    strict: Any,
    rows: dict[int, list[int]],
    label: str,
    errors: list[str],
    *,
    expected_witness_order: list[int],
) -> dict[str, object]:
    if not isinstance(strict, dict):
        errors.append(f"{label} strict_inequality must be an object")
        return {}
    starting_error_count = len(errors)
    try:
        row = int(strict["row"])
        witness_order = [int(value) for value in strict["witness_order"]]
    except (KeyError, TypeError, ValueError):
        errors.append(f"{label} strict row and witness_order must be present")
        return {}

    row_witnesses = rows.get(row)
    if row_witnesses is None:
        errors.append(f"{label} strict_inequality uses missing row {row}")
    elif sorted(row_witnesses) != sorted(witness_order):
        errors.append(f"{label} strict_inequality witness_order must list row witnesses")
    if witness_order != expected_witness_order:
        errors.append(f"{label} strict_inequality witness_order changed")

    outer_pair = _pair(strict.get("outer_pair"), f"{label}.outer_pair", errors)
    inner_pair = _pair(strict.get("inner_pair"), f"{label}.inner_pair", errors)
    for pair_label, pair_value in (("outer", outer_pair), ("inner", inner_pair)):
        for endpoint in pair_value:
            if endpoint not in witness_order:
                errors.append(
                    f"{label} {pair_label}_pair endpoint {endpoint} is not a witness"
                )
    if len(errors) != starting_error_count:
        return {}

    outer_interval = _interval_for_pair(witness_order, outer_pair)
    inner_interval = _interval_for_pair(witness_order, inner_pair)
    if strict.get("outer_interval") != outer_interval:
        errors.append(f"{label} outer_interval mismatch")
    if strict.get("inner_interval") != inner_interval:
        errors.append(f"{label} inner_interval mismatch")
    if not (
        outer_interval[0] <= inner_interval[0]
        and inner_interval[1] <= outer_interval[1]
        and outer_interval != inner_interval
    ):
        errors.append(f"{label} outer interval must properly contain inner interval")
    outer_span = outer_interval[1] - outer_interval[0]
    inner_span = inner_interval[1] - inner_interval[0]
    if strict.get("outer_span") != outer_span:
        errors.append(f"{label} outer_span mismatch")
    if strict.get("inner_span") != inner_span:
        errors.append(f"{label} inner_span mismatch")

    return {
        "row": row,
        "witness_order": witness_order,
        "outer_pair": outer_pair,
        "inner_pair": inner_pair,
        "outer_interval": outer_interval,
        "inner_interval": inner_interval,
        "outer_span": outer_span,
        "inner_span": inner_span,
    }


def _family_packet(packet: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    packets = packet.get("family_packets")
    if not isinstance(packets, list):
        errors.append("family_packets must be a list")
        return {}
    matches = [
        family_packet
        for family_packet in packets
        if isinstance(family_packet, dict) and family_packet.get("family_id") == FAMILY_ID
    ]
    if len(matches) != 1:
        errors.append(f"expected exactly one {FAMILY_ID} family packet, got {len(matches)}")
        return {}
    return matches[0]


def replay_packet(packet: dict[str, Any]) -> tuple[dict[str, object], list[str]]:
    """Replay the local T11 packet and return a compact summary plus errors."""
    errors: list[str] = []
    if packet.get("schema") != SOURCE_PACKET_SCHEMA:
        errors.append(f"unexpected source schema: {packet.get('schema')!r}")
    if packet.get("template_id") != TEMPLATE_ID:
        errors.append(f"unexpected template_id: {packet.get('template_id')!r}")
    if packet.get("cyclic_order") != list(range(9)):
        errors.append("cyclic_order must be the natural nonagon order")

    family = _family_packet(packet, errors)
    if not family:
        return {}, errors
    if family.get("family_id") != FAMILY_ID:
        errors.append(f"unexpected family_id: {family.get('family_id')!r}")
    rows = _rows(family.get("core_selected_rows"), errors)
    cycle_steps = family.get("cycle_steps")
    if not isinstance(cycle_steps, list):
        errors.append("cycle_steps must be a list")
        return {}, errors
    if len(cycle_steps) != EXPECTED_CYCLE_LENGTH:
        errors.append(
            f"expected a {EXPECTED_CYCLE_LENGTH}-step strict cycle, "
            f"got {len(cycle_steps)}"
        )

    steps: list[dict[str, object]] = []
    strict_summaries: list[dict[str, object]] = []
    equality_chains: list[list[list[int]]] = []
    clean_steps: list[bool] = []
    for index, raw_step in enumerate(cycle_steps):
        if not isinstance(raw_step, dict):
            errors.append(f"cycle_steps[{index}] must be an object")
            continue
        label = f"cycle_steps[{index}]"
        starting_error_count = len(errors)
        strict_summary = _replay_strict(
            raw_step.get("strict_inequality"),
            rows,
            label,
            errors,
            expected_witness_order=EXPECTED_STRICT_WITNESS_ORDERS[index]
            if index < len(EXPECTED_STRICT_WITNESS_ORDERS)
            else [],
        )
        equality_chain, equality_steps = _replay_equality(
            raw_step.get("equality_to_next_outer_pair"),
            rows,
            f"{label}.equality_to_next_outer_pair",
            errors,
        )
        strict_summaries.append(strict_summary)
        equality_chains.append(equality_chain)
        clean_steps.append(len(errors) == starting_error_count)
        steps.append(
            {
                "cycle_step": index,
                "strict_inequality": strict_summary,
                "equality_chain_to_next_outer_pair": equality_chain,
                "equality_steps": equality_steps,
            }
        )

    closes = False
    if (
        len(strict_summaries)
        == len(equality_chains)
        == len(clean_steps)
        == EXPECTED_CYCLE_LENGTH
        and all(strict_summaries)
        and all(clean_steps)
    ):
        closes = True
        for index, strict_summary in enumerate(strict_summaries):
            equality_chain = equality_chains[index]
            next_strict = strict_summaries[(index + 1) % len(strict_summaries)]
            if not equality_chain:
                closes = False
                continue
            if equality_chain[0] != strict_summary.get("inner_pair"):
                errors.append(f"cycle step {index} equality does not start at strict inner pair")
                closes = False
            if equality_chain[-1] != next_strict.get("outer_pair"):
                errors.append(f"cycle step {index} equality does not end at next outer pair")
                closes = False

    stored_chain = family.get("cycle_pair_chain")
    expected_chain = [
        {
            "cycle_step": step["cycle_step"],
            "strict_from_outer_pair": step["strict_inequality"].get("outer_pair"),
            "strict_to_inner_pair": step["strict_inequality"].get("inner_pair"),
            "equality_chain_to_next_outer_pair": step[
                "equality_chain_to_next_outer_pair"
            ],
            "next_outer_pair": strict_summaries[(index + 1) % len(strict_summaries)].get(
                "outer_pair"
            )
            if len(strict_summaries) == EXPECTED_CYCLE_LENGTH and all(strict_summaries)
            else None,
        }
        for index, step in enumerate(steps)
        if isinstance(step.get("strict_inequality"), dict)
    ]
    if stored_chain != expected_chain:
        errors.append("stored cycle_pair_chain mismatch")

    summary = {
        "source_template_id": packet.get("template_id"),
        "source_family_id": family.get("family_id"),
        "core_row_count": len(rows),
        "core_centers": sorted(rows),
        "cycle_length": len(cycle_steps),
        "cycle_steps": steps,
        "strict_cycle_contradiction": closes,
    }
    if not closes:
        errors.append("strict inequalities and equality connectors do not close a cycle")
    return summary, errors


def minireplay_payload(packet: dict[str, Any]) -> dict[str, object]:
    """Build the stable T11 mini-replay artifact payload."""
    replay, errors = replay_packet(packet)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Minimal input-data replay of the focused T11/F07 strict-cycle "
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
            "Three selected-distance connector paths identify each strict edge's "
            "inner pair with the next strict edge's outer pair, closing a "
            "directed strict cycle."
        ),
        "provenance": {
            "generator": "scripts/check_n9_t11_strict_cycle_minireplay.py",
            "command": (
                "python scripts/check_n9_t11_strict_cycle_minireplay.py "
                "--write --assert-expected"
            ),
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
    """Assert the stable expected T11 mini-replay facts."""
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected schema")
    if payload.get("ok") is not True:
        raise AssertionError(f"mini-replay is not ok: {payload.get('validation_errors')!r}")
    replay = payload.get("replay")
    if not isinstance(replay, dict):
        raise AssertionError("missing replay object")
    expected = {
        "source_template_id": TEMPLATE_ID,
        "source_family_id": FAMILY_ID,
        "core_row_count": 4,
        "core_centers": [0, 1, 5, 6],
        "cycle_length": EXPECTED_CYCLE_LENGTH,
        "strict_cycle_contradiction": True,
    }
    for key, expected_value in expected.items():
        if replay.get(key) != expected_value:
            raise AssertionError(
                f"unexpected replay {key}: {replay.get(key)!r} != {expected_value!r}"
            )
    steps = replay.get("cycle_steps")
    if not isinstance(steps, list) or len(steps) != EXPECTED_CYCLE_LENGTH:
        raise AssertionError("expected three cycle steps")
    expected_chains = [
        [[0, 3]],
        [[0, 5], [5, 7]],
        [[1, 5], [0, 1], [0, 2]],
    ]
    actual_chains = [step.get("equality_chain_to_next_outer_pair") for step in steps]
    if actual_chains != expected_chains:
        raise AssertionError(f"unexpected equality chains: {actual_chains!r}")
