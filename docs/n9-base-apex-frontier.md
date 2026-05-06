# n=9 base-apex frontier

Status: exploratory research lead only. This note is not a proof, not a
counterexample, and not a source for changing the repository's official/global
status. The case `n >= 9` remains open.

This note records the corrected bookkeeping target for extending the
base-apex argument in `docs/n8-geometric-proof.md` from `n = 8` to `n = 9`.
It supersedes an earlier informal slack recommendation from private archived
exploration notes, but only as planning guidance.

## Correct slack ledger

Let `A` be a bad strictly convex `n`-gon and let `T(A)` be the number of
isosceles triples `(p,{a,b})`, where `p` is the apex and `{a,b}` is the base.
The base-apex count gives

```text
T(A) >= 6n
T(A) <= n(n-2).
```

For `n = 9`, the upper-minus-baseline slack is

```text
n(n-2) - 6n = 9.
```

At a vertex, write the distance-class profile among the other eight vertices
as a partition `(m_1,...,m_r)` with `sum m_i = 8` and `max m_i >= 4`. Its
profile excess is

```text
s = sum_i binom(m_i,2) - 6.
```

The important correction is that the profile excesses do not have to sum to
`9`. If `E` is the sum of profile excesses and `D` is the unused base-apex
capacity, then the exact ledger is

```text
E + D = 9, with E >= 0 and D >= 0.
```

So `sum s_i <= 9`; equality is only the special case where every side and
diagonal capacity is saturated.

## n=9 profile table

The possible vertex profiles and excesses are:

```text
s=0   (4,1,1,1,1)
s=1   (4,2,1,1)
s=2   (4,2,2)
s=3   (4,3,1)
s=4   (5,1,1,1)
s=5   (5,2,1)
s=6   (4,4)
s=7   (5,3)
s=9   (6,1,1)
s=10  (6,2)
s=15  (7,1)
s=22  (8)
```

Only profiles with `s <= 9` can appear in an `n = 9` bad polygon, and even
then only in combinations whose total profile excess is at most `9`.

## Practical next target

The first useful artifact is a finite ledger, not a theorem. It should:

- enumerate all `n = 9` distance-class profiles and their excesses;
- enumerate profile-excess distributions with total `E <= 9`;
- carry the remaining slack as a separate capacity deficit `D = 9 - E`;
- report conservative saturation guarantees for cyclic base families.

This does not close `n = 9`. It identifies the exact places where a geometric
anti-concentration lemma or a stronger turn-cover argument would need to enter.

The first executable diagnostic is `scripts/explore_n9_base_apex.py`. It keeps
the ledger separate from the turn-cover closure:

```bash
python scripts/explore_n9_base_apex.py --summary
python scripts/explore_n9_base_apex.py --turn-cover
python scripts/explore_n9_base_apex.py --motifs
python scripts/explore_n9_base_apex.py --low-excess-report --out data/certificates/n9_base_apex_low_excess_ledgers.json
python scripts/check_n9_base_apex_low_excess_ledgers.py --check --json
python scripts/explore_n9_base_apex.py --escape-budget-report --out data/certificates/n9_base_apex_escape_budget_report.json
python scripts/check_n9_base_apex_escape_budget.py --check --json
```

The focused generated report
`data/certificates/n9_base_apex_low_excess_ledgers.json` records the
strict-threshold unresolved low-excess ledgers, the counts by `E` and `D`, and
the minimum relevant length-2/length-3 deficit motif classes. It is
`FINITE_BOOKKEEPING_NOT_A_PROOF`, not a claim that `n=9` is closed. The
checker command independently replays the partition table, ledger arithmetic,
turn-cover summaries, and minimum escape motif classes from the stored JSON.

The companion generated report
`data/certificates/n9_base_apex_escape_budget_report.json` records a coarser
budget map for the same diagnostic. For each capacity-deficit budget `D`, it
counts how many labelled and dihedral placements of `r <= D` relevant deficits
on length-2 and length-3 bases can escape the current turn-cover closure. It
also records the total number `binom(18,r)` of such relevant placements, so the
escaping counts are visibly scoped to the two cyclic base families used by this
turn-cover mechanism.

This is still only bookkeeping. The report does not place any remaining budget
on sides or length-4 diagonals, does not test geometric realizability of the
escape placements, and does not close `n = 9`.

A later selected-baseline overlay
`data/certificates/n9_selected_baseline_escape_budget_overlay.json` compares
the same turn-cover budget against the 184 complete selected-witness
assignments that survive the pair/crossing/count filters before vertex-circle
pruning. In those row systems, the selected 4-witness rows use 54 base-apex
incidences against total cyclic capacity 63, leaving 9 selected-baseline empty
capacity units in every case. Under the strict threshold, the selected-baseline
deficits still force the current turn-cover contradiction in 44 of the 184
assignments; under the conservative threshold, they force it in 2. The one
formerly recorded `accepted_frontier` row system from
`data/certificates/n9_incidence_frontier_bounded.json` is now classified by
the row-Ptolemy product-cancellation filter in that bounded natural-order
slice. The selected-baseline overlay schema `v2` therefore records
`accepted_frontier_count = 0` and has no surviving frontier escape example to
analyze.

