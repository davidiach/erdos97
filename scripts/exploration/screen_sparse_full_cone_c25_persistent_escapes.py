#!/usr/bin/env python3
"""Exactly screen the two persistent C25 transfer-CEGAR probe escapes.

The residual-seed augmentation packet leaves the original transfer-CEGAR
``probe:0`` and ``probe:1`` orders outside all three transferred and eight
compressed residual seed orbits.  This script classifies exactly those two
fixed orders against the complete fixed-order Kalmanson row family.

The LP is used only to find candidate witnesses.  Stored results are accepted
only when the checker replays either an exact positive integer zero-sum
certificate or an exact integer Gordan separating potential.  Every claim is
therefore bounded to the fixed C25 selected-witness pattern and the two listed
cyclic orders; no all-order obstruction, geometric realizability result,
counterexample, or proof of Erdos Problem #97 is claimed.
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
from compress_sparse_full_cone_certificates import (  # noqa: E402
    positive_circuit_audit,
)
from kalmanson_order_utils import all_kalmanson_rows  # noqa: E402
from pilot_sparse_full_cone_order_cegar import (  # noqa: E402
    PATTERNS,
    certificate_order_quads,
)
from probe_sparse_full_cone_c25_residual_seed_augmentation import (  # noqa: E402
    check_payload as check_augmentation_payload,
    check_source_chain_references,
    model_packet_matches,
    packet_definitions,
    seed_packets,
)
from run_sparse_full_cone_c25_transfer_cegar import (  # noqa: E402
    PATTERN,
    check_order_record,
)
from run_sparse_full_cone_seeded_cegar import (  # noqa: E402
    file_sha256,
)
from screen_sparse_full_cone_fresh_orders import (  # noqa: E402
    classify_order,
    separator_audit,
    stable_json_sha256,
)


DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_residual_seed_probe_2026-07-29"
    / "summary.json"
)
DEFAULT_TARGET_INDICES = (0, 1)


def load_source(
    source_path: Path,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    """Replay the augmentation artifact and return its direct source chain."""

    augmentation = json.loads(source_path.read_text(encoding="utf-8"))
    check_augmentation_payload(augmentation)
    compression, cegar, transfer, first = check_source_chain_references(augmentation)
    return augmentation, compression, cegar, transfer


def target_models(
    cegar: Mapping[str, Any],
    target_indices: Sequence[int],
) -> list[dict[str, Any]]:
    """Select the requested transfer-CEGAR counterfactual probe models."""

    by_index = {
        int(model["probe_model_index"]): model
        for model in cegar["counterfactual_probe"]["models"]
    }
    if len(by_index) != len(cegar["counterfactual_probe"]["models"]):
        raise AssertionError("C25 transfer-CEGAR probe indices are duplicated")
    requested = [int(index) for index in target_indices]
    if len(set(requested)) != len(requested):
        raise ValueError("target probe indices must be distinct")
    missing = [index for index in requested if index not in by_index]
    if missing:
        raise ValueError(f"unknown C25 transfer-CEGAR probe indices: {missing}")
    return [by_index[index] for index in requested]


def reconstruct_seed_packets(
    compression: Mapping[str, Any],
    transfer: Mapping[str, Any],
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, list[Any]],
]:
    """Replay the three transferred and eight residual exact seed orbits."""

    (
        transferred_records,
        transferred_orbits,
        residual_records,
        residual_orbits,
    ) = seed_packets(compression, transfer)
    packets = packet_definitions(
        transferred_orbits,
        residual_records,
        residual_orbits,
    )
    return transferred_records, residual_records, packets


def target_seed_audit(
    model: Mapping[str, Any],
    packets: Mapping[str, Sequence[Any]],
) -> dict[str, object]:
    """Replay the target order and its exact absence from every seed packet."""

    n, offsets = PATTERNS[PATTERN]
    order = check_order_record(model, n=n, offsets=offsets)
    if not bool(model["lightweight_filters"]["survives"]):
        raise AssertionError("persistent C25 target no longer survives light filters")
    if model["seed_orbit_matches"]:
        raise AssertionError("persistent C25 target matches a transferred source seed")
    matches = model_packet_matches(order, packets)
    all_matches = matches["transferred_plus_all_residuals"]
    if all_matches:
        raise AssertionError("persistent C25 target matches an augmented seed orbit")
    return {
        "source_transferred_seed_orbit_matches": model["seed_orbit_matches"],
        "seed_packet_matches": matches,
        "all_eleven_seed_orbit_match_count": len(all_matches),
    }


def classify_target(
    model: Mapping[str, Any],
    packets: Mapping[str, Sequence[Any]],
    *,
    tolerance: float,
    retry_count: int,
    retry_seed: int,
    max_separator_denominator: int,
) -> dict[str, object]:
    """Run the established exact Gordan-alternative classifier on one target."""

    adapted = dict(model)
    adapted["fresh_model_index"] = int(model["probe_model_index"])
    record = classify_order(
        PATTERN,
        adapted,
        tolerance=tolerance,
        retry_count=retry_count,
        retry_seed=retry_seed,
        max_separator_denominator=max_separator_denominator,
    )
    probe_model_index = int(record.pop("fresh_model_index"))
    return {
        "target_id": f"probe:{probe_model_index}",
        "probe_model_index": probe_model_index,
        **target_seed_audit(model, packets),
        **record,
    }


def classification_decision(records: Sequence[Mapping[str, Any]]) -> str:
    classifications = Counter(str(record["classification"]) for record in records)
    if classifications["UNRESOLVED_NUMERICAL_SCREEN"]:
        return "STOP_FOR_UNRESOLVED_EXACT_CLASSIFICATION"
    if classifications["EXACT_INTEGER_SEPARATING_POTENTIAL"]:
        return "INVESTIGATE_EXACT_FIXED_ORDER_CONE_ESCAPE"
    if classifications["EXACT_POSITIVE_ZERO_SUM_CERTIFICATE"] == len(records):
        return "CONTINUE_C25_CLAUSE_ROUTE_WITH_EXACT_POSITIVE_CIRCUITS"
    raise AssertionError("unexpected persistent-escape classification mix")


def screen_summary(records: Sequence[Mapping[str, Any]]) -> dict[str, object]:
    classifications = Counter(str(record["classification"]) for record in records)
    widths = Counter(
        int(record["unique_ordered_quad_count"])
        for record in records
        if record["classification"] == "EXACT_POSITIVE_ZERO_SUM_CERTIFICATE"
    )
    supports = Counter(
        int(record["positive_inequalities"])
        for record in records
        if record["classification"] == "EXACT_POSITIVE_ZERO_SUM_CERTIFICATE"
    )
    return {
        "selected_target_order_count": len(records),
        "exact_positive_certificate_count": classifications[
            "EXACT_POSITIVE_ZERO_SUM_CERTIFICATE"
        ],
        "exact_separating_potential_count": classifications[
            "EXACT_INTEGER_SEPARATING_POTENTIAL"
        ],
        "unresolved_numerical_screen_count": classifications[
            "UNRESOLVED_NUMERICAL_SCREEN"
        ],
        "classification_histogram": {
            key: classifications[key] for key in sorted(classifications)
        },
        "certificate_unique_quad_count_histogram": {
            str(key): widths[key] for key in sorted(widths)
        },
        "certificate_positive_inequality_count_histogram": {
            str(key): supports[key] for key in sorted(supports)
        },
        "minimum_certificate_unique_quad_count": min(widths, default=None),
        "maximum_certificate_unique_quad_count": max(widths, default=None),
        "minimum_certificate_positive_inequality_count": min(supports, default=None),
        "maximum_certificate_positive_inequality_count": max(supports, default=None),
    }


def seed_summary(
    transferred_records: Sequence[Mapping[str, Any]],
    residual_records: Sequence[Mapping[str, Any]],
    packets: Mapping[str, Sequence[Any]],
) -> dict[str, object]:
    all_orbits = packets["transferred_plus_all_residuals"]
    return {
        "transferred_seed_orbit_count": len(transferred_records),
        "compressed_residual_seed_orbit_count": len(residual_records),
        "all_seed_orbit_count": len(all_orbits),
        "all_seed_exact_affine_image_count": sum(
            int(orbit.affine_map_count) for orbit in all_orbits
        ),
        "transferred_seed_widths": [
            int(record["ordered_quad_count"]) for record in transferred_records
        ],
        "compressed_residual_seed_widths": [
            int(record["ordered_quad_count"]) for record in residual_records
        ],
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    augmentation, compression, cegar, transfer = load_source(source_path)
    selected = target_models(cegar, args.target_index)
    transferred_records, residual_records, packets = reconstruct_seed_packets(
        compression,
        transfer,
    )
    records = []
    for ordinal, model in enumerate(selected):
        retry_seed = args.retry_seed + ordinal * args.target_seed_stride
        records.append(
            classify_target(
                model,
                packets,
                tolerance=args.tolerance,
                retry_count=args.retry_count,
                retry_seed=retry_seed,
                max_separator_denominator=args.max_separator_denominator,
            )
        )
    n, offsets = PATTERNS[PATTERN]
    return {
        "type": "sparse_full_cone_c25_persistent_escape_screen_v1",
        "trust": "EXACT_FIXED_ORDER_FULL_CONE_CLASSIFICATION_FOR_TWO_C25_TARGETS",
        "status": "BOUNDED_TWO_ORDER_C25_FULL_CONE_SCREEN",
        "claim_scope": (
            "Exact Gordan-alternative classification of transfer-CEGAR "
            "counterfactual probe orders 0 and 1 for the fixed "
            "C25_sidon_2_5_9_14 selected-witness pattern. The targets are "
            "replayed outside all three transferred and eight compressed "
            "residual seed orbits. Each conclusive record stores either an "
            "exact positive Kalmanson zero-sum certificate or an exact integer "
            "separating potential. This is not an all-order obstruction, a "
            "geometric realizability result, a proof of Erdos Problem #97, a "
            "counterexample, or an official/global status update."
        ),
        "source_augmentation_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_augmentation_sha256": file_sha256(source_path),
        "source_cegar_artifact": str(augmentation["source_cegar_artifact"]),
        "source_cegar_sha256": str(augmentation["source_cegar_sha256"]),
        "pattern": PATTERN,
        "n": n,
        "circulant_offsets": list(offsets),
        "configuration": {
            "target_probe_model_indices": [
                int(index) for index in args.target_index
            ],
            "selection": (
                "the two predeclared original transfer-CEGAR probe escapes "
                "outside all eleven stored seed orbits"
            ),
            "tolerance": args.tolerance,
            "retry_count": args.retry_count,
            "retry_seed": args.retry_seed,
            "target_seed_stride": args.target_seed_stride,
            "max_separator_denominator": args.max_separator_denominator,
        },
        "seed_packet_summary": seed_summary(
            transferred_records,
            residual_records,
            packets,
        ),
        "records": records,
        "summary": screen_summary(records),
        "decision": classification_decision(records),
        "next_target": (
            "Compress the two new exact positive circuits and test their "
            "quotient-preserving affine orbits before extending C25 cyclic-order "
            "search limits."
        ),
    }


def check_positive_record(
    record: Mapping[str, Any],
    order: Sequence[int],
) -> None:
    certificate = record["certificate"]
    checked = check_certificate_dict(certificate)
    if not checked.zero_sum_verified:
        raise AssertionError("persistent C25 positive certificate failed")
    if certificate["cyclic_order"] != list(order):
        raise AssertionError("persistent C25 certificate order drifted")
    if stable_json_sha256(certificate) != record["certificate_sha256"]:
        raise AssertionError("persistent C25 certificate hash drifted")
    quads = certificate_order_quads(certificate, order)
    if len(quads) != int(record["unique_ordered_quad_count"]):
        raise AssertionError("persistent C25 certificate width drifted")
    if checked.positive_inequalities != int(record["positive_inequalities"]):
        raise AssertionError("persistent C25 certificate support drifted")
    if checked.weight_sum != int(record["weight_sum"]):
        raise AssertionError("persistent C25 certificate weight sum drifted")
    if checked.max_weight != int(record["max_weight"]):
        raise AssertionError("persistent C25 certificate max weight drifted")
    circuit_audit = positive_circuit_audit(certificate)
    if circuit_audit != record["positive_circuit_audit"]:
        raise AssertionError("persistent C25 circuit audit drifted")
    if not bool(circuit_audit["positive_circuit_verified"]):
        raise AssertionError("persistent C25 certificate is not a circuit")


def check_separator_record(
    record: Mapping[str, Any],
    order: Sequence[int],
) -> None:
    n, offsets = PATTERNS[PATTERN]
    rows = all_kalmanson_rows(n, offsets, order)
    potential = [int(value) for value in record["separating_potential"]]
    if stable_json_sha256(potential) != record["separator_sha256"]:
        raise AssertionError("persistent C25 separator hash drifted")
    audit = separator_audit(rows, potential)
    if audit != record["separator_audit"]:
        raise AssertionError("persistent C25 separator audit drifted")
    if not bool(audit["all_row_dots_strictly_positive"]):
        raise AssertionError("persistent C25 separator is not strict")


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    if payload["type"] != "sparse_full_cone_c25_persistent_escape_screen_v1":
        raise AssertionError("persistent C25 screen artifact type drifted")
    source_path = ROOT / str(payload["source_augmentation_artifact"])
    if file_sha256(source_path) != str(payload["source_augmentation_sha256"]):
        raise AssertionError("persistent C25 augmentation source hash drifted")
    augmentation, compression, cegar, transfer = load_source(source_path)
    if payload["source_cegar_artifact"] != augmentation["source_cegar_artifact"]:
        raise AssertionError("persistent C25 CEGAR source path drifted")
    if payload["source_cegar_sha256"] != augmentation["source_cegar_sha256"]:
        raise AssertionError("persistent C25 CEGAR source hash drifted")

    n, offsets = PATTERNS[PATTERN]
    if payload["pattern"] != PATTERN or int(payload["n"]) != n:
        raise AssertionError("persistent C25 pattern metadata drifted")
    if payload["circulant_offsets"] != list(offsets):
        raise AssertionError("persistent C25 offsets drifted")

    configuration = payload["configuration"]
    indices = [int(index) for index in configuration["target_probe_model_indices"]]
    if indices != list(DEFAULT_TARGET_INDICES):
        raise AssertionError("persistent C25 target selection drifted")
    selected = target_models(cegar, indices)
    transferred_records, residual_records, packets = reconstruct_seed_packets(
        compression,
        transfer,
    )
    expected_seed_summary = seed_summary(
        transferred_records,
        residual_records,
        packets,
    )
    if payload["seed_packet_summary"] != expected_seed_summary:
        raise AssertionError("persistent C25 seed summary drifted")

    records = payload["records"]
    if len(records) != len(selected):
        raise AssertionError("persistent C25 record count drifted")
    verified_certificates = 0
    verified_separators = 0
    verified_unresolved = 0
    for record, model in zip(records, selected, strict=True):
        model_index = int(model["probe_model_index"])
        if int(record["probe_model_index"]) != model_index:
            raise AssertionError("persistent C25 target index drifted")
        if record["target_id"] != f"probe:{model_index}":
            raise AssertionError("persistent C25 target id drifted")
        order = check_order_record(model, n=n, offsets=offsets)
        if record["order"] != order:
            raise AssertionError("persistent C25 target order drifted")
        for field in ("order_sha256", "dihedral_order_sha256"):
            if record[field] != model[field]:
                raise AssertionError(f"persistent C25 {field} drifted")
        expected_seed_audit = target_seed_audit(model, packets)
        for field, value in expected_seed_audit.items():
            if record[field] != value:
                raise AssertionError(f"persistent C25 {field} drifted")

        classification = str(record["classification"])
        if classification == "EXACT_POSITIVE_ZERO_SUM_CERTIFICATE":
            check_positive_record(record, order)
            verified_certificates += 1
        elif classification == "EXACT_INTEGER_SEPARATING_POTENTIAL":
            check_separator_record(record, order)
            verified_separators += 1
        elif classification == "UNRESOLVED_NUMERICAL_SCREEN":
            verified_unresolved += 1
        else:
            raise AssertionError("persistent C25 classification drifted")

    if payload["summary"] != screen_summary(records):
        raise AssertionError("persistent C25 screen summary drifted")
    decision = classification_decision(records)
    if payload["decision"] != decision:
        raise AssertionError("persistent C25 screen decision drifted")
    return {
        "status": "OK",
        "verified_target_orders": len(records),
        "verified_exact_positive_certificates": verified_certificates,
        "verified_exact_integer_separators": verified_separators,
        "recorded_unresolved_numerical_screens": verified_unresolved,
        "verified_seed_orbits": int(expected_seed_summary["all_seed_orbit_count"]),
        "verified_exact_affine_seed_images": int(
            expected_seed_summary["all_seed_exact_affine_image_count"]
        ),
        "decision": decision,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument(
        "--target-index",
        type=int,
        action="append",
        default=None,
        help="transfer-CEGAR counterfactual probe index; defaults to 0 and 1",
    )
    parser.add_argument("--tolerance", type=float, default=1.0e-9)
    parser.add_argument("--retry-count", type=int, default=16)
    parser.add_argument("--retry-seed", type=int, default=20260730)
    parser.add_argument("--target-seed-stride", type=int, default=1_000)
    parser.add_argument("--max-separator-denominator", type=int, default=1_000_000)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.target_index is None:
        args.target_index = list(DEFAULT_TARGET_INDICES)
    return args


def main() -> int:
    args = parse_args()
    positive = (
        args.tolerance,
        args.retry_count,
        args.target_seed_stride,
        args.max_separator_denominator,
    )
    if any(value <= 0 for value in positive):
        raise SystemExit(
            "tolerance, retries, seed stride, and denominator must be positive"
        )
    if args.check is not None:
        payload = json.loads(args.check.read_text(encoding="utf-8"))
        print(json.dumps(check_payload(payload), indent=2, sort_keys=True))
        return 0

    payload = build_payload(args)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8", newline="\n")
    if args.json or args.out is None:
        print(text, end="")
    else:
        summary = payload["summary"]
        print(
            f"selected={summary['selected_target_order_count']} "
            f"certificates={summary['exact_positive_certificate_count']} "
            f"separators={summary['exact_separating_potential_count']} "
            f"unresolved={summary['unresolved_numerical_screen_count']} "
            f"decision={payload['decision']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
