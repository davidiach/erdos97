# Glossary

Status: navigation aid only; not mathematical evidence.

This glossary standardizes local vocabulary used across the repository. It is
not a source of truth for claim status. When a definition matters for a proof,
prefer the linked proof-facing document, `STATE.md`, `RESULTS.md`,
`docs/claims.md`, or `metadata/erdos97.yaml`.

## Problem Language

### Bad vertex

A vertex `v` of a strictly convex polygon is bad when at least four other
vertices lie at the same Euclidean distance from `v`. In selected-witness
language, one chosen 4-set witnessing this is denoted `S_v`.

Source: `README.md`, `STATE.md`.

### Counterexample

A strictly convex polygon in which every vertex is bad. This repository claims
no counterexample. A certified counterexample would need exact coordinates, or
an exact algebraic certificate, checking both selected distance equalities and
strict convexity.

Source: `docs/verification-contract.md`.

### Selected-witness system

For each center `i`, a 4-element set `S_i` of other labels whose squared
distances from `i` are required to be equal. The selected sets may vary with
the center, and the directed incidence graph need not be symmetric.

Source: `README.md`, `STATE.md`.

### Strictly convex polygon

A polygon whose vertices are in cyclic order with no three consecutive or
nonconsecutive vertices collinear on the boundary, and with every other vertex
strictly on the same side of each oriented edge. In code, strict convexity is
checked through edge-line orientation margins.

Source: `scripts/verify_candidate.py`, `docs/verification-contract.md`.

## Claim Scope

### Official/global status

The status of Erdos Problem #97 outside this repository. It remains
falsifiable/open unless manually rechecked and updated from the official
problem page.

Source: `metadata/erdos97.yaml`, `docs/upstream-alignment.md`.

### Repo-local finite-case artifact

A machine-checked finite-case result maintained by this repository. The
current source-of-truth finite-case result is the selected-witness exclusion
for `n <= 8`, pending independent review before paper-style or public
theorem-style use.

Source: `STATE.md`, `RESULTS.md`.

### Review-pending artifact

A checked or replayable artifact that is kept separate from the strongest
source-of-truth result until independent review validates the mathematical
argument, implementation, data conventions, and claim scope.

Source: `docs/review-priorities.md`.

### Fixed selected-witness pattern

An abstract directed 4-neighbor incidence pattern, independent of a particular
geometric realization. Obstructing one fixed pattern does not obstruct other
possible selected-witness systems.

Source: `docs/candidate-patterns.md`.

### Fixed cyclic order

A single cyclic ordering of labels for a fixed pattern. A fixed-order
obstruction applies only to that supplied order unless a separate all-order
search or proof is provided.

Source: `docs/round2/kalmanson_distance_filter.md`.

### All-order fixed-pattern obstruction

An obstruction that checks every cyclic order for one fixed abstract
selected-witness pattern. It is still not a global proof of Erdos Problem #97.

Source: `docs/kalmanson-two-order-search.md`.

## Core Obstructions

### Two-circle cap

For distinct centers `a,b`, the selected rows satisfy
`|S_a cap S_b| <= 2`; otherwise two Euclidean circles would share at least
three points.

Source: `docs/claims.md`.

### Radical-axis crossing / bisection

If two selected rows share exactly two witnesses `{a,b}`, then the line through
the two centers is the perpendicular bisector of segment `ab`, and the source
chord crosses the common-witness chord in the cyclic order.

Source: `docs/claims.md`, `docs/mutual-rhombus-filter.md`.

### Mutual-rhombus midpoint obstruction

When two chords are mutual common-witness images, the corresponding midpoint
equations can force label coincidences. If exact rational row reduction forces
two labels to coincide, the fixed pattern is impossible in a strictly convex
polygon.

Source: `docs/mutual-rhombus-filter.md`.

### Kalmanson inequality

A strict convex distance inequality attached to an ordered quadrilateral in a
cyclic order. The repository uses exact positive combinations of such
inequalities, after quotienting selected-distance equalities, to produce
fixed-order or fixed-pattern obstructions.

