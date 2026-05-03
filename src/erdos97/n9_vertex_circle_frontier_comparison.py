"""Compare n=9 vertex-circle local cores with larger frontier patterns."""

from __future__ import annotations

from itertools import combinations
from typing import Sequence

from erdos97.n9_vertex_circle_obstruction_shapes import (
    _distance_equality_path,
    _json_pair,
    local_core_summary,
    motif_family_summary,
)
from erdos97.search import built_in_patterns
from erdos97.vertex_circle_order_filter import StrictInequality, vertex_circle_order_obstruction

P18_CROSSING_COMPATIBLE_ORDER = [
    0,
    8,
    4,
    15,
    1,
    5,
    11,
    9,
    3,
    7,
    17,
    13,
    2,
    6,
    14,
    10,
    16,
    12,
]

C19_VERTEX_CIRCLE_ACYCLIC_ORDER = [
    18,
    10,
    7,
    17,
    6,
    3,
    5,
    9,
    14,
    11,
    2,
    13,
    4,
    16,
    12,
    15,
    0,
    8,
    1,
]

EXPECTED_EXACT_CORE_EMBEDDING_HITS = {
    "P18_parity_balanced": 0,
    "C19_skew": 0,
}
EXPECTED_P18_CORE_SIZE = 6
EXPECTED_P18_VERTEX_SUPPORT_SIZE = 14
EXPECTED_P18_STRICT_CYCLE_SPAN_SIGNATURE = [[2, 1], [3, 1]]


def _source_order_variants(vertices: Sequence[int]) -> list[list[int]]:
    ordered = sorted(vertices)
    return [ordered, list(reversed(ordered))]


def _cyclic_order_preserving_maps(
    source_vertices: Sequence[int],
    target_n: int,
):
    source_vertices = sorted(source_vertices)
    source_size = len(source_vertices)
    for target_subset in combinations(range(target_n), source_size):
        target_order = list(target_subset)
        for source_order in _source_order_variants(source_vertices):
            for shift in range(source_size):
                yield {
                    source_order[idx]: target_order[(idx + shift) % source_size]
                    for idx in range(source_size)
                }


def _core_vertex_support(certificate: dict[str, object]) -> set[int]:
    vertices: set[int] = set()
    for row in certificate["core_selected_rows"]:
        if not isinstance(row, dict):
            raise AssertionError("malformed core row")
        vertices.add(int(row["row"]))
        vertices.update(int(witness) for witness in row["witnesses"])
    return vertices


def _core_embeds_in_pattern(
    certificate: dict[str, object],
    target_rows: Sequence[Sequence[int]],
) -> tuple[bool, dict[int, int] | None, int]:
    core_rows = certificate["core_selected_rows"]
    source_vertices = _core_vertex_support(certificate)
    attempts = 0
    for label_map in _cyclic_order_preserving_maps(source_vertices, len(target_rows)):
        attempts += 1
        ok = True
        for row in core_rows:
            if not isinstance(row, dict):
                raise AssertionError("malformed core row")
            target_center = label_map[int(row["row"])]
            target_witnesses = {label_map[int(witness)] for witness in row["witnesses"]}
            if set(target_rows[target_center]) != target_witnesses:
                ok = False
                break
        if ok:
            return True, label_map, attempts
    return False, None, attempts


def _span_signature(edges: Sequence[StrictInequality]) -> list[list[int]]:
    return [
        [int(outer_span), int(inner_span)]
        for outer_span, inner_span in sorted(
            (
                edge.outer_interval[1] - edge.outer_interval[0],
                edge.inner_interval[1] - edge.inner_interval[0],
            )
            for edge in edges
        )
    ]


def _cycle_core(
    rows: Sequence[Sequence[int]],
    edges: Sequence[StrictInequality],
) -> dict[str, object]:
    core_rows = {edge.row for edge in edges}
    cycle_steps = []
    for idx, edge in enumerate(edges):
        next_edge = edges[(idx + 1) % len(edges)]
        equality_path = _distance_equality_path(rows, edge.inner_pair, next_edge.outer_pair)
        core_rows.update(int(step["row"]) for step in equality_path)
        cycle_steps.append(
            {
                "strict_row": int(edge.row),
                "outer_pair": _json_pair(edge.outer_pair),
                "inner_pair": _json_pair(edge.inner_pair),
                "outer_span": int(edge.outer_interval[1] - edge.outer_interval[0]),
                "inner_span": int(edge.inner_interval[1] - edge.inner_interval[0]),
                "equality_to_next_outer_pair": {
                    "start_pair": _json_pair(edge.inner_pair),
                    "end_pair": _json_pair(next_edge.outer_pair),
                    "path": equality_path,
                },
            }
        )
    vertex_support = set(core_rows)
    for row in core_rows:
        vertex_support.update(rows[row])
    return {
        "status": "strict_cycle",
        "cycle_length": len(edges),
        "span_signature": _span_signature(edges),
        "core_rows": [int(row) for row in sorted(core_rows)],
        "core_size": len(core_rows),
        "vertex_support": [int(vertex) for vertex in sorted(vertex_support)],
        "vertex_support_size": len(vertex_support),
        "cycle_steps": cycle_steps,
    }


