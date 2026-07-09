# Review priorities

Status: planning guidance only; not mathematical evidence.

This file turns current review feedback into concrete work items. It does not
change the global claim: no general proof and no counterexample are claimed,
and the official/global status remains falsifiable/open. The local `n <= 8`
geometric theorem has passed repository review; its selected-witness
corroboration remains machine-checked and external review is still welcome.

For a Codex-ready task list with issue links, commands, acceptance criteria,
trust deltas, and forbidden overclaiming text, see `docs/codex-backlog.md`.

## Priority 1 - external review of the octagon theorem

Target: `docs/n8-geometric-proof.md`.

Proof trail: `docs/n8-proof-trail.md` joins the geometric proof note, the
machine-checked selected-witness artifact route, and the literature-backed
Dumitrescu shortcut into one claim-neutral reviewer map.

Ask independent geometry reviewers to check:

- the base-apex lemma and its strict-convexity use;
- the isosceles-triangle count `T(A) <= n(n-2)`;
- equality saturation in the octagon case;
- the length-2 diagonal step forcing all side lengths equal;
- the length-3 diagonal step forcing a cover of adjacent exterior-turn pairs;
- the final vertex-cover and total-turn contradiction.

Repository audit outcome (2026-07-09): accepted after explicitly adding the
on-base midpoint exclusion and diagonal half-plane separation. A future
external review should still identify every accepted lemma and any exact gap;
the computational pipeline remains independent audit evidence.

## Priority 2 - audit and extend the n=8 checker

Proof trail: `docs/n8-proof-trail.md` records how the selected-witness artifact
route, independent artifact audit, SymPy-free partial recheck, residual
checker, and class `14` checker fit together.

Audit the current checker, and extend it toward a more independent `n=8`
finite-artifact check that treats the checked-in JSON and certificate data as
inputs, not as generated truth. Any extension should avoid reusing the current
canonicalization and algebra-helper code except where the input format forces
it.

Suggested inputs:

- `data/incidence/n8_reconstructed_15_survivors.json`;
- `data/incidence/n8_incidence_completeness.json`;
- `certificates/n8_exact_analysis.json`.

Suggested checks:

- the 15 survivor classes are valid selected-witness incidence systems;
- claimed cyclic-order eliminations are reproducible;
- named exact certificates for classes `3`, `4`, `5`, and `14` verify from the
  certificate data;
- the checker reports only `EXACT_OBSTRUCTION` or explicit uncertainty.

Current audit entrypoint:

```bash
python scripts/independent_check_n8_artifacts.py --check --json
```

This command checks the checked-in survivor, completeness, compatible-order,
and exact-analysis artifacts as input data. It is an artifact-consistency and
exact-obstruction audit entrypoint, not an independent regeneration of the full
incidence enumeration.

Partial SymPy-free independent cross-check:

```bash
python scripts/independent_n8_obstruction_recheck.py --check --json
```

This command independently replays the compatible cyclic-order counts, the
class `12` cyclic-order kill, and the `y_2`-in-PB-span kill for ten classes
using pure-Python rational arithmetic. It does not verify the Groebner-based
classes `3`, `4`, `5`, or `14`.

## Priority 3 - isolate class 14

Class `14` is the most delicate current survivor obstruction because it uses
PB+ED Groebner reasoning plus a strict-interior conclusion. Move toward a short,
standalone certificate file with a minimal verifier that checks:

- the polynomial system under the stated normalization;
- the claimed Groebner basis or an equivalent exact contradiction;
- every solution branch used in the argument;
- the strict-interior or non-strict-convexity conclusion.

This should be small enough for an external reviewer to audit without reading
the full search pipeline.

Current focused entrypoint:

```bash
python scripts/check_n8_class14_certificate.py --check --json
python scripts/check_n8_residual_certificates.py --check --json
```

The class `14` checker rebuilds only the class `14` `PB+ED` system from the
checked-in survivor rows, compares the stored Groebner basis, derives the four
real branches, and verifies exact strict-interior failure. The residual checker
does the analogous focused replay for classes `3`, `4`, and `5`. Both remain
repo-local audits pending external review.

## Priority 4 - pin literature coverage

Before any paper-style or public theorem-style claim, run a literature sweep
covering repeated distances in convex polygons, isosceles-triangle counts,
metric oriented matroids, and order-k Voronoi degeneracies. Record both found
references and negative search results in `docs/literature-risk.md`.

Do not use unchecked literature summaries to alter the official/global status.
Recheck the official Erdos Problems page before any status update.

## Priority 5 - audit the n=9 vertex-circle exhaustive checker

Target: `docs/n9-vertex-circle-exhaustive.md`.

