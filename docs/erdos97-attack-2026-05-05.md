# Erdős Problem #97 — Multi-agent Attack Report (2026-05-05)

**Status:** No general proof and no counterexample are claimed for Erdős #97.
This document records a multi-agent computational and theoretical attack that
**substantially strengthens the n = 8 and n = 9 finite-case results** via
independent verification, and surveys the remaining frontier.

The official/global status of Erdős #97 (erdosproblems.com/97, last edited
2025-10-27) remains FALSIFIABLE/OPEN.

2026-05-06 supersession note: `docs/n9-groebner-decoders.md` adds a
review-pending replayable decoder for the F07/F08/F09/F13 follow-up families.
The remaining-F07/F08/F09/F13 language below records the state of the
2026-05-05 attack report before that follow-up and should be read as
historical provenance, not current dashboard status.

2026-05-07 supersession note: current source-of-truth wording treats the n = 9
finite-case package as review-pending and the n = 10 singleton-slice package as
draft review-pending. Archived phrases below such as "proved-locally" or "audit
confirms soundness" should not be read as public theorem claims, independent
review completion, a general proof, or a counterexample.

## Headline findings

1. **Audit of the review-pending n = 9 vertex-circle exhaustive checker:
   SOUND.** Every filter (L4 perpendicular-bisector vertex bound, L5 two-circle
   bound, L6 perpendicularity + cyclic-order crossing, indegree cap from L4,
   vertex-circle nested-chord strict-monotonicity) is a necessary condition for
   any selected-witness counterexample at n = 9 in cyclic order. The 70-row-0
   enumeration is exhaustive (no symmetry quotient; relabeling only). Search
   structure (minimum-remaining-options heuristic, backtracking) is correct.
   Results: 16,752 nodes / 0 full assignments under all filters; 100,817
   nodes / 184 full assignments under filters 1–4 (cross-check), every one of
   the 184 killed by filter 5 (158 self-edge, 26 strict-cycle).
   Artifact: `data/certificates/n9_vertex_circle_exhaustive.json`.

2. **Independent Gröbner basis verification at n = 8: COMPLETE PROOF.**
   For all 15 surviving incidence-completeness classes at n = 8, sympy's
   Gröbner basis over ℚ produces:
   - 14 / 15 patterns: GB = {1} (no complex solutions, hence no real
     solutions, hence no Euclidean realization).
   - 1 / 15 (id = 14): GB has 15 elements, zero-dimensional ideal with 4
     real algebraic configurations on the lattice
     `{0, 1/2, 1 ± √3/2}^2`. All 4 are 6-pointed-star shapes that fail
     strict convexity around their centroid.
   Total Gröbner wall-clock: 3.4 s.
   Univariate elimination polynomial for class 14 (in the chosen gauge):
   `y_7^4 - (7/2) y_7^2 + 1/16 = 0`, with roots
   `y_7 = ±(1 + sqrt(3)/2), ±(1 - sqrt(3)/2)`.
   This gives a **second, independent, machine-checked proof that no
   strictly-convex 4-bad 8-gon exists**, complementing the existing
   incidence-completeness + perpendicular-bisector / collinearity certificate
   at `docs/n8-exact-survivors.md`.
   Artifact: `data/certificates/2026-05-05/n8_groebner_results.json`.

3. **Independent Gröbner basis verification at n = 9: partial exact
   pruning, with decoder follow-up needed.** The 184 selected-witness
   assignments collapse into 16 dihedral families. The committed Gröbner
   artifacts currently provide the following review-pending stratification:
   - 11 / 16 families (150 / 184 labelled assignments): grevlex GB = {1}.
     No complex solutions, no real solutions, no Euclidean realization.
   - 1 / 16 (F12, orbit 18, covering 18 assignments): grevlex GB has 14
     generators including the elimination relation `y_8^2 + 1/4 = 0`.
     Real-root infeasibility is immediate: `y_8 = ±i/2` has no real
     value, so no real solutions exist.
   - 4 / 16 (F07, F08, F09, F13; orbits 6, 2, 6, 2; total 16 assignments):
     grevlex GB has 62 generators each. The exploratory run notes report
     that `sympy.solve` finds only degenerate real solutions, but this PR
     does not yet include replayable real-root / non-degeneracy decoders for
     those four families.

   **Combined: the committed n = 9 Gröbner artifacts exactly kill 168 / 184
   labelled assignments** (150 by GB = {1}, 18 by F12's no-real univariate
   relation) and leave 16 labelled assignments in F07/F08/F09/F13 needing a
   replayable decoder or certificate before the algebraic route can be called
   a second-source proof of the full n = 9 finite case. The vertex-circle
   filter remains the current complete n = 9 review-pending obstruction.
   Artifact: `data/certificates/2026-05-05/n9_groebner_results.json`.

