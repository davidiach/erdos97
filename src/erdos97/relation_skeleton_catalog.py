"""Build a small relation-skeleton catalog from focused local lemma packets.

This module is proof-mining scaffolding. It extracts a common typed view of
focused vertex-circle quotient obstructions. It does not prove the full
n=9 case, does not claim a counterexample, and does not update the global
status of Erdos Problem #97.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence


SCHEMA = "erdos97.relation_skeleton_catalog.v1"
STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Sixteen-entry relation-skeleton catalog for focused n=9 vertex-circle "
    "selected-distance quotient obstructions; proof-mining scaffolding only, "
    "not a proof of n=9, not a counterexample, not an independent review of "
    "the exhaustive checker, and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_relation_skeleton_catalog.py",
    "command": "python scripts/check_relation_skeleton_catalog.py --assert-expected --write",
}

SELF_EDGE_TEMPLATE_IDS = ("T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08", "T09")
STRICT_CYCLE_TEMPLATE_IDS = ("T10", "T11", "T12")
FOCUSED_TEMPLATE_IDS = (*SELF_EDGE_TEMPLATE_IDS, *STRICT_CYCLE_TEMPLATE_IDS)

EXPECTED_SKELETON_IDS = (
    "VC-T01-F09-strict-self-edge",
    "VC-T02-F01-strict-self-edge",
    "VC-T02-F04-strict-self-edge",
    "VC-T02-F08-strict-self-edge",
    "VC-T02-F14-strict-self-edge",
    "VC-T03-F05-strict-self-edge",
    "VC-T03-F15-strict-self-edge",
    "VC-T04-F13-strict-self-edge",
    "VC-T05-F10-strict-self-edge",
    "VC-T06-F11-strict-self-edge",
    "VC-T07-F06-strict-self-edge",
    "VC-T08-F02-strict-self-edge",
    "VC-T09-F03-strict-self-edge",
    "VC-T10-F12-strict-directed-cycle",
    "VC-T11-F07-strict-directed-cycle",
    "VC-T12-F16-strict-directed-cycle",
)
EXPECTED_CONTRADICTION_TYPE_COUNTS = {
    "strict_directed_cycle": 3,
    "strict_self_edge": 13,
}
EXPECTED_SOURCE_ARTIFACTS = (
    "data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json",
    "data/certificates/n9_vertex_circle_t02_self_edge_lemma_packet.json",
    "data/certificates/n9_vertex_circle_t03_self_edge_lemma_packet.json",
    "data/certificates/n9_vertex_circle_t04_self_edge_lemma_packet.json",
    "data/certificates/n9_vertex_circle_t05_self_edge_lemma_packet.json",
    "data/certificates/n9_vertex_circle_t06_self_edge_lemma_packet.json",
    "data/certificates/n9_vertex_circle_t07_self_edge_lemma_packet.json",
    "data/certificates/n9_vertex_circle_t08_self_edge_lemma_packet.json",
    "data/certificates/n9_vertex_circle_t09_self_edge_lemma_packet.json",
    "data/certificates/n9_vertex_circle_t10_strict_cycle_lemma_packet.json",
    "data/certificates/n9_vertex_circle_t11_strict_cycle_lemma_packet.json",
    "data/certificates/n9_vertex_circle_t12_strict_cycle_lemma_packet.json",
)
EXPECTED_FAMILY_DETAILS = {
    "VC-T01-F09-strict-self-edge": ("T01", "F09", "strict_self_edge", 6, 1),
    "VC-T02-F01-strict-self-edge": ("T02", "F01", "strict_self_edge", 18, 1),
    "VC-T02-F04-strict-self-edge": ("T02", "F04", "strict_self_edge", 18, 1),
    "VC-T02-F08-strict-self-edge": ("T02", "F08", "strict_self_edge", 2, 1),
    "VC-T02-F14-strict-self-edge": ("T02", "F14", "strict_self_edge", 2, 1),
    "VC-T03-F05-strict-self-edge": ("T03", "F05", "strict_self_edge", 18, 1),
    "VC-T03-F15-strict-self-edge": ("T03", "F15", "strict_self_edge", 2, 1),
    "VC-T04-F13-strict-self-edge": ("T04", "F13", "strict_self_edge", 2, 1),
    "VC-T05-F10-strict-self-edge": ("T05", "F10", "strict_self_edge", 18, 1),
    "VC-T06-F11-strict-self-edge": ("T06", "F11", "strict_self_edge", 18, 1),
    "VC-T07-F06-strict-self-edge": ("T07", "F06", "strict_self_edge", 18, 1),
    "VC-T08-F02-strict-self-edge": ("T08", "F02", "strict_self_edge", 18, 1),
    "VC-T09-F03-strict-self-edge": ("T09", "F03", "strict_self_edge", 18, 1),
    "VC-T10-F12-strict-directed-cycle": ("T10", "F12", "strict_directed_cycle", 18, 2),
    "VC-T11-F07-strict-directed-cycle": ("T11", "F07", "strict_directed_cycle", 6, 3),
    "VC-T12-F16-strict-directed-cycle": ("T12", "F16", "strict_directed_cycle", 2, 3),
}
DOES_NOT_PROVE = (
    "n=9",
    "Erdos Problem #97",
    "a counterexample",
    "independent review of the n=9 exhaustive checker",
)


def _source_artifact(path: str, role: str, packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": path,
        "role": role,
        "schema": packet.get("schema"),
        "status": packet.get("status"),
        "trust": packet.get("trust"),
    }


def _source_artifacts(focused_packets: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        _source_artifact(path, f"focused {template_id} local lemma packet", focused_packets[template_id])
        for template_id, path in zip(FOCUSED_TEMPLATE_IDS, EXPECTED_SOURCE_ARTIFACTS, strict=True)
    ]


def _coverage_from_t01(packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "assignment_count": int(packet["assignment_count"]),
        "assignment_ids": list(packet["assignment_ids"]),
        "family_count": int(packet["family_count"]),
        "families": [str(packet["family_id"])],
        "orbit_size_sum": int(packet["orbit_size"]),
    }


def _coverage_from_t10(packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "assignment_count": int(packet["assignment_count"]),
        "assignment_ids": list(packet["assignment_ids"]),
        "family_count": int(packet["family_count"]),
        "families": list(packet["family_ids"]),
        "orbit_size_sum": int(packet["orbit_size_sum"]),
    }


def _minimal_hypotheses(row_count: int) -> list[str]:
    return [
        "natural cyclic order on labels 0..8",
        f"the listed {row_count} selected rows are exact equidistant 4-tie rows",
        "strict convexity makes vertex-circle chord monotonicity applicable",
        "only the displayed local rows and quotient relations are used",
    ]


def _strict_edge_from_t01(packet: Mapping[str, Any]) -> dict[str, Any]:
    strict = packet["strict_inequality"]
    return {
        "source": "vertex_circle_chord_monotonicity",
        "row": int(strict["row"]),
        "witness_order": list(strict["witness_order"]),
        "outer_pair": list(strict["outer_pair"]),
        "inner_pair": list(strict["inner_pair"]),
        "outer_class": list(strict["outer_class"]),
        "inner_class": list(strict["inner_class"]),
        "outer_span": int(strict["outer_span"]),
        "inner_span": int(strict["inner_span"]),
    }


def _strict_edge_from_cycle_step(step: Mapping[str, Any]) -> dict[str, Any]:
    strict = step["strict_inequality"]
    return {
        "source": "vertex_circle_chord_monotonicity",
        "row": int(strict["row"]),
        "witness_order": list(strict["witness_order"]),
        "outer_pair": list(strict["outer_pair"]),
        "inner_pair": list(strict["inner_pair"]),
        "outer_class": list(strict["outer_class"]),
        "inner_class": list(strict["inner_class"]),
        "outer_span": int(strict["outer_span"]),
        "inner_span": int(strict["inner_span"]),
    }


def _t01_skeleton(packet: Mapping[str, Any]) -> dict[str, Any]:
    equality_steps = list(packet["local_lemma"]["selected_distance_equalities"])
    strict_edge = _strict_edge_from_t01(packet)
    return {
        "skeleton_id": EXPECTED_SKELETON_IDS[0],
        "source_packet": EXPECTED_SOURCE_ARTIFACTS[0],
        "source_template_id": str(packet["template_id"]),
        "source_family_id": str(packet["family_id"]),
        "obstruction_system": "vertex_circle_selected_distance_quotient",
        "contradiction_type": "strict_self_edge",
        "review_status": "review_pending",
        "coverage": _coverage_from_t01(packet),
        "hypotheses": {
            "cyclic_order": list(packet["cyclic_order"]),
            "selected_rows": list(packet["core_selected_rows"]),
            "minimal_local_hypotheses": _minimal_hypotheses(int(packet["core_size"])),
        },
        "relation_quotient": {
            "equality_steps": equality_steps,
            "equality_chains": [list(packet["equality_chain"])],
            "strict_edges": [strict_edge],
        },
        "conclusion": {
            "kind": "strict_self_edge",
            "quotient_class": strict_edge["outer_class"],
            "strict_from_pair": strict_edge["outer_pair"],
            "strict_to_pair": strict_edge["inner_pair"],
            "obstruction": "strict edge from a quotient class to itself",
            "contradiction_statement": str(packet["local_lemma"]["contradiction"]),
        },
        "verifier": "python scripts/check_relation_skeleton_catalog.py --check --assert-expected --json",
        "does_not_prove": list(DOES_NOT_PROVE),
    }


def _family_packets(packet: Mapping[str, Any], *, expected_template: str) -> list[Mapping[str, Any]]:
    family_packets = packet["family_packets"]
    if not isinstance(family_packets, list):
        raise ValueError(f"{expected_template} packet family_packets must be a list")
    if str(packet.get("template_id")) != expected_template:
        raise ValueError(f"expected template {expected_template}, got {packet.get('template_id')!r}")
    out = []
    for family_packet in family_packets:
        if not isinstance(family_packet, Mapping):
            raise ValueError(f"{expected_template} family packets must be mappings")
        out.append(family_packet)
    return out


def _coverage_from_family(family_packet: Mapping[str, Any]) -> dict[str, Any]:
    family_id = str(family_packet["family_id"])
    return {
        "assignment_count": int(family_packet["assignment_count"]),
        "family_count": 1,
        "families": [family_id],
        "orbit_size_sum": int(family_packet["orbit_size"]),
    }


def _strict_edge_from_self_edge_family(family_packet: Mapping[str, Any]) -> dict[str, Any]:
    strict = family_packet["strict_inequality"]
    return {
        "source": "vertex_circle_chord_monotonicity",
        "row": int(strict["row"]),
        "witness_order": list(strict["witness_order"]),
        "outer_pair": list(strict["outer_pair"]),
        "inner_pair": list(strict["inner_pair"]),
        "outer_class": list(strict["outer_class"]),
        "inner_class": list(strict["inner_class"]),
        "outer_span": int(strict["outer_span"]),
        "inner_span": int(strict["inner_span"]),
    }


def _self_edge_family_skeleton(
    *,
    packet: Mapping[str, Any],
    family_packet: Mapping[str, Any],
    source_packet: str,
) -> dict[str, Any]:
    template_id = str(packet["template_id"])
    family_id = str(family_packet["family_id"])
    strict_edge = _strict_edge_from_self_edge_family(family_packet)
    return {
        "skeleton_id": f"VC-{template_id}-{family_id}-strict-self-edge",
        "source_packet": source_packet,
        "source_template_id": template_id,
        "source_family_id": family_id,
        "obstruction_system": "vertex_circle_selected_distance_quotient",
        "contradiction_type": "strict_self_edge",
        "review_status": "review_pending",
        "coverage": _coverage_from_family(family_packet),
        "hypotheses": {
            "cyclic_order": list(packet["cyclic_order"]),
            "selected_rows": list(family_packet["core_selected_rows"]),
            "minimal_local_hypotheses": _minimal_hypotheses(int(family_packet["core_size"])),
        },
        "relation_quotient": {
            "equality_steps": list(family_packet["local_lemma"]["selected_distance_equalities"]),
            "equality_chains": [list(family_packet["equality_chain"])],
            "strict_edges": [strict_edge],
        },
        "conclusion": {
            "kind": "strict_self_edge",
            "quotient_class": strict_edge["outer_class"],
            "strict_from_pair": strict_edge["outer_pair"],
            "strict_to_pair": strict_edge["inner_pair"],
            "obstruction": "strict edge from a quotient class to itself",
            "contradiction_statement": str(family_packet["local_lemma"]["contradiction"]),
        },
        "verifier": "python scripts/check_relation_skeleton_catalog.py --check --assert-expected --json",
        "does_not_prove": list(DOES_NOT_PROVE),
    }


def _t10_family_packet(packet: Mapping[str, Any]) -> Mapping[str, Any]:
    family_packets = packet["family_packets"]
    if not isinstance(family_packets, Sequence) or len(family_packets) != 1:
        raise ValueError("T10 packet must contain exactly one family packet")
    family_packet = family_packets[0]
    if not isinstance(family_packet, Mapping):
        raise ValueError("T10 family packet must be a mapping")
    if family_packet.get("family_id") != "F12":
        raise ValueError("T10 family packet must be F12")
    return family_packet


def _cycle_steps(family_packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    steps = family_packet["cycle_steps"]
    if not isinstance(steps, list):
        raise ValueError("T10 cycle_steps must be a list")
    return steps


def _t10_quotient_cycle(family_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    quotient_cycle = []
    for chain in family_packet["cycle_pair_chain"]:
        quotient_cycle.append(
            {
                "cycle_step": int(chain["cycle_step"]),
                "strict_from_pair": list(chain["strict_from_outer_pair"]),
                "strict_to_pair": list(chain["strict_to_inner_pair"]),
                "equality_chain_to_next_outer_pair": list(
                    chain["equality_chain_to_next_outer_pair"]
                ),
                "next_outer_pair": list(chain["next_outer_pair"]),
            }
        )
    return quotient_cycle


def _t10_skeleton(packet: Mapping[str, Any]) -> dict[str, Any]:
    family_packet = _t10_family_packet(packet)
    steps = _cycle_steps(family_packet)
    strict_edges = [_strict_edge_from_cycle_step(step) for step in steps]
    return {
        "skeleton_id": "VC-T10-F12-strict-directed-cycle",
        "source_packet": EXPECTED_SOURCE_ARTIFACTS[9],
        "source_template_id": str(packet["template_id"]),
        "source_family_id": str(family_packet["family_id"]),
        "obstruction_system": "vertex_circle_selected_distance_quotient",
        "contradiction_type": "strict_directed_cycle",
        "review_status": "review_pending",
        "coverage": _coverage_from_t10(packet),
        "hypotheses": {
            "cyclic_order": list(packet["cyclic_order"]),
            "selected_rows": list(family_packet["core_selected_rows"]),
            "minimal_local_hypotheses": _minimal_hypotheses(int(family_packet["core_size"])),
        },
        "relation_quotient": {
            "equality_steps": list(family_packet["local_lemma"]["selected_distance_equalities"]),
            "equality_chains": [
                list(item["equality_chain_to_next_outer_pair"])
                for item in family_packet["cycle_pair_chain"]
            ],
            "strict_edges": strict_edges,
        },
        "conclusion": {
            "kind": "strict_directed_cycle",
            "cycle_length": int(family_packet["cycle_length"]),
            "quotient_cycle": _t10_quotient_cycle(family_packet),
            "obstruction": "directed strict cycle in the quotient graph",
            "contradiction_statement": str(family_packet["local_lemma"]["contradiction"]),
        },
        "verifier": "python scripts/check_relation_skeleton_catalog.py --check --assert-expected --json",
        "does_not_prove": list(DOES_NOT_PROVE),
    }


def _strict_cycle_family_skeleton(
    *,
    packet: Mapping[str, Any],
    family_packet: Mapping[str, Any],
    source_packet: str,
) -> dict[str, Any]:
    template_id = str(packet["template_id"])
    family_id = str(family_packet["family_id"])
    steps = _cycle_steps(family_packet)
    strict_edges = [_strict_edge_from_cycle_step(step) for step in steps]
    return {
        "skeleton_id": f"VC-{template_id}-{family_id}-strict-directed-cycle",
        "source_packet": source_packet,
        "source_template_id": template_id,
        "source_family_id": family_id,
        "obstruction_system": "vertex_circle_selected_distance_quotient",
        "contradiction_type": "strict_directed_cycle",
        "review_status": "review_pending",
        "coverage": _coverage_from_family(family_packet),
        "hypotheses": {
            "cyclic_order": list(packet["cyclic_order"]),
            "selected_rows": list(family_packet["core_selected_rows"]),
            "minimal_local_hypotheses": _minimal_hypotheses(int(family_packet["core_size"])),
        },
        "relation_quotient": {
            "equality_steps": list(family_packet["local_lemma"]["selected_distance_equalities"]),
            "equality_chains": [
                list(item["equality_chain_to_next_outer_pair"])
                for item in family_packet["cycle_pair_chain"]
            ],
            "strict_edges": strict_edges,
        },
        "conclusion": {
            "kind": "strict_directed_cycle",
            "cycle_length": int(family_packet["cycle_length"]),
            "quotient_cycle": _t10_quotient_cycle(family_packet),
            "obstruction": "directed strict cycle in the quotient graph",
            "contradiction_statement": str(family_packet["local_lemma"]["contradiction"]),
        },
        "verifier": "python scripts/check_relation_skeleton_catalog.py --check --assert-expected --json",
        "does_not_prove": list(DOES_NOT_PROVE),
    }


def relation_skeleton_catalog_payload(
    focused_packets: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Return the focused-packet relation-skeleton catalog."""

    for template_id in FOCUSED_TEMPLATE_IDS:
        packet = focused_packets[template_id]
        if str(packet.get("template_id")) != template_id:
            raise ValueError(f"expected {template_id} packet, got {packet.get('template_id')!r}")
    skeletons = [
        _t01_skeleton(focused_packets["T01"]),
        *(
            _self_edge_family_skeleton(
                packet=focused_packets[template_id],
                family_packet=family_packet,
                source_packet=EXPECTED_SOURCE_ARTIFACTS[FOCUSED_TEMPLATE_IDS.index(template_id)],
            )
            for template_id in SELF_EDGE_TEMPLATE_IDS[1:]
            for family_packet in _family_packets(focused_packets[template_id], expected_template=template_id)
        ),
        _t10_skeleton(focused_packets["T10"]),
        *(
            _strict_cycle_family_skeleton(
                packet=focused_packets[template_id],
                family_packet=family_packet,
                source_packet=EXPECTED_SOURCE_ARTIFACTS[FOCUSED_TEMPLATE_IDS.index(template_id)],
            )
            for template_id in STRICT_CYCLE_TEMPLATE_IDS[1:]
            for family_packet in _family_packets(focused_packets[template_id], expected_template=template_id)
        ),
    ]
    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "catalog_scope": "vertex-circle selected-distance quotient skeletons",
        "n": 9,
        "row_size": 4,
        "cyclic_order": list(range(9)),
        "skeleton_count": len(skeletons),
        "contradiction_type_counts": EXPECTED_CONTRADICTION_TYPE_COUNTS,
        "skeleton_ids": list(EXPECTED_SKELETON_IDS),
        "skeletons": skeletons,
        "interpretation": [
            "This catalog extracts relation skeletons from focused local lemma packets.",
            "Each entry separates selected-distance quotient equalities from vertex-circle strict inequalities.",
            "The catalog is intended to support reusable local-lemma review and bridge proof mining.",
            "No proof of the n=9 case is claimed.",
            "No proof of Erdos Problem #97 and no counterexample are claimed.",
        ],
        "source_artifacts": _source_artifacts(focused_packets),
        "provenance": PROVENANCE,
    }
    assert_expected_relation_skeleton_catalog(payload)
    return payload


