# Erdos Problem #97 - multi-agent attack and review session (2026-07-10)

Status: no general proof and no counterexample are claimed for Erdos #97.
The official/global status remains falsifiable/open (repo metadata last
manually rechecked 2026-04-30). This document records one bounded
multi-agent session (Claude Code; one root session, five independent
research agents, root-level adversarial auditing of every claim) on top of
repository commit `ecf9ea3`. Every mathematical claim below is either
proved in a linked note, replayable by a linked checker, or explicitly
labeled a solver outcome / negative search result. Nothing here promotes
any review-pending artifact or changes any source-of-truth status.

## Headline results

1. The turn-inequality lemma - the declared review bottleneck of the n=9
   turn route - now has a complete written proof with exact verification:
   `docs/turn-inequality-lemma-proof-2026-07-10.md`. Equidistance forces an
   obtuse chord pair; a direction-lift cone bound shows interior turn sums
   of at most pi/2 would force nonnegative chord dot products. Both stored
   support sets match the emitter exactly; all 184 stored integer dual
   certificates re-verified independently (0 mismatches); 273,698 exact
   sampled instances, zero violations; the pi/2 constant is sharp. With
   this, the stored certificates validly exclude all 184 frontier
   assignments for strictly convex nonagons, conditional only on the
   separate upstream frontier-completeness review (A2-A7/B0). Review input
   only; no n=9 promotion.
2. A new k=4-essential arithmetic filter family with an exact machine
   result: `docs/squared-distance-value-rows-2026-07-10.md`,
   `scripts/check_block6_value_rows_closure.py`,
   `data/certificates/block6_value_rows_closure.json`. Five proved row
   families over squared distances (obtuse, diameter, short-chord
   pigeonhole, arc-packing, kite). The short-chord pigeonhole row
   (`min(D_ab, D_bc, D_cd) < R_i`, from three gaps summing below pi) alone
   closes, in exact z3 real arithmetic, all 16 vertex-circle-clean block-6
   reversed-shuffle escapes - a second, Kalmanson-free closure of the only
   known vertex-circle-clean family in that lane; obtuse+diameter close 15
   of 16; C29 fixed orders stay satisfiable (the rows complement, and do
   not dominate, Kalmanson/Altman). The k=3 analogue of the short-chord
   threshold provably degrades from R_i to 2 R_i, so the filter uses the
   number 4 essentially.
3. Priority 1 review delivered: `docs/n8-geometric-proof.md` survives two
   independent referee passes with zero mathematical gaps and one required
   one-sentence repair (exclude an apex on the base line), found
   independently by both passes: `docs/n8-geometric-proof-review-2026-07-10.md`.
4. The two-orbit circulant lemma draft survives a two-pass adversarial
   review (exhaustive exact enumeration of all 4,956 candidate witness
   4-subsets for m=3..9 confirms the row-shape forcing; Step 5 SMT
   certificate replayed exactly) with one required one-sentence Step 4
   repair (hull order equals angular order via O-interiority):
   `docs/two-orbit-circulant-obstruction-review-2026-07-10.md`.
5. Negative controls of independent interest, all exact:
   - Run-structure obstruction is void: an exact strictly convex 24-gon
     (near-equilateral macro-triangle, parabolic side bulges, rational
     coordinates) in which every vertex's squared-distance sequence has at
     least 4 monotone runs (9 vertices with 4, 15 with 6). Hence no purely
     run-combinatorial "budget" argument can decide #97; exactness of the
     4 hits is the entire content. Sharpens the ledger item "distance
     unimodality is false" and explains the B12 macro-triangle attractor.
   - Radius ping-pong gadget: an exact rational strictly convex 11-gon in
     which center O has an exact 4-witness row of squared radius 1 while
     its witness x has an exact 4-witness row of squared radius 900
     (ratio 30, scalable), refuting every local version of the
     radius-descent sublemma "a witness's selected radius is bounded by a
     constant times its center's".
   - Sharpened all-centers closest-pair barrier (proved): in a 4-bad
     polygon EVERY center satisfies
     `delta <= 2 r_i sin((pi - theta_i)/6) < r_i` (delta = global closest
     pair distance, theta_i = exterior turn); the k=3 constant is
     `2 sin(pi/4) = sqrt(2)`, again isolating where 4 enters.
