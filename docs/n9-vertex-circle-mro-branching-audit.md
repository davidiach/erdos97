# n=9 Vertex-circle MRO Branching Audit

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note audits one narrow control-flow question in the repo-native `n=9`
vertex-circle exhaustive checker: the dynamic minimum-remaining-options
choice of the next row changes only search order, conditional on the listed
partial filters being sound. It does not claim a proof of `n=9`, does not
claim a counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Minimum-remaining-options Branching Lemma

Let `A` be a partial selected-witness assignment. For each unassigned center
`c`, define `V_c(A)` to be the list of row masks for `c` that pass the current
partial pair/crossing/count filters against `A`.

The checker constructs `V_c(A)` with `valid_options_for_center`: it scans all
literal row masks in `OPTIONS[c]` and appends exactly those not rejected by
compatibility, selected-indegree capacity, or witness-pair capacity against
the current partial assignment.

The recursive search then computes `V_c(A)` for every unassigned center and
chooses a center `c*` with minimum `|V_c(A)|`. If any `V_c(A)` is empty, the
search returns from that partial assignment. Otherwise it branches over every
mask in `V_c*(A)`.

Conditional on the partial filters being necessary conditions, this choice
cannot omit a valid completion:

1. If some `V_c(A)` is empty, no completion extending `A` can exist, because
   every completion must assign a row to `c`, and that row would have to pass
   the same current partial filters.
2. If all `V_c(A)` are nonempty, every completion extending `A` has a unique
   row value `m` at the selected center `c*`, and by definition
   `m in V_c*(A)`.
3. The branch loop iterates over every `m in V_c*(A)`, so the branch
   containing that completion is visited.

Thus the minimum-remaining-options rule is a variable-ordering heuristic in
this finite backtracking search. It is not a quotient and not an additional
mathematical pruning rule.

## Code-shape Audit

The checked source block is
`src/erdos97/n9_vertex_circle_exhaustive.py`.

The option constructor has the required exhaustive shape:

```python
out = []
for m in OPTIONS[center]:
    ...
    out.append(m)
return out
```

The branch selector has the required variable-ordering shape:

```python
best_center = None
best_options = None
for center in range(N):
    if center in assign:
        continue
    opts = valid_options_for_center(...)
    if best_options is None or len(opts) < len(best_options):
        best_center = center
        best_options = opts
        if not opts:
            break
if not best_options:
    return

center = best_center
for m in best_options:
    assign[center] = m
    ...
    search(assign, column_counts, witness_pair_counts)
```

A one-off static audit reported:

```text
exhaustive_search functions: 1
contains best_center: true
contains best_options: true
branches over "for m in best_options": true
zero-options return present: true
valid_options_for_center present: true
```

## Scope

This audit isolates the row-order heuristic only. It does not prove the
geometric necessity of the pair/crossing/count filters, does not audit the
vertex-circle partial pruning predicate, and does not independently replay the
184 pre-vertex-circle assignments.

The remaining frontier-soundness audit still needs to check the pruning
lemmas and the relation between the repo-native checker and archive variants.

## Commands

Run the exhaustive checker and the targeted artifact test:

```bash
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected

python -m pytest tests/test_n9_vertex_circle_exhaustive.py -q -m "artifact"
```
