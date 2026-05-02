#!/usr/bin/env python3
"""Explore the corrected n=9 base-apex slack ledger."""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n9_base_apex import (  # noqa: E402
    distance_profiles,
    deficit_placement_classes,
    excess_distributions,
    guaranteed_full_bases,
    ledger_summary,
    minimum_capacity_deficit_to_escape_turn_cover,
    profile_assumption_summaries,
    profile_ledger_cases,
    turn_cover_diagnostic,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the full JSON payload")
    parser.add_argument("--summary", action="store_true", help="print a compact summary")
    parser.add_argument(
        "--distributions",
        action="store_true",
        help="include unlabeled profile-excess distributions",
    )
    parser.add_argument(
        "--turn-cover",
        action="store_true",
        help="include the full-saturation turn-cover diagnostic",
    )
    parser.add_argument(
        "--unresolved",
        action="store_true",
        help="include profile ledgers unresolved by the strict turn-cover diagnostic",
    )
    parser.add_argument(
        "--assumptions",
        action="store_true",
        help="include standard profile-assumption summaries",
    )
    parser.add_argument(
        "--motifs",
        action="store_true",
        help="include minimum deficit-placement motif classes",
    )
    args = parser.parse_args()

    payload = ledger_summary()
    if args.distributions:
        payload["unlabeled_excess_distributions"] = [
            dataclasses.asdict(row) for row in excess_distributions()
        ]
    if args.turn_cover:
        payload["full_saturation_turn_cover"] = dataclasses.asdict(
            turn_cover_diagnostic()
        )
        payload["strict_turn_cover_escape"] = dataclasses.asdict(
            minimum_capacity_deficit_to_escape_turn_cover()
        )
    if args.unresolved:
        payload["strict_unresolved_profile_ledgers"] = [
            dataclasses.asdict(row)
            for row in profile_ledger_cases(forced_by_turn_cover=False)
        ]
    if args.assumptions:
        payload["standard_profile_assumption_summaries"] = [
            dataclasses.asdict(row) for row in profile_assumption_summaries()
        ]
    if args.motifs:
        payload["strict_minimum_escape_motif_classes"] = [
            dataclasses.asdict(row) for row in deficit_placement_classes()
        ]
        payload["conservative_minimum_escape_motif_classes"] = [
            dataclasses.asdict(row)
            for row in deficit_placement_classes(contradiction_threshold=4)
        ]
    if (
        args.json
        or args.distributions
        or args.turn_cover
        or args.unresolved
        or args.assumptions
        or args.motifs
    ):
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    if args.summary:
        assumption_summaries = payload["profile_assumption_summaries"]
        compact = {
            "n": payload["n"],
            "status": payload["status"],
            "base_apex_slack": payload["base_apex_slack"],
            "profile_count": payload["profile_count"],
            "profile_excess_values": payload["profile_excess_values"],
            "unlabeled_excess_distribution_count": payload[
                "unlabeled_excess_distribution_count"
            ],
            "strict_turn_cover_minimum_deficit_to_escape": payload[
                "turn_cover_escape"
            ]["strict_positive_threshold"]["minimum_capacity_deficit_to_escape"],
            "conservative_turn_cover_minimum_deficit_to_escape": payload[
                "turn_cover_escape"
            ]["sum_exceeds_threshold"]["minimum_capacity_deficit_to_escape"],
            "strict_minimum_escape_motif_classes": payload[
                "minimum_escape_motif_summary"
            ]["strict_positive_threshold"]["dihedral_class_count"],
            "conservative_minimum_escape_motif_classes": payload[
                "minimum_escape_motif_summary"
            ]["sum_exceeds_threshold"]["dihedral_class_count"],
            "strict_turn_cover_forced_distribution_count": payload[
                "turn_cover_distribution_summary"
            ]["strict_positive_threshold"]["forced_by_turn_cover_count"],
            "conservative_turn_cover_forced_distribution_count": payload[
                "turn_cover_distribution_summary"
            ]["sum_exceeds_threshold"]["forced_by_turn_cover_count"],
            "anti_concentration_0_1_distribution_count": assumption_summaries[0][
                "distribution_count"
            ],
            "anti_concentration_0_1_unresolved_count": assumption_summaries[0][
                "unresolved_by_turn_cover_count"
            ],
            "guaranteed_full_length2_bases_when_D_is_0": guaranteed_full_bases(
                capacity_deficit=0,
                cyclic_length=2,
            ),
            "guaranteed_full_length2_bases_when_D_is_4": guaranteed_full_bases(
                capacity_deficit=4,
                cyclic_length=2,
            ),
            "guaranteed_full_length2_bases_when_D_is_9": guaranteed_full_bases(
                capacity_deficit=9,
                cyclic_length=2,
            ),
        }
        print(json.dumps(compact, indent=2, sort_keys=True))
        return 0

    print("n=9 base-apex profile ledger")
    print("status: exploratory bookkeeping only")
    print()
    print("excess  profiles")
    print("------  --------")
    for profile in distance_profiles():
        print(f"{profile.excess:>6}  {profile.parts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
