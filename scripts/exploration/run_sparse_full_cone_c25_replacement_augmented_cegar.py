#!/usr/bin/env python3
"""Run 192-history C25 CEGAR with the selected width-four replacement seed.

This bounded follow-up activates the three transferred seeds, the persistent
width-four seed, and only the new width-four replacement selected by the
preceding compression. It blocks 192 known C25 order classes, measures fresh
transfer, and learns at most eight new exact full-cone certificate orbits.

This is a fixed-pattern finite diagnostic, not an all-order obstruction,
geometric realizability result, counterexample, or proof of Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
EXPLORATION = Path(__file__).resolve().parent
for path in (SCRIPTS, EXPLORATION):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_kalmanson_certificate import check_certificate_dict  # noqa: E402
from compress_sparse_full_cone_c25_selected_residual_augmented_escapes import (  # noqa: E402
    check_payload as check_compression_payload,
)
from probe_sparse_full_cone_small_templates import (  # noqa: E402
    dihedral_order_key,
)
import run_sparse_full_cone_c25_selected_residual_augmented_cegar as prior  # noqa: E402
from run_sparse_full_cone_seeded_cegar import (  # noqa: E402
    ClauseOrbit,
    build_clause_orbit,
    clause_matches,
    file_sha256,
    unique_clauses,
)


PATTERN = prior.PATTERN
DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_selected_residual_augmented_escape_compression_2026-07-30"
    / "summary.json"
)
DEFAULT_PROBE_ORDER_LIMIT = 16
DEFAULT_PROBE_MAX_ITERATIONS = 12_000
DEFAULT_FULL_CERTIFICATE_LIMIT = 8
DEFAULT_MAX_ITERATIONS = 12_000
DEFAULT_CONFLICT_CAP = 1_024
DEFAULT_RANDOM_SEED = 20_260_802
SELECTED_REPLACEMENT_SOURCE_TARGET_ID = "residual:2"
CERTIFICATE_LIMIT_STATUS = (
    "BOUNDED_C25_REPLACEMENT_AUGMENTED_CERTIFICATE_LIMIT_REACHED"
)
CONTINUE_DECISION = "COMPRESS_NEW_C25_REPLACEMENT_AUGMENTED_ESCAPES"
REVIEW_DECISION = "REVIEW_C25_REPLACEMENT_AUGMENTED_CEGAR"


def load_sources(
    source_path: Path,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    check_compression_payload(source)
    cegar_path = ROOT / str(source["source_artifact"])
    cegar = json.loads(cegar_path.read_text(encoding="utf-8"))
    prior.check_payload(cegar)
    old_compression_path = ROOT / str(
        cegar["source_residual_compression_artifact"]
    )
    (
        old_compression,
        parent,
        parent_source,
        augmentation,
        residual_compression,
        prior_cegar,
        transfer,
        first,
    ) = prior.load_sources(old_compression_path)
    return (
        source,
        cegar,
        old_compression,
        parent,
        parent_source,
        augmentation,
        residual_compression,
        prior_cegar,
        transfer,
        first,
    )


def blocked_history(
    cegar: Mapping[str, Any],
    parent: Mapping[str, Any],
    augmentation: Mapping[str, Any],
    prior_cegar: Mapping[str, Any],
    transfer: Mapping[str, Any],
    first: Mapping[str, Any],
) -> list[dict[str, object]]:
    history = prior.blocked_history(
        parent,
        augmentation,
        prior_cegar,
        transfer,
        first,
    )
    streams = (
        (
            "selected_residual_probe",
            "probe_model_index",
            cegar["counterfactual_probe"]["models"],
        ),
        (
            "selected_residual_escape",
            "model_index",
            cegar["seeded_cegar"]["models"],
        ),
    )
    for packet, index_key, models in streams:
        for model in models:
            index = int(model[index_key])
            history.append(
                {
                    "history_id": f"{packet}:{index}",
                    "packet": packet,
                    "order": [int(label) for label in model["order"]],
                    "order_sha256": str(model["order_sha256"]),
                    "dihedral_order_sha256": str(
                        model["dihedral_order_sha256"]
                    ),
                }
            )
    keys = {dihedral_order_key(row["order"]) for row in history}
    if len(history) != 192 or len(keys) != 192:
        raise AssertionError("replacement history must have 192 classes")
    return history


def replacement_record(
    row: Mapping[str, Any],
    orbit: ClauseOrbit,
) -> dict[str, object]:
    checked = check_certificate_dict(row["compressed_certificate"])
    if not checked.zero_sum_verified:
        raise AssertionError("replacement certificate failed exact replay")
    return {
        "seed_id": "replacement_escape_compressed:2",
        "seed_role": "EXACT_MINIMUM_FIVE_SEED_ESCAPE_COVER",
        "source_target_id": str(row["source_target_id"]),
        "source_model_index": int(row["source_model_index"]),
        "ordered_quad_count": int(row["compressed_unique_ordered_quad_count"]),
        "compressed_certificate_sha256": str(
            row["compressed_certificate_sha256"]
        ),
        "positive_inequalities": checked.positive_inequalities,
        "weight_sum": checked.weight_sum,
        "max_weight": checked.max_weight,
        "affine_clause_orbit": orbit.summary(),
    }


def seed_selection(
    source: Mapping[str, Any],
    cegar: Mapping[str, Any],
    old_compression: Mapping[str, Any],
    parent_source: Mapping[str, Any],
    residual_compression: Mapping[str, Any],
    transfer: Mapping[str, Any],
) -> tuple[
    list[dict[str, object]],
    dict[str, object],
    dict[str, object],
    list[ClauseOrbit],
    list[dict[str, object]],
]:
    (
        transferred,
        persistent,
        old_selected,
        old_active,
        inherited_inactive,
    ) = prior.seed_selection(
        old_compression,
        parent_source,
        residual_compression,
        transfer,
    )
    cover = source["run"]["coverage_comparison"][
        "minimum_affine_source_covers"
    ]["residual_targets"]
    if cover["selected_source_target_ids"] != [
        SELECTED_REPLACEMENT_SOURCE_TARGET_ID
    ]:
        raise AssertionError("replacement minimum cover drifted")
    rows = {
        str(row["source_target_id"]): row
        for row in source["run"]["compressed_models"]
    }
    selected = rows[SELECTED_REPLACEMENT_SOURCE_TARGET_ID]
    orbit = build_clause_orbit(
        PATTERN,
        int(selected["source_model_index"]),
        selected["compressed_certificate"],
    )
    if orbit.summary() != selected["affine_clause_orbit"]:
        raise AssertionError("replacement orbit drifted")
    active = [*old_active[:-1], orbit]
    if len({item.canonical_clause_sha256 for item in active}) != 5:
        raise AssertionError("replacement active orbit duplicated")
    inactive_new = [
        {
            "seed_id": f"replacement_escape_compressed:{row['source_model_index']}",
            "source_target_id": str(row["source_target_id"]),
            "source_model_index": int(row["source_model_index"]),
            "ordered_quad_count": int(
                row["compressed_unique_ordered_quad_count"]
            ),
            "compressed_certificate_sha256": str(
                row["compressed_certificate_sha256"]
            ),
            "inactive_reason": "NOT_SELECTED_BY_EXACT_MINIMUM_ESCAPE_COVER",
        }
        for row in rows.values()
        if str(row["source_target_id"])
        != SELECTED_REPLACEMENT_SOURCE_TARGET_ID
    ]
    old_inactive = {
        **old_selected,
        "inactive_reason": "ZERO_MARGINAL_TARGETS_OVER_FOUR_PARENT_SEEDS",
    }
    inactive = [*inherited_inactive, old_inactive, *inactive_new]
    if len(inactive) != 24:
        raise AssertionError("replacement inactive packet drifted")
    return (
        transferred,
        persistent,
        replacement_record(selected, orbit),
        active,
        inactive,
    )


def probe_comparison(
    models: Sequence[Mapping[str, Any]],
    parent_orbits: Sequence[ClauseOrbit],
    replacement: ClauseOrbit,
) -> dict[str, object]:
    active = [*parent_orbits, replacement]
    summaries = {
        "parent_four_seeds": prior.coverage_for(models, parent_orbits),
        "replacement_width4_only": prior.coverage_for(
            models,
            [replacement],
        ),
        "parent_plus_replacement": prior.coverage_for(models, active),
    }
    parent_ids = {
        int(model["probe_model_index"])
        for model in models
        if clause_matches(model["order"], parent_orbits)
    }
    replacement_ids = {
        int(model["probe_model_index"])
        for model in models
        if clause_matches(model["order"], [replacement])
    }
    return {
        **summaries,
        "replacement_covered_probe_model_indices": sorted(replacement_ids),
        "replacement_marginal_over_parent_probe_model_indices": sorted(
            replacement_ids - parent_ids
        ),
        "replacement_overlap_with_parent_probe_model_indices": sorted(
            replacement_ids & parent_ids
        ),
        "active_uncovered_probe_model_indices": sorted(
            set(range(len(models))) - (parent_ids | replacement_ids)
        ),
    }


def route_decision(
    probe: Mapping[str, Any],
    comparison: Mapping[str, Any],
    seeded: Mapping[str, Any],
) -> str:
    count = int(probe["inverse_pair_escape_order_count"])
    if (
        count > 0
        and int(
            comparison["parent_four_seeds"]["covered_probe_order_count"]
        )
        == count
        and int(
            comparison["replacement_width4_only"]["covered_probe_order_count"]
        )
        == count
        and not comparison[
            "replacement_marginal_over_parent_probe_model_indices"
        ]
        and int(seeded["new_full_certificate_count"])
        == DEFAULT_FULL_CERTIFICATE_LIMIT
        and seeded["status"] == CERTIFICATE_LIMIT_STATUS
        and all(
            "certificate" in model["full_kalmanson"]
            for model in seeded["models"]
        )
    ):
        return CONTINUE_DECISION
    return REVIEW_DECISION


def unpack_for_run(source_path: Path) -> tuple[Any, ...]:
    loaded = load_sources(source_path)
    (
        source,
        cegar,
        old_compression,
        parent,
        parent_source,
        augmentation,
        residual_compression,
        prior_cegar,
        transfer,
        first,
    ) = loaded
    history = blocked_history(
        cegar,
        parent,
        augmentation,
        prior_cegar,
        transfer,
        first,
    )
    seeds = seed_selection(
        source,
        cegar,
        old_compression,
        parent_source,
        residual_compression,
        transfer,
    )
    return (*loaded, history, *seeds)


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    unpacked = unpack_for_run(source_path)
    source, cegar = unpacked[:2]
    history = unpacked[10]
    transferred, persistent, replacement, active, inactive = unpacked[11:]
    probe, inverse = prior.collect_history_disjoint_probe(
        active,
        history,
        order_limit=args.probe_order_limit,
        max_iterations=args.probe_max_iterations,
        conflict_cap=args.conflict_cap,
        random_seed=args.random_seed,
    )
    comparison = probe_comparison(probe["models"], active[:-1], active[-1])
    seeded = prior.run_history_disjoint_seeded_cegar(
        active,
        history,
        inverse,
        full_certificate_limit=args.full_certificate_limit,
        max_iterations=args.max_iterations,
        conflict_cap=args.conflict_cap,
        random_seed=args.random_seed,
        certificate_limit_status=CERTIFICATE_LIMIT_STATUS,
    )
    decision = route_decision(probe, comparison, seeded)
    n, offsets = prior.PATTERNS[PATTERN]
    return {
        "type": "sparse_full_cone_c25_replacement_augmented_cegar_v1",
        "trust": "EXACT_CLAUSES_IN_BOUNDED_192_HISTORY_C25_CEGAR",
        "status": "BOUNDED_C25_WIDTH4_REPLACEMENT_AUGMENTED_CEGAR",
        "claim_scope": (
            "Five exact C25 seed orbits drive a bounded order CEGAR after 192 "
            "known order classes are blocked. Exact finite clauses only; not "
            "an all-order obstruction, geometric result, proof, counterexample, "
            "or official/global status update."
        ),
        "source_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_sha256": file_sha256(source_path),
        "configuration": {
            "pattern": PATTERN,
            "probe_order_limit": args.probe_order_limit,
            "probe_max_iterations": args.probe_max_iterations,
            "full_certificate_limit": args.full_certificate_limit,
            "max_iterations": args.max_iterations,
            "conflict_cap": args.conflict_cap,
            "random_seed": args.random_seed,
            "history_equivalence": "cyclic rotation and reversal",
            "active_seed_policy": (
                "four parent seeds plus selected width-four replacement only"
            ),
        },
        "pattern": PATTERN,
        "n": n,
        "circulant_offsets": list(offsets),
        "transferred_seed_templates": transferred,
        "selected_persistent_seed_template": persistent,
        "selected_replacement_seed_template": replacement,
        "inactive_seed_templates": inactive,
        "active_seed_orbit_count": len(active),
        "active_exact_affine_seed_image_count": sum(
            orbit.affine_map_count for orbit in active
        ),
        "unique_active_seed_orbit_clause_count": len(unique_clauses(active)),
        "blocked_history": {
            "order_count": len(history),
            "dihedral_order_count": len(
                {dihedral_order_key(row["order"]) for row in history}
            ),
            "packet_histogram": dict(
                sorted(Counter(row["packet"] for row in history).items())
            ),
            "identities": prior.history_identity(history),
        },
        "counterfactual_probe": probe,
        "counterfactual_seed_packet_coverage": comparison,
        "seeded_cegar": seeded,
        "decision": decision,
        "next_target": (
            "Compress the eight newly learned exact replacement-seed escapes "
            "and reassess marginal affine coverage before more order search."
        ),
    }


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    if payload["type"] != "sparse_full_cone_c25_replacement_augmented_cegar_v1":
        raise AssertionError("replacement artifact type drifted")
    n, offsets = prior.PATTERNS[PATTERN]
    if payload["pattern"] != PATTERN or int(payload["n"]) != n:
        raise AssertionError("replacement pattern drifted")
    if payload["circulant_offsets"] != list(offsets):
        raise AssertionError("replacement offsets drifted")
    source_path = ROOT / str(payload["source_artifact"])
    if source_path.resolve() != DEFAULT_SOURCE.resolve():
        raise AssertionError("replacement source artifact drifted")
    if file_sha256(source_path) != str(payload["source_sha256"]):
        raise AssertionError("replacement source hash drifted")
    unpacked = unpack_for_run(source_path)
    history = unpacked[10]
    transferred, persistent, replacement, active, inactive = unpacked[11:]
    expected_config = {
        "pattern": PATTERN,
        "probe_order_limit": DEFAULT_PROBE_ORDER_LIMIT,
        "probe_max_iterations": DEFAULT_PROBE_MAX_ITERATIONS,
        "full_certificate_limit": DEFAULT_FULL_CERTIFICATE_LIMIT,
        "max_iterations": DEFAULT_MAX_ITERATIONS,
        "conflict_cap": DEFAULT_CONFLICT_CAP,
        "random_seed": DEFAULT_RANDOM_SEED,
        "history_equivalence": "cyclic rotation and reversal",
        "active_seed_policy": (
            "four parent seeds plus selected width-four replacement only"
        ),
    }
    if payload["configuration"] != expected_config:
        raise AssertionError("replacement configuration drifted")
    expected_history = {
        "order_count": len(history),
        "dihedral_order_count": len(
            {dihedral_order_key(row["order"]) for row in history}
        ),
        "packet_histogram": dict(
            sorted(Counter(row["packet"] for row in history).items())
        ),
        "identities": prior.history_identity(history),
    }
    if payload["blocked_history"] != expected_history:
        raise AssertionError("replacement history drifted")
    if payload["transferred_seed_templates"] != transferred:
        raise AssertionError("replacement transferred seeds drifted")
    if payload["selected_persistent_seed_template"] != persistent:
        raise AssertionError("replacement persistent seed drifted")
    if payload["selected_replacement_seed_template"] != replacement:
        raise AssertionError("replacement selected seed drifted")
    if payload["inactive_seed_templates"] != inactive:
        raise AssertionError("replacement inactive seeds drifted")
    if int(payload["active_seed_orbit_count"]) != len(active):
        raise AssertionError("replacement active count drifted")
    if int(payload["active_exact_affine_seed_image_count"]) != sum(
        orbit.affine_map_count for orbit in active
    ):
        raise AssertionError("replacement active images drifted")
    if int(payload["unique_active_seed_orbit_clause_count"]) != len(
        unique_clauses(active)
    ):
        raise AssertionError("replacement active clauses drifted")
    probe = payload["counterfactual_probe"]
    inverse_count = prior.check_probe(
        probe,
        history,
        active,
        order_limit=DEFAULT_PROBE_ORDER_LIMIT,
        max_iterations=DEFAULT_PROBE_MAX_ITERATIONS,
        conflict_cap=DEFAULT_CONFLICT_CAP,
    )
    comparison = probe_comparison(probe["models"], active[:-1], active[-1])
    if payload["counterfactual_seed_packet_coverage"] != comparison:
        raise AssertionError("replacement coverage drifted")
    previous_status = prior.CERTIFICATE_LIMIT_STATUS
    prior.CERTIFICATE_LIMIT_STATUS = CERTIFICATE_LIMIT_STATUS
    try:
        audit = prior.check_seeded_cegar(
            payload["seeded_cegar"],
            history,
            active,
            initial_inverse_count=inverse_count,
            full_certificate_limit=DEFAULT_FULL_CERTIFICATE_LIMIT,
            max_iterations=DEFAULT_MAX_ITERATIONS,
            conflict_cap=DEFAULT_CONFLICT_CAP,
        )
    finally:
        prior.CERTIFICATE_LIMIT_STATUS = previous_status
    decision = route_decision(probe, comparison, payload["seeded_cegar"])
    if payload["decision"] != decision:
        raise AssertionError("replacement decision drifted")
    return {
        "status": "OK",
        "verified_blocked_history_orders": len(history),
        "verified_active_seed_certificates": len(active),
        "verified_inactive_seed_certificates": len(inactive),
        "verified_counterfactual_probe_orders": len(probe["models"]),
        "verified_new_exact_full_cone_certificates": audit[
            "verified_certificates"
        ],
        "verified_exact_affine_certificate_images": audit["verified_images"],
        "verified_new_unique_affine_orbit_clauses": audit[
            "verified_learned_clauses"
        ],
        "decision": decision,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--probe-order-limit", type=int, default=16)
    parser.add_argument("--probe-max-iterations", type=int, default=12_000)
    parser.add_argument("--full-certificate-limit", type=int, default=8)
    parser.add_argument("--max-iterations", type=int, default=12_000)
    parser.add_argument("--conflict-cap", type=int, default=1_024)
    parser.add_argument("--random-seed", type=int, default=DEFAULT_RANDOM_SEED)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check:
        path = args.check if args.check.is_absolute() else ROOT / args.check
        print(
            json.dumps(
                check_payload(json.loads(path.read_text(encoding="utf-8"))),
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    payload = build_payload(args)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.out:
        path = args.out if args.out.is_absolute() else ROOT / args.out
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        comparison = payload["counterfactual_seed_packet_coverage"]
        print(
            f"history={payload['blocked_history']['order_count']} "
            f"parent={comparison['parent_four_seeds']['covered_probe_order_count']}/16 "
            f"replacement={comparison['replacement_width4_only']['covered_probe_order_count']}/16 "
            f"marginal={len(comparison['replacement_marginal_over_parent_probe_model_indices'])} "
            f"certificates={payload['seeded_cegar']['new_full_certificate_count']} "
            f"decision={payload['decision']}"
        )
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
