# GPT Pro follow-up triage, 2026-05-11

Status: provenance and task-selection guidance only; not mathematical evidence.

This note triages ten additional GPT Pro outputs supplied in chat. It does not
promote any claim, alter the source-of-truth status, or replace the checked
finite-case and exact-obstruction artifacts. The repository still claims no
general proof and no counterexample for Erdos Problem #97.

## Decision

Do not update `README.md`, `STATE.md`, `RESULTS.md`, or
`metadata/erdos97.yaml` from this batch. The useful parts are either already in
the repo or should remain as negative-control/provenance leads until converted
into small checked artifacts.

Highest-value salvage:

- a standalone parabola model-case write-up, if promoted from the existing
  synthesis artifact;
- the exact nonconvex eight-point all-bad model as a possible convexity-check
  negative control;
- the reminder that diameter-endpoint shortcuts are unsafe.

## Outputs 1 and 2: small-case incidence obstruction

Triage: already covered, with stronger repo-local machinery.

The side-pair/diagonal-pair capacity proof in Output 1 is the same geometric
base-apex count recorded in `docs/n8-geometric-proof.md`, and its selected-row
version is the sharpened incidence count in `docs/claims.md`. The conclusion
`n >= 8` and the saturated `n=8` constraints are already source-tracked.

Output 2's Fano/perpendicularity proof for `n=7` matches the proof-facing
summary in `docs/claims.md` and the reproducible enumeration in
`docs/n7-fano-enumeration.md`. Its lower bound on the number of row-pairs with
two common witnesses is a useful sanity check, but it is not a new source claim.

Recommended current action: no source-of-truth update.

## Outputs 3 and 4: parabola model case and failed shortcuts

Triage: the parabola proof is valid as a model-case theorem; keep it separate
from the global problem.

The proof for points on the standard parabola

```text
p(t) = (t, t^2)
```

is the same argument already recorded in
`data/llm_runs/ten_prompt_review_2026-04-29/corrected_synthesis.md`: if four
parameters `u_1,...,u_4` are at the same distance from `p(t)`, Vieta's formulas
for

```text
(u-t)^2 * (1 + (u+t)^2) = R
```

give

```text
u_1 + u_2 + u_3 + u_4 = 0
u_1^2 + u_2^2 + u_3^2 + u_4^2 = 4*t^2 - 2.
```

Choosing a point with minimal `|t|` gives a contradiction. This is a clean
subcase obstruction and is worth a standalone proof note if it is promoted into
the proof-facing docs. It is not evidence of a general theorem beyond that
subcase.

The alternating-radius octagon/regular two-orbit discussion is already
subsumed by `docs/two-orbit-radius-propagation.md`, which records the exact
convexity obstruction for the relevant ansatz and a broader alternating
two-radius regular-family check.

The diameter-endpoint shortcut should remain rejected. A diameter endpoint can
still have four other vertices at the same smaller distance, so proof routes
that try to choose a diameter endpoint and bound all smaller distance layers by
three need an additional argument.

Recommended current action: if this branch is revived, add
`docs/parabola-model-case.md` as a compact standalone proof and link it from
the proof-facing index. Do not promote it to a global result.

## Output 5: exact nonconvex eight-point all-bad model

Triage: useful negative control; not a counterexample.

The pasted coordinates with `a = 2 - sqrt(3)` were sanity-checked locally with
exact SymPy arithmetic. For the supplied rows, every selected squared radius is
exactly equal; rows alternate between squared radii `2 - sqrt(3)` and `1`.
The convex hull of the eight points has labels `[5, 3, 1, 7]`, so only four of
the eight points are hull vertices.

This is therefore an exact all-bad point set outside strict convex position. It
is a good trap for weak convexity checks, especially checks that only inspect a
claimed cyclic label order and miss self-intersection or interior points. It is
not a counterexample to Erdos Problem #97.

Recommended current action: optionally add a small JSON artifact and verifier
later, for example `data/certificates/nonconvex_all_bad_octagon_control.json`
plus a script that checks exact row distances and hull size. This is lower
priority than the current `n=9` local-lemma and finite-artifact audit tasks.

## Existing exact nonconvex ten-point control

Output 2's pentagon-plus-inner-pentagon near miss is already represented by
`golden_decagon_example()` in `src/erdos97/affine_circuit_certificates.py` and
checked by:

```bash
python scripts/check_affine_circuit_certificates.py --example golden-decagon --assert-expected --json
```

This remains a negative control showing that the equal-distance equations are
not inherently contradictory once strict convexity is dropped.

## Output 6: compact n=8 saturation proof

Triage: already covered by the octagon proof-note draft.

The follow-up proof excluding bad convex octagons is essentially the same route
as `docs/n8-geometric-proof.md`: the base-apex capacity count saturates at
`n=8`; length-2 diagonals force all side lengths equal; length-3 diagonals
force the set of exterior turns equal to `2*pi/3` to hit every adjacent pair in
the 8-cycle; at least four such turns contradict total exterior turn `2*pi`.

