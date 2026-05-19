# Research Directions, 2026-05-19

Status: `RESEARCH_DIRECTIONS`.

This note records prioritized next directions for Erdos Problem #97 work. It is
planning guidance and proof-mining design, not mathematical evidence. It does
not change the repository claims: no general proof and no counterexample are
claimed; the official/global status remains falsifiable/open; and the strongest
source-of-truth local result remains the repo-local machine-checked
selected-witness `n <= 8` artifact. The `n=9` and `n=10` artifacts remain
review-pending or draft as already recorded.

Trust labels below are deliberately weak unless an exact checked theorem is
already in the repository.

## 1. Aggarwal Forbidden-Cycle Transfer

Trust label: `LITERATURE_ANCHOR` plus `DESIGN_NOTE`.

Aggarwal's unit-distance paper has a useful cut-matrix obstruction that should
be kept separate from the full variable-radius selected-witness matrix. The
paper was last revised on arXiv in 2014 and published in 2015. It defines
0-1 cut matrices coming from an antipodal cut of a convex polygon, records that
distance matrices for those cuts are distance-like, and proves that no
distance-like matrix can be a cycle with an intersection-free edge. In the
paper's terminology, such a cycle is witnessed by rows
`r_1 = 1, r_2, ..., r_l` and columns `c_1 = 1, c_2, ..., c_l`, with
`r_i != r_{i+1}` and `c_i != c_{i+1}`, and with the two entries
`(r_i,c_i)` and `(r_i,c_{i+1})` equal to `1` for every `i` cyclically. See
Aggarwal, "On Unit Distances in a Convex Polygon", arXiv:1009.2216,
Discrete Mathematics 338 (2015), 88--92.

Safe transfer scope:

- Choose a cyclic order and an antipodal cut, i.e. two contiguous boundary
  chains from the same convex polygon.
- Choose one exact ordinary-distance quotient class `Q`, such as a common
  unit-distance class or a selected-distance quotient class already proved
  equal by exact selected-row equalities.
- Build the cut matrix `M_Q` for cross-chain pairs only:

```text
M_Q[row a, column b] = 1
  iff the ordinary pair {a,b} lies in the exact class Q.
```

- Search `M_Q` for Aggarwal cycles with an intersection-free edge using the
  paper's one-only containment convention: extra `1` entries in the submatrix
  are harmless, but every required cycle entry must be in the same exact
  quotient class.

Unsafe transfer:

- Do not combine all selected center-witness edges into one matrix. In this
  problem the selected radius may vary with the center, so a matrix whose row
  `i` marks `j in S_i` is not a unit-distance cut matrix and not one
  same-distance class.
- Do not apply the theorem to non-antipodal or non-cut partitions without a
  separate proof that Aggarwal's distance-like hypotheses still hold.
- Do not treat a numerical near-equality class as `Q`.

Implementation is deferred in this PR. A small exact checker would need only:

1. a cyclic-order antipodal-cut enumerator;
2. a source of exact ordinary-distance quotient classes from selected rows;
3. a pattern-containment search for the required cycle entries;
4. an output schema saying `EXACT_FIXED_CLASS_CUT_OBSTRUCTION`, with the cut,
   quotient class, row/column indices, and cycle entries.

The most natural reuse point is the existing vertex-circle quotient machinery,
but that code should be called only after the data model above is explicit.
This direction is promising as a fixed quotient-class filter; it is not a
bridge from arbitrary variable-radius counterexamples by itself.

## 2. Diameter-Lens And Diameter-Pair Packet

Trust label: `CONDITIONAL_LOCAL_LEMMA_SPEC`.

Conditional lemma:

Let `{v,u}` be a global diameter pair of a strictly convex polygon, and suppose
`u in S_v`. Then every point of `S_v` lies on the circle centered at `v` with
radius `|vu|`. Since `{v,u}` is a diameter pair, every chord between two
witnesses in `S_v` has length at most `|vu|`. If two witnesses subtend angle
`theta` at `v`, then

```text
2 |vu| sin(theta/2) <= |vu|.
```

The witness rays all lie in the open vertex cone at `v`, so `theta < pi`, and
therefore `theta <= pi/3`. Hence the angular span of `S_v` around `v` is at
most `pi/3`.

This is an ordinary global-diameter-pair statement. It should remain separate
from the smallest-enclosing-circle diameter case, where all vertices lie in a
disk with diameter `{v,u}`. That case supplies different right-angle and cap
constraints and should not be silently merged with the selected-row hypothesis
`u in S_v`.

Exact packet spec:

