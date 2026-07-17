# Claim and artifact changelog

Status: reviewability aid only; not mathematical evidence.

This changelog records claim-scope changes, demotions, audit additions, and
reviewability fixes that affect how an external reader should interpret the
repository. It is intentionally not a full git history. No general proof and no
counterexample are claimed.

## 2026-07-17

- Corrected the slack-2 method-boundary records of the near-saturation
  support obstruction draft after an internal adversarial review: the
  earlier record claiming the turn count fails at `n = 8` was wrong (a
  strict form of the turn count closes every slack-2 distribution except
  two distinct unsaturated gap-2 diagonals, which always disconnect the
  side-equality chain). The lemma-draft statement, proof steps, and all
  sharpened counting consequences are unchanged; the artifact schema moved
  to `v2` and the stored artifact was regenerated. Also normalized the
  artifact's native trust field to the canonical
  `REVIEW_PENDING_DIAGNOSTIC` class (dropping the one-off
  `mismatch_overrides` entry), retitled the note's statement heading from
  "Theorem" to "Lemma draft", fixed a citation that conflated the nonagon
  profile-deficiency refinement with the localized per-label cap, added
  the missing `n <= 7` raw-budget step to the uniform-threshold corollary,
  added the verification-contract fields (known counterexample attempts,
  3-neighbor survival), moved the RESULTS.md entry into its own
  status-labeled subsection, queued the draft in
  `docs/review-priorities.md`, and registered the new checker line in the
  Makefile-chain and audit-order tests. No claim, scope, or status change
  beyond the corrected boundary record.

## 2026-07-16

- Added the review-pending near-saturation support obstruction draft
  (`docs/near-saturation-support-obstruction.md`,
  `scripts/check_near_saturation_support_obstruction.py`,
  `data/certificates/near_saturation_support_obstruction.json`): the
  edge-sensitive rich-support pair budget sharpens to
  `sum_i binom(|R_i|,2) <= n(n-2) - 2` for strictly convex `n`-gons with
  `n >= 8`, because pair-capacity slack `0` or `1` forces the
  equilateral/turn-cover contradiction for arbitrary support-size
  profiles. New counting floors: at least six exact-four centers in a
  hypothetical 4-bad decagon (previously five) and at least four in a
  hypothetical 4-bad hendecagon (previously three). Labeled
  `LEMMA_DRAFT` / `REVIEW_PENDING`; not a proof of `n=9`, `n=10`,
  `n=11`, or Erdos Problem #97, and no status change.

## 2026-07-10

- Migrated the three 2026-07-02 all-`m` certificate manifest entries
  (`two_orbit_window_all_m_smt`, `quarter_cell_mixed_cells_all_m_smt`,
  `quarter_cell_first_derivative_all_m_dominance`) to the provenance-v2
  registry format (`trust_class` instead of native `trust`); no claim,
  trust level, or artifact byte change.
- Moved the portable float replay comparison into a shared module
  (`src/erdos97/portable_compare.py`) and applied it to the quarter-cell
  closure screen artifact, whose `max_min_turn` diagnostic differs in the
  last ulps across libm implementations. Signs, booleans, counts, and
  claim-scope fields remain exact comparisons.
- Reclassified the three-orbit finite-`m` screen bucket counts
  (`screen_candidates`, `refuted`, `boundary_exclusions`) as
  platform-variant diagnostics: near the tangency boundary the float64
  pre-screen admits different candidate sets per platform, all of which the
  60-digit escalation then refutes or boundary-excludes. Replay comparison
  now checks the replay-stable fields (system enumeration counts,
  quarter-cell handoffs, unresolved/survivor lists, `clear`) exactly plus a
  per-side bucket accounting identity, instead of cross-platform equality
  of the bucket counts. The screen's evidence grade and claim scope are
  unchanged.
- Made release-packet source verification opportunistic: when the recorded
  source commit is absent from the clone (shallow CI checkout, or history
  rewritten by a squash-merge), the recorded snapshot digest is verified
  against the present sources instead of the missing commit. The tests
  workflow now checks out full history so PR CI takes the strict path, and
  the packet was rebuilt so the recorded source commit is one that exists
  in the pushed history (the previous pin referenced a commit that was
  never pushed).
- Committed the dependency-free `lake-manifest.json` the pinned
  `lean-action` CI step requires, and added the `lean/Erdos97.lean` library
  root importing every module, so the required Lean compilation job can
  build the whole pilot.
- Made the Lean pilot actually compile under the pinned dependency-free
  `v4.31.0` toolchain: the first CI compilation revealed the pilot had
  never been machine-checked (the pre-pin `verify-lean` silently skips
  when `lake` is absent). Renamed every `lemma` declaration keyword to
  `theorem` (core Lean 4 has no `lemma`; it is a Mathlib synonym) and
  repaired three proof bodies that relied on implicit-argument
  elaboration `lake build` rejects. No theorem or definition statement
  changed; sketch boundaries are unchanged.