This overlay is not a geometric realizability test. Actual unselected
equal-distance triples or profile excess could fill selected-baseline empty
capacity slots, so the artifact is only a finite bookkeeping map for where the
current turn-cover method does and does not bite.

The sharp strict-threshold slice is recorded separately at
`data/certificates/n9_base_apex_d3_escape_slice.json`. This is the case
`E=6`, `D=3`, `r=3`, where all three capacity-deficit units are relevant
length-2/length-3 deficits and there is no leftover budget to park on sides or
length-4 diagonals. The diagnostic finds 3,003 labelled profile-excess
sequences, 108 labelled strict escape placements, and 18,088 common-dihedral
coupled profile/escape classes. These are proof-search fingerprints only: the
artifact does not say that any coupled class is realizable, nor that the
`D=3` slice is impossible.

## Turn-cover diagnostic

Index the length-2 diagonal `{v_i,v_{i+2}}` by `i`. If it is fully saturated,
then the short-side apex `v_{i+1}` is present, so

```text
|v_i v_{i+1}| = |v_{i+1} v_{i+2}|.
```

Index the length-3 diagonal `{v_i,v_{i+3}}` by `i`. If it is fully saturated,
then its short-side apex is either `v_{i+1}` or `v_{i+2}`. When the neighboring
length-2 diagonals `i` and `i+1` are also saturated, this gives the clause

```text
tau_{i+1} = 2*pi/3  or  tau_{i+2} = 2*pi/3.
```

With every length-2 and length-3 diagonal saturated, these clauses form the
edge set of a 9-cycle, so the minimum turn cover has size `5`. That would
contradict the total exterior-turn sum.

The executable diagnostic finds that, using the strict-positivity threshold
where three forced `2*pi/3` turns already exhaust the `2*pi` budget, at least
three length-2/length-3 capacity deficits are needed to escape this particular
closure. Using the more conservative "forced turns alone exceed `2*pi`"
threshold, two such deficits suffice to escape.

Among the 95 unlabeled profile-excess distributions with `E <= 9`, this
conditional mechanism closes 65 distributions under the strict-positivity
threshold and 50 under the conservative threshold. The remaining distributions
need either stronger saturation information, an anti-concentration lemma, or a
different geometric obstruction.

The unresolved strict-threshold ledgers are exactly the low-profile-excess
ones:

```text
E <= 6, equivalently D >= 3.
```

This reverses the original intuition in an important way. A pure
anti-concentration lemma, by itself, does not close `n = 9`: if only the
profiles with excess `0` and `1` are allowed, there are 10 unlabeled excess
distributions and the current turn-cover diagnostic still leaves 7 unresolved.
Those unresolved cases have too much unused base-apex capacity, not too much
profile concentration.

The next mathematical target is therefore sharper:

```text
Either prove E >= 7,
or prove that D >= 3 cannot be placed so as to spoil the length-2/length-3
turn-cover clauses,
or add a separate obstruction for the low-excess ledgers.
```

## Minimum escape motifs

The `--motifs` diagnostic classifies relevant length-2/length-3 saturation
failures up to dihedral symmetry. A "relevant" deficit is one spent on a
length-2 or length-3 diagonal, because only those bases participate in the
turn-cover closure here. Deficits spent on sides or length-4 diagonals do not
help escape this particular diagnostic.

Under the strict-positivity threshold, the minimum relevant deficit count is
`3`. There are `108` labelled escaping placements, falling into `8` dihedral
classes:

```text
length-2 spoiled   length-3 spoiled
----------------   ----------------
{0,2}              {3}
{0,2}              {5}
{0,3}              {1}
{0,4}              {5}
{0,1,3}            {}
{0,1,5}            {}
{0,2,4}            {}
{0,2,5}            {}
```

Under the conservative "forced turns alone exceed `2*pi`" threshold, the
minimum relevant deficit count is `2`. There are `72` labelled escaping
placements, falling into `6` dihedral classes:

```text
length-2 spoiled   length-3 spoiled
----------------   ----------------
{0}                {1}
{0}                {3}
{0,1}              {}
{0,2}              {}
{0,3}              {}
{0,4}              {}
```

These motif lists give the next finite target. To improve the `n = 9`
base-apex route, one needs a geometric reason that the relevant deficits cannot
fall into these motifs, or a separate obstruction that attacks the motifs
directly.

This is still conditional bookkeeping. It does not say that `n = 9` is closed;
it says that profile distributions with very small capacity deficit are the
ones this exact turn-cover mechanism can attack directly.

## Lemma target to refine

The old shorthand "no high concentration" is too weak as stated. For example,
the profile `(4,2,2)` has no class of size at least five and no second class of
size at least three, but it still has profile excess `2`.

A sharper target for the easy regime is:

```text
Only the profiles (4,1,1,1,1) and (4,2,1,1) survive the first geometric filters.
```

Even this does not force full saturation unless all nine vertices have excess
`1`. The remaining capacity deficit still has to be accounted for explicitly.

The research question is therefore:

```text
Can strict convexity force either enough profile excess, enough base saturation,
or enough structured saturation in length-2 and length-3 diagonals to trigger
the exterior-turn contradiction?
```

The current answer is unknown.
