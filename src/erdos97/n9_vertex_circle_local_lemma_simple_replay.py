"""Second-source packet replay for n=9 vertex-circle local lemmas.

This module deliberately avoids importing ``vertex_circle_quotient_replay``.
It checks the stored packet records directly: selected-row equality paths,
cyclic witness orders, nested vertex-circle intervals, and local obstruction
counts.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

SCHEMA = "erdos97.n9_vertex_circle_local_lemma_simple_replay.v1"
STATUS = "REVIEW_PENDING_PACKET_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Second-source packet-level audit for the aggregate n=9 vertex-circle "
    "local-lemma coverage. This is not a proof of n=9, not a counterexample, "
    "not an independent review of the exhaustive checker, and not a global "
    "status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_local_lemma_simple_replay.py",
    "command": (
        "python scripts/check_n9_vertex_circle_local_lemma_simple_replay.py "
        "--assert-expected --write"
    ),
}

EXPECTED_SELF_EDGE_ASSIGNMENT_COUNT = 158
EXPECTED_SELF_EDGE_FAMILY_COUNT = 13
EXPECTED_STRICT_CYCLE_ASSIGNMENT_COUNT = 26
EXPECTED_STRICT_CYCLE_FAMILY_COUNT = 3
EXPECTED_TOTAL_ASSIGNMENT_COUNT = 184
EXPECTED_TOTAL_FAMILY_COUNT = 16


def simple_packet_replay_payload(
    self_edge_packet: Mapping[str, Any],
    strict_cycle_packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Replay local obstruction records directly from stored packet JSON."""

    errors: list[dict[str, str]] = []
    self_edge_records: list[dict[str, Any]] = []
    strict_cycle_records: list[dict[str, Any]] = []

    order = _shared_order(self_edge_packet, strict_cycle_packet, errors)
    if order:
        for template, family in _family_records(
            self_edge_packet,
            packet_kind="self-edge",
            errors=errors,
        ):
            try:
                self_edge_records.append(_audit_self_edge_family(template, family, order))
            except (KeyError, TypeError, ValueError, AssertionError) as exc:
                errors.append(_error(_family_scope(template, family), exc))
        for template, family in _family_records(
            strict_cycle_packet,
            packet_kind="strict-cycle",
            errors=errors,
        ):
            try:
                strict_cycle_records.append(
                    _audit_strict_cycle_family(template, family, order)
                )
            except (KeyError, TypeError, ValueError, AssertionError) as exc:
                errors.append(_error(_family_scope(template, family), exc))

    self_edge_assignment_count = sum(
        int(record["assignment_count"]) for record in self_edge_records
    )
    strict_cycle_assignment_count = sum(
        int(record["assignment_count"]) for record in strict_cycle_records
    )
    covered_assignment_count = self_edge_assignment_count + strict_cycle_assignment_count
    covered_family_count = len(self_edge_records) + len(strict_cycle_records)
    errors.extend(
        _coverage_errors(
            self_edge_packet,
            strict_cycle_packet,
            self_edge_family_count=len(self_edge_records),
            self_edge_assignment_count=self_edge_assignment_count,
            strict_cycle_family_count=len(strict_cycle_records),
            strict_cycle_assignment_count=strict_cycle_assignment_count,
            covered_family_count=covered_family_count,
            covered_assignment_count=covered_assignment_count,
        )
    )
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "method": (
            "Packet-level replay from selected rows, stored equality paths, "
            "and stored cyclic interval strict inequalities; this module does "
            "not call the quotient-replay helper or enumerate assignments."
        ),
        "n": int(self_edge_packet.get("n", 0)),
        "cyclic_order": list(order),
        "source_artifacts": [
            _source_summary(
                self_edge_packet,
                "data/certificates/n9_vertex_circle_self_edge_template_packet.json",
                "source self-edge template packet",
            ),
            _source_summary(
                strict_cycle_packet,
                "data/certificates/n9_vertex_circle_strict_cycle_template_packet.json",
                "source strict-cycle template packet",
            ),
        ],
        "self_edge": {
            "family_count": len(self_edge_records),
            "assignment_count": self_edge_assignment_count,
            "records": self_edge_records,
        },
        "strict_cycle": {
            "family_count": len(strict_cycle_records),
            "assignment_count": strict_cycle_assignment_count,
            "records": strict_cycle_records,
        },
        "coverage_summary": {
            "covered_family_count": covered_family_count,
            "covered_assignment_count": covered_assignment_count,
            "self_edge_family_count": len(self_edge_records),
            "self_edge_assignment_count": self_edge_assignment_count,
            "strict_cycle_family_count": len(strict_cycle_records),
            "strict_cycle_assignment_count": strict_cycle_assignment_count,
            "expected_family_count": EXPECTED_TOTAL_FAMILY_COUNT,
            "expected_assignment_count": EXPECTED_TOTAL_ASSIGNMENT_COUNT,
        },
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed audit says the stored local packet records contain enough "
            "data to replay their local reflexive strict-edge or strict-cycle "
            "contradictions without the quotient-replay helper. It does not "
            "certify that the packet family list is complete for n=9."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_simple_packet_replay(payload: Mapping[str, Any]) -> None:
    """Assert the expected packet-level replay counts and scope guardrails."""

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
        "covered_family_count": EXPECTED_TOTAL_FAMILY_COUNT,
        "covered_assignment_count": EXPECTED_TOTAL_ASSIGNMENT_COUNT,
        "self_edge_family_count": EXPECTED_SELF_EDGE_FAMILY_COUNT,
        "self_edge_assignment_count": EXPECTED_SELF_EDGE_ASSIGNMENT_COUNT,
        "strict_cycle_family_count": EXPECTED_STRICT_CYCLE_FAMILY_COUNT,
        "strict_cycle_assignment_count": EXPECTED_STRICT_CYCLE_ASSIGNMENT_COUNT,
    }
    for key, value in expected.items():
        if coverage.get(key) != value:
            raise AssertionError(
                f"coverage_summary[{key!r}] mismatch: expected {value}, "
                f"got {coverage.get(key)!r}"
            )


