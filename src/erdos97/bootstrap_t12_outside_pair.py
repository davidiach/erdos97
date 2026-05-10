"""Outside-pair packet for the bootstrap/T12 target.

This module isolates the row-pressure subcase where a missing T12/F16 row has
one bootstrap-core witness and needs an outside pair while its row center
remains private in every deletion closure.  It is proof-mining bookkeeping only
and does not prove that any missing row is geometrically forced.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_row_pressure import build_t12_row_pressure_payload


SCHEMA = "erdos97.bootstrap_t12_outside_pair.v1"
STATUS = "BOOTSTRAP_T12_OUTSIDE_PAIR_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Outside-pair packet for the two tight n=9 bootstrap/T12 records; "
    "isolates the single missing T12/F16 row center that needs an outside pair "
    "while the row center remains private in every deletion closure. This "
    "does not prove that the missing row is forced, does not prove n=9, does "
    "not prove the bridge, and does not claim a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = REPO_ROOT / "data" / "certificates" / "bootstrap_t12_outside_pair.json"

PRESSURE_CLASS = "NEEDS_OUTSIDE_PAIR_AND_PRIVATE_CENTER"
LEDGER_HIT_MODE = "LEDGER_PRIVATE_PAIR_HIT"
PRIVATE_HALO_ONLY_MODE = "PRIVATE_HALO_ONLY"


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _pair(values: Sequence[Any]) -> tuple[int, int]:
    a, b = int(values[0]), int(values[1])
    if a == b:
        raise ValueError("pair endpoints must be distinct")
    return tuple(sorted((a, b)))


def _pair_key(values: Sequence[Any]) -> str:
    a, b = _pair(values)
    return f"{a}-{b}"


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _support_pair_mode(hit: Mapping[str, Any]) -> str:
    if bool(hit["ledger_private_pair_hit"]):
        return LEDGER_HIT_MODE
    return PRIVATE_HALO_ONLY_MODE


def _support_pair_option(
    *,
    row_record: Mapping[str, Any],
    hit: Mapping[str, Any],
) -> dict[str, object]:
    support_pair = list(_pair(hit["support"]))
    core_witnesses = _int_list(row_record["bootstrap_core_witnesses"])
    row_center_private_core_vertices = _int_list(row_record["row_center_private_core_vertices"])
    private_halo_core_vertices = _int_list(hit["private_halo_core_vertices"])
    missing_private_halo_core_vertices = sorted(
        set(row_center_private_core_vertices) - set(private_halo_core_vertices)
    )
    activation_witnesses = sorted(set(core_witnesses) | set(support_pair))

    return {
        "support_pair": support_pair,
        "support_pair_key": _pair_key(support_pair),
        "activation_witnesses_from_core_plus_pair": activation_witnesses,
        "activation_witness_count": len(activation_witnesses),
        "activation_ready_with_pair": len(activation_witnesses) >= 3,
        "private_halo_core_vertices": private_halo_core_vertices,
        "private_halo_containment_count": int(hit["private_halo_containment_count"]),
        "pair_private_in_all_deletion_halos": not missing_private_halo_core_vertices,
        "missing_private_halo_core_vertices": missing_private_halo_core_vertices,
        "ledger_private_pair_core_vertices": _int_list(hit["ledger_private_pair_core_vertices"]),
        "ledger_private_pair_hit": bool(hit["ledger_private_pair_hit"]),
        "support_pair_mode": _support_pair_mode(hit),
    }


def _outside_pair_record(row_record: Mapping[str, Any]) -> dict[str, object]:
    support_pair_options = [
        _support_pair_option(row_record=row_record, hit=hit)
        for hit in row_record["support_hits"]
    ]
    support_pair_options.sort(key=lambda option: str(option["support_pair_key"]))
    support_mode_counts = Counter(
        str(option["support_pair_mode"]) for option in support_pair_options
    )
    witness_counts_by_deletion_core = {
        str(exposure["core_vertex"]): int(exposure["witness_count_in_closure"])
        for exposure in row_record["deletion_closure_exposures"]
    }

    return {
        "source_record_id": int(row_record["source_record_id"]),
        "classification_assignment_id": str(row_record["classification_assignment_id"]),
        "row_center": int(row_record["row_center"]),
        "roles": [str(role) for role in row_record["roles"]],
        "witnesses": _int_list(row_record["witnesses"]),
        "bootstrap_core_witnesses": _int_list(row_record["bootstrap_core_witnesses"]),
        "outside_witnesses": _int_list(row_record["outside_witnesses"]),
        "activation_deficit_from_bootstrap_core": int(
            row_record["activation_deficit_from_bootstrap_core"]
        ),
        "outside_support_kind": str(row_record["outside_support_kind"]),
        "pressure_class": str(row_record["pressure_class"]),
        "row_center_private_core_vertices": _int_list(row_record["row_center_private_core_vertices"]),
        "row_center_private_in_all_deletion_closures": bool(
            row_record["row_center_private_in_all_deletion_closures"]
        ),
        "max_witness_count_in_deletion_closure": int(
            row_record["max_witness_count_in_deletion_closure"]
        ),
        "witness_counts_by_deletion_core": witness_counts_by_deletion_core,
        "support_pair_options": support_pair_options,
        "support_pair_option_count": len(support_pair_options),
        "support_pair_modes": _json_counter(support_mode_counts),
        "ledger_private_pair_support_hit_count": int(
            row_record["ledger_private_pair_support_hit_count"]
        ),
    }


def _outside_pair_records(row_pressure: Mapping[str, Any]) -> list[dict[str, object]]:
    row_records = row_pressure.get("row_records")
    if not isinstance(row_records, list):
        raise AssertionError("row-pressure payload row_records must be a list")
    records = [
        _outside_pair_record(row_record)
        for row_record in row_records
        if row_record["pressure_class"] == PRESSURE_CLASS
    ]
    records.sort(key=lambda record: (int(record["source_record_id"]), int(record["row_center"])))
    return records


def build_t12_outside_pair_payload() -> dict[str, object]:
    """Return the deterministic outside-pair bootstrap/T12 packet."""

    row_pressure = build_t12_row_pressure_payload()
    records = _outside_pair_records(row_pressure)

    rows_by_source: defaultdict[int, list[int]] = defaultdict(list)
    role_counts = Counter(role for record in records for role in record["roles"])
    support_pair_counts: Counter[str] = Counter()
    support_label_counts: Counter[int] = Counter()
    support_mode_counts: Counter[str] = Counter()
    containment_counts: Counter[int] = Counter()
    ledger_hit_pairs: list[list[int]] = []
    ledger_miss_pairs: list[list[int]] = []
    ledger_core_vertices: set[int] = set()
    private_in_all_count = 0
    for record in records:
        source_id = int(record["source_record_id"])
        row_center = int(record["row_center"])
        rows_by_source[source_id].append(row_center)
        for option in record["support_pair_options"]:
            support_pair = _int_list(option["support_pair"])
            support_pair_counts[str(option["support_pair_key"])] += 1
            for label in support_pair:
                support_label_counts[label] += 1
            support_mode = str(option["support_pair_mode"])
            support_mode_counts[support_mode] += 1
            containment_counts[int(option["private_halo_containment_count"])] += 1
            if bool(option["pair_private_in_all_deletion_halos"]):
                private_in_all_count += 1
            if bool(option["ledger_private_pair_hit"]):
                ledger_hit_pairs.append(support_pair)
                ledger_core_vertices.update(_int_list(option["ledger_private_pair_core_vertices"]))
            else:
                ledger_miss_pairs.append(support_pair)

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This packet isolates a fixed selected-row outside-pair gap; it does not prove the row is forced.",
            "Private-pair ledger hits are bookkeeping contacts, not Euclidean rich-class certificates.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "source_record_ids": sorted(rows_by_source),
            "outside_pair_row_record_count": len(records),
            "row_centers_by_source_id": {
                str(source_id): centers for source_id, centers in sorted(rows_by_source.items())
            },
            "support_pair_option_count": sum(
                int(record["support_pair_option_count"]) for record in records
            ),
            "support_pair_counts": _json_counter(support_pair_counts),
            "support_label_counts": _json_counter(support_label_counts),
            "support_pair_mode_counts": _json_counter(support_mode_counts),
            "private_halo_containment_count_distribution": _json_counter(containment_counts),
            "support_pairs_private_in_all_deletion_halos_count": private_in_all_count,
            "ledger_private_pair_support_hit_count": len(ledger_hit_pairs),
            "ledger_private_pair_support_miss_count": len(ledger_miss_pairs),
            "ledger_hit_support_pairs": sorted(ledger_hit_pairs),
            "ledger_miss_support_pairs": sorted(ledger_miss_pairs),
            "ledger_private_pair_core_vertices": sorted(ledger_core_vertices),
            "row_center_private_in_all_deletions_count": sum(
                1 for record in records if record["row_center_private_in_all_deletion_closures"]
            ),
            "role_counts": _json_counter(role_counts),
            "activation_deficit_counts": {"2": len(records)},
            "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
            "next_bridge_question": (
                "Can a future bridge force an equality-connector row from one "
                "bootstrap-core witness plus an outside pair with partial "
                "private-pair ledger support?"
            ),
        },
        "records": records,
        "source_artifacts": [
            {
                "path": "data/certificates/bootstrap_t12_row_pressure.json",
                "role": "source row-pressure records and outside-pair supports",
                "schema": row_pressure.get("schema"),
                "status": row_pressure.get("status"),
                "trust": row_pressure.get("trust"),
            }
        ],
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_outside_pair.py",
            "command": "python scripts/check_bootstrap_t12_outside_pair.py --write --assert-expected",
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline counts for the outside-pair packet."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected bootstrap/T12 outside-pair schema")
    if payload.get("status") != STATUS:
        raise AssertionError("unexpected bootstrap/T12 outside-pair status")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("summary must be a mapping")
    expected_summary = {
        "source_record_ids": [151],
        "outside_pair_row_record_count": 1,
        "row_centers_by_source_id": {"151": [6]},
        "support_pair_option_count": 3,
        "support_pair_counts": {"3-5": 1, "3-8": 1, "5-8": 1},
        "support_label_counts": {"3": 2, "5": 2, "8": 2},
        "support_pair_mode_counts": {
            LEDGER_HIT_MODE: 2,
            PRIVATE_HALO_ONLY_MODE: 1,
        },
        "private_halo_containment_count_distribution": {"4": 3},
        "support_pairs_private_in_all_deletion_halos_count": 3,
        "ledger_private_pair_support_hit_count": 2,
        "ledger_private_pair_support_miss_count": 1,
        "ledger_hit_support_pairs": [[3, 8], [5, 8]],
        "ledger_miss_support_pairs": [[3, 5]],
        "ledger_private_pair_core_vertices": [0, 2],
        "row_center_private_in_all_deletions_count": 1,
        "role_counts": {"equality_connector_row": 1},
        "activation_deficit_counts": {"2": 1},
        "forcing_target_status": "OPEN_TARGET_NOT_PROVED",
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"summary {key} is {summary.get(key)!r}, expected {expected!r}")

    records = payload.get("records")
    if not isinstance(records, list):
        raise AssertionError("records must be a list")
    if len(records) != 1:
        raise AssertionError("outside-pair packet should contain exactly one row")
    record = records[0]
    expected_record = {
        "source_record_id": 151,
        "classification_assignment_id": "A152",
        "row_center": 6,
        "roles": ["equality_connector_row"],
        "witnesses": [0, 3, 5, 8],
        "bootstrap_core_witnesses": [0],
        "outside_witnesses": [3, 5, 8],
        "activation_deficit_from_bootstrap_core": 2,
        "outside_support_kind": "outside_2_set",
        "pressure_class": PRESSURE_CLASS,
        "row_center_private_core_vertices": [0, 1, 2, 4],
        "row_center_private_in_all_deletion_closures": True,
        "max_witness_count_in_deletion_closure": 1,
        "witness_counts_by_deletion_core": {"0": 0, "1": 1, "2": 1, "4": 1},
        "support_pair_option_count": 3,
        "support_pair_modes": {
            LEDGER_HIT_MODE: 2,
            PRIVATE_HALO_ONLY_MODE: 1,
        },
        "ledger_private_pair_support_hit_count": 2,
    }
    for key, expected in expected_record.items():
        if record.get(key) != expected:
            raise AssertionError(f"outside-pair record {key} is {record.get(key)!r}, expected {expected!r}")

    expected_pairs = {
        "3-5": {
            "support_pair": [3, 5],
            "mode": PRIVATE_HALO_ONLY_MODE,
            "ledger_core_vertices": [],
        },
        "3-8": {
            "support_pair": [3, 8],
            "mode": LEDGER_HIT_MODE,
            "ledger_core_vertices": [0],
        },
        "5-8": {
            "support_pair": [5, 8],
            "mode": LEDGER_HIT_MODE,
            "ledger_core_vertices": [2],
        },
    }
    options = record.get("support_pair_options")
    if not isinstance(options, list):
        raise AssertionError("support_pair_options must be a list")
    by_key = {str(option["support_pair_key"]): option for option in options}
    if set(by_key) != set(expected_pairs):
        raise AssertionError("unexpected outside-pair support options")
    for key, expected in expected_pairs.items():
        option = by_key[key]
        if option["support_pair"] != expected["support_pair"]:
            raise AssertionError(f"support pair {key} changed")
        if option["support_pair_mode"] != expected["mode"]:
            raise AssertionError(f"support pair {key} mode changed")
        if option["ledger_private_pair_core_vertices"] != expected["ledger_core_vertices"]:
            raise AssertionError(f"support pair {key} ledger core vertices changed")
        if not option["activation_ready_with_pair"]:
            raise AssertionError(f"support pair {key} is not activation-ready")
        if option["activation_witness_count"] != 3:
            raise AssertionError(f"support pair {key} activation count changed")
        if not option["pair_private_in_all_deletion_halos"]:
            raise AssertionError(f"support pair {key} is no longer private in all halos")
