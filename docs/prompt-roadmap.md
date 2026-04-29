# Prompt Roadmap

Status: HEURISTIC planning note. This file is not mathematical evidence and
does not claim a proof or counterexample for Erdos Problem #97.

This note distills the local prompt-pack comparison into repo-facing guidance:
which prompt directions are worth running next, what artifacts they should
produce, and which routes should be treated as exhausted or auxiliary.

## Operating Protocol

Use prompt runs as hypothesis generators, not as sources of truth.

1. Run proof-generation prompts in fresh no-web chats.
2. Audit any plausible proof in a separate no-web chat.
3. Keep web/literature triangulation in a separate mode from proof generation.
4. Promote only independently checked results into repo docs.
5. Prefer outputs that create reproducible artifacts: scripts, JSON survivor
   lists, exact certificates, or small formally checkable lemmas.

The most important audit checks are:

1. Identify every load-bearing use of strict convexity.
2. Justify cyclic-order claims from convexity, not pictures.
3. Verify every crossing-bisector use instead of assuming it.
4. Treat generic rank and dimension counts as diagnostics unless the special
   solution locus is controlled.
5. Label numerical evidence separately from exact claims.

## Current Prompt Status

### Completed Or Parked: A/B Matrix Route

The centered-circle incidence matrix route has already produced its stable
matrix-only yield:

1. the crossing-bisector lemma;
2. the forbidden noncrossing `2x2`, `2x3`, and `3x2` submatrices;
3. the discharging bound
   `sum_i binom(|S_i|, 2) <= n(n-2)`;
4. the matrix-only consequence `n >= 8` under minimum row size `4`;
5. explicit abstract A/B countermodels showing that A/B alone cannot prove the
   full theorem.

Do not keep rerunning this as a standalone prompt unless the goal is a
targeted audit of a new lemma. Future work should use this route as a filter
or subroutine, not as the main engine.

For the detailed audit of recent A/B prompt runs, see
`incoming/chatgpt-runs/audit.md`.

### Priority 1: Certified Fragile-Hypergraph Computation

This is the best next direction because it can produce reproducible repo
artifacts.

The first Prompt 3 fragile-cover run was reviewed in
`incoming/prompt3-runs/audit.md`. Its cover lemma is valid and already matches
the repo's minimal-counterexample critical-tie claim, but the run also gives
linear-cover and convex-octagon warning examples showing that cover plus
crossing is not enough. Treat fragile cover as a computation filter, not as a
standalone contradiction route.

Target deliverables:

1. a precise finite abstraction of fragile pointed `4`-sets;
2. proved constraints: cover, self-exclusion, row intersection, cyclic
   crossing, and any additional exact geometric filters;
3. enumeration code up to a small `n` range;
4. JSON survivor artifacts;
5. symmetry reduction under cyclic/dihedral relabeling;
6. handoff from surviving hypergraphs to polynomial equal-distance systems;
7. optional rank-test integration with existing exactification tools.

Success does not require a general proof. A useful result is a short list of
survivor patterns, a new exact obstruction, or a reproducible infeasibility
certificate for a finite range.

### Priority 2: Affine-Circuit / Rank Rigidity

This has high upside but is more fragile than the computation route.

Use the corrected target:

> In the non-concyclic case, prove that the only kernel functions are the
> unavoidable span of `1`, `x`, `y`, and `x^2+y^2`, or construct an explicit
> exotic syzygy.

Avoid the older naive rank claim. The unavoidable quadratic kernel is real and
must be built into the statement. Generic rank at random non-solutions is only
diagnostic.

The first Prompt 2 rank run was reviewed in
`incoming/prompt2-runs/audit.md`. Its quotient reduction is useful: after
choosing a nonsingular lifted four-point base, exotic syzygies are exactly the
kernel of the remaining-column affine-circuit matrix, and singleton peeling
reduces this to a weighted two-core. The continuation refines those defects to
minimal-support cofactor certificates: isolated quotient columns, balanced
pair-gain components, and mixed hypercore determinant identities. This is a
checker specification, not a proof of full rank.

Useful artifacts from this path:

1. a concrete exotic-syzygy example;
2. a finite list of rank-defect incidence patterns;
3. a verified symbolic minor for a restricted pattern class;
4. a bridge lemma connecting rank rigidity to selected witness patterns.

### Side Probe: Smooth Strictly Convex Curve

The smooth-curve falsification probe is useful for intuition:

> Does there exist a smooth strictly convex closed curve such that every point
> has some centered circle meeting the curve in at least four other points?

Either answer would clarify whether the obstruction is primarily discrete or
convex-geometric. This should remain a side experiment unless it produces a
short rigorous lemma.

### Side Probe: Local Angle Filters

The first Prompt 0 run was reviewed in `incoming/prompt0-runs/audit.md`. It
does not provide a proof, but its middle-witness angle inequality appears
usable as a local filter after correcting the cone statement at a hull vertex:
other vertices lie in the closed incident-edge cone, with only adjacent
vertices on the boundary rays. Treat this as an auxiliary filter for selected
witness patterns, not as a primary proof route.

### Side Probe: Fishburn-Reeds / Near-Miss Perturbation

The `k=3` Fishburn-Reeds and Danzer-style examples are useful stress tests, not
templates to promote directly to `k=4`.

A useful prompt run here should try to prove that perturbing or lifting a
known `3`-neighbor example necessarily creates an exact obstruction, or else
produce exact algebraic data for a serious candidate. Floating-point
near-misses remain provenance only.

## Lower Priority Routes

The following can be useful, but should not displace the certified computation
and corrected rank paths:

1. vertex-centered incidence bounds;
2. VC-dimension or shatter-function estimates;
3. perpendicular-bisector arrangement counts;
4. sum inequality `sum_i m_i < 4n`;
5. SOS/Lasserre certificates for fixed small patterns;
6. local four-vertex-theorem analogies.

These routes become high value only if they produce a concrete lemma or a
checkable certificate that interacts with the selected-witness formulation.

## Suggested Next Work Item

Start a Prompt 4 style computation pass:

1. Define the exact fragile-hypergraph abstraction used in this repo.
2. Implement or extend enumeration for the next finite range not already
   covered by `n=7` and `n=8`.
3. Emit reproducible JSON artifacts.
4. Add tests for every combinatorial filter.
5. Route survivors to existing exact obstruction machinery.

Keep all outputs labeled as finite abstraction, incidence pattern, exact
obstruction, numerical evidence, or failed approach according to the repo trust
taxonomy.
