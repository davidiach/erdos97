# External n=9 reproduction and next research target

Status: external reproducibility audit and proposed research direction; no
accepted-result transition. This repository still accepts only its existing
repo-local `n <= 8` result. Its general `n=9` candidate remains review-pending.

## Audited snapshots

- External: Adam McKenna's
  [erdos-97-96-formalization at d6b8e128](https://github.com/mysticflounder/erdos-97-96-formalization/tree/d6b8e128af554eb430d060a31f26f863cea97c14).
- Local comparison: [982e5a36](https://github.com/davidiach/erdos97/tree/982e5a363be60cfd805db5ae40d4b258e53f9dfb).
- Evidence: [audit record](../reports/external-n9-audit-2026-09-10/audit.json),
  [source manifest](../reports/external-n9-audit-2026-09-10/source-manifest.json),
  and [independent statement probe](../reports/external-n9-audit-2026-09-10/N9Audit.lean).

The external source pins Lean **4.33.1** and mathlib commit
`0df444a360eaa60ab8c11dca51a86af692955474`. Its
[comparator documentation](https://github.com/mysticflounder/erdos-97-96-formalization/blob/d6b8e128af554eb430d060a31f26f863cea97c14/comparator/README.md)
also contains older Lean 4.27 verification records. Those historical records
do not by themselves verify this snapshot.

## Reproduction result

**Passed.** The current `SmallCardinality` target built successfully (8,983
Lake jobs), and the independent statement probe elaborated successfully. All
five inspected declarations had exactly `propext`, `Classical.choice`, and
`Quot.sound` in their axiom closures: no `sorryAx` and no additional
computational axiom. The [axiom output](../reports/external-n9-audit-2026-09-10/n9-axioms.log)
and [complete compressed build log](../reports/external-n9-audit-2026-09-10/n9-build.log.gz)
are retained.

The checked statement concerns every nonempty finite subset of the Euclidean
plane with at most nine points, subject to convex independence: no point is
in the convex hull of the others. It rules out the condition that **every**
point has at least four points of the set at a common positive distance.
Positive distance excludes the center itself. The probe writes these
hypotheses out directly, rather than relying on the external project's names
for the problem statement.

The audit fetched 87 external project Lean modules in the import closure of
`Erdos9796Proof.P97.SmallCardinality`, together with the three unchanged Lake
configuration files. Every fetched file was checked against the pinned Git
blob ID; the manifest also records SHA-256 hashes. All 87 project modules were
built from source. Pinned upstream dependency checkouts and official mathlib
cache artifacts were used. This is not a rebuild of every dependency from
source, a full external repository build, or a second-kernel/nanoda audit.

The official macOS arm64 Lean archive was verified against its GitHub release
digest. No system toolchain or original research checkout was changed.
The toolchain and dependency pins, commands, file hashes, exit codes, and
observed axiom lists are recorded in the audit JSON.

Successful elaboration and an axiom audit establish this specific formal
reproduction result. They do not constitute independent human review of the
mathematical definitions or authorize a status transition in this repository.
The general Problem #97 remains outside this audit; no general proof or
counterexample is claimed. The official problem page was not successfully
refreshed during this audit.

## Reproduce with a complete checkout

Use a separate directory with the official Lean 4.33.1 toolchain available.
Starting from this repository's root, copy the probe into a fresh external
checkout and run:

```bash
git clone --no-checkout https://github.com/mysticflounder/erdos-97-96-formalization.git /tmp/external-erdos97-audit
git -C /tmp/external-erdos97-audit checkout --detach d6b8e128af554eb430d060a31f26f863cea97c14
cp reports/external-n9-audit-2026-09-10/N9Audit.lean /tmp/external-erdos97-audit/lean/N9Audit.lean
cd /tmp/external-erdos97-audit/lean
lake env lean --version
lake exe cache get
lake build Erdos9796Proof.P97.SmallCardinality
lake env lean N9Audit.lean
```

Use a fresh destination, confirm version 4.33.1, and preserve the pinned
manifest rather than updating packages. Each command must exit zero. Check
every printed axiom list, including the final independently written theorem;
the allowed set is `propext`, `Classical.choice`, and `Quot.sound`. A successful
process exit alone is insufficient because Lean permits admitted declarations.
This full-checkout replay recipe was not the acquisition method used in the
recorded run: that run fetched and hash-verified only the required source
closure. It used the same original Lake files and proof target.

## Comparison that changes our priorities

| Question | External snapshot | This repository | Consequence |
| --- | --- | --- | --- |
| General problem | Open geometric branches remain in the source | No general proof or counterexample claimed | Neither project supplies a general solution here |
| Finite formal result | `SmallCardinality` supplies an unrestricted `n <= 9` statement; reproduction result above | Accepted repo-local `n <= 8`; general `n=9` candidate pending review | External work is ahead on this specific formal milestone |
| Our finite evidence | Different formal proof organization | Fresh `make verify-n9-candidate` passed; 184 regenerated frontier cases all have Kalmanson obstructions | Useful independent-route evidence, not an automatic promotion |
| Local geometric tools | Existing Kalmanson equality schemas and radius-order reversal lemmas | Hinge compression, full-rich-class deletion profiles, midpoint/radius analysis | Merely adding another terminal inequality is unlikely to address the common bottleneck |
| Productive next step | A concrete surviving deletion branch is exposed | Our methods can help extract a small necessary geometric configuration | Prove a forcing implication with all original hypotheses retained |

The local candidate command skipped its Lean pilot compilation because `lake`
was absent from that command's PATH. Its Python/exact checks passed; it is not
being reported as a fresh local Lean build. The external reproduction uses a
separately installed, explicitly selected toolchain. Native-decide `n=10/11`
claims, comparator theorem totals, and the full general theorem's axiom closure
were not reproduced in this task.

## One bounded target: the B1 card-six blocker-between branch

At the pinned external source,
[`false_of_b1CanonicalAdjacentClosedResidual`](https://github.com/mysticflounder/erdos-97-96-formalization/blob/d6b8e128af554eb430d060a31f26f863cea97c14/lean/Erdos9796Proof/P97/ATail/FrontierLiveClosure/TwoDeletionCollision.lean#L1914)
still has an admitted body. It receives three alternatives: an escape source,
a five-point physical class, or a six-point physical class with both canonical
deletions in the strict second cap and the retained blocker-between order.
The six-point count is a **distance-class size**, not the polygon size.

The proposed subgoal is to exclude the last alternative in the producer's
no-escape branch. Preserve all the ambient types and arguments from
[`B1CardSixCanonicalBlockerBetweenResidual`](https://github.com/mysticflounder/erdos-97-96-formalization/blob/d6b8e128af554eb430d060a31f26f863cea97c14/lean/Erdos9796Proof/P97/ATail/FrontierLiveClosure/B1CardSixCanonicalAdjacent.lean#L213):

```text
For every original D, S, radius, H, F, C, E:
  B1PhysicalClassFiveSixNormalForm C
  and no B1EscapeSourceContext C
  and B1CardSixCanonicalBlockerBetweenResidual C E
  imply False.
```

This is an **unproved proposed subgoal**, not a theorem added by this audit.
The endpoint includes the original good-deletion witness, an omitted peer,
distinct source centers, class/cap memberships, and a boundary-order condition.
The order is about indices on the retained polygon boundary; it must not be
replaced by Euclidean collinearity or arbitrary cyclic relabeling.

An important integration detail: `B1CanonicalAdjacentClosedResidual` does not
store the producer's no-escape proof. A result needing that proof must be used
inside `b1_canonicalAdjacentClosedResidual_of_normalForm`, before the producer
forgets it, or through an explicitly strengthened interface. It cannot simply
be invoked on the weaker downstream residual. Closing this arm would leave
the escape-source and card-five alternatives, as well as other global branches,
unresolved.

### Why our methods fit, and what has to be new

The external adjacent-case proof already combines at least four physical-class
points in the strict second cap, at most one in the first-apex fiber, and at
most one remaining noncanonical source. When both canonical deletions are
interior, the crude bound permits equality: `4 <= 1 + 2 + 1`. Counting alone
therefore stops. The no-escape hypothesis and the omitted-peer/actual-blocker
data provide concrete geometric information to inspect at this equality case.

Our [equilateral-hinge note](kalmanson-equilateral-hinge.md) gives a compact
contradiction once three suitable equal-distance witness pairs occur in the
required order. Our [two-deletion profile](minimal-two-deletion-profile.md)
and [critical-radius midpoint note](fragile-critical-radius-midpoint.md) help
organize the actual rich classes and shared witnesses. Their hypotheses must
be mapped explicitly; none currently proves this external branch impossible.
The `n=9` exhaustive hinge-forcing result cannot be extrapolated to arbitrary
polygon sizes or to this six-point class.

The external project already has
[Kalmanson equality schemas](https://github.com/mysticflounder/erdos-97-96-formalization/blob/d6b8e128af554eb430d060a31f26f863cea97c14/lean/Erdos9796Proof/P97/ATail/KalmansonThreeEqualitySchemas.lean)
and [radius-order reversals](https://github.com/mysticflounder/erdos-97-96-formalization/blob/d6b8e128af554eb430d060a31f26f863cea97c14/lean/Erdos9796Proof/P97/ATail/KalmansonRadiusOrderReversal.lean).
The proposed contribution is a proof that the retained B1 geometry forces a
forbidden configuration, not a claim of novelty for those inequalities.

### Next experiment and acceptance gate

1. Extract the saturated class/cap roles and every allowed vertex/center alias
   from the original producer. Retain full rich classes, actual blocker
   provenance, distinctness, and the boundary order.
2. Run exact incidence/order preflight, then test whether those necessary
   constraints force a hinge, another existing Kalmanson obstruction, or an
   incompatible radius order. A feasible abstract pattern is a limitation of
   that abstraction, not a Euclidean counterexample.
3. If a contradiction is found, produce a small exact certificate and prove
   the extraction from the original geometry. If the abstraction survives,
   record a concrete surviving pattern and the missing geometric constraint
   before expanding search.
4. Formalize the successful implication under the original hypotheses and
   audit its transitive axioms. Require an independent review of the geometric
   extraction and exact call-site integration before claiming a branch closed.

The frontier comparison is source inspection, not a build of the external
B1 modules. The external obligation registry records an older source head and
still names the broader five/six consumer; the current source dispatches that
consumer to the narrower admitted declaration above. Do not treat the old
registry's hole count as a fresh inventory.

## Decision

Prioritize the existing independent review of our finite candidate and a
small, necessary-configuration lemma for this explicit surviving branch.
Retain attribution to the external implementation. This audit does not supply
evidence of copying or justify an accusation. No message to its author was
sent, and no external repository was modified.
