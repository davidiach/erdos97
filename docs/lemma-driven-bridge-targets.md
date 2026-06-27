# Lemma-driven Bridge Targets

Status: `BRIDGE_ROADMAP_ONLY`.

Claim scope: proof-planning map for bridge lemmas from arbitrary or minimal
counterexamples to currently checked local obstruction packets.

Source of truth: `README.md`, `STATE.md`, `RESULTS.md`, `docs/claims.md`, and
`metadata/erdos97.yaml`.

Last assembled: 2026-06-09.

## Non-claims

- This map does not prove Erdos Problem #97.
- This map does not claim a counterexample.
- This map does not prove `n=9`, `n=10`, or any larger finite case.
- This map does not promote review-pending local-lemma packets.
- This map does not update the official/global status.

## Purpose

The bridge program has many checked diagnostics now. The useful next step is
not another broad catalogue unless it proves a new necessary condition. This
map names the bridge lemmas that would actually connect the existing finite
packets to arbitrary or minimal counterexamples, and it records the negative
controls each candidate must survive.

## Current proved footholds

- Minimality gives exact critical 4-ties: every minimal counterexample admits
  a fragile-cover witness system. See `docs/minimal-fragile-cover-bridge.md`.
- Adaptive peeling gives the ear-orderable/radius-blocker fork. A non-ear
  counterexample contains a radius-blocker. See
  `docs/adaptive-radius-blocker-bridge.md`.
- Rich-triple closure gives the bootstrap fork. If the bootstrap rank is at
  most `3`, an ear-orderable selected-witness system exists; otherwise a
  minimal generator has deletion closures, private halos, and a weighted
  outside-pair capacity ledger. See `docs/bootstrap-core-bridge.md`.
- Strict quotient self-edges and directed strict cycles are valid local
  obstruction criteria once the relevant selected-distance equalities and
  vertex-circle strict edges are genuinely available. See
  `docs/n9-vertex-circle-self-edge-criterion.md` and
  `docs/n9-vertex-circle-strict-cycle-criterion.md`.

These are necessary-structure or local-obstruction lemmas only. They do not
force one of the stored local templates by themselves.

## Best current finite targets