Reviewer packet: `docs/n9-review-packet.md` collects the current dependency
map, reproduction commands, expected invariants, and acceptance outcomes for
the review. It is a worksheet only and does not promote any `n=9` claim.
The run-capture aid `docs/n9-review-run-bundle.md` records digest-level
provenance for one execution of the compact command surface; it is drift
detection only and does not replace written independent review.
The decision-intake aid `docs/n9-review-decision-intake.md` validates any
external written-review record against the open gate ledger and allowed
outcomes; it is still intake validation only.
The vertex-circle route preflight
`docs/n9-vertex-circle-route-decision-preflight.md` checks that the internal
A6/A7, A8, and A10 notes are ready to hand to the decision intake while the
route gates remain open and independent written review remains required.

The 2026-05-03 archive bundle has been refactored into a repo-native checker
that leaves 0 full `n=9` selected-witness assignments after exact
vertex-circle pruning. Treat this as review-pending until an independent audit
checks:

- the necessity of the two-overlap crossing, witness-pair cap, indegree cap,
  and vertex-circle strict-cycle filters;
- the absence of a hidden symmetry quotient in the 70 row0 choices;
- that minimum-remaining-options branching changes only search order;
- that the raw 184/16 and 102-certificate archive variants agree with the
  repo-native counts after their conventions are documented.

Acceptance standard: a written review should either promote the checker to the
same repo-local finite-case status as `n <= 8`, or identify the exact
mathematical or implementation gap.

Audit aid: `docs/n9-vertex-circle-independent-recheck.md` records a separate
implementation-level recheck. Its scripts reproduce the 184 pre-vertex-circle
frontier, match the stored frontier set and labels, and catalog 219 minimal
obstruction cores covering all 184 systems. This is useful evidence for the
Priority 5 review, but it does not by itself close the review or promote the
`n=9` artifact.

Current input-data audit:

```bash
python scripts/check_n9_vertex_circle_input_audit.py --check --assert-expected --summary-json
```

This command recomputes the row-0 coverage directly as the 70 lexicographic
4-subsets of labels `1..8`, checks the stored row-0 witness lists and masks,
and verifies summary arithmetic from the checked-in JSON. It is a small audit
of the "no hidden row0 quotient" checklist item only; it does not rerun the
brancher, replay vertex-circle certificates, prove `n=9`, or complete
independent review. Use `--json` instead when the full expected-count block is
needed.

Current incidence-filter audit:

```bash
python scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --summary-json
```

This command recomputes the row-level two-overlap crossing table,
witness-pair cap predicate, and selected-indegree cap predicate. It does not
rerun the brancher, audit strict-edge geometry, review selected-distance
quotient soundness, prove `n=9`, or complete review. Use `--json` instead
when the full histogram blocks are needed.

Current branch-option audit:

```bash
python scripts/check_n9_vertex_circle_branch_options.py --check --assert-expected --summary-json
```

This command walks the no-vertex-circle fixed-order search states and compares
the helper `valid_options_for_center` predicate and maintained count arrays
against a direct implementation. It does not prove dynamic-MRO branch coverage,
strict-edge geometry, selected-distance quotient soundness, `n=9`, or complete
review. Use `--json` instead when the full mismatch example block is needed.

Current dynamic-MRO choice audit:

```bash
python scripts/check_n9_vertex_circle_dynamic_mro_choices.py --check --assert-expected --summary-json
```

This command replays the actual minimum-remaining-options branch choice with
and without vertex-circle pruning. It recomputes all unassigned-center option
lists directly at every reached state and checks first-minimum tie breaking.
It does not prove filter soundness, strict-edge geometry, selected-distance
quotient soundness, `n=9`, or complete review. Use `--json` instead when the
full depth and tie histograms are needed.

Current frontier-coverage crosswalk:

```bash
python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check --assert-expected --summary-json
```

This command reruns the dynamic no-vertex-circle brancher and compares the 184
generated complete selected-row assignments with the stored frontier
classification artifact. It does not prove filter soundness, strict-edge
geometry, selected-distance quotient soundness, `n=9`, or complete review. Use
`--json` instead when the full mismatch example block is needed.

The 2026-06-09 internal A6/A7 review note records
`accepted_A6_A7_source_frontier_internal` for the row0, incidence-filter,
branch-option, dynamic-MRO, frontier-coverage, fixed-order replay, compact
brancher, and mixed-rich landing evidence bundle. Treat it as input to a
formal review-decision record, not as a source-of-truth gate closure.

Current Kalmanson self-edge replay:

```bash
python scripts/check_n9_kalmanson_selfedge.py --verify-certificate data/certificates/n9_kalmanson_selfedge.json --assert-expected --summary-json
```

This command treats the stored 184 terminal assignments as certificate inputs
and checks that each has one strict Kalmanson inequality whose two sides reduce
to the same selected-distance quotient multiset. It is a compact certificate
replay only; it does not independently audit brancher coverage, the
pair/crossing filters, the Kalmanson geometric convention, `n=9`, or complete
review. Use `--json` when the full replay payload is needed.

Independent Kalmanson self-edge input replay:

```bash
python scripts/check_n9_kalmanson_selfedge_independent_replay.py --check --assert-expected --summary-json
```

This command intentionally avoids importing the Kalmanson self-edge generator
module. It treats `data/certificates/n9_kalmanson_selfedge.json` as input and
rechecks row shape, row-pair crossing, witness-pair capacity,
selected-distance quotienting, stored strict Kalmanson self-edges, assignment
uniqueness, and the certificate digest. It is still a stored-certificate audit:
it does not regenerate the 184 frontier, audit brancher coverage, prove `n=9`,
or complete independent review. Use `--json` when the first stored self-edge
example record is needed.

Fresh-frontier Kalmanson replay:

```bash
python scripts/check_n9_kalmanson_selfedge_frontier_replay.py --check --assert-expected --summary-json
```

This command imports no `erdos97` package modules and does not read the stored
Kalmanson certificate. It regenerates the same 184 terminal selected-witness
assignments and finds one strict Kalmanson self-edge for each. It is
corroborating audit evidence only, not a change to the review gate or a
promotion of `n=9`.

Current Kalmanson three-row core compression:

```bash
python scripts/check_n9_kalmanson_three_row_core_compression.py --check --assert-expected --summary-json
```

This command also imports no `erdos97` package modules and regenerates the
same 184 terminal selected-witness assignments. It searches all strict
Kalmanson inequalities and all row subsets in increasing cardinality, then
checks that every assignment has an optimally chosen Kalmanson self-edge core
using exactly three selected rows. It is proof-mining compression evidence
only, not brancher soundness, a bridge proof, a proof of `n=9`, or complete
independent review. Use `--json` when the full per-assignment core records are
needed.

Current dihedral-orbit audit:

```bash
python scripts/check_n9_vertex_circle_dihedral_orbit_audit.py --check --assert-expected --summary-json
```

This command treats the stored motif-family artifact and frontier
classification as inputs. It independently replays the cyclic/reflection
dihedral relabelings, checks canonical representatives and orbit sizes, and
crosswalks the 184 stored classification rows back to the disjoint motif
orbits. It is orbit bookkeeping only, not frontier coverage, filter soundness,
or a proof of `n=9`. Use `--json` when the full mismatch example block is
needed.

Current motif-obstruction audit:

```bash
python scripts/check_n9_vertex_circle_motif_obstruction_audit.py --check --assert-expected --summary-json
```

This command treats the stored 16 motif representatives as inputs, recomputes
selected-distance quotient classes and vertex-circle strict interval edges,
and checks the stored representative self-edge equality paths or strict-cycle
edge chains. It is stored-certificate bookkeeping only, not frontier coverage,
brancher soundness, incidence-filter soundness, dihedral orbit bookkeeping, or
a proof of `n=9`. Use `--json` when the full example error block is needed.

Current frontier comparison:

```bash
python scripts/compare_n9_vertex_circle_frontier.py --check --assert-expected --summary-json
```

This command checks the stored P18/C19 comparison artifact against the current
local-core and vertex-circle helpers. It records zero exact n=9 local-core
embeddings into the recorded P18 and C19 patterns, preserves the P18
strict-cycle and C19 fixed-order pass guardrails, and does not prove `n=9`,
provide a counterexample, or supply a transfer theorem. Use `--json` when the
full pattern records are needed.

Current frontier-assignment audit:

```bash
python scripts/check_n9_vertex_circle_frontier_assignment_audit.py --check --assert-expected --summary-json
```

This command checks the stored 184 frontier assignments directly for row
shape, center coverage, pairwise row-intersection caps, two-overlap crossing,
witness-pair capacity, and selected-indegree capacity. It does not prove
frontier coverage, brancher soundness, strict-edge geometry, selected-distance
quotient soundness, `n=9`, or complete review. Use `--json` when the full
example error block is needed.

Current branching-order replay:

```bash
python scripts/check_n9_vertex_circle_mro_branching_replay.py --check --assert-expected --summary-json
```

This command reruns the search with a fixed center order `0,1,...,8` after row
`0`, reusing the same necessary-filter helpers. It checks that the fixed order
also closes the vertex-circle-pruned search and reaches the same `184`
pre-vertex-circle frontier classification as the dynamic MRO artifact. It does
not prove the filters, independently replay vertex-circle geometry, prove
`n=9`, or complete review. Use `--json` when the full fixed-order replay
sections are needed.

Current strict-edge geometry audit:

```bash
python scripts/check_n9_vertex_circle_strict_edge_geometry.py --check --assert-expected --summary-json
```

This command independently enumerates all proper interval containments for the
630 candidate selected rows and compares them with the checker strict-edge
table. It addresses the vertex-circle strict-edge generator only; it does not
review selected-distance quotient soundness, branch coverage, the crossing
filters, prove `n=9`, or complete review. Use `--json` instead when the full
mismatch example block is needed.

The 2026-06-09 internal A8 review note records
`accepted_A8_stri