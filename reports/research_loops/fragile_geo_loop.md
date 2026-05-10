# Fragile-cover geometric loop

Status: `FAILED_ROUTE` / `NEXT_EXPERIMENT`. This is a bounded research-loop
report, not a proof, not a counterexample, and not a source-of-truth status
change. The official/global status remains falsifiable/open. The local
`n <= 8` result remains repo-local and machine-checked with independent review
recommended for public theorem-style claims.

## Bridge target

Target bridge: strengthen the minimal fragile-cover bridge with a genuinely
geometric necessary condition. The current fragile hypergraph axioms and
two-overlap crossing rule are necessary but too weak; the block-6 family is the
standing negative control.

I used the existing block-6 controls and diagnostics rather than adding code.
No checker is implemented here because the refined condition below is necessary
for geometry but does not yet reject all audited full extensions of the
two-block control.

## Control baseline

Commands run:

```bash
python scripts/check_fragile_hypergraph.py --blocks 1 --json
python scripts/check_fragile_hypergraph.py --blocks 1 --check-full-extension --json
python scripts/check_fragile_hypergraph.py --blocks 2 --assert-ok --json
python scripts/check_fragile_hypergraph.py --blocks 2 --check-full-extension --assert-full-extension --json
```

Observed baseline:

- One block passes the fragile-cover hypergraph check.
- One block fails the optional full selected-row extension check with
  `failure_reason = no extension exists`.
- Two blocks pass the fragile-cover hypergraph check.
- Two blocks also pass the optional full selected-row extension check. The
  first extension found has full rows

```text
0  -> {1,2,3,4}
1  -> {3,6,9,11}
2  -> {1,3,5,8}
3  -> {0,2,4,5}
4  -> {0,3,8,11}
5  -> {0,1,6,7}
6  -> {7,8,9,10}
7  -> {0,4,6,9}
8  -> {0,5,7,10}
9  -> {6,8,10,11}
10 -> {2,5,9,11}
11 -> {1,5,6,10}
```

## Cycle 1: dependency-cycle condition

Propose: forbid directed cycles in the fragile witness map `pi`, or at least
forbid reciprocal fragile-center dependencies.

Audit: the canonical block-6 witness map already has reciprocal dependencies
inside each block:

```text
0 -> 3, 3 -> 0
6 -> 9, 9 -> 6
```

Mental geometric check: a reciprocal pair only says each center belongs to the
other center's critical 4-tie. This forces the two critical radii to share the
same inter-center distance, but equality of two critical radii is not a
contradiction. With a two-overlap, the source chord and common-witness chord can
be mutual perpendicular bisectors, producing a rhombus-type local picture
rather than an immediate impossibility.

Refine: pure acyclicity of `pi` is not established as necessary. Do not
implement it.

## Cycle 2: critical-radius propagation

Propose: apply the minimum-radius short-chord argument to the fragile rows.
For a fragile center `i`, one consecutive pair among its four critical witnesses
is shorter than the critical radius. If an endpoint of that pair is also a
fragile center selecting the other endpoint, this gives a strict radius
inequality between fragile critical radii.

Audit against the two-block full extension used above:

```text
row/column pair caps: pass
minimum-radius fixed-order filter: pass
radius propagation: PASS_ACYCLIC_CHOICE
certified minimum radius-propagation edge count: 5
```

The same run also found many fixed-selection stuck sets in this arbitrary full
extension:

```text
minimal stuck size: 4
total stuck sets at size 4: 449
forward ear order exists: yes, seed {0,7,10}
greedy reverse peeling terminal set: {3,5,7,8,9,11}
```

Interpretation: the radius signal is geometric and necessary in the usual fixed
selected-row setting, but it still has acyclic short-gap choices on this
control. The stuck-set data is useful stress information, not a necessary
geometric obstruction, because the fixed-row ear-orderable bridge remains open.

Refine: radius propagation alone does not reject the two-block control.

## Cycle 3: row-circle Ptolemy quotient

Propose: every full selected-row extension of a geometric fragile-cover system
must satisfy row-circle constraints. For each selected row `i`, its four
witnesses lie on a circle centered at `i`; in their cyclic/angular order they
satisfy Ptolemy equality. Therefore the strict Ptolemy-log inequalities used in
the existing fixed-pattern tooling are valid row-wise necessary inequalities.
If a positive combination of these strict inequalities sums to zero after
quotienting by selected-distance equalities, that full extension is exactly
obstructed.