## 2026-07-09

- Promoted `docs/n8-geometric-proof.md` from draft to `REPO_LOCAL_THEOREM`
  after two independent line-by-line derivations accepted the base-apex count,
  octagon equality saturation, equilateral chord formula, length-3 diagonal
  step, and `C_8` vertex-cover contradiction. The note now states explicitly
  that an apex cannot lie on its base line and that the two open boundary
  chains of a strict-convex diagonal lie in opposite open half-planes. The
  theorem excludes bad strictly convex polygons only for `n <= 8`; external
  publication review is still encouraged, `n >= 9` remains open, and the
  official/global status is unchanged.
- Reclassified the selected-witness `n <= 8` computation as independent
  machine-checked corroboration of the elementary theorem. Its artifact trust
  labels and review boundaries remain unchanged.
- Condensed the README's bootstrap/T12 review-pending narrative into a short
  route summary pointing to the working state, documentation index, focused
  bridge notes, and current next-lemma contract. The `n=9` material remains
  review-pending and the separate `n=10` continuation remains draft-only.
- Reconciled issue-navigation prose with GitHub state verified on 2026-07-09:
  issues `#5`, `#81`, `#82`, and `#83` were closed as completed on 2026-05-17,
  and the repository had no open GitHub issues at verification time. The issue
  crosswalk is now presented as a historical acceptance record.
- Documentation navigation cleanup only; no mathematical claim, trust label,
  or official/global status changed.

## 2026-07-02

- Added an all-`m` dominance closure of the nine first-derivative
  quarter-cell signed band cells
  (`docs/quarter-cell-first-derivative-all-m-dominance.md`,
  `scripts/check_quarter_cell_first_derivative_all_m_dominance.py`,
  `data/certificates/quarter_cell_first_derivative_all_m_dominance.json`,
  tests, managed manifest entry + registered audit command). Exact sympy
  corner identities `F_c(T,0,0) = +/-(sin T + cos T - 1)` (with
  `A = 2 sin(h)(cos h - sin h)` of order `sin h` against a band radius of
  order `sin^2 h`), exact vanishing-boundary identities, an
  outward-rounded interval Lipschitz bound (`<= 4`) over a box containing
  every band square, and z3-verified band/dominance inequalities give each
  derivative component its corner sign throughout the band square for
  every `m >= 8`, closing all nine cells by one-variable integration.
  Together with the mixed-derivative artifact below, all twelve signed
  band cells are closed for every `m >= 8`, so -- conditional on the
  review-pending A-row reduction and band-confinement prose -- every
  `m = 0 mod 4` quarter cell is exactly closed (`m = 4` by its own SMT
  artifact). The finite `m = 8, 12, 16` interval certificate is superseded
  as primary for all twelve cells and retained as an independent
  cross-check. Trust `EXACT_OBSTRUCTION` with disclosed sympy/interval/z3
  trust roots; non-quarter branches remain screen-grade (`m <= 16`) or
  open (`m > 16`), and there is no change to the strongest local result or
  the official/global status.

- Added an exact all-`m` closure of the three mixed-derivative quarter-cell
  signed band cells (`docs/quarter-cell-mixed-cells-all-m-smt.md`,
  `scripts/check_quarter_cell_mixed_cells_all_m_smt.py`,
  `data/certificates/quarter_cell_mixed_cells_all_m_smt.json`, tests,
  managed manifest entry + registered audit command). For cells `LL_y-_z+`,
  `LH_y+_z+`, and `HH_y+_z-`, sympy verifies the boundary identities
  `F(d,0) = F(0,e) = 0` exactly and z3 NRA proves the cleared
  mixed-derivative numerator cannot be nonnegative over a polynomial
  relaxation containing every `T = 2*pi/m in (0, pi/4]` and the full closed
  band square, so double integration gives a negative killer turn
  throughout each strict cell for every `m >= 8` -- upgrading those three
  cells from the finite `m = 8, 12, 16` interval certificate, which remains
  the only machine closure of the other nine cells and an independent
  finite-`m` cross-check of these three. The artifact also records the
  route boundary: the direct all-`m` killer-turn sign claim and the nine
  first-derivative cells returned `unknown` from z3 NRA within the tried
  budgets in this encoding (450-480 s and 120 s respectively), with a
  small-T dominance lemma named as the next target. Trust `EXACT_OBSTRUCTION` for the three
  named cells only, conditional on the review-pending A-row reduction and
  band-confinement prose; no change to the strongest local result or the
  official/global status.

## 2026-07-01

