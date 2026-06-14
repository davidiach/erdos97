# Adversarial Verifier — Erdős #97 exploration (2026-06-14)

Read-only re-runs. No source modified, no commit, no proof/counterexample claimed.

## Reproduction table

| lane | command | reproduced? | key numbers |
|---|---|---|---|
| A6 | `a6_topological_parity.py` | yes | n7 54/54 killed; n8 15→0 (15 survive both); n9 184→0 (22 parity + 162 parallel). repo cross-check: 22/162/0/184 |
| B2 | `b2_scalable_incidence_search.py --n 9 --symmetry none` | yes | row0=70, nodes=22,591, self_edge=3,048, strict_cycle=16,003, survivors=0 |
| B2 | VC-off REPL (row_strict[k]=[]) | yes | survivors=184, digest=dc28b32d…f213d55 (exact match) |
| A2 | `a2_sos_exact_certify.py --classify` | yes | 13 equality_empty (gb_len=1, 1∈ideal) + class14 convexity_only (gb_len=15) |
| A2 | `… --certify 5 --mult-deg 1 --json` | yes | certificate_found=True, exact_identity_verified=True, 64 eqs, 14 mult, max_deg=1 |
| A1 | `a1_dimension_elimination.py` | yes | F01 GB=1 empty; F07 GB=62 finite zero-dim, 20 real pts, 0 strictly convex; turn-packing Farkas λ=1 (5>4); P24 12 neg turns → premise false |

## A6 soundness verdict: SOUND. "All 184" reproduced (22 + 162).

- Edges are emitted by `perpendicularity_edges` / repo `phi_map` ONLY when
  `|S_i ∩ S_j| == 2` exactly — precisely L6 (both centers on the perp-bisector
  of the witness chord ⟹ ij ⊥ uv). No perpendicularity is asserted that L6
  does not force.
- `parallel_endpoint_violation` buckets chords only by (connected component,
  2-coloring parity); equal parity = even number of +π/2 turns = genuinely
  equal slope. Shared endpoint ⟹ 3 collinear ⟹ L2 violation. No over-assertion.
- Standalone build matches the repo's own `forced_perpendicular_graph` /
  `odd_forced_perpendicular_cycle` (cross-check 22/162/0/184).
- Provenance gap confirmed independently: `n9_incidence_frontier.py` imports
  `odd_forced_perpendicular_cycle` (catches the 22) but has NO parallel-endpoint
  filter; `incidence_filters.py` lacks it; only `n8_incidence.py` carries it
  ("no same-color forced-parallel chords sharing an endpoint"). So 162/184 were
  never tested combinatorially before vertex-circle. Genuine simplification.
- Necessary-only: leaves all 15 n=8 survivors alive (report states this; ceiling
  is honest).

## Issues found: none material.

- No report claims a proof of #97, a counterexample, or promotes n=9/n=10
  beyond REVIEW_PENDING/draft.
- No cross-lane contradiction: B1 (0 SAT, 30/184 UNSAT, rest unknown) is
  consistent with A6 (all 184 killed) and B2 (0 survivors).
- Trust labels (A1 EXACT_OBSTRUCTION_PER_FIXED_PATTERN+HEURISTIC, A2 EXACT,
  B1/B2 MACHINE_CHECKED…REVIEW_PENDING, C2 EXACT+NUMERICAL, E1
  LITERATURE_BACKED/UNVERIFIED) are honest and scoped.

## Ranked shortlist

1. A6 — parity+parallel kills all 184 combinatorially. Weakest assumption: it is
   necessary-only (cannot touch n=8 survivors), so it is a route *consolidation*,
   not a new theorem. Next: lift `parallel_endpoint_violation` into
   `incidence_filters.py` + add to `n9_incidence_frontier` prefilters; confirm
   the live n=9 search closes without the vertex-circle stage.
2. A2 — exact rational degree-1 Nullstellensatz on 13/14 n=8 classes. Weakest:
   class 14 needs convexity (not equality-empty); degree-1 may not generalize.
   Next: certify class 14 with a degree-≥2 Positivstellensatz including turn ineqs.
3. A1 — turn-packing Farkas + P24 separation isolates the convexity injection.
   Weakest: per-fixed-pattern only; the Bridge Lemma (every counterexample
   reduces to such a pattern) is open. Next: attempt the bridge for one n=8 class.
4. B2 — independent oracle reproduces 70/184/digest/0. Weakest: pure-Python
   per-node cost stalls n=10 (0/66 slices). Next: CP-SAT/bitset port to close n=10.
5. B1 — second-source z3 gives 0 SAT but only 30/184 decisive UNSAT. Weakest:
   QF_NRA non-decisive (154 unknown). Next: exact-certify the 154 via A2's path.

## One-liner per remaining lane

- A3 ear-orderability: keep. A4 endpoint-diameter: keep. A5 antipodal-cut
  (0 new kills, l=2==Kalmanson): negative-control — archive. A7 inversion/Möbius:
  keep. C1 new-ansatz (no candidate, #7 mode): negative-control. C2 k3→k4: keep.
  D1 Lean: keep. E1 literature-transfer: keep (snippet-sourced, flagged).
