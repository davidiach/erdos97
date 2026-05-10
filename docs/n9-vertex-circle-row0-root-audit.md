# n=9 Vertex-circle Row0 Root Audit

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note audits one narrow review concern for the repo-native `n=9`
vertex-circle exhaustive checker: the `row0 choices: 70` count is a literal
root-loop count, not a hidden cyclic or dihedral symmetry quotient. It does not
claim a proof of `n=9`, does not claim a counterexample, does not complete
independent review of the exhaustive checker, and does not update the
official/global status.

## Row0 Root Enumeration Lemma

Work with a labelled convex nonagon in fixed cyclic order

```text
0, 1, ..., 8.
```

Each selected-witness row `S_i` is a 4-subset of the other eight labels. In
particular, a complete assignment has a unique row `S_0`, and

```text
S_0 in {4-subsets of {1,2,3,4,5,6,7,8}}.
```

Therefore the root row has exactly

```text
binom(8,4) = 70
```

literal choices.

The checker constructs exactly this universe:

```python
OPTIONS[center] = [
    mask(combo)
    for combo in combinations(
        [target for target in range(N) if target != center],
        ROW_SIZE,
    )
]
```

and the exhaustive search starts with:

```python
for row0 in OPTIONS[0]:
    assign = {0: row0}
    ...
```

Thus `row0` is the first root variable in a fixed-label search. The code does
not replace row0 choices by orbit representatives, does not rotate row0
patterns, and does not identify a row0 choice with its reflection.

## Exact Audit

A one-off exact audit of the checked module reported:

```text
N: 9
ROW_SIZE: 4
binom(N-1, ROW_SIZE): 70
options_per_center: [70,70,70,70,70,70,70,70,70]
row0_count: 70
row0_matches_literal_combinations: true
all_centers_literal: true
row0_unique: true
row0_contains_center: false
first row0 tuple: (1,2,3,4)
last row0 tuple:  (5,6,7,8)
```

The incoming archived script has the same root-loop structure and archived
outputs also report `row0 choices: 70` for both the vertex-circle-pruned run
and the no-vertex-circle-pruning cross-check.

## Scope

This audit addresses only the row0-root universe. It does not prove that every
later pruning rule is necessary, does not prove that dynamic
minimum-remaining-options branching is harmless, and does not independently
replay the 184 pre-vertex-circle assignments.

The remaining frontier-soundness audit still needs to check the pruning
lemmas, the branching order, and the relation between the repo-native checker
and the archive variants.

## Commands

Run the exhaustive checker and the targeted row0 regression test:

```bash
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected

python -m pytest tests/test_n9_vertex_circle_exhaustive.py -q -m "artifact"
```