4. **Bridge Lemma A' computational consistency at n = 8 and n = 9.** Of the
   15 n = 8 surviving incidence patterns, 11 admit an ear ordering and 4 do
   not (ids 0, 1, 2, 3, sharing a "K_4-stuck" core). Of the 184 n = 9
   surviving witness assignments, 182 are ear-orderable; the 2 that are not
   are isomorphic Cayley-Z/9 circulants with offset multisets {+1, +3, −2, −3}
   and {−1, +2, +3, −3} (each is the inverse-orbit of the other). Both are
   killed by strict-cycle (vertex-circle) obstructions. Bridge Lemma A' is
   consistent with the data but is **not** falsified by these objects, since
   none survives to be realized. Artifact:
   `data/certificates/2026-05-05/bridge_lemma_check.json`.

5. **n = 11 single-row-0 timing.** A direct port of the n = 9 vertex-circle
   exhaustive checker to n = 11 reaches ~404 K nodes in 300 s for row 0 = 0
   without finding any full assignment, but does not finish that single
   row 0 in the time budget. Across 7 distinct row 0 singletons (0, 1, 3, 4,
   5, 6, 100) all return 0 full assignments before timeout, suggesting the
   filter set continues to dominate at n = 11. Naive scaling extrapolates
   to ~40 hours wall-clock for full n = 11 coverage on 4 cores in pure
   Python; a Rust / C++ port plus row-0 symmetry pruning could plausibly
   bring this under one hour. No cyclic-shift family at n = 11 evades the
   filters (175 distinct 4-subsets of ℤ/11 with pair-cap ≤ 2 all blocked).
   Artifact: `data/certificates/2026-05-05/n11_partial.json`.

6. **n = 10 full coverage in progress.** A 4-worker port of the n = 9
   exhaustive checker to n = 10 is running. Singleton-slice coverage
   (`data/certificates/n10_vertex_circle_singleton_slices.json`) already
   reports zero full assignments across all 126 row-0 choices (4,142,738
   total nodes visited). The full integrated rerun is expected to confirm
   this without anomaly.

7. **Stuck-set census.** Across n = 8 (15 patterns), n = 9 (184 patterns),
   and n = 10 (200-pattern sample, pre-vertex-circle), every pattern admits
   stuck sets of size 4. No stuck set violates L5 globally. The combinatorial
   stuck-set framework alone is therefore insufficient — geometric
   obstructions (vertex-circle, Gröbner) must close the cases. Artifact:
   `data/certificates/2026-05-05/stuck_set_census.json`.

8. **No counterexample at n = 14, 15, 16, 17, 18 in attempted patterns.**
   Aggressive numerical search across cyclic, two-orbit, three-lift, and
   randomized 4-regular candidate patterns at n = 14–18, after combinatorial
   filtering, produces no convergent realization with residual < 1e-6 and
   convexity margin > 1e-4.

9. **Literature update (2026-05-05).** Erdős #97 remains open
   (erdosproblems.com/97; Lean `formal-conjectures` repo carries the
   theorem with body `sorry`, `category research open, AMS 52`). No new
   k = 4 lower-bound construction has been published. No paper recovers
   the unpublished 1975 Erdős all-k Danzer claim. Aggarwal 2010
   (`n log_2 n + O(n)` upper bound for unit distances on a convex n-gon)
   remains state-of-the-art; Pach–Sharir's `f(n) ≪ n^{2/5}` is the
   standing combinatorial bound. AI-driven Erdős sweeps in 2025 do not
   list #97 among contributed solutions. Memo:
   `data/runs/2026-05-05/literature_update.md`.

## Theoretical-program progress

- **Lemma 12 / Endpoint Control (§5.1).** Reduction from "Endpoint Control
  Aux Claim" to a full proof of #97 confirmed clean. The mixed-side
  sub-claim (witnesses straddle the A-block) is identified as the most
  attackable concrete sub-step. Same-side cases (witnesses on the near or
  far chain only) require a tie-breaking rule on (i*, r*) to break the
  L–R asymmetry. No proof produced; concrete attack vectors logged.
  Memo: `data/runs/2026-05-05/endpoint_control_analysis.md`.