def _pattern_vertex_circle_summary(
    name: str,
    rows: Sequence[Sequence[int]],
    order: Sequence[int],
    n9_strict_cycle_span_counts: dict[tuple[tuple[int, int], ...], int],
) -> dict[str, object]:
    result = vertex_circle_order_obstruction(rows, order, name)
    if not result.obstructed:
        return {
            "pattern": name,
            "obstructed": False,
            "status": "passes_vertex_circle_filter",
            "order": list(order),
        }
    if result.self_edge_conflicts:
        return {
            "pattern": name,
            "obstructed": True,
            "status": "self_edge",
            "order": list(order),
        }
    core = _cycle_core(rows, result.cycle_edges)
    span_key = tuple(tuple(item) for item in core["span_signature"])
    core.update(
        {
            "pattern": name,
            "obstructed": True,
            "order": list(order),
            "matching_n9_strict_cycle_span_bucket_count": n9_strict_cycle_span_counts.get(
                span_key,
                0,
            ),
        }
    )
    return core


def frontier_comparison_summary() -> dict[str, object]:
    """Return exact-embedding and loose-shape comparisons for frontier patterns."""
    local_payload = local_core_summary()
    motif_payload = motif_family_summary()
    certificates = local_payload["certificates"]
    patterns = built_in_patterns()
    target_specs = {
        "P18_parity_balanced": P18_CROSSING_COMPATIBLE_ORDER,
        "C19_skew": C19_VERTEX_CIRCLE_ACYCLIC_ORDER,
    }

    embedding_results = []
    for pattern_name, order in target_specs.items():
        rows = patterns[pattern_name].S
        hits = []
        attempts = 0
        for certificate in certificates:
            hit, label_map, certificate_attempts = _core_embeds_in_pattern(
                certificate,
                rows,
            )
            attempts += certificate_attempts
            if hit:
                hits.append(
                    {
                        "family_id": certificate["family_id"],
                        "status": certificate["status"],
                        "core_size": certificate["core_size"],
                        "label_map": {
                            str(source): int(target)
                            for source, target in sorted(label_map.items())
                        },
                    }
                )
        embedding_results.append(
            {
                "pattern": pattern_name,
                "order": list(order),
                "exact_core_embedding_hits": len(hits),
                "checked_core_count": len(certificates),
                "cyclic_order_preserving_maps_tested": attempts,
                "hits": hits,
            }
        )

    strict_cycle_span_counts = {}
    for bucket in motif_payload["loose_obstruction_shapes"]["strict_cycle_span_buckets"]:
        key = tuple(tuple(item) for item in bucket["span_signature"])
        strict_cycle_span_counts[key] = int(bucket["count"])

    pattern_summaries = [
        _pattern_vertex_circle_summary(
            "P18_parity_balanced",
            patterns["P18_parity_balanced"].S,
            P18_CROSSING_COMPATIBLE_ORDER,
            strict_cycle_span_counts,
        ),
        _pattern_vertex_circle_summary(
            "C19_skew",
            patterns["C19_skew"].S,
            C19_VERTEX_CIRCLE_ACYCLIC_ORDER,
            strict_cycle_span_counts,
        ),
    ]

    payload = {
        "type": "n9_vertex_circle_frontier_comparison_v1",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "scope": "Compare exact n=9 local cores with P18 and C19 frontier vertex-circle behavior.",
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "The official/global status remains falsifiable/open.",
            "Exact core embeddings require a cyclic-order-preserving injection whose selected rows match exactly.",
        ],
        "n9_local_core_artifact": "data/certificates/n9_vertex_circle_local_cores.json",
        "exact_core_embedding_results": embedding_results,
        "pattern_vertex_circle_results": pattern_summaries,
        "interpretation": [
            "No n=9 local core embeds exactly into the recorded P18 or C19 row systems under this strict row-preserving test.",
            "P18 is still killed by a local strict-cycle core of size 6, and its span signature matches an n=9 strict-cycle shape bucket.",
            "The recorded C19 order still passes the vertex-circle filter, so any global route needs an additional exact ingredient or a sharper vertex-circle condition.",
        ],
    }
    assert_expected_frontier_comparison(payload)
    return payload


def assert_expected_frontier_comparison(payload: dict[str, object]) -> None:
    """Assert expected frontier comparison counts."""
    embeddings = payload["exact_core_embedding_results"]
    if not isinstance(embeddings, list):
        raise AssertionError("missing embedding results")
    for result in embeddings:
        if not isinstance(result, dict):
            raise AssertionError("malformed embedding result")
        expected = EXPECTED_EXACT_CORE_EMBEDDING_HITS[result["pattern"]]
        if result["exact_core_embedding_hits"] != expected:
            raise AssertionError(f"unexpected embedding hits for {result['pattern']}")

    pattern_results = {
        result["pattern"]: result for result in payload["pattern_vertex_circle_results"]
    }
    p18 = pattern_results["P18_parity_balanced"]
    if not p18["obstructed"] or p18["status"] != "strict_cycle":
        raise AssertionError("P18 should have a strict-cycle obstruction")
    if p18["core_size"] != EXPECTED_P18_CORE_SIZE:
        raise AssertionError(f"unexpected P18 core size: {p18['core_size']}")
    if p18["vertex_support_size"] != EXPECTED_P18_VERTEX_SUPPORT_SIZE:
        raise AssertionError("unexpected P18 vertex support size")
    if p18["span_signature"] != EXPECTED_P18_STRICT_CYCLE_SPAN_SIGNATURE:
        raise AssertionError("unexpected P18 span signature")
    if p18["matching_n9_strict_cycle_span_bucket_count"] <= 0:
        raise AssertionError("P18 span signature should appear among n=9 buckets")

    c19 = pattern_results["C19_skew"]
    if c19["obstructed"] or c19["status"] != "passes_vertex_circle_filter":
        raise AssertionError("C19 recorded order should pass vertex-circle filter")