def _skeletons_by_id(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    skeletons = payload.get("skeletons")
    if not isinstance(skeletons, list):
        raise AssertionError("skeletons must be a list")
    by_id = {
        str(skeleton["skeleton_id"]): skeleton
        for skeleton in skeletons
        if isinstance(skeleton, Mapping) and "skeleton_id" in skeleton
    }
    if set(by_id) != set(EXPECTED_SKELETON_IDS):
        raise AssertionError(f"unexpected skeleton ids: {sorted(by_id)!r}")
    return {skeleton_id: by_id[skeleton_id] for skeleton_id in EXPECTED_SKELETON_IDS}


def assert_expected_relation_skeleton_catalog(payload: Mapping[str, Any]) -> None:
    """Assert stable constants for the relation-skeleton catalog."""

    expected_top = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "catalog_scope": "vertex-circle selected-distance quotient skeletons",
        "n": 9,
        "row_size": 4,
        "cyclic_order": list(range(9)),
        "skeleton_count": len(EXPECTED_SKELETON_IDS),
        "contradiction_type_counts": EXPECTED_CONTRADICTION_TYPE_COUNTS,
        "skeleton_ids": list(EXPECTED_SKELETON_IDS),
        "provenance": PROVENANCE,
    }
    for key, expected in expected_top.items():
        if payload.get(key) != expected:
            raise AssertionError(f"{key} mismatch: expected {expected!r}, got {payload.get(key)!r}")

    skeletons = _skeletons_by_id(payload)
    t01 = skeletons[EXPECTED_SKELETON_IDS[0]]
    t10 = skeletons["VC-T10-F12-strict-directed-cycle"]

    if t01["contradiction_type"] != "strict_self_edge":
        raise AssertionError("T01 skeleton must be a strict self-edge")
    if t01["source_template_id"] != "T01" or t01["source_family_id"] != "F09":
        raise AssertionError("T01 skeleton source ids changed")
    if t01["coverage"]["assignment_count"] != 6:
        raise AssertionError("T01 skeleton assignment count changed")
    if t01["conclusion"]["kind"] != "strict_self_edge":
        raise AssertionError("T01 skeleton conclusion kind changed")
    if t01["conclusion"]["quotient_class"] != [0, 1]:
        raise AssertionError("T01 skeleton quotient class changed")
    if len(t01["relation_quotient"]["strict_edges"]) != 1:
        raise AssertionError("T01 skeleton must have one displayed strict edge")

    if t10["contradiction_type"] != "strict_directed_cycle":
        raise AssertionError("T10 skeleton must be a strict directed cycle")
    if t10["source_template_id"] != "T10" or t10["source_family_id"] != "F12":
        raise AssertionError("T10 skeleton source ids changed")
    if t10["coverage"]["assignment_count"] != 18:
        raise AssertionError("T10 skeleton assignment count changed")
    if t10["conclusion"]["kind"] != "strict_directed_cycle":
        raise AssertionError("T10 skeleton conclusion kind changed")
    if t10["conclusion"]["cycle_length"] != 2:
        raise AssertionError("T10 skeleton cycle length changed")
    if len(t10["relation_quotient"]["strict_edges"]) != 2:
        raise AssertionError("T10 skeleton must have two displayed strict edges")

    source_by_template = dict(zip(FOCUSED_TEMPLATE_IDS, EXPECTED_SOURCE_ARTIFACTS, strict=True))
    for skeleton_id, (template_id, *_rest) in EXPECTED_FAMILY_DETAILS.items():
        source_packet = source_by_template[template_id]
        if skeletons[skeleton_id]["source_packet"] != source_packet:
            raise AssertionError(f"{skeleton_id} source packet changed")

    for skeleton_id, (
        template_id,
        family_id,
        contradiction_type,
        assignment_count,
        strict_edge_count,
    ) in EXPECTED_FAMILY_DETAILS.items():
        skeleton = skeletons[skeleton_id]
        if skeleton["source_template_id"] != template_id or skeleton["source_family_id"] != family_id:
            raise AssertionError(f"{skeleton_id} source ids changed")
        if skeleton["contradiction_type"] != contradiction_type:
            raise AssertionError(f"{skeleton_id} contradiction type changed")
        if skeleton["coverage"]["assignment_count"] != assignment_count:
            raise AssertionError(f"{skeleton_id} assignment count changed")
        if len(skeleton["relation_quotient"]["strict_edges"]) != strict_edge_count:
            raise AssertionError(f"{skeleton_id} strict edge count changed")

    for skeleton in skeletons.values():
        if skeleton["review_status"] != "review_pending":
            raise AssertionError("all skeletons must remain review-pending")
        if skeleton["does_not_prove"] != list(DOES_NOT_PROVE):
            raise AssertionError("does_not_prove guardrail changed")
