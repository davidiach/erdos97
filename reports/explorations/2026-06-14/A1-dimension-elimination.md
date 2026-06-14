# A1 — Real-algebraic dimension / elimination emptiness argument

Trust label: `EXACT_OBSTRUCTION_PER_FIXED_PATTERN` (the Groebner emptiness /
zero-dimensionality and the Farkas turn-packing certificates) + `HEURISTIC`
(the dimension count) + `SHARP_REASONED_GAP` (the statement of the smallest
decisive obstruction).

Scope guardrail: this note does **not** prove Erdos Problem #97, does **not**
claim a counterexample, and does **not** promote any source-of-truth status.
The official/global status of #97 (erdosproblems.com/97) remains FALSIFIABLE /
OPEN. Every algebraic fact below is computed in exact arithmetic
(`sympy` over `QQ` / `Q(sqrt3)`); nothing is a floating-point near-equality.

Reproduction:

```bash
python scripts/exploration/a1_dimension_elimination.py          # ~19 s wall
python scripts/exploration/a1_dimension_elimination.py --json   # machine view
python scripts/exploration/a1_dimension_elimination.py --fast   # skip lex GB
ruff check scripts/exploration/a1_dimension_elimination.py
```

Inputs (treated as data, not truth):
`data/certificates/2026-05-05/n9_groebner_results.json` (the 16 dihedral
representatives of the n=9 selected-witness frontier);
`scripts/verify_p24_metric_linear_nonconvex.py` (the P24 non-convex control);
the proven turn-inequality lemma emitter in
`src/erdos97/n9_turn_inequality_frontier.py` (lemma note:
`docs/turn-inequality-lemma.md`).

---

## 0. The question this lane owns

On the strictly convex stratum, is the real solution variety of the 4-bad
system (3n equal-distance equations, 2n-4 effective coordinates) empty? Three
admissible routes were on the table: (i) exact elimination on a small
structured instance to exhibit the over-determination concretely; (ii) a
transversality / dimension count; (iii) a singular-locus argument showing the
convex stratum meets the variety only at degenerate points. The DECISIVE
requirement is that whatever is used must **not** be killed by the P24 control,
which satisfies every metric/rank condition yet is non-convex.

The honest finding of this lane: the algebraic emptiness/finiteness is real but
is **pattern-local**, and the place where strict convexity must enter is *not*
inside the equal-distance ideal at all — it is an extra semialgebraic layer.
I pin down two exact ways to inject it, verify the P24 separation for both, and
state precisely the smallest gap that remains (a Bridge Lemma, already known
open). Dimension heuristics are not proofs and are labelled as such throughout.

---

## 1. Part A — the over-determination, made exact (fixed pattern)

Fix a 4-set `S_i` per center. Each center contributes the three squared-distance
equalities `|p_i-p_a|^2 - |p_i-p_b|^2 = 0`, `b in S_i \ {a}`, giving `3n`
polynomials in `2n` coordinates. Gauge-fix a similarity by `p_0=(0,0)`,
`p_1=(1,0)` (kills 2 translation + 1 rotation + 1 scale d.o.f.), leaving
`2n-4` effective coordinates. The naive virtual dimension is

```text
dim_virtual = (2n - 4) - 3n = -(n + 4)  < 0.
```

For `n=9`: 14 effective coordinates, 27 equations, virtual dimension `-13`.

The exact grevlex Groebner basis collapses this *much further* than the
virtual count even when the variety is nonempty:

| pattern | grevlex GB | unit ideal `{1}` (variety empty)? | zero-dimensional? |
|---|---|---|---|
| F01 (n=9, `[[1,2,3,8],[0,2,4,7],...]`) | size 1 | **yes — variety empty** | n/a |
| F07 (n=9, `[[1,2,4,8],[0,2,3,5],...]`) | size 62 | no | **yes — finite** |

So the system is not merely "expected-negative-dimensional": for F01 the complex
(hence real) variety is literally empty; for F07 it is zero-dimensional, a
collapse from 14 free coordinates to a finite point set. The lex elimination in
`y2` for F07 returns the univariate `y2^2 - 3/4 = 0` (real roots `+-sqrt3/2`),
confirming the variety is nonempty over the reals but supported on `Q(sqrt3)`.

This Part-A picture is consistent with — and is an exact re-derivation of — the
2026-05-05 sweep recorded in `docs/n9-groebner-decoders.md` (150/184 labelled
assignments have GB `{1}`; the rest are zero-dimensional). The new value added
here is the explicit framing as a *real-algebraic over-determination collapse*
together with Part B (the convexity injection and the P24 separation).

