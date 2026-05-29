#!/usr/bin/env python3
"""Validate the n=9 base-apex review-pending audit path.

This checker joins existing checked-in artifacts. It does not generate a new
certificate, prove the n=9 case, provide a counterexample, test geometric
realizability, establish incidence completeness, or change the global status.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for candidate in (ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from erdos97.n9_base_apex_d3_artifact_join import (  # noqa: E402
    DEFAULT_ARTIFACT_PATHS as D3_DEFAULT_ARTIFACT_PATHS,
    EXPECTED_INCIDENCE_STATE,
    EXPECTED_REALIZABILITY_STATE,
    validate_artifact_stack as validate_d3_artifact_stack,
)
from erdos97.n9_vertex_circle_exhaustive import (  # noqa: E402
    assert_expected_counts as assert_expected_vertex_circle_counts,
)
from scripts.check_n9_base_apex_escape_budget import (  # noqa: E402
    validate_payload as validate_escape_budget,
)
from scripts.check_n9_base_apex_low_excess_escape_ladder import (  # noqa: E402
    validate_payload as validate_low_excess_ladder,
)
from scripts.check_n9_base_apex_low_excess_ledgers import (  # noqa: E402
    validate_payload as validate_low_excess_ledgers,
)
from scripts.check_n9_selected_baseline_d3_escape_class_crosswalk import (  # noqa: E402
    validate_payload as validate_selected_baseline_d3_crosswalk,
)


EXPECTED_SCHEMA = "erdos97.n9_base_apex_audit_path.v1"
EXPECTED_STATUS = "EXPLORATORY_LEDGER_ONLY"
EXPECTED_TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
EXPECTED_CLAIM_SCOPE = (
    "Reviewer-facing audit path for n=9 base-apex low-excess and D=3 "
    "bookkeeping artifacts joined to the selected-baseline and review-pending "
    "vertex-circle frontier; not a proof of n=9, not a counterexample, not "
    "an incidence-completeness result, not a geometric realizability test, "
    "and not a global status update."
)
REVIEW_SCOPE_NOTES = [
    "The low-excess ledger and escape-budget layers are finite bookkeeping.",
    "The D=3 packet rows keep realizability and incidence states UNKNOWN.",
    "The selected-baseline D=3 landings are not geometric realizability counts.",
    "The vertex-circle frontier remains review-pending and does not promote n=9.",
    "No general proof and no counterexample are claimed.",
]
EXPECTED_HANDOFF_NAMES = [
    "low_excess_to_escape_budget",
    "escape_budget_to_ladder",
    "ladder_to_d3_slice",
    "d3_slice_to_packet_stack",
    "d3_slice_to_selected_baseline",
    "selected_baseline_to_vertex_frontier",
]

DEFAULT_ARTIFACT_PATHS = {
    "low_excess_ledgers": Path(
        "data/certificates/n9_base_apex_low_excess_ledgers.json"
    ),
    "escape_budget": Path("data/certificates/n9_base_apex_escape_budget_report.json"),
    "low_excess_ladder": Path(
        "data/certificates/n9_base_apex_low_excess_escape_ladder.json"
    ),
    "selected_baseline_d3_crosswalk": Path(
        "data/certificates/n9_selected_baseline_d3_escape_class_crosswalk.json"
    ),
    "n9_vertex_circle_exhaustive": Path(
        "data/certificates/n9_vertex_circle_exhaustive.json"
    ),
    **D3_DEFAULT_ARTIFACT_PATHS,
}

D3_ARTIFACT_KEYS = tuple(D3_DEFAULT_ARTIFACT_PATHS)


def strict_int(value: Any) -> bool:
    """Return true only for JSON integers, excluding bool."""

    return type(value) is int


def display_path(path: Path, root: Path = ROOT) -> str:
    """Return a stable repo-relative path when possible."""

    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def resolve_artifact_paths(
    root: Path,
    overrides: Mapping[str, Path] | None = None,
) -> dict[str, Path]:
    """Return absolute artifact paths with optional per-artifact overrides."""

    overrides = overrides or {}
    paths: dict[str, Path] = {}
    for key, default in DEFAULT_ARTIFACT_PATHS.items():
        path = overrides.get(key, default)
        paths[key] = path if path.is_absolute() else root / path
    return paths


def load_json(path: Path) -> Any:
    """Load one JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def load_artifacts(paths: Mapping[str, Path]) -> tuple[dict[str, Any], list[str]]:
    """Load all audit-path artifacts."""

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


