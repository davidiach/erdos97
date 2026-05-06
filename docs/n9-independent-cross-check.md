# n=9 Independent Cross-check of the Vertex-circle Exhaustive Result

Status: `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`.

This note records an independent cross-check of the n=9 vertex-circle
exhaustive finite-case result. It does not claim a general proof of Erdős
Problem #97 and does not claim a counterexample. The official/global status
remains falsifiable/open.

## Why an independent cross-check?

Priority 5 of `docs/review-priorities.md` asks for an audit of:

- the absence of a hidden symmetry quotient in the 70 row0 choices;
- that the canonical minimum-remaining-options branching changes only the
  search order, not the leaf set;
- that the raw 184/16 archive variants agree with the repo-native counts.

The canonical checker is in `src/erdos97/n9_vertex_circle_exhaustive.py`. This
cross-check is implemented independently in `scripts/check_n9_independent.py`
and is **not allowed to import** from the canonical module. It re-implements
every primitive needed (open arc, chord crossing, row enumeration, pairwise
compatibility, vertex-circle nested-chord predicate, union-find quotient) in
a separate file.

## What is different

The canonical checker uses:

1. dynamic minimum-remaining-options row order;
2. vertex-circle pruning *applied incrementally* during recursion;
3. one common precomputed compatibility table (`COMPATIBLE`).

The independent cross-check uses:

1. **sequential row order 0, 1, 2, ..., 8** (fixed, no min-remaining
   heuristic);
2. **vertex-circle filter applied only at the leaves** (after rows 0..8 are
   all chosen by filters 1–4);
3. **two redundant enumerations** in the same script: a recursive *generator*
   and a separate *brute-force* search that produces the same leaf set; both
   use a freshly built compatibility table that is independent of the
   canonical one.

If the search order or the canonical incremental pruning had been silently
suppressing a leaf, this cross-check would catch it: the leaves are produced
*without* the vertex-circle filter, sorted lexicographically, and compared
between the two independent search routines. After agreement, vertex-circle
is applied separately to each leaf with a fresh implementation.

## Reproduced counts

The script `scripts/check_n9_independent.py` reproduces the following counts
without consulting the canonical checker:

```text
row0 choices                       : 70   (no symmetry quotient)
filter-1..4 leaves (generator)     : 184
filter-1..4 leaves (brute force)   : 184
vertex-circle self_edge            : 158
vertex-circle strict_cycle         :  26
vertex-circle full survivors       :   0
ear-orderable leaves               : 182
non-ear-orderable leaves           :   2
```

These match every count in `data/certificates/n9_vertex_circle_exhaustive.json`
and the 2026-05-05 attack report's bridge-lemma section
(`data/certificates/2026-05-05/bridge_lemma_check.json`).

## What the cross-check actually verifies

- **70 row0 choices.** ``C(8, 4) = 70`` already, so the row0 count *cannot*
  hide a symmetry quotient. Any cyclic-shift or dihedral quotient would only
  reduce the count below 70; the 70 here is the full, unquotiented row0
  enumeration. The script enumerates rows directly via
  ``itertools.combinations`` and asserts the count is 70.

- **184 cross-check leaves.** Filters 1–4 (witness overlap ≤ 2; two-overlap
  source/witness chords cross; pair count ≤ 2; indegree ≤ 5) produce 184 full
  selected-witness assignments at n=9. The cross-check produces these via two
  independent search routines whose outputs are cross-validated for equality.

- **184 → 0 split.** The vertex-circle predicate, freshly reimplemented here,
  reports 158 self-edge and 26 strict-cycle obstructions. **Every** one of
  the 184 candidate full assignments is killed by an exact vertex-circle
  obstruction. Zero full assignments survive all filters.

- **Ear-orderability bonus.** Of the 184 leaves, 182 admit an ear ordering
  and 2 do not, under the canonical "3-vertex seed + (>= 3 internal
  witnesses) closure" definition from
  ``scripts/test_bridge_lemma_n8_n9.py::is_ear_orderable``. The 2
  non-ear-orderable leaves are exactly the two Z/9 circulants with offset
  multisets ``{1, 3, 6, 7}`` and ``{2, 3, 6, 8}``, in agreement with the
  2026-05-05 attack report. Cross-tabulating with vertex-circle status
  yields ``{ear|self_edge: 158, ear|strict_cycle: 24,
  non_ear|self_edge: 0, non_ear|strict_cycle: 2,
  ear|ok: 0, non_ear|ok: 0}``, identical to the canonical
  `bridge_lemma_check.json` cross-tabulation.

## What the cross-check does NOT verify

- It does not re-prove the geometric necessity of the filters. Necessity
  arguments for each filter are recorded in
  `docs/vertex-circle-order-filter.md` and elsewhere; the cross-check assumes
  them.
- It does not replay the algebraic Gröbner-basis cross-check from
  `data/certificates/2026-05-05/n9_groebner_results.json`. Those are
  different second-source obstructions for the same 184 leaves.
- It does not extend to n=10 or n=11.

## Honesty notes

- The independent script computes its own ``OPTIONS``/``COMPATIBLE``/
  ``STRICT_EDGES`` analogues from scratch. It does NOT import from
  ``src/erdos97/n9_vertex_circle_exhaustive.py``. However, the *underlying
  combinatorial primitives* (cyclic distance, chord crossing, nested
  containment in angular order around a vertex, distance-class quotient) are
  inherently the same. Two checkers using the same definitions of "selected
  witness", "two-overlap chord crossing", and "vertex-circle nested
  containment" should agree numerically; the value of this cross-check is in
  protecting against *implementation* bugs (off-by-one, accidentally
  symmetry-quotienting, wrong angular sort), not in providing a different
  *theory* of the obstruction.
- Sequential row order vs. min-remaining row order: the LEAF set of a
  backtracking search is invariant under the row order that backtracking
  uses. Different search orders only change the *internal* node count, not
  the set of full assignments reached. The cross-check exploits this
  invariance to detect search-order bugs; it does not re-derive the canonical
  node count.
- The canonical checker reports ``nodes_visited = 100,817`` for the
  vertex-circle-disabled cross-check. The independent script processes more
  internal nodes (sequential row order is less aggressive than min-remaining
  row order), but produces the same 184-leaf set; that is the relevant
  invariant.

## Reproduction

```bash
python scripts/check_n9_independent.py
python scripts/check_n9_independent.py --assert-expected
python scripts/check_n9_independent.py --write   # regenerates JSON
```

Output JSON: `data/certificates/n9_independent_check.json`.

## Conclusion

The independent cross-check confirms every advertised count of the canonical
n=9 vertex-circle exhaustive result. There is no hidden symmetry quotient
(70 = C(8,4) = 70), no leak from min-remaining row order (the sequential
generator and brute-force enumerator agree on the 184 leaves), and the
184-to-0 vertex-circle split (158 self-edge + 26 strict cycle) reproduces
exactly. The 2026-05-05 ear-orderable bonus count (182/2) is also reproduced
under the canonical "3-vertex seed + (>= 3 internal witnesses) closure"
definition, including the cross-tabulation with vertex-circle status.

This cross-check builds confidence in the n=9 finite case but does not change
the repo's claim status: no general proof of Erdős Problem #97 is claimed,
no counterexample is claimed, the global status remains falsifiable/open,
and the established repo-local source-of-truth small-case result is the
n ≤ 8 selected-witness artifact.