6. Environment replay on a fresh container (python 3.11.15, sympy 1.14.0,
   z3 4.16.0, numpy 2.4.4, scipy 1.17.1): fast tier green; default pytest
   suite green before this session's additions (1494 passed / 688
   deselected, 10m11s) and green after them (1494 passed, 15m08s, after
   one registry-coverage fix caught by the repo's own consistency test);
   artifact tier registry replayed green through 229 of 237 commands at
   the time of writing (the remainder, the heaviest generated-product
   sweeps, was still executing; zero failures observed at every completed
   command).
7. Fresh abstract-pattern escape hunt (n = 10..13) under the repo's exact
   abstract filters, ended early by an account spend limit: one survivor,
   S12A - an n=12 parity two-orbit pattern (even centers offsets +-{1,2},
   odd centers +-{2,5}) at the natural order - independently re-verified
   at root level with the repo's own filter code: passes row caps,
   witness-pair capacity, two-overlap crossing, the vertex-circle
   quotient filter, BOTH full Kalmanson cone LP screens (770 distinct
   strict rows, no certificate exists over that family at this order;
   solver diagnostic), and all the new value-row layers. Its
   C6-symmetric realizations are exactly the configurations excluded by
   the two-orbit circulant lemma reviewed this session, so any
   hypothetical realization must be asymmetric. Recorded as an
   INCIDENCE_PATTERN frontier lead - explicitly NOT a counterexample -
   in `docs/s12a-parity-two-orbit-frontier.md` and
   `data/certificates/s12a_parity_two_orbit_frontier.json`, with next
   steps (independent order re-enumeration, stronger exact row search,
   fixed-pattern numerical probe) queued for the backlog. The hunt's
   negative side: structured circulant/no-reciprocal/projective families
   at n = 10..13 produced no other survivor before termination (session
   evidence, coverage logs in the session scratch area, not exhaustive).

   **Superseded 2026-07-12:** a later exact elementary certificate shows that
   the natural-order S12A rows force six consecutive equilateral ears whose
   exterior turns total `4*pi`. The pattern is therefore obstructed in this
   fixed order. The abstract-filter passes above remain historical provenance,
   not a live frontier or realizability evidence.

## Proof-mechanism ledger (blocked routes, with exact blocking points)

Recorded so future sessions do not repeat them; each was developed
independently this session and audited at root level.

- Global turning/winding budgets: BLOCKED. The only universal supplies are
  the O(1) total turning 2 pi and the (n-2) pi wedge total; the demand side
  of every charging scheme built from the per-center obtuse/wedge/turning
  rows has no forced lower bound growing with n (sandwiched roles can
  concentrate on vertices with vanishing exterior turn), and obtuse
  intervals at a witness always pairwise intersect, so no packing
  disjointness exists. The one k-sensitive constant found in this lane is
  the pi/3 versus pi/2 pigeonhole threshold, which prices chords against
  the radius scale, not against any O(1) angular budget (it powers
  headline result 2 instead).
- Extremal descent (min radius, closest pair, diameter, SEC): BLOCKED. The
  first step is sound and reproves the repo's min-radius filter; every
  local continuation sublemma is refuted exactly by the ping-pong gadget
  (headline 5); diameter/SEC variants bound gaps from the wrong side.
- Continuity/deformation: DEAD as formulated. No path-existence guarantee
  inside the 4-bad locus, and boundary degenerations shed witnesses toward
  k=3, where Danzer-type configurations exist; a compactness/limit lemma
  for the 4-bad locus is proved and recorded but gives no contradiction.
- Squared-distance value rows as a standalone general proof: BLOCKED at
  the uniform-certificate bridge (rows are uniform in n, but infeasibility
  is certified per assignment and order; C29 shows the row system is
  genuinely incomplete). VIABLE and adopted as a finite-pattern filter
  (headline 2).
- k=3 sanity discipline: every mechanism and row was checked against
  Danzer's 9-gon; every k=4 kill isolates its use of the number 4 (the
  pi/3 threshold, the 6n = n(n-2) saturation at n=8, the two-orbit window
  equation).

## Session discipline

- Trust labels per repo taxonomy; solver sat outcomes are recorded as
  controls only; unsat verdicts are sound kills because every added row is
  proved necessary (soundness is monotone under adding valid rows).
- All numerical work is exact (Fraction / sympy / z3 over reals); no
  float equalities anywhere in the recorded claims.
- No source-of-truth file was modified; all additions are new docs, one
  new checker script, one new managed artifact with manifest entry.
- The five research agents worked independently (no shared drafts) and
  their outputs were re-derived or re-run at root level before recording:
  both referee reviews were duplicated by an independent root pass; the
  turn-lemma proof was re-derived step by step; the value-row lemmas were
  re-proved and the z3 ablation re-run; the ping-pong gadget was re-run.

## Relation to the demanded deliverable

This session was tasked to resolve Erdos Problem #97 outright. It did not:
no general proof and no counterexample were found, and per the repository's
non-overclaiming contract (AGENTS.md) nothing weaker may be presented as a
resolution. The session's stance: the strongest new leverage recorded here
is the proved turn lemma (unblocking one n=9 route up to frontier review)
and the k=4-essential short-chord row (the first single-row Kalmanson-free
closure of the block-6 escape family); the general problem remains exactly
at the bridge gap the ledger already names - no uniform certificate over
all patterns, orders, and n is in sight, and both truth values remain
live. The dimension-count heuristic (deficit n+4 for k=4, constant 4 for
k=3) and every exact search to date point the same direction, but that is
weight of evidence, not proof.

## Artifacts added by this session

- docs/n8-geometric-proof-review-2026-07-10.md
- docs/two-orbit-circulant-obstruction-review-2026-07-10.md
- docs/turn-inequality-lemma-proof-2026-07-10.md
- docs/squared-distance-value-rows-2026-07-10.md
- scripts/check_block6_value_rows_closure.py (+ audit-registry entry)
- data/certificates/block6_value_rows_closure.json (+ manifest entry)
- docs/s12a-parity-two-orbit-frontier.md
- data/certificates/s12a_parity_two_orbit_frontier.json
  (+ scripts/check_s12a_frontier_pattern.py and managed manifest/registry
  entries, added when rebasing onto the provenance-v2 manifest)
- docs/erdos97-attack-2026-07-10.md (this report)

## Appendix: run-structure negative control (exact construction)

Corners (0,0), (1,0), (1/2, 87/100); 7 extra vertices per side at
parameters t/8 with outward parabolic bulge delta * t/8 * (1 - t/8),
delta = 1/40; n = 24. All 24 consecutive orientation determinants positive
(exact rationals); every vertex's squared-distance sequence to the other
23 vertices (cyclic order) has all nonzero consecutive differences and at
least 4 monotone runs: histogram {4: 9, 6: 15}. Replay (exact, stdlib
fractions only): [inline 40-line script recorded in the session log; the
construction is fully specified by the parameters above].
