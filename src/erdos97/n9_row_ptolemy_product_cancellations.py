"""n=9 row-Ptolemy product-cancellation diagnostics.

This module sweeps the 184 complete n=9 selected-witness assignments that
survive the pair/crossing/count filters before vertex-circle obstruction. It
records where a fixed-row-order Ptolemy cancellation gives an independent exact
obstruction. It does not prove the n=9 case and does not claim a
counterexample.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence

from erdos97 import n9_vertex_circle_exhaustive as n9
from erdos97.incidence_filters import row_ptolemy_product_cancellation_certificates
from erdos97.n9_vertex_circle_obstruction_shapes import (
    _rows_from_assignment,
    canonical_dihedral_rows,
    pre_vertex_circle_assignments,
)

SCHEMA = "erdos97.n9_row_ptolemy_product_cancellations.v2"
STATUS = "EXPLORATORY_LEDGER_ONLY"
TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
CLAIM_SCOPE = (
    "Focused n=9 row-Ptolemy product-cancellation bookkeeping for the "
    "fixed natural cyclic order; not a proof of n=9, not a counterexample, "
    "not a geometric realizability test, and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/analyze_n9_row_ptolemy_product_cancellations.py",
    "command": (
        "python scripts/analyze_n9_row_ptolemy_product_cancellations.py "
        "--assert-expected --out "
        "data/certificates/n9_row_ptolemy_product_cancellations.json"
    ),
}
TEMPLATE_CROSSWALK_SOURCE_PATH = (
    "data/certificates/n9_vertex_circle_core_templates.json"
)
TEMPLATE_CROSSWALK_CLAIM_SCOPE = (
    "Diagnostic join from row-Ptolemy hit families to review-pending n=9 "
    "vertex-circle local-core template labels; not a proof of n=9, not a "
    "counterexample, and not a global status update."
)

EXPECTED_PRE_VERTEX_CIRCLE_NODES = 100_817
EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS = 184
EXPECTED_HIT_ASSIGNMENTS = 26
EXPECTED_HIT_CERTIFICATES = 216
EXPECTED_HIT_FAMILIES = 3
EXPECTED_HIT_ASSIGNMENT_STATUS_COUNTS = {"self_edge": 26}
EXPECTED_HIT_FAMILY_COUNTS = {"F02": 18, "F09": 6, "F13": 2}
EXPECTED_CERTIFICATE_COUNT_BY_CENTER = {str(center): 24 for center in range(n9.N)}
EXPECTED_CERTIFICATES_PER_HIT_ASSIGNMENT = {"6": 18, "12": 6, "18": 2}
EXPECTED_HIT_FAMILY_TEMPLATE_IDS = {"F02": "T08", "F09": "T01", "F13": "T04"}
EXPECTED_HIT_TEMPLATE_ASSIGNMENT_COUNTS = {"T01": 6, "T04": 2, "T08": 18}
EXPECTED_HIT_TEMPLATE_CERTIFICATE_COUNTS = {"T01": 72, "T04": 36, "T08": 108}
EXPECTED_HIT_TEMPLATE_STATUS_COUNTS = {"self_edge": 3}
EXPECTED_NONHIT_TEMPLATE_IDS = [
    "T02",
    "T03",
    "T05",
    "T06",
    "T07",
    "T09",
    "T10",
    "T11",
    "T12",
]
EXPECTED_NONHIT_FAMILY_COUNT = 13
EXPECTED_NONHIT_FAMILY_ORBIT_SIZE_SUM = 158
EXPECTED_STRICT_CYCLE_HIT_FAMILY_COUNT = 0
EXPECTED_STRICT_CYCLE_NONHIT_FAMILY_COUNT = 3


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _family_labels(
    rows_by_assignment: Sequence[Sequence[Sequence[int]]],
) -> tuple[dict[tuple[tuple[int, ...], ...], str], dict[str, int]]:
    families: dict[tuple[tuple[int, ...], ...], int] = defaultdict(int)
    for rows in rows_by_assignment:
        families[canonical_dihedral_rows(rows)] += 1

    key_to_family: dict[tuple[tuple[int, ...], ...], str] = {}
    family_orbit_sizes: dict[str, int] = {}
    for family_index, (family_key, orbit_size) in enumerate(
        sorted(families.items()),
        start=1,
    ):
        family_id = f"F{family_index:02d}"
        key_to_family[family_key] = family_id
        family_orbit_sizes[family_id] = int(orbit_size)
    return key_to_family, family_orbit_sizes


def _hit_record(
    assignment_index: int,
    rows: Sequence[Sequence[int]],
    family_id: str,
    family_orbit_size: int,
    status: str,
    certificates: Sequence[dict[str, object]],
) -> dict[str, object]:
    return {
        "assignment_index": int(assignment_index),
        "family_id": family_id,
        "family_orbit_size": int(family_orbit_size),
        "vertex_circle_status": status,
        "selected_rows": [[int(label) for label in row] for row in rows],
        "certificate_count": len(certificates),
        "certificates": list(certificates),
    }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_template_payload() -> dict[str, Any]:
    path = _repo_root() / TEMPLATE_CROSSWALK_SOURCE_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{TEMPLATE_CROSSWALK_SOURCE_PATH} is not a JSON object")
    return payload


def _template_crosswalk(
    *,
    template_payload: dict[str, Any],
    hit_records: Sequence[dict[str, object]],
) -> dict[str, object]:
    families = template_payload.get("families")
    templates = template_payload.get("templates")
    if not isinstance(families, list) or not isinstance(templates, list):
        raise ValueError("template payload must contain family and template rows")
    families_by_id = {
        str(family["family_id"]): family
        for family in families
        if isinstance(family, dict) and "family_id" in family
    }
    templates_by_id = {
        str(template["template_id"]): template
        for template in templates
        if isinstance(template, dict) and "template_id" in template
    }

    hit_assignment_counts = Counter(str(record["family_id"]) for record in hit_records)
    hit_certificate_counts: Counter[str] = Counter()
    for record in hit_records:
        hit_certificate_counts[str(record["family_id"])] += int(record["certificate_count"])

    hit_family_rows = []
    template_assignment_counts: Counter[str] = Counter()
    template_certificate_counts: Counter[str] = Counter()
    hit_family_template_ids: dict[str, str] = {}
    for family_id in sorted(hit_assignment_counts):
        family = families_by_id[family_id]
        template_id = str(family["template_id"])
        template = templates_by_id[template_id]
        hit_count = int(hit_assignment_counts[family_id])
        certificate_count = int(hit_certificate_counts[family_id])
        template_assignment_counts[template_id] += hit_count
        template_certificate_counts[template_id] += certificate_count
        hit_family_template_ids[family_id] = template_id
        hit_family_rows.append(
            {
                "family_id": family_id,
                "template_id": template_id,
                "template_status": str(family["status"]),
                "template_core_size": int(family["core_size"]),
                "template_strict_edge_count": int(family["strict_edge_count"]),
                "family_orbit_size": int(family["orbit_size"]),
                "hit_assignment_count": hit_count,
                "hit_certificate_count": certificate_count,
                "certificate_count_per_hit_assignment": certificate_count // hit_count,
                "template_family_count": int(template["family_count"]),
                "template_orbit_size_sum": int(template["orbit_size_sum"]),
            }
        )

    template_status_counts = Counter(
        str(templates_by_id[template_id]["status"])
        for template_id in template_assignment_counts
    )
    hit_template_rows = []
    for template_id in sorted(template_assignment_counts):
        template = templates_by_id[template_id]
        hit_template_rows.append(
            {
                "template_id": template_id,
                "template_status": str(template["status"]),
                "families": sorted(
                    family_id
                    for family_id, row_template_id in hit_family_template_ids.items()
                    if row_template_id == template_id
                ),
                "hit_family_count": sum(
                    1
                    for row_template_id in hit_family_template_ids.values()
                    if row_template_id == template_id
                ),
                "hit_assignment_count": int(template_assignment_counts[template_id]),
                "hit_certificate_count": int(template_certificate_counts[template_id]),
            }
        )

    all_family_ids = set(families_by_id)
    hit_family_ids = set(hit_family_template_ids)
    nonhit_family_ids = sorted(all_family_ids - hit_family_ids)
    nonhit_template_ids = sorted(
        {str(families_by_id[family_id]["template_id"]) for family_id in nonhit_family_ids}
    )
    strict_cycle_hit_family_count = sum(
        1
        for family_id in hit_family_ids
        if families_by_id[family_id]["status"] == "strict_cycle"
    )
    strict_cycle_nonhit_family_count = sum(
        1
        for family_id in nonhit_family_ids
        if families_by_id[family_id]["status"] == "strict_cycle"
    )

    return {
        "claim_scope": TEMPLATE_CROSSWALK_CLAIM_SCOPE,
        "source_artifact": {
            "path": TEMPLATE_CROSSWALK_SOURCE_PATH,
            "schema": template_payload.get("schema"),
            "status": template_payload.get("status"),
            "trust": template_payload.get("trust"),
        },
        "hit_template_count": len(template_assignment_counts),
        "hit_family_template_ids": hit_family_template_ids,
        "hit_template_assignment_counts": {
            template_id: int(template_assignment_counts[template_id])
            for template_id in sorted(template_assignment_counts)
        },
        "hit_template_certificate_counts": {
            template_id: int(template_certificate_counts[template_id])
            for template_id in sorted(template_certificate_counts)
        },
        "hit_template_status_counts": {
            status: int(template_status_counts[status])
            for status in sorted(template_status_counts)
        },
        "strict_cycle_hit_family_count": strict_cycle_hit_family_count,
        "nonhit_family_count": len(nonhit_family_ids),
        "nonhit_family_orbit_size_sum": sum(
            int(families_by_id[family_id]["orbit_size"])
            for family_id in nonhit_family_ids
        ),
        "strict_cycle_nonhit_family_count": strict_cycle_nonhit_family_count,
        "nonhit_template_ids": nonhit_template_ids,
        "hit_family_rows": hit_family_rows,
        "hit_template_rows": hit_template_rows,
    }


def row_ptolemy_product_cancellation_report() -> dict[str, object]:
    """Return the stable n=9 row-Ptolemy product-cancellation artifact."""

    assignments, nodes = pre_vertex_circle_assignments()
    rows_by_assignment = [_rows_from_assignment(assign) for assign in assignments]
    family_labels, family_orbit_sizes = _family_labels(rows_by_assignment)

    hit_records: list[dict[str, object]] = []
    status_counts: Counter[str] = Counter()
    family_hit_counts: Counter[str] = Counter()
    certificate_count_by_center: Counter[int] = Counter()
    certificates_per_hit: Counter[int] = Counter()
    total_certificates = 0

    for assignment_index, (assign, rows) in enumerate(
        zip(assignments, rows_by_assignment),
    ):
        certificates = row_ptolemy_product_cancellation_certificates(
            rows,
            n9.ORDER,
        )
        if not certificates:
            continue

        family_key = canonical_dihedral_rows(rows)
        family_id = family_labels[family_key]
        status = n9.vertex_circle_status(assign)
        status_counts[status] += 1
        family_hit_counts[family_id] += 1
        certificates_per_hit[len(certificates)] += 1
        total_certificates += len(certificates)
        for certificate in certificates:
            certificate_count_by_center[int(certificate["row"])] += 1
        hit_records.append(
            _hit_record(
                assignment_index,
                rows,
                family_id,
                family_orbit_sizes[family_id],
                status,
                certificates,
            )
        )
    template_payload = _load_template_payload()
    template_crosswalk = _template_crosswalk(
        template_payload=template_payload,
        hit_records=hit_records,
    )

    hit_family_rows = [
        {
            "family_id": family_id,
            "hit_assignment_count": int(family_hit_counts[family_id]),
            "family_orbit_size": int(family_orbit_sizes[family_id]),
        }
        for family_id in sorted(family_hit_counts)
    ]

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n9.N,
        "witness_size": n9.ROW_SIZE,
        "cyclic_order": list(n9.ORDER),
        "source_frontier": {
            "description": (
                "Complete n=9 assignments after pair/crossing/count filters "
                "and before vertex-circle obstruction."
            ),
            "row0_choices": len(n9.OPTIONS[0]),
            "nodes_visited": int(nodes),
            "assignment_count": len(assignments),
            "dihedral_family_count": len(family_orbit_sizes),
        },
        "filter": {
            "name": "row_ptolemy_product_cancel",
            "historical_alias": "F15 row-Ptolemy symmetric quad",
            "fixed_order_requirement": (
                "The row witness cyclic order must be supplied or certified; "
                "the selected-distance quotient alone is not an orderless "
                "abstract-incidence obstruction."
            ),
            "trigger": "d02=d23 and d13=d01 for row witnesses w0,w1,w2,w3",
            "ptolemy_identity": "d02*d13 = d01*d23 + d03*d12",
            "cancellation_conclusion": "d03*d12 = 0",
        },
        "hit_summary": {
            "hit_assignment_count": len(hit_records),
            "hit_certificate_count": int(total_certificates),
            "hit_family_count": len(family_hit_counts),
            "hit_assignment_vertex_circle_status_counts": dict(
                sorted(status_counts.items()),
            ),
            "hit_family_counts": hit_family_rows,
            "certificate_count_by_center": _json_counter(certificate_count_by_center),
            "certificates_per_hit_assignment_counts": _json_counter(
                certificates_per_hit,
            ),
        },
        "hit_records": hit_records,
        "interpretation": [
            "Each recorded hit is an exact obstruction for one fixed selected-witness assignment under the natural cyclic order.",
            "The proof uses Ptolemy on a row witness circle plus exact selected-distance quotient equalities.",
            "The filter kills 26 of the 184 n=9 pre-vertex-circle assignments, covering 3 of the 16 deterministic dihedral family labels.",
            "For this n=9 frontier, every hit is also a vertex-circle self-edge case; this diagnostic does not dominate or replace the vertex-circle checker.",
            "The template crosswalk only joins deterministic artifact labels; template ids are not theorem names.",
            "The row order must be supplied or certified. This is not an orderless abstract-incidence obstruction.",
            "No proof of the n=9 case is claimed.",
        ],
        "template_crosswalk": template_crosswalk,
        "source_artifacts": [
            {
                "path": "data/certificates/n9_vertex_circle_exhaustive.json",
                "role": "review-pending source frontier count target",
            },
            {
                "path": "data/certificates/n9_vertex_circle_motif_families.json",
                "role": "deterministic family-id convention used for F02/F09/F13 labels",
            },
            {
                "path": TEMPLATE_CROSSWALK_SOURCE_PATH,
                "role": "review-pending local-core template labels used for the diagnostic crosswalk",
            },
            {
                "path": "data/runs/2026-05-05/new_obstructions.md",
                "role": "archived exploratory memo for the historical F15 alias",
            },
        ],
        "provenance": PROVENANCE,
    }
    assert_expected_counts(payload)
    return payload


def assert_expected_counts(payload: dict[str, object]) -> None:
    """Assert stable headline counts for the n=9 cancellation report."""

    source = payload["source_frontier"]
    summary = payload["hit_summary"]
    if not isinstance(source, dict) or not isinstance(summary, dict):
        raise AssertionError("malformed row-Ptolemy product-cancellation payload")

    if source["nodes_visited"] != EXPECTED_PRE_VERTEX_CIRCLE_NODES:
        raise AssertionError(f"unexpected source nodes: {source['nodes_visited']}")
    if source["assignment_count"] != EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS:
        raise AssertionError(
            f"unexpected source assignments: {source['assignment_count']}",
        )
    if summary["hit_assignment_count"] != EXPECTED_HIT_ASSIGNMENTS:
        raise AssertionError(
            f"unexpected hit assignments: {summary['hit_assignment_count']}",
        )
    if summary["hit_certificate_count"] != EXPECTED_HIT_CERTIFICATES:
        raise AssertionError(
            f"unexpected hit certificates: {summary['hit_certificate_count']}",
        )
    if summary["hit_family_count"] != EXPECTED_HIT_FAMILIES:
        raise AssertionError(f"unexpected hit families: {summary['hit_family_count']}")
    if (
        summary["hit_assignment_vertex_circle_status_counts"]
        != EXPECTED_HIT_ASSIGNMENT_STATUS_COUNTS
    ):
        raise AssertionError("unexpected hit status counts")

    actual_family_counts = {
        str(row["family_id"]): int(row["hit_assignment_count"])
        for row in summary["hit_family_counts"]
        if isinstance(row, dict)
    }
    if actual_family_counts != EXPECTED_HIT_FAMILY_COUNTS:
        raise AssertionError(f"unexpected hit family counts: {actual_family_counts}")
    if summary["certificate_count_by_center"] != EXPECTED_CERTIFICATE_COUNT_BY_CENTER:
        raise AssertionError("unexpected certificate center counts")
    if (
        summary["certificates_per_hit_assignment_counts"]
        != EXPECTED_CERTIFICATES_PER_HIT_ASSIGNMENT
    ):
        raise AssertionError("unexpected certificate-per-hit histogram")

    crosswalk = payload.get("template_crosswalk")
    if not isinstance(crosswalk, dict):
        raise AssertionError("missing template crosswalk")
    if crosswalk.get("claim_scope") != TEMPLATE_CROSSWALK_CLAIM_SCOPE:
        raise AssertionError("unexpected template crosswalk claim scope")
    if crosswalk.get("hit_template_count") != len(EXPECTED_HIT_TEMPLATE_ASSIGNMENT_COUNTS):
        raise AssertionError("unexpected hit template count")
    if crosswalk.get("hit_family_template_ids") != EXPECTED_HIT_FAMILY_TEMPLATE_IDS:
        raise AssertionError("unexpected hit family/template ids")
    if (
        crosswalk.get("hit_template_assignment_counts")
        != EXPECTED_HIT_TEMPLATE_ASSIGNMENT_COUNTS
    ):
        raise AssertionError("unexpected hit template assignment counts")
    if (
        crosswalk.get("hit_template_certificate_counts")
        != EXPECTED_HIT_TEMPLATE_CERTIFICATE_COUNTS
    ):
        raise AssertionError("unexpected hit template certificate counts")
    if crosswalk.get("hit_template_status_counts") != EXPECTED_HIT_TEMPLATE_STATUS_COUNTS:
        raise AssertionError("unexpected hit template status counts")
    if (
        crosswalk.get("strict_cycle_hit_family_count")
        != EXPECTED_STRICT_CYCLE_HIT_FAMILY_COUNT
    ):
        raise AssertionError("unexpected strict-cycle hit family count")
    if crosswalk.get("nonhit_family_count") != EXPECTED_NONHIT_FAMILY_COUNT:
        raise AssertionError("unexpected nonhit family count")
    if (
        crosswalk.get("nonhit_family_orbit_size_sum")
        != EXPECTED_NONHIT_FAMILY_ORBIT_SIZE_SUM
    ):
        raise AssertionError("unexpected nonhit family orbit-size sum")
    if (
        crosswalk.get("strict_cycle_nonhit_family_count")
        != EXPECTED_STRICT_CYCLE_NONHIT_FAMILY_COUNT
    ):
        raise AssertionError("unexpected strict-cycle nonhit family count")
    if crosswalk.get("nonhit_template_ids") != EXPECTED_NONHIT_TEMPLATE_IDS:
        raise AssertionError("unexpected nonhit template ids")
