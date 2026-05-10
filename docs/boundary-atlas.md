# Boundary Atlas

Status: organizing vocabulary only; not mathematical evidence.

This atlas groups common degeneration and obstruction modes for Erdos Problem
#97 work in this repository. It is meant to help reviewers and future agents
classify failures without promoting numerical artifacts, fixed-pattern
obstructions, or review-pending finite-case artifacts beyond their recorded
scope.

For claim status, use `STATE.md`, `RESULTS.md`, `docs/claims.md`, and
`metadata/erdos97.yaml`.

## How To Use This Atlas

- Record which boundary stratum a candidate or proof attempt hits.
- Link to exact checkers or artifacts when a failure is certified.
- Keep numerical warnings separate from exact obstructions.
- Do not infer a global theorem from one stratum unless a separate bridge
  proves that every counterexample must enter it.

## Strata

### COLLISION_BOUNDARY

Two labels coincide, or a pair distance tends to zero.

Typical signal:

- exact midpoint or algebraic equations force `p_i = p_j`;
- a numerical run reports tiny minimum pair distance;
- a real-root decoder finds only coincident or lower-cardinality
  configurations.

Current examples:

- `B12_3x4_danzer_lift` fixed selected pattern, killed by mutual-rhombus
  midpoint equations.
- Some archived C12 numerical artifacts, retained as rejected provenance.

Relevant files:

- `docs/mutual-rhombus-filter.md`
- `data/runs/best_B12_slsqp_m1e-6.json`
- `scripts/check_mutual_rhombus_filter.py`

Claim role: exact obstruction when equality is proved by a checker; numerical
warning when seen only in floating-point runs.

### NONSTRICT_CONVEX_BOUNDARY

The polygon loses strict convexity: an orientation margin reaches zero,
vertices become collinear, or a realization lies on a non-strict boundary.

Typical signal:

- convexity margin is nonpositive or near zero;
- exact algebraic branches produce collinear or non-strict configurations;
- a proof branch ends by showing a required point lies in the wrong strict
  half-plane or in a strict interior position.

Current examples:

- `n=8` survivor classes killed by strict-convexity failure.
- The historical B12 near-miss with convexity margin near `1e-6`.
- The review-pending n=9 real-root decoder follow-up, where accepted real
  configurations are degenerate rather than strictly convex.

Relevant files:

- `docs/n8-exact-survivors.md`
- `docs/n9-groebner-decoders.md`
- `docs/verification-contract.md`
- `scripts/verify_candidate.py`

Claim role: exact obstruction only when the branch certificate proves
non-strictness; otherwise a numerical warning.

### COLLINEAR_WITNESS_BOUNDARY

Witness or center constraints force collinearity that is incompatible with
strict convexity or with the intended circle/circumcenter argument.

Typical signal:

- an exact survivor certificate reports collinearity;
- a circumcenter or radical-axis argument degenerates;
- the selected witness triple no longer determines a proper circle.

Current examples:

- Named `n=8` survivor-class certificates in the exact survivor pass.

Relevant files:

- `docs/n8-exact-survivors.md`
- `scripts/analyze_n8_exact_survivors.py`
- `certificates/n8_exact_analysis.json`

Claim role: exact obstruction for the certified branch only.

### MIDPOINT_COLLAPSE

Perpendicular-bisector or mutual-rhombus equations force midpoint identities
that collapse distinct labels.

Typical signal:

- reciprocal common-witness chords give equations
  `p_x + p_y = p_a + p_b`;
- rational row reduction forces equal coordinates for distinct labels.

Current examples:

- `B12_3x4_danzer_lift`
- `B20_4x5_FR_lift`
- several fixed `C*_pm_*` patterns recorded in the mutual-rhombus filter.

Relevant files:

- `docs/mutual-rhombus-filter.md`
- `scripts/check_mutual_rhombus_filter.py`

Claim role: exact fixed-pattern obstruction when replayed from the stated
pattern data.

### RANK_DROP_LOCUS

The selected squared-distance system has a Jacobian rank drop beyond the
generic diagnostic rank, or a rank argument depends on exact solutions rather
than numerical non-solutions.

Typical signal:

- the Jacobian has the translation, rotation, and scaling kernels at exact
  solutions;
- generic rank `2n - 3` at non-solutions is detected but cannot prove
  nonexistence.

Current examples:

- The generic rank route is recorded as a failed or conditional program.

Relevant files:

- `docs/claims.md`
- `docs/exactification-plan.md`
- `docs/failed-ideas.md`

Claim role: diagnostic or conditional unless paired with a proved bridge and
exact solution-space argument.

### DISTANCE_QUOTIENT_SELF_EDGE

Selected-distance equalities quotient ordinary pair distances, and a
vertex-circle monotonicity inequality forces a strict self-edge.

Typical signal:

- quotienting identifies `[a,b]` and `[c,d]`;
- cyclic order around one center forces `[a,b] > [c,d]`;
- the two classes are equal in the quotient.

Current examples:

- n=9 vertex-circle T01/F09 self-edge local lemma candidate.
- Many review-pending n=9 exhaustive-checker self-edge kills.

Relevant files:

- `docs/vertex-circle-order-filter.md`
- `docs/n9-vertex-circle-t01-self-edge-lemma.md`
- `data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json`

Claim role: exact local obstruction for the displayed hypotheses; review
status follows the referenced packet.

### DISTANCE_QUOTIENT_CYCLE

Selected-distance quotienting and vertex-circle monotonicity produce a directed
cycle of strict inequalities among distance classes.

Typical signal:

- a quotient graph contains a cycle using strict inequalities;
- the cycle length is often 2 or 3 in current n=9 packets.

Current examples:

- n=9 T10/F12, T11/F07, and T12/F16 strict-cycle local lemma packets.
- Review-pending n=9 exhaustive-checker strict-cycle kills.

Relevant files:

- `docs/n9-vertex-circle-obstruction-shapes.md`
- `docs/n9-vertex-circle-strict-cycle-template-packet.md` if added later
- `docs/n9-vertex-circle-t10-strict-cycle-lemma.md`
- `data/certificates/n9_vertex_circle_strict_cycle_template_packet.json`

Claim role: exact local obstruction for certified hypotheses; not an n=9
completeness proof by itself.

### CYCLIC_ORDER_FORBIDDEN

A supplied cyclic order violates exact cyclic-order constraints: crossing
requirements, Kalmanson inverse pairs, Altman diagonal sums, vertex-circle
order, or related order filters.

Typical signal:

- the cyclic crossing CSP is UNSAT;
- a Kalmanson/Farkas certificate sums strict inequalities to zero;
- an all-order search shows every cyclic order contains a forbidden ordered
  quadrilateral pair for one fixed pattern.

Current examples:

- C13 Sidon all-order Kalmanson obstruction.
- C19 skew all-order Kalmanson/Z3 obstruction.
- P24 cyclic crossing CSP.
- P18 vertex-circle order obstruction.

Relevant files:

- `docs/cyclic-crossing-csp.md`
- `docs/kalmanson-two-order-search.md`
- `docs/round2/kalmanson_distance_filter.md`
- `docs/vertex-circle-order-filter.md`

Claim role: fixed-order or fixed-pattern obstruction according to the checker
scope; never a global proof without a separate bridge.

### INCIDENCE_OVERLAP_BOUNDARY

The selected-witness incidence pattern violates necessary pair-sharing,
triple-sharing, crossing, indegree, or count constraints before geometry is
fully considered.

Typical signal:

- adjacent rows share too many selected witnesses;
- row pairs violate the two-circle cap;
- an indegree or pair-count equality case is impossible.

Current examples:

- Small-case incidence exclusions through `n <= 8`.
- Fixed patterns killed by adjacent-row two-overlap rules.

Relevant files:

- `docs/n8-incidence-enumeration.md`
- `docs/claims.md`
- `src/erdos97/incidence_filters.py`

Claim role: exact obstruction when the necessary incidence lemma applies to
the stated pattern or finite enumeration.

### SOLVER_TRUST_BOUNDARY

A finite abstraction has a solver-backed UNSAT replay, but not yet an
independent proof object or second implementation.

Typical signal:

- Z3 replays a stored UNSAT certificate;
- no DIMACS/DRAT/LRAT, SMT proof, or pure finite-order checker exists yet;
- a review priority asks for a solver-independent replay path.

Current examples:

- C19 all-order Kalmanson order UNSAT certificate.

Relevant files:

- `docs/kalmanson-two-order-search.md`
- `docs/review-priorities.md`
- `data/certificates/c19_skew_all_orders_kalmanson_z3.json`

Claim role: exact within the current solver-backed artifact scope, with
remaining independent-replay review risk explicitly recorded.

### LITERATURE_RISK_BOUNDARY

A statement could be mis-scoped because nearby literature concerns a different
problem, such as `k=3`, common-radius unit distances, lower-bound
constructions, or informal/unpublished claims.

Typical signal:

- a source proves a nearby but not equivalent statement;
- a literature summary has not been pinned to a primary source;
- official/global status needs rechecking before public claims.

Current examples:

- Danzer and Fishburn-Reeds `k=3` constructions.
- Erdos 1975 all-`k` Danzer report, treated as unverified literature risk.
- Unit-distance lower-bound constructions that do not resolve the
  variable-radius selected-witness problem.

Relevant files:

- `docs/literature-risk.md`
- `references/source_manifest.yml`
- `metadata/erdos97.yaml`

Claim role: audit warning only.

## Adding A New Boundary Entry

New entries should include:

- a stable all-caps name;
- the failure mode in one sentence;
- typical signals;
- current examples, if any;
- exact files or commands that check it;
- whether the entry is an exact obstruction, numerical warning, review risk,
  or open bridge target.

Do not add a boundary entry to `STATE.md` or `RESULTS.md` unless it changes a
source-of-truth claim after the usual review process.
