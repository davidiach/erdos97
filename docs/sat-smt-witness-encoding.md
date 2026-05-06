# SAT/SMT encoding for the n vertex-witness incidence search

## Scope and trust statement

This document describes an extension to the existing pure-Python finite-case
checkers (`src/erdos97/n9_vertex_circle_exhaustive.py` and friends) that
expresses the same necessary combinatorial filters as a SAT or SMT problem
solvable by an off-the-shelf solver.  The motivation is to push the
exhaustive search beyond `n = 9`, where pure-Python enumeration becomes
expensive.

**This is a review-pending finite-case artifact.**  Nothing here proves
Erdos Problem #97 in general.  In particular:

- An **UNSAT** result for a given `n` proves only that *no n-row selected-
  witness incidence pattern survives the encoded combinatorial filters*.
  This is strictly weaker than a geometric proof, since the encoded filters
  are necessary but not sufficient.  When taken together with the existing
  pure-Python checker (which agrees on `n = 9`), it gives a second
  independent route to the finite-case statement.

- A **SAT** result returns one (or more) incidence patterns.  No claim of
  geometric realizability is made or implied.  The returned pattern still
  must clear additional filters (rectangle traps, mutual midpoint matrix
  collapses, Ptolemy/Kalmanson order obstructions, exactification, etc.)
  before it could be considered a candidate.

- A **SAT** result for the realizability SMT (`scripts/smt_realize_witness.py`)
  returns a numerical witness in real coordinates.  Even an exact rational
  witness would not by itself settle Erdos #97 — it would be a candidate
  pattern requiring independent reviewer audit, geometric verification with
  exact arithmetic, and a careful confirmation that strict convexity holds
  in a global sense.

## Variables

We mirror the variable layout of the pure-Python n=9 checker.  For each
center `i` in `{0, ..., n-1}`:

- `OPTIONS[i]` is the list of `C(n-1, 4)` 4-subsets of `{0, ..., n-1} \ {i}`.
- For SMT we use a single integer variable `row_i in {0, ..., |OPTIONS[i]| - 1}`
  plus auxiliary Booleans `x_{i,k}` defined to be `(row_i == k)`.
- For SAT we use one Boolean per `(i, k)` and impose exactly-one over the row.

The 2-dimensional pair indexing matches the existing checker:
`PAIRS = [(i, j) : 0 <= i < j < n]` with bijection `pair_index`.

## Combinatorial constraints (R, P, A, T, W)

| Code | Constraint | Source in repo |
|------|------------|----------------|
| R | Exactly one row choice per center | bookkeeping |
| P | `\|S_i ∩ S_j\| ≤ 2`; on overlap exactly 2, the source chord `(i,j)` and the witness chord `(a,b)` cross in the cyclic order | `n9_vertex_circle_exhaustive.COMPATIBLE` |
| A | Adjacent rows `(i, i+1)` share at most one witness | implied by P; encoded redundantly |
| T | No three rows share three witnesses (three points on a circle pin a unique center) | new vs. n=9 checker; the check is correct because three non-collinear points have a unique circumcenter |
| W | Each unordered witness pair `(a, b)` is covered by at most 2 rows | `MAX_INDEGREE` /  `witness_pair_counts` |

`P` is a 2-row clause; `T` is a 3-row clause.  `W` becomes a cardinality
constraint over the `x_{c,k}` whose option contains both `a` and `b` as
witnesses.

## Vertex-circle constraint (V)

This is the only constraint that requires a non-trivial encoding.  For
each row `(i, k)`:

- `selected_pair_idx[i,k]` is the list of "selected pair" indices
  (the unordered pairs `(i, w)` for each witness `w` in option `k`).
- `strict_edges[i,k]` is the list of nested-chord pairs
  `(outer_pair_idx, inner_pair_idx)` arising from the cyclic order of the
  four witnesses around `i`.  Outer chord *strictly contains* inner chord.

We must decide a global equivalence relation on pair indices such that:

1. If row `(i, k)` is selected, all pair indices in `selected_pair_idx[i,k]`
   share the same equivalence class.
2. Each strict edge `(outer, inner)` becomes a directed edge in the
   resulting class graph.
3. The class graph contains no self-loop and no directed cycle.

### Z3 encoding

We give each pair index `pi` an integer variable `rank[pi]` in
`{0, ..., num_pairs - 1}`.  Then:

- For each row `(i, k)` with selected pairs `[sel_0, sel_1, ..., sel_3]`:
  `x_{i,k} → rank[sel_0] = rank[sel_1] = rank[sel_2] = rank[sel_3]`.