def _nested_get(value: Any, *keys: str) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _add_prefixed_errors(
    errors: list[str],
    label: str,
    component_errors: Sequence[str],
) -> None:
    errors.extend(f"{label}: {error}" for error in component_errors)


def _run_validator(
    errors: list[str],
    label: str,
    payload: Any,
    validator: Callable[[Any], list[str]],
) -> None:
    try:
        component_errors = validator(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"{label}: validator raised {exc}")
        return
    _add_prefixed_errors(errors, label, component_errors)


def _expect_equal(
    errors: list[str],
    label: str,
    actual: Any,
    expected: Any,
) -> None:
    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _list_len(value: Any) -> int | None:
    return len(value) if isinstance(value, list) else None


def _sum_int_rows(rows: Any, key: str) -> int | None:
    if not isinstance(rows, list):
        return None
    values = [row.get(key) for row in rows if isinstance(row, dict)]
    if len(values) != len(rows) or not all(strict_int(value) for value in values):
        return None
    return sum(int(value) for value in values)


def _row_matching(rows: Any, key: str, value: Any) -> dict[str, Any] | None:
    if not isinstance(rows, list):
        return None
    for row in rows:
        if isinstance(row, dict) and row.get(key) == value:
            return row
    return None


def _escape_budget_unresolved_count(payload: Any, *, minimum_deficit: int) -> int | None:
    rows = _nested_get(payload, "capacity_deficit_distribution")
    if not isinstance(rows, list):
        return None
    total = 0
    for row in rows:
        if not isinstance(row, dict):
            return None
        capacity_deficit = row.get("capacity_deficit")
        profile_count = row.get("profile_ledger_count")
        if not strict_int(capacity_deficit) or not strict_int(profile_count):
            return None
        if capacity_deficit >= minimum_deficit:
            total += int(profile_count)
    return total


def _placement_count(rows: Any) -> int | None:
    return _sum_int_rows(rows, "placement_count")


def _d3_crosswalk_rows(payload: Any) -> list[dict[str, Any]] | None:
    rows = _nested_get(payload, "crosswalk_rows")
    if not isinstance(rows, list):
        return None
    d3_rows = [
        row
        for row in rows
        if (
            isinstance(row, dict)
            and row.get("total_profile_excess") == 6
            and row.get("capacity_deficit") == 3
        )
    ]
    return d3_rows


def _append_handoff_check(
    handoffs: list[dict[str, Any]],
    errors: list[str],
    *,
    name: str,
    description: str,
    evidence: Mapping[str, Any],
    local_errors: Sequence[str],
) -> None:
    handoffs.append(
        {
            "name": name,
            "ok": not local_errors,
            "description": description,
            "evidence": dict(evidence),
            "errors": list(local_errors),
        }
    )
    errors.extend(f"{name}: {error}" for error in local_errors)