| Target | Current evidence | Missing lemma |
| --- | --- | --- |
| `T01`--`T12` local templates | `docs/n9-vertex-circle-local-lemma-review-packet.md` packages 12 templates, 16 families, and 184 stored assignments | A proof that a minimal/rich-support counterexample must contain one of these local cores, without enumerating the whole frontier |
| non-ear frontier rows `81` and `151` | `docs/bridge-lemma-frontier.md` and `docs/bootstrap-vertex-circle-overlay.md` isolate the two tight `n=9` non-ear rows and their `T12/F16` strict-cycle landing | A bootstrap/rich-class lemma that makes the needed T12 row relations genuinely available |
| source `81`, row `3` | `docs/bootstrap-t12-81-3-closure-target.md` and `docs/bootstrap-t12-81-3-rich-triple-contract.md` reduce the target to the connector pair `[0,1]` | Force a genuine center-`3` rich class containing `[0,1]`, or classify the label-`6` connector-avoiding escape |
| source `151`, row `6` | `docs/bootstrap-t12-151-6-outside-pair-connector-contract.md` splits endpoint-`8` supports from private-halo-only pair `[3,5]`; `docs/bootstrap-t12-151-6-outside-pair-escape-partition.md` shows the private-halo-only lane has `12` basic survivors before vertex-circle replay; `docs/bootstrap-t12-151-6-endpoint8-forcing-preflight.md` records that endpoint-`8` forcing is not ready from current evidence; `docs/bootstrap-t12-151-6-private-lane-core-catalog.md` shows every private-lane survivor has a row-`6` three-row strict-cycle core; `docs/bootstrap-t12-151-6-private-lane-strict-core-split.md` splits the `44` row-`6` three-row strict-cycle cores into `32` label-`8`-visible and `12` label-`8`-free occurrences; `docs/bootstrap-t12-151-6-label8-free-residual-targets.md` shows every label-`8`-free exact signature requires auxiliary witness label `4`; `docs/bootstrap-t12-151-6-label4-quotient-roles.md` shows label `4` reaches every residual strict cycle quotient class directly or through selected-distance equalities; `docs/bootstrap-t12-151-6-label4-transfer-paths.md` pins shortest selected-distance transfer paths from label-`4` pairs to cycle endpoint pairs; `docs/bootstrap-t12-151-6-label4-transfer-obligations.md` splits positive transfers into row-local equality obligations; `docs/bootstrap-t12-151-6-label4-transfer-length-components.md` collapses those obligations into six equal-length segment components, including the unique row-`6` cascade `D[0,6]=D[4,5]=D[5,6]`; `docs/bootstrap-t12-151-6-label4-transfer-component-feasibility.md` rejects component-alone impossibility by giving a strict cyclic arc witness for each component considered alone; `docs/bootstrap-t12-151-6-label4-support-hypothesis-ledger.md` pins the seven centered support requirements and shows the cascade needs center `5` with `[4,6]` plus center `6` with `[0,5]`, while no transfer requirement is exact pair `[3,5]`; `docs/bootstrap-t12-151-6-label4-cascade-row-criticality.md` shows the auxiliary-center-`5,8` cascade signatures need the full local row package `{5,6,8}` for the strict cycle; `docs/bootstrap-t12-151-6-label4-cascade-endpoint8-targets.md` shows any center-`8` rich class containing `[0,4,6]` keeps those cascade packages quotient-obstructed; `docs/bootstrap-t12-151-6-label4-center8-rich-triple-preflight.md` records that current support evidence has no center-`8` support requirement and does not force that rich triple; `docs/bootstrap-t12-151-6-label4-center8-source-crosswalk.md` records that the existing source-`151` row-`8` singleton packet does not supply any pair from `[0,4,6]`; `docs/bootstrap-t12-151-6-label4-center8-core-route.md` shows `8` of `9` center-`8` cores are target-compatible, but only `4` of `32` label-`8`-visible cores are visible and target-compatible, with `6` assignments still lacking a center-`8` target core; `docs/bootstrap-t12-151-6-label4-center8-residual-target-rows.md` splits those six assignments into four off-center `[0,4,6]` row cases and two target-sparse cases; `docs/bootstrap-t12-151-6-label4-center8-migration-support-crosswalk.md` shows `3` of `5` off-center rows have same-center support backing, but none supplies center-`8` migration | Force endpoint-`8` outside-pair support, prove center migration for support-backed off-center `[0,4,6]` rows, obstruct target-sparse assignments `0` and `11`, or add a genuine geometric source for the center-`8` rich triple plus the row-`5`/row-`6` cascade equalities |
| source `151`, rows `7` and `8` | `docs/bootstrap-t12-hard-strict-endpoints.md` isolates missing strict-edge endpoint sets | Supply the hard endpoint labels from genuine closure/support geometry, not fixed-row bookkeeping |
| block-6 fragile family | `docs/block6-fragile-vertex-circle-extension-audit.md` and `docs/bridge-negative-controls.md` record exact negative controls | A minimal/rich-class condition that rejects the family beyond fixed natural/block-preserving order slices |

## Recommended lemma contracts

### Contract A: exact local-template forcing

Statement shape:

```text
Under stated minimal/rich-support hypotheses, a counterexample contains one of
the T01--T12 selected-distance quotient local cores.
```

Useful evidence:

- `scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --summary-json`
- `scripts/check_relation_skeleton_local_lemma_crosswalk.py --check --assert-expected --summary-json`
- `scripts/check_n9_relation_skeleton_closed_descent_crosswalk.py --check --assert-expected --summary-json`

Required guardrails:

- Do not assume the review-pending 184-frontier brancher is already a theorem.
- State exact incidence, order, support-size, and richness hypotheses.
- Make clear whether the lemma forces a selected row, a rich class, or only a
  connector equality.

### Contract B: `81:3` connector forcing

Statement shape:

```text
In the bootstrap-core setting for the source-81 closure target, either center
3 has a genuine rich class containing witnesses 0 and 1, or a specified
connector-avoiding label-6 supply must occur before center 3 activates.
```

Useful evidence:

- `docs/bootstrap-t12-81-3-closure-target.md`
- `docs/bootstrap-t12-81-3-rich-triple-contract.md`
- `docs/bootstrap-t12-81-3-chain-closure-csp.md`
- `docs/bootstrap-t12-81-3-repeated-support-saturation-audit.md`
- `docs/closure-visibility-anti-activation-control.md`

Required guardrails:

- Closure exposure of the fixed selected row is not rich-class forcing.
- Full target-label visibility does not pin the fourth witness; see
  `docs/closure-activation-negative-controls.md`.
- Target-label visibility in a deletion closure is not the same as activation
  provenance by the target triple.
- The repeated-support saturation packet closes only the stored-prefix,
  same-center-disjoint repeated-support model.

### Contract C: endpoint-8 outside-pair forcing

Statement shape:

```text
For the source-151 row-6 outside-pair target, any genuine outside-pair support
compatible with the bootstrap/private-halo hypotheses includes endpoint 8.
```

Useful evidence:

- `docs/bootstrap-t12-151-6-outside-pair-connector-contract.md`
- `docs/bootstrap-t12-151-6-outside-pair-full-neighborhood-vertex-circle.md`
- `docs/bootstrap-t12-151-6-outside-pair-escape-partition.md`
- `docs/bootstrap-t12-151-6-endpoint8-forcing-preflight.md`
- `docs/bootstrap-t12-151-6-private-lane-core-catalog.md`
- `docs/bootstrap-t12-151-6-private-lane-strict-core-split.md`
- `docs/bootstrap-t12-151-6-label8-free-residual-targets.md`
- `docs/bootstrap-t12-151-6-label4-quotient-roles.md`
- `docs/bootstrap-t12-151-6-label4-transfer-paths.md`
- `docs/bootstrap-t12-151-6-label4-transfer-obligations.md`
- `docs/bootstrap-t12-151-6-label4-transfer-length-components.md`
- `docs/bootstrap-t12-151-6-label4-transfer-component-feasibility.md`
- `docs/bootstrap-t12-151-6-label4-support-hypothesis-ledger.md`
- `docs/bootstrap-t12-151-6-label4-cascade-row-criticality.md`
- `docs/bootstrap-t12-151-6-label4-cascade-endpoint8-targets.md`
- `docs/bootstrap-t12-151-6-label4-center8-rich-triple-preflight.md`
- `docs/bootstrap-t12-151-6-label4-center8-source-crosswalk.md`
- `docs/bootstrap-t12-151-6-label4-center8-core-route.md`
- `docs/bootstrap-t12-151-6-label4-center8-residual-target-rows.md`
- `docs/bootstrap-t12-relation-sufficient-rows.md`

Required guardrails:

- The fixed full-neighborhood vertex-circle packet kills selected-row
  neighborhoods, not support existence.
- The private-halo-only lane has basic-filter survivors, so it cannot be
  dismissed by incidence/crossing filters alone.
- The label-`4` cascade row-criticality packet shows that forcing only the
  row-`5`/row-`6` cascade equalities is not enough; the row-`8` strict endpoint
  row or a different genuine support-rich obstruction is still needed.
- The endpoint-target packet sharpens the sufficient row-`8` target to a
  center-`8` rich class containing `[0,4,6]`; it does not prove that such a
  rich class is forced by the bootstrap/private-halo hypotheses.
- The center-`8` rich-triple preflight records that the current support ledger
  has no center-`8` support requirement and no label-`8` support witness, so
  the new target still needs a genuine geometric forcing source.
- The center-`8` source crosswalk records that the existing source-`151`
  row-`8` singleton packet uses core `[1,2]` with supports `[5,7]` and cannot
  supply any pair from `[0,4,6]`; do not reuse it as the cascade source.
- The center-`8` core-route packet records that label-`8` visibility alone is
  still too weak: only `4` of `32` label-`8`-visible local cores are both
  visible and center-`8` target-compatible, and `6` private-lane assignments
  still have no center-`8` target core. The target is a target-compatible
  center-`8` local core, not arbitrary label-`8` visibility.
- The residual target-row packet records that four of those six residual
  assignments have `[0,4,6]` only off-center, while assignments `0` and `11`
  have no full target row in any residual strict core. Off-center rows are not
  center-`8` supply without a center-migration lemma.
- The target-sparse completion packet records that assignments `0` and `11`
  have no one-row repair: all `12` completions of target-pair rows to
  `[0,4,6]` fail basic filters before vertex-circle replay. This is not yet a
  proof that those assignments are impossible.
- The target-sparse two-row repair packet records that even after allowing one
  additional arbitrary non-completion row replacement, all `6624` repair
  candidates fail basic filters. This still does not prove an exact
  target-sparse obstruction.
- The target-sparse three-row repair packet records that even after allowing
  two additional arbitrary non-completion row replacements, all `1599696`
  depth-two repair candidates fail basic filters. This still does not prove
  assignments `0` and `11` impossible; the remaining target needs genuine
  support geometry, center migration, or a mechanism beyond two arbitrary
  extra row repairs.
