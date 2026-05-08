"""Cross-artifact checks for the n=9 base-apex D=3 bookkeeping stack.

This checker joins already generated JSON artifacts. It is not a generator and
does not prove the n=9 case, provide a counterexample, establish incidence
completeness, test geometric realizability, or change the global status.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

N = 9
TOTAL_PROFILE_EXCESS = 6
CAPACITY_DEFICIT = 3
EXPECTED_PROFILE_SEQUENCE_COUNT = 3003
EXPECTED_ESCAPE_PLACEMENT_COUNT = 108
EXPECTED_D3_CLASS_COUNT = 18088
EXPECTED_D3_ORBIT_SIZE_COUNTS = {"18": 17948, "9": 140}
EXPECTED_REPRESENTATIVE_COUNT = 88
EXPECTED_PROFILE_IDS = [f"P{index:02d}" for index in range(19, 30)]
EXPECTED_ESCAPE_IDS = [f"X{index:02d}" for index in range(8)]
EXPECTED_TARGET_CAPACITY_TOTAL = 60
EXPECTED_REALIZABILITY_STATE = "UNKNOWN"
EXPECTED_INCIDENCE_STATE = "UNKNOWN"
EXPECTED_STATE_SCOPE = "bookkeeping-only"
EXPECTED_STATUS = "EXPLORATORY_LEDGER_ONLY"
EXPECTED_TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
EXPECTED_CLAIM_SCOPE = (
    "Cross-artifact consistency checker for n=9 base-apex D=3 bookkeeping "
    "artifacts; not a proof of n=9, not a counterexample, not an "
    "incidence-completeness result, not a geometric realizability test, and "
    "not a global status update."
)

DEFAULT_ARTIFACT_PATHS = {
    "d3_escape_slice": Path("data/certificates/n9_base_apex_d3_escape_slice.json"),
    "d3_escape_frontier_packet": Path(
        "data/certificates/n9_base_apex_d3_escape_frontier_packet.json"
    ),
    "low_excess_escape_crosswalk": Path(
        "data/certificates/n9_base_apex_low_excess_escape_crosswalk.json"
    ),
    "d3_p19_incidence_capacity_pilot": Path(
        "data/certificates/n9_base_apex_d3_p19_incidence_capacity_pilot.json"
    ),
    "d3_incidence_capacity_packet": Path(
        "data/certificates/n9_base_apex_d3_incidence_capacity_packet.json"
    ),
}

EXPECTED_ARTIFACT_CONTRACTS = {
    "d3_escape_slice": {
        "schema": "erdos97.n9_base_apex_d3_escape_slice.v1",
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "claim_scope": (
            "Focused n=9 base-apex D=3,r=3 coupled escape-slice bookkeeping; "
            "not a proof of n=9, not a counterexample, not a geometric "
            "realizability test, and not a global status update."
        ),
        "source_artifacts": {
            "escape_budget": "data/certificates/n9_base_apex_escape_budget_report.json",
            "low_excess_ledgers": (
                "data/certificates/n9_base_apex_low_excess_ledgers.json"
            ),
            "selected_baseline_overlay": (
                "data/certificates/n9_selected_baseline_escape_budget_overlay.json"
            ),
        },
        "provenance": {
            "generator": "scripts/analyze_n9_d3_escape_slice.py",
            "command": (
                "python scripts/analyze_n9_d3_escape_slice.py --assert-expected "
                "--out data/certificates/n9_base_apex_d3_escape_slice.json"
            ),
        },
    },
    "d3_escape_frontier_packet": {
        "schema": "erdos97.n9_base_apex_d3_escape_frontier_packet.v1",
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "claim_scope": (
            "Focused n=9 base-apex D=3,r=3 escape-frontier representative "
            "packet bookkeeping; not a proof of n=9, not a counterexample, "
            "not a geometric realizability test, and not a global status "
            "update."
        ),
        "source_artifacts": {
            "d3_escape_slice": (
                "data/certificates/n9_base_apex_d3_escape_slice.json"
            ),
            "low_excess_escape_crosswalk": (
                "data/certificates/n9_base_apex_low_excess_escape_crosswalk.json"
            ),
        },
        "provenance": {
            "generator": (
                "scripts/analyze_n9_base_apex_d3_escape_frontier_packet.py"
            ),
            "command": (
                "python scripts/analyze_n9_base_apex_d3_escape_frontier_packet.py "
                "--assert-expected --out "
                "data/certificates/n9_base_apex_d3_escape_frontier_packet.json"
            ),
        },
    },
    "low_excess_escape_crosswalk": {
        "schema": "erdos97.n9_base_apex_low_excess_escape_crosswalk.v1",
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "claim_scope": (
            "Focused n=9 base-apex low-excess profile/escape crosswalk "
            "bookkeeping; not a proof of n=9, not a counterexample, not a "
            "geometric realizability test, and not a global status update."
        ),
        "source_artifacts": {
            "d3_escape_slice": (
                "data/certificates/n9_base_apex_d3_escape_slice.json"
            ),
            "escape_budget": "data/certificates/n9_base_apex_escape_budget_report.json",
            "low_excess_escape_ladder": (
                "data/certificates/n9_base_apex_low_excess_escape_ladder.json"
            ),
            "low_excess_ledgers": (
                "data/certificates/n9_base_apex_low_excess_ledgers.json"
            ),
        },
        "provenance": {
            "generator": (
                "scripts/analyze_n9_base_apex_low_excess_escape_crosswalk.py"
            ),
            "command": (
                "python scripts/analyze_n9_base_apex_low_excess_escape_crosswalk.py "
                "--assert-expected --out "
                "data/certificates/n9_base_apex_low_excess_escape_crosswalk.json"
            ),
        },
    },
    "d3_p19_incidence_capacity_pilot": {
        "schema": "erdos97.n9_base_apex_d3_p19_incidence_capacity_pilot.v1",
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "claim_scope": (
            "Focused n=9 base-apex D=3 P19 incidence-capacity pilot ledger "
            "for rows R000..R007; not a proof of n=9, not a counterexample, "
            "not an incidence-completeness result, not a geometric "
            "realizability test, and not a global status update."
        ),
        "source_artifacts": {
            "d3_escape_frontier_packet": (
                "data/certificates/n9_base_apex_d3_escape_frontier_packet.json"
            ),
            "low_excess_escape_crosswalk": (
                "data/certificates/n9_base_apex_low_excess_escape_crosswalk.json"
            ),
        },
        "provenance": {
            "generator": (
                "scripts/analyze_n9_base_apex_d3_p19_incidence_capacity_pilot.py"
            ),
            "command": (
                "python scripts/analyze_n9_base_apex_d3_p19_incidence_capacity_pilot.py "
                "--assert-expected --out "
                "data/certificates/n9_base_apex_d3_p19_incidence_capacity_pilot.json"
            ),
        },
    },
    "d3_incidence_capacity_packet": {
        "schema": "erdos97.n9_base_apex_d3_incidence_capacity_packet.v1",
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "claim_scope": (
            "Full n=9 base-apex D=3 incidence-capacity packet ledger for all "
            "88 D=3 packet rows; not a proof of n=9, not a counterexample, "
            "not an incidence-completeness result, not a geometric "
            "realizability test, and not a global status update."
        ),
        "source_artifacts": {
            "d3_escape_frontier_packet": (
                "data/certificates/n9_base_apex_d3_escape_frontier_packet.json"
            ),
            "low_excess_escape_crosswalk": (
                "data/certificates/n9_base_apex_low_excess_escape_crosswalk.json"
            ),
        },
        "provenance": {
            "generator": (
                "scripts/analyze_n9_base_apex_d3_incidence_capacity_packet.py"
            ),
            "command": (
                "python scripts/analyze_n9_base_apex_d3_incidence_capacity_packet.py "
                "--assert-expected --out "
                "data/certificates/n9_base_apex_d3_incidence_capacity_packet.json"
            ),
        },
    },
}

PACKET_JOIN_FIELDS = (
    "representative_id",
    "representative_profile_sequence",
    "excess_multiset",
    "escape_class_id",
    "canonical_escape_placement",
    "common_dihedral_pair_class_count",
    "labelled_profile_sequence_count",
    "labelled_escape_placement_count",
)

CROSSWALK_JOIN_FIELDS = (
    "excess_multiset",
    "escape_class_id",
    "canonical_escape_placement",
    "common_dihedral_pair_class_count",
    "labelled_profile_sequence_count",
    "labelled_escape_placement_count",
)


def strict_int(value: Any) -> bool:
    """Return true only for JSON integers, excluding bool."""

    return type(value) is int


def resolve_artifact_paths(
    root: Path,
    overrides: Mapping[str, Path] | None = None,
) -> dict[str, Path]:
    """Return absolute artifact paths with optional per-artifact overrides."""

    out: dict[str, Path] = {}
    overrides = overrides or {}
    for key, default_path in DEFAULT_ARTIFACT_PATHS.items():
        path = overrides.get(key, default_path)
        out[key] = path if path.is_absolute() else root / path
    return out


def load_json(path: Path) -> Any:
    """Load one JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def load_artifacts(paths: Mapping[str, Path]) -> tuple[dict[str, Any], list[str]]:
    """Load all artifacts, returning payloads and load errors."""

    artifacts: dict[str, Any] = {}
    errors: list[str] = []
    for key, path in paths.items():
        try:
            artifacts[key] = load_json(path)
        except FileNotFoundError:
            errors.append(f"{key} artifact is missing: {path.as_posix()}")
        except UnicodeDecodeError as exc:
            errors.append(f"{key} artifact is not valid UTF-8: {exc}")
        except json.JSONDecodeError as exc:
            errors.append(f"{key} artifact is not valid JSON: {exc}")
        except OSError as exc:
            errors.append(f"{key} artifact could not be read: {exc}")
    return artifacts, errors