Source: `docs/round2/kalmanson_distance_filter.md`,
`docs/kalmanson-two-order-search.md`.

### Farkas certificate

An exact positive linear combination of strict inequalities whose coefficient
vector sums to zero after the selected-distance quotient. Summing the strict
inequalities then gives a contradiction of the form `0 > 0`.

Source: `docs/round2/kalmanson_distance_filter.md`.

### Vertex-circle self-edge

A vertex-circle obstruction where selected-distance quotienting identifies two
ordinary chord distances, but cyclic order around a center forces one of them
to be strictly larger than itself.

Source: `docs/vertex-circle-order-filter.md`,
`docs/n9-vertex-circle-local-lemmas.md`.

### Vertex-circle strict cycle

A directed cycle of strict chord inequalities in the selected-distance
quotient. A realizable strict inequality graph must be acyclic and irreflexive.

Source: `docs/vertex-circle-order-filter.md`,
`docs/n9-vertex-circle-obstruction-shapes.md`.

### Altman diagonal-order obstruction

For a natural cyclic order, chord-length sums by cyclic distance are strictly
ordered. A natural-order cyclic-offset selected pattern forcing equality of two
different diagonal-order sums is impossible.

Source: `docs/altman-diagonal-sums.md`.

### Row-circle Ptolemy diagnostic

A diagnostic using the fact that four selected witnesses for one center lie on
a circle centered at that vertex. Current nonlinear instances are numerical
diagnostics unless exactified.

Source: `docs/row-circle-ptolemy-nlp.md`,
`docs/row-ptolemy-product-filter.md`.

## Bridge Vocabulary

### Minimal counterexample

A counterexample with the minimum possible number of vertices. Minimality
forces every deleted vertex to be essential to some remaining vertex's exact
critical 4-tie, but this is not by itself a contradiction.

Source: `docs/claims.md`.

### Critical 4-tie

An exact distance class of size exactly 4 at a center. In a minimal
counterexample, every vertex belongs to one such class for some remaining
center after deletion.

Source: `docs/minimal-fragile-cover-bridge.md`.

### Fragile-cover witness system

A partial selected-witness system produced from minimal-counterexample
critical ties. It is necessary structure for minimal counterexamples, but the
current hypergraph constraints alone are too weak to prove the problem.

Source: `docs/minimal-fragile-cover-bridge.md`,
`docs/bridge-negative-controls.md`.

### Bootstrap core

Local or partial structure meant to bootstrap a global contradiction. Use this
term only with an explicit bridge statement, data source, and non-claim.

Source: `docs/codex-strategy-instructions.md`.

### Radius-blocker

A set encountered by adaptive peeling in which every rich distance class at
each retained center has at most two witnesses inside the set. It is an open
bridge target, not a solved obstruction.

Source: `docs/adaptive-radius-blocker-bridge.md`.

## Evidence And Certificates

### Numerical near-miss

A floating-point artifact with small residuals or small convexity margin.
Near-misses are not counterexamples and cannot certify exact equality.

Source: `STATE.md`, `docs/verification-contract.md`.

### Exactification

The process of replacing numerical or heuristic evidence with exact
coordinates, exact algebraic certificates, interval certificates, SMT
certificates, or formal proofs.

Source: `docs/exactification-plan.md`.

### Interval certificate

A certificate that proves stated inequalities or residual bounds over intervals.
It does not prove exact equality unless the interval method actually supplies
an exact acceptance condition.

Source: `docs/exactification-plan.md`, `docs/codex-backlog.md`.

### SMT certificate

A finite solver certificate or replay artifact. In this repository, SMT-backed
results must keep solver scope explicit and should prefer independently
checkable proof objects when available.

Source: `docs/sat-smt-plan.md`, `docs/review-priorities.md`.

### Boundary stratum

A named degeneracy or failure surface where candidate systems collapse,
violate strictness, lose rank, or hit an exact obstruction. See
`docs/boundary-atlas.md`.
