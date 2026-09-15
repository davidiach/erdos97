# STATE.md - Erdos Problem #97 working state

Status: `EXTERNAL_NEGATIVE_RESOLUTION`, recorded 14 September 2026.

Kruer, Kohlmeyer, and Price's *Unit distances in convex polygons*, released on
13 September 2026, supplies the external negative result. The construction has
at least four unit-distance neighbours at every vertex in strictly convex
position. See the [source-pinned record](docs/external-resolution-2026-09-14.md)
and [external metadata](metadata/external-resolution-2026-09-14.json).

Local contribution boundary: no general proof and no counterexample are claimed
as an original or independently replayed result of this repository. Existing
local claim scopes and pending reviews remain unchanged.

The [canonical metadata](metadata/erdos97.yaml) retains the website label
falsifiable/open last successfully checked on 2026-07-09. The 2026-09-14 retry
failed; neither a current website label nor a new successful check is asserted.
That dated website record must not be read as the current mathematical outcome.

## Target

The original unrestricted search is retired. Preserve this research record;
do not launch further affirmative-proof attempts from historical task lists.
Any further audit or smaller-explicit-example project needs an explicit new scope.

The original question allowed different radii and witnesses at different
vertices. The external result uses distance one at every vertex. Numerical
near-equalities remain insufficient for a new explicit construction.

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

The following table is retained as the **pre-resolution local research map**,
not an automatic work queue. Independent external-result reproduction and
preservation of existing evidence are distinct from continuing these old routes.

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