- Added an exact all-`m` SMT (z3 NRA) certificate for Step 5 of the
  review-pending two-orbit circulant obstruction
  (`docs/two-orbit-window-all-m-smt.md`,
  `scripts/check_two_orbit_window_all_m_smt.py`,
  `data/certificates/two_orbit_window_all_m_smt.json`, tests, managed
  manifest entry + registered audit command). A single polynomial relaxation
  in `(cos h, sin h, cos 2ah, sin 2ah, cos ph, sin ph)` contains every
  integer instance `(m, a, p)` and is UNSAT together with the open-window
  root condition, so the row equation `E_A` has no root in the
  strict-convexity window for every `m >= 3` at once; three further z3
  decisions pin upper-boundary contact uniquely to the known `m = 3`
  corner `x = sec(pi/3)`, a fourth shows exact lower-boundary contact is
  impossible in the relaxation, and a no-gap control shows the odd-offset
  gap constraint is load-bearing. This supersedes the finite `m <= 400` float64
  screen as the machine audit of Step 5 (the screen remains a per-`m`
  cross-check). Trust `EXACT_OBSTRUCTION` (SMT) for the Step 5 window
  exclusion only; the two-orbit lemma's Steps 1-4 remain review-pending
  prose, and there is no change to the strongest local result or the
  official/global status.

## 2026-06-13

- Added an independent SMT (z3 NRA) second source for the `n = 8`
  exact-survivor obstruction (`docs/n8-survivors-smt-cross-check.md`,
  `scripts/check_n8_survivors_smt.py`,
  `data/certificates/n8_survivors_smt.json`, tests, managed manifest entry +
  registered audit command). For each of the 15 reconstructed survivor
  classes, the equal-distance + perpendicular-bisector constraints together
  with order-free strict convex position (every vertex exposed in some
  direction -- no assumption that the canonical label order is the boundary
  order) are UNSAT, so no class has a strictly convex octagon realization in
  any order; 14 of the 15 are already UNSAT with no convexity assumption at
  all (order-independent), only class 14 needs the exposed-vertex constraint.
  This uses a different decision procedure than
  the existing artifacts (z3 NRA vs SymPy Groebner bases and the cyclic-order
  argument) and uniformly covers all 15 classes -- including the four
  Groebner-dependent classes (3, 4, 5, 14) the SymPy-free recheck deliberately
  skips. Trust `EXACT_OBSTRUCTION` (SMT), repo-local cross-check pending
  external review; strengthens but does not replace the existing `n = 8`
  artifacts; no status change.

- Closed the `m = 4` (three concentric squares, `n = 12`) quarter cell exactly,
  the smallest open sub-case left by the three-orbit finite-m closure screen.
  Branch-G 4-badness reduces to three explicit algebraic conditions on the
  radii and offsets, and an SMT (z3) certificate shows all 64 discrete
  sign/witness combinations are UNSAT inside the strict-convexity radius window
  (convexity inequalities are not even needed). Added
  `docs/three-square-m4-exact-closure.md`,
  `scripts/check_three_square_m4_closure.py`,
  `data/certificates/three_square_m4_closure.json` (managed manifest entry,
  registered audit command), trust `EXACT_OBSTRUCTION` (SMT). Restricted-family
  result: the m=4 half-step branches remain screen-grade, the `m = 8, 12, 16`
  quarter cells remain open, and the official/global status is unchanged.
- Reduced and partially settled the remaining `m = 8, 12, 16` quarter cells
  (`docs/quarter-cell-closure.md`, `scripts/check_quarter_cell_closure.py`,
  `data/certificates/quarter_cell_closure.json`). Two exact, `m`-uniform
  self-tested lemmas: the **A-row reduction** (a quarter cell closes iff `A_0`
  cannot be 4-bad, uniform in the C-row choice `a3`) and the **boundary-band
  confinement** of the offsets. A float grid for `m in {4,8,12,16}` shows every
  sampled witness configuration is strictly non-convex, but the locus is
  **tangent** to the convexity boundary (margin vanishes, grid-dependent), so
  for `m >= 8` this is evidence of closure, not a certificate -- those cells
  remain open. Recorded route limits: the exact-SMT route does not scale past
  `m = 4` (z3 NRA times out on the cubic turn determinants / witness
  disjunctions), and a float screen cannot certify closure due to the tangency.
  Trust: `LEMMA` (exact) for the reductions, `NUMERICAL_EVIDENCE` for the
  `m >= 8` non-convexity. No status change.

## 2026-06-12