- selected-witness pattern;
- cyclic order;
- distinguished ordered row `(v, S_v)` and distinguished witness `u in S_v`;
- metric inequalities `|vu|^2 >= |xy|^2` for every unordered vertex pair
  `{x,y}`;
- selected equalities `|vw|^2 = |vu|^2` for all `w in S_v`;
- optional derived angular-span certificate for the four witnesses around
  `v`.

Double-boundary endpoint negative control:

The endpoint-only double-boundary package should not be treated as a
contradiction. Normalize a diameter pair to `A = (0,0)`, `B = (1,0)`, and set

```text
R(theta) = (cos theta, sin theta),
L(phi) = (1 - cos phi, sin phi).
```

For `0 < alpha < beta < pi/3`, the seven points

```text
A, L(alpha), L(beta), R(pi/3), R(beta), R(alpha), B
```

in cyclic order form a strictly convex diameter-lens anchor. The endpoint rows

```text
S_A = {B, R(alpha), R(beta), R(pi/3)}
S_B = {A, L(alpha), L(beta), R(pi/3)}
```

both select the diameter radius, overlap in the one non-endpoint equilateral
apex, and attain the seven-vertex lower bound. This anchor is not a 4-bad
polygon, but it shows that any case-1 proof must use witness rows at the
boundary witnesses or another exact certificate. Strict convexity plus the
same-side/seven-vertex package is not enough.

Boundary-witness isolation lemma:

Let

```text
K^+ = B(A,1) cap B(B,1) cap {y >= 0}.
```

If `R(theta) = (cos theta, sin theta)` with `0 < theta < pi/3` and
`X in K^+` satisfies `|X - R(theta)| = 1`, then `X = A`. The boundary check is
elementary: on the segment `AB`, equality forces the segment parameter to be
`0`; on the same right arc, all chord gaps are strictly less than `pi/3`; and
on the left arc, the same-side formula gives equality only when the left angle
is `0`. Since squared distance to `R(theta)` is convex, no other point of the
upper half-lens can be a unit-distance neighbor.

Consequent pruning rule:

For a noncommon upper right-arc endpoint witness `R`, a reciprocal selected
edge `A <-> R` forces `R`'s selected radius to be the diameter. The isolation
lemma then forces the other three selected witnesses in `S_R` below the
diameter line. The symmetric statement holds for noncommon left-arc witnesses
and for the lower half-lens. This is only a finite-pruning ingredient: it does
not cover the common equilateral apex, it requires the reciprocal selected
edge, and it does not by itself rule out a full 4-bad completion.

This packet cannot be applied directly to the stored 184 `n=9` frontier
assignments unless a separate metric diameter certificate identifies a
diameter pair in each assignment. The next useful artifact would be a
hand-checkable local lemma note plus one toy exact packet, including the
boundary-witness isolation check above, not a claim about the full frontier.

## 3. Fishburn--Reeds k=4 Extension Search

Trust label: `COUNTEREXAMPLE_PATTERN_MINING_ONLY`.

The Fishburn--Reeds construction is a `k=3` common-radius example. A `k=4`
analogue search is still useful as structured pattern mining, but every output
must be treated as a candidate pattern until exactified.

Narrow search model:

- restrict to a bipartite chain or two-arc common-radius ansatz;
- count constraints as undirected distance constraints, not directed
  center-row incidences;
- enforce strict convex cyclic order by symbolic inequalities or robust
  interval checks before calling anything a geometric candidate;
- report the selected same-radius graph separately from any variable-radius
  selected-witness interpretation.

Exactification requirements for any hit:

- exact coordinates or an exact algebraic certificate;
- exact equality verification for the undirected distance constraints;
- strict convexity and distinct-vertex certificates;
- a selected-row interpretation with four witnesses at every center, if the
  candidate is meant to address Erdos #97 rather than common-radius mining.

No prototype is added here because the repository already has extensive
fixed-pattern and numerical machinery. The value of this direction is a
carefully scoped pattern generator, not another floating near-miss.

## 4. Reciprocal-Radial Global Budget

Trust label: `RESEARCH_PACKET`.

The existing `docs/reciprocal-radial-budget.md` already records the local
middle-witness inequality. Do not duplicate that packet.

For a global summation theorem, the object to sum is the positive jump

```text
J_{i,t} = |x_t| [e_{t-1},e_t]
          / ([x_t,e_{t-1}] [x_t,e_t])
```

as seen from many centers `i`, or the equivalent cotangent jump at middle
witnesses in selected equal-radius rows. The local signs are controlled only
when the witness is a middle witness in the visible chain from the center, and
the cleared polynomial form relies on positive denominators
`r^2 + x_a . x_b` for consecutive equal-radius witness rays.