def _shared_order(
    self_edge_packet: Mapping[str, Any],
    strict_cycle_packet: Mapping[str, Any],
    errors: list[dict[str, str]],
) -> tuple[int, ...]:
    try:
        _validate_packet_header(self_edge_packet, role="self-edge")
        _validate_packet_header(strict_cycle_packet, role="strict-cycle")
        self_order = _order_from_packet(self_edge_packet)
        strict_order = _order_from_packet(strict_cycle_packet)
        if self_order != strict_order:
            raise ValueError("source packets must use the same cyclic_order")
        if int(self_edge_packet.get("n", len(self_order))) != int(
            strict_cycle_packet.get("n", len(strict_order))
        ):
            raise ValueError("source packets must use the same n")
        return self_order
    except (KeyError, TypeError, ValueError, AssertionError) as exc:
        errors.append(_error("source packets", exc))
        return ()


def _validate_packet_header(packet: Mapping[str, Any], *, role: str) -> None:
    if packet.get("status") != "REVIEW_PENDING_DIAGNOSTIC_ONLY":
        raise AssertionError(f"{role} packet status mismatch")
    if packet.get("trust") != TRUST:
        raise AssertionError(f"{role} packet trust mismatch")
    if int(packet.get("n", 0)) != 9:
        raise AssertionError(f"{role} packet n mismatch")
    claim_scope = str(packet.get("claim_scope", ""))
    for forbidden in ("proof of n=9", "counterexample", "global status update"):
        if f"not a {forbidden}" not in claim_scope and f"not an {forbidden}" not in claim_scope:
            raise AssertionError(f"{role} packet must explicitly reject {forbidden!r}")