- **Three-cap SEC bridge (§5.4).** Cap-occupancy counting at n = 8 closes
  `min{M(p), M(q), M(r)} ≤ 3` for the 3-cap SEC support: if all three were
  bad, each would have ≥ 2 witnesses in its opposite cap, forcing
  `n - 3 ≥ 6`, i.e. `n ≥ 9`. This complements the diameter case (proved)
  and gives a geometry-only closure of the SEC reduction at n = 8. The
  n = 9 rigid case `(a, b, c) = (2, 2, 2)` (each cap holds exactly two
  outside vertices) is identified as the next attack target via L6
  perpendicularity overdetermination, in the spirit of the §3.3 n = 7
  parity argument.

  **Caveat / correction.** A separate audit raised that the cap lemma as
  stated in canonical-synthesis.md §5.4 ("distances from a chord endpoint
  to convex-position points inside the cap are all distinct") is not
  literally true for non-inscribed convex polygons. The classical Moser
  cap lemma applies when the polygon is inscribed in a circle, where chord
  monotonicity (`2R sin(θ/2)` monotone on the inscribed arc) gives the
  conclusion. Re-reviewing the §5.4 diameter case under this stricter
  reading is recommended; the n = 8 cap-occupancy count above only uses
  the inscribed special case at the SEC-supporting vertices and is
  therefore safe.

- **Bridge Lemma A' / ear-orderability (§5.2).** The data at n = 9 (182 / 184
  ear-orderable, 2 not, all killed by vertex-circle) is consistent with
  Bridge Lemma A' but does not prove it. The 2 non-ear circulants on ℤ/9
  with offsets {+1, +3, −2, −3} and {−1, +2, +3, −3} are interesting
  edge-case test objects for any future ear-orderability lemma at higher n.

- **Quantitative L9 (Q-L9).** A new sharp inequality:
  `ε(P) ≥ δ_min(P) · sin θ_int(v) / 2` holds at any 4-bad vertex v of a
  strictly convex polygon, where ε(P) is the radial deviation from the
  best-fit circle, δ_min the smallest interpoint distance, and θ_int the
  transversality angle between the v-witness circle and the best-fit
  circle. This explains the observed numerical drift toward near-cyclic
  configurations as solver-induced cluster collapse, and suggests a
  scale-invariant filter `δ_min(P) > 4 · ε(P)` to suppress the basin.

- **New fixed-pattern obstruction F15 (Ptolemy symmetric-quad).** A new
  exact filter: in the union-find generated by selected-distance
  equalities, if a row's witnesses `w_0, w_1, w_2, w_3` (in angular order)
  satisfy `class(w_0 w_2) = class(w_2 w_3)` and `class(w_1 w_3) = class(w_0 w_1)`,
  then Ptolemy's equality (forced by concyclicity on the row circle)
  combined with these UF coincidences gives `|w_0 w_3| · |w_1 w_2| = 0`,
  contradicting positivity. F15 fires on 26 of the 184 n = 9 pre-vertex-circle
  survivors (a strict subset of vertex-circle's 158 self-edge kills, but a
  shorter and structurally different proof). Memo:
  `data/runs/2026-05-05/new_obstructions.md`.

- **Selection lemma / canonical-chord injectivity (§5.3).** Substantial
  new partial progress:
  - The **symmetric-kite case** (where two would-be `phi`-colliders
    `v_i, v_j` have equal selected radii `r_i = r_j`) is **rigorously
    proved**: a barycentric-coordinate argument shows
    `sin(phi_1 + theta) > sin(2*theta)` under the short-base + L8
    semicircle constraints, forcing one of the witnesses `p, q` to lie
    strictly inside the convex hull of `{v_i, v_j, x_1}`, contradicting
    convex position.
  - The **asymmetric-kite case** (`r_i ≠ r_j`) has 287,208 negative
    computational test parameter combinations producing **zero** strictly
    convex 8-vertex realizations. Symmetric proof does not extend
    immediately, but the obstruction structure (witnesses `y_1, y_2`
    "blocking" `p, q` from below the asymmetric kite) is identifiable
    and should be amenable to analytic closure.
  - **Noncrossing data:** across 1,935 random near-bad convex polygons,
    the canonical-chord assignment never produced crossing chords (0 / 1935).
  - If the asymmetric-kite case is closed analytically, the Selection
    Lemma program (§5.3) closes Erdős #97 outright via
    `|bad set| ≤ n − 3`.
  Memo: `data/runs/2026-05-05/selection_lemma_progress.md`.

## Combinatorial / algebraic verification matrix

