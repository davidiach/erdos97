# Bridge Lemma A' progress (n=8, n=9 finite test)

This note records an empirical test of **Bridge Lemma A'** (canonical-synthesis,
§5.2) at the finite cases `n = 8` and `n = 9`, plus a note on the n=10/n=11
status and an explicit sub-conjecture.  The script that produces the JSON
certificate is `scripts/test_bridge_lemma_n8_n9.py`; the certificate is
`data/certificates/bridge_lemma_n8_n9_test.json`.

**Trust:** repo-local exploratory finite test.  No proof of Bridge Lemma A' or
Erdős #97 is claimed; no counterexample is claimed.  The 2026-05-05 attack
(`data/certificates/2026-05-05/bridge_lemma_check.json`) already established
the ear-orderability counts; this note adds **structural analysis** and
**empirical realization tests** for the non-ear-orderable patterns.

## Bridge Lemma A' (statement)

> Every realizable strictly-convex `k=4` counterexample to Erdős #97 admits
> some ear-orderable witness selection.

An *ear-orderable* witness pattern is a vertex ordering `v_1, ..., v_n` such
that for every `k ≥ 4`, `|W_{v_k} ∩ {v_1, ..., v_{k-1}}| ≥ 3`.  Combined with
the rank theorem (rank `R_W(p) = 2n - 3` generically for ear-orderable `W`)
and the Euler-homogeneity bound (rank `≤ 2n - 4` at solutions), Bridge Lemma A'
would close Erdős #97.

## Empirical findings at n=8

The 15 incidence-survivor classes (`data/incidence/n8_reconstructed_15_survivors.json`):

- **Ear-orderable:** 11 classes (ids 4–14).
- **Non-ear-orderable:** 4 classes (ids 0, 1, 2, 3).

**Mutually-witnessed K_k cores.**  Define a *K_k core* as a vertex subset
`U ⊆ V` of size `k` such that for every `v ∈ U`, all `k-1` other vertices of
`U` lie in `W_v`.

| id | ear? | K_4 cores | K_3 cores | largest 3-seed closure |
|---:|:----:|:---------:|:---------:|:----------------------:|
| 0 | no | `{0,1,2,3}, {4,5,6,7}` | many | <8 |
| 1 | no | `{0,1,2,3}, {4,5,6,7}` | many | <8 |
| 2 | no | `{0,1,2,3}, {4,5,6,7}` | many | <8 |
| 3 | **no** | **none** | 8 | 5 |
| 4–14 | yes | none | many | 8 |

**Geometric obstruction for K_4 cores (clean argument).**  If `{a,b,c,d}`
is a K_4 mutually-witnessed core, then each of `a,b,c,d` has the other three
as part of its 4-witness set on a common circle around it:

- `b, c, d` all lie at distance `r_a` from `a`.
- `a, c, d` all lie at distance `r_b` from `b`.
- `a, b, d` all lie at distance `r_c` from `c`.
- `a, b, c` all lie at distance `r_d` from `d`.

The four constraints `|ab|=r_a=r_b`, `|ac|=r_a=r_c`, `|ad|=r_a=r_d`, `|bc|=r_b=r_c`,
`|bd|=r_b=r_d`, `|cd|=r_c=r_d` force `r_a = r_b = r_c = r_d` and all six pairwise
distances equal — a **regular tetrahedron**, which embeds in `R^3` but not in
`R^2`.  ∎

This argument **immediately rules out ids 0, 1, 2** at n=8.

**id 3 is non-ear without a K_4 core.**  This is the new finding from this
script.  id 3 has no K_4 mutually-witnessed core but has 8 K_3 cores; the
largest 3-seed forward-closure reaches only 5 of 8 vertices.  The Groebner
basis kill at id 3 (`data/certificates/2026-05-05/n8_groebner_results.json`)
is independent of the K_4-core argument.

**Refined sub-conjecture (revised).**  The pre-task hypothesis "K_4-stuck cores
are geometrically unrealizable, and Bridge Lemma A' reduces to that" is
**only partially** correct:

- ✓ K_4 mutually-witnessed cores ARE geometrically unrealizable (regular
  tetrahedron in R^2).
- ✗ Non-ear-orderable patterns at n=8 are NOT all K_4-core patterns: id 3
  is a counterexample.

So Bridge Lemma A' does NOT cleanly reduce to "K_4-cores are unrealizable"
alone.  At least at n=8, a second mechanism (here, the Groebner kill of id 3)
is needed.

## Empirical findings at n=9

Among the 184 4-regular witness assignments surviving incidence filters
(before the vertex-circle filter), per the 2026-05-05 cross-tabulation:

- **Ear-orderable:** 182 patterns.
- **Non-ear-orderable:** 2 patterns (idx 81 and idx 151).

The two non-ear patterns are circulants on `Z/9` with offsets `{1,3,6,7}`
(idx 81) and `{2,3,6,8}` (idx 151, the `v -> -v` image of idx 81).  Both are
killed by the strict-cycle vertex-circle obstruction.

