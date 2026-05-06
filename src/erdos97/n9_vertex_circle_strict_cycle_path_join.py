"""Join n=9 strict-cycle assignments to transformed local-core cycles.

This module is diagnostic. It does not prove Erdos Problem #97, does not
claim a counterexample, and does not promote the review-pending n=9 checker.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Sequence

from erdos97 import n9_vertex_circle_exhaustive as n9
from erdos97.n9_vertex_circle_frontier_motif_classification import (
    invert_label_map,
    transform_compact_rows,
)
from erdos97.n9_vertex_circle_obstruction_shapes import EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS
from erdos97.n9_vertex_circle_obstruction_shapes import (
    EXPECTED_STRICT_CYCLE_LENGTH_COUNTS as EXPECTED_FULL_ASSIGNMENT_STRICT_CYCLE_LENGTH_COUNTS_RAW,
)
from erdos97.n9_vertex_circle_self_edge_path_join import (
    compact_core_rows,
    transform_equality_path,
    transform_pair,
    validate_equality_path,
    validate_label_map,
)
from erdos97.vertex_circle_quotient_replay import (
    StrictInequality,
    _distance_class_union_find,
    _strict_inequalities,
    pair,
    parse_selected_rows,
    replay_vertex_circle_quotient,
)


SCHEMA = "erdos97.n9_vertex_circle_strict_cycle_path_join.v1"
STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Assignment-level join of the 26 n=9 strict-cycle frontier assignments to "
    "transformed family representative local-core strict cycles; not a proof "
    "of n=9, not a counterexample, not an independent review of the exhaustive "
    "checker, and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_strict_cycle_path_join.py",
    "command": (
        "python scripts/check_n9_vertex_circle_strict_cycle_path_join.py "
        "--assert-expected --write"
    ),
}
EXPECTED_SELF_EDGE_ASSIGNMENTS = 158
EXPECTED_STRICT_CYCLE_ASSIGNMENTS = 26
EXPECTED_STRICT_CYCLE_FAMILIES = 3
EXPECTED_STRICT_CYCLE_TEMPLATES = 3
EXPECTED_CYCLE_STEP_COUNT = 60
EXPECTED_CYCLE_LENGTH_COUNTS = {"2": 18, "3": 8}
EXPECTED_FIRST_FULL_ASSIGNMENT_CYCLE_LENGTH_COUNTS = {
    str(length): int(count)
    for length, count in EXPECTED_FULL_ASSIGNMENT_STRICT_CYCLE_LENGTH_COUNTS_RAW.items()
}
EXPECTED_CORE_SIZE_COUNTS = {"4": 24, "6": 2}
EXPECTED_STRICT_EDGE_COUNT_COUNTS = {"36": 24, "54": 2}
EXPECTED_CONNECTOR_PATH_LENGTH_COUNTS = {"0": 6, "1": 28, "2": 26}
EXPECTED_FAMILY_ASSIGNMENT_COUNTS = {"F07": 6, "F12": 18, "F16": 2}
EXPECTED_TEMPLATE_ASSIGNMENT_COUNTS = {"T10": 18, "T11": 6, "T12": 2}
EXPECTED_SPAN_SIGNATURE_COUNTS = {
    "2:1,2:1": 18,
    "2:1,3:1,3:2": 6,
    "3:1,3:1,3:1": 2,
}


def _edge_to_json(edge: StrictInequality) -> dict[str, Any]:
    return {
        "row": int(edge.row),
        "witness_order": [int(label) for label in edge.witness_order],
        "outer_interval": [int(value) for value in edge.outer_interval],
        "inner_interval": [int(value) for value in edge.inner_interval],
        "outer_pair": [int(value) for value in edge.outer_pair],
        "inner_pair": [int(value) for value in edge.inner_pair],
        "outer_class": [int(value) for value in edge.outer_class],
        "inner_class": [int(value) for value in edge.inner_class],
        "outer_span": int(edge.outer_interval[1] - edge.outer_interval[0]),
        "inner_span": int(edge.inner_interval[1] - edge.inner_interval[0]),
    }


def _strict_cycle_certificates(
    local_core_payload: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    certificates = local_core_payload.get("certificates")
    if not isinstance(certificates, list):
        raise ValueError("local-core payload must contain certificates")
    return {
        str(certificate["family_id"]): certificate
        for certificate in certificates
        if certificate.get("status") == "strict_cycle"
    }


def _find_transformed_cycle_edge(
    edges: Sequence[StrictInequality],
    expected_row: int,
    outer_pair: Sequence[int],
    inner_pair: Sequence[int],
) -> StrictInequality:
    expected_outer = pair(*outer_pair)
    expected_inner = pair(*inner_pair)
    for edge in edges:
        if (
            edge.row == expected_row
            and edge.outer_pair == expected_outer
            and edge.inner_pair == expected_inner
        ):
            return edge
    raise AssertionError(
        f"transformed strict-cycle edge not found: {expected_outer} > {expected_inner}"
    )


def _strict_edges_for_rows(rows: Sequence[Sequence[int]]) -> list[StrictInequality]:
    """Return all replay strict inequalities for a compact selected-row core."""

    parsed_rows = parse_selected_rows(rows)
    uf = _distance_class_union_find(n9.N, parsed_rows)
    return _strict_inequalities(n9.N, list(n9.ORDER), parsed_rows, uf)


def _transform_cycle_step(
    step: dict[str, Any],
    label_map: Sequence[int],
) -> dict[str, Any]:
    raw_edge = step["strict_inequality"]
    raw_equality = step["equality_to_next_outer_pair"]
    return {
        "expected_row": int(label_map[int(raw_edge["row"])]),
        "expected_outer_pair": transform_pair(raw_edge["outer_pair"], label_map),
        "expected_inner_pair": transform_pair(raw_edge["inner_pair"], label_map),
        "equality_to_next_outer_pair": transform_equality_path(raw_equality, label_map),
    }


def _span_signature(edges: Sequence[dict[str, Any]]) -> str:
    tokens = sorted(
        f"{int(edge['outer_span'])}:{int(edge['inner_span'])}" for edge in edges
    )
    return ",".join(tokens)


def _template_family_rows(template_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    families = template_payload.get("families")
    if not isinstance(families, list):
        raise ValueError("template payload must contain families")
    return {
        str(family["family_id"]): family
        for family in families
        if isinstance(family, dict) and family.get("status") == "strict_cycle"
    }


def _template_span_signature(template_family: dict[str, Any]) -> str:
    summary = template_family.get("obstruction_summary")
    if not isinstance(summary, dict):
        raise ValueError("template family must contain obstruction_summary")
    span_counts = summary.get("cycle_span_counts")
    if not isinstance(span_counts, list):
        raise ValueError("template family must contain cycle_span_counts")
    tokens = []
    for span_count in span_counts:
        count = int(span_count["count"])
        outer_span = int(span_count["outer_span"])
        inner_span = int(span_count["inner_span"])
        tokens.extend(f"{outer_span}:{inner_span}" for _ in range(count))
    return ",".join(sorted(tokens))


def _validate_template_family(record: dict[str, Any], template_family: dict[str, Any]) -> None:
    expected = {
        "template_id": str(template_family["template_id"]),
        "status": "strict_cycle",
        "core_size": int(template_family["core_size"]),
        "cycle_length": int(template_family["obstruction_summary"]["cycle_length"]),
        "strict_edge_count": int(template_family["strict_edge_count"]),
        "span_signature": _template_span_signature(template_family),
    }
    for key, value in expected.items():
        if record.get(key) != value:
            raise AssertionError(
                f"{record['assignment_id']} {key} does not match template artifact"
            )


def _validate_transformed_cycle_steps(
    rows: Sequence[Sequence[int]],
    steps: Sequence[dict[str, Any]],
) -> None:
    for index, step in enumerate(steps):
        edge = step["strict_inequality"]
        equality = step["equality_to_next_outer_pair"]
        next_edge = steps[(index + 1) % len(steps)]["strict_inequality"]
        if pair(*equality["start_pair"]) != pair(*edge["inner_pair"]):
            raise AssertionError("cycle equality must start at current inner pair")
        if pair(*equality["end_pair"]) != pair(*next_edge["outer_pair"]):
            raise AssertionError("cycle equality must end at next outer pair")
        validate_equality_path(rows, equality)


def strict_cycle_path_join_record(
    assignment: dict[str, Any],
    certificate: dict[str, Any],
) -> dict[str, Any]:
    """Return one transformed strict-cycle path record for a labelled assignment."""

    family_id = str(assignment["family_id"])
    validate_label_map(assignment["to_canonical_label_map"])
    inverse_map = invert_label_map(assignment["to_canonical_label_map"])
    expected_core_rows = transform_compact_rows(
        compact_core_rows(certificate),
        inverse_map,
    )
    if assignment["core_selected_rows"] != expected_core_rows:
        raise AssertionError(
            f"{assignment['assignment_id']} core rows do not match transformed family core"
        )

    parsed_rows = parse_selected_rows(assignment["core_selected_rows"])
    result = replay_vertex_circle_quotient(
        n9.N,
        list(n9.ORDER),
        parsed_rows,
    )
    if result.self_edge_conflicts:
        raise AssertionError(f"{assignment['assignment_id']} core replay has self-edge")
    if result.status != "strict_cycle":
        raise AssertionError(
            f"{assignment['assignment_id']} core replay status {result.status!r}"
        )
    all_strict_edges = _strict_edges_for_rows(assignment["core_selected_rows"])
    if len(all_strict_edges) != result.strict_edge_count:
        raise AssertionError("replayed strict-edge count mismatch")

    raw_steps = certificate["cycle_steps"]
    transformed_steps = [_transform_cycle_step(step, inverse_map) for step in raw_steps]
    cycle_steps = []
    for transformed in transformed_steps:
        edge = _find_transformed_cycle_edge(
            all_strict_edges,
            int(transformed["expected_row"]),
            transformed["expected_outer_pair"],
            transformed["expected_inner_pair"],
        )
        cycle_steps.append(
            {
                "strict_inequality": _edge_to_json(edge),
                "equality_to_next_outer_pair": transformed["equality_to_next_outer_pair"],
            }
        )
    _validate_transformed_cycle_steps(assignment["core_selected_rows"], cycle_steps)

    cycle_length = len(cycle_steps)
    connector_lengths = [
        len(step["equality_to_next_outer_pair"]["path"]) for step in cycle_steps
    ]
    edge_json = [step["strict_inequality"] for step in cycle_steps]
    return {
        "assignment_id": str(assignment["assignment_id"]),
        "family_id": family_id,
        "template_id": str(assignment["template_id"]),
        "status": "strict_cycle",
        "core_size": int(assignment["core_size"]),
        "strict_edge_count": int(result.strict_edge_count),
        "cycle_length": cycle_length,
        "connector_path_lengths": connector_lengths,
        "span_signature": _span_signature(edge_json),
        "to_canonical_label_map": [
            int(label) for label in assignment["to_canonical_label_map"]
        ],
        "core_selected_rows": assignment["core_selected_rows"],
        "cycle_steps": cycle_steps,
        "contradiction": {
            "kind": "strict_cycle",
            "statement": "strict inequalities form a directed cycle after selected-distance quotienting",
            "cycle_length": cycle_length,
        },
    }


def strict_cycle_path_join_source_artifacts(
    local_core_payload: dict[str, Any],
    classification_payload: dict[str, Any],
    template_payload: dict[str, Any],
    obstruction_shape_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return embedded source-artifact metadata for the strict-cycle join."""

    return [
        {
            "path": "data/certificates/n9_vertex_circle_local_cores.json",
            "role": "family representative strict-cycle inequalities and equality connectors",
            "type": local_core_payload.get("type"),
            "trust": local_core_payload.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_frontier_motif_classification.json",
            "role": "assignment-to-family label maps and transformed core rows",
            "schema": classification_payload.get("schema"),
            "status": classification_payload.get("status"),
            "trust": classification_payload.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_core_templates.json",
            "role": "strict-cycle local-core template ids and span summaries",
            "schema": template_payload.get("schema"),
            "status": template_payload.get("status"),
            "trust": template_payload.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_obstruction_shapes.json",
            "role": "first full-assignment strict-cycle length counts for diagnostic comparison",
            "type": obstruction_shape_payload.get("type"),
            "trust": obstruction_shape_payload.get("trust"),
        },
    ]