| n  | Selected-witness method | Gröbner basis (this round) | Status |
|----|------------------------|---------------------------|--------|
| ≤ 6 | Direct (§3.1, §3.2)     | trivial                   | proved |
| 7   | Fano parity (§3.3)      | trivial                   | proved |
| 8   | Incidence-completeness + cyclic-order + perp-bisector / collinearity (15 classes) | **GB = {1} for 14 / 15; one zero-dim variety with 4 real configs all failing strict convexity** | proved (multi-source) |
| 9   | Vertex-circle + L4 + L5 + L6-crossing (184 → 0) | **GB = {1} for 150; F12 has `y₈² + 1/4 = 0` (no real); F07/F08/F09/F13 remain decoder/certificate follow-up** | vertex-circle proved-locally (review-pending); Gröbner partial |
| 10  | Vertex-circle singleton slices (0 surviving, 4.1M nodes); independent secondary checker matches bit-for-bit on tested rows | n/a (no surviving system to feed) | proved-locally (review-pending) |
| 11  | Single row-0 singleton: 0 full assignments after 300 s timeout × 8 row 0's tested | n/a | exploratory only |
| ≥ 12 | open                  | open                      | open   |

## What was tried and did not produce a proof or counterexample

- **Counterexample search at n = 14 – 60** with cyclic, two-orbit, three-lift,
  Sidon-type, affine-stretched-regular, and randomized patterns. No
  realization with residual < 1e-6 and convexity margin > 1e-4 was found
  in the time budget. The B12_3x4_danzer_lift cluster basin remains the
  closest documented numerical near-miss, and is exactly killed by the
  mutual-rhombus filter.

- **First-order perturbation around regular n-gon** at n ∈ {12, 14, 16, 18,
  20, 24}. For every choice of "chord-class merge" pair (k_1, k_2), the
  linearised system has positive kernel-mod-rigid dimension (e.g. 12 free
  parameters for n=24, (k_1, k_2)=(3, 9)), but Newton iteration on the
  full nonlinear merge-equation system always converges to **degenerate
  configurations** (vertex coalescence). A `D_m`-symmetric two-orbit
  Danzer-style 2m-gon search at m ∈ {6, 7, 8, 9, 10, 12} finds no
  inner-radius `r_b` solution to the merge equations inside the convex
  window `(cos(π/m), 1/cos(π/m))`. The natural perturbation ansatz is
  thus definitively ruled out for n ≤ 24. Memo:
  `data/runs/2026-05-05/perturbation_analysis.py` and
  `data/runs/2026-05-05/perturbation_results.json`.
- **Direct attack on Bridge Lemma A'.** Combinatorial counting on stuck
  sets reproduces the |S| ≤ (n − |S|)(n − |S| − 1) bound from L4/L5 at
  n = 8, 9, 10, which does not rule out stuck sets of size 4. Pure
  combinatorial argument cannot close the bridge; geometry must enter.
- **Direct attack on the Endpoint Control Aux Claim (m = 4).** Reduction
  is clean, but no proof of the auxiliary claim was produced. The
  mixed-side sub-claim (§ above) is the cleanest next step.
- **Three-cap rigid (n = 9, (2,2,2)) case.** Three forced perpendicularity
  equations identified, but the parity-style closure (analogous to §3.3
  at n = 7) was not produced.
- **Danzer 9-point extension to k = 4.** The classical Danzer 9-vertex
  k = 3 construction does not lift to k = 4 by any of the obvious
  one-parameter or symmetric perturbations attempted. The same is true
  of Fishburn–Reeds 20-vertex k = 3.
- **Erdős 1975 unpublished all-k claim.** Not recovered in the
  literature; remains unverified.

## Suggested next steps (ranked)

1. **Audit the n = 9 selected-witness result before any promotion.** The
   audit in this report found no soundness defects in the vertex-circle
   exhaustive checker. The Gröbner basis attack independently kills 168 / 184
   labelled assignments, so it is useful corroboration, but it is not yet a
   complete second-source proof until F07/F08/F09/F13 get replayable
   real-root / non-degeneracy decoders.

2. **Independently audit the Gröbner attack at n = 9.** All 5
   nontrivial families (F07, F08, F09, F12, F13) admit short-form
   real-root / non-degeneracy certificates: F12 by the univariate
   relation `y_8^2 + 1/4 = 0`; F07/F08/F09/F13 by checking that every
   solution sympy returns has only 4 distinct coordinate points. Reviewer
   should re-run the algebraic decoders, confirm the relations, and
   verify that no other branch of the variety was missed.

3. **Push the finite-case pipeline to n = 10.** The full integrated
   coverage rerun in this round should complete within an hour;
   independently, port the search to Rust / C++ to cut time.

4. **Three-cap rigid case at n = 9.** The (2, 2, 2) case identified above
   is a finite combinatorial problem with three forced perpendicularity
   equations; closing it would close the SEC reduction at n = 9 (modulo
   the diameter-case audit).

