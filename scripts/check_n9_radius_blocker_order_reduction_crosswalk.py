#!/usr/bin/env python3
"""Check the order-reduction scope of the n=9 radius-blocker shape sweep.

This is a finite bridge diagnostic only. It proves no general theorem about
Erdos Problem #97 and supplies no counterexample.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.radius_blocker_packets import (  # noqa: E402
    TRUST,
    canonical_dihedral_subset,
    dihedral_subset_images,
    subset_positions_in_order,
)

SCHEMA = "erdos97.n9_radius_blocker_order_reduction_crosswalk.v1"
STATUS = "N9_RADIUS_BLOCKER_ORDER_REDUCTION_DIAGNOSTIC_ONLY"
DEFAULT_SHAPE_SWEEP = (
    ROOT / "data" / "certificates" / "n9_radius_blocker_shape_sweep.json"
)
DEFAULT_OUT = (
    ROOT
    / "data"
    / "certificates"
    / "n9_radius_blocker_order_reduction_crosswalk.json"
)
N = 9
SAMPLE_ORDER_BLOCKERS = (
    {
        "order": [3, 0, 8, 1, 4, 2, 5, 7, 6],
        "blocker": [0, 2, 6, 8],
        "natural_blocker": [1, 2, 5, 8],
        "canonical_representative": [0, 1, 3, 6],
    },
    {
        "order": [4, 7, 1, 5, 0, 8, 2, 6, 3],
        "blocker": [1, 3, 4, 8],
        "natural_blocker": [0, 2, 5, 8],
        "canonical_representative": [0, 1, 3, 6],
    },
    {
        "order": [8, 6, 4, 2, 0, 7, 5, 3, 1],
        "blocker": [0, 1, 5, 7],
        "natural_blocker": [4, 5, 6, 8],
        "canonical_representative": [0, 1, 2, 4],
    },
)
EXPECTED_SUMMARY = {
    "n": 9,
    "source_shape_count": 10,
    "covered_labelled_blocker_count": 126,
    "all_labelled_four_blockers_covered": True,
    "sample_reduction_count": 3,
    "order_reduction_scope": (
        "Every supplied cyclic order and four-blocker subset relabels to "
        "natural order by sending order[i] to i."
    ),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_shape_sweep(path: Path) -> Mapping[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise AssertionError("shape sweep artifact is not an object")
    return payload


def shape_cases(payload: Mapping[str, object]) -> list[Mapping[str, object]]:
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise AssertionError("shape sweep artifact has no cases list")
    out: list[Mapping[str, object]] = []
    for case in cases:
        if not isinstance(case, Mapping):
            raise AssertionError(f"shape sweep case is not an object: {case!r}")
        out.append(case)
    return out


def compact_case_records(cases: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for case in cases:
        records.append(
            {
                "blocker": list(case["blocker"]),
                "dihedral_orbit_size": int(case["dihedral_orbit_size"]),
                "incidence_survivors": int(case["incidence_survivors"]),
                "vertex_circle_status_counts": dict(
                    case["vertex_circle_status_counts"]
                ),
            }
        )
    return sorted(records, key=lambda record: record["blocker"])


def sample_reductions() -> list[dict[str, object]]:
    samples: list[dict[str, object]] = []
    for sample in SAMPLE_ORDER_BLOCKERS:
        order = sample["order"]
        blocker = sample["blocker"]
        natural_blocker = list(subset_positions_in_order(order, blocker))
        canonical = list(canonical_dihedral_subset(N, natural_blocker))
        samples.append(
            {
                "order": list(order),
                "blocker": list(blocker),
                "natural_blocker": natural_blocker,
                "canonical_representative": canonical,
            }
        )
    return samples


def build_payload(shape_sweep_path: Path = DEFAULT_SHAPE_SWEEP) -> dict[str, object]:
    """Build the deterministic order-reduction crosswalk payload."""

    source = load_shape_sweep(shape_sweep_path)
    cases = shape_cases(source)
    representatives = [tuple(int(label) for label in case["blocker"]) for case in cases]
    covered_labelled_blockers = sorted(
        {
            image
            for representative in representatives
            for image in dihedral_subset_images(N, representative)
        }
    )
    all_labelled_blockers = sorted(combinations(range(N), 4))
    samples = sample_reductions()

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Order-reduction crosswalk for the n=9 exact-four radius-blocker "
            "shape sweep. It records that any supplied cyclic order and "
            "four-blocker subset relabels to the natural-order labelled "
            "four-blocker coverage already stored in the shape sweep. This "
            "does not prove n=9, does not prove the adaptive blocker bridge, "
            "and is not a counterexample."
        ),
        "summary": {
            "n": N,
            "source_shape_count": len(cases),
            "covered_labelled_blocker_count": len(covered_labelled_blockers),
            "all_labelled_four_blockers_covered": (
                covered_labelled_blockers == all_labelled_blockers
            ),
            "sample_reduction_count": len(samples),
            "order_reduction_scope": (
                "Every supplied cyclic order and four-blocker subset relabels "
                "to natural order by sending order[i] to i."
            ),
        },
        "source_shape_sweep": {
            "path": shape_sweep_path.relative_to(ROOT).as_posix(),
            "schema": source.get("schema"),
            "status": source.get("status"),
            "trust": source.get("trust"),
            "sha256": sha256_file(shape_sweep_path),
            "summary": source.get("summary"),
        },
        "shape_representatives": compact_case_records(cases),
        "sample_reductions": samples,
        "reduction_rule": {
            "label_map": "for a cyclic order order, send each label order[i] to i",
            "blocker_image": (
                "the transformed blocker is sorted(label_map[label] for label "
                "in blocker)"
            ),
            "why_this_matches_the_shape_sweep": (
                "The exact-four row-option rule depends only on the center "
                "label and blocker membership. Under this relabelling, row "
                "options, row-pair crossing in the supplied order, witness-pair "
                "caps, indegree caps, and selected-distance vertex-circle "
                "replay are transported to the natural-order packet for the "
                "transformed blocker."
            ),
        },
        "interpretation_warnings": [
            "This is a relabelling crosswalk for exact-four row-option packets only.",
            "It does not add richer-than-four rich-class semantics.",
            "It does not classify arbitrary n=9 rich-class systems.",
            "No general proof and no counterexample are claimed.",
        ],
        "provenance": {
            "generator": "scripts/check_n9_radius_blocker_order_reduction_crosswalk.py",
            "command": (
                "python scripts/check_n9_radius_blocker_order_reduction_crosswalk.py "
                "--write --assert-expected"
            ),
            "sources": [
                "data/certificates/n9_radius_blocker_shape_sweep.json",
                "src/erdos97/radius_blocker_packets.py",
            ],
        },
    }


def assert_expected_payload(payload: Mapping[str, object]) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"unexpected status: {payload.get('status')!r}")
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("summary is missing")
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary[{key!r}] is {summary.get(key)!r}, expected {expected!r}"
            )
    if payload.get("sample_reductions") != list(SAMPLE_ORDER_BLOCKERS):
        raise AssertionError("sample reductions changed")


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    checked = json.loads(path.read_text(encoding="utf-8"))
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_summary(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("n=9 radius-blocker order-reduction crosswalk")
    print(f"claim scope: {payload['claim_scope']}")
    print(f"source shapes: {summary['source_shape_count']}")
    print(f"labelled blockers covered: {summary['covered_labelled_blocker_count']}")
    print(
        "all labelled four-blockers covered: "
        f"{summary['all_labelled_four_blockers_covered']}"
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SHAPE_SWEEP)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--write", action="store_true", help="write the artifact")
    parser.add_argument("--check", action="store_true", help="compare artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="print full JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload(args.source)
    if args.assert_expected:
        assert_expected_payload(payload)
    if args.check:
        compare_artifact(payload, args.out)
    if args.write:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_summary(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
