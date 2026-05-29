# n=9 Reduction Chain

Status: `REVIEW_PENDING_DEPENDENCY_MAP`.

This note is a claim map for the current `n=9` selected-witness finite-case
work. It is not a proof of Erdos Problem #97, not a counterexample, not an
official/global status update, and not an independent review. Its purpose is to
make the exact dependency chain auditable.

The candidate finite-case claim being mapped is:

```text
No strictly convex 9-gon has a selected 4-witness row at every vertex.
```

Even if accepted, this would be a repo-local finite-case statement only. It
would not prove the general problem for larger polygons.

## Chain A: Vertex-circle Route

This is the current canonical review-pending `n=9` route.

| Step | Assertion | Evidence | Status |
| --- | --- | --- | --- |
| A0 | A bad nonagon may be labelled in cyclic order `0,...,8`. | Relabel the strictly convex cyclic order. | proved |
| A1 | At every center `i`, choose one 4-subset `S_i` of equidistant witnesses. | This is exactly the selected-witness formulation of the finite case. | proved |
| A2 | The selected rows satisfy the two-circle row-intersection cap. | Two distinct circles meet in at most two points. | proved |
| A3 | A two-overlap row pair forces the source chord to cross the common-witness chord. | Radical-axis/perpendicular-bisector crossing lemma in `docs/claims.md`. | proved |
| A4 | Each unordered witness pair appears in at most two selected rows. | All centers equidistant from the pair lie on one perpendicular-bisector line, and a line meets a strictly convex polygon boundary in at most two vertices. | proved |
| A5 | In `n=9`, each target has selected indegree at most `5`. | For indegree `d`, the selected rows containing the target use `3d` pair incidences; each of the `8` partner pairs can be used at most twice, so `3d <= 16`. | proved |
| A6 | The brancher enumerates all full selected-witness assignments satisfying A2-A5 in the natural cyclic order. | `scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json` and the branch-option, dynamic-MRO, row0-root, and frontier-coverage audits referenced in `docs/n9-vertex-circle-exhaustive.md`. | machine-checked review-pending |
| A7 | The pre-vertex-circle frontier has exactly `184` full assignments. | Same exhaustive cross-check, run without vertex-circle pruning. | machine-checked review-pending |
| A8 | Vertex-circle nested chord intervals give strict inequalities between ordinary pair distances. | Vertex-cone/chord-order geometry and the strict-edge geometry audit. | proof-facing review-pending |
| A9 | Selected-distance equalities quotient ordinary pair distances by row. | Directly generated from the selected rows. | proved |
| A10 | Every one of the `184` frontier assignments contains a quotient self-edge or strict directed cycle. | `docs/n9-vertex-circle-certificate-chain.md`, local-lemma packets, quotient-soundness audit, and local-lemma audit path. | machine-checked review-pending |
| A11 | Therefore no true bad nonagon exists, assuming A6, A8, and A10 survive independent review. | Follows from the chain above. | review-pending conditional |

The live review burden in this route is not the arithmetic count `184 = 158 +
26` by itself. The burden is accepting that the brancher covers exactly the
finite frontier, that the vertex-circle strict-edge rule is a necessary
geometric rule, and that the quotient certificates are replayed correctly.

## Chain B: Turn-packing Route

This is a second review-pending route over the same 184-assignment frontier. It
does not replace Chain A, but it gives a compact independent obstruction style
if its geometric turn lemma is accepted.

