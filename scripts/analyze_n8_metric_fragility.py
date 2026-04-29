#!/usr/bin/env python3
"""Probe metric fragility uniqueness on the n=8 survivor classes.

This script is deliberately narrow. It checks full selected equal-distance
equations for the 15 n=8 incidence survivors. If those equations are
inconsistent, fragility questions are vacuous for that class. If they are
consistent, it asks whether any selected row is algebraically forced to have an
alternate equal-distance four-subset at the same center, which would rule out
fragility for that row in n=8.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in [SRC, SCRIPTS]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import analyze_n8_exact_survivors as exact  # noqa: E402
from erdos97.fragile_hypergraph import covering_subsets, rows_from_zero_one_matrix  # noqa: E402

EXPECTED_INCONSISTENT_CLASSES = list(range(14))
EXPECTED_CONSISTENT_CLASSES = [14]


def _contains_one(groebner_basis) -> bool:
    return any(poly.as_expr() == 1 for poly in groebner_basis.polys)


def _alternate_foursets(rows: list[list[int]], center: int) -> list[tuple[int, ...]]:
    selected = set(exact.witnesses(rows, center))
    return [
        tuple(candidate)
        for candidate in itertools.combinations([idx for idx in range(exact.N) if idx != center], 4)
        if set(candidate) != selected
    ]


def _equal_distance_equations(center: int, witnesses: tuple[int, ...]) -> list[object]:
    sp, _symbols, coords, _vars = exact.sympy_context()
    pix, piy = coords[center]
    base = witnesses[0]
    pbx, pby = coords[base]
    base_dist = (pix - pbx) ** 2 + (piy - pby) ** 2
    equations = []
    for other in witnesses[1:]:
        pox, poy = coords[other]
        equations.append(
            sp.expand((pix - pox) ** 2 + (piy - poy) ** 2 - base_dist)
        )
    return equations


def _forced_alternate_foursets(rows: list[list[int]], groebner_basis) -> dict[int, list[tuple[int, ...]]]:
    sp, _symbols, _coords, _vars = exact.sympy_context()
    forced: dict[int, list[tuple[int, ...]]] = {}
    for center in range(exact.N):
        center_forced = []
        for candidate in _alternate_foursets(rows, center):
            equations = _equal_distance_equations(center, candidate)
            if all(sp.expand(groebner_basis.reduce(eq)[1]) == 0 for eq in equations):
                center_forced.append(candidate)
        forced[center] = center_forced
    return forced


def _json_forced(forced: dict[int, list[tuple[int, ...]]]) -> dict[str, list[list[int]]]:
    return {
        str(center): [[int(label) for label in candidate] for candidate in candidates]
        for center, candidates in sorted(forced.items())
    }


def analyze_class(record: dict) -> dict[str, object]:
    sp, _symbols, _coords, vars_order = exact.sympy_context()
    class_id = int(record["id"])
    rows = record["rows"]
    equations = exact.ed_equations(rows)
    basis = sp.groebner(equations, *vars_order, order="grevlex", domain=sp.QQ)
    inconsistent = _contains_one(basis)

    payload: dict[str, object] = {
        "class_id": class_id,
        "selected_ed_equation_count": len(equations),
        "selected_ed_ideal_inconsistent": inconsistent,
    }
    if inconsistent:
        payload["metric_fragility_probe"] = "vacuous_inconsistent_selected_ed_ideal"
        return payload

    forced = _forced_alternate_foursets(rows, basis)
    forced_counts = {str(center): len(candidates) for center, candidates in sorted(forced.items())}
    forced_nonfragile_rows = [
        center for center, candidates in sorted(forced.items()) if candidates
    ]
    eligible_rows = {
        center: row
        for center, row in rows_from_zero_one_matrix(rows).items()
        if center not in forced_nonfragile_rows
    }
    cover_stats = covering_subsets(exact.N, eligible_rows)
    payload.update(
        {
            "metric_fragility_probe": "consistent_selected_ed_ideal",
            "forced_alternate_foursets_by_center": _json_forced(forced),
            "forced_alternate_fourset_counts": forced_counts,
            "algebraically_forced_nonfragile_rows": forced_nonfragile_rows,
            "eligible_fragile_rows_not_forced_nonfragile": sorted(eligible_rows),
            "eligible_rows_cover_all_vertices": cover_stats["cover_exists"],
            "eligible_min_cover_size": cover_stats["min_cover_size"],
            "eligible_cover_counts_by_size": cover_stats["cover_counts_by_size"],
            "eligible_example_covers_by_size": cover_stats["example_covers_by_size"],
        }
    )
    return payload


def analyze_survivors(path: Path) -> dict[str, object]:
    survivors = json.loads(path.read_text(encoding="utf-8"))
    classes = [analyze_class(record) for record in survivors]
    inconsistent = [
        int(row["class_id"])
        for row in classes
        if row["selected_ed_ideal_inconsistent"]
    ]
    consistent = [
        int(row["class_id"])
        for row in classes
        if not row["selected_ed_ideal_inconsistent"]
    ]
    consistent_with_cover = [
        int(row["class_id"])
        for row in classes
        if row.get("eligible_rows_cover_all_vertices") is True
    ]
    return {
        "type": "n8_metric_fragility_probe",
        "n": exact.N,
        "source": str(path),
        "survivor_classes": len(survivors),
        "selected_ed_inconsistent_classes": inconsistent,
        "selected_ed_consistent_classes": consistent,
        "consistent_classes_with_eligible_fragile_cover": consistent_with_cover,
        "interpretation": (
            "For inconsistent classes, full selected equal-distance equations "
            "already have no complex solution under the p0=(0,0), p1=(1,0) "
            "normalization. For consistent classes, the probe reports whether "
            "fragility is algebraically forced to fail by alternate rich "
            "four-subsets. It does not certify existence of a strict convex "
            "realization."
        ),
        "classes": classes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--survivors",
        type=Path,
        default=ROOT / "data" / "incidence" / "n8_reconstructed_15_survivors.json",
        help="n=8 reconstructed survivor JSON",
    )
    parser.add_argument("--json", action="store_true", help="print full JSON")
    parser.add_argument("--check", action="store_true", help="assert expected fingerprints")
    parser.add_argument("--write-artifact", type=Path, help="write JSON artifact")
    args = parser.parse_args()

    data = analyze_survivors(args.survivors)

    if args.check:
        assert data["survivor_classes"] == 15
        assert data["selected_ed_inconsistent_classes"] == EXPECTED_INCONSISTENT_CLASSES
        assert data["selected_ed_consistent_classes"] == EXPECTED_CONSISTENT_CLASSES
        assert data["consistent_classes_with_eligible_fragile_cover"] == [14]
        class14 = data["classes"][14]
        assert class14["algebraically_forced_nonfragile_rows"] == []
        assert class14["eligible_rows_cover_all_vertices"] is True
        assert class14["eligible_min_cover_size"] == 3

    if args.write_artifact:
        args.write_artifact.parent.mkdir(parents=True, exist_ok=True)
        args.write_artifact.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print("survivor classes:", data["survivor_classes"])
        print("selected ED inconsistent classes:", data["selected_ed_inconsistent_classes"])
        print("selected ED consistent classes:", data["selected_ed_consistent_classes"])
        print(
            "consistent classes with eligible fragile cover:",
            data["consistent_classes_with_eligible_fragile_cover"],
        )
        if args.check:
            print("OK: n=8 metric-fragility fingerprints verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