def _check_match(
    local_errors: list[str],
    label: str,
    actual: Any,
    expected: Any,
) -> None:
    if actual != expected:
        local_errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def evaluate_handoff_checks(
    artifacts: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Return named review handoff checks and validation errors."""

    handoffs: list[dict[str, Any]] = []
    errors: list[str] = []

    low = artifacts.get("low_excess_ledgers")
    escape = artifacts.get("escape_budget")
    ladder = artifacts.get("low_excess_ladder")
    selected = artifacts.get("selected_baseline_d3_crosswalk")
    vertex = artifacts.get("n9_vertex_circle_exhaustive")
    d3_slice = artifacts.get("d3_escape_slice")
    d3_crosswalk = artifacts.get("low_excess_escape_crosswalk")
    d3_packet = artifacts.get("d3_escape_frontier_packet")
    full_packet = artifacts.get("d3_incidence_capacity_packet")
    p19_pilot = artifacts.get("d3_p19_incidence_capacity_pilot")

    strict_low_motifs = _nested_get(low, "strict_minimum_escape_motif_classes")
    conservative_low_motifs = _nested_get(
        low,
        "conservative_minimum_escape_motif_classes",
    )
    strict_budget_motifs = _nested_get(
        escape,
        "strict_positive_threshold",
        "minimum_escape_motif_classes",
    )
    conservative_budget_motifs = _nested_get(
        escape,
        "sum_exceeds_threshold",
        "minimum_escape_motif_classes",
    )
    local_errors: list[str] = []
    _check_match(local_errors, "n", _nested_get(low, "n"), _nested_get(escape, "n"))
    _check_match(
        local_errors,
        "witness_size",
        _nested_get(low, "witness_size"),
        _nested_get(escape, "witness_size"),
    )
    _check_match(
        local_errors,
        "low unresolved D>=3 ledger count",
        _nested_get(low, "strict_unresolved_profile_ledger_count"),
        _escape_budget_unresolved_count(escape, minimum_deficit=3),
    )
    _check_match(
        local_errors,
        "strict escape motif class count",
        _list_len(strict_low_motifs),
        _list_len(strict_budget_motifs),
    )
    _check_match(
        local_errors,
        "strict escape motif labelled placement count",
        _placement_count(strict_low_motifs),
        _placement_count(strict_budget_motifs),
    )
    _check_match(
        local_errors,
        "conservative escape motif class count",
        _list_len(conservative_low_motifs),
        _list_len(conservative_budget_motifs),
    )
    _append_handoff_check(
        handoffs,
        errors,
        name="low_excess_to_escape_budget",
        description=(
            "Low-excess ledger counts agree with the escape-budget view of "
            "strict D>=3 unresolved profiles and minimum escape motifs."
        ),
        evidence={
            "low_unresolved_profile_ledger_count": _nested_get(
                low,
                "strict_unresolved_profile_ledger_count",
            ),
            "escape_budget_d_ge_3_profile_ledger_count": (
                _escape_budget_unresolved_count(escape, minimum_deficit=3)
            ),
            "strict_escape_motif_class_count": _list_len(strict_low_motifs),
            "strict_escape_motif_labelled_placement_count": _placement_count(
                strict_low_motifs
            ),
            "conservative_escape_motif_class_count": _list_len(
                conservative_low_motifs
            ),
        },
        local_errors=local_errors,
    )

    ladder_rows = _nested_get(ladder, "ladder_rows")
    strict_escape_slice = _nested_get(ladder, "strict_escape_slice")
    local_errors = []
    _check_match(
        local_errors,
        "low unresolved ledger count vs ladder row sum",
        _nested_get(low, "strict_unresolved_profile_ledger_count"),
        _sum_int_rows(ladder_rows, "unlabeled_profile_ledger_count"),
    )
    _check_match(
        local_errors,
        "minimum relevant deficit",
        _nested_get(
            escape,
            "strict_positive_threshold",
            "minimum_relevant_deficit_count_to_spoil",
        ),
        _nested_get(ladder, "strict_minimal_relevant_escape"),
    )
    _check_match(
        local_errors,
        "strict escape class count",
        _list_len(strict_budget_motifs),
        _nested_get(strict_escape_slice, "dihedral_escape_class_count"),
    )
    _check_match(
        local_errors,
        "strict escape labelled placement count",
        _placement_count(strict_budget_motifs),
        _nested_get(strict_escape_slice, "labelled_escape_placement_count"),
    )
    _append_handoff_check(
        handoffs,
        errors,
        name="escape_budget_to_ladder",
        description=(
            "The low-excess ladder packages the strict escape-budget threshold "
            "and sums exactly the unresolved low-excess profile ledgers."
        ),
        evidence={
            "ladder_rung_count": _list_len(ladder_rows),
            "ladder_unlabeled_profile_ledger_count": _sum_int_rows(
                ladder_rows,
                "unlabeled_profile_ledger_count",
            ),
            "strict_minimal_relevant_escape": _nested_get(
                ladder,
                "strict_minimal_relevant_escape",
            ),
            "strict_escape_class_count": _nested_get(
                strict_escape_slice,
                "dihedral_escape_class_count",
            ),
            "strict_escape_labelled_placement_count": _nested_get(
                strict_escape_slice,
                "labelled_escape_placement_count",
            ),
        },
        local_errors=local_errors,
    )

    d3_ladder_row = _row_matching(ladder_rows, "total_profile_excess", 6)
    local_errors = []
    _check_match(
        local_errors,
        "D=3 ladder capacity deficit",
        _nested_get(d3_ladder_row, "capacity_deficit"),
        3,
    )
    _check_match(
        local_errors,
        "D=3 labelled profile sequence count",
        _nested_get(d3_ladder_row, "labelled_profile_sequence_count"),
        _nested_get(d3_slice, "profile_slice", "labelled_profile_sequence_count"),
    )
    _check_match(
        local_errors,
        "D=3 common-dihedral class count",
        _nested_get(d3_ladder_row, "common_dihedral_pair_class_count"),
        _nested_get(d3_slice, "coupled_slice", "common_dihedral_pair_class_count"),
    )
    _check_match(
        local_errors,
        "D=3 labelled escape placement count",
        _nested_get(strict_escape_slice, "labelled_escape_placement_count"),
        _nested_get(d3_slice, "escape_slice", "labelled_escape_placement_count"),
    )
    _append_handoff_check(
        handoffs,
        errors,
        name="ladder_to_d3_slice",
        description=(
            "The E=6, D=3 ladder rung agrees with the dedicated D=3 escape "
            "slice on profile, escape, and coupled class counts."
        ),
        evidence={
            "total_profile_excess": _nested_get(
                d3_ladder_row,
                "total_profile_excess",
            ),
            "capacity_deficit": _nested_get(d3_ladder_row, "capacity_deficit"),
            "labelled_profile_sequence_count": _nested_get(
                d3_ladder_row,
                "labelled_profile_sequence_count",
            ),
            "labelled_escape_placement_count": _nested_get(
                strict_escape_slice,
                "labelled_escape_placement_count",
            ),
            "common_dihedral_pair_class_count": _nested_get(
                d3_ladder_row,
                "common_dihedral_pair_class_count",
            ),
        },
        local_errors=local_errors,
    )

    d3_rows = _d3_crosswalk_rows(d3_crosswalk)
    full_rows = _nested_get(full_packet, "rows")
    pilot_rows = _nested_get(p19_pilot, "rows")
    local_errors = []
    _check_match(
        local_errors,
        "D=3 crosswalk row count",
        _list_len(d3_rows),
        _nested_get(d3_packet, "representative_count"),
    )
    _check_match(
        local_errors,
        "D=3 packet vs full packet representative count",
        _nested_get(d3_packet, "representative_count"),
        _nested_get(full_packet, "representative_count"),
    )
    _check_match(
        local_errors,
        "full packet row count",
        _list_len(full_rows),
        _nested_get(full_packet, "representative_count"),
    )
    _check_match(
        local_errors,
        "D=3 class count",
        _nested_get(d3_slice, "coupled_slice", "common_dihedral_pair_class_count"),
        _nested_get(d3_packet, "common_dihedral_pair_class_count"),
    )
    _check_match(
        local_errors,
        "P19 pilot row count",
        _list_len(pilot_rows),
        _nested_get(p19_pilot, "representative_count"),
    )
    _check_match(
        local_errors,
        "full packet realizability state",
        _nested_get(full_packet, "realizability_state"),
        EXPECTED_REALIZABILITY_STATE,
    )
    _check_match(
        local_errors,
        "full packet incidence state",
        _nested_get(full_packet, "incidence_state"),
        EXPECTED_INCIDENCE_STATE,
    )
    _append_handoff_check(
        handoffs,
        errors,
        name="d3_slice_to_packet_stack",
        description=(
            "The D=3 slice, representative packet, P19 pilot, and all-row "
            "incidence-capacity packet keep the same 88-row bookkeeping stack."
        ),
        evidence={
            "d3_crosswalk_row_count": _list_len(d3_rows),
            "d3_packet_representative_count": _nested_get(
                d3_packet,
                "representative_count",
            ),
            "full_packet_row_count": _list_len(full_rows),
            "p19_pilot_row_count": _list_len(pilot_rows),
            "d3_common_dihedral_pair_class_count": _nested_get(
                d3_slice,
                "coupled_slice",
                "common_dihedral_pair_class_count",
            ),
            "realizability_state": _nested_get(full_packet, "realizability_state"),
            "incidence_state": _nested_get(full_packet, "incidence_state"),
        },
        local_errors=local_errors,
    )

    local_errors = []
    _check_match(
        local_errors,
        "selected-baseline D=3 capacity budget",
        _nested_get(selected, "capacity_deficit_budget"),
        _nested_get(d3_slice, "profile_slice", "capacity_deficit"),
    )
    _check_match(
        local_errors,
        "selected-baseline escape class count",
        _nested_get(selected, "escape_class_count"),
        _nested_get(d3_slice, "escape_slice", "dihedral_escape_class_count"),
    )
    _check_match(
        local_errors,
        "non-comparable D=3 reference count",
        _nested_get(
            selected,
            "crosswalk_summary",
            "not_comparable_reference_common_dihedral_profile_escape_class_count",
        ),
        _nested_get(d3_slice, "coupled_slice", "common_dihedral_pair_class_count"),
    )
    _append_handoff_check(
        handoffs,
        errors,
        name="d3_slice_to_selected_baseline",
        description=(
            "The selected-baseline D=3 crosswalk points back to the same "
            "D=3 profile/escape reference while keeping the counts "
            "non-comparable."
        ),
        evidence={
            "capacity_deficit_budget": _nested_get(
                selected,
                "capacity_deficit_budget",
            ),
            "escape_class_count": _nested_get(selected, "escape_class_count"),
            "not_comparable_reference_count": _nested_get(
                selected,
                "crosswalk_summary",
                "not_comparable_reference_common_dihedral_profile_escape_class_count",
            ),
            "d3_common_dihedral_pair_class_count": _nested_get(
                d3_slice,
                "coupled_slice",
                "common_dihedral_pair_class_count",
            ),
        },
        local_errors=local_errors,
    )

    vertex_cross_check = _nested_get(
        vertex,
        "cross_check_without_vertex_circle_pruning",
    )
    assignment_count = _nested_get(selected, "assignment_count")
    forced = _nested_get(selected, "forced_budget3_slot_choice_count")
    escaping = _nested_get(selected, "escaping_budget3_slot_choice_count")
    total_slot_choices = _nested_get(selected, "total_budget3_slot_choice_count")
    self_edge_count = _nested_get(vertex_cross_check, "counts", "self_edge")
    strict_cycle_count = _nested_get(vertex_cross_check, "counts", "strict_cycle")
    local_errors = []
    _check_match(
        local_errors,
        "selected-baseline assignment count",
        assignment_count,
        _nested_get(vertex_cross_check, "full_assignments"),
    )
    _check_match(
        local_errors,
        "selected-baseline slot-choice arithmetic",
        total_slot_choices,
        assignment_count * 84 if strict_int(assignment_count) else None,
    )
    _check_match(
        local_errors,
        "selected-baseline forced plus escaping slot choices",
        forced + escaping if strict_int(forced) and strict_int(escaping) else None,
        total_slot_choices,
    )
    _check_match(
        local_errors,
        "vertex frontier obstruction partition",
        self_edge_count + strict_cycle_count
        if strict_int(self_edge_count) and strict_int(strict_cycle_count)
        else None,
        _nested_get(vertex_cross_check, "full_assignments"),
    )
    _check_match(
        local_errors,
        "vertex-circle pruned main search full assignments",
        _nested_get(vertex, "main_search", "full_assignments"),
        0,
    )
    _append_handoff_check(
        handoffs,
        errors,
        name="selected_baseline_to_vertex_frontier",
        description=(
            "The selected-baseline D=3 rows land on the same 184 "
            "pre-vertex-circle frontier assignments and preserve the "
            "review-pending self-edge/strict-cycle partition."
        ),
        evidence={
            "assignment_count": assignment_count,
            "total_budget3_slot_choice_count": total_slot_choices,
            "forced_budget3_slot_choice_count": forced,
            "escaping_budget3_slot_choice_count": escaping,
            "vertex_frontier_assignment_count": _nested_get(
                vertex_cross_check,
                "full_assignments",
            ),
            "self_edge_count": self_edge_count,
            "strict_cycle_count": strict_cycle_count,
            "main_full_assignments": _nested_get(
                vertex,
                "main_search",
                "full_assignments",
            ),
        },
        local_errors=local_errors,
    )

    return handoffs, errors


def validate_vertex_circle_artifact(payload: Any) -> list[str]:
    """Return validation errors for the stored n=9 vertex-circle artifact."""

    if not isinstance(payload, dict):
        return ["n9_vertex_circle_exhaustive must be a JSON object"]
    errors: list[str] = []
    try:
        assert_expected_vertex_circle_counts(payload)
    except AssertionError as exc:
        errors.append(f"expected-count replay failed: {exc}")

    _expect_equal(
        errors,
        "n9_vertex_circle_exhaustive.trust",
        payload.get("trust"),
        "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING",
    )
    scope = payload.get("scope")
    if not isinstance(scope, str):
        errors.append("n9_vertex_circle_exhaustive.scope must be a string")
    else:
        lowered = scope.lower()
        for phrase in (
            "candidate repo-local",
            "does not update",
            "official/global",
        ):
            if phrase not in lowered:
                errors.append(
                    f"n9_vertex_circle_exhaustive.scope must include {phrase!r}"
                )
    return errors


def validate_cross_links(artifacts: Mapping[str, Any]) -> list[str]:
    """Return audit-path cross-artifact consistency errors."""

    errors: list[str] = []
    low = artifacts.get("low_excess_ledgers")
    escape = artifacts.get("escape_budget")
    ladder = artifacts.get("low_excess_ladder")
    selected = artifacts.get("selected_baseline_d3_crosswalk")
    vertex = artifacts.get("n9_vertex_circle_exhaustive")
    d3_slice = artifacts.get("d3_escape_slice")
    full_packet = artifacts.get("d3_incidence_capacity_packet")
    p19_pilot = artifacts.get("d3_p19_incidence_capacity_pilot")

    _expect_equal(
        errors,
        "low_excess strict unresolved ledger count",
        _nested_get(low, "strict_unresolved_profile_ledger_count"),
        30,
    )
    _expect_equal(
        errors,
        "escape budget strict minimum relevant deficit",
        _nested_get(
            escape,
            "strict_positive_threshold",
            "minimum_relevant_deficit_count_to_spoil",
        ),
        3,
    )

    ladder_rows = _nested_get(ladder, "ladder_rows")
    d3_ladder_row = None
    if isinstance(ladder_rows, list):
        for row in ladder_rows:
            if isinstance(row, dict) and row.get("total_profile_excess") == 6:
                d3_ladder_row = row
                break
    if d3_ladder_row is None:
        errors.append("low_excess_ladder is missing the E=6 D=3 rung")
    else:
        _expect_equal(
            errors,
            "ladder E=6 labelled profile sequence count",
            d3_ladder_row.get("labelled_profile_sequence_count"),
            _nested_get(
                d3_slice,
                "profile_slice",
                "labelled_profile_sequence_count",
            ),
        )
        _expect_equal(
            errors,
            "ladder E=6 common-dihedral class count",
            d3_ladder_row.get("common_dihedral_pair_class_count"),
            _nested_get(
                d3_slice,
                "coupled_slice",
                "common_dihedral_pair_class_count",
            ),
        )

    vertex_cross_check = _nested_get(
        vertex,
        "cross_check_without_vertex_circle_pruning",
    )
    if not isinstance(vertex_cross_check, dict):
        errors.append("n9 vertex-circle cross-check summary is missing")
    else:
        _expect_equal(
            errors,
            "selected-baseline assignment count vs vertex frontier",
            _nested_get(selected, "assignment_count"),
            vertex_cross_check.get("full_assignments"),
        )
        _expect_equal(
            errors,
            "vertex frontier self-edge count",
            _nested_get(vertex_cross_check, "counts", "self_edge"),
            158,
        )
        _expect_equal(
            errors,
            "vertex frontier strict-cycle count",
            _nested_get(vertex_cross_check, "counts", "strict_cycle"),
            26,
        )

    assignment_count = _nested_get(selected, "assignment_count")
    total_slot_choices = _nested_get(selected, "total_budget3_slot_choice_count")
    if strict_int(assignment_count) and strict_int(total_slot_choices):
        _expect_equal(
            errors,
            "selected-baseline D=3 slot-choice arithmetic",
            total_slot_choices,
            assignment_count * 84,
        )
    else:
        errors.append("selected-baseline D=3 slot-choice counts must be ints")
    forced = _nested_get(selected, "forced_budget3_slot_choice_count")
    escaping = _nested_get(selected, "escaping_budget3_slot_choice_count")
    if strict_int(forced) and strict_int(escaping) and strict_int(total_slot_choices):
        _expect_equal(
            errors,
            "selected-baseline forced+escaping slot choices",
            forced + escaping,
            total_slot_choices,
        )
    else:
        errors.append("selected-baseline forced/escaping counts must be ints")

    _expect_equal(
        errors,
        "selected-baseline non-comparable D=3 reference",
        _nested_get(
            selected,
            "crosswalk_summary",
            "not_comparable_reference_common_dihedral_profile_escape_class_count",
        ),
        _nested_get(
            d3_slice,
            "coupled_slice",
            "common_dihedral_pair_class_count",
        ),
    )
    _expect_equal(
        errors,
        "full packet realizability state",
        _nested_get(full_packet, "realizability_state"),
        EXPECTED_REALIZABILITY_STATE,
    )
    _expect_equal(
        errors,
        "full packet incidence state",
        _nested_get(full_packet, "incidence_state"),
        EXPECTED_INCIDENCE_STATE,
    )
    _expect_equal(
        errors,
        "P19 pilot realizability state",
        _nested_get(p19_pilot, "realizability_state"),
        EXPECTED_REALIZABILITY_STATE,
    )
    _expect_equal(
        errors,
        "P19 pilot incidence state",
        _nested_get(p19_pilot, "incidence_state"),
        EXPECTED_INCIDENCE_STATE,
    )
    _handoff_checks, handoff_errors = evaluate_handoff_checks(artifacts)
    errors.extend(handoff_errors)
    return errors


def validate_audit_path(artifacts: Mapping[str, Any]) -> list[str]:
    """Return validation errors for the complete base-apex audit path."""

    errors: list[str] = []
    missing = sorted(set(DEFAULT_ARTIFACT_PATHS) - set(artifacts))
    for key in missing:
        errors.append(f"missing loaded artifact: {key}")
    if missing:
        return errors

    _run_validator(
        errors,
        "low_excess_ledgers",
        artifacts["low_excess_ledgers"],
        validate_low_excess_ledgers,
    )
    _run_validator(
        errors,
        "escape_budget",
        artifacts["escape_budget"],
        validate_escape_budget,
    )
    _run_validator(
        errors,
        "low_excess_ladder",
        artifacts["low_excess_ladder"],
        validate_low_excess_ladder,
    )
    _run_validator(
        errors,
        "selected_baseline_d3_crosswalk",
        artifacts["selected_baseline_d3_crosswalk"],
        validate_selected_baseline_d3_crosswalk,
    )
    _run_validator(
        errors,
        "n9_vertex_circle_exhaustive",
        artifacts["n9_vertex_circle_exhaustive"],
        validate_vertex_circle_artifact,
    )

    d3_artifacts = {key: artifacts[key] for key in D3_ARTIFACT_KEYS}
    _add_prefixed_errors(
        errors,
        "d3_artifact_stack",
        validate_d3_artifact_stack(d3_artifacts),
    )
    errors.extend(validate_cross_links(artifacts))
    return errors


def summary_payload(
    root: Path,
    paths: Mapping[str, Path],
    artifacts: Mapping[str, Any],
    errors: Sequence[str],
) -> dict[str, Any]:
    """Return a stable compact audit-path summary."""

    vertex_cross_check = _nested_get(
        artifacts,
        "n9_vertex_circle_exhaustive",
        "cross_check_without_vertex_circle_pruning",
    )
    selected_summary = _nested_get(
        artifacts,
        "selected_baseline_d3_crosswalk",
        "crosswalk_summary",
    )
    return {
        "ok": not errors,
        "schema": EXPECTED_SCHEMA,
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "claim_scope": EXPECTED_CLAIM_SCOPE,
        "review_scope_notes": REVIEW_SCOPE_NOTES,
        "handoff_checks": evaluate_handoff_checks(artifacts)[0],
        "artifacts": {
            key: display_path(path, root)
            for key, path in sorted(paths.items())
        },
        "base_apex": {
            "strict_unresolved_profile_ledger_count": _nested_get(
                artifacts,
                "low_excess_ledgers",
                "strict_unresolved_profile_ledger_count",
            ),
            "strict_minimum_relevant_deficit_count_to_spoil": _nested_get(
                artifacts,
                "escape_budget",
                "strict_positive_threshold",
                "minimum_relevant_deficit_count_to_spoil",
            ),
            "low_excess_ladder_rung_count": len(
                _nested_get(artifacts, "low_excess_ladder", "ladder_rows") or []
            ),
            "d3_representative_count": _nested_get(
                artifacts,
                "d3_escape_frontier_packet",
                "representative_count",
            ),
            "d3_common_dihedral_pair_class_count": _nested_get(
                artifacts,
                "d3_escape_slice",
                "coupled_slice",
                "common_dihedral_pair_class_count",
            ),
            "d3_realizability_state": _nested_get(
                artifacts,
                "d3_incidence_capacity_packet",
                "realizability_state",
            ),
            "d3_incidence_state": _nested_get(
                artifacts,
                "d3_incidence_capacity_packet",
                "incidence_state",
            ),
        },
        "selected_baseline_d3": {
            "assignment_count": _nested_get(
                artifacts,
                "selected_baseline_d3_crosswalk",
                "assignment_count",
            ),
            "selected_baseline_class_count": _nested_get(
                artifacts,
                "selected_baseline_d3_crosswalk",
                "selected_baseline_class_count",
            ),
            "escape_class_count": _nested_get(
                artifacts,
                "selected_baseline_d3_crosswalk",
                "escape_class_count",
            ),
            "total_budget3_slot_choice_count": _nested_get(
                artifacts,
                "selected_baseline_d3_crosswalk",
                "total_budget3_slot_choice_count",
            ),
            "forced_budget3_slot_choice_count": _nested_get(
                artifacts,
                "selected_baseline_d3_crosswalk",
                "forced_budget3_slot_choice_count",
            ),
            "escaping_budget3_slot_choice_count": _nested_get(
                artifacts,
                "selected_baseline_d3_crosswalk",
                "escaping_budget3_slot_choice_count",
            ),
            "nonzero_crosswalk_cell_count": (
                selected_summary.get("nonzero_crosswalk_cell_count")
                if isinstance(selected_summary, dict)
                else None
            ),
        },
        "vertex_circle_frontier": {
            "trust": _nested_get(
                artifacts,
                "n9_vertex_circle_exhaustive",
                "trust",
            ),
            "row0_choices": (
                vertex_cross_check.get("row0_choices")
                if isinstance(vertex_cross_check, dict)
                else None
            ),
            "frontier_assignment_count": (
                vertex_cross_check.get("full_assignments")
                if isinstance(vertex_cross_check, dict)
                else None
            ),
            "self_edge_count": (
                _nested_get(vertex_cross_check, "counts", "self_edge")
                if isinstance(vertex_cross_check, dict)
                else None
            ),
            "strict_cycle_count": (
                _nested_get(vertex_cross_check, "counts", "strict_cycle")
                if isinstance(vertex_cross_check, dict)
                else None
            ),
            "main_full_assignments": _nested_get(
                artifacts,
                "n9_vertex_circle_exhaustive",
                "main_search",
                "full_assignments",
            ),
        },
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for key, default_path in DEFAULT_ARTIFACT_PATHS.items():
        parser.add_argument(
            f"--{key.replace('_', '-')}",
            type=Path,
            default=default_path,
            help=f"Path to {key}.",
        )
    parser.add_argument("--check", action="store_true", help="fail if validation fails")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print stable JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print stable compact reviewer-facing JSON",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    overrides = {
        key: getattr(args, key)
        for key in DEFAULT_ARTIFACT_PATHS
    }
    paths = resolve_artifact_paths(ROOT, overrides)
    artifacts, errors = load_artifacts(paths)
    if not errors:
        errors = validate_audit_path(artifacts)
    summary = summary_payload(ROOT, paths, artifacts, errors)

    if args.json or args.summary_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print("FAILED: n=9 base-apex audit path", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 base-apex audit path")
        print(f"scope: {EXPECTED_CLAIM_SCOPE}")
        base = summary["base_apex"]
        selected = summary["selected_baseline_d3"]
        frontier = summary["vertex_circle_frontier"]
        print(
            "base-apex: "
            f"low-ledgers={base['strict_unresolved_profile_ledger_count']}, "
            f"D=3 rows={base['d3_representative_count']}, "
            f"D=3 classes={base['d3_common_dihedral_pair_class_count']}"
        )
        print(
            "selected baseline: "
            f"assignments={selected['assignment_count']}, "
            f"slot choices={selected['total_budget3_slot_choice_count']}, "
            f"escaping={selected['escaping_budget3_slot_choice_count']}"
        )
        print(
            "vertex frontier: "
            f"assignments={frontier['frontier_assignment_count']}, "
            f"self-edge={frontier['self_edge_count']}, "
            f"strict-cycle={frontier['strict_cycle_count']}"
        )
        if args.check:
            print("OK: n=9 base-apex audit path checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
