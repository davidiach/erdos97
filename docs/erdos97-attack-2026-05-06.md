# Erdős Problem #97 — Multi-agent Attack Report (2026-05-06)

**Status:** No general proof and no counterexample of Erdős #97 are claimed in
this round. The official/global status of Erdős #97
(erdosproblems.com/97, last edited 2025-10-27) remains FALSIFIABLE/OPEN.

This document summarizes a coordinated multi-agent attack run on
2026-05-06 in the `claude/erdos-97-conjecture-EwpmU` branch. It builds on
the 2026-05-05 round (`docs/erdos97-attack-2026-05-05.md`).

## TL;DR

The 2026-05-06 round produced:

0. **Asymmetric-kite case of canonical-chord injectivity PROVED**
   (review-pending; `docs/asymmetric-kite-closure.md`,
   `data/runs/2026-05-06/asymmetric_kite_proof.py`). This was the open half
   of the §5.3 Selection Lemma program (canonical-chord injectivity); the
   symmetric case was proved 2026-05-05. The asymmetric case uses a
   product-to-sum factorization of the CCW left-turn cross product at `p`
   into a product of three sines (or a sine and a cosine), all strictly
   positive on the canonical-chord constraint box `α_i, α_j ∈ (0, π/6)`,
   `A, B ∈ [3α_·, π − 3α_·)`, under the WLOG `r_i ≤ r_j` (i.e.
   `α_i ≥ α_j`). The cosine factor `cos((A + α_i + 2α_j) / 2)` is
   strictly positive precisely because `α_i ≥ α_j`. Combined with the
   2026-05-05 symmetric proof, this gives **canonical-chord injectivity**
   on the bad set. **Erdős #97 settles via §5.3 IF the noncrossing claim
   also closes** (currently 0/1935 numerical violations; analytic proof
   open). All identities sympy-verified at exact rational arithmetic.

1. **Complete second-source proof of n = 9** (review-pending). The 2026-05-05
   round left 16 / 184 labelled selected-witness assignments at n = 9 (in
   families F07/F08/F09/F13) without a replayable real-root / non-degeneracy
   decoder. This round adds explicit Gröbner real-root decoders for all four
   families (`docs/n9-groebner-decoders.md`,
   `data/certificates/n9_groebner_real_root_decoders.json`). Combined with
   the prior 168 / 184, the n = 9 finite case is now killed by Gröbner-basis
   methods alone (150 GB={1}, 18 univariate `y_8^2 + 1/4 = 0`, 16 by
   real-root + strict-convexity audit on `Q(sqrt(3))`). All 80 real
   algebraic configurations across F07–F13 collapse to coincident vertices
   on a hexagonal lattice.

2. **Independent cross-checks of the n = 9 vertex-circle result:**
   - A from-scratch reimplementation that does not import from the canonical
     module reproduces the 70-row0 → 184-leaf → 0-survivor split with
     identical 158 self-edge / 26 strict-cycle counts
     (`docs/n9-independent-cross-check.md`,
     `scripts/check_n9_independent.py`).
   - A SAT encoding (pysat) confirms the same UNSAT verdict: 184 rejections,
     0 admissible witness systems
     (`scripts/sat_encode_vertex_witness.py`,
     `data/certificates/sat_n9_witness.json`).

3. **Closure of the n = 9 three-cap rigid (2,2,2) sub-case** (conditional on
   the cap-occupancy hypothesis already used at n = 8): 0 / 184 cross-check
   survivors admit the (2,2,2) cap-occupancy under any element of D_9
   (`docs/n9-three-cap-rigid.md`,
   `data/certificates/n9_three_cap_222.json`,
   `scripts/check_n9_three_cap_222.py`). This gives an independent
   parallel route to n = 9 closure that does not invoke the vertex-circle
   filter.

4. **Short human-readable proof of n ≤ 8** (`docs/n8-short-proof.md`). A
   self-contained 3-page proof using only L2 (no three collinear) and L4
   (perpendicular-bisector vertex bound), plus elementary plane geometry:
   base-apex isosceles count gives n ≥ 8, and at n = 8 the equality case
   forces an equilateral octagon whose length-3 diagonals impose a
   `τ_j = 2π/3` vertex cover of the 8-cycle, giving total exterior turning
   ≥ 8π/3 > 2π.