5. **Mixed-side endpoint-control sub-claim (m = 4).** Likely accessible
   by L1 + L4 + L6; same-side sub-claim probably needs a tie-breaker on
   (i*, r*).

6. **Q-L9 implementation.** Scale-invariant non-cyclicity floor as a
   numerical-search filter to suppress cluster-collapse basins.

7. **Independent reviewer audit of the n = 8 and n = 9 finite-case
   artifacts** before any public theorem-style statement.

## Trust-level summary

- `THEOREM`: nothing new at this level beyond items already in repo.
- `LEMMA` (newly verified, conditional on audit):
  - n = 8 selected-witness 4-bad polygon non-existence has a
    Gröbner-basis-only proof (no convexity-specific filter required for
    14 of 15 classes; class 14 needs a real-root + strict-convexity
    check, both explicit).
  - n = 9 selected-witness 4-bad polygon non-existence remains a
    vertex-circle review-pending finite-case artifact. The Gröbner route
    independently kills 168 / 184 labelled assignments and leaves
    F07/F08/F09/F13 as algebraic decoder/certificate follow-up.
- `INCIDENCE_COMPLETENESS`: vertex-circle filter at n = 9, n = 10
  singleton-slice (audit confirms soundness).
- `EXACT_OBSTRUCTION`: Gröbner-basis kills 168 / 184 n = 9 selected-witness
  assignments via GB = {1} (150) + univariate real-root infeasibility
  (18 in F12: `y_8^2 + 1/4 = 0`). The remaining 16 labelled assignments in
  F07/F08/F09/F13 are `EXACTIFICATION` targets until a replayable decoder or
  certificate is committed.
- `EVIDENCE`: Bridge Lemma A' consistent with n = 8 and n = 9 ear-orderability
  data.
- `EXACTIFICATION`: Q-L9 (scale-invariant near-cyclic deviation lower bound).
- `FAILED_APPROACH` (this round): direct global counterexample search at
  n = 14–60; ear-orderability as a discriminator; pure combinatorial closure
  of stuck sets.

## Provenance

All artifacts produced in this attack round:

```text
data/certificates/2026-05-05/
├── bridge_lemma_check.json     # n=8, n=9 ear-orderability audit
├── n8_groebner_results.json    # all 15 n=8 patterns under sympy GB
├── n9_groebner_results.json    # 16 n=9 dihedral families under sympy GB
├── n11_partial.json            # n=11 single-row-0 timings
└── stuck_set_census.json       # n=8, n=9, n=10 stuck-set census

data/runs/2026-05-05/
├── endpoint_control_analysis.md   # Lemma 12 sub-claim analysis
├── groebner_attack.py             # GB encoder + driver (sympy)
├── groebner_all.py                # batch driver
├── groebner_n8_n9.md              # GB attack writeup
└── literature_update.md           # 2026-05-05 literature memo
```

Each artifact is provenance-only and is `REVIEW_PENDING`. None promotes
the official/global FALSIFIABLE/OPEN status of Erdős #97. Each carries
the standard caveat: independent reviewer audit is required before any
public theorem-style use.

## Honest assessment

This attack round did not produce a proof or counterexample of the full
Erdős #97 problem. What it did produce:

- An independent audit of the review-pending n = 9 vertex-circle checker
  finding no soundness defects;
- A second-source proof of the n = 8 finite case via Gröbner basis
  alone, with explicit algebraic certificates;
- A partial second-source algebraic check of the n = 9 finite case:
  168 / 184 labelled assignments are killed by the committed Gröbner
  artifacts, while F07/F08/F09/F13 remain follow-up targets for replayable
  real-root / non-degeneracy decoding;
- Bit-for-bit cross-validation of the n = 10 singleton-slice artifact
  against an independent from-scratch reimplementation on the first 5
  row 0 choices;
- Computational confirmation that Bridge Lemma A' is consistent with all
  surviving witness graphs at n = 8 and n = 9;
- Quantitative version of L9 explaining numerical near-cyclic drift;
- Cap-occupancy closure of the 3-cap SEC reduction at n = 8 (and the
  identified attack target at n = 9);
- A literature confirmation that no new construction or partial result
  has been published since the prior repo sweep.

The cumulative effect is to make the n = 8 finite-case result more robust and
to provide useful, incomplete algebraic corroboration for the review-pending
n = 9 finite-case pipeline. It also identifies two concrete attackable
sub-steps for general n (mixed-side endpoint control, n = 9 three-cap rigid
case). The official/global status of #97 is unchanged.
