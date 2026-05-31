# n=9 Vertex-circle Partial-pruning Audit

Status: `REVIEW_PENDING_PARTIAL_PRUNING_AUDIT`.

This note audits one narrow pruning question in the repo-native `n=9`
vertex-circle exhaustive checker: once a partial assignment already has a
vertex-circle quotient self-edge or directed strict cycle, later selected rows
cannot repair that obstruction. It does not claim a proof of `n=9`, does not
claim a counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Partial-pruning Monotonicity Lemma

Let `A` be a partial selected-witness assignment and let `B` be an extension of
`A`. The selected rows in `A` generate an equivalence relation `~_A` on
ordinary unordered vertex pairs: selected distances in the same row are
identified. The rows in `B` generate a coarser relation `~_B`, because `B`
contains every row of `A` and may add more equality identifications.

Likewise, every vertex-circle strict edge produced by a row of `A` is still a
strict edge in `B`; later rows may add strict edges but do not remove old ones.

If `A` has a quotient self-edge, then some strict edge `p > q` has
`p ~_A q`. Since `~_B` is coarser, `p ~_B q` too. The same strict edge remains
present, so `B` has a quotient self-edge.

If `A` has a directed strict cycle among `~_A`-classes, map every class in
that cycle to its `~_B`-class. The image is a closed directed walk in the
`B` quotient graph. If any cycle edge has both endpoints mapped to the same
`~_B`-class, then `B` has a quotient self-edge. Otherwise the closed directed
walk has length at least two and contains a directed cycle. Hence `B` has a
strict-cycle obstruction.

Thus vertex-circle partial pruning is monotone: once the checker sees
`self_edge` or `strict_cycle` on a partial assignment, no extension can become
realizable by adding more selected rows.

## Code-shape Audit

The checked source block is
`src/erdos97/n9_vertex_circle_exhaustive.py`.

The quotient construction recomputes the selected-distance union-find from
the currently assigned rows:

```python
for center, m in assign.items():
    selected_pairs = SELECTED_PAIR_INDICES[(center, m)]
    base = selected_pairs[0]
    for pidx in selected_pairs[1:]:
        uf.union(base, pidx)
```

The strict graph also scans the currently assigned rows:

```python
for center, m in assign.items():
    for outer, inner in STRICT_EDGES[(center, m)]:
        outer_root = uf.find(outer)
        inner_root = uf.find(inner)
        if outer_root == inner_root:
            return "self_edge"
        graph[outer_root].append(inner_root)
```

The recursive search applies vertex-circle partial pruning immediately after
adding one row:

```python
status = vertex_circle_status(assign) if use_vertex_circle else "ok"
if status == "ok":
    search(assign, column_counts, witness_pair_counts)
else:
    counts[f"partial_{status}"] += 1
```

An earlier one-off static audit reported:

```text
vertex_circle_status lines: 192-226
self_edge return present: true
strict_cycle return present: true
uf union selected pairs present: true
strict edges from assigned rows present: true
partial prune call present: true
```

## Scope

This audit proves monotonicity of the quotient-graph obstruction under adding
rows. It assumes that selected-row equalities and vertex-circle strict edges
are valid necessary conditions for any realizable assignment.

It does not prove the geometric vertex-circle strict-chord lemma, does not
audit the pair/crossing/count filters, does not independently replay the 184
pre-vertex-circle assignments, and does not prove the full `n=9` finite case.

## Stored-frontier Replay

The command
`scripts/check_n9_vertex_circle_partial_pruning.py --check --assert-expected --summary-json`
turns the monotonicity note into a stored-frontier diagnostic. It scans every
nonempty subset of selected rows from the 184 stored pre-vertex-circle frontier
assignments in
`data/certificates/n9_vertex_circle_frontier_motif_classification.json`.
Use `--json` instead when mismatch examples or other full diagnostic fields are
needed.

The replay checks:

- 184 stored assignments;
- 94,024 nonempty row subsets;
- 58,606 obstructed subsets;
- zero checker/replay status mismatches;
- zero cases where an obstructed subset extends to a stored full assignment
  that is vertex-circle clean.

The subset status counts are:

```text
ok:           35418
self_edge:    24890
strict_cycle: 33716
```

This does not prove frontier coverage, brancher soundness, strict-edge
geometry, selected-distance quotient soundness, `n=9`, a counterexample, or
any official/global status update. It is a reproducibility check for the
partial-pruning step on the stored frontier only.

## Commands

Run the stored-frontier partial-pruning audit:

```bash
python scripts/check_n9_vertex_circle_partial_pruning.py --check --assert-expected --summary-json
```

Run the exhaustive checker and the targeted artifact test:

```bash
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected

python -m pytest tests/test_n9_vertex_circle_exhaustive.py -q -m "artifact"
```