def _coverage_errors(
    self_edge_packet: Mapping[str, Any],
    strict_cycle_packet: Mapping[str, Any],
    *,
    self_edge_family_count: int,
    self_edge_assignment_count: int,
    strict_cycle_family_count: int,
    strict_cycle_assignment_count: int,
    covered_family_count: int,
    covered_assignment_count: int,
) -> list[dict[str, str]]:
    errors = []
    checks = [
        (
            "self-edge coverage",
            self_edge_family_count,
            EXPECTED_SELF_EDGE_FAMILY_COUNT,
            _packet_count(
                self_edge_packet,
                "self_edge_family_count",
                "self-edge coverage",
                "family count",
                errors,
            ),
            "family count",
        ),
        (
            "self-edge coverage",
            self_edge_assignment_count,
            EXPECTED_SELF_EDGE_ASSIGNMENT_COUNT,
            _packet_count(
                self_edge_packet,
                "self_edge_assignment_count",
                "self-edge coverage",
                "assignment count",
                errors,
            ),
            "assignment count",
        ),
        (
            "strict-cycle coverage",
            strict_cycle_family_count,
            EXPECTED_STRICT_CYCLE_FAMILY_COUNT,
            _packet_count(
                strict_cycle_packet,
                "strict_cycle_family_count",
                "strict-cycle coverage",
                "family count",
                errors,
            ),
            "family count",
        ),
        (
            "strict-cycle coverage",
            strict_cycle_assignment_count,
            EXPECTED_STRICT_CYCLE_ASSIGNMENT_COUNT,
            _packet_count(
                strict_cycle_packet,
                "strict_cycle_assignment_count",
                "strict-cycle coverage",
                "assignment count",
                errors,
            ),
            "assignment count",
        ),
        (
            "aggregate coverage",
            covered_family_count,
            EXPECTED_TOTAL_FAMILY_COUNT,
            EXPECTED_TOTAL_FAMILY_COUNT,
            "family count",
        ),
        (
            "aggregate coverage",
            covered_assignment_count,
            EXPECTED_TOTAL_ASSIGNMENT_COUNT,
            EXPECTED_TOTAL_ASSIGNMENT_COUNT,
            "assignment count",
        ),
    ]
    for scope, observed, expected, packet_value, label in checks:
        if observed != expected:
            errors.append(_error(scope, AssertionError(f"{label} {observed} != {expected}")))
        if packet_value is not None and observed != packet_value:
            errors.append(
                _error(scope, AssertionError(f"{label} {observed} != packet {packet_value}"))
            )
    return errors


def _packet_count(
    packet: Mapping[str, Any],
    key: str,
    scope: str,
    label: str,
    errors: list[dict[str, str]],
) -> int | None:
    try:
        return int(packet.get(key, -1))
    except (TypeError, ValueError):
        errors.append(_error(scope, AssertionError(f"packet {label} is not an integer")))
        return None


def _order_from_packet(packet: Mapping[str, Any]) -> tuple[int, ...]:
    raw_order = packet.get("cyclic_order")
    if not isinstance(raw_order, Sequence) or isinstance(raw_order, str):
        raise ValueError("packet must contain cyclic_order")
    order = tuple(int(label) for label in raw_order)
    if len(set(order)) != len(order):
        raise ValueError("cyclic_order must have distinct labels")
    return order


def _family_records(
    packet: Mapping[str, Any],
    *,
    packet_kind: str,
    errors: list[dict[str, str]],
) -> list[tuple[Mapping[str, Any], Mapping[str, Any]]]:
    templates = packet.get("templates")
    if not isinstance(templates, list):
        errors.append(_error(packet_kind, ValueError("packet must contain templates")))
        return []
    records = []
    for template in templates:
        if not isinstance(template, Mapping):
            errors.append(_error(packet_kind, ValueError("template entry must be an object")))
            continue
        family_records = template.get("family_records")
        if not isinstance(family_records, list):
            errors.append(
                _error(
                    str(template.get("template_id", packet_kind)),
                    ValueError("template must contain family_records"),
                )
            )
            continue
        for family in family_records:
            if not isinstance(family, Mapping):
                errors.append(
                    _error(
                        str(template.get("template_id", packet_kind)),
                        ValueError("family entry must be an object"),
                    )
                )
                continue
            records.append((template, family))
    return records


def _audit_self_edge_family(
    template: Mapping[str, Any],
    family: Mapping[str, Any],
    order: Sequence[int],
) -> dict[str, Any]:
    if family.get("status") != "self_edge":
        raise AssertionError("self-edge family status mismatch")
    rows = _parse_rows(family["core_selected_rows"])
    edge = family["strict_inequality"]
    equality = family["distance_equality"]
    if not isinstance(edge, Mapping) or not isinstance(equality, Mapping):
        raise AssertionError("self-edge family must contain edge and equality records")
    _verify_strict_inequality(edge, rows, order)
    _verify_equality_path(
        equality,
        rows,
        expected_start=_pair(edge["outer_pair"]),
        expected_end=_pair(edge["inner_pair"]),
    )
    if _pair(edge.get("outer_class")) != _pair(edge.get("inner_class")):
        raise AssertionError("stored strict edge is not reflexive")
    return _family_summary(
        template,
        family,
        obstruction_kind="reflexive_strict_edge",
        replayed_step_count=len(equality.get("path", [])),
    )