def strict_cycle_path_join_payload(
    local_core_payload: dict[str, Any],
    classification_payload: dict[str, Any],
    template_payload: dict[str, Any],
    obstruction_shape_payload: dict[str, Any],
) -> dict[str, Any]:
    """Return transformed strict-cycle records for all strict-cycle assignments."""

    certificates = _strict_cycle_certificates(local_core_payload)
    template_families = _template_family_rows(template_payload)
    records = []
    family_counts: Counter[str] = Counter()
    template_counts: Counter[str] = Counter()
    cycle_lengths: Counter[int] = Counter()
    core_sizes: Counter[int] = Counter()
    strict_edge_counts: Counter[int] = Counter()
    connector_lengths: Counter[int] = Counter()
    span_signatures: Counter[str] = Counter()
    family_rows: dict[str, dict[str, Any]] = {}

    for assignment in classification_payload["assignments"]:
        if assignment["status"] != "strict_cycle":
            continue
        family_id = str(assignment["family_id"])
        certificate = certificates[family_id]
        record = strict_cycle_path_join_record(assignment, certificate)
        template_family = template_families.get(family_id)
        if template_family is None:
            raise AssertionError(f"{family_id} missing from strict-cycle templates")
        _validate_template_family(record, template_family)
        family_counts[family_id] += 1
        template_id = str(record["template_id"])
        template_counts[template_id] += 1
        cycle_length = int(record["cycle_length"])
        core_size = int(record["core_size"])
        strict_edge_count = int(record["strict_edge_count"])
        cycle_lengths[cycle_length] += 1
        core_sizes[core_size] += 1
        strict_edge_counts[strict_edge_count] += 1
        span_signatures[str(record["span_signature"])] += 1
        connector_lengths.update(int(length) for length in record["connector_path_lengths"])
        family_rows[family_id] = {
            "assignment_count": int(family_counts[family_id]),
            "core_size": core_size,
            "cycle_length": cycle_length,
            "family_id": family_id,
            "orbit_size": int(certificate["orbit_size"]),
            "span_signature": str(record["span_signature"]),
            "status": "strict_cycle",
            "strict_edge_count": strict_edge_count,
            "template_id": template_id,
        }
        records.append(record)

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "cyclic_order": list(n9.ORDER),
        "source_assignment_count": int(classification_payload["assignment_count"]),
        "self_edge_assignment_count": int(
            classification_payload["status_counts"]["self_edge"]
        ),
        "strict_cycle_assignment_count": len(records),
        "strict_cycle_family_count": len(family_counts),
        "strict_cycle_template_count": len(template_counts),
        "cycle_step_count": sum(int(record["cycle_length"]) for record in records),
        "cycle_length_counts": {
            str(length): int(cycle_lengths[length]) for length in sorted(cycle_lengths)
        },
        "first_full_assignment_cycle_length_counts": obstruction_shape_payload[
            "strict_cycle_summary"
        ]["cycle_length_counts"],
        "core_size_assignment_counts": {
            str(size): int(core_sizes[size]) for size in sorted(core_sizes)
        },
        "strict_edge_count_assignment_counts": {
            str(count): int(strict_edge_counts[count])
            for count in sorted(strict_edge_counts)
        },
        "connector_path_length_counts": {
            str(length): int(connector_lengths[length])
            for length in sorted(connector_lengths)
        },
        "span_signature_counts": {
            signature: int(span_signatures[signature])
            for signature in sorted(span_signatures)
        },
        "family_assignment_counts": {
            family_id: int(family_counts[family_id]) for family_id in sorted(family_counts)
        },
        "template_assignment_counts": {
            template_id: int(template_counts[template_id])
            for template_id in sorted(template_counts)
        },
        "families": [family_rows[family_id] for family_id in sorted(family_rows)],
        "records": records,
        "interpretation": [
            "Each record transforms a strict-cycle family representative local-core certificate into one labelled n=9 frontier assignment.",
            "The transformed strict-cycle edges are replayed from the assignment's compact core rows.",
            "Connector paths identify each strict edge's inner pair with the next strict edge's outer pair.",
            "Cycle-length counts here summarize transformed local-core certificates, not first full-assignment obstruction-shape cycles.",
            "These records are compact replay aids and lemma-mining diagnostics, not theorem names.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_artifacts": strict_cycle_path_join_source_artifacts(
            local_core_payload,
            classification_payload,
            template_payload,
            obstruction_shape_payload,
        ),
        "provenance": PROVENANCE,
    }
    assert_expected_strict_cycle_path_join_counts(payload)
    return payload