5. **K_4 mutually-witnessed core obstruction** (`docs/bridge-lemma-progress.md`,
   `data/certificates/bridge_lemma_n8_n9_test.json`,
   `scripts/test_bridge_lemma_n8_n9.py`). A clean geometric argument:
   if 4 vertices form a mutually-witnessed core (each is in the others'
   selected sets), all 6 pairwise distances are equal — a regular tetrahedron
   in R², impossible. This rigorously rules out n = 8 incidence-survivor
   ids 0, 1, 2 (each containing the cores `{0,1,2,3}` and `{4,5,6,7}`).
   id 3, F12 at n = 9, and the n = 9 non-ear circulants idx 81 / 151 are
   *not* covered by this argument and require Gröbner / vertex-circle.
   So Bridge Lemma A' does NOT cleanly reduce to "K_4-cores are unrealizable"
   alone, contrary to the prior sub-conjecture in
   `docs/erdos97-attack-2026-05-05.md`.

6. **Ear-elimination rank theorem (Route B explicit minor)** with symbolic
   verification at n = 5, 6 (`docs/ear-rank-theorem-route-B.md`,
   `scripts/verify_ear_rank.py`,
   `data/certificates/ear_rank_verification.json`). This addresses the
   gauge-fixing gap (§6.5 of `docs/canonical-synthesis.md`) by exhibiting a
   `(2n-3) × (2n-3)` minor whose determinant factors as a block-triangular
   product of small symbolic determinants, each verifiably nonzero at a
   generic rational evaluation point.

7. **Endpoint Control mixed-side analysis** (`docs/endpoint-control-mixed-side.md`,
   `scripts/test_endpoint_control_mixed.py`). Symmetric mixed-side closed
   by an elementary forced-coincidence argument; asymmetric mixed-side
   open with explicit identification of the obstruction. The 2+2 framing
   in the prior 2026-05-05 attack is sharper than necessary: 1+1 mixed
   suffices for the `M(j^-) ≤ m - 1` reduction.

8. **No counterexample at n ∈ {11, 12, 13, 14, 15} in the 2026-05-06 sweep**
   (`scripts/sweep_2026_05_06.py`,
   `scripts/search_new_patterns.py`,
   `scripts/anneal_search.py`,
   `data/runs/2026-05-06/`). Tested 51 patterns at n = 11 (5 passed
   incidence pre-filters; best `eq_rms = 0.84`, far from `1e-8` target),
   77 at n = 12 (15 passed; best `eq_rms = 0.65`), with simulated annealing
   and SLSQP refinement. No robust convergence, no near-miss with simultaneous
   `eq_rms < 1e-8` and `convexity_margin > 1e-3` and `min_edge > 1e-3`.

9. **Negative findings (filters that don't add new kills):**
   - **Inversion / Möbius filter** (`docs/inversion-filter.md`,
     `data/certificates/inversion_filter_test.json`):
     6 audits F1–F6 implemented; 0 kills on n = 8 (15 patterns) and n = 9
     (184 cross-check survivors). All audits are implied by the existing
     pair-cap filter.
   - **Paraboloid lift / column-Plücker subsystem**
     (`docs/paraboloid-lift-attack.md`,
     `data/certificates/paraboloid_lift_test_n8.json`): the dual
     column-determinant Plücker subsystem is an algebraic *consequence* of
     the existing row equidistance system. Mathematically equivalent, no
     new exact obstructions.
   - **Probabilistic / entropy methods**
     (`docs/probabilistic-method-attack.md`): no asymptotic improvement on
     Pach–Sharir's `f(n) ≪ n^{2/5}` bound. Did extract that the base-apex
     isosceles count gives `f(n) ≤ ⌊(1 + √(8n−15))/2⌋ = O(√n)` for
     strictly convex polygons, sharper than the general n^{2/5}, but only
     gives `f(n) ≤ 3` for n ≤ 7 (already known). This is a re-statement of
     the n=8 short proof's §1, packaged for general n.

10. **Stronger filters at higher n proposed but not yet tested**
    (`docs/stronger-filters.md`, `src/erdos97/stronger_filters.py`,
    `scripts/test_stronger_filters.py`): three new filters
    (triple uniqueness, forced-perpendicularity 2-coloring, mutual-rhombus
    rational closure) applied incrementally during search to prune deeper.
    Status: ran on n=9; benchmark on n=11 still in progress at time of
    report.

11. **Literature unchanged from 2026-05-05**
    (`docs/literature-update-2026-05-06.md`): no new papers, no new Lean
    proofs, no new constructions. Erdős #97 remains FALSIFIABLE/OPEN with
    `f(n) ≪ n^{2/5}` (Pach–Sharir) the standing combinatorial bound.

12. **n = 10 integrated exhaustive run** in progress
    (`docs/n10-vertex-circle-exhaustive.md`,
    `scripts/check_n10_vertex_circle_exhaustive.py`). The singleton-slice
    artifact (`data/certificates/n10_vertex_circle_singleton_slices.json`)
    already covers all 126 row0 choices independently and reports 0 full
    assignments; the integrated rerun is intended to corroborate it without
    row0 slicing.

## What this round did NOT produce

- A proof of Erdős #97 (a single missing ingredient remains: the
  noncrossing claim of §5.3, supported by 0/1935 numerical violations
  but lacking an analytic proof).
