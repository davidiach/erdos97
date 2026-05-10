# Claim and artifact changelog

Status: reviewability aid only; not mathematical evidence.

This changelog records claim-scope changes, demotions, audit additions, and
reviewability fixes that affect how an external reader should interpret the
repository. It is intentionally not a full git history. No general proof and no
counterexample are claimed.

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