def _audit_strict_cycle_family(
    template: Mapping[str, Any],
    family: Mapping[str, Any],
    order: Sequence[int],
) -> dict[str, Any]:
    if family.get("status") != "strict_cycle":
        raise AssertionError("strict-cycle family status mismatch")
    rows = _parse_rows(family["core_selected_rows"])
    cycle_steps = family.get("cycle_steps")
    if not isinstance(cycle_steps, list):
        raise AssertionError("strict-cycle family must contain cycle_steps")
    if int(family.get("cycle_length", -1)) != len(cycle_steps):
        raise AssertionError("cycle_length does not match cycle_steps")

    for index, step in enumerate(cycle_steps):
        if not isinstance(step, Mapping):
            raise AssertionError("cycle step must be an object")
        edge = step.get("strict_inequality")
        equality = step.get("equality_to_next_outer_pair")
        if not isinstance(edge, Mapping) or not isinstance(equality, Mapping):
            raise AssertionError("cycle step must contain edge and equality")
        next_edge = cycle_steps[(index + 1) % len(cycle_steps)]["strict_inequality"]
        _verify_strict_inequality(edge, rows, order)
        _verify_equality_path(
            equality,
            rows,
            expected_start=_pair(edge["inner_pair"]),
            expected_end=_pair(next_edge["outer_pair"]),
        )

    return _family_summary(
        template,
        family,
        obstruction_kind="directed_strict_cycle",
        replayed_step_count=len(cycle_steps),
    )


def _parse_rows(raw_rows: Any) -> dict[int, tuple[int, ...]]:
    if not isinstance(raw_rows, list):
        raise ValueError("core_selected_rows must be a list")
    rows: dict[int, tuple[int, ...]] = {}
    for raw_row in raw_rows:
        if not isinstance(raw_row, list) or len(raw_row) != 5:
            raise ValueError("each selected row must have one center and four witnesses")
        labels = tuple(int(label) for label in raw_row)
        center, witnesses = labels[0], labels[1:]
        if center in rows:
            raise ValueError(f"duplicate selected row center {center}")
        if center in witnesses or len(set(witnesses)) != 4:
            raise ValueError(f"invalid witnesses for row {center}")
        rows[center] = witnesses
    return rows


def _verify_strict_inequality(
    edge: Mapping[str, Any],
    rows: Mapping[int, tuple[int, ...]],
    order: Sequence[int],
) -> None:
    center = int(edge["row"])
    witnesses = rows.get(center)
    if witnesses is None:
        raise AssertionError(f"strict edge row {center} is not selected")
    witness_order = _witness_order(center, witnesses, order)
    if list(witness_order) != [int(label) for label in edge["witness_order"]]:
        raise AssertionError(f"strict edge row {center} witness_order mismatch")
    outer = _interval(edge["outer_interval"], len(witness_order))
    inner = _interval(edge["inner_interval"], len(witness_order))
    if _pair_at_interval(witness_order, outer) != _pair(edge["outer_pair"]):
        raise AssertionError("outer_pair does not match outer_interval")
    if _pair_at_interval(witness_order, inner) != _pair(edge["inner_pair"]):
        raise AssertionError("inner_pair does not match inner_interval")
    outer_span = outer[1] - outer[0]
    inner_span = inner[1] - inner[0]
    if int(edge.get("outer_span", outer_span)) != outer_span:
        raise AssertionError("outer_span does not match outer_interval")
    if int(edge.get("inner_span", inner_span)) != inner_span:
        raise AssertionError("inner_span does not match inner_interval")
    if not (outer[0] <= inner[0] and inner[1] <= outer[1] and outer_span > inner_span):
        raise AssertionError("stored strict edge is not a nested interval inequality")


