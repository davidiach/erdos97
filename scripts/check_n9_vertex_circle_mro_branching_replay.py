#!/usr/bin/env python3
"""Fixed-order replay audit for the n=9 vertex-circle MRO brancher."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97 import n9_vertex_circle_exhaustive as n9  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402

SCHEMA = "erdos97.n9_vertex_circle_mro_branching_replay.v1"
STATUS = "REVIEW_PENDING_BRANCHING_REPLAY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Fixed-center-order replay audit for the review-pending n=9 "
    "vertex-circle exhaustive checker. It compares the dynamic "
    "minimum-remaining-options artifact with a deterministic center order "
    "0,1,...,8 while reusing the same necessary-filter helpers. It does not "
    "prove the filters, does not independently replay vertex-circle "
    "geometry, does not prove n=9, does not claim a counterexample, and does "
    "not update the official/global status."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_mro_branching_replay.py",
    "command": (
        "python scripts/check_n9_vertex_circle_mro_branching_replay.py "
        "--check --assert-expected --json"
    ),
}

DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "n9_vertex_circle_exhaustive.json"
EXPECTED_FIXED_MAIN_NODES = 37_544
EXPECTED_FIXED_MAIN_FULL = 0
EXPECTED_FIXED_MAIN_COUNTS = {
    "partial_self_edge": 34_445,
    "partial_strict_cycle": 35_029,
}
EXPECTED_FIXED_CROSS_NODES = 520_782
EXPECTED_FIXED_CROSS_FULL = 184
EXPECTED_FIXED_CROSS_COUNTS = {
    "self_edge": 158,
    "strict_cycle": 26,
}


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def fixed_center_order_search(use_vertex_circle: bool) -> dict[str, Any]:
    """Run the n=9 search with center order 0,1,...,8 after fixed row 0."""

    nodes = 0
    full = 0
    counts: Counter[str] = Counter()

    def search(
        assign: n9.Assignment,
        column_counts: list[int],
        witness_pair_counts: list[int],
    ) -> None:
        nonlocal nodes, full
        nodes += 1
        if len(assign) == n9.N:
            full += 1
            if use_vertex_circle:
                counts["full_survivor"] += 1
            else:
                counts[n9.vertex_circle_status(assign)] += 1
            return

        center = next(candidate for candidate in range(n9.N) if candidate not in assign)
        options = n9.valid_options_for_center(
            center,
            assign,
            column_counts,
            witness_pair_counts,
        )
        if not options:
            return

        for row_mask in options:
            assign[center] = row_mask
            for target in n9.MASK_BITS[row_mask]:
                column_counts[target] += 1
            for pair_index in n9.ROW_PAIR_INDICES[row_mask]:
                witness_pair_counts[pair_index] += 1

            status = n9.vertex_circle_status(assign) if use_vertex_circle else "ok"
            if status == "ok":
                search(assign, column_counts, witness_pair_counts)
            else:
                counts[f"partial_{status}"] += 1

            for pair_index in n9.ROW_PAIR_INDICES[row_mask]:
                witness_pair_counts[pair_index] -= 1
            for target in n9.MASK_BITS[row_mask]:
                column_counts[target] -= 1
            del assign[center]

    for row0 in n9.OPTIONS[0]:
        assign: n9.Assignment = {0: row0}
        column_counts = [0] * n9.N
        witness_pair_counts = [0] * len(n9.PAIRS)
        for target in n9.MASK_BITS[row0]:
            column_counts[target] += 1
        for pair_index in n9.ROW_PAIR_INDICES[row0]:
            witness_pair_counts[pair_index] += 1
        if n9.vertex_circle_status(assign) == "ok":
            search(assign, column_counts, witness_pair_counts)

    return {
        "row_order_rule": "fixed_center_order",
        "vertex_circle_pruning": use_vertex_circle,
        "row0_choices": len(n9.OPTIONS[0]),
        "nodes_visited": nodes,
        "full_assignments": full,
        "counts": dict(sorted(counts.items())),
    }


def mro_branching_replay_payload(
    artifact: Mapping[str, Any],
    *,
    artifact_path: Path = DEFAULT_ARTIFACT,
) -> dict[str, Any]:
    """Return a fixed-order replay audit for the dynamic-MRO artifact."""

    errors: list[str] = []
    try:
        n9.assert_expected_counts(dict(artifact))
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"stored MRO artifact expected-count check failed: {exc}")

    fixed_main = fixed_center_order_search(use_vertex_circle=True)
    fixed_cross = fixed_center_order_search(use_vertex_circle=False)
    _audit_fixed_counts(fixed_main, fixed_cross, errors)
    comparison = _comparison_summary(artifact, fixed_main, fixed_cross, errors)

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifact": {
            "path": display_path(artifact_path, ROOT),
            "type": artifact.get("type"),
            "trust": artifact.get("trust"),
        },
        "review_independence": {
            "uses_dynamic_mro_brancher": False,
            "uses_shared_filter_helpers": True,
            "uses_vertex_circle_status_helper": True,
            "method": (
                "Runs a separate recursive search that always picks the "
                "lowest unassigned center after row 0, then compares full "
                "assignment counts and vertex-circle classifications to the "
                "stored dynamic-MRO artifact."
            ),
        },
        "dynamic_mro_summary": _source_summary(artifact, errors),
        "fixed_center_order_main": fixed_main,
        "fixed_center_order_cross_check": fixed_cross,
        "comparison_summary": comparison,
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed replay says the fixed center order and dynamic "
            "minimum-remaining-options order agree on the closed main search "
            "and on the 184 pre-vertex-circle frontier classifications. It "
            "does not prove the pruning lemmas or complete n=9 review."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_mro_branching_replay(payload: Mapping[str, Any]) -> None:
    """Assert the expected fixed-order replay audit result."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    if payload.get("provenance") != PROVENANCE:
        raise AssertionError(f"provenance mismatch: {payload.get('provenance')!r}")
    if payload.get("claim_scope") != CLAIM_SCOPE:
        raise AssertionError(f"claim_scope mismatch: {payload.get('claim_scope')!r}")
    claim_scope = CLAIM_SCOPE
    for required in (
        "does not prove the filters",
        "does not independently replay vertex-circle geometry",
        "does not prove n=9",
        "does not claim a counterexample",
        "does not update the official/global status",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    review = payload.get("review_independence")
    if not isinstance(review, Mapping):
        raise AssertionError("review_independence must be an object")
    if review.get("uses_dynamic_mro_brancher") is not False:
        raise AssertionError("replay must not call the dynamic MRO brancher")
    if review.get("uses_shared_filter_helpers") is not True:
        raise AssertionError("replay scope must disclose shared filter helpers")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")

    comparison = payload.get("comparison_summary")
    if not isinstance(comparison, Mapping):
        raise AssertionError("comparison_summary must be an object")
    expected = {
        "row0_choices_match": True,
        "main_full_assignments_match": True,
        "cross_check_full_assignments_match": True,
        "cross_check_status_counts_match": True,
        "dynamic_mro_main_nodes": n9.EXPECTED_MAIN_NODES,
        "fixed_order_main_nodes": EXPECTED_FIXED_MAIN_NODES,
        "dynamic_mro_cross_check_nodes": n9.EXPECTED_CROSS_CHECK_NODES,
        "fixed_order_cross_check_nodes": EXPECTED_FIXED_CROSS_NODES,
    }
    for key, value in expected.items():
        if comparison.get(key) != value:
            raise AssertionError(
                f"comparison_summary[{key!r}] mismatch: expected {value!r}, "
                f"got {comparison.get(key)!r}"
            )


def _audit_fixed_counts(
    fixed_main: Mapping[str, Any],
    fixed_cross: Mapping[str, Any],
    errors: list[str],
) -> None:
    _check_equal(errors, "fixed main nodes", fixed_main.get("nodes_visited"), EXPECTED_FIXED_MAIN_NODES)
    _check_equal(errors, "fixed main full", fixed_main.get("full_assignments"), EXPECTED_FIXED_MAIN_FULL)
    _check_equal(errors, "fixed main counts", fixed_main.get("counts"), EXPECTED_FIXED_MAIN_COUNTS)
    _check_equal(errors, "fixed cross nodes", fixed_cross.get("nodes_visited"), EXPECTED_FIXED_CROSS_NODES)
    _check_equal(errors, "fixed cross full", fixed_cross.get("full_assignments"), EXPECTED_FIXED_CROSS_FULL)
    _check_equal(errors, "fixed cross counts", fixed_cross.get("counts"), EXPECTED_FIXED_CROSS_COUNTS)


def _source_summary(artifact: Mapping[str, Any], errors: list[str]) -> dict[str, Any]:
    main = _mapping_field(artifact, "main_search", errors)
    cross = _mapping_field(artifact, "cross_check_without_vertex_circle_pruning", errors)
    return {
        "row_order_rule": "dynamic_minimum_remaining_options",
        "main": {
            "row0_choices": main.get("row0_choices"),
            "nodes_visited": main.get("nodes_visited"),
            "full_assignments": main.get("full_assignments"),
            "counts": main.get("counts"),
        },
        "cross_check": {
            "row0_choices": cross.get("row0_choices"),
            "nodes_visited": cross.get("nodes_visited"),
            "full_assignments": cross.get("full_assignments"),
            "counts": cross.get("counts"),
        },
    }


def _comparison_summary(
    artifact: Mapping[str, Any],
    fixed_main: Mapping[str, Any],
    fixed_cross: Mapping[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    main = _mapping_field(artifact, "main_search", errors)
    cross = _mapping_field(artifact, "cross_check_without_vertex_circle_pruning", errors)
    row0_choices_match = (
        main.get("row0_choices")
        == cross.get("row0_choices")
        == fixed_main.get("row0_choices")
        == fixed_cross.get("row0_choices")
    )
    main_full_match = main.get("full_assignments") == fixed_main.get("full_assignments")
    cross_full_match = cross.get("full_assignments") == fixed_cross.get("full_assignments")
    cross_counts_match = cross.get("counts") == fixed_cross.get("counts")
    for name, ok in (
        ("row0 choices", row0_choices_match),
        ("main full assignments", main_full_match),
        ("cross-check full assignments", cross_full_match),
        ("cross-check status counts", cross_counts_match),
    ):
        if not ok:
            errors.append(f"{name} mismatch between dynamic MRO and fixed-order replay")

    return {
        "row0_choices_match": row0_choices_match,
        "main_full_assignments_match": main_full_match,
        "cross_check_full_assignments_match": cross_full_match,
        "cross_check_status_counts_match": cross_counts_match,
        "dynamic_mro_main_nodes": int(main.get("nodes_visited", -1)),
        "fixed_order_main_nodes": int(fixed_main.get("nodes_visited", -1)),
        "dynamic_mro_cross_check_nodes": int(cross.get("nodes_visited", -1)),
        "fixed_order_cross_check_nodes": int(fixed_cross.get("nodes_visited", -1)),
    }


def _mapping_field(
    artifact: Mapping[str, Any],
    key: str,
    errors: list[str],
) -> Mapping[str, Any]:
    value = artifact.get(key)
    if not isinstance(value, Mapping):
        errors.append(f"{key} must be an object")
        return {}
    return value


def _check_equal(errors: list[str], name: str, actual: Any, expected: Any) -> bool:
    if actual != expected:
        errors.append(f"{name} mismatch: {actual!r} != {expected!r}")
        return False
    return True


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    comparison = payload["comparison_summary"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"row0 choices match: {comparison['row0_choices_match']}",
        f"main full assignments match: {comparison['main_full_assignments_match']}",
        f"cross-check full assignments match: {comparison['cross_check_full_assignments_match']}",
        f"cross-check status counts match: {comparison['cross_check_status_counts_match']}",
    ]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--check", action="store_true", help="validate the replay")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="emit JSON payload")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact_path = _resolve(args.artifact)
    try:
        artifact = load_artifact(artifact_path)
        if not isinstance(artifact, Mapping):
            raise TypeError("n=9 vertex-circle artifact top level must be an object")
        payload = mro_branching_replay_payload(artifact, artifact_path=artifact_path)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        payload = {
            "schema": SCHEMA,
            "status": STATUS,
            "trust": TRUST,
            "claim_scope": CLAIM_SCOPE,
            "validation_status": "failed",
            "validation_errors": [str(exc)],
            "provenance": dict(PROVENANCE),
        }

    if args.assert_expected:
        assert_expected_mro_branching_replay(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 vertex-circle MRO branching replay")
        for line in summary_lines(payload):
            print(line)
        print("OK: n=9 MRO branching replay checks passed")
    else:
        print("FAILED: n=9 MRO branching replay", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
