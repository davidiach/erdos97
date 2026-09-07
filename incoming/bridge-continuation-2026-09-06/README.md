# Bridge continuation: preserved findings and publication audit

Research: 6 September 2026. Publication: 7 September 2026.

**Review-pending restricted research, not a proof or counterexample to Erdős
Problem #97.** This packet publishes the four previously delivered research
packets, their complete source and evidence, and a scoped audit of the final
conversation's exploratory statements. No accepted result, finite bound,
source-of-truth status, or existing certificate is promoted.

## Findings and exact scope

| Preserved packet | Written result or control | Essential limitation |
|---|---|---|
| [Convex chains and conics](snapshots/chain-conic-obstructions-2026-09-06/README.md) | Two-good vertices on convex/concave graphs and ellipses; conic-plus-one and three-consecutive-turn obstructions | No extraction of these shapes from arbitrary four-rich polygons |
| [One-closer bridge](snapshots/rank-one-bridge-2026-09-06/README.md) | An assigned-radius system with at most one strictly closer point cannot be four-rich everywhere; sharp minimum-layer deficiency | Does not treat radii with two or more closer points |
| [Two-closer layer escape](snapshots/rank-two-layer-escape-2026-09-06/README.md) | Fixed-radius edge bound `e_r <= 2n-3-p-2c`; rich minimum layer exports at least four higher-radius targets, with the stated incidence and radius-band bounds | Arbitrary variable-radius two-closer systems remain unresolved; exact return control defeats unconditional layer deletion |
| [Closure audit](snapshots/bridge-closure-audit-2026-09-06/README.md) | Conditional low-Gabriel-degree radius descent and exact failures of global Gabriel counting, rich-ear deletion, and a three-witness middle-edge forest shortcut | Descent need not iterate; controls are not globally four-rich |

Each packet contains its complete proof note, hypotheses, failure controls,
original reports, and verifier. These are paper-proof candidates and exact
regression controls, not independent mathematical review or formalization.
The fixed-radius Gabriel argument in the last packet simplifies an earlier
bound; it is not a new variable-radius theorem.

## Correction to the final nine-orbit discussion

The concrete nine-orbit table quoted in the final conversation **passes the
older selected filters but is rejected by the existing right-angle containment
rule**. It must not be presented as a live Euclidean-realizability candidate.

[Exact fixed-pattern report](nine-orbit-candidate.json) and
[replay source](check_candidate.py) record 351 physical center-pair checks,
35,100 strict ordinary-distance Kalmanson inequalities checked through the
specified cancellation/domination filters, and six containment certificates.
This is not full Kalmanson-cone feasibility, full chord-angle feasibility, a
new nine-orbit exhaustive search, or an exclusion of every nine-orbit system.

One certificate, with physical label `i + 9*k` meaning `omega^k*z_i`, is

```text
[center, base, other witness, right endpoint, right endpoint]
[7,      15,   16,            18,             0]
```

At center 7, vertices 15 and 16 are equidistant: 15 is the selected gain-one
witness from orbit 6, and 16 is an orbit mate. Their isosceles triangle has an
acute angle at 15. The selected arrow from orbit 6 to orbit 0, rotated once,
forces the angle `(18,15,0)` to be a right angle. In the boundary fan at 15,
the order is `16,18,0,7`, so that right angle is strictly inside the acute
base angle `(16,15,7)`, a contradiction. The other certificates are stored
with their physical labels; rotations and a second witness account for six.

The repository's existing
[containment proof](../c3-own-side-eight-orbits-2026-09-05/README.md) and
[certificate verifier](../c3-own-side-eight-orbits-2026-09-05/c3_eight_check.py)
are reused, not claimed as new. `replay.py --check --require-primary` additionally
checks every stored certificate through that existing verifier at its pinned
Git blob. Both replay implementations are from the same research/publication
workflow, not external independent review.

[Exploration inventory](EXPLORATION.md) captures the other final statements,
including where source logs are absent and where findings already live on
`main`. It does not manufacture absent run records.

## Preservation and provenance

All **41 original packet files** are retained byte-for-byte in `snapshots/`,
including original manifests, source code, reports, and test output. The
[publication provenance](provenance.json) binds those files to the SHA-256
hashes of the four delivered ZIPs. It does not replace the original manifests.
The separate rank-two delivery report is also retained as
[historical delivery validation](original-delivery-validation.json).

Statements such as "no PR was opened" or `repository_write_performed: false`
in the snapshots describe their preparation sessions. They are intentionally
not rewritten to describe this publication. The present README and PR body
record the later import and fresh checks.

The previously merged
[unbounded six-exception family](../unbounded-six-exception-family-2026-09-06/README.md),
[66-point construction](../../docs/orbit66-exact-partial-construction.md),
and [27-point nonconvex product control](../../docs/c3-product-27-nonconvex-control.md)
are linked rather than duplicated. PR #940 already imported the unbounded
family; its six good vertices remain exceptions at every finite length.

## Reproduce

Use Python 3.10 or newer. Only the conic packet's full symbolic checks need
SymPy; the archived run and publication replay use **SymPy 1.14.0**, already
compatible with the repository's development dependencies. Other packet
checks use the standard library. Pytest is needed for the integration tests.

From this directory:

```sh
python replay.py --manifest-only
python replay.py --check --require-primary --output /tmp/bridge-replay.json
python -m pytest -q -o addopts='' test_publication.py
```

For an isolated export without the sibling repository checker, omit
`--require-primary`; its absence is reported explicitly. All other checks
still run. Individual packet replays are available:

```sh
python replay.py --check --packet chain-conic
python replay.py --check --packet rank-one
python replay.py --check --packet rank-two
python replay.py --check --packet closure-audit
python replay.py --candidate-only --require-primary
```

The harness copies each snapshot into a temporary directory, regenerates its
reports, requires byte identity, runs the archived unit tests in separate
processes, and rechecks all original source hashes afterward. It never writes
generated data into the committed snapshots. The unchanged original commands
also remain usable from each individual snapshot directory.

The historical modules share names such as `verify`, `fixtures`, and
`test_bridge`. Scoped collection isolation prevents Python module collisions;
`test_publication.py` still executes **all 101 original unit tests**. The
scoped Ruff configuration excludes only the immutable historical inputs;
the maintained publication harness is linted normally. Full report replays
are artifact-marked integration tests, and original unit suites run in the
ordinary fast collection. No root lint or test settings are changed.

## Publication validation and limitations

[Fresh local publication validation](publication-validation.json) records all
four packet verifiers, all **101 archived unit tests** (33 + 51 + 17), the
rank-two independent-representation control oracle, and an exact match for
the conic report. The full report-regeneration harness separately compares
all generated report bytes. Finite regression counts remain exactly those
in the archived packets; repeated executions are not additional independent
proofs.

A complete local checkout was unavailable: attempted GitHub git access failed
DNS resolution. Consequently repository-wide `make verify-fast` and
`make verify-artifacts` were not run locally. Focused publication checks are
not those repository-wide gates. Hosted publication validation, ordinary PR
CI, and independent mathematical review are separate evidence categories.

**Remaining obligations:** universal four-richness has not been shown
impossible even for arbitrary varying radii with at most two closer points;
and arbitrary counterexamples have not been reduced to that rank regime.
None of the archived controls refutes a lemma whose missing premise is
richness at every original vertex. The candidate correction above is only
for the displayed fixed-order nine-orbit pattern.
