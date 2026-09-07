# Final exploration inventory and evidence boundary

This is a publication audit of the final conversation, not a fresh exhaustive
mathematical search. The four research packets in `snapshots/` are preserved
in full. The additional closing conversation did not deliver a new ZIP or
saved optimization/run log with its numerical exploration claims. Those
claims are recorded below at that lower evidence level, not silently promoted.

## 1. Nine-orbit own-side C3 search

The conversation reported that extending the existing angular-first search
from eight to nine orbits produced earlier-filter survivors in each of the
28 maximum-radius row-zero slices. No complete per-slice output, adapted
source, seed record, or optimization log from that final run is available in
the delivered artifacts. This PR does **not** claim to have recovered or
reproduced that 28-slice run, nor does it assert complete enumeration.

The concrete table that was printed is retained exactly in
`nine-orbit-candidate.json` under `rows`:

```text
0 -> (1,1), (2,1)
1 -> (3,1), (4,1)
2 -> (4,1), (7,1)
3 -> (2,1), (5,1)
4 -> (6,2), (8,1)
5 -> (0,0), (7,2)
6 -> (0,0), (3,2)
7 -> (6,1), (8,1)
8 -> (1,0), (5,2)
```

The second entry in each pair is a rotation gain modulo three. The physical
boundary order is `0,...,26`, with label `i+9*k` representing `omega^k*z_i`;
label zero is a maximum-norm orbit. These are combinatorial premises, not
coordinates or equally spaced angular phases.

**Fresh exact result:** the table passes the explicitly reimplemented
no-reciprocity, two-circle/crossing, right-angle interlacing, radius-order,
monotone-path shortcut, and selected Kalmanson cancellation/domination filters.
However, six applications of the existing right-angle containment rule reject
it in this supplied order. See the parent README for a hand-checkable example.

The final response's characterization of this table as an unresolved
nonlinear-realization frontier is therefore withdrawn for this fixed order.
No numerical attempt is needed to reject this particular table. This neither
classifies all nine-orbit systems nor establishes an all-order obstruction to
the abstract unlabelled arrow graph. No complete Kalmanson LP or chord-angle
feasibility decision is claimed by the fresh lightweight replay.

## 2. Unbounded family and endpoint closure

The exact family and arbitrary finite continuation are already retained in
[the merged packet](../unbounded-six-exception-family-2026-09-06/README.md)
(PR #940). Its written all-radius bounds leave exactly six good vertices at
every finite length. Merely extending the **same prescribed recurrence** cannot
make those vertices rich. This follows from that existing theorem, not from
a new numerical search in the present PR.

The final conversation additionally discussed backward parameter extension
and an asymptotic missing witness. No separate backward-extension exclusion
proof or retained computation was delivered. Do not interpret that discussion
as an exclusion of every modified seed, reversed recurrence, changed carrier,
or different endpoint-completion construction.

## 3. The exact 66-point partial construction

The earlier [66-point construction](../../docs/orbit66-exact-partial-construction.md)
already certifies 60 rich vertices and six exceptions. In its selected
own-side graph, orbit 3 lacks two outgoing cross-orbit witnesses and orbit 7
lacks one. Its two-constraint growth adds two arrows per new orbit and does
not automatically remove that three-arrow deficit. Those are existing
construction bookkeeping facts, not new results of this import.

The final conversation reported a search over incoming/outgoing constraint
circle intersections and small near-reciprocal residuals. The search code,
coverage, numerical outputs, and exactification records for that final probe
are not present in the delivered artifacts. Record the claimed probe as
**conversation-reported exploratory work only**. It supplies neither an
exhaustive nonexistence conclusion nor a new exact identity. Do not infer that
all possible appended or altered orbits have been excluded.

## 4. The 27-point product control

The existing [product control](../../docs/c3-product-27-nonconvex-control.md)
gives four exact witnesses at every point, but only 18 of its 27 points are
hull vertices. It is not a convex counterexample. This PR links the existing
exact checker rather than rerunning it or duplicating its artifact.

The final response's claimed deformation degrees of freedom and failed
convexification search are not supported by a delivered rank certificate,
source/log bundle, or exhaustive argument. They are retained here as
unverified exploration, not a theorem about every realization of that product
template. Convexity remains essential.

## 5. A possible global incidence target

For the verified finite members of the six-exception family whose other
vertices have maximum multiplicity exactly four, the multiplicity sum is

```text
3*2 + 3*3 + (n-6)*4 = 4n-9.
```

The arbitrary-size family proof only supplies multiplicity **at least four**
at its rich vertices; it does not establish the same exact sum at every size.
The finite identity must not be extrapolated without an additional upper bound.

A universal inequality `sum_v M_P(v) < 4*|P|` would imply Erdős #97, simply
because its negation at every vertex would give a sum at least `4*|P|`.
No such universal inequality is proved here. A bound for a selected
one-circle-per-center directed incidence system would likewise need its own
precise hypotheses and proof. The repository's
[failed-ideas record](../../docs/failed-ideas.md) already warns against
unsupported end/middle-neighbor counting and injectivity assumptions.

The publication does not independently verify the final response's attribution
of a stronger conjecture, its AlphaEvolve discussion, or its claimed current
public status. Those external statements are not needed by, and are not
accepted evidence for, any mathematical result in this packet.

## 6. What the import does not do

It does not complete the unrestricted bridge, assert a counterexample,
promote the accepted finite bound, merge a PR, or supply an independent review.
The negative controls target specified weaker lemmas; most of their vertices
are not four-rich. All-rich-specific closure is still a distinct obligation.
The original failed routes are retained to make those boundaries auditable.