What is not yet controlled:

- how often a vertex appears as a middle witness across all selected rows;
- whether the right-hand tangent-half-angle budgets cancel or telescope;
- whether denominators from different centers can be compared exactly;
- whether selected rows can be chosen to avoid any global shortage.

Negative control: the unit pentagon local example in
`docs/reciprocal-radial-budget.md` has one bad center whose two middle
inequalities are tight. Thus any theorem must use a genuine multi-row global
budget, not a single-row obstruction.

Plausibility: moderate as a bridge ingredient, low as a standalone proof until
a summation index and cancellation mechanism are identified.

## 5. Radius Multiset And Reciprocal Selected-Edge Diagnostics

Trust label: `BOOKKEEPING_DIAGNOSTIC`.

Valid observation:

If `a in S_b` and `b in S_a`, then

```text
r_a = |ab| = r_b.
```

Thus every connected component of the undirected reciprocal selected-edge graph
has one common selected radius. This is exact, but it is only bookkeeping:
private per-center radii remain allowed off reciprocal components.

Existing radius-propagation and minimum-radius material should be checked
before adding code. A useful small diagnostic, if needed later, would report:

- reciprocal selected-edge components;
- the centers whose selected radii are forced equal by reciprocity;
- ordinary pair-distance quotient classes induced only by those reciprocal
  edges;
- whether any component lands in an existing exact fixed-class filter.

This diagnostic should not be described as a radius obstruction unless it is
combined with an exact inequality cycle or certificate.

## 6. Selection-Free Numerical Or SDP-Style Mining

Trust label: `FUTURE_NUMERICAL_DIAGNOSTIC`.

The repository already covers much of the numerical landscape through SLSQP,
affine-stretch experiments, fixed-pattern searches, and exactification notes.
New selection-free numerical work should therefore target a genuinely different
object.

Possible future issue:

- an EDM or Gram-matrix relaxation with variables for squared distances,
  triangle/Euclidean constraints, and soft row-wise multiplicity penalties;
- a mixed-integer or moment relaxation for "at least four equal distances from
  each center";
- a smooth surrogate that penalizes the fourth-smallest within-row distance
  spread while preserving strict-convexity margins.

Output discipline:

- numerical failure is not obstruction evidence;
- numerical success is not a counterexample;
- every candidate must include exactification requirements before promotion.

## 7. Global Distance-Multiplicity Accounting

Trust label: `NEGATIVE_NOTE`.

Global pair-distance multiplicity theorems are naturally common-distance
statements. Erdos #97 allows each center to use a private radius, so `n`
selected rows can involve `n` unrelated radius values. A global theorem about
how often one distance can occur does not see the row-local requirement unless
many selected rows are first proved to share one ordinary distance class.

Useful role: support common-radius subcases, reciprocal components, or exact
quotient-class filters.

Not useful by itself: counting all selected center-witness incidences as if
they were one global distance multiplicity.

## 8. Self-Centered Point-Circle Incidence Bounds

Trust label: `SPECULATIVE_BRIDGE_NOTE`.

The incidence framing has `n` points and `n` circles, with each circle centered
at one of the points and required to contain at least four other points. Generic
point-circle incidence bounds are far too weak for this threshold: they are
designed for large asymptotic incidence counts, while a counterexample needs
only `4n` directed incidences.

A sharp convex self-centered theorem of the form

```text
some centered circle incidence system has at most 3n rich incidences
```

under the exact Erdos #97 hypotheses would essentially solve the problem. That
makes this direction a speculative bridge target rather than a near-term
literature shortcut.

## 9. Rejected Or Low-Priority Directions

Trust label: `FAILED_ROUTE`.

Inversion-as-linearity is rejected as stated. Inversion centered at `p_i` does
not turn a circle centered at `p_i` into a line, because that circle does not
pass through the inversion center. It maps to another circle centered at
`p_i`, with reciprocal radius.

Gram-rank obstruction is not new. The useful exact rank facts collapse back to
the repository's existing EDM, Jacobian-rank, perpendicular-bisector, and
selected-distance quotient machinery. Generic rank at nonsolutions remains a
diagnostic, not a proof.

## Follow-Up Queue

1. Implement the Aggarwal fixed quotient-class cut checker only after the data
   model above is wired to exact quotient classes and antipodal cuts.
2. Write the diameter-pair local lemma as a proof-facing note if a concrete
   finite packet needs it.
3. Open any Fishburn--Reeds `k=4` search as pattern mining with explicit
   exactification gates.
4. Try a reciprocal-radial summation only after identifying the global index
   set and a negative control that the proposed theorem must avoid.