def cloned_artifacts(artifacts: Mapping[str, Any]) -> dict[str, Any]:
    """Return a JSON-style deep copy suitable for tests."""

    return copy.deepcopy(dict(artifacts))


def display_path(path: Path, root: Path) -> str:
    """Return a stable repo-relative path when possible."""

    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _object(value: Any, label: str, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{label} must be a JSON object")
        return None
    return value


def _list(value: Any, label: str, errors: list[str]) -> list[Any] | None:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return None
    return value


def _object_rows(
    rows: Sequence[Any],
    label: str,
    errors: list[str],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        row_label = f"{label}[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{row_label} must be an object")
            continue
        out.append(row)
    if len(out) != len(rows):
        errors.append(f"{label} object row count mismatch")
    return out


def _int_field(
    row: Mapping[str, Any],
    key: str,
    label: str,
    errors: list[str],
) -> int | None:
    value = row.get(key)
    if not strict_int(value):
        errors.append(f"{label}.{key} must be an int")
        return None
    return int(value)


def _int_list(value: Any, label: str, errors: list[str]) -> list[int] | None:
    if not isinstance(value, list) or not all(strict_int(item) for item in value):
        errors.append(f"{label} must be a list of ints")
        return None
    return [int(item) for item in value]


def _str_field(
    row: Mapping[str, Any],
    key: str,
    label: str,
    errors: list[str],
) -> str | None:
    value = row.get(key)
    if not isinstance(value, str):
        errors.append(f"{label}.{key} must be a string")
        return None
    return value


def _join_key(
    row: Mapping[str, Any],
    label: str,
    errors: list[str],
) -> tuple[tuple[int, ...], str] | None:
    multiset = _int_list(row.get("excess_multiset"), f"{label}.excess_multiset", errors)
    escape_id = row.get("escape_class_id")
    if not isinstance(escape_id, str):
        errors.append(f"{label}.escape_class_id must be a string")
        return None
    if multiset is None:
        return None
    return (tuple(multiset), escape_id)


def _field_equal(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    field: str,
    left_label: str,
    right_label: str,
    errors: list[str],
) -> None:
    if left.get(field) != right.get(field):
        errors.append(f"{left_label}.{field} does not match {right_label}.{field}")


def _rows_by_key(
    rows: Sequence[Any],
    label: str,
    errors: list[str],
) -> dict[tuple[tuple[int, ...], str], dict[str, Any]]:
    out: dict[tuple[tuple[int, ...], str], dict[str, Any]] = {}
    for index, row in enumerate(rows):
        row_label = f"{label}[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{row_label} must be an object")
            continue
        key = _join_key(row, row_label, errors)
        if key is None:
            continue
        if key in out:
            errors.append(f"{label} duplicate join key: {key!r}")
            continue
        out[key] = row
    return out


