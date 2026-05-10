"""Row-pressure diagnostic for the bootstrap/T12 forcing target.

This module refines the T12 forcing-target ledger by asking how each missing
T12/F16 row center sits relative to the bootstrap core, deletion closures, and
private halos.  It is proof-mining bookkeeping only: it does not prove that
any missing row is forced.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_forcing_targets import build_t12_forcing_targets_payload
from erdos97.bootstrap_vertex_circle_overlay import build_overlay_payload


SCHEMA = "erdos97.bootstrap_t12_row_pressure.v1"
STATUS = "BOOTSTRAP_T12_ROW_PRESSURE_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Row-pressure diagnostic for the two tight n=9 bootstrap/T12 records; "
    "classifies missing T12/F16 row centers by bootstrap-core witness count, "
    "deletion-closure exposure, and private-halo support only. This does not "
    "prove that the missing rows are forced, does not prove n=9, does not "
    "prove the bridge, and does not claim a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = REPO_ROOT / "data" / "certificates" / "bootstrap_t12_row_pressure.json"


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _pair(values: Sequence[Any]) -> tuple[int, int]:
    a, b = int(values[0]), int(values[1])
    if a == b:
        raise ValueError("pair endpoints must be distinct")
    return tuple(sorted((a, b)))


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _closure_labels(n: int, core_vertex: int, private_halo: Iterable[Any]) -> list[int]:
    return sorted(set(range(n)) - {int(core_vertex)} - set(_int_list(private_halo)))


def _private_pair_index(
    private_pair_records: Sequence[Mapping[str, Any]],
) -> dict[tuple[int, int], list[int]]:
    index: defaultdict[tuple[int, int], set[int]] = defaultdict(set)
    for record in private_pair_records:
        index[_pair(record["pair"])].add(int(record["core_vertex"]))
    return {pair: sorted(core_vertices) for pair, core_vertices in sorted(index.items())}


def _outside_support_subsets(outside_witnesses: Sequence[int], deficit: int) -> list[list[int]]:
    if deficit <= 0:
        return []
    return [list(combo) for combo in combinations(sorted(outside_witnesses), deficit)]


def _support_hits(
    *,
    support_subsets: Sequence[Sequence[int]],
    deletion_closures: Sequence[Mapping[str, Any]],
    private_pair_records: Sequence[Mapping[str, Any]],
) -> list[dict[str, object]]:
    pair_index = _private_pair_index(private_pair_records)
    out = []
    for support in support_subsets:
        support_set = set(_int_list(support))
        halo_core_vertices = [
            int(closure["core_vertex"])
            for closure in deletion_closures
            if support_set <= set(_int_list(closure["private_halo"]))
        ]
        ledger_core_vertices: list[int] = []
        if len(support_set) == 2:
            ledger_core_vertices = pair_index.get(_pair(sorted(support_set)), [])
        out.append(
            {
                "support": sorted(support_set),
                "private_halo_core_vertices": sorted(halo_core_vertices),
                "private_halo_containment_count": len(halo_core_vertices),
                "ledger_private_pair_core_vertices": ledger_core_vertices,
                "ledger_private_pair_hit": bool(ledger_core_vertices),
            }
        )
    return out


def _deletion_closure_exposures(
    *,
    n: int,
    row_center: int,
    witnesses: Sequence[int],
    deletion_closures: Sequence[Mapping[str, Any]],
) -> list[dict[str, object]]:
    witness_set = set(witnesses)
    out = []
    for closure in deletion_closures:
        closure_labels = _closure_labels(n, int(closure["core_vertex"]), closure["private_halo"])
        closure_set = set(closure_labels)
        witnesses_in_closure = sorted(witness_set & closure_set)
        private_witnesses = sorted(witness_set & set(_int_list(closure["private_halo"])))
        center_in_closure = row_center in closure_set
        witness_count = len(witnesses_in_closure)
        out.append(
            {
                "core_vertex": int(closure["core_vertex"]),
                "deletion_seed": _int_list(closure["deletion_seed"]),
                "closure_labels": closure_labels,
                "closure_size": int(closure["closure_size"]),
                "row_center_in_closure": center_in_closure,
                "witnesses_in_closure": witnesses_in_closure,
                "witness_count_in_closure": witness_count,
                "private_witnesses": private_witnesses,
                "activation_ready_in_closure": witness_count >= 3,
                "row_exposed_in_closure": center_in_closure and witness_count >= 3,
            }
        )
    return out


def _pressure_class(
    *,
    exposed_deletion_core_vertices: Sequence[int],
    activation_deficit_from_core: int,
) -> str:
    if exposed_deletion_core_vertices:
        return "ALREADY_PRESENT_IN_A_DELETION_CLOSURE"
    if activation_deficit_from_core <= 0:
        return "CORE_SUFFICIENT_BUT_ROW_CENTER_PRIVATE"
    if activation_deficit_from_core == 1:
        return "NEEDS_ONE_OUTSIDE_LABEL_AND_PRIVATE_CENTER"
    if activation_deficit_from_core == 2:
        return "NEEDS_OUTSIDE_PAIR_AND_PRIVATE_CENTER"
    return "NEEDS_OUTSIDE_TRIPLE_AND_PRIVATE_CENTER"


def _row_pressure_record(
    *,
    target_record: Mapping[str, Any],
    gap: Mapping[str, Any],
    overlay_record: Mapping[str, Any],
) -> dict[str, object]:
    source_id = int(target_record["source_record_id"])
    n = int(overlay_record["n"])
    row_center = int(gap["center"])
    witnesses = _int_list(gap["witnesses"])
    bootstrap_core = set(_int_list(target_record["bootstrap_core"]))
    outside = set(_int_list(target_record["outside"]))
    core_witnesses = sorted(set(witnesses) & bootstrap_core)
    outside_witnesses = sorted(set(witnesses) & outside)
    activation_deficit = max(0, 3 - len(core_witnesses))
    support_subsets = _outside_support_subsets(outside_witnesses, activation_deficit)
    deletion_closures = overlay_record["deletion_closures"]
    exposures = _deletion_closure_exposures(
        n=n,
        row_center=row_center,
        witnesses=witnesses,
        deletion_closures=deletion_closures,
    )
    exposed_core_vertices = [
        int(exposure["core_vertex"])
        for exposure in exposures
        if exposure["row_exposed_in_closure"]
    ]
    support_hits = _support_hits(
        support_subsets=support_subsets,
        deletion_closures=deletion_closures,
        private_pair_records=target_record["private_pair_records"],
    )
    ledger_private_pair_hits = [
        hit for hit in support_hits if bool(hit["ledger_private_pair_hit"])
    ]
    center_private_core_vertices = [
        int(closure["core_vertex"])
        for closure in deletion_closures
        if row_center in set(_int_list(closure["private_halo"]))
    ]
    pressure_class = _pressure_class(
        exposed_deletion_core_vertices=exposed_core_vertices,
        activation_deficit_from_core=activation_deficit,
    )
    return {
        "source_record_id": source_id,
        "classification_assignment_id": target_record["classification_assignment_id"],
        "row_center": row_center,
        "roles": gap["roles"],
        "witnesses": witnesses,
        "bootstrap_core_witnesses": core_witnesses,
        "outside_witnesses": outside_witnesses,
        "bootstrap_core_witness_count": len(core_witnesses),
        "activation_deficit_from_bootstrap_core": activation_deficit,
        "outside_support_subsets": support_subsets,
        "outside_support_kind": (
            "core_sufficient"
            if activation_deficit == 0
            else f"outside_{activation_deficit}_set"
        ),
        "support_hits": support_hits,
        "ledger_private_pair_support_hits": ledger_private_pair_hits,
        "ledger_private_pair_support_hit_count": len(ledger_private_pair_hits),
        "deletion_closure_exposures": exposures,
        "exposed_deletion_core_vertices": exposed_core_vertices,
        "max_witness_count_in_deletion_closure": max(
            int(exposure["witness_count_in_closure"]) for exposure in exposures
        ),
        "row_center_private_core_vertices": sorted(center_private_core_vertices),
        "row_center_private_in_all_deletion_closures": len(center_private_core_vertices)
        == len(deletion_closures),
        "pressure_class": pressure_class,
    }


def build_t12_row_pressure_payload() -> dict[str, object]:
    """Return the deterministic bootstrap/T12 row-pressure payload."""

    targets = build_t12_forcing_targets_payload()
    overlay = build_overlay_payload()
    overlay_by_source = {
        int(record["source_record_id"]): record for record in overlay["records"]
    }

    row_records = []
    for target_record in targets["records"]:
        source_id = int(target_record["source_record_id"])
        overlay_record = overlay_by_source[source_id]
        for gap in target_record["row_gaps"]:
            row_records.append(
                _row_pressure_record(
                    target_record=target_record,
                    gap=gap,
                    overlay_record=overlay_record,
                )
            )
    row_records.sort(key=lambda record: (int(record["source_record_id"]), int(record["row_center"])))

    pressure_counts = Counter(str(record["pressure_class"]) for record in row_records)
    deficit_counts = Counter(
        int(record["activation_deficit_from_bootstrap_core"]) for record in row_records
    )
    support_kind_counts = Counter(str(record["outside_support_kind"]) for record in row_records)
    rows_by_source: defaultdict[int, list[int]] = defaultdict(list)
    exposed_rows_by_source: defaultdict[int, list[int]] = defaultdict(list)
    private_center_rows_by_source: defaultdict[int, list[int]] = defaultdict(list)
    ledger_pair_support_rows_by_source: defaultdict[int, list[int]] = defaultdict(list)
    for record in row_records:
        source_id = int(record["source_record_id"])
        row_center = int(record["row_center"])
        rows_by_source[source_id].append(row_center)
        if record["exposed_deletion_core_vertices"]:
            exposed_rows_by_source[source_id].append(row_center)
        if record["row_center_private_in_all_deletion_closures"]:
            private_center_rows_by_source[source_id].append(row_center)
        if record["ledger_private_pair_support_hits"]:
            ledger_pair_support_rows_by_source[source_id].append(row_center)

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This classifies fixed selected-row gaps; it does not prove the row centers are forced.",
            "Private-halo containment and ledger private-pair hits are bookkeeping contacts, not Euclidean certificates.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "target_source_ids": [int(record["source_record_id"]) for record in targets["records"]],
            "row_gap_record_count": len(row_records),
            "row_gap_centers_by_source_id": {
                str(source_id): centers for source_id, centers in sorted(rows_by_source.items())
            },
            "pressure_class_counts": _json_counter(pressure_counts),
            "activation_deficit_counts": _json_counter(deficit_counts),
            "outside_support_kind_counts": _json_counter(support_kind_counts),
            "deletion_closure_exposed_row_count": sum(
                1 for record in row_records if record["exposed_deletion_core_vertices"]
            ),
            "row_center_private_in_all_deletions_count": sum(
                1 for record in row_records if record["row_center_private_in_all_deletion_closures"]
            ),
            "ledger_private_pair_support_row_count": sum(
                1 for record in row_records if record["ledger_private_pair_support_hits"]
            ),
            "exposed_rows_by_source_id": {
                str(source_id): centers
                for source_id, centers in sorted(exposed_rows_by_source.items())
            },
            "private_center_rows_by_source_id": {
                str(source_id): centers
                for source_id, centers in sorted(private_center_rows_by_source.items())
            },
            "ledger_private_pair_support_rows_by_source_id": {
                str(source_id): centers
                for source_id, centers in sorted(ledger_pair_support_rows_by_source.items())
            },
            "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
            "next_bridge_question": (
                "Can closure-exposed rows, one-outside-label rows, and the "
                "single outside-pair row be forced from genuine rich-class "
                "geometry rather than fixed selected-row bookkeeping?"
            ),
        },
        "row_records": row_records,
        "source_artifacts": [
            {
                "path": "data/certificates/bootstrap_t12_forcing_targets.json",
                "role": "missing T12/F16 row centers and direct cycle-pair contacts",
                "schema": targets.get("schema"),
                "status": targets.get("status"),
                "trust": targets.get("trust"),
            },
            {
                "path": "data/certificates/bootstrap_vertex_circle_overlay.json",
                "role": "bootstrap deletion closures and source overlay records",
                "schema": overlay.get("schema"),
                "status": overlay.get("status"),
                "trust": overlay.get("trust"),
            },
        ],
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_row_pressure.py",
            "command": "python scripts/check_bootstrap_t12_row_pressure.py --write --assert-expected",
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline counts for the row-pressure diagnostic."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected bootstrap/T12 row-pressure schema")
    if payload.get("status") != STATUS:
        raise AssertionError("unexpected bootstrap/T12 row-pressure status")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("summary must be a mapping")
    expected_summary = {
        "target_source_ids": [81, 151],
        "row_gap_record_count": 6,
        "row_gap_centers_by_source_id": {"81": [3, 8], "151": [5, 6, 7, 8]},
        "pressure_class_counts": {
            "ALREADY_PRESENT_IN_A_DELETION_CLOSURE": 2,
            "NEEDS_ONE_OUTSIDE_LABEL_AND_PRIVATE_CENTER": 3,
            "NEEDS_OUTSIDE_PAIR_AND_PRIVATE_CENTER": 1,
        },
        "activation_deficit_counts": {"0": 2, "1": 3, "2": 1},
        "outside_support_kind_counts": {
            "core_sufficient": 2,
            "outside_1_set": 3,
            "outside_2_set": 1,
        },
        "deletion_closure_exposed_row_count": 2,
        "row_center_private_in_all_deletions_count": 4,
        "ledger_private_pair_support_row_count": 1,
        "exposed_rows_by_source_id": {"81": [3], "151": [7]},
        "private_center_rows_by_source_id": {"81": [8], "151": [5, 6, 8]},
        "ledger_private_pair_support_rows_by_source_id": {"151": [6]},
        "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"summary {key} is {summary.get(key)!r}, expected {expected!r}")

    records = payload.get("row_records")
    if not isinstance(records, list):
        raise AssertionError("row_records must be a list")
    expected_records = {
        (81, 3): {
            "bootstrap_core_witnesses": [0, 1, 4],
            "activation_deficit_from_bootstrap_core": 0,
            "exposed_deletion_core_vertices": [2],
            "pressure_class": "ALREADY_PRESENT_IN_A_DELETION_CLOSURE",
        },
        (81, 8): {
            "bootstrap_core_witnesses": [0, 2],
            "outside_support_subsets": [[5], [6]],
            "activation_deficit_from_bootstrap_core": 1,
            "pressure_class": "NEEDS_ONE_OUTSIDE_LABEL_AND_PRIVATE_CENTER",
        },
        (151, 5): {
            "bootstrap_core_witnesses": [2, 4],
            "outside_support_subsets": [[7], [8]],
            "activation_deficit_from_bootstrap_core": 1,
            "pressure_class": "NEEDS_ONE_OUTSIDE_LABEL_AND_PRIVATE_CENTER",
        },
        (151, 6): {
            "bootstrap_core_witnesses": [0],
            "outside_support_subsets": [[3, 5], [3, 8], [5, 8]],
            "activation_deficit_from_bootstrap_core": 2,
            "ledger_private_pair_support_hit_count": 2,
            "pressure_class": "NEEDS_OUTSIDE_PAIR_AND_PRIVATE_CENTER",
        },
        (151, 7): {
            "bootstrap_core_witnesses": [0, 1, 4],
            "activation_deficit_from_bootstrap_core": 0,
            "exposed_deletion_core_vertices": [2],
            "pressure_class": "ALREADY_PRESENT_IN_A_DELETION_CLOSURE",
        },
        (151, 8): {
            "bootstrap_core_witnesses": [1, 2],
            "outside_support_subsets": [[5], [7]],
            "activation_deficit_from_bootstrap_core": 1,
            "pressure_class": "NEEDS_ONE_OUTSIDE_LABEL_AND_PRIVATE_CENTER",
        },
    }
    by_key = {
        (int(record["source_record_id"]), int(record["row_center"])): record
        for record in records
    }
    if set(by_key) != set(expected_records):
        raise AssertionError("unexpected row-pressure record keys")
    for key, expected in expected_records.items():
        record = by_key[key]
        for field, expected_value in expected.items():
            if record.get(field) != expected_value:
                raise AssertionError(
                    f"row-pressure {key} {field} is {record.get(field)!r}, expected {expected_value!r}"
                )