- A counterexample to Erdős #97.
- A push of the finite case to n ≥ 11 (n = 11 vertex-circle search remains
  too slow in Python; the Cython/C port and SAT encoding sample, but full
  coverage is still ~40 core-hours).
- A proof of Bridge Lemma A' at general n.
- A proof of the noncrossing claim that completes §5.3.
- A proof of the asymmetric Endpoint Control mixed-side sub-claim.
- A new algebraic obstruction beyond what existing Gröbner / vertex-circle
  methods deliver.

## Theoretical-program progress (cumulative, as of 2026-05-06)

| Program | Status |
|---|---|
| Lemma 12 / Endpoint descent | Symmetric mixed-side closed; asymmetric open with localized obstruction. |
| Ear-elimination + Bridge Lemma A' | Rank theorem Route B (explicit minor) verified at small n. K_4-core obstruction proves 3/4 non-ear classes at n=8. Bridge Lemma A' general n still open. |
| Selection lemma / canonical-chord injectivity | Symmetric kite proved (2026-05-05); **asymmetric kite proved this round, review-pending** (`docs/asymmetric-kite-closure.md`). Combined: canonical-chord injectivity is proved (review-pending). The remaining noncrossing claim is the only blocker for §5.3 to settle Erdős #97. |
| Three-cap SEC / Moser cap | Diameter case proved; (2,2,2) rigid case at n=9 closed (this round, conditional). Non-rigid cases at n ≥ 10 open. |
| Distance-bound reduction | Uniform-radius case still conditional on Erdős–Fishburn (open since 1992). Variable-radius case still no attack. |

## Combinatorial / algebraic verification matrix (cumulative)

| n  | Finite-case status | Algebraic second source |
|----|-------------------|-------------------------|
| ≤ 6 | Proved (direct) | trivial |
| 7   | Proved (Fano parity) | trivial |
| 8   | Proved (incidence + 14 perpbis/collinear/equal-dist + 1 Gröbner; also short hand proof in `docs/n8-short-proof.md`) | All 15 GB-only proofs (14 GB={1}, 1 zero-dim with strict-convexity audit) |
| 9   | Vertex-circle proved-locally (review-pending); SAT confirms; 3-cap (2,2,2) closes via separate route | **All 184 patterns: 150 GB={1}, 18 univariate `y_8^2 + 1/4 = 0`, 16 real-root + strict-convexity audit on `Q(sqrt(3))` (this round)** |
| 10  | Vertex-circle singleton slices: 0 / 126; integrated run in progress | n/a (no surviving system to feed) |
| 11  | Single row-0 sample: 0 / 8 in 300s; full coverage ≥ 40 core-hours; SAT encoding viable but slow; cyclic 4-subset screen rules out all 175 cyclic patterns | n/a |
| ≥ 12 | open | open |

## Honest assessment

The 2026-05-06 round did **not** produce a complete proof of Erdős #97 or
a counterexample. Its primary contributions are:

- **Asymmetric-kite analytic closure** (review-pending), giving full
  canonical-chord injectivity. One remaining sub-claim
  (noncrossing of canonical chords, computationally robust at 0/1935
  test polygons) blocks §5.3 from settling Erdős #97 entirely.