def validate_artifact_contracts(
    artifacts: Mapping[str, Any],
    errors: list[str],
) -> None:
    """Validate identity/provenance contracts for all joined artifacts."""

    for artifact_key, expected_fields in EXPECTED_ARTIFACT_CONTRACTS.items():
        payload = _object(artifacts.get(artifact_key), artifact_key, errors)
        if payload is None:
            continue
        for field, expected in expected_fields.items():
            if payload.get(field) != expected:
                errors.append(f"{artifact_key}.{field} mismatch")


def validate_d3_slice(slice_payload: Any, errors: list[str]) -> None:
    """Validate pinned D=3 escape-slice totals and orbit arithmetic."""

    payload = _object(slice_payload, "d3_escape_slice", errors)
    if payload is None:
        return
    profile = _object(payload.get("profile_slice"), "d3_escape_slice.profile_slice", errors)
    escape = _object(payload.get("escape_slice"), "d3_escape_slice.escape_slice", errors)
    coupled = _object(payload.get("coupled_slice"), "d3_escape_slice.coupled_slice", errors)
    if profile is None or escape is None or coupled is None:
        return

    profile_count = _int_field(
        profile,
        "labelled_profile_sequence_count",
        "d3_escape_slice.profile_slice",
        errors,
    )
    escape_count = _int_field(
        escape,
        "labelled_escape_placement_count",
        "d3_escape_slice.escape_slice",
        errors,
    )
    class_count = _int_field(
        coupled,
        "common_dihedral_pair_class_count",
        "d3_escape_slice.coupled_slice",
        errors,
    )
    labelled_pair_count = _int_field(
        coupled,
        "labelled_profile_escape_pair_count",
        "d3_escape_slice.coupled_slice",
        errors,
    )

    if profile_count != EXPECTED_PROFILE_SEQUENCE_COUNT:
        errors.append("d3_escape_slice profile sequence count must be 3003")
    if escape_count != EXPECTED_ESCAPE_PLACEMENT_COUNT:
        errors.append("d3_escape_slice escape placement count must be 108")
    if class_count != EXPECTED_D3_CLASS_COUNT:
        errors.append("d3_escape_slice common-dihedral class count must be 18088")

    orbit_counts = coupled.get("common_dihedral_pair_orbit_size_counts")
    if orbit_counts != EXPECTED_D3_ORBIT_SIZE_COUNTS:
        errors.append("d3_escape_slice orbit size counts must be 17948*18 and 140*9")
        return

    orbit_class_count = sum(int(count) for count in orbit_counts.values())
    orbit_labelled_count = sum(int(size) * int(count) for size, count in orbit_counts.items())
    if orbit_class_count != EXPECTED_D3_CLASS_COUNT:
        errors.append("d3_escape_slice orbit class count does not sum to 18088")
    if labelled_pair_count is not None and orbit_labelled_count != labelled_pair_count:
        errors.append("d3_escape_slice orbit arithmetic 17948*18+140*9 mismatch")
    if (
        profile_count is not None
        and escape_count is not None
        and labelled_pair_count is not None
        and profile_count * escape_count != labelled_pair_count
    ):
        errors.append("d3_escape_slice labelled pair count must equal 3003*108")