- The target-sparse support-cone packet records that adding the cascade
  support equalities center `5` with `[4,6]` and center `6` with `[0,5]` gives
  no bounded one- or two-row Kalmanson/Altman cone certificate for the local
  target-pair or completion probes. Adding a center-`8` exact target row
  covers `27` of `30` endpoint-augmented probes, leaving exactly the
  assignment-`0` endpoint rows `[0,1,4,6]`, `[0,2,4,6]`, and `[0,4,6,7]`.
  The target-sparse full-cone miss packet probes those three quotients with
  arbitrary nonnegative weights over the same `255` natural-order
  Kalmanson/Altman strict rows; HiGHS reports both normalized LP screens
  infeasible, and the exact dual-certificate follow-up stores nonnegative
  integer potentials certifying that the natural-order row family cannot
  produce either normalized screen. The alternate-order Kalmanson follow-up
  kills the same three quotients in the fixed cyclic order
  `[0,1,2,3,4,5,7,8,6]` by exact zero-sum certificates. The
  order-sensitivity crosswalk records that these two exact packets do not
  form a no-new-ingredient all-order route. The next target is useful
  cyclic-order forcing, a stronger row family tied to geometry, or a genuine
  endpoint/source geometry lemma, not another solver-only replay of the same
  cone.
- The private-halo-only pair `[3,5]` is the named escape and must be excluded
  or explicitly realized as an escape mechanism.

### Contract D: hard strict-endpoint forcing

Statement shape:

```text
For the source-151 row-7/row-8 hard strict-endpoint targets, the missing
strict-edge endpoint labels are forced by genuine deletion-closure or singleton
support geometry.
```

Useful evidence:

- `docs/bootstrap-t12-hard-strict-endpoints.md`
- `docs/bootstrap-t12-open-connector-pair.md`
- `docs/bootstrap-t12-singleton-full-neighborhood-crosswalk.md`
- `docs/bootstrap-t12-anti-activation-negative-control.md`

Required guardrails:

- Singleton support does not automatically supply both connector endpoints.
- A full selected-row closure exposure can still switch the target fourth
  witness.
- Another selected-row neighborhood widening over the same packets is low
  leverage unless it proves support existence or a new necessary condition.

### Contract E: block-6 negative-control exclusion

Statement shape:

```text
Every fragile-cover system from a minimal counterexample satisfies an extra
minimal/rich-class condition that the block-6 negative-control family fails.
```

Useful evidence:

- `docs/minimal-fragile-cover-bridge.md`
- `docs/bridge-negative-controls.md`
- `docs/block6-fragile-vertex-circle-extension-audit.md`
- `docs/block6-fragile-sixth-row-survivor-catalog.md`

Required guardrails:

- Fragile-cover hypergraph constraints, full-row extension, row-circle
  Ptolemy product-cancellation, and local row-depth closure each have exact
  negative controls.
- Vertex-circle pruning alone has the reversed-second-block clean-row escape;
  those 16 rows need Kalmanson certificates in their fixed orders.
- A useful condition should either handle arbitrary cyclic orders/all
  full-row extensions or explain why minimal/rich-class geometry avoids that
  quantifier.

## Low-leverage moves to avoid

- Repeating selected-row neighborhood widenings around `81:3`, `81:8`,
  `151:5`, `151:6`, or `151:8` without a support-existence or row-forcing
  theorem.
- Treating closure exposure as selected-row availability.
- Treating a fixed selected-row obstruction as an all-rich-class or
  all-cyclic-order obstruction.
- Treating vertex-circle cleanliness of an abstract row system as Euclidean
  realizability or counterexample evidence.
- Using the block-6 fragile rows to refute the problem; they are guardrails
  against overstrong bridge claims, not candidates.

## Acceptance standard for the next bridge PR

A bridge PR should be considered high leverage if it does at least one of:

- states and proves a new necessary condition for minimal counterexamples;
- turns one of the contracts above into a checked exact lemma;
- rejects a named negative control under clearly stated minimal/rich-class
  hypotheses;
- replaces an enumeration layer with a smaller reusable local lemma and a
  replayable certificate.

It should not claim a proof of Erdos Problem #97, `n=9`, `n=10`, or an official
status change unless the full source-of-truth review standard is separately
met.

## Smoke commands

Use these commands to replay the current bridge-target evidence:

```bash
python scripts/check_bridge_lemma_frontier.py --check --assert-expected --json
python scripts/check_bootstrap_core_bridge.py --assert-expected
python scripts/check_bootstrap_t12_bridge_target_map.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --summary-json
python scripts/check_bootstrap_t12_81_3_repeated_support_saturation_audit.py --check --assert-expected --summary-json
python scripts/check_bootstrap_t12_singleton_full_neighborhood_crosswalk.py --check --assert-expected --json
python scripts/check_block6_fragile_sixth_row_survivors.py --assert-expected --json
python scripts/check_block6_reversed_block_clean_kalmanson.py --check --assert-expected --json
```