**Trust:** the GB size, unit-ideal, zero-dimensionality and univariate root facts
are `EXACT_OBSTRUCTION` for the stated fixed pattern in the stated gauge only.
A different gauge yields a different (but equivalent) GB; the gauge-invariant
statement follows because similarities preserve strict convexity. There is **no**
claim of an analogous algebraic structure at general `n`.

---

## 2. Part B — where strict convexity must enter (the decisive issue)

P24 (`scripts/verify_p24_metric_linear_nonconvex.py`) satisfies every selected
equal-distance equation, has `|S_i cap S_j| <= 1`, and is locally rigid modulo
similarities (exact Jacobian rank `44 = 2n-4` in 48 coordinates), yet it is
**not** convex. Therefore **any route using only the equal-distance ideal plus
rank/linearity cannot separate the convex solutions from P24.** Strict convexity
has to enter as an *additional* semialgebraic constraint. Two exact ways were
verified, and the P24 separation was checked for both.

### 2.1 Route B1 — semialgebraic turn-sign projection

For a real point `p` of the (zero-dimensional) variety, evaluate the `n`
consecutive-turn determinants `tau_i = cross(p_{i+1}-p_i, p_{i+2}-p_{i+1})`.
Strict convexity `<=>` all `tau_i` strictly the same sign **and** the `n`
vertices are distinct. This is the projection of the real variety onto the sign
pattern of the turn polynomials. It is exactly the route of
`scripts/decode_n9_groebner_f07_f13.py`; here it is re-exposed and independently
re-verified live.

Live result on F07 (20 real points enumerated):

```text
turn-sign histogram (pos,neg,zero):  {[9,0,0]:1, [6,3,0]:9, [3,6,0]:9, [0,9,0]:1}
strictly convex real points: 0
```

**A load-bearing subtlety surfaced by the probe.** Two real points DO have an
all-same-sign turn pattern (`[9,0,0]` and `[0,9,0]`), so a naive "all turns same
sign" convexity test would *wrongly* pass them. They are the **degenerate triple
cover of an equilateral triangle**: vertices `{0,3,6}` coincide at `(0,0)`,
`{1,4,7}` at `(1,0)`, `{2,5,8}` at `(1/2, +-sqrt3/2)` — only 3 distinct points,
each traversed three times, which is why every consecutive turn is positive.
The correct convexity injection must require **both** same-sign turns **and**
`n` distinct vertices. With distinctness enforced, the strictly convex count is
0: convexity excludes the entire real variety.

### 2.2 Route B2 — turn-packing elimination (the coupling this lane emphasizes)

This is the route that most cleanly answers "how does strict convexity enter so
the route is not killed by P24". The proven turn-inequality lemma
(`docs/turn-inequality-lemma.md`) is, read correctly, a **real-algebraic
elimination of the convexity-coupled system onto the turn-variable space**: for
a center `i` and a selected offset pair `a < b` with equal center-distance, the
*algebraic* equality `|p_{i+a}-p_i| = |p_{i+b}-p_i|` forces (via
`u.v = -|v|^2/2 < 0` and the cone argument) the **linear** turn inequalities

```text
sum_{h=1}^{b-1} t_{i+h} >= 1,     sum_{h=a+1}^{n-1} t_{i+h} >= 1,
```

where `t_i = 2 tau_i / pi`. Strict convexity then supplies the two **global**
facts

```text
t_i > 0 for all i,      sum_i t_i = 4,
```

and a Farkas / turn-packing certificate (`docs/turn-packing-bridge.md`) proves
the resulting turn polytope is empty for the fixed pattern + cyclic order.

Live result (reusing the proven emitter `turn_inequality_terms_for_pattern`
and `find_turn_farkas_certificate`):

| pattern | turn inequalities | Farkas lambda | selected ineqs | `> 4*lambda` | polytope empty |
|---|---|---|---|---|---|
| F07 | 108 | 1 | 5 | yes (5 > 4) | **yes** |
| F01 | 108 | 1 | 5 | yes (5 > 4) | **yes** |

A notable, genuinely additive finding: **B2 kills F07 from the combinatorial
selected pattern + cyclic order alone, without needing the variety to be empty
or even computing the Groebner basis.** B1 needs the (expensive) 0-dimensional
variety enumeration; B2 needs only the proven linear turn lemma. They are
complementary, and B2 is the cheaper, more robust convexity obstruction.

### 2.3 The P24 separation (the whole point)

Route B2's two global premises — `t_i > 0` for all `i` and `sum_i t_i = 4` —
**are exactly strict convexity**, and they are **FALSE for P24**. Recomputing
P24's turns exactly in `Q(sqrt3)`:

```text
P24: equal-distance rows hold = True,  Jacobian rank = 44 (= 2n-4)
P24: turn signs (pos, neg, zero) = (12, 12, 0)  ->  all-positive = False
P24: total signed turning / 2pi = 1.0  (a star-like turning-number-1 non-convex closed polygon)
```