def _d3_crosswalk_rows(crosswalk_payload: Any, errors: list[str]) -> list[dict[str, Any]]:
    payload = _object(crosswalk_payload, "low_excess_escape_crosswalk", errors)
    if payload is None:
        return []
    rows = _list(
        payload.get("crosswalk_rows"),
        "low_excess_escape_crosswalk.crosswalk_rows",
        errors,
    )
    if rows is None:
        return []
    d3_rows: list[dict[str, Any]] = []
    for index, row in enumerate(_object_rows(rows, "low_excess_escape_crosswalk.crosswalk_rows", errors)):
        label = f"low_excess_escape_crosswalk.crosswalk_rows[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be an object")
            continue
        profile_count = _int_field(row, "labelled_profile_sequence_count", label, errors)
        escape_count = _int_field(row, "labelled_escape_placement_count", label, errors)
        pair_count = _int_field(row, "labelled_profile_escape_pair_count", label, errors)
        if (
            profile_count is not None
            and escape_count is not None
            and pair_count is not None
            and profile_count * escape_count != pair_count
        ):
            errors.append(
                f"{label}.labelled_profile_escape_pair_count must equal "
                "profile*escape count"
            )
        if (
            row.get("total_profile_excess") == TOTAL_PROFILE_EXCESS
            and row.get("capacity_deficit") == CAPACITY_DEFICIT
        ):
            d3_rows.append(row)
    return d3_rows


