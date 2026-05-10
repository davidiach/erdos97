# Independent audit target loop

Date: 2026-05-10

Status: planning guidance only; not mathematical evidence. This report does
not change any repository claim. No general proof and no counterexample are
claimed. The official/global status remains falsifiable/open. The `n <= 8`
selected-witness result remains repo-local and machine-checked pending
independent review. The `n=9` and `n=10` vertex-circle artifacts remain
review-pending/draft as already recorded.

## Inputs read

- `AGENTS.md`
- `README.md`
- `STATE.md`
- `RESULTS.md`
- `docs/claims.md`
- `docs/review-priorities.md`
- `docs/reviewer-guide.md`
- `docs/n8-exact-survivors.md`
- `docs/n9-vertex-circle-exhaustive.md`
- `docs/n10-vertex-circle-singleton-slices.md`
- `docs/codex-backlog.md`
- `metadata/erdos97.yaml`

## Small live check

Command run:

```bash
python scripts/independent_check_n8_artifacts.py --check --json
```

Result: passed in this workspace.

Key reproduced fields:

- `verified: true`
- `overall_status: n8_artifacts_verified_repo_local_pending_external_review`
- `survivor_json.record_count: 15`
- `exact_obstruction_artifacts.certificates.class14_pb_ed_groebner_basis: true`
- `exact_obstruction_artifacts.certificates.class14_solution_branches: true`
- `exact_obstruction_artifacts.certificates.class14_strict_interior: true`

This command is useful as a baseline, but it imports the current n=8 analyzer.
It should not be mistaken for the independent standalone class-14 audit
recommended below.

## Cycle 1: propose, audit, refine

Proposal: choose the review-pending `n=9` vertex-circle checker because it has
the largest possible trust payoff: a successful independent audit could move a
candidate finite-case extension closer to the repo-local `n <= 8` trust level.

Audit of proposal: the `n=9` target has a broad audit surface. A reviewer must
check the geometric necessity of each pruning rule, the row0 coverage, the
minimum-remaining-options branch order, partial vertex-circle pruning, and the
archive convention reconciliation. That is valuable, but it is too large for
the next bounded input-data replay if the goal is to remove the most delicate
current trust dependency first.

Refinement: demote `n=9` to runner-up and first audit the narrowest high-risk
dependency in the current source-of-truth local result: `n=8` class `14`.

## Cycle 2: propose, audit, refine

Proposal: choose `n=8` class `14` and verify the PB+ED Groebner basis plus the
strict-interior branch conclusion as a standalone certificate replay.

Audit of proposal: merely rerunning `scripts/analyze_n8_exact_survivors.py`
would reuse the same code path that produced the current acceptance. The
valuable audit must treat checked-in JSON as input data, reconstruct the
polynomial system independently from the class-14 incidence rows, and fail
closed when certificate fields are missing or unsupported.

Refinement: the target is not "rerun n=8"; it is "standalone class-14 input
replay." The audit should avoid current canonicalization helpers and should not
import `scripts/analyze_n8_exact_survivors.py`. It may use a standard exact
algebra engine, but the certificate logic and strict-interior sign check should
be written as a small separate verifier or as external review notes.

## Cycle 3: propose, audit, refine

Proposal: define a concrete class-14 audit with explicit pass/fail/unknown
criteria, negative controls, and no source-of-truth metadata updates.

Audit of proposal: the plan must not promote any result. It must also not
silently convert the checked-in artifact into proof by prose. The checked JSON
is input data to be validated, not generated truth.

Refinement: select `n=8` class `14` as the best next independent trust audit
target. Record `n=9` vertex-circle as the next target after class `14`; defer
`n=10` singleton slices until the shared generic vertex-circle machinery has
more independent review or a replayable terminal-conflict certificate format.

## Selection

Best next independent audit target: `n=8` class `14`.

Why this target:

- It is explicitly called out as the most delicate current `n=8` survivor
  obstruction: PB+ED Groebner reasoning plus a strict-interior conclusion.
- It supports the repository's current strongest local finite-case artifact,
  while still staying inside the repo-local pending-review scope.
- It is small enough for a reviewer to audit without reading the full search
  pipeline.
- It has concrete checked-in inputs and a crisp expected outcome: every
  recorded real branch fails strict convexity by having only four hull vertices.
- A successful audit improves trust in the existing `n <= 8` artifact without
  changing the official/global status or promoting the review-pending `n=9` or
  draft `n=10` artifacts.

Runner-up: `n=9` vertex-circle checker.

Why not first: it has high payoff but broader risk. Its audit should follow
after the class-14 standalone replay, using the same discipline: checked-in
JSON as input data, no status promotion, and explicit uncertainty on
unsupported cases.

Deferred: `n=10` singleton slices.

Why deferred: it is still a draft continuation with all 126 singleton slices
recorded, but it depends on the same generic vertex-circle machinery and needs
either broader second-implementation agreement or replayable terminal-conflict
certificates before it is the best next trust target.

## Concrete audit plan for `n=8` class `14`

### Scope