def _verify_equality_path(
    equality: Mapping[str, Any],
    rows: Mapping[int, tuple[int, ...]],
    *,
    expected_start: tuple[int, int],
    expected_end: tuple[int, int],
) -> None:
    current = _pair(equality["start_pair"])
    if current != expected_start:
        raise AssertionError("equality path start_pair mismatch")
    path = equality.get("path")
    if not isinstance(path, list):
        raise AssertionError("equality path must contain a path list")
    for step in path:
        if not isinstance(step, Mapping):
            raise AssertionError("equality path step must be an object")
        row = int(step["row"])
        next_pair = _pair(step["next_pair"])
        _assert_row_supports_pair(rows, row, current)
        _assert_row_supports_pair(rows, row, next_pair)
        current = next_pair
    if current != _pair(equality["end_pair"]):
        raise AssertionError("equality path end_pair does not match final step")
    if current != expected_end:
        raise AssertionError("equality path end_pair mismatch")


def _assert_row_supports_pair(
    rows: Mapping[int, tuple[int, ...]],
    row: int,
    candidate_pair: tuple[int, int],
) -> None:
    witnesses = rows.get(row)
    if witnesses is None:
        raise AssertionError(f"equality path row {row} is not selected")
    if row not in candidate_pair:
        raise AssertionError(f"row {row} cannot identify pair {list(candidate_pair)}")
    other = candidate_pair[0] if candidate_pair[1] == row else candidate_pair[1]
    if other not in witnesses:
        raise AssertionError(f"row {row} does not select witness {other}")


def _witness_order(
    center: int,
    witnesses: Sequence[int],
    order: Sequence[int],
) -> tuple[int, ...]:
    positions = {label: index for index, label in enumerate(order)}
    if center not in positions:
        raise AssertionError(f"center {center} is missing from cyclic_order")
    missing = [label for label in witnesses if label not in positions]
    if missing:
        raise AssertionError(f"witness labels missing from cyclic_order: {missing!r}")
    center_pos = positions[center]
    return tuple(sorted(witnesses, key=lambda label: (positions[label] - center_pos) % len(order)))


def _interval(raw_interval: Any, witness_count: int) -> tuple[int, int]:
    if not isinstance(raw_interval, list) or len(raw_interval) != 2:
        raise AssertionError("interval must have two endpoints")
    start, end = int(raw_interval[0]), int(raw_interval[1])
    if not (0 <= start < end < witness_count):
        raise AssertionError("interval endpoints must satisfy 0 <= start < end < count")
    return start, end


def _pair(raw_pair: Any) -> tuple[int, int]:
    if not isinstance(raw_pair, Sequence) or isinstance(raw_pair, str) or len(raw_pair) != 2:
        raise AssertionError("pair must contain two labels")
    left, right = int(raw_pair[0]), int(raw_pair[1])
    if left == right:
        raise AssertionError("pair labels must be distinct")
    return tuple(sorted((left, right)))


def _pair_at_interval(
    witness_order: Sequence[int],
    interval: tuple[int, int],
) -> tuple[int, int]:
    return _pair([witness_order[interval[0]], witness_order[interval[1]]])


def _family_summary(
    template: Mapping[str, Any],
    family: Mapping[str, Any],
    *,
    obstruction_kind: str,
    replayed_step_count: int,
) -> dict[str, Any]:
    return {
        "template_id": str(template["template_id"]),
        "family_id": str(family["family_id"]),
        "template_key": str(template["template_key"]),
        "assignment_count": int(family["assignment_count"]),
        "orbit_size": int(family["orbit_size"]),
        "core_size": int(family["core_size"]),
        "obstruction_kind": obstruction_kind,
        "replayed_step_count": replayed_step_count,
    }


def _source_summary(packet: Mapping[str, Any], path: str, role: str) -> dict[str, Any]:
    return {
        "path": path,
        "role": role,
        "schema": packet.get("schema"),
        "status": packet.get("status"),
        "trust": packet.get("trust"),
    }


def _family_scope(template: Mapping[str, Any], family: Mapping[str, Any]) -> str:
    return f"{template.get('template_id', '?')}/{family.get('family_id', '?')}"


def _error(scope: str, exc: BaseException) -> dict[str, str]:
    return {
        "scope": scope,
        "error": str(exc),
    }
