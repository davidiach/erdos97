# Erdos Problem #97 research log

![tests](https://github.com/davidiach/erdos97/actions/workflows/tests.yml/badge.svg)

This repository is a public research log and reproducibility workspace for
Erdos Problem #97. It is intentionally not presented as a solved-proof
repository.

## Status at a glance

- Official/global status: **falsifiable/open**.
- No general proof and no counterexample are claimed.
- Strongest local result: an elementary geometric theorem rules out bad
  strictly convex polygons with `n <= 8`; the selected-witness pipeline gives
  independent repo-local, machine-checked finite-case corroboration.
- The geometric proof was line-by-line rederived in the 2026-07-09 repository
  audit. Independent external review is still recommended before paper-style
  citation, and is not claimed here.
- Review-pending `n=9` and draft `n=10` artifacts are recorded for audit, but
  they are not promoted to the source-of-truth strongest local result.
- Canonical status metadata lives in
  [`metadata/erdos97.yaml`](metadata/erdos97.yaml).

## The problem

Given a strictly convex polygon, look at one vertex `v` and ask how many other
vertices can be the same distance from `v`. Erdos Problem #97 asks whether
every convex polygon has at least one vertex for which no distance occurs four
times.

Equivalently: can there be a strictly convex polygon in which **every** vertex
has four other vertices on some circle centered at that vertex?

In the selected-witness language used throughout this repo, a counterexample
would consist of:

```text
n >= 5
strictly convex points p_0,...,p_{n-1}
4-sets S_i subset {0,...,n-1} \ {i}
```

such that, for every center `i`, all squared distances

```text
|p_i - p_j|^2,  j in S_i
```

are equal. The radius may depend on `i`, the selected witness set may depend on
`i`, and the directed incidence graph need not be symmetric.

## Where to start

| If you want... | Read... |
| --- | --- |
| the short working dashboard | [`STATE.md`](STATE.md) |
| the compact results ledger | [`RESULTS.md`](RESULTS.md) |
| the proof-facing claims and caveats | [`docs/claims.md`](docs/claims.md) |
| the full documentation map | [`docs/index.md`](docs/index.md) |
| independent audit instructions | [`docs/reviewer-guide.md`](docs/reviewer-guide.md) |
| current review priorities | [`docs/review-priorities.md`](docs/review-priorities.md) |
| Codex-ready task backlog | [`docs/codex-backlog.md`](docs/codex-backlog.md) |
| the long-form synthesis | [`docs/canonical-synthesis.md`](docs/canonical-synthesis.md) |
| upstream/public status alignment | [`docs/upstream-alignment.md`](docs/upstream-alignment.md) |
| provenance and claim-history notes | [`docs/public-provenance.md`](docs/public-provenance.md), [`CHANGELOG.md`](CHANGELOG.md) |

The live GitHub issue list is here:
[github.com/davidiach/erdos97/issues](https://github.com/davidiach/erdos97/issues).

## What is currently recorded

### Local small cases

The elementary proof in
[`docs/n8-geometric-proof.md`](docs/n8-geometric-proof.md) rules out bad
strictly convex polygons with `n <= 8`: a base-apex count handles `n <= 7`,
and equality for an octagon forces too many exterior turns of size `2*pi/3`.
The selected-witness incidence pipeline independently corroborates `n <= 8`
in the repo-local, machine-checked finite-case sense.

- `n <= 7`: incidence counting and the crossing/bisection lemma rule out the
  cases. The repo also keeps a reproducible `n=7` Fano enumeration because it
  is structurally useful; see
  [`docs/n7-fano-enumeration.md`](docs/n7-fano-enumeration.md).
- `n=8`: the incidence enumerator reduces all necessary survivors to 15
  canonical classes, and exact cyclic-order / perpendicular-bisector /
  equal-distance checks leave no strictly convex realization. See
  [`docs/n8-incidence-enumeration.md`](docs/n8-incidence-enumeration.md) and
  [`docs/n8-exact-survivors.md`](docs/n8-exact-survivors.md).

An interactive visualization of the octagon endgame is available at
[`docs/octagon-trap.html`](docs/octagon-trap.html). External mathematical
review of the theorem remains welcome; the repository audit is not presented
as independent publication review.

### Fixed-pattern obstructions

Several previously live selected-witness patterns are now exactly obstructed by
local filters such as crossing-bisector, mutual-rhombus, phi 4-cycle,
cyclic-crossing CSP, vertex-circle order, Altman, and Kalmanson/Farkas checks.
These are fixed-pattern or fixed-order results, not a general proof.

The fixed S12A parity two-orbit pattern is now exactly obstructed in its
natural cyclic order by six forced consecutive equilateral ears: their forced
exterior turns total `4*pi`, exceeding the polygon total `2*pi`. See
[`docs/s12a-parity-two-orbit-frontier.md`](docs/s12a-parity-two-orbit-frontier.md).
This is a fixed-pattern, fixed-order result only; other cyclic orders of the
abstract S12A pattern are not classified.

Useful entry points:

- [`docs/mutual-rhombus-filter.md`](docs/mutual-rhombus-filter.md)
- [`docs/phi4-rectangle-trap.md`](docs/phi4-rectangle-trap.md)
- [`docs/cyclic-crossing-csp.md`](docs/cyclic-crossing-csp.md)
- [`docs/vertex-circle-order-filter.md`](docs/vertex-circle-order-filter.md)
- [`docs/round2/round2_merged_report.md`](docs/round2/round2_merged_report.md)
- [`docs/kalmanson-two-order-search.md`](docs/kalmanson-two-order-search.md)
- [`docs/sparse-frontier-diagnostic.md`](docs/sparse-frontier-diagnostic.md)
- [`docs/s12a-parity-two-orbit-frontier.md`](docs/s12a-parity-two-orbit-frontier.md)

The fixed abstract patterns `C19_skew` and `C13_sidon_1_2_4_10` are killed
across all cyclic orders by exact Kalmanson/Farkas certificate searches. That
does not settle the larger sparse frontier and does not prove Erdos #97.

Restricted symmetry-family diagnostics are also recorded. The two-orbit
circulant family has a review-pending obstruction note whose window-root
step is now exactly certified for all `m >= 3` at once by an SMT (z3)
certificate (see [`docs/two-orbit-window-all-m-smt.md`](docs/two-orbit-window-all-m-smt.md));
the note's remaining reduction steps stay review-pending prose, so the
family lemma itself is still a review-pending draft. The three-orbit
program closes the `m = 4` quarter cell exactly and now closes all twelve
quarter-cell signed-band cells for every `m >= 8` at once: the three
mixed-derivative cells by an exact SMT-plus-boundary-identity certificate
(see
[`docs/quarter-cell-mixed-cells-all-m-smt.md`](docs/quarter-cell-mixed-cells-all-m-smt.md))
and the nine first-derivative cells by an exact-corner-plus-certified-
Lipschitz dominance certificate (see
[`docs/quarter-cell-first-derivative-all-m-dominance.md`](docs/quarter-cell-first-derivative-all-m-dominance.md)),
with the earlier finite-`m` interval certificate retained as an
independent cross-check. All of this is still restricted three-orbit
quarter-cell evidence conditional on review-pending reduction prose --
non-quarter branches stay screen-grade for `m <= 16` and open beyond --
and it is not a proof of Erdos #97. See
[`docs/quarter-cell-derivative-certificate.md`](docs/quarter-cell-derivative-certificate.md).

For concentric equilateral-triangle orbits, review-pending exact reciprocal and
circle-product obstruction drafts exclude the natural four- and five-orbit
own-pair constructions.  A four-dimensional orthogonality argument also
excludes the generic all-five four-cross-singleton system when every mutual
gain-pair is nonreciprocal.  Reciprocal all-cross gains, mixed row shapes, and
uncovered half-step shapes remain, so this is a restricted obstruction rather
than a global result; see
[`docs/four-c3-generic-orbit-obstruction.md`](docs/four-c3-generic-orbit-obstruction.md),
[`docs/five-c3-tournament-obstruction.md`](docs/five-c3-tournament-obstruction.md),
and
[`docs/five-c3-all-cross-nonreciprocal-obstruction.md`](docs/five-c3-all-cross-nonreciprocal-obstruction.md).

An exact bounded certificate also rules out the real two-mode cyclic family
`z_i = w^i + t w^(k i)` for every real `t`, `9 <= n <= 80`, and
`2 <= k <= n-2`. Its deterministic replay covers 2,988 `(n,k)` cases
and classifies 1,865,543 real collision-root occurrences with zero unresolved,
using exact number-field arithmetic and outward-rounded Arb intervals. This is
a review-pending bounded restricted-family certificate diagnostic only: it
does not cover arbitrary configurations, complex coefficients, additional
modes, or unbounded `n`, and it does not prove or refute Erdos Problem #97.
See
[`docs/two-mode-cyclic-exact-n80.md`](docs/two-mode-cyclic-exact-n80.md).

### Review-pending frontier artifacts

The repo records an exhaustive `n=9` vertex-circle checker as a candidate
repo-local finite-case extension. Its cross-check leaves 184 full
selected-witness assignments after pair/crossing/count filters, and the
vertex-circle filter kills all 184 by exact self-edge or strict-cycle
obstructions. This remains review-pending; see
[`docs/n9-vertex-circle-exhaustive.md`](docs/n9-vertex-circle-exhaustive.md).
A companion combined replay now records the same compact frontier accounting
with localized counting and explicit per-assignment obstruction certificates;
it is still audit evidence only, not an `n=9` proof or status promotion.
The Kalmanson self-edge route also has a self-contained frontier-regeneration
replay that reaches the same 184 terminal assignments and finds one strict
Kalmanson self-edge for each. It is primary-route review evidence under the
still-open frontier, Kalmanson geometry, quotient replay, and written-review
gates; it is not an `n=9` proof or status promotion. A follow-up compression
checker records that an optimally chosen Kalmanson self-edge core uses exactly
three selected rows in all 184 assignments; that compression remains
proof-mining evidence only.

A companion closed-descent packet reformulates the 16 compact local-core
quotient obstructions as finite descent regions and extracted strict cycles.
It is diagnostic-only local packet data, not local-lemma completeness, a bridge
proof, or an `n=9` proof; see
[`docs/n9-vertex-circle-quotient-soundness-audit.md`](docs/n9-vertex-circle-quotient-soundness-audit.md).

The `n=9` Groebner decoder follow-up is a second-source algebraic audit target,
not a status promotion; see
[`docs/n9-groebner-decoders.md`](docs/n9-groebner-decoders.md).

Bootstrap/T12 material remains proof-mining and route-pruning evidence only.
The source-`151` lane has isolated a connector-avoiding private pair, a missing
center-`8` endpoint/core migration step, two target-sparse residual assignments,
and an order-sensitive fixed-order certificate route. The source-`81` lane
closes the currently bounded chain and repeated-support continuations under its
stated filters. Neither lane proves support existence, row forcing, genuine
rich-class order, the bootstrap bridge, or `n=9`.

Use [`STATE.md`](STATE.md) for the working frontier and
[`docs/index.md`](docs/index.md) for the complete packet inventory. The focused
proof-facing route is summarized in
[`docs/minimal-fragile-cover-bridge.md`](docs/minimal-fragile-cover-bridge.md),
[`docs/minimal-two-deletion-profile.md`](docs/minimal-two-deletion-profile.md),
[`docs/all-rich-class-pair-budget.md`](docs/all-rich-class-pair-budget.md),
[`docs/bootstrap-core-bridge.md`](docs/bootstrap-core-bridge.md),
[`docs/bootstrap-t12-bridge-target-map.md`](docs/bootstrap-t12-bridge-target-map.md),
and the current
[`next-lemma obligation contract`](docs/bootstrap-t12-151-6-label4-next-lemma-obligations.md).
These diagnostics do not promote the review-pending `n=9` candidate.

An incoming `n=10` singleton-slice continuation is recorded as a finite-case
draft review target only; see
[`docs/n10-vertex-circle-singleton-slices.md`](docs/n10-vertex-circle-singleton-slices.md).
It now has a portable C++ second-source replay that matches all 126 stored
singleton rows, still as review evidence only and not an `n=10` proof.

### Numerical near-misses

The historical best saved near-miss is `B12_3x4_danzer_lift`. It is useful as
a degeneration diagnostic, but it is **not** a counterexample. Its fixed
selected pattern is now exactly killed by the mutual-rhombus midpoint filter,
and the saved floating-point artifact is retained only as provenance for a
failed route.

```text
n: 12
pattern: B12_3x4_danzer_lift
max selected-distance spread: 0.006806368780585714
RMS equality residual:       0.0019599509549614457
convexity margin:            9.999999943508973e-07
minimum edge length:         0.0007465865604262556
status: numerical artifact only; fixed selected pattern exactly killed
```

Any proposed counterexample needs exact coordinates, an exact algebraic
certificate, an interval certificate, an SMT certificate, or a formal proof
covering both the distance equalities and strict convexity. Numerical
near-misses are not counterexamples.

## Trust labels

The repo uses explicit labels so that proof, computation, and exploration do
not blur together:

- `THEOREM` / `LEMMA`: proved local statements.
- `MACHINE_CHECKED_FINITE_CASE_ARTIFACT`: checked finite-case result in the
  repo-local sense.
- `EXACT_OBSTRUCTION`: exact arithmetic, algebraic, interval, SMT, or formal
  certificate killing a stated pattern or class.
- `NUMERICAL_EVIDENCE`: floating-point evidence only.
- `HEURISTIC` / `CONJECTURE`: search guidance or plausible but unproved
  mathematics.
- `COUNTEREXAMPLE_CANDIDATE`: requires independent verification and is not a
  counterexample claim.

See [`docs/claims.md`](docs/claims.md) and
[`docs/verification-contract.md`](docs/verification-contract.md) for the
proof-facing standard.

## Repository map

```text
.
|-- README.md
|-- STATE.md                  # short working dashboard
|-- RESULTS.md                # compact results ledger
|-- metadata/
|   `-- erdos97.yaml          # canonical status metadata snapshot
|-- docs/                     # proofs, audits, provenance, and planning notes
|-- src/erdos97/              # reusable search and verification code
|-- scripts/                  # command-line checkers and generators
|-- tests/                    # pytest coverage for code and artifacts
|-- data/                     # checked JSON artifacts and numerical runs
`-- certificates/             # legacy n=8 certificate paths
```

New generated checked certificates should normally live under
`data/certificates/`. The top-level `certificates/` directory is retained for
legacy n=8 artifacts and manual templates whose paths are already referenced by
docs, tests, and manifests.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
make verify-fast
```

If `make` is not available, run the fast tier directly:

```bash
python scripts/check_text_clean.py
python scripts/check_status_consistency.py
python scripts/check_artifact_provenance.py
git diff --check
python -m ruff check .
python -m pytest -q
```

`make verify-lint` runs the sub-minute text/status/provenance/ruff tier without
pytest. The default pytest configuration excludes tests marked `artifact`,
`slow`, or `exhaustive`; run `python -m pytest -q -m ""` only when you
intentionally want the full marker set.

For the checked CPython 3.12 direct-dependency snapshot, install the snapshot
before installing this package:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt
pip install -e . --no-deps
```

The snapshot pins direct dependencies only. Python 3.10 and 3.11 compatibility
CI instead resolves the supported ranges in `pyproject.toml`.

## Artifact checks

Run the artifact tier before finite-case, certificate, or public
theorem-style updates:

```bash
make verify-artifacts
```

For CI-style metadata capture, run:

```bash
make audit-artifacts
```

Both targets use the command registry in
[`scripts/run_artifact_audit.py`](scripts/run_artifact_audit.py): `verify-artifacts`
runs the registry without metadata capture, while `audit-artifacts` records
per-command stdout/stderr and environment metadata. If `make` is unavailable,
use `python scripts/run_artifact_audit.py --verify-only` for the same raw
artifact command set.

The command registry and the excluded pytest tiers support deterministic,
zero-based CI shards. Every command or collected test is assigned by SHA-256
of its stable id, so the shards are disjoint and their union is the unsharded
selection:

```bash
python scripts/run_artifact_audit.py --verify-only --shard-count 8 --shard-index 0
python -m pytest -q -m "artifact" --shard-count 8 --shard-index 0
python -m pytest -q -m "(slow or exhaustive) and not artifact" \
  --shard-count 8 --shard-index 0
```

Run every index from `0` through `shard-count - 1` for complete coverage.
For sharded metadata audits, the two global status/provenance preflights belong
to shard `0` and therefore run exactly once across the complete shard set.

Pull requests run the fast tier and, when artifact-sensitive files change, the
artifact-marked pytest shards. The direct artifact-command audit and the
non-artifact slow/exhaustive pytest shards run after merge to `main`, on the
weekly schedule, or by manual dispatch. Documentation-only and Lean-only pull
requests use their dedicated fast/status and Lean workflows instead of
starting the artifact pytest matrix. Superseded runs on the same branch are
cancelled automatically.

Useful exploratory commands:

```bash
erdos97-search --list-patterns
erdos97-search --verify data/runs/best_B12_slsqp_m1e-6.json --tol 1e-6
python scripts/interval_verify_candidate.py data/runs/best_B12_slsqp_m1e-6.json
python scripts/check_mutual_rhombus_filter.py --assert-expected
python scripts/check_vertex_circle_order_filter.py --pattern P18_parity_balanced --search --assert-obstructed
python scripts/check_min_radius_filter.py --pattern C19_skew --assert-pass
```

Optional dependencies for selected exactification paths:

```bash
pip install sympy z3-solver
```

## Research hygiene

1. Do not present floating-point equalities as exact.
2. Keep search heuristics separate from necessary mathematical constraints.
3. Record failed approaches clearly enough that future work avoids repeating
   them.
4. Prefer small reproducible JSON artifacts over screenshots or prose-only
   claims.
5. Do not prepare OEIS submissions from AI-generated output.

## Nearby examples

The 3-neighbor version is false: Danzer produced a 9-point convex polygon
where every vertex has 3 equidistant vertices, and Fishburn-Reeds produced a
20-point convex polygon where every vertex has 3 equidistant vertices at a
common radius. These examples do not automatically extend to the 4-neighbor
target.

A 1975 Erdos paper reports an unpublished all-`k` Danzer claim, but the
official #97 page says this was not repeated later and was presumably
mistaken. This repository treats that statement as unverified literature risk,
not as a `k=4` counterexample; see
[`docs/literature-risk.md`](docs/literature-risk.md).

## Contribution policy

Contributions are welcome if they are reproducible and clearly labelled.
Especially useful contributions include:

- independent verification scripts;
- exact obstruction lemmas;
- interval, SOS, SMT, or formal certificates for restricted classes;
- new incidence patterns satisfying known necessary filters;
- numerical candidates with robust convexity margins and residual below
  `1e-10`.

Please avoid presenting numerical near-equalities as counterexamples.

## License and citation

Code is licensed under the MIT License. Research notes, documentation, data
artifacts, issue templates, and certificate templates are licensed under
CC-BY-4.0. See [`LICENSE.md`](LICENSE.md).

If you use this repository, please cite it using
[`CITATION.cff`](CITATION.cff).

## Maintenance checklist

- Run `make verify-fast` or the equivalent raw fast-tier commands after code or
  documentation changes.
- Run `make verify-artifacts` before finite-case, certificate, or public
  theorem-style updates, or record exactly why a command could not be run.
- Keep `README.md`, `STATE.md`, `RESULTS.md`, and
  `metadata/erdos97.yaml` aligned when a source-of-truth status changes.
- Confirm this README still says no general proof and no counterexample are
  claimed.
- Keep current-work pointers aligned with
  [`docs/review-priorities.md`](docs/review-priorities.md),
  [`docs/codex-backlog.md`](docs/codex-backlog.md), and the live GitHub issue
  list.
