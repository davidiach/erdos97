# n=9 Base-Apex Low-Excess Prompt Loop

Status: bounded research-loop note only. This is not a proof of `n=9`, not a
counterexample, not a geometric realizability test, and not a global status
update. Trust label: `FINITE_BOOKKEEPING_NOT_A_PROOF`.

## Object Studied

The object is the strict-threshold low-excess part of the `n=9` base-apex
ledger. Write `E` for total profile excess and `D` for unused base-apex
capacity. The bookkeeping identity is

```text
E + D = 9.
```

The current turn-cover diagnostic closes only ledgers with `D < 3`. The
unresolved strict-threshold ledgers are therefore exactly the low-excess band

```text
E <= 6, equivalently D >= 3.
```

## Diagnostics Replayed

All commands below completed successfully in this working tree.

```bash
python scripts/explore_n9_base_apex.py --summary
python scripts/explore_n9_base_apex.py --turn-cover
python scripts/explore_n9_base_apex.py --motifs
python scripts/check_n9_base_apex_low_excess_ledgers.py --check --json
python scripts/check_n9_base_apex_escape_budget.py --check --json
python scripts/check_n9_base_apex_low_excess_escape_ladder.py --check --json
python scripts/check_n9_base_apex_low_excess_escape_crosswalk.py --check --json
python scripts/check_n9_d3_escape_slice.py --check --json
python scripts/check_n9_base_apex_d3_escape_frontier_packet.py --check --json
python scripts/check_n9_base_apex_d3_p19_incidence_capacity_pilot.py --check --json
python scripts/check_n9_base_apex_d3_incidence_capacity_packet.py --check --json
python scripts/check_n9_base_apex_d3_artifact_join.py --check --json
python scripts/check_n9_selected_baseline_d3_escape_class_crosswalk.py --check --json
python scripts/check_n9_selected_baseline_escape_budget_overlay.py --check --json
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
```

Key checked numbers:

- `95` unlabeled profile-excess ledgers with `E <= 9`.
- strict threshold: `65` ledgers forced by turn-cover, `30` unresolved.
- strict minimum relevant escape: `3` length-2/length-3 deficit units,
  `108` labelled placements, `8` dihedral escape classes.
- low-excess ladder: `30` ledgers, `108` escape placements,
  `30,184` common-dihedral profile/escape pair classes.
- sharp `D=3` slice: `3,003` labelled profile sequences, `108` escape
  placements, `18,088` common-dihedral pair classes.
- `D=3` representative packet: `11` profile multisets by `8` escape classes,
  hence `88` representative rows; realizability and incidence states are
  still `UNKNOWN`.
- selected-baseline overlay: strict selected-baseline deficits force `44` of
  `184` pre-vertex-circle assignments; the `D=3` selected-baseline crosswalk
  has `13,710` forced and `1,746` escaping assignment/slot choices. These are
  selected-baseline bookkeeping counts, not profile-capacity realizability
  counts.
- review-pending vertex-circle checker: `184` pre-vertex-circle assignments
  are killed by exact self-edge or strict-cycle obstructions. This remains a
  separate review-pending selected-witness finite-case artifact.

## Cycle 1: Try `E >= 7`

Propose: target a geometric anti-concentration lemma proving every bad
strictly convex nonagon has total profile excess `E >= 7`. This would make
`D <= 2`, so the existing strict turn-cover diagnostic would close the ledger.

Audit: the diagnostics do not expose a local reason for such a strong lower
bound. Even under the restrictive assumption that only excesses `0` and `1`
occur, there are `10` profile ledgers and `7` remain unresolved by turn-cover.
The target would need a new geometric lemma that rules out low-excess profile
distributions directly, not just a refinement of the current bookkeeping.

Refine: keep `E >= 7` as a possible future bridge, but do not make it the next
exact target. It is too global for the artifacts currently in hand.

## Cycle 2: Block `D >= 3` Escape Placements

Propose: prove that the `D >= 3` capacity deficit cannot be placed so as to
spoil the length-2/length-3 turn-cover clauses.

Audit: the statement is correct in spirit but too wide as an immediate finite
target. The strict-threshold escape mechanism needs only `r=3` relevant
deficits, while ledgers with `D > 3` have spare budget `D - r`. Existing
artifacts intentionally do not place this spare budget on sides, length-4
diagonals, or redundant length-2/length-3 failures. A direct all-`D >= 3`
statement would therefore mix the sharp escape obstruction with extra
unassigned-capacity choices.

Refine: isolate the boundary case `D=3`. There, the three relevant deficits
consume the entire capacity deficit budget, so every displayed escape row has
exact per-base saturation targets: the three displayed length-2/length-3 bases
are each down by one unit, and every other cyclic base is saturated.

## Cycle 3: Separate Low-Excess Obstruction

Propose: build a separate exact obstruction for the sharp `E=6, D=3, r=3`
slice using the existing incidence-capacity packet.

Audit: this is the cleanest next target. The checked packet already exposes
all `88` representative rows, but leaves both states as `UNKNOWN`. It records
the profile multisets, escape classes, deficient base chords, and target
capacity totals. The `D=3` artifact join confirms consistency across the slice,
packet, low-excess crosswalk, P19 pilot, and all-row packet.

Refined next target:

```text
For each row of
data/certificates/n9_base_apex_d3_incidence_capacity_packet.json,
decide finite profile-capacity feasibility.

Input row data:
- one total-excess-6 profile multiset on the nine centers;
- one strict r=3 escape class X00..X07;
- the three displayed deficient length-2/length-3 base chords;
- exact target base-apex capacities, with total capacity 60.

Required finite assignment:
- assign each center a full distance-class partition of the other eight
  labels matching its profile excess;
- count every unordered base pair whenever its endpoints lie in the same
  class at an apex;
- meet the row's exact per-base target: displayed deficient length-2/3 bases
  are one below full capacity, all other bases are saturated;
- satisfy the existing pair/crossing/cap necessary filters when a selected
  4-witness row is extracted from each center.

Desired outcome:
- either reject all 88 rows by exact finite bookkeeping, closing the sharp
  D=3 minimal-escape slice only;
- or emit a compact survivor packet whose rows can be attacked by exact
  vertex-circle template checks or a geometric capacity lemma.
```

This target is a separate obstruction for low-excess ledgers, with the first
deliverable scoped to the sharp `D=3` slice. It does not claim that ledgers
with `D > 3` are closed. If the `D=3` slice is obstructed, the next ladder step
should add the spare-capacity placement data for `D=4`, then repeat the same
profile-capacity feasibility audit.

## What This Would Rule Out

If completed, this target would rule out only the strict-threshold
`E=6, D=3, r=3` profile/escape bookkeeping slice under the stated finite
profile-capacity hypotheses. It would not prove the full `n=9` case, would not
settle `D > 3`, and would not update the official/global Erdos #97 status.

## Suggested Verification Shape

The checker should treat existing JSON artifacts as inputs rather than as
generated truth, mirroring the style of the current `check_n9_base_apex_*`
scripts. A successful first checker should be runnable as something like:

```bash
python scripts/check_n9_base_apex_d3_profile_capacity_feasibility.py --check --json
```

The report artifact, if any, should keep rows with status `UNKNOWN` explicit
instead of silently accepting unsupported feasibility.