| Step | Assertion | Evidence | Status |
| --- | --- | --- | --- |
| B0 | Start from the same 184 assignments produced by A6-A7. | `scripts/check_n9_turn_inequality_frontier.py` regenerates the source frontier and records the same frontier hash. | machine-checked review-pending |
| B1 | If two selected witnesses at offsets `1 <= a < b <= 8` are equidistant from center `i`, then two exterior-turn sums are strictly greater than `pi/2`. | `docs/turn-inequality-lemma.md`. | proof-facing review-pending |
| B2 | Replacing the strict inequalities by weak normalized inequalities `>= 1` is legitimate. | Strict geometry implies the weaker closed halfspace, if B1 is correct. | conditional on B1 |
| B3 | For each of the 184 assignments, the weak turn system has an integer turn-packing/Farkas contradiction. | `data/certificates/n9_turn_inequality_frontier.json` checked by `scripts/check_n9_turn_inequality_frontier.py --check --assert-expected --summary-json`; use `--json` for full certificate rows. | machine-checked review-pending |
| B4 | The certificate principle is elementary: if `m > 4*lambda` intervals are forced and each turn variable appears at most `lambda` times, then `sum t_i = 4` is contradicted. | `docs/turn-packing-bridge.md`. | proved, assuming stored intervals are forced |
| B5 | Therefore no true bad nonagon exists, assuming A6-A7, B1, and B3 survive independent review. | Follows from the chain above. | review-pending conditional |

This route has a different bottleneck from Chain A. Its final contradictions
are short arithmetic certificates, but the exterior-turn lemma and indexing are
the proof-facing hinge.

## Chain C: Algebraic Cross-audit

The Groebner route is useful corroboration for the same frontier, but it is not
currently the primary route and does not independently establish the whole
frontier reduction.

| Step | Assertion | Evidence | Status |
| --- | --- | --- | --- |
| C0 | The 184 labelled frontier assignments collapse to 16 dihedral families. | 2026-05-05 artifact and follow-up decoder docs. | machine-checked review-pending |
| C1 | 150 labelled assignments have Groebner basis `{1}` over `QQ`. | `data/certificates/2026-05-05/n9_groebner_results.json`. | machine-checked review-pending |
| C2 | 18 labelled assignments in F12 have no real solution because a generator gives `y_8^2 + 1/4 = 0`. | Same artifact. | machine-checked review-pending |
| C3 | The remaining 16 labelled assignments have only degenerate real configurations, not strictly convex nonagons. | `docs/n9-groebner-decoders.md` and `data/certificates/n9_groebner_real_root_decoders.json`. | machine-checked review-pending |
| C4 | Therefore the algebraic route corroborates the vertex-circle obstruction of all 184 assignments. | It consumes the dihedral-family reduction and closes the displayed families. | review-pending corroboration |

The algebraic route is valuable as a second source, but a reviewer should not
treat it as a standalone `n=9` proof unless the 184-to-16 family reduction and
decoder replay are independently audited.

## Current Bottlenecks

The strongest honest reading is:

```text
The repo has multiple machine-checked, review-pending routes that close the
stored n=9 selected-witness frontier. The remaining work is independent review
of the reduction and obstruction chain, not a claimed status promotion.
```

The most important finite-case review targets are:

- necessity of the row filters A2-A5;
- absence of hidden symmetry quotienting in row0 coverage and branch order;
- soundness of vertex-circle strict-edge geometry;
- soundness of selected-distance quotient self-edge and strict-cycle replay;
- independent agreement that the 184 frontier is the intended pre-obstruction
  source frontier;
- for the turn route, the exterior-turn lemma and interval indexing.

The most important global gap is separate:

```text
There is no bridge from arbitrary larger counterexamples to the n=9 frontier.
```

Thus none of these artifacts proves Erdos Problem #97.

## Minimal Review Command Set

For the vertex-circle route:

```bash
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
python scripts/check_n9_vertex_circle_input_audit.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_strict_edge_geometry.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_quotient_soundness.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --summary-json
```

For the turn-packing route:

```bash
python scripts/check_n9_turn_inequality_frontier.py --check --assert-expected --summary-json
```

For the algebraic cross-audit:

```bash
python scripts/decode_n9_groebner_f07_f13.py
```

These commands are review aids. Passing them does not, by itself, complete
independent mathematical review.