def validate_crosswalk_slice(
    crosswalk_payload: Any,
    errors: list[str],
) -> list[dict[str, Any]]:
    """Validate the E=6,D=3 crosswalk slice and return its rows."""

    d3_rows = _d3_crosswalk_rows(crosswalk_payload, errors)
    if len(d3_rows) != EXPECTED_REPRESENTATIVE_COUNT:
        errors.append("low_excess_escape_crosswalk E=6,D=3 row count must be 88")

    total = 0
    row_ids: list[tuple[str, str]] = []
    for index, row in enumerate(d3_rows):
        label = f"low_excess_escape_crosswalk.d3_rows[{index}]"
        class_count = _int_field(row, "common_dihedral_pair_class_count", label, errors)
        if class_count is not None:
            total += class_count
        profile_id = _str_field(row, "profile_ledger_id", label, errors)
        escape_id = _str_field(row, "escape_class_id", label, errors)
        if profile_id is not None and escape_id is not None:
            row_ids.append((profile_id, escape_id))
    if total != EXPECTED_D3_CLASS_COUNT:
        errors.append("low_excess_escape_crosswalk E=6,D=3 class sum must be 18088")

    expected_product = [
        (profile_id, escape_id)
        for profile_id in EXPECTED_PROFILE_IDS
        for escape_id in EXPECTED_ESCAPE_IDS
    ]
    if row_ids != expected_product:
        errors.append("low_excess_escape_crosswalk D=3 rows must be P19..P29 x X00..X07")
    return d3_rows


