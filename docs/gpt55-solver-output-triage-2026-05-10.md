# GPT-5.5/Opus solver-output triage, 2026-05-10

Status: `PROVENANCE` / task-selection note. No general proof and no
counterexample are claimed.

This note records the decision on twelve AI-generated outputs produced after
introducing `docs/gpt55-solver-brief.md`. The raw outputs are not mathematical
evidence. The useful material is grouped into a small action queue below.

## Decision summary

Do the vertex-circle local-lemma extraction first. It is the only cluster that
turns review-pending finite data into small reusable mathematics with a short
path to proof-facing documentation and compact verification.

Keep the class-14 audit proposals as a staged finite-artifact hardening task.
They are valuable for external trust in the `n=8` pipeline, but they are audit
infrastructure rather than a new bridge.

Keep the `n=9` proof-carrying certificate proposals as a larger future audit
project. They are well-scoped but require CNF/LRAT tooling and should benefit
from the smaller local lemmas first.

Preserve the fragile critical-radius idea as a bridge seed only after correcting
the geometry: the equal-radius two-overlap case gives a rhombus, not a
rectangle.

## Output clusters

| Outputs | Verdict | Action |
|---|---|---|
| 2, 3, 8, Opus1 | Best near-term math. These extract bounded vertex-circle self-edge and strict-cycle lemmas from the `n=9` template packets. | Promote to a local-lemma extraction task. Start with output 3's nested-spoke self-edge lemma, then output 2's shared-endpoint self-edge lemma, then output 8's T10/F12 strict-cycle lemma. Use Opus1's non-vacuity/redundancy audit as a guardrail, not as the first implementation scope. |
| 1, 4, 6(second), 9, 10 | Duplicate variants of the same `n=8` class `14` audit plan. | Merge into one staged class-14 RUR/interiority certificate task. Stage 1: branch/interiority replay. Stage 2: PB+ED equation replay. Stage 3: saturated RUR or ideal-containment completeness. |
| 6(first), 7 | Duplicate variants of an `n=9` proof-carrying finite certificate. | Keep as a major future audit task. Encode the non-vertex-circle filters as CNF, prove the 184 survivors complete with a checked proof, and replay self-edge/strict-cycle certificates with a DSU quotient. Defer until the smaller vertex-circle local lemmas are extracted. |
| Opus2 | Promising fragile-cover metric idea, but the stated rectangle dichotomy is geometrically wrong. | Salvage as a corrected fragile radius-midpoint lemma and diagnostic. Do not treat it as a contradiction or bridge theorem yet. |

## Near-term task

Create a proof-facing vertex-circle local-lemma packet with three small lemmas:

1. **Nested-spoke self-edge.** If `S_i = {a,b,c,d}` in angular order
   `a,b,c,d`, `{b,d} subset S_a`, and `{a,c} subset S_b`, then row `i` gives
   `D_ad > D_bc`, while rows `a,b` force `D_ad = D_bc`.
2. **Shared-endpoint nested self-edge.** If `a,b,d in S_c`, `b` lies strictly
   between `a` and `d` in angular order around `c`, `{c,a} subset S_d`, and
   `{c,b} subset S_a`, then row `c` gives `D_ad > D_ab`, while rows `d,a`
   force `D_ad = D_ab`.
3. **T10/F12 strict cycle.** The local core
   `0->{1,2,5,6}`, `3->{0,1,4,6}`, `6->{1,3,4,7}`,
   `8->{0,3,6,7}`, with angular orders `0,3,6,7` at center `8` and
   `4,6,0,1` at center `3`, gives
   `D_06 > D_16 > D_01 = D_06`.

Expected deliverables:

- a proof-facing note with exact hypotheses and proofs;
- a compact checker that scans the existing `n=9` template packet data and
  reports which families instantiate each lemma;
- a non-vacuity/redundancy diagnostic saying whether the instantiated template
  is already killed by simpler cap/crossing constraints;
- status kept as `REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE`.

This task does not prove `n=9`, does not promote the review-pending checker,
and does not prove Erdos Problem #97.

## Class-14 audit task

Merge the repeated class-14 outputs into one staged task:

```text
CB-N8-CLASS14-RUR - Standalone class-14 branch/interiority audit
```

Stage 1 should verify only the listed real branches and their strict-interior
certificates:

- input the eliminant `16*t^4 - 56*t^2 + 1`;
- isolate its four real roots by Sturm checks;
- consume coordinate expressions for the four branches;
- verify denominator nonvanishing;
- verify barycentric or quadrilateral-hull interior certificates on every
  branch by exact sign checks.

Stage 2 should replay the class-14 `PB+ED` equations under the same
parametrization by exact reduction modulo the eliminant.

Stage 3 should add completeness: a saturated RUR, ideal-containment traces, or
another exact proof that no strict-candidate branch is hidden.

This task strengthens trust in the existing `n=8` finite artifact. It is not a
new general proof route.

## n=9 certificate audit task

Merge the two proof-carrying `n=9` finite-certificate outputs into one future
task:

```text
CB-N9-VC-PCERT - Proof-carrying n=9 vertex-circle audit certificate
```

The intended certificate has two layers:

- **Coverage:** encode exactly-one row choices plus the non-vertex-circle
  filters as a CNF, block the 184 listed survivor assignments, and verify UNSAT
  with an independent proof checker.
- **Local contradiction replay:** for each survivor, rebuild the
  selected-distance quotient with union-find and verify either a self-edge or a
  strict directed cycle from vertex-circle interval containment.

This is high audit value but likely larger than the local-lemma task because it
requires CNF/proof tooling and careful clause-specification review.

## Fragile-radius bridge seed

Corrected salvage of Opus2:

If fragile centers `y,z` share exactly witnesses `{u,v}` and `m` is the
midpoint of `uv`, then

```text
r_y^2 - r_z^2 = |y-m|^2 - |z-m|^2.
```

Thus `r_y = r_z` iff `m` is also the midpoint of `yz`. In that equal-radius
case, `uv` and `yz` are mutual perpendicular bisectors, so the four labels form
a rhombus with the opposite pairs `{u,v}` and `{y,z}` alternating around the
convex hull. They do not generally form a rectangle.

Suggested task:

```text
CB-FRAGILE-RADIUS-MIDPOINT - Add fragile critical-radius two-overlap diagnostic
```

This should report equal-radius rhombus branches and unequal-radius ordering
branches on the block-6 and two-block controls. It should not claim to kill
the block-6 family unless the branch diagnostic actually proves no branch
survives.

## Priority order

1. `CB-N9-VC-LOCAL-LEMMAS`: smallest proof-facing payoff and best bridge-mining
   value.
2. `CB-N8-CLASS14-RUR`: valuable audit hardening for the delicate `n=8`
   survivor.
3. `CB-N9-VC-PCERT`: larger finite-certificate audit after local lemmas reduce
   the obstruction vocabulary.
4. `CB-FRAGILE-RADIUS-MIDPOINT`: promising bridge seed, but requires corrected
   geometry and negative-control testing before promotion.
