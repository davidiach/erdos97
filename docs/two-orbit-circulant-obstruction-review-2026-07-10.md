# Review record: docs/two-orbit-circulant-obstruction.md (2026-07-10)

Status: written review record from an AI research session (Claude Code
multi-agent session, 2026-07-10). Review input for the maintainer's decision
intake only; not an external human review; does not by itself change any
claim status. No general proof and no counterexample are claimed for Erdos
Problem #97; the official/global status remains falsifiable/open.

Scope: the two-orbit circulant lemma draft
`docs/two-orbit-circulant-obstruction.md` (LEMMA draft, review pending),
whose Step 5 already carries the exact all-m SMT certificate
(`docs/two-orbit-window-all-m-smt.md`). This review covers the
review-pending prose Steps 0-4, replays the Step 5 machine layer, and
audits the named failure modes. The independently derived companion
`docs/symmetric-two-orbit-reduction.md` was used as a cross-check source.

Method: two passes inside one session - (a) a root-reviewer re-derivation
of Steps 0-4 (including direct recomputation of the two Step 4 turn
determinants via `Im(conj(u) v)`); (b) a dedicated referee agent with six
exact check scripts, including an exhaustive exact enumeration, for
`m = 3..9`, of all `C(2m-1, 4)` candidate witness 4-subsets at a
representative vertex (4,956 subsets), deciding for each whether it can be
equidistant from the vertex for any radius ratio `x > 0`.

## Per-step verdicts (reconciled)

- Step 0 (setup; WLOG `phi in [0, h]`): ACCEPTED. Reindexing shifts `phi`
  by `2h`; conjugation negates `phi`; both preserve 4-badness and strict
  convexity.
- Step 1 (offset forcing `phi in {0, h}`): ACCEPTED. Cross-orbit
  equidistance from `A_0` factors as
  `sin((l-k)h) * sin(phi + (k+l)h) = 0`, forcing `phi` to a multiple of
  `h` (mod `pi`); the same-orbit classes are pairs with strictly increasing
  radii plus at most the antipode; the 2+1 = 3 cap for interior `phi` was
  verified exactly for `m = 3..12` and on interior-`phi` grids. The step
  correctly uses no convexity (strictly convex interior-offset members of
  the family exist, e.g. `x = 1`).
- Step 2 (`phi = 0` impossible): ACCEPTED. The nearer of two same-ray
  points is a strict convex combination of the center `O` (interior, as
  center of the regular `A`-orbit) and the farther point, hence interior -
  contradicting strict convexity. Verified via exact half-plane
  computations for `m = 3..9`.
- Step 3 (row shape forced to same-orbit pair + cross-orbit pair; equation
  `E_A`): ACCEPTED, with one recommended clarification (C1 below). The
  exhaustive 4-subset enumeration for `m = 3..9` confirms: only
  pair+pair shapes are ever equidistant from `A_0` for any `x > 0`;
  asymmetric rows, rows with three or more same-orbit witnesses,
  antipode/pole compositions, two-cross-pair rows, and all-cross rows are
  impossible exactly as the note's micro-case parentheticals claim.
  Importantly, the reflection symmetry of the witness classes is derived
  from the distance formulas, not assumed, and only vertex `A_0`'s row is
  ever used - so no witness-choice equivariance across vertices is
  assumed anywhere.
- Step 4 (strict-convexity window `cos h < x < sec h`): ACCEPTED, with one
  REQUIRED one-sentence repair (R1 below). Both turn determinants
  (`2 sin h (x - cos h)` and `2 x sin h (1 - x cos h)`) were re-derived
  symbolically by both passes and verified; the hull order equals the
  alternating angular order on grids inside, outside, and near the window
  boundary for `m = 3..9`; the endpoint cases are exact collinearity
  degenerations.
- Step 5 reduction (monotonicity of `g` on the window; `T`-interval form):
  ACCEPTED. Step 5 conclusion (no window root for any `m >= 3`):
  ACCEPTED (machine-verified) - the z3 certificate replays exactly
  (all six decisions; artifact matches field for field), the embedding
  lemma (every integer instance lies in the polynomial relaxation) was
  re-derived and is sound, and the prose cosine ladder was re-checked
  independently for all `(a, p)` with `m <= 60`, finding the unique
  closed-boundary contact at `(m, a, p) = (3, 1, 1)` with root exactly
  `x = 2 = sec(pi/3)`, excluded by the open window. The finite screens
  reproduce the note's recorded numbers verbatim (`m <= 120`: 142,190
  pairs, one escalation, one boundary hit; `m <= 400` clear).

## Findings requiring action

- R1 (REQUIRED, Step 4, one sentence): the note asserts "All points are
  extreme iff the closed polygon in this angular order is strictly convex,
  iff both signed turn types are positive" without justifying that the
  boundary cyclic order is the angular order. The one-line repair: the
  common center `O` is interior to the configuration's hull (it is
  interior to the hull of the regular `A`-orbit already), and the cyclic
  order of hull vertices around any interior point is their angular order;
  with `phi = h` the `2m` angles `0, h, ..., (2m-1)h` are distinct, so the
  alternating angular order is the only candidate boundary order, and
  positivity of the two turn types is then equivalent to strict convexity.
  This is the only place in Steps 0-4 where a skeptical reader must
  currently supply an argument themselves.
- C1 (recommended, Step 3): the micro-case parenthetical eliminating
  degenerate compositions omits naming the two-same-orbit-pairs
  composition (two `A`-orbit pairs on one circle), which is impossible by
  Step 1's strictly increasing same-orbit radii; name it for completeness.

## Known-failure-mode audit

- Witness sets assumed symmetric under the vertex's reflection axis: NOT
  present (symmetry is derived; arbitrary per-vertex witness choices are
  handled by the exhaustive composition analysis).
- Aligned orbits excluded without proof: NOT present (Step 2 proves it).
- Second-orbit rows assumed to mirror first-orbit rows: NOT present (only
  the `A_0` row is used; the proof shows `A_0` itself cannot be 4-rich in
  the window, which suffices).
- Convexity-window boundary cases: handled (open window; the unique
  boundary contact `m = 3, x = sec(pi/3)` is excluded by strictness).
- Hidden common radius: NOT present (`E_A` involves only `A_0`'s own
  radius; no cross-vertex radius relation is ever used).

## Overall verdict

The two-orbit circulant obstruction note SURVIVES this review: no
mathematical gap was found in Steps 0-4, Step 5 is machine-certified and
its reduction re-derived, and the two action items are presentational
(R1 required, C1 recommended). Within its stated scope (vertex sets that
are unions of two concentric regular `m`-gons), the lemma's proof is, on
this review, complete once R1's sentence is added. This review does not
promote the note into the source-of-truth dashboard, and the note's own
"review pending" label remains until the maintainer decides.
