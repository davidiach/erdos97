"""Deletion-profile crosswalk for the large fragile-cycle halo covers.

The fixed 23=27 core has four retained critical T4 rows.  This module
exhausts its four- and five-halo covers and asks which retained T4 coverage
graphs already contain an exclusive mutual pair.  Such a pair gives an exact
full-rich-class dichotomy: an additional T4 row must reuse an endpoint, or
the minimal two-deletion profile lemma forces a T5/T44 certifier.

This is a bounded crosswalk conditional on the fixed retained rows.  It does
not force the core, an added row, a richer profile, a full selected extension,
or a Euclidean realization.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import combinations, combinations_with_replacement
import json
from typing import Any, Mapping, Sequence

from erdos97.fragile_cycle_halo_lift_frontier import (
    CORE_ORDER,
    FRAGILE_CENTERS,
    PAIR_CAP,
    REQUIRED_WITNESSES,
    _pair,
    _selected_pair_ok,
    cyclic_order_for_gaps,
)
from erdos97.fragile_cycle_halo_slot_budget import (
    EXPECTED_CENSUS as SLOT_BUDGET_EXPECTED_CENSUS,
    _coverage_multisets,
    _spare_kind,
)
from erdos97.fragile_hypergraph import essential_row_matching


SCHEMA = "erdos97.fragile_cycle_halo_deletion_crosswalk.v1"
STATUS = "EXACT_BOUNDED_HALO_DELETION_CROSSWALK"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact retained-T4 coverage-graph and minimal two-deletion-profile "
    "crosswalk for every four- and five-halo essential cover of the fixed "
    "23=27 core. A retained-exclusive mutual pair forces the conditional "
    "alternative of an added T4 endpoint-reuse row or a T5/T44 deletion "
    "certifier. Pair-free covers show that retained T4 coverage alone does "
    "not force either alternative. This does not force the core, upgrade all "
    "retained-private halos, close full selected extensions, prove Euclidean "
    "realizability, n=11, n=12, the general problem, or a counterexample."
)
CONCLUSION = (
    "The deletion-profile route detects 144000 of 529200 four-halo covers "
    "and 166320 of 512820 five-halo covers through exactly one retained-"
    "exclusive mutual pair. Only pairs 1-3, 1-6, and 3-6 occur. The remaining "
    "385200 and 346500 pair-free covers are exact negative controls for any "
    "claim that singleton/two-deletion T4 coverage alone upgrades retained-"
    "private halos. Further progress must force an endpoint-reuse T4 row, a "
    "richer T5/T44 profile, or genuinely metric geometry in that residue."
)
PROVENANCE = {
    "generator": "scripts/check_fragile_cycle_halo_deletion_crosswalk.py",
    "command": (
        "python scripts/check_fragile_cycle_halo_deletion_crosswalk.py "
        "--write --assert-expected --summary-json"
    ),
}

EXPECTED_CROSSWALK: dict[int, dict[str, Any]] = {
    4: {
        "placement_count": 210,
        "essential_cover_count": 529_200,
        "pair_free_cover_count": 385_200,
        "exclusive_trigger_cover_count": 144_000,
        "exclusive_pair_count_histogram": {"0": 385_200, "1": 144_000},
        "exclusive_pair_identity_histogram": {
            "1-3": 41_760,
            "1-6": 52_920,
            "3-6": 49_320,
        },
        "private_spare_trigger_records": [
            {
                "exclusive_trigger": False,
                "retained_private_halo_count": 3,
                "spare_kind": "duplicated_halo",
                "cover_count": 163_440,
            },
            {
                "exclusive_trigger": True,
                "retained_private_halo_count": 3,
                "spare_kind": "duplicated_halo",
                "cover_count": 75_960,
            },
            {
                "exclusive_trigger": False,
                "retained_private_halo_count": 4,
                "spare_kind": "duplicated_missing_core",
                "cover_count": 107_100,
            },
            {
                "exclusive_trigger": True,
                "retained_private_halo_count": 4,
                "spare_kind": "duplicated_missing_core",
                "cover_count": 10_080,
            },
            {
                "exclusive_trigger": False,
                "retained_private_halo_count": 4,
                "spare_kind": "required_anchor_reuse",
                "cover_count": 114_660,
            },
            {
                "exclusive_trigger": True,
                "retained_private_halo_count": 4,
                "spare_kind": "required_anchor_reuse",
                "cover_count": 57_960,
            },
        ],
        "placement_trace_sha256": (
            "ce5e62165d13a1de2ebbd093604bfc4cf29068825096aeaa5ed489f335091332"
        ),
    },
    5: {
        "placement_count": 462,
        "essential_cover_count": 512_820,
        "pair_free_cover_count": 346_500,
        "exclusive_trigger_cover_count": 166_320,
        "exclusive_pair_count_histogram": {"0": 346_500, "1": 166_320},
        "exclusive_pair_identity_histogram": {
            "1-3": 55_440,
            "1-6": 55_440,
            "3-6": 55_440,
        },
        "private_spare_trigger_records": [
            {
                "exclusive_trigger": False,
                "retained_private_halo_count": 5,
                "spare_kind": "none",
                "cover_count": 346_500,
            },
            {
                "exclusive_trigger": True,
                "retained_private_halo_count": 5,
                "spare_kind": "none",
                "cover_count": 166_320,
            },
        ],
        "placement_trace_sha256": (
            "04793a25fd4896bf2eab14029fc04383aa77a473f753c4d0c4057dc3c4edadb7"
        ),
    },
}

Rows = dict[int, tuple[int, ...]]
Pair = tuple[int, int]


def retained_gamma(
    rows: Mapping[int, Sequence[int]], labels: Sequence[int]
) -> dict[int, frozenset[int]]:
    """Return retained T4 covering centers for every supplied label."""

    return {
        int(label): frozenset(
            int(center) for center, row in rows.items() if label in row
        )
        for label in labels
    }


def retained_exclusive_pairs(
    rows: Mapping[int, Sequence[int]], labels: Sequence[int]
) -> tuple[Pair, ...]:
    """Return exclusive mutual pairs in the retained T4 coverage graph."""

    gamma = retained_gamma(rows, labels)
    return tuple(
        (left, right)
        for left, right in combinations(sorted(rows), 2)
        if gamma[left] == {right} and gamma[right] == {left}
    )


def retained_t4_certifiers(
    rows: Mapping[int, Sequence[int]], deletion_pair: Sequence[int]
) -> tuple[int, ...]:
    """Return retained T4 centers certifying one two-vertex deletion."""

    pair = frozenset(int(value) for value in deletion_pair)
    if len(pair) != 2:
        raise ValueError("deletion_pair must contain two distinct labels")
    return tuple(
        sorted(
            center
            for center, row in rows.items()
            if center not in pair and not pair.isdisjoint(row)
        )
    )


def retained_uncertified_pairs(
    rows: Mapping[int, Sequence[int]], labels: Sequence[int]
) -> tuple[Pair, ...]:
    """Return deletion pairs having no retained T4 certifier."""

    return tuple(
        pair
        for pair in combinations(sorted(int(value) for value in labels), 2)
        if not retained_t4_certifiers(rows, pair)
    )


def _rows_json(rows: Mapping[int, Sequence[int]]) -> list[list[int]]:
    return [
        [center, *sorted(int(value) for value in rows[center])]
        for center in sorted(rows)
    ]


def _stratum_records(counter: Counter[tuple[int, str, bool]]) -> list[dict[str, Any]]:
    return [
        {
            "exclusive_trigger": exclusive,
            "retained_private_halo_count": private_count,
            "spare_kind": spare_kind,
            "cover_count": cover_count,
        }
        for (private_count, spare_kind, exclusive), cover_count in sorted(
            counter.items()
        )
    ]


def _representative(
    gaps: tuple[int, ...],
    order: tuple[int, ...],
    rows: Mapping[int, Sequence[int]],
) -> dict[str, Any]:
    gamma = retained_gamma(rows, order)
    exclusive = retained_exclusive_pairs(rows, order)
    uncertified = retained_uncertified_pairs(rows, order)
    if uncertified != exclusive:
        raise AssertionError("T4 certifier/exclusive-pair identity failed")
    total_pairs = len(order) * (len(order) - 1) // 2
    return {
        "halo_gaps": list(gaps),
        "cyclic_order": list(order),
        "retained_rows": _rows_json(rows),
        "retained_gamma": {
            str(label): sorted(gamma[label]) for label in sorted(gamma)
        },
        "retained_exclusive_pairs": [list(pair) for pair in exclusive],
        "retained_uncertified_deletion_pairs": [
            list(pair) for pair in uncertified
        ],
        "retained_t4_certified_deletion_pair_count": total_pairs - len(uncertified),
        "total_deletion_pair_count": total_pairs,
    }


def _placement_scan(gaps: tuple[int, ...]) -> dict[str, Any]:
    """Exhaust one canonical large-halo placement."""

    order = cyclic_order_for_gaps(gaps)
    labels = frozenset(order)
    halo_labels = labels - set(CORE_ORDER)
    assigned: Rows = {}
    pair_counts: Counter[Pair] = Counter()
    counts: Counter[str] = Counter()
    exclusive_pair_histogram: Counter[str] = Counter()
    strata: Counter[tuple[int, str, bool]] = Counter()
    representatives: dict[str, dict[str, Any]] = {}

    def record(spare: int | None) -> None:
        _, unmatched = essential_row_matching(len(order), assigned)
        if unmatched:
            counts["matching_reject_count"] += 1
            return
        exclusive = retained_exclusive_pairs(assigned, order)
        if len(exclusive) > 1:
            raise AssertionError("fixed core unexpectedly has two exclusive pairs")
        if any(4 in pair for pair in exclusive):
            raise AssertionError("center 4 cannot be retained-exclusive")
        halo_indegrees = Counter(
            witness
            for row in assigned.values()
            for witness in row
            if witness in halo_labels
        )
        private_count = sum(
            halo_indegrees[label] == 1 for label in halo_labels
        )
        trigger = bool(exclusive)
        counts["essential_cover_count"] += 1
        counts[
            "exclusive_trigger_cover_count" if trigger else "pair_free_cover_count"
        ] += 1
        counts[f"exclusive_pair_count_{len(exclusive)}"] += 1
        for left, right in exclusive:
            exclusive_pair_histogram[f"{left}-{right}"] += 1
        strata[(private_count, _spare_kind(spare), trigger)] += 1
        key = (
            f"pair_{exclusive[0][0]}_{exclusive[0][1]}"
            if exclusive
            else "pair_free"
        )
        if key not in representatives:
            representatives[key] = _representative(gaps, order, assigned)

    def search(index: int, remaining: Counter[int], spare: int | None) -> None:
        if index == len(FRAGILE_CENTERS):
            record(spare)
            return
        center = FRAGILE_CENTERS[index]
        available = sorted(
            label
            for label, multiplicity in remaining.items()
            if multiplicity
            and label != center
            and label not in REQUIRED_WITNESSES[center]
        )
        for left, right in combinations(available, 2):
            row = tuple(sorted((*REQUIRED_WITNESSES[center], left, right)))
            if not all(
                _selected_pair_ok(center, row, other, other_row, order)
                for other, other_row in assigned.items()
            ):
                continue
            row_pairs = [_pair(a, b) for a, b in combinations(row, 2)]
            if any(pair_counts[pair] >= PAIR_CAP for pair in row_pairs):
                continue
            remaining[left] -= 1
            remaining[right] -= 1
            assigned[center] = row
            for pair in row_pairs:
                pair_counts[pair] += 1
            search(index + 1, remaining, spare)
            for pair in row_pairs:
                pair_counts[pair] -= 1
            del assigned[center]
            remaining[left] += 1
            remaining[right] += 1

    for spare, multiset in _coverage_multisets(labels, len(gaps)):
        search(0, multiset, spare)

    return {
        "halo_gaps": list(gaps),
        "counts": dict(sorted(counts.items())),
        "exclusive_pair_identity_histogram": dict(
            sorted(exclusive_pair_histogram.items())
        ),
        "private_spare_trigger_records": _stratum_records(strata),
        "representatives": representatives,
    }


def _aggregate_halo_count(halo_count: int) -> dict[str, Any]:
    aggregate_counts: Counter[str] = Counter()
    pair_histogram: Counter[str] = Counter()
    strata: Counter[tuple[int, str, bool]] = Counter()
    representatives: dict[str, dict[str, Any]] = {}
    trace = sha256()
    placement_count = 0
    for gaps in combinations_with_replacement(CORE_ORDER, halo_count):
        placement = _placement_scan(gaps)
        placement_count += 1
        aggregate_counts.update(placement["counts"])
        pair_histogram.update(placement["exclusive_pair_identity_histogram"])
        for record in placement["private_spare_trigger_records"]:
            strata[
                (
                    int(record["retained_private_halo_count"]),
                    str(record["spare_kind"]),
                    bool(record["exclusive_trigger"]),
                )
            ] += int(record["cover_count"])
        for key, representative in placement["representatives"].items():
            representatives.setdefault(key, representative)
        trace.update(
            json.dumps(
                {
                    "gaps": placement["halo_gaps"],
                    "counts": placement["counts"],
                    "pairs": placement["exclusive_pair_identity_histogram"],
                    "strata": placement["private_spare_trigger_records"],
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        )
    result = {
        "halo_count": halo_count,
        "placement_count": placement_count,
        "essential_cover_count": aggregate_counts["essential_cover_count"],
        "pair_free_cover_count": aggregate_counts["pair_free_cover_count"],
        "exclusive_trigger_cover_count": aggregate_counts[
            "exclusive_trigger_cover_count"
        ],
        "exclusive_pair_count_histogram": {
            str(count): aggregate_counts[f"exclusive_pair_count_{count}"]
            for count in (0, 1)
        },
        "exclusive_pair_identity_histogram": dict(sorted(pair_histogram.items())),
        "private_spare_trigger_records": _stratum_records(strata),
        "placement_trace_sha256": trace.hexdigest(),
        "representatives": representatives,
    }
    expected_source = SLOT_BUDGET_EXPECTED_CENSUS[halo_count]
    if result["placement_count"] != expected_source["placement_count"]:
        raise AssertionError("slot-budget placement count changed")
    if result["essential_cover_count"] != expected_source["aggregate_counts"][
        "essential_covers"
    ]:
        raise AssertionError("slot-budget essential-cover count changed")
    return result


def halo_deletion_crosswalk_payload() -> dict[str, Any]:
    """Build the complete deterministic deletion-profile crosswalk."""

    four = _aggregate_halo_count(4)
    five = _aggregate_halo_count(5)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_contract": {
            "quotient_identification": "23=27",
            "retained_centers": list(FRAGILE_CENTERS),
            "halo_counts": [4, 5],
            "retained_rows_are_T4_profiles": True,
            "source_slot_budget_schema": (
                "erdos97.fragile_cycle_halo_slot_budget.v1"
            ),
        },
        "deletion_profile_lemma": {
            "gamma_definition": (
                "Gamma_R(x) is the set of retained T4 centers whose row "
                "contains x"
            ),
            "exclusive_definition": (
                "Gamma_R(x)={z} and Gamma_R(z)={x}"
            ),
            "retained_identity": (
                "a deletion pair has no retained T4 certifier exactly when "
                "it is retained-exclusive mutual"
            ),
            "full_rich_class_dichotomy": (
                "each retained-exclusive pair is either broken by an added "
                "T4 row centered outside the retained family and containing "
                "an endpoint, or remains globally exclusive and therefore "
                "forces a T5/T44 certifier by the minimal two-deletion lemma"
            ),
            "pair_free_negative_control": (
                "if no retained-exclusive pair occurs, the retained T4 rows "
                "already certify every two-vertex deletion; singleton and "
                "two-deletion T4 coverage alone therefore force neither an "
                "added row nor a richer certifier"
            ),
            "candidate_exclusive_pairs": [[1, 3], [1, 6], [3, 6]],
            "maximum_retained_exclusive_pair_count": 1,
            "center_4_exclusion": (
                "required rows 1 and 3 both contain center 4, so Gamma_R(4) "
                "has size at least two"
            ),
        },
        "four_halos": four,
        "five_halos": five,
        "summary": {
            "essential_cover_count": (
                four["essential_cover_count"] + five["essential_cover_count"]
            ),
            "exclusive_trigger_cover_count": (
                four["exclusive_trigger_cover_count"]
                + five["exclusive_trigger_cover_count"]
            ),
            "pair_free_negative_control_count": (
                four["pair_free_cover_count"] + five["pair_free_cover_count"]
            ),
            "deletion_profile_trigger_is_universal": False,
        },
        "limitations": [
            "The fixed 23=27 quotient core and four retained T4 rows are assumed.",
            "The census classifies retained T4 coverage, not every rich class.",
            "The dichotomy does not choose between added T4 reuse and T5/T44.",
            "Pair-free is a coverage-level negative control, not an abstract or Euclidean counterexample.",
            "No full-extension, Euclidean, n=11, n=12, general, or counterexample claim is made.",
        ],
        "conclusion": CONCLUSION,
        "provenance": PROVENANCE,
    }


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert the stable crosswalk totals and claim boundary."""

    for key, expected in (
        ("schema", SCHEMA),
        ("status", STATUS),
        ("trust", TRUST),
        ("claim_scope", CLAIM_SCOPE),
        ("conclusion", CONCLUSION),
        ("provenance", PROVENANCE),
    ):
        if payload.get(key) != expected:
            raise AssertionError(f"{key} changed")
    for halo_count, expected in EXPECTED_CROSSWALK.items():
        section = payload.get("four_halos" if halo_count == 4 else "five_halos")
        if not isinstance(section, Mapping):
            raise AssertionError(f"missing {halo_count}-halo section")
        for key, value in expected.items():
            if section.get(key) != value:
                raise AssertionError(f"{halo_count}-halo {key} changed")
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("missing summary")
    if summary.get("essential_cover_count") != 1_042_020:
        raise AssertionError("combined cover count changed")
    if summary.get("exclusive_trigger_cover_count") != 310_320:
        raise AssertionError("combined trigger count changed")
    if summary.get("pair_free_negative_control_count") != 731_700:
        raise AssertionError("combined pair-free count changed")
    if summary.get("deletion_profile_trigger_is_universal") is not False:
        raise AssertionError("deletion trigger boundary changed")


__all__ = [
    "CLAIM_SCOPE",
    "CONCLUSION",
    "PROVENANCE",
    "SCHEMA",
    "STATUS",
    "TRUST",
    "assert_expected_payload",
    "halo_deletion_crosswalk_payload",
    "retained_exclusive_pairs",
    "retained_gamma",
    "retained_t4_certifiers",
    "retained_uncertified_pairs",
]