- For each row `(i, k)` and each strict edge `(outer, inner)`:
  `x_{i,k} → rank[outer] < rank[inner]`.

This is a precise integer-programming-style encoding:

- Two pair indices with the same rank are in the same equivalence class.
- Strict-edge endpoints with different ranks have a forced ordering.
- A self-loop in the class graph requires a row to force `rank[outer] = rank[inner]`
  via union-find collapse from elsewhere, plus `rank[outer] < rank[inner]` from the strict
  edge — contradiction.
- A directed cycle on classes requires a chain `r_a < r_b < ... < r_a`, contradiction.

This encoding is sound: if the integer constraints are satisfiable, the
ranks induce an equivalence relation (sets of pair indices with the same
rank) and a strict total order between distinct classes, so the class graph
is acyclic and self-loop-free.  Conversely, if the union-find class graph
of any model from the pure-Python checker is acyclic and self-loop-free,
we can choose ranks to match a topological order on classes.

### Pysat fallback (CEGAR)

The full multi-row class acyclicity does not encode compactly in pure CNF
without polynomially many additional clauses.  The `--solver pysat` mode
runs a counterexample-guided abstraction-refinement (CEGAR) loop:

1. The base CNF encodes only R, P, A, W (plus a sequential-counter
   at-most-2 cardinality constraint per witness pair).
2. Pysat (CaDiCaL) returns a candidate assignment.
3. The candidate is checked with `vertex_circle_status_pattern`, which is a
   direct port of the `n9_vertex_circle_exhaustive` checker.
4. If the candidate fails V (self-edge or strict cycle), we add a no-good
   blocking clause `(¬x_{0,k_0} ∨ ¬x_{1,k_1} ∨ … ∨ ¬x_{n−1,k_{n−1}})` and
   resolve.
5. Otherwise we record the surviving model.

This is sound: a final UNSAT means no assignment satisfies R, P, A, W *and*
V, since every R/P/A/W-feasible assignment is either rejected by the
post-hoc V check or returned as a survivor.  The blocking step uses only
the chosen `x` literals, so the no-good rules out exactly that one
assignment (no spurious extra exclusions).

For n = 9 the CEGAR loop closes in 184 iterations (matching
`EXPECTED_CROSS_CHECK_FULL = 184` in `n9_vertex_circle_exhaustive`),
exactly reproducing the breakdown 158 self-edge + 26 strict-cycle.

### What V proves

Combined with R/P/A/T/W, the V constraint exactly captures the
filters in `n9_vertex_circle_exhaustive.summary_payload`.  Therefore an
UNSAT result on this combined encoding for fixed `n` is equivalent to
"the pure-Python exhaustive search returns 0 surviving patterns at this
`n`".

## Sanity check at n = 9

The pure-Python checker gives 0 surviving patterns at n = 9 (recorded in
`data/certificates/n9_vertex_circle_exhaustive.json`).  We verify that
our SMT encoding agrees: `python3 scripts/sat_encode_vertex_witness.py
--n 9 --solver z3 --output data/certificates/sat_n9_witness.json`.

## n = 11 attempt

For `n = 11`, the encoding has 11 row variables, ~330 4-subset Booleans,
55 pair-rank integers, and a few hundred thousand pair/triple clauses.
The script writes `data/certificates/sat_n11_witness.json` with the result
and (if SAT) a sample pattern.  The result is reported as `unknown` if z3
times out — there is no false UNSAT in that case.

## Realizability follow-up

When the SAT encoding returns a pattern that survives V, we run
`scripts/smt_realize_witness.py` to ask z3-over-the-reals for a
strictly-convex realization in `R^2` with explicit gauge fixed
(`p_0 = (0, 0)`, `p_1 = (1, 0)`).  An SMT result here is a candidate, not
a proof.

## Limitations

- **Filter completeness**: The encoded filters are necessary but not
  sufficient for geometric realizability.  An SMT-SAT pattern may still be
  ruled out by additional filters not encoded here (rectangle traps,
  mutual-midpoint matrix collapses, Kalmanson 2-order obstructions,
  Ptolemy NLP, etc.).
- **Solver soundness**: We rely on z3's correctness for QF_LIA on the rank
  encoding and for QF_NRA for the realizability test.  Z3 is widely used
  but not formally verified.
- **`unknown` results**: Reported honestly.  We never claim `unsat` from
  an `unknown` solver outcome.