def validate_packet_to_crosswalk_join(
    packet_payload: Any,
    d3_crosswalk_rows: Sequence[dict[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    """Validate that D=3 packet representatives join to crosswalk rows."""

    payload = _object(packet_payload, "d3_escape_frontier_packet", errors)
    if payload is None:
        return []
    representatives = _list(
        payload.get("representatives"),
        "d3_escape_frontier_packet.representatives",
        errors,
    )
    if representatives is None:
        return []
    if len(representatives) != EXPECTED_REPRESENTATIVE_COUNT:
        errors.append("d3_escape_frontier_packet representative count must be 88")
    if payload.get("common_dihedral_pair_class_count") != EXPECTED_D3_CLASS_COUNT:
        errors.append("d3_escape_frontier_packet class count must be 18088")

    rows = _object_rows(representatives, "d3_escape_frontier_packet.representatives", errors)
    if len(rows) != EXPECTED_REPRESENTATIVE_COUNT:
        errors.append("d3_escape_frontier_packet object row count must be 88")
    crosswalk_by_key = _rows_by_key(
        d3_crosswalk_rows,
        "low_excess_escape_crosswalk.d3_rows",
        errors,
    )
    packet_keys: list[tuple[tuple[int, ...], str]] = []
    for index, row in enumerate(rows):
        label = f"d3_escape_frontier_packet.representatives[{index}]"
        expected_id = f"R{index:03d}"
        if row.get("representative_id") != expected_id:
            errors.append(f"{label}.representative_id must be {expected_id}")
        key = _join_key(row, label, errors)
        if key is None:
            continue
        packet_keys.append(key)
        crosswalk_row = crosswalk_by_key.get(key)
        if crosswalk_row is None:
            errors.append(f"{label} has no matching E=6,D=3 crosswalk row")
            continue
        for field in CROSSWALK_JOIN_FIELDS:
            _field_equal(row, crosswalk_row, field, label, "crosswalk", errors)

    if packet_keys and len(set(packet_keys)) != EXPECTED_REPRESENTATIVE_COUNT:
        errors.append("d3_escape_frontier_packet join keys must be unique")
    return rows


def _profile_id_by_multiset(
    d3_crosswalk_rows: Sequence[dict[str, Any]],
    errors: list[str],
) -> dict[tuple[int, ...], str]:
    out: dict[tuple[int, ...], str] = {}
    for index, row in enumerate(d3_crosswalk_rows):
        label = f"low_excess_escape_crosswalk.d3_rows[{index}]"
        profile_id = row.get("profile_ledger_id")
        multiset = _int_list(row.get("excess_multiset"), f"{label}.excess_multiset", errors)
        if not isinstance(profile_id, str) or multiset is None:
            continue
        key = tuple(multiset)
        existing = out.setdefault(key, profile_id)
        if existing != profile_id:
            errors.append(f"{label} profile multiset maps to conflicting profile ids")
    return out


def validate_full_packet_join(
    full_payload: Any,
    packet_rows: Sequence[dict[str, Any]],
    d3_crosswalk_rows: Sequence[dict[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    """Validate the full incidence-capacity packet against packet rows."""

    payload = _object(full_payload, "d3_incidence_capacity_packet", errors)
    if payload is None:
        return []
    rows_value = _list(payload.get("rows"), "d3_incidence_capacity_packet.rows", errors)
    if rows_value is None:
        return []
    rows = _object_rows(rows_value, "d3_incidence_capacity_packet.rows", errors)
    if len(rows_value) != EXPECTED_REPRESENTATIVE_COUNT:
        errors.append("d3_incidence_capacity_packet row count must be 88")
    if len(rows) != EXPECTED_REPRESENTATIVE_COUNT:
        errors.append("d3_incidence_capacity_packet object row count must be 88")

    packet_by_id = {
        row.get("representative_id"): row
        for row in packet_rows
        if isinstance(row.get("representative_id"), str)
    }
    profile_id_by_multiset = _profile_id_by_multiset(d3_crosswalk_rows, errors)
    row_product: list[tuple[str, str]] = []
    for index, row in enumerate(rows):
        label = f"d3_incidence_capacity_packet.rows[{index}]"
        expected_id = f"R{index:03d}"
        if row.get("representative_id") != expected_id:
            errors.append(f"{label}.representative_id must be {expected_id}")
        packet_row = packet_by_id.get(row.get("representative_id"))
        if packet_row is None:
            errors.append(f"{label} has no matching D=3 packet representative")
        else:
            for field in PACKET_JOIN_FIELDS:
                _field_equal(row, packet_row, field, label, "d3 packet", errors)

        multiset = _int_list(row.get("excess_multiset"), f"{label}.excess_multiset", errors)
        profile_id = _str_field(row, "profile_ledger_id", label, errors)
        if multiset is not None and profile_id is not None:
            expected_profile_id = profile_id_by_multiset.get(tuple(multiset))
            if expected_profile_id is not None and profile_id != expected_profile_id:
                errors.append(f"{label}.profile_ledger_id does not match crosswalk")
        escape_id = _str_field(row, "escape_class_id", label, errors)
        if profile_id is not None and escape_id is not None:
            row_product.append((profile_id, escape_id))

    expected_product = [
        (profile_id, escape_id)
        for profile_id in EXPECTED_PROFILE_IDS
        for escape_id in EXPECTED_ESCAPE_IDS
    ]
    if row_product != expected_product:
        errors.append("d3_incidence_capacity_packet rows must be P19..P29 x X00..X07")
    return rows


def _validate_state_rows(
    payload: Any,
    rows: Sequence[dict[str, Any]],
    label: str,
    errors: list[str],
    *,
    rows_have_target_total: bool,
) -> None:
    obj = _object(payload, label, errors)
    if obj is None:
        return
    if obj.get("target_capacity_total") != EXPECTED_TARGET_CAPACITY_TOTAL:
        errors.append(f"{label}.target_capacity_total must be 60")
    for field, expected in (
        ("realizability_state", EXPECTED_REALIZABILITY_STATE),
        ("incidence_state", EXPECTED_INCIDENCE_STATE),
        ("state_scope", EXPECTED_STATE_SCOPE),
    ):
        if obj.get(field) != expected:
            errors.append(f"{label}.{field} must be {expected}")

    for index, row in enumerate(rows):
        row_label = f"{label}.rows[{index}]"
        for field, expected in (
            ("realizability_state", EXPECTED_REALIZABILITY_STATE),
            ("incidence_state", EXPECTED_INCIDENCE_STATE),
            ("state_scope", EXPECTED_STATE_SCOPE),
        ):
            if row.get(field) != expected:
                errors.append(f"{row_label}.{field} must be {expected}")
        if rows_have_target_total and row.get("target_capacity_total") != 60:
            errors.append(f"{row_label}.target_capacity_total must be 60")
        totals = row.get("target_capacity_totals_by_cyclic_length")
        if not isinstance(totals, dict) or not all(strict_int(v) for v in totals.values()):
            errors.append(f"{row_label}.target_capacity_totals_by_cyclic_length must be int totals")
        elif sum(int(value) for value in totals.values()) != 60:
            errors.append(f"{row_label}.target_capacity_totals_by_cyclic_length must sum to 60")


def validate_p19_pilot_join(
    pilot_payload: Any,
    full_rows: Sequence[dict[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    """Validate that the P19 pilot is the R000..R007 full-packet projection."""

    payload = _object(pilot_payload, "d3_p19_incidence_capacity_pilot", errors)
    if payload is None:
        return []
    rows_value = _list(payload.get("rows"), "d3_p19_incidence_capacity_pilot.rows", errors)
    if rows_value is None:
        return []
    rows = _object_rows(rows_value, "d3_p19_incidence_capacity_pilot.rows", errors)
    expected_ids = [f"R{index:03d}" for index in range(8)]
    if payload.get("source_representative_ids") != expected_ids:
        errors.append("d3_p19_incidence_capacity_pilot source ids must be R000..R007")
    if len(rows_value) != 8:
        errors.append("d3_p19_incidence_capacity_pilot row count must be 8")
    if len(rows) != 8:
        errors.append("d3_p19_incidence_capacity_pilot object row count must be 8")

    for index, row in enumerate(rows):
        label = f"d3_p19_incidence_capacity_pilot.rows[{index}]"
        if row.get("representative_id") != expected_ids[index]:
            errors.append(f"{label}.representative_id must be {expected_ids[index]}")
        if index >= len(full_rows):
            errors.append(f"{label} has no matching full-packet row")
            continue
        full_row = full_rows[index]
        expected_projection = {
            field: value
            for field, value in full_row.items()
            if field != "target_capacity_total"
        }
        if set(row) != set(expected_projection):
            errors.append(f"{label} keys do not match full packet R{index:03d} projection")
        for field, value in expected_projection.items():
            if row.get(field) != value:
                errors.append(f"{label}.{field} does not match full packet R{index:03d}")
    return rows


def validate_artifact_stack(artifacts: Mapping[str, Any]) -> list[str]:
    """Return cross-artifact consistency errors for the D=3 bookkeeping stack."""

    errors: list[str] = []
    missing = sorted(set(DEFAULT_ARTIFACT_PATHS) - set(artifacts))
    for key in missing:
        errors.append(f"missing loaded artifact: {key}")
    if missing:
        return errors

    validate_artifact_contracts(artifacts, errors)
    validate_d3_slice(artifacts["d3_escape_slice"], errors)
    d3_crosswalk_rows = validate_crosswalk_slice(
        artifacts["low_excess_escape_crosswalk"],
        errors,
    )
    packet_rows = validate_packet_to_crosswalk_join(
        artifacts["d3_escape_frontier_packet"],
        d3_crosswalk_rows,
        errors,
    )
    full_rows = validate_full_packet_join(
        artifacts["d3_incidence_capacity_packet"],
        packet_rows,
        d3_crosswalk_rows,
        errors,
    )
    pilot_rows = validate_p19_pilot_join(
        artifacts["d3_p19_incidence_capacity_pilot"],
        full_rows,
        errors,
    )
    _validate_state_rows(
        artifacts["d3_incidence_capacity_packet"],
        full_rows,
        "d3_incidence_capacity_packet",
        errors,
        rows_have_target_total=True,
    )
    _validate_state_rows(
        artifacts["d3_p19_incidence_capacity_pilot"],
        pilot_rows,
        "d3_p19_incidence_capacity_pilot",
        errors,
        rows_have_target_total=False,
    )
    return errors


def _sum_row_int(rows: Any, key: str) -> int | None:
    if not isinstance(rows, list):
        return None
    values = [row.get(key) for row in rows if isinstance(row, dict)]
    if len(values) != len(rows) or not all(strict_int(value) for value in values):
        return None
    return sum(int(value) for value in values)


def summary_payload(
    root: Path,
    paths: Mapping[str, Path],
    artifacts: Mapping[str, Any],
    errors: Sequence[str],
) -> dict[str, Any]:
    """Return a compact JSON summary for the cross-artifact checker."""

    crosswalk = artifacts.get("low_excess_escape_crosswalk")
    d3_rows: list[Any] = []
    if isinstance(crosswalk, dict) and isinstance(crosswalk.get("crosswalk_rows"), list):
        d3_rows = [
            row
            for row in crosswalk["crosswalk_rows"]
            if isinstance(row, dict)
            and row.get("total_profile_excess") == TOTAL_PROFILE_EXCESS
            and row.get("capacity_deficit") == CAPACITY_DEFICIT
        ]
    full = artifacts.get("d3_incidence_capacity_packet")
    full_rows = full.get("rows", []) if isinstance(full, dict) else []
    pilot = artifacts.get("d3_p19_incidence_capacity_pilot")
    pilot_rows = pilot.get("rows", []) if isinstance(pilot, dict) else []
    packet = artifacts.get("d3_escape_frontier_packet")
    packet_rows = packet.get("representatives", []) if isinstance(packet, dict) else []
    return {
        "ok": not errors,
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "claim_scope": EXPECTED_CLAIM_SCOPE,
        "artifacts": {
            key: display_path(path, root)
            for key, path in sorted(paths.items())
        },
        "d3_slice": {
            "labelled_profile_sequence_count": _nested_get(
                artifacts,
                "d3_escape_slice",
                "profile_slice",
                "labelled_profile_sequence_count",
            ),
            "labelled_escape_placement_count": _nested_get(
                artifacts,
                "d3_escape_slice",
                "escape_slice",
                "labelled_escape_placement_count",
            ),
            "common_dihedral_pair_class_count": _nested_get(
                artifacts,
                "d3_escape_slice",
                "coupled_slice",
                "common_dihedral_pair_class_count",
            ),
        },
        "d3_packet_representative_count": (
            len(packet_rows) if isinstance(packet_rows, list) else None
        ),
        "d3_crosswalk_row_count": len(d3_rows),
        "d3_crosswalk_common_dihedral_pair_class_count": _sum_row_int(
            d3_rows,
            "common_dihedral_pair_class_count",
        ),
        "full_packet_row_count": len(full_rows) if isinstance(full_rows, list) else None,
        "p19_pilot_row_count": len(pilot_rows) if isinstance(pilot_rows, list) else None,
        "validation_errors": list(errors),
    }


def _nested_get(mapping: Mapping[str, Any], *keys: str) -> Any:
    value: Any = mapping
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value