**At n=9, no surviving pattern has a K_4 mutually-witnessed core.**  The two
non-ear patterns are circulants whose largest mutually-witnessed clique is
only K_3.  The geometric obstruction is therefore *not* the regular-tetrahedron
mechanism — it is the strict-cycle/self-edge vertex-circle obstruction.

This means at n=9 the K_4-core sub-conjecture is **vacuously consistent** (no
K_4 cores survive at all), but it does not contribute to closing the non-ear
cases.  Bridge Lemma A' at n=9 holds because the strict-cycle obstruction
kills both non-ear patterns.

## Geometric realization tests (least-squares)

For each non-ear-orderable pattern, the script runs least-squares minimization
of the squared-distance equality residuals across multiple modes (polar,
direct, support) and restarts.  All residuals are well above zero, consistent
with non-realizability:

| pattern | best mode | `eq_rms` | `max_spread` | `convexity_margin` |
|:--|:--|--:|--:|--:|
| n=8 id 0 | direct | 6.673e-01 | 2.394 | -0.034 |
| n=8 id 1 | polar | 6.676e-01 | 2.426 | -0.029 |
| n=8 id 2 | direct | 6.586e-01 | 2.345 | -0.024 |
| n=8 id 3 | polar | 6.634e-01 | 2.451 | -0.032 |
| n=9 idx 81 | direct | 8.882e-01 | 3.179 | -0.014 |
| n=9 idx 151 | direct | 8.882e-01 | 3.179 | -0.014 |

All convexity margins are NEGATIVE (the optimizer cannot find a strictly
convex configuration), and all `eq_rms` values are large (the optimizer
cannot drive the squared-distance equalities to zero either).  No realization
was found, consistent with non-realizability — though least-squares failure
is not a rigorous proof of non-existence.

- See `data/certificates/bridge_lemma_n8_n9_test.json` →
  `realization_tests` for the full per-pattern records (coordinates,
  pairwise distance tables, etc.).

The numerical residuals do not constitute a proof of unrealizability; they
are evidence that the optimizer cannot find a feasible point.  The exact
unrealizability proofs at n=8 are the n8 Groebner kills (basis = `{1}`) on
`data/certificates/2026-05-05/n8_groebner_results.json`.

## Status of n=10 and n=11

- **n=10**: per `data/certificates/n10_vertex_circle_singleton_slices.json`,
  zero surviving full assignments under vertex-circle pruning, so Bridge
  Lemma A' is **vacuously satisfied at n=10** for the surviving witness
  systems.  Pre-vertex-circle survivors were not enumerated here (would
  require the same multi-day budget noted in the n=10 secondary artifact).
- **n=11**: per `data/certificates/2026-05-05/n11_partial.json`, the full
  exhaustive search projects to 40+ core-hours and has not been run.  The
  cyclic-shift pre-screen rules out all 175 cyclic 4-subsets, suggesting any
  hypothetical n=11 counterexample (if it exists) would have to be aperiodic.

These two cases are deferred — beyond the budget of this script.  No claim is
made about Bridge Lemma A' at n ≥ 10.

## Honest summary

- Bridge Lemma A' **holds empirically at n=7, n=8, and n=9** (within the
  scope of the surviving witness systems).
- The K_4-mutually-witnessed-core obstruction is a clean geometric fact: it
  rules out ids 0, 1, 2 at n=8 by the regular-tetrahedron argument.
- The K_4-core sub-conjecture **does NOT subsume** Bridge Lemma A' at n=8:
  id 3 is non-ear without a K_4 core, and the n=9 non-ear circulants have no
  K_4 cores either.
- The complementary obstructions (Groebner = `{1}` at n=8 ids 3, 4, 5, 12,
  14; strict-cycle vertex-circle at n=9) close the remaining non-ear cases
  by independent machinery.
- **No proof of Bridge Lemma A' at general n is given here.**

Files produced:

- `scripts/test_bridge_lemma_n8_n9.py` — analysis script.
- `data/certificates/bridge_lemma_n8_n9_test.json` — JSON certificate.
- `docs/bridge-lemma-progress.md` — this note.

## Open subtasks (follow-ups)

1. Enumerate pre-vertex-circle survivors at n=10 to extend the
   ear-orderability census (multi-day compute).
2. Look for **structural commonality** of id 3 (n=8) and idx 81/151 (n=9):
   they are all non-ear without K_4 cores.  Is there a common
   stuck-set / circulant structure that *implies* unrealizability without
   case-by-case Groebner / vertex-circle checks?  This is the natural next
   sub-conjecture to test.
3. For id 3 at n=8, decode the Groebner kill into a human-readable obstruction
   (currently only "basis = `{1}`" is recorded); compare it to the strict-cycle
   obstruction at n=9 to see if they share a graph-theoretic shadow.