This is a useful reviewer-facing phrasing because it keeps the slack at `n=9`
visible: the same capacity bound is `63`, while the forced lower count is only
`54`. That explains exactly where the saturation argument stops.

Recommended current action: no new source-of-truth update. If the octagon
proof note is revised for external review, consider borrowing this output's
explicit `m(a,b)` notation and final `n=9` slack calculation as explanatory
text. Keep the note's current status as a proof-note draft pending independent
review.

## Output 7: alternate n=8 middle-target enumeration

Triage: partly known, partly unverified. Do not promote.

The initial incidence ingredients are already source-tracked:

- the two-circle cap `|S_i cap S_j| <= 2`;
- the target-pair cap that a pair `{a,b}` can occur in at most two selected
  rows;
- the `n=8` witness indegree regularity proof `d_x = 4`, recorded in
  `docs/claims.md` and `docs/n8-incidence-enumeration.md`.

The new proposed ingredient is a middle-target rule: if `j in S_i` and
`|S_i cap S_j| = 2`, then `j` must be one of the two middle targets of `S_i`
in angular order around `p_i`. The geometric intuition is plausible: the line
`p_i p_j` is the perpendicular bisector of a chord of the selected circle
centered at `p_i`, so its direction is an angle-bisector direction for that
chord. But to be usable in this repo it needs a precise lemma covering:

- the boundary-order-to-angular-order hypothesis at a hull vertex;
- the exclusion of the opposite angle-bisector ray;
- the case where the two common witnesses are not adjacent among the four
  selected targets;
- why an extreme selected target cannot be such a bisector point.

The output then says an exact enumeration leaves nine labelled incidence
patterns, three fail by a wrong-midpoint-direction condition, and the remaining
six force a single distance class containing a `K_{2,3}`. This is not currently
a checked repo artifact, and the count does not match the existing
`n=8` incidence pipeline, which leaves 15 canonical survivor classes before
exact geometric obstruction. The proposed enumeration may simply be using a
stronger middle-target filter, but that filter and the nine-pattern count would
need a replayable script or JSON certificate before they can be cited.

The final `K_{2,3}` obstruction is valid only with its exact equality scope
made explicit: two centers sharing the same three targets at one common radius
would force three intersections of two distinct equal-radius circles. A checker
would need to verify that the selected-distance quotient really puts all six
edges of the alleged `K_{2,3}` into one distance class, not just into two
separate row-radius classes.

Recommended current action: preserve this as an alternate n=8 proof route to
benchmark against the existing 15-class checker. A useful follow-up artifact
would be a small script that implements the middle-target rule, emits the nine
patterns, and verifies the wrong-bisector or single-distance-`K_{2,3}` kill for
each pattern. Until then, keep `docs/n8-geometric-proof.md`,
`docs/n8-incidence-enumeration.md`, and `docs/n8-exact-survivors.md` as the
source-tracked n=8 routes.

## Output 8: two-pattern n=8 collapse and explicit n=9 slack pattern

Triage: useful cross-reference, but still not a source-of-truth update.

The `n <= 8` conclusion is already covered by the repository's existing
routes. The proof's first three lemmas match the current incidence/crossing
toolkit. Its n=8 counting phase is a good compact derivation of the saturated
octagon structure:

- all nonadjacent row-pairs have two common witnesses;
- all adjacent row-pairs have exactly one common witness;
- all target indegrees are four;
- the length-2 source chord condition forces adjacent labels into each row.

The output then says the remaining n=8 crossing possibilities reduce to the
two cyclic patterns

```text
S_i = {i-1,i+1,i+2,i+5}
S_i = {i-1,i+1,i+3,i+6}
```

and each pattern forces every consecutive triple to be equilateral. This would
be a nice short proof if the finite reduction to exactly those two patterns is
replayed by a checker. It should not replace the current
`docs/n8-geometric-proof.md` argument or the 15-class incidence/exact pipeline
until that tiny enumeration is made reproducible.

The explicit n=9 pattern displayed at the end is already tracked in
`docs/n9-incidence-frontier.md` as the row-Ptolemy frontier pattern:

```text
S0 = {1,2,3,8}
S1 = {0,3,4,7}
S2 = {1,3,5,6}
S3 = {2,4,5,8}
S4 = {0,3,6,8}
S5 = {2,4,6,7}
S6 = {1,5,7,8}
S7 = {0,1,4,6}
S8 = {0,2,5,7}
```

It does satisfy the early pair/crossing/count filters in the natural cyclic
order and has balanced indegrees. In the fixed natural order, the repo classifies
it by six exact row-Ptolemy product-cancellation certificates. That obstruction
is order-sensitive: `tests/test_n9_incidence_frontier.py` records a scrambled
order where the row-Ptolemy certificates disappear. Separately, the
review-pending exhaustive n=9 vertex-circle checker kills all 184 complete
patterns surviving the pair/crossing/count filters, including this kind of
slack-frontier behavior, but that n=9 artifact remains review-pending.