- Added the three-orbit (t=3) paired-cosine reduction and finite-m closure
  screen (`docs/three-orbit-window-closure.md`,
  `scripts/check_three_orbit_window_closure.py`,
  `data/certificates/three_orbit_window_closure_m3_16.json`,
  `tests/test_three_orbit_window_closure.py`). All four offset branches are
  enumerated for `m = 3..16`; every screen candidate is refuted by 60-digit
  deterministic re-derivation or excluded as an exact boundary hit. The
  branch-G quarter cells (`m = 0 mod 4`, `a1 = a2 = m/4`, `s = m/2`) are
  exactly characterized as one-parameter degenerate families and recorded
  as named open sub-cases. Review-pending reduction plus screen evidence
  only: no all-`m` lemma, no exact certificate for screened cells, and no
  change to the official/global open status.

## 2026-06-09

- Added a review-pending lemma draft covering the full two-orbit circulant
  family: no strictly convex union of two concentric regular `m`-gons is
  4-bad, for any radii and any relative rotation
  (`docs/two-orbit-circulant-obstruction.md`, audit checker
  `scripts/check_two_orbit_dynamic_window_lemma.py`, with float64 screening
  plus high-precision escalation). This is a restricted family obstruction,
  not a change to the official/global open status. It was derived
  independently of the same-day restricted symmetric two-orbit reduction note
  (`docs/symmetric-two-orbit-reduction.md`); the two notes now
  cross-reference each other as mutual second-source provenance.
- Added the dynamic-witness free-pattern searcher
  (`src/erdos97/dynamic_witness_search.py`,
  `scripts/search_dynamic_witness.py`) and its first recorded equivariant
  sweep artifact (`data/runs/dynamic_witness_sweep_2026-06-09/`), recorded
  as `NUMERICAL_EVIDENCE` with no candidate found and explicit
  anti-degeneracy floors against the cluster exploit. A second deep pass at
  4x the restart budget (`data/runs/dynamic_witness_sweep_2026-06-09b/`)
  sharpened the same no-candidate outcome.
- Added the review-pending half-step matching reduction for multi-orbit
  cyclic configurations (`docs/half-step-matching-reduction.md`): no
  aligned orbit pairs, half-step pairs form a partial matching, and every
  `t = 3` branch is strictly overdetermined. Structural reduction
  bookkeeping only.

## 2026-05-10

- Added `docs/public-provenance.md` as the public replacement map for old
  private-archive footnotes. The cited mathematical and computational content
  now points to checked-in docs, scripts, data, or verification routes.
- Clarified the `n=8` exact-survivor status split: each reconstructed survivor
  class has an exact obstruction, while the aggregate `n=8` exclusion remains a
  repo-local `MACHINE_CHECKED_FINITE_CASE_ARTIFACT` pending independent review.
- Recorded this changelog so claim promotions and demotions are visible even
  when the public git history is not the most convenient audit surface.
- The default pytest tier was sped up in the public branch history; full
  artifact and exhaustive checks remain separate from `pytest -q`.

## 2026-05-08

- Added several review-pending `n=9` vertex-circle lemma packets and selected
  baseline D=3 bookkeeping artifacts. These are proof-mining and audit aids
  only; they do not promote the `n=9` finite-case status or alter the
  official/global problem status.

## 2026-05-06

- Added replayable real-root and non-degeneracy decoders for the remaining
  `n=9` Groebner families F07, F08, F09, and F13. These are recorded as
  review-pending algebraic corroboration only.

## 2026-05-05

- Added a second-source Groebner audit for the 15 `n=8` incidence-completeness
  survivors. It is strong corroborating evidence for the local `n <= 8`
  pipeline, but the public theorem-style status still requires independent
  review.
- Added partial `n=9` Groebner pruning results for selected families. These are
  review-pending and do not promote the `n=9` source-of-truth status.
- Recorded sparse-frontier diagnostics for C25/C29-style Sidon patterns. The
  C29 survivor order was later killed by a fixed-order Kalmanson/Farkas
  certificate; no all-order C29 claim is made.

## Prior Public Ledger Entries

- `B12_3x4_danzer_lift` was demoted from numerical near-miss to historical
  degeneration diagnostic once the fixed selected-witness pattern was exactly
  killed by mutual-rhombus midpoint equations.
- `C19_skew` was first killed for one fixed cyclic order by a compact
  Kalmanson/Farkas certificate, then later killed across all cyclic orders for
  that fixed abstract selected-witness pattern by the stored Z3 all-order
  certificate. This remains fixed-pattern work only, not a proof of Erdos #97.
- `C13_sidon_1_2_4_10` was first killed for one fixed cyclic order by a compact
  Kalmanson/Farkas certificate, then later killed across all cyclic orders for
  that fixed abstract selected-witness pattern by the exact order search. This
  remains fixed-pattern work only.
- The repo-local source-of-truth finite-case claim remains `n <= 8`. The
  `n=9` and `n=10` artifacts are audit targets until independent review
  justifies promotion.