Audit only the class-14 exact obstruction certificate. Do not regenerate the
full `n=8` incidence enumeration. Do not update `README.md`, `STATE.md`,
`RESULTS.md`, `metadata/erdos97.yaml`, or any generated artifact.

### Input data

Treat these checked-in files as read-only input data:

- `data/incidence/n8_reconstructed_15_survivors.json`
- `certificates/n8_exact_analysis.json`
- optionally `certificates/n8_polynomial_systems.txt` as a human-readable
  cross-check, not as authority

The verifier or written audit should identify class `14` by its stored class
id and rows. It should not rely on canonicalization code to discover the class.

### Independent reconstruction

1. Parse the class-14 `8 x 8` binary selected-witness matrix.
2. Check only local schema facts needed by the certificate: zero diagonal,
   row size `4`, and binary entries.
3. Use the gauge

   ```text
   p0 = (0,0), p1 = (1,0), y2 != 0
   ```

4. Reconstruct perpendicular-bisector equations from each two-overlap
   row-pair `{i,j}` with common witnesses `{a,b}`:

   ```text
   (p_i - p_j) dot (p_a - p_b) = 0
   det(p_j - p_i, p_a + p_b - 2 p_i) = 0
   ```

5. Reconstruct equal-distance equations for every selected row by choosing a
   deterministic base witness from the row and equating squared distances from
   the center to the other selected witnesses.

### Algebra replay

1. Recompute the lexicographic Groebner basis over `QQ` from the reconstructed
   PB+ED equations, using the class-14 variable order recorded by the current
   artifact:

   ```text
   x6, y6, y7, x2, y2, x3, y3, x4, y4, x5, y5, x7
   ```

2. Normalize the basis to monic polynomial representatives and compare against
   the certificate's expected basis, or independently reduce the expected
   basis and generated equations both ways.
3. Report `UNKNOWN` rather than pass if the stored basis cannot be parsed, if
   the variable order is absent or ambiguous, or if the generated equations do
   not reduce exactly.

### Branch replay

1. Parse the four recorded real algebraic branches.
2. Represent `a = sqrt(3)/2` exactly by `4*a^2 - 3 = 0` with `a > 0`.
3. Evaluate every reconstructed PB+ED equation on each branch.
4. Check that the four branches exhaust the real solutions exposed by the
   basis: the independent factors force `y5 = +/- 1` and
   `x3 = +/- sqrt(3)/2`, with the remaining coordinates determined by the
   linear basis elements.
5. Reject or report `UNKNOWN` if any branch is missing, duplicate, malformed,
   or not forced by the basis.

### Strict-interior replay

For each branch:

1. Use the hull labels recorded in the certificate as input.
2. Compute exact orientation signs for each hull edge and its next hull vertex.
3. Compute exact orientation signs from each hull edge to every non-hull label.
4. Verify all hull turns have one strict sign and all non-hull points lie
   strictly on the same interior side of every hull edge.
5. Use exact sign reasoning only. Acceptable sign facts include
   `0 < 1 - a < 1/2 < a < 1` for `a = sqrt(3)/2`.

The expected conclusion is only that the recorded class-14 PB+ED branches are
not strictly convex realizations. It is not a general proof and not a
counterexample claim.

### Negative controls

Run at least these failure checks before trusting the verifier:

- remove one equal-distance equation and require the verifier to stop short of
  the same conclusion;
- flip one class-14 row entry and require schema/equation/basis mismatch;
- perturb one branch coordinate and require branch evaluation failure;
- replace one hull label list with a non-hull label and require the
  strict-interior check to fail or return `UNKNOWN`;
- delete the stored branch list and require `UNKNOWN`, not success.

### Deliverable

Preferred deliverable: a short standalone audit report plus, if warranted, a
small checker with a command shaped like:

```bash
python scripts/independent_check_n8_class14.py \
  --survivors data/incidence/n8_reconstructed_15_survivors.json \
  --certificate certificates/n8_exact_analysis.json \
  --check --json
```

The checker should be disjoint from the current analyzer except for unavoidable
standard-library or exact-algebra dependencies. If no checker is added, the
written audit should still include the exact equations, basis comparison,
branch evaluation, strict-interior sign table, environment, command transcript,
and failure modes.

### Acceptance standard

Accept the audit as useful only if it answers all of these:

- Did the auditor reconstruct the class-14 PB+ED system from checked-in JSON?
- Did the auditor verify the exact algebra without importing the current n=8
  analyzer?
- Did the auditor verify every real branch and the strict-interior conclusion
  by exact signs?
- Did negative controls fail closed?
- Did the report preserve the current claim scope and avoid promoting `n=8`,
  `n=9`, `n=10`, or the global Erdos #97 status?

## Follow-on target after class `14`

After the class-14 audit, the next best independent trust target is the `n=9`
vertex-circle checker. A future n=9 audit should treat
`data/certificates/n9_vertex_circle_exhaustive.json` as input, independently
replay row0 coverage and the 184 pre-vertex-circle obstruction classification,
and review the geometric necessity of the vertex-circle self-edge/strict-cycle
filter. It must keep the artifact review-pending unless a broader review
decision explicitly promotes it.
