# Erdős #97 — parallel-parabola closure, metric compatibility, and clustered geometry

Research packet, 9 September 2026.

**The unrestricted problem is not solved here.** These are written theorems
pending independent mathematical review, exact controls, and bounded research
records. There is no accepted-bound promotion, global planar counterexample,
Lean formalization, or repository write.

## A complete all-size exclusion of the recorded parabola route

The repository's opposite-chain two-parabola closure scaffold is impossible
at every finite size, with arbitrary real parameters and center-dependent
radii, even without assuming convexity. Its square-sum identity makes the
potential `g(t)=t^2+c/4` average to `-g(t)` on each row. At a maximum of `|g|`,
four distinct witnesses would have to have the same square, which is impossible.

More generally, a finite deterministic cycle of parallel parabolic carriers
cannot support four equidistant witnesses at every point. Vieta gives a
constant height drift for each carrier; a cycle either has nonzero drift,
contradicting a finite extremum, or zero drift, forcing four witnesses onto
one horizontal level of a parabola. Read **`parabola/proof.md`** for both proofs.
Mixed-carrier rows and vertex-dependent target-carrier choices are not excluded.

## A complete all-size obstruction to a metric/local-star relaxation

For every k>=4 there exists a finite rational cyclically ordered metric in
which every vertex has at least k unit-distance witnesses, all triangle and
Kalmanson inequalities are strict, all Ptolemy inequalities hold, and distance
fibers at two distinct centers overlap in at most one label. **Every vertex
and its entire rich neighborhood admit an exact strictly convex planar
realization in the induced order.** Yet the whole metric has no planar
Euclidean realization. Nonunit distances within each row are all distinct.

The separate local coordinate charts are not claimed to fit together. Thus
one-center realizability plus these metric/order restrictions cannot replace
global Euclidean compatibility. Proofs using additional relations between
centers are not excluded.

Read **`star_metric_theorem.md`** for the full arbitrary-k proof. The explicit
138-label control has 784 directed unit incidences. Both a primary checker and
a separate coordinate/matrix oracle verify its rich stars. An exhaustive
integer checker verifies every triangle and quadruple. Ptolemy equalities
forced by witness circles are preserved, not replaced by weak approximate
identities.

`proofs.md` also preserves the first, weaker metric control, which has *all*
Ptolemy inequalities strict but does not realize the witness-circle stars.
Both controls admit an exact positive scalar turn vector satisfying the
repository's stated equal-distance interval-turn inequalities. Those scalar
values are not asserted to match all actual geometric angles; the stronger
proof note gives an explicit incompatibility example.

## A separate theorem about actual convex polygons

An all-rich strictly convex polygon with at most **16** vertices cannot have
its vertices partitioned into three consecutive nonempty blocks so that every
vertex can choose four equal-distance witnesses outside its own block.

The proof uses a source-row packing bound, saturation of the target-pair
budget, and an impossible five-cycle inversion graph. Radii are unrestricted
and there is no coordinate symmetry. This is **not an exclusion of arbitrary
polygons through sixteen vertices**: the external-witness condition is an
extra hypothesis.

## Continued search and inherited frontier

Source/target median rules strengthen the fixed tripled-Danzer search. Five
complete assignments surviving those rules are rejected by 54 exact Kalmanson
certificates. A subsequent solver timeout is inconclusive; the full family is
not excluded.

The preceding three exact research packets are retained and replayed. The
fixed nine-point seed still requires at least two internally supported new
vertices in any all-rich extension. This run does not exclude the two-vertex
escape, move that seed to an all-rich configuration, or establish a universal
radius-descent theorem.

`frontier.md` states the remaining gap. `EXPLORATION.md` gives search scope,
failures, and provenance limits. `validation.json` consolidates the final Python checks with the immediately
preceding full exact-metric and inherited replay, while recording the unchanged
mathematical source and input hashes. The component reports retain the actual
commands, code versions, and execution times. `validation_before_turn_extension.json` is an earlier successful validation of
the first metric version. `validation_full_before_parabola.json` records the
subsequent complete metric/star/inherited replay before the final standalone
parabola addition. Neither historical report is relabelled as a later run.

## Reproduction

All exact Python checks use the standard library:

```sh
python grid_metric.py --check
python grid_oracle.py
python circle_star_metric.py --check
python circle_star_oracle.py
python turn_control.py --check
python audit_medians.py --check
python -m unittest -v test_final_push.py test_star_extension.py
(cd parabola && python verify.py --check && python -m unittest -v test_parabola.py)
```

The two exhaustive metric audits require C++17 and GMP development libraries.
The driver compiles them into a temporary directory, runs both complete
checks, and compares their generated reports byte-for-byte:

```sh
python replay.py --full-metric --output fresh_validation.json
```

To replay the preceding packet and all its inherited exact tests too:

```sh
python replay.py --full-metric --with-inherited --output fresh_full_validation.json
```

The archived input ZIP is SHA-256 pinned and extracted only into temporary
copies. Its original source files are not edited. Numerical discovery scripts
additionally use NumPy/SciPy; their failures never become exclusion claims.

There are **66 new tests** (54 core/star tests plus 12 parabola tests) and
**101 inherited tests**. Repeated executions and
separate implementations created in this research workflow are not external
independent review. No repository-wide CI was run: the available GitHub reads
confirmed the baseline, but direct git access failed and no full checkout was
available. No PR was opened.