P24 has 12 negative turns, so the all-positive-turn premise fails and route B2
**does not apply to it** — which is precisely correct. The metric/rank route
(equal-distance rows + rank `2n-4`) cannot see this; the convexity ingredient
(`t_i > 0` for all `i`, equivalently the same-sign turn-determinant projection
with distinctness) is exactly the load-bearing piece that excludes P24. This is
the concrete demonstration, required by the lane, that the convexity injection
is the new ingredient and that a metric/rank-only argument is necessarily
killed by P24.

**uses_strict_convexity: YES.** Both injection routes use strict convexity
essentially: B1 uses the same-sign turn-determinant sign condition + vertex
distinctness; B2 uses the all-positive normalized exterior turns and
`sum t_i = 4`. Drop either and P24 survives.

---

## 3. The smallest decisive obstruction (sharp, honest)

Routes B1 and B2 each close a **fixed** selected-witness pattern in a **fixed**
cyclic order. Neither closes an **arbitrary** 4-bad polygon. The remaining gap
is precisely the already-catalogued **Bridge Lemma**:

> Every realizable strictly-convex 4-bad polygon admits some selected-witness
> 4-set assignment whose cyclic-ordered pattern is sign-obstructed (B1) or
> turn-packing-obstructed (B2).

Equivalently, in the language of `docs/canonical-synthesis.md` §5.2, every
realizable counterexample admits an ear-orderable / packing-obstructed witness
selection. This bridge is **open** and is known to be non-combinatorial (a
4-out-regular digraph can have "stuck sets"; the geometry must rule them out).
The contribution of this lane is to confirm, with the P24 control, that:

1. the *algebraic* over-determination alone is pattern-local and not enough
   (F07's variety is nonempty);
2. the convexity injection is what actually closes each fixed pattern, and it is
   exactly the ingredient P24 lacks;
3. the only missing step between "every fixed pattern is closed" and the theorem
   is the Bridge Lemma — a reduction of an arbitrary counterexample to a fixed
   obstructed pattern, not any further algebraic emptiness fact.

A transversality / generic-dimension argument was deliberately **not** pursued
as a proof: failed-idea #9 already records that generic Jacobian rank at
non-solutions does not control the rank on the solution variety (a true solution
sits on the rank-drop locus by the L10 scaling kernel). The exact zero-dimensional
collapse in Part A is the rigorous version of "the variety is small", and it is
honest about being pattern-local.

---

## 4. What this lane did NOT establish

- **No general-`n` emptiness.** Part A is exact only for the two displayed n=9
  patterns; there is no claim that the variety is empty/finite for general `n`
  or for all patterns. (The 2026-05-05 sweep covers the full n=9 frontier; this
  lane re-derives two representatives and adds the convexity-injection framing.)
- **No proof of the Bridge Lemma.** The reduction from an arbitrary 4-bad
  polygon to a fixed obstructed pattern is untouched and remains the open gap.
- **No counterexample, no near-miss.** Nothing here approaches the
  `docs/exactification-plan.md` trigger; the only "all-positive-turn" variety
  point found is the degenerate triangle triple-cover (3 distinct vertices).
- **The turn-inequality lemma itself is review-pending** (its short Euclidean
  proof is the bottleneck flagged in `docs/turn-inequality-lemma.md`); this lane
  consumes it as a stated lemma and does not re-prove it. If that lemma is
  correct, B2's per-pattern obstructions and the P24 separation are exact.
- **Dimension counts are heuristic.** The `-(n+4)` virtual dimension is a
  guideline; convexity is semialgebraic, not algebraic, so it cannot enter the
  dimension count of the equal-distance ideal — which is exactly why a separate
  injection layer (B1/B2) is mandatory.

---

## 5. Bridge value

This lane does not strengthen the global bridge to a proof, but it sharpens the
target usefully:

- It isolates **distinctness** as a necessary part of any turn-sign convexity
  test (the F07 triangle triple-cover would otherwise leak a false convex point).
- It shows B2 (turn-packing) is a strictly cheaper convexity obstruction than B1
  (variety enumeration), so future frontier work should prefer the turn-packing
  certificate and reserve Groebner for patterns the turn lemma cannot reach.
- It gives a one-command, exact, reproducible demonstration that the convexity
  ingredient is load-bearing against the P24 control — a reusable guardrail for
  any future "metric/rank-only" proof attempt.

Confidence that the *stated* facts (Part A emptiness/finiteness; B1/B2 per-pattern
obstructions; P24 separation) are correct: high. Confidence that this route, as
is, advances toward a *proof* of #97 beyond the existing finite-case program:
low — the open Bridge Lemma is untouched and that is stated plainly.
