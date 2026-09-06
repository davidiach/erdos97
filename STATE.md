# STATE.md - Erdos Problem #97 working state

Status: no general proof and no counterexample are claimed.
Official/global status: falsifiable/open, as recorded in
[canonical metadata](metadata/erdos97.yaml). This dashboard does not recheck
or update the official page.

## Target

Find, or rule out, a strictly convex polygon where each vertex has four other
vertices at one common distance. The radius and selected witnesses may differ
between vertices. Numerical near-equalities are not counterexamples.

## Strongest proved state

The repo-local elementary geometric theorem rules out bad strictly convex
polygons for `n <= 8`. The selected-witness computation corroborates `n <= 8`
in a repo-local, machine-checked finite-case sense. Independent external review
remains recommended before paper-style citation and is not claimed.

The equilateral sub-case of `n=9` is also a restricted repo-local theorem.
Equal sides are an extra hypothesis; this does not settle general `n=9`.

- [Claims and proof qualifications](docs/claims.md)
- [Octagon proof trail](docs/n8-proof-trail.md)
- [Equilateral nonagon](docs/n9-equilateral-chord-obstruction.md)
- [Complete results ledger](RESULTS.md)

## Active review and research

| Area | Current boundary | Next useful work |
|---|---|---|
| `n <= 8` | Accepted locally; external review encouraged | Review the elementary proof and independent certificate trail |
| General `n=9` | Finite-case candidate remains review-pending | Complete independent reduction, geometry, replay, and written-review obligations |
| `n=10` | Singleton-slice finite-case draft remains review-pending | Audit the draft's input coverage and independent replay |
| Radius descent and C3 packets | Restricted incoming research, review-pending | Check hypotheses and geometric translation before broader claims |
| Bootstrap / fragile-cover bridge | Open geometric forcing obligations | Find necessary geometry that excludes surviving abstract controls |
| Numerical search | Diagnostics and exactification targets | Require exact preflight and exact evidence for any stronger claim |

- [Review priorities](docs/review-priorities.md) and [task backlog](docs/codex-backlog.md)
- [Finite-case entry points](docs/topics/finite-cases.md)
- [Bridge entry points](docs/topics/bridges.md)
- [Constructions and restricted families](docs/topics/constructions.md)
- [Incoming packet inventory](incoming/README.md)

## New exact fixed-pattern obstructions

`C19_skew` and `C13_sidon_1_2_4_10` have exact obstructions across all cyclic
orders of those fixed selected-witness patterns. They do not settle arbitrary
patterns or the general problem. [Kalmanson map](docs/topics/kalmanson.md).

## Two-orbit family obstruction and free-pattern search (2026-06-09)

See the [retained detailed record](docs/research-state-detail-2026-09-06.md#two-orbit-family-obstruction-and-free-pattern-search-2026-06-09)
and the [restricted-family map](docs/topics/constructions.md).

## Doubled-Danzer 18-gon equivariant route (closed at this base family)

[Failed-approach record](docs/danzer18-doubling-failed-approach.md).
The conclusion is restricted to its stated route and base family.

## Best saved near-miss

The historical `B12_3x4_danzer_lift` numerical artifact is retained as failed-route
provenance. Its fixed selected pattern is exactly killed. It is not a
counterexample. [Numerical provenance](docs/research-state-detail-2026-09-06.md#best-saved-near-miss).

## Top remaining live / unresolved patterns

Use the [candidate-pattern catalogue](docs/candidate-patterns.md) and exact
preflight; names and old numerical reports do not establish viability.

## Numerical status: C13 Sidon-type circulant

Its numerical plateau is historical diagnostic evidence only. The fixed
abstract C13 pattern has an exact all-cyclic-order obstruction.
[Recorded numerical history](docs/research-state-detail-2026-09-06.md#numerical-status-c13-sidon-type-circulant).

## Top killed approaches

[Failed ideas](docs/failed-ideas.md) and the
[historical research log index](reports/research-log-index.md) preserve negative
results and scope limits so they can be checked before restarting a route.

## Exactification frontier

[Verification contract](docs/verification-contract.md) and
[exactification plan](docs/exactification-plan.md). Any stronger accepted result
must follow the [reviewed transition contract](docs/status-transitions.md).

## Open literature questions

[Literature risk](docs/literature-risk.md) and
[reference workflow](references/README.md). Dated metadata is a recorded check,
not a claim that external sources have been refreshed today.

## Navigation and maintenance

[Documentation map](docs/index.md), [complete inventory](docs/inventory.md),
and [contributor workflow](CONTRIBUTING.md). Detailed state prose from before
this dashboard cleanup remains in the
[dated snapshot](docs/research-state-detail-2026-09-06.md).