def assert_expected_strict_cycle_path_join_counts(payload: dict[str, Any]) -> None:
    """Assert stable headline counts for the transformed strict-cycle join."""

    if payload["schema"] != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload['schema']}")
    if payload["status"] != STATUS:
        raise AssertionError(f"unexpected status: {payload['status']}")
    if payload["trust"] != TRUST:
        raise AssertionError(f"unexpected trust: {payload['trust']}")
    if payload["claim_scope"] != CLAIM_SCOPE:
        raise AssertionError("claim scope changed")
    if payload["n"] != n9.N or payload["row_size"] != n9.ROW_SIZE:
        raise AssertionError("unexpected n or row size")
    if payload["cyclic_order"] != list(n9.ORDER):
        raise AssertionError("unexpected cyclic order")
    if payload["source_assignment_count"] != EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS:
        raise AssertionError("unexpected source assignment count")
    if payload["self_edge_assignment_count"] != EXPECTED_SELF_EDGE_ASSIGNMENTS:
        raise AssertionError("unexpected self-edge assignment count")
    if payload["strict_cycle_assignment_count"] != EXPECTED_STRICT_CYCLE_ASSIGNMENTS:
        raise AssertionError("unexpected strict-cycle assignment count")
    if payload["strict_cycle_family_count"] != EXPECTED_STRICT_CYCLE_FAMILIES:
        raise AssertionError("unexpected strict-cycle family count")
    if payload["strict_cycle_template_count"] != EXPECTED_STRICT_CYCLE_TEMPLATES:
        raise AssertionError("unexpected strict-cycle template count")
    if payload["cycle_step_count"] != EXPECTED_CYCLE_STEP_COUNT:
        raise AssertionError("unexpected strict-cycle step count")
    if payload["cycle_length_counts"] != EXPECTED_CYCLE_LENGTH_COUNTS:
        raise AssertionError("unexpected cycle-length counts")
    if (
        payload["first_full_assignment_cycle_length_counts"]
        != EXPECTED_FIRST_FULL_ASSIGNMENT_CYCLE_LENGTH_COUNTS
    ):
        raise AssertionError("unexpected first full-assignment cycle-length counts")
    if payload["core_size_assignment_counts"] != EXPECTED_CORE_SIZE_COUNTS:
        raise AssertionError("unexpected core-size counts")
    if payload["strict_edge_count_assignment_counts"] != EXPECTED_STRICT_EDGE_COUNT_COUNTS:
        raise AssertionError("unexpected strict-edge-count distribution")
    if payload["connector_path_length_counts"] != EXPECTED_CONNECTOR_PATH_LENGTH_COUNTS:
        raise AssertionError("unexpected connector path-length counts")
    if payload["span_signature_counts"] != EXPECTED_SPAN_SIGNATURE_COUNTS:
        raise AssertionError("unexpected span-signature counts")
    if payload["family_assignment_counts"] != EXPECTED_FAMILY_ASSIGNMENT_COUNTS:
        raise AssertionError("unexpected family assignment counts")
    if payload["template_assignment_counts"] != EXPECTED_TEMPLATE_ASSIGNMENT_COUNTS:
        raise AssertionError("unexpected template assignment counts")
    if len(payload["families"]) != EXPECTED_STRICT_CYCLE_FAMILIES:
        raise AssertionError("unexpected family row count")
    if len(payload["records"]) != EXPECTED_STRICT_CYCLE_ASSIGNMENTS:
        raise AssertionError("unexpected record count")
    family_counts = {
        str(family["family_id"]): int(family["assignment_count"])
        for family in payload["families"]
    }
    if family_counts != EXPECTED_FAMILY_ASSIGNMENT_COUNTS:
        raise AssertionError("family rows do not match assignment counts")