This is genuinely geometric: it uses concyclicity of each selected witness
quadruple, not just incidence.

Audit 1, first two-block extension: using the existing Ptolemy-log row builder,
the first extension found above has an exact zero Ptolemy-log row:

```text
row: 6
witness order: 7,8,9,10
positive pairs: {7,9}, {8,10}
negative pairs: {7,8}, {9,10}
```

After selected-distance quotienting for that full extension, the row vector is
identically zero. If the full extension were geometric in the supplied cyclic
order, the strict inequality would read `0 > 0`, so that specific full
extension is exactly killed.

Audit 2, bounded extension enumeration: a quick bounded enumeration of full
extensions found a survivor after three extensions examined. That survivor has
no single zero Ptolemy-log row, and a nonnegative zero-sum LP over the
Ptolemy-log rows was infeasible.

The escaping full extension was:

```text
0  -> {1,2,3,4}
1  -> {3,6,9,11}
2  -> {1,3,5,10}
3  -> {0,2,4,5}
4  -> {0,3,8,11}
5  -> {0,1,6,7}
6  -> {7,8,9,10}
7  -> {1,5,6,8}
8  -> {0,5,7,9}
9  -> {6,8,10,11}
10 -> {2,5,9,11}
11 -> {0,4,6,10}
```

I also ran the row-circle Ptolemy NLP diagnostic on the first full extension.
It returned `ROW_CIRCLE_PTOLEMY_NLP_FAILED`, not an obstruction:

```text
distance classes: 31
row Ptolemy equalities: 12
max margin: -0.028147134441496933
row Ptolemy max residual: 0.0006520414228680285
optimizer message: Positive directional derivative for linesearch
```

This numerical failure is not proof of obstruction.

Refine: the row-circle Ptolemy quotient condition is the best candidate from
this loop, but a simple zero-row or positive-cone Ptolemy-log checker is not
yet sufficient to reject the two-block fragile family. A checker should not be
promoted until it searches all relevant full extensions, or until a stronger
exact row-circle certificate is available for the extension family rather than
one extension.

## Blocker

The key quantifier is the blocker:

```text
fragile rows from a minimal counterexample must admit at least one full
selected-row extension satisfying all geometric row-circle constraints.
```

Killing one arbitrary extension is not enough. The current full-extension
diagnostic is existential and returns the first abstract extension it finds.
The row-circle Ptolemy zero-row obstruction kills that first extension, but the
bounded enumeration already found another extension escaping the same simple
certificate.

## Next experiment

The next productive experiment is an all-extension audit for the two-block
control:

1. Enumerate full selected-row extensions of the fixed two-block fragile rows
   under the existing pair/crossing constraints, with explicit node and output
   limits.
2. For each extension, run exact row-circle Ptolemy-log tests:
   single zero rows first, then nonnegative zero-sum cone feasibility after
   selected-distance quotienting.
3. Report one of three outcomes:
   `ALL_EXTENSIONS_KILLED_BY_EXACT_ROW_CIRCLE_CERTIFICATE`,
   `SURVIVOR_EXTENSION_FOUND`, or `UNKNOWN_LIMIT_REACHED`.
4. Only if all extensions are killed with replayable exact certificates should
   this become a tiny checker.

Trust label for the present report: `FAILED_ROUTE` for dependency-cycle and
fragile-only radius acyclicity as immediate filters; `NEXT_EXPERIMENT` for the
row-circle all-extension audit.

## Commands run beyond the baseline

The following were run as inline Python diagnostics without writing artifacts:

```bash
python - <<'PY'
# Imported block6_family/full_selected_extension, stuck-set diagnostics,
# radius-choice optimization, and row_circle_ptolemy_nlp_diagnostic.
# Summarized the first two-block full extension, stuck-set state,
# radius propagation state, and row-circle NLP state.
PY

python - <<'PY'
# Imported scripts/check_ptolemy_log_filter.py helpers.
# Built Ptolemy-log rows for the first two-block full extension and found
# one exact zero row.
PY

python - <<'PY'
# Bounded full-extension enumeration for the two-block fragile rows.
# Examined 3 full extensions, killed 2 by a zero Ptolemy-log row,
# and found 1 survivor without a zero row.
PY

python - <<'PY'
# Ran nonnegative zero-sum LP over the survivor extension's Ptolemy-log rows.
# Result: infeasible for that simple Ptolemy-log cone test.
PY
```

These diagnostics do not alter any repository theorem claim.