Recommended current action: no metadata/status update. If this branch is
continued, the best artifact would be a script that proves the n=8 two-pattern
reduction from the saturated row constraints. For n=9, use the displayed
pattern as a benchmark already connected to row-Ptolemy and vertex-circle
review artifacts, not as a new live candidate.

## Output 9: candidate n=9 turn-inequality LP obstruction

Triage: promising review-pending route; not a source-of-truth update.

The side-aware pair-cap sharpening gives a compact n=9 indegree argument: if a
vertex `x` appears in `r_x` selected rows, then the `3*r_x` witness-pair
occurrences involving `x` have capacity

```text
2 side-neighbor pairs * 1 + 6 diagonal pairs * 2 = 14,
```

so `r_x <= 4`. Since total selected appearances are `36`, every `r_x` must be
4. This is stronger than the generic n=9 checker bound `r_x <= 5`, although an
ad hoc replay over the existing 184 pair/crossing/count frontier assignments
also found all 184 to be 4-regular.

The proposed turn lemma is also plausible and useful: if a row centered at `i`
contains selected offsets `a < b`, then equal distances from `i` force the
edge-direction turn along the arc from `i` to `i+b` to exceed `pi/2`, and the
reverse complementary arc to exceed `pi/2`. In normalized variables
`t_i = 2*tau_i/pi`, the weak constraints are:

```text
sum_i t_i = 4,   t_i >= 0,
sum_{h=1}^{b-1} t_{i+h} >= 1,
sum_{h=a+1}^{8} t_{i+h} >= 1.
```

I ran an ad hoc exact-rational Z3 replay over the 184 complete n=9 assignments
that survive the existing pair/crossing/count filters in
`GenericVertexSearch(use_vertex_circle=False)`. All 184 were `unsat` under
these weak turn constraints. A SciPy `linprog` replay gave the same result.

This is not yet a claim-bearing artifact. Before this can change the local
finite-case status, the repo needs:

- a proof-facing write-up of the turn lemma, including the reverse-arc
  inequality and indexing conventions;
- a small checker that treats the 184 frontier assignments, or a regenerated
  equivalent frontier, as input;
- exact infeasibility certificates or a trusted replay route for the rational
  linear systems;
- documentation that keeps this as a candidate n=9 finite-case extension,
  still independent-review pending and not a general proof.

Recommended current action: turn this into a Codex backlog task or a compact
checker artifact. It may be a cleaner second route to the review-pending n=9
finite case than the vertex-circle exhaustive checker, but it should not update
`README.md`, `STATE.md`, `RESULTS.md`, or `metadata/erdos97.yaml` until it is
implemented and reviewed.

## Output 10: side-sensitive n<=8 proof and new side-cap n=9 pattern

Triage: the n<=8 proof is already covered; the n=9 pattern is a useful
frontier example.

The side-sensitive perpendicular-bisector count and the saturated octagon
argument duplicate the proof-note route in `docs/n8-geometric-proof.md` and
Output 6 above. The displayed angle-sum contradiction is the same obstruction
phrased with interior angles rather than exterior turns: at least four
interior angles would be `60` degrees, while the other four are strictly below
`180` degrees, giving total angle sum below `960` degrees instead of the
required `1080` degrees.

The new n=9 incidence pattern is different from the row-Ptolemy frontier
pattern in Output 8:

```text
S0 = {1,2,4,6}
S1 = {0,2,3,5}
S2 = {1,3,4,8}
S3 = {0,2,4,7}
S4 = {2,5,6,8}
S5 = {1,3,6,7}
S6 = {4,5,7,8}
S7 = {0,3,6,8}
S8 = {0,1,5,7}
```

Ad hoc checks showed:

- balanced selected indegrees `[4,4,4,4,4,4,4,4,4]`;
- no row-pair cap, adjacent two-overlap, crossing-bisector, column-pair cap,
  phi4, or natural-order row-Ptolemy obstruction under
  `classify_pattern`;
- no side-sensitive pair-cap violation;
- `GenericVertexSearch.vertex_circle_status` reports `self_edge`;
- in the existing full n=9 pair/crossing/count frontier enumeration order, it
  is assignment 4;
- the candidate weak turn-inequality Z3 system from Output 9 is `unsat`.

So this is a good witness that the side-sensitive capacity obstruction really
does have slack at n=9. It is not a geometric candidate after the stronger
review-pending filters are applied.

Recommended current action: keep this pattern as a regression/benchmark if the
turn-inequality LP checker is promoted into a real artifact. It is a compact
example that passes the first incidence/crossing layer but is killed by both
vertex-circle self-edge and the candidate turn LP.

## Prompting guidance

Further GPT Pro prompts are most useful if they ask for machine-checkable
objects:

1. exact coordinates plus selected rows for negative controls;
2. a verifier snippet or JSON artifact schema;
3. an explicit diff against `docs/claims.md`, `RESULTS.md`, and existing
   failed-route docs;
4. a trust label for every claim.

Avoid prompts that ask for a narrative proof first. In this repo, the useful
unit of progress is a small exact lemma, a replayable certificate, or a
well-labelled failed route.