- **Complete second-source algebraic proof** of n = 9 (review-pending),
  via Gröbner basis methods alone (150 GB={1}, 18 univariate
  `y_8^2 + 1/4 = 0`, 16 real-root + strict-convexity audit on
  `Q(sqrt(3))`).
- **Independent SAT and from-scratch Python cross-checks** of the n = 9
  vertex-circle exhaustive result, removing implementation-bug risk.
- **Three-cap (2,2,2) closure** at n = 9 via combinatorial enumeration
  conditional on the cap-occupancy hypothesis.
- **K_4 mutually-witnessed core obstruction**: rigorous geometric
  proof that 3/4 non-ear-orderable n = 8 incidence classes are
  unrealizable.
- **Ear-elimination rank theorem Route B** (explicit minor) closes the
  §6.5 gauge-fixing gap at small n.
- **Endpoint Control mixed-side**: symmetric closed; asymmetric reduced
  to a 1+1 sub-claim.
- **Negative findings recorded**: inversion / Möbius filter, paraboloid
  Plücker subsystem, kite-identity / few-distance / row-chord-order
  filters all add 0 new exact obstructions on registered patterns.

This does **not** alter the official/global FALSIFIABLE/OPEN status of
Erdős #97. The variable-radius `n ≥ 10` case is unchanged at the level
of finite enumeration, but the §5.3 Selection Lemma program is now one
sub-claim (noncrossing of canonical φ-chords) away from a complete
solution of Erdős #97 — the highest-leverage outstanding sub-task in the
repo.

## File-level provenance

```
docs/asymmetric-kite-closure.md
docs/n8-short-proof.md
docs/n9-groebner-decoders.md
docs/n9-independent-cross-check.md
docs/n9-three-cap-rigid.md
docs/bridge-lemma-progress.md
docs/endpoint-control-mixed-side.md
docs/ear-rank-theorem-route-B.md
docs/inversion-filter.md
docs/paraboloid-lift-attack.md
docs/stronger-filters.md
docs/sat-smt-witness-encoding.md
docs/probabilistic-method-attack.md
docs/literature-update-2026-05-06.md
docs/n10-vertex-circle-exhaustive.md
docs/erdos97-attack-2026-05-06.md   # this file

data/certificates/n9_groebner_real_root_decoders.json
data/certificates/n9_three_cap_222.json
data/certificates/bridge_lemma_n8_n9_test.json
data/certificates/ear_rank_verification.json
data/certificates/inversion_filter_test.json
data/certificates/paraboloid_lift_test.json
data/certificates/paraboloid_lift_test_n8.json
data/certificates/new_filters_test.json
data/certificates/sat_n9_witness.json
data/certificates/n10_groebner_survivors_cache.json

data/runs/2026-05-06/
  search_new_patterns_summary.json
  sweep_n11.json
  sweep_n12.json
  S13_sidon_1_2_5_7_slsqp_m1e-03_seed42.json

scripts/anneal_search.py
scripts/check_n9_independent.py
scripts/check_n9_three_cap_222.py
scripts/check_n10_vertex_circle_exhaustive.py
scripts/check_n11_vertex_circle_fast.py
scripts/decode_n9_groebner_f07_f13.py
scripts/groebner_n10.py
scripts/n11_fast.c
scripts/sat_encode_vertex_witness.py
scripts/search_new_patterns.py
scripts/smt_realize_witness.py
scripts/sweep_2026_05_06.py
scripts/test_bridge_lemma_n8_n9.py
scripts/test_ear_orderable_higher_n.py
scripts/test_endpoint_control_mixed.py
scripts/test_inversion_filter.py
scripts/test_new_filters.py
scripts/test_paraboloid_filters.py
scripts/test_stronger_filters.py
scripts/verify_ear_rank.py

src/erdos97/inversion_filter.py
src/erdos97/new_filters.py
src/erdos97/paraboloid_lift_filters.py
src/erdos97/stronger_filters.py
```

Each artifact is `REVIEW_PENDING`. None promotes the official/global
FALSIFIABLE/OPEN status of Erdős #97. Each carries the standard caveat:
independent reviewer audit is required before any public theorem-style use.
